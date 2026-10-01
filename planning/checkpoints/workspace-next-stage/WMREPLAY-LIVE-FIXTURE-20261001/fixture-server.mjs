import http from 'node:http'

// Local, in-memory UI fixture only.  It intentionally has no database,
// broker, provider, OAuth, filesystem or external network capability.
const host = process.env.TW_FIXTURE_HOST || '127.0.0.1'
const port = Number(process.env.TW_FIXTURE_PORT || 8010)
const rows = Array.from({ length: 12 }, (_, index) => {
  const timestamp = 1710000000 + index * 60
  const open = 1.08 + index * 0.00012
  const close = open + (index % 3 === 0 ? 0.0002 : index % 3 === 1 ? -0.0001 : 0.00008)
  return {
    timestamp,
    open: Number(open.toFixed(6)),
    high: Number((Math.max(open, close) + 0.00028).toFixed(6)),
    low: Number((Math.min(open, close) - 0.00018).toFixed(6)),
    close: Number(close.toFixed(6)),
    volume: 100 + index * 15,
  }
})

const dataset = {
  dataset_id: 'ui-live-fixture',
  instrument_id: 'EURUSD',
  timeframe: 'M1',
  timeframe_seconds: 60,
  provider: 'offline-fixture',
  quality_status: 'verified_fixture_only',
  holdout_status: 'locked',
  row_count: 5000,
  artifact_sha256: 'sha256:ui-live-fixture-no-future-leak',
  dataset_available: true,
}

const sessions = new Map()
let sequence = 1

function seedSession(recordId = 'replay-fixture', cursor = 4, revision = 1, parent = null) {
  sessions.set(recordId, {
    record_id: recordId,
    revision,
    payload: {
      dataset_id: dataset.dataset_id,
      cursor_index: Math.max(0, Math.min(rows.length - 1, cursor)),
      branch_id: `${recordId}-branch`,
      parent_session_id: parent,
      parent_revision: parent ? revision : null,
      status: cursor >= rows.length - 1 ? 'completed' : 'paused',
      instrument_id: dataset.instrument_id,
      timeframe: dataset.timeframe,
    },
  })
}
seedSession()

function json(res, status, body) {
  const encoded = JSON.stringify(body)
  res.writeHead(status, {
    'content-type': 'application/json; charset=utf-8',
    'cache-control': 'no-store',
  })
  res.end(encoded)
}

function empty(res, status = 204) {
  res.writeHead(status, { 'cache-control': 'no-store' })
  res.end()
}

async function readBody(req) {
  let body = ''
  for await (const chunk of req) body += chunk
  if (!body) return {}
  try { return JSON.parse(body) } catch { return null }
}

function sessionView(session, requestedCursor = null) {
  const canonicalCursor = session.payload.cursor_index
  const viewCursor = requestedCursor === null ? canonicalCursor : requestedCursor
  const visibleRows = rows.slice(0, viewCursor + 1)
  const last = visibleRows.at(-1) || rows[0]
  return {
    ...session,
    dataset_sha256: dataset.artifact_sha256,
    cutoff_timestamp: last.timestamp,
    visible_rows: visibleRows,
    visible_row_count: visibleRows.length,
    total_row_count: dataset.row_count,
    has_future_rows: visibleRows.length < rows.length,
    view_cursor_index: viewCursor,
    canonical_cursor_index: canonicalCursor,
    historical_view: viewCursor !== canonicalCursor,
  }
}

function catalogItem(session) {
  return {
    record_id: session.record_id,
    session_id: session.record_id,
    dataset_id: dataset.dataset_id,
    instrument_id: dataset.instrument_id,
    timeframe: dataset.timeframe,
    timeframe_seconds: dataset.timeframe_seconds,
    status: session.payload.status,
    revision: session.revision,
    dataset_available: true,
    updated_at: '2026-10-01T00:00:00Z',
  }
}

function blockedMutation(res) {
  return json(res, 403, { detail: 'fixture_mutation_blocked', execution_capability: false })
}

async function handle(req, res) {
  const url = new URL(req.url || '/', `http://${host}:${port}`)
  const path = url.pathname
  if (req.method === 'GET' && path === '/health') return json(res, 200, { status: 'ok', fixture: true, execution_capability: false })
  if (req.method === 'GET' && path === '/api/v2/overview') {
    return json(res, 200, {
      schema_version: 'workspace-overview-v1',
      workspace_id: req.headers['x-workspace-id'] || 'tenant-a',
      counts: { datasets: 1, research_jobs: { queued: 0, running: 0, completed: 1, failed: 0 }, records: { playbooks: 1, journal: 2, annotations: 3 } },
      execution_capability: false,
      source: 'offline-fixture',
    })
  }
  if (req.method === 'GET' && path === '/api/v2/session/status') {
    return json(res, 200, { status: 'ready', session_id: 'local-demo-session:fixture', execution_capability: false, source: 'offline-fixture' })
  }
  if (req.method === 'GET' && path === '/api/v2/execution/capabilities') {
    return json(res, 200, { execution_capability: false, broker_actions: false, mode: 'PREP_ONLY_OFFLINE' })
  }
  if (req.method === 'GET' && path === '/api/v2/connectors/notion/oauth/status') {
    return json(res, 200, { configured: false, connected: false, status: 'owner_gated', execution_capability: false })
  }
  if (req.method === 'GET' && path === '/api/v2/live/status') {
    return json(res, 200, { status: 'locked', live_capability: false, reason: 'owner_gated', source: 'offline-fixture' })
  }
  if (req.method === 'GET' && path === '/api/v2/data/datasets') return json(res, 200, { items: [dataset], datasets: [dataset] })
  if (req.method === 'GET' && path === '/api/v2/data/providers') return json(res, 200, { items: [{ provider: 'offline-fixture', status: 'ready', network: false, holdout: 'locked' }] })
  if (req.method === 'GET' && path === '/api/v2/replay/sessions') {
    return json(res, 200, { items: [...sessions.values()].map(catalogItem) })
  }
  if (req.method === 'POST' && path === '/api/v2/replay/sessions') {
    const body = await readBody(req)
    if (!body || body.dataset_id !== dataset.dataset_id) return json(res, 422, { detail: 'fixture_dataset_required' })
    const id = `local-fixture-${sequence++}`
    seedSession(id, Number.isInteger(body.start_index) ? body.start_index : 0)
    return json(res, 201, sessionView(sessions.get(id)))
  }
  const replayMatch = path.match(/^\/api\/v2\/replay\/sessions\/([^/]+)(?:\/([^/]+))?$/)
  if (replayMatch) {
    const id = decodeURIComponent(replayMatch[1])
    const action = replayMatch[2] || ''
    const session = sessions.get(id)
    if (!session) return json(res, 404, { detail: 'replay_not_found' })
    if (req.method === 'GET' && !action) {
      const rawCursor = url.searchParams.get('cursor_index')
      const requested = rawCursor === null ? null : Number(rawCursor)
      if (requested !== null && (!Number.isInteger(requested) || requested < 0 || requested > session.payload.cursor_index)) return json(res, 422, { detail: 'invalid_historical_cursor' })
      return json(res, 200, sessionView(session, requested))
    }
    if (req.method === 'POST' && action === 'step') {
      const body = await readBody(req)
      if (body?.expected_revision !== session.revision) return json(res, 409, { detail: 'revision_conflict' })
      const steps = Number.isInteger(body?.steps) ? Math.max(1, body.steps) : 1
      session.payload.cursor_index = Math.min(rows.length - 1, session.payload.cursor_index + steps)
      session.payload.status = session.payload.cursor_index >= rows.length - 1 ? 'completed' : 'paused'
      session.revision += 1
      return json(res, 200, sessionView(session))
    }
    if (req.method === 'POST' && action === 'branch') {
      const body = await readBody(req)
      const cursor = Number.isInteger(body?.cursor_index) ? body.cursor_index : session.payload.cursor_index
      const branchId = `${id}-branch-${sequence++}`
      seedSession(branchId, cursor, 1, id)
      return json(res, 201, sessionView(sessions.get(branchId)))
    }
    return blockedMutation(res)
  }
  if (req.method === 'GET' && path === '/api/v2/journal') return json(res, 200, { items: [] })
  if (req.method === 'GET' && path === '/api/v2/playbooks') return json(res, 200, { items: [{ record_id: 'fixture-playbook', status: 'draft', revision: 1, title: 'Offline fixture playbook' }] })
  if (req.method === 'GET' && path === '/api/v2/research/engines') return json(res, 200, { items: [{ engine_id: 'bar-breakout-v1', status: 'fixture_only' }] })
  if (req.method === 'GET' && path === '/api/v2/ai/status') return json(res, 200, { status: 'offline', provider: 'offline-fixture', execution_capability: false })
  if (req.method === 'GET' && path.startsWith('/api/v2/research/jobs/')) return json(res, 404, { detail: 'fixture_job_not_found' })
  return json(res, 404, { detail: 'fixture_route_not_found', path })
}

const server = http.createServer((req, res) => {
  handle(req, res).catch((error) => json(res, 500, { detail: 'fixture_server_error', message: String(error?.message || error) }))
})

server.listen(port, host, () => {
  console.log(JSON.stringify({ status: 'ready', host, port, fixture: 'ui-live-offline', execution_capability: false }))
})

function shutdown() {
  server.close(() => process.exit(0))
}
process.on('SIGINT', shutdown)
process.on('SIGTERM', shutdown)
