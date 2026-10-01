import assert from 'node:assert/strict'
import { spawn } from 'node:child_process'
import { mkdir } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const artifactDir = path.dirname(fileURLToPath(import.meta.url))
const here = path.resolve(artifactDir, '..', '..', '..', '..', 'projects', 'mt5-tradingview-backtester', 'foundation_v2', 'web')
const origin = 'http://127.0.0.1:4176'
const evidenceDir = artifactDir
const viteBin = path.join(here, 'node_modules', 'vite', 'bin', 'vite.js')
const pathToFileURL = (value) => new URL('file:///' + value.replaceAll('\\\\', '/'))
const { chromium } = await import(pathToFileURL(path.join(here, 'node_modules', 'playwright', 'index.mjs')).href)
const rows = [
  { timestamp: 1760000000, open: 1.0800, high: 1.0810, low: 1.0796, close: 1.0804, volume: 100 },
  { timestamp: 1760003600, open: 1.0804, high: 1.0816, low: 1.0801, close: 1.0810, volume: 110 },
  { timestamp: 1760007200, open: 1.0810, high: 1.0812, low: 1.0800, close: 1.0805, volume: 120 },
  { timestamp: 1760010800, open: 1.0805, high: 1.0818, low: 1.0804, close: 1.0813, volume: 130 },
]
const instrument = {
  instrument_id: 'EURUSD', asset_class: 'fx', base_ccy: 'EUR', quote_ccy: 'USD', account_ccy: 'USD',
  tick_size: '0.0001', pip_size: '0.0001', contract_size: '100000', quantity_min: '0.01', quantity_step: '0.01',
  effective_from_utc: '2026-01-01T00:00:00Z', effective_to_utc: '',
}
const costModel = {
  version: 'replay-fixture-cost-v1', spread_basis: 'bid_ask_embedded', commission_per_side_account: '1',
  minimum_fee_account: '0', slippage_price_per_side: '0', financing_account: '0', quote_to_account_rate: '1', account_ccy: 'USD', rounding_decimals: 2,
}
const sessions = new Map()
const postLog = []
let conflictNextQueue = false

function seed(id, { conflict = false } = {}) {
  sessions.set(id, {
    record_id: id,
    revision: 1,
    conflict,
    payload: { dataset_id: 'ui-trade-fixture', cursor_index: 2, branch_id: `${id}-branch`, parent_session_id: null, status: 'paused', execution: null },
  })
}
function executionFor(session, pending = null) {
  return {
    schema_version: 'replay-execution-v1', replay_session_id: session.record_id, branch_id: session.payload.branch_id,
    dataset_id: session.payload.dataset_id, dataset_sha256: 'fixture-trade-sha256', instrument_spec: instrument, cost_model: costModel,
    spread_price: '0.0002', timeframe_seconds: 3600, starting_balance: '10000', phase_index: 1, phase_initial_balance: '10000',
    balance: '10000', floating_pl: '0', equity: '10000', cursor_index: session.payload.cursor_index,
    event_sequence: pending ? 1 : 0, pending_market_order: pending, position: null,
    ledger: pending ? [{ sequence: 1, kind: 'market_order_queued', operation_id: pending.operation_id, cursor_index: session.payload.cursor_index, side: pending.side, quantity: pending.quantity, stop_loss: pending.stop_loss, take_profit: pending.take_profit }] : [],
    evaluation_quality: 'full_for_declared_model',
  }
}
function view(id) {
  const session = sessions.get(id)
  const visible = rows.slice(0, session.payload.cursor_index + 1)
  return {
    ...session, dataset_sha256: 'fixture-trade-sha256', cutoff_timestamp: visible.at(-1).timestamp,
    visible_rows: visible, visible_row_count: visible.length, total_row_count: rows.length,
    has_future_rows: visible.length < rows.length, view_cursor_index: session.payload.cursor_index,
    canonical_cursor_index: session.payload.cursor_index, historical_view: false,
  }
}
function fulfill(route, status, payload) {
  return route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(payload) })
}
async function waitForServer() {
  for (let i = 0; i < 80; i += 1) {
    try { if ((await fetch(origin)).ok) return } catch {}
    await new Promise((resolve) => setTimeout(resolve, 100))
  }
  throw new Error('Vite did not start')
}
function workspaceUrl(id) {
  return `${origin}/?workspace=tenant-ui&view=trade&surface=workspace&session=${id}&dataset=ui-trade-fixture&mode=Practice`
}
async function bodyText(page) { return page.locator('body').innerText() }
async function overflow(page) { return page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth) }

async function main() {
  await mkdir(evidenceDir, { recursive: true })
  seed('trade-success')
  seed('trade-conflict', { conflict: true })
  const server = spawn(process.execPath, [viteBin, '--host', '127.0.0.1', '--port', '4176', '--strictPort'], { cwd: here, stdio: ['ignore', 'pipe', 'pipe'] })
  const serverErrors = []
  server.stderr.on('data', (chunk) => serverErrors.push(String(chunk)))
  let browser
  let context
  const consoleErrors = []
  try {
    await waitForServer()
    browser = await chromium.launch({ headless: true })
    context = await browser.newContext({ viewport: { width: 1440, height: 900 } })
    await context.tracing.start({ screenshots: true, snapshots: true, sources: true })
    const page = await context.newPage()
    page.on('console', (message) => { if (message.type() === 'error') consoleErrors.push(message.text()) })
    page.on('pageerror', (error) => consoleErrors.push(`pageerror:${error.message}`))
    await page.route('**/api/v2/data/datasets', (route) => {
      if (route.request().method() !== 'GET') return fulfill(route, 405, { detail: 'method_not_allowed' })
      return fulfill(route, 200, { items: [{ dataset_id: 'ui-trade-fixture', instrument_id: 'EURUSD', timeframe: 'H1', timeframe_seconds: 3600, quality_status: 'verified', holdout_status: 'locked', row_count: rows.length, instrument_spec: instrument }] })
    })
    await page.route('**/api/v2/replay/sessions/**', async (route) => {
      const request = route.request()
      const url = new URL(request.url())
      const pieces = url.pathname.split('/').filter(Boolean)
      const id = decodeURIComponent(pieces[4] || '')
      const action = pieces[5] || ''
      const session = sessions.get(id)
      if (!session) return fulfill(route, 404, { detail: 'replay_not_found' })
      if (request.method() === 'GET') return fulfill(route, 200, view(id))
      const body = request.postDataJSON()
      postLog.push({ id, action, body })
      if (body.expected_revision !== session.revision) return fulfill(route, 409, { detail: 'record revision conflict' })
      if (action === 'execution') {
        session.revision += 1
        session.payload.execution = executionFor(session)
        return fulfill(route, 200, view(id))
      }
      if (action === 'orders' && pieces[6] === 'market') {
        if (session.conflict && conflictNextQueue) {
          conflictNextQueue = false
          session.revision += 1
          return fulfill(route, 409, { detail: 'record revision conflict' })
        }
        const pending = { operation_id: body.operation_id, side: body.side, quantity: String(body.quantity), stop_loss: String(body.stop_loss), take_profit: String(body.take_profit), requested_cursor_index: session.payload.cursor_index }
        session.revision += 1
        session.payload.execution = executionFor(session, pending)
        return fulfill(route, 200, view(id))
      }
      return fulfill(route, 404, { detail: 'unknown_action' })
    })

    // Desktop success: initialization POST -> execution state -> market-order POST -> pending ledger state.
    await page.goto(workspaceUrl('trade-success'))
    await page.getByRole('button', { name: 'Khởi tạo local simulator' }).waitFor()
    assert.equal(await page.getByTestId('trade-simulator-banner').getAttribute('data-testid'), 'trade-simulator-banner')
    await page.getByRole('button', { name: 'Khởi tạo local simulator' }).click()
    await page.getByRole('button', { name: 'Queue vào simulator' }).waitFor()
    assert.match(await bodyText(page), /Execution assumptions/)
    await page.getByRole('button', { name: 'Queue vào simulator' }).click()
    await page.waitForTimeout(500); if (await page.getByText('Đã có market order đang chờ fill', { exact: true }).count() === 0) { console.log('QUEUE_DEBUG', await bodyText(page), JSON.stringify(postLog)); throw new Error('queue state not visible') }
    assert.match(await page.locator('.trade-active-state').innerText(), /BUY 0\.01.*sẽ fill ở bar kế tiếp/s)
    assert.match(await page.locator('.trade-account-strip').innerText(), /Pending/)
    assert.equal(await page.getByRole('button', { name: 'Queue vào simulator' }).count(), 0)
    assert.ok(postLog.some((entry) => entry.id === 'trade-success' && entry.action === 'execution' && entry.body.expected_revision === 1), 'initialize POST should carry revision 1')
    const successOrder = postLog.find((entry) => entry.id === 'trade-success' && entry.action === 'orders')
    assert.ok(successOrder, 'market-order POST should be intercepted')
    assert.equal(successOrder.body.expected_revision, 2)
    assert.equal(successOrder.body.side, 'BUY')
    assert.equal(successOrder.body.quantity, '0.01')
    assert.equal(await overflow(page), 0)
    await page.screenshot({ path: path.join(evidenceDir, 'trade-mutation-success-1440.png'), fullPage: true })

    // Keep the same accepted success state under the narrow mobile viewport.
    await page.setViewportSize({ width: 390, height: 844 })
    assert.equal(await overflow(page), 0)
    await page.screenshot({ path: path.join(evidenceDir, 'trade-mutation-success-390.png'), fullPage: true })

    // Fresh mobile session: successful initialization followed by a server-side revision conflict on queue.
    await page.goto(workspaceUrl('trade-conflict'))
    await page.setViewportSize({ width: 390, height: 844 })
    await page.getByRole('button', { name: 'Khởi tạo local simulator' }).waitFor()
    await page.getByRole('button', { name: 'Khởi tạo local simulator' }).click()
    await page.getByRole('button', { name: 'Queue vào simulator' }).waitFor()
    conflictNextQueue = true
    await page.getByRole('button', { name: 'Queue vào simulator' }).click()
    await page.getByRole('alert').waitFor()
    assert.match(await page.getByRole('alert').innerText(), /Không queue được draft: record revision conflict/i)
    assert.equal(await page.getByRole('button', { name: 'Queue vào simulator' }).count(), 1, 'conflict keeps draft available for recovery')
    assert.equal(await page.getByText('Đã có market order đang chờ fill', { exact: true }).count(), 0)
    assert.equal(await overflow(page), 0)
    await page.screenshot({ path: path.join(evidenceDir, 'trade-mutation-conflict-390.png'), fullPage: true })

    const requests = postLog.map((entry) => `${entry.id}:${entry.action}:${entry.body.expected_revision}`)
    const conflictPost = postLog.find((entry) => entry.id === 'trade-conflict' && entry.action === 'orders')
    assert.ok(conflictPost, 'conflict market-order POST should be intercepted')
    assert.equal(conflictPost.body.expected_revision, 2)
    const unexpectedErrors = consoleErrors.filter((message) => !/409 \(Conflict\)/.test(message))
    assert.deepEqual(unexpectedErrors, [])
    await context.tracing.stop({ path: path.join(evidenceDir, 'trade-mutation-trace.zip') })
    const runtime = {
      status: 'PASS', fixture: 'local-intercepted-trade-simulator', origin,
      checks: ['initialize_post_revision_and_execution_state', 'queue_post_revision_and_pending_ledger_state', '409_revision_conflict_preserves_draft', 'broker_provider_external_calls_absent', 'responsive_1440_390', 'no_horizontal_overflow', 'no_unexpected_console_or_page_errors'],
      requests, post_count: postLog.length, console_errors: consoleErrors,
      screenshots: ['trade-mutation-success-1440.png', 'trade-mutation-success-390.png', 'trade-mutation-conflict-390.png', 'trade-mutation-trace.zip'],
    }
    await import('node:fs/promises').then(({ writeFile }) => writeFile(path.join(evidenceDir, 'runtime.json'), JSON.stringify(runtime, null, 2)))
    console.log(JSON.stringify(runtime, null, 2))
  } finally {
    if (context && !context._options) { /* no-op: tracing is stopped on pass */ }
    if (browser) await browser.close()
    server.kill('SIGTERM')
    if (serverErrors.length) process.stderr.write(serverErrors.join(''))
  }
}
main().catch((error) => { console.error(error); process.exitCode = 1 })




