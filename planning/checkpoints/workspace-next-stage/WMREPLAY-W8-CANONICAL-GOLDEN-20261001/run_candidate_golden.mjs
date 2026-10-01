import { createHash } from 'node:crypto'
import { createRequire } from 'node:module'
import { execFileSync } from 'node:child_process'
import { mkdir, readFile, stat, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const here = path.dirname(fileURLToPath(import.meta.url))
const workspaceRoot = path.resolve(here, '../../../..')
const webRoot = path.join(workspaceRoot, 'projects', 'mt5-tradingview-backtester', 'foundation_v2', 'web')
const origin = process.env.TW_GOLDEN_ORIGIN || 'http://127.0.0.1:5173'
const workspaceId = 'canonical-golden-fixture'
const mt5Root = path.join(workspaceRoot, 'projects', 'mt5-tradingview-backtester')
const require = createRequire(import.meta.url)
const { chromium } = require(path.join(webRoot, 'node_modules', 'playwright'))

await mkdir(here, { recursive: true })

const rows = Array.from({ length: 30 }, (_, index) => {
  const open = 1.08 + index * 0.0001
  const close = open + (index % 3 === 0 ? 0.0002 : index % 3 === 1 ? -0.0001 : 0.00008)
  return {
    timestamp: 1710000000 + index * 60,
    open: Number(open.toFixed(6)),
    high: Number((Math.max(open, close) + 0.00025).toFixed(6)),
    low: Number((Math.min(open, close) - 0.0002).toFixed(6)),
    close: Number(close.toFixed(6)),
    volume: 100 + index,
  }
})
const dataset = {
  dataset_id: 'canonical-golden-dataset',
  instrument_id: 'EURUSD',
  timeframe: 'M1',
  timeframe_seconds: 60,
  quality_status: 'verified_fixture_only',
  holdout_access: false,
  provider_id: 'offline-fixture',
  row_count: 5000,
  artifact_sha256: 'sha256:canonical-golden-fixture',
}
const session = {
  record_id: 'golden-session',
  session_id: 'golden-session',
  revision: 1,
  payload: {
    dataset_id: dataset.dataset_id,
    cursor_index: 19,
    branch_id: 'golden-session-branch',
    parent_session_id: null,
    status: 'paused',
    instrument_id: dataset.instrument_id,
    timeframe: dataset.timeframe,
  },
  dataset_sha256: dataset.artifact_sha256,
  cutoff_timestamp: rows[19].timestamp,
  visible_rows: rows.slice(0, 20),
  visible_row_count: 20,
  total_row_count: rows.length,
  has_future_rows: true,
  view_cursor_index: 19,
  canonical_cursor_index: 19,
  historical_view: false,
}
const catalogItem = {
  record_id: session.record_id,
  session_id: session.session_id,
  dataset_id: dataset.dataset_id,
  instrument_id: dataset.instrument_id,
  timeframe: dataset.timeframe,
  timeframe_seconds: dataset.timeframe_seconds,
  status: session.payload.status,
  revision: session.revision,
  dataset_available: true,
  updated_at: '2026-10-01T00:00:00Z',
}

function largeAnalytics(count = 5000) {
  const ledger = Array.from({ length: count }, (_, index) => {
    const pnl = index % 3 === 0 ? 12 : index % 3 === 1 ? -7 : 0
    const iso = new Date(Date.UTC(2024, 0, 1) + index * 86_400_000).toISOString()
    return {
      trade_id: `golden-${String(index + 1).padStart(5, '0')}`,
      open_time_utc: iso,
      close_time_utc: iso,
      net_pnl: pnl,
      realized_r: pnl / 10,
      side: index % 2 ? 'sell' : 'buy',
      source: { session_id: session.session_id },
    }
  })
  let balance = 1000
  const curve = ledger.map((trade) => ({ trade_id: trade.trade_id, closed_trade_balance: (balance += trade.net_pnl) }))
  return {
    schema_version: 'analytics-read-model-v1',
    analytics_available: true,
    stale: false,
    provenance: {
      dataset_id: dataset.dataset_id,
      dataset_sha256: dataset.artifact_sha256,
      protocol_sha256: 'sha256:canonical-golden-protocol',
      metrics_schema_version: 'metrics-v2',
      split: 'research',
      playbook_id: 'canonical-golden-fixture',
      status: 'fresh',
    },
    scope: {
      selected_trade_count: count,
      total_trade_count: count,
      observed_range: { first_close_utc: ledger[0].close_time_utc, last_close_utc: ledger.at(-1).close_time_utc },
      balance_curve_scope: 'closed trades',
    },
    metrics: {
      closed_trade_count: count,
      net_pnl: ledger.reduce((sum, row) => sum + row.net_pnl, 0),
      closed_trade_balance_curve: curve,
      closed_trade_balance_max_drawdown: 7,
      definitions: { net_pnl: { question: 'Net result?', unit: 'account units', formula: 'sum(net_pnl)', source: 'ledger', version: 'v1' } },
    },
    ledger,
  }
}
const overviewFixture = {
  schema_version: 'workspace-overview-v1',
  workspace_id: workspaceId,
  counts: { datasets: 1, research_jobs: { queued: 0, running: 0, completed: 1, failed: 0 }, records: { playbooks: 1, journal: 2, annotations: 3 } },
  execution_capability: false,
  source: 'offline-fixture',
}
const analyticsFixture = largeAnalytics()
const payloadHashes = {
  overview: createHash('sha256').update(JSON.stringify(overviewFixture)).digest('hex'),
  dataset: createHash('sha256').update(JSON.stringify(dataset)).digest('hex'),
  session: createHash('sha256').update(JSON.stringify(session)).digest('hex'),
  analytics: createHash('sha256').update(JSON.stringify(analyticsFixture)).digest('hex'),
}

function sourceProvenance() {
  const status = execFileSync('git', ['-C', mt5Root, 'status', '--short', '--', 'foundation_v2/web/src', 'foundation_v2/web/tests'], { encoding: 'utf8' })
  const diff = execFileSync('git', ['-C', mt5Root, 'diff', '--binary', '--', 'foundation_v2/web/src', 'foundation_v2/web/tests'])
  return {
    head: execFileSync('git', ['-C', mt5Root, 'rev-parse', 'HEAD'], { encoding: 'utf8' }).trim(),
    workingTreeCleanForScopedPaths: !status.trim(),
    scopedStatus: status.trim().split(/\r?\n/).filter(Boolean),
    scopedDiffSha256: createHash('sha256').update(diff).digest('hex').toUpperCase(),
  }
}

const sizes = [
  { width: 1440, height: 900 },
  { width: 768, height: 900 },
  { width: 390, height: 844 },
]
const surfaces = [
  { id: 'dashboard', route: `/?view=overview&workspace=${workspaceId}`, selector: '[data-testid="dashboard-data-state"]' },
  { id: 'sessions', route: `/?view=replay&select=1&workspace=${workspaceId}`, selector: '[data-testid="replay-session-dashboard"]' },
  { id: 'replay', route: `/?view=replay&surface=workspace&session=${session.session_id}&workspace=${workspaceId}`, selector: '[data-testid="replay-chart"]' },
  { id: 'analytics', route: `/?view=analytics&surface=workspace&job=large-fixture&workspace=${workspaceId}`, selector: '[data-testid="analytics-workspace"]' },
]

function json(route, status, payload) {
  return route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(payload) })
}

async function fixtureRoute(route, requests) {
  const request = route.request()
  const url = new URL(request.url())
  const endpoint = `${request.method()} ${url.pathname}${url.search}`
  requests.push({ endpoint, workspaceHeader: request.headers()['x-workspace-id'] || null })
  if (request.method() !== 'GET') return json(route, 405, { detail: 'method_not_allowed_in_candidate_golden_fixture' })
  if (url.pathname === '/api/v2/overview') return json(route, 200, overviewFixture)
  if (url.pathname === '/api/v2/replay/sessions') return json(route, 200, { items: [catalogItem], total: 1 })
  if (url.pathname === `/api/v2/replay/sessions/${session.session_id}`) return json(route, 200, session)
  if (url.pathname === '/api/v2/data/datasets') return json(route, 200, { items: [dataset], datasets: [dataset], holdout_access: false })
  if (url.pathname === '/api/v2/data/providers') return json(route, 200, { items: [{ provider: 'offline-fixture', status: 'ready', network: false, holdout: 'locked' }] })
  if (url.pathname.endsWith('/analytics')) return json(route, 200, analyticsFixture)
  if (url.pathname === '/api/v2/session/status') return json(route, 200, { status: 'ready', session_id: 'canonical-golden-fixture', execution_capability: false, source: 'offline-fixture' })
  if (url.pathname === '/api/v2/execution/capabilities') return json(route, 200, { execution_capability: false, broker_actions: false, mode: 'PREP_ONLY_OFFLINE' })
  if (url.pathname === '/api/v2/connectors/notion/oauth/status') return json(route, 200, { configured: false, connected: false, status: 'owner_gated', execution_capability: false })
  if (url.pathname === '/api/v2/live/status') return json(route, 200, { status: 'locked', live_capability: false, reason: 'owner_gated', source: 'offline-fixture' })
  if (url.pathname === '/api/v2/journal' || url.pathname === '/api/v2/playbooks') return json(route, 200, { items: [] })
  return json(route, 200, { items: [] })
}

function stableSelectors() {
  return ['#root', '[data-testid="fxreplay-shell"]', '.fx-shell', '.fx-topbar', '.fx-rail', '.fx-content', '.fx-content main', 'main h1', '[data-testid="dashboard-data-state"]', '[data-testid="replay-session-dashboard"]', '[data-testid="replay-chart"]', '[data-testid="analytics-workspace"]', 'tbody']
}

async function geometry(page) {
  return page.evaluate((selectors) => {
    const rect = (node) => {
      if (!node) return null
      const r = node.getBoundingClientRect()
      return { x: Number(r.x.toFixed(3)), y: Number(r.y.toFixed(3)), width: Number(r.width.toFixed(3)), height: Number(r.height.toFixed(3)) }
    }
    const result = {}
    for (const selector of selectors) result[selector] = [...document.querySelectorAll(selector)].slice(0, 4).map(rect)
    return {
      viewport: { width: innerWidth, height: innerHeight, devicePixelRatio },
      document: { scrollWidth: document.documentElement.scrollWidth, scrollHeight: document.documentElement.scrollHeight },
      selectors: result,
      theme: document.documentElement.getAttribute('data-tw-theme'),
      lang: document.documentElement.getAttribute('lang'),
    }
  }, stableSelectors())
}

async function waitForSettled(page, surface) {
  await page.goto(`${origin}${surface.route}`, { waitUntil: 'networkidle' })
  await page.locator(surface.selector).waitFor({ state: 'visible', timeout: 15_000 })
  if (surface.id === 'replay') await page.locator('[data-testid="replay-chart"][data-visible-row-count="20"]').waitFor({ timeout: 15_000 })
  if (surface.id === 'analytics') await page.getByText('N = 5.000', { exact: true }).waitFor({ timeout: 15_000 })
  await page.evaluate(() => document.fonts?.ready)
  await page.addStyleTag({ content: '*,:before,:after{animation:none!important;transition:none!important;caret-color:transparent!important;scroll-behavior:auto!important}' })
  await page.waitForTimeout(750)
}

function sha256File(file) {
  return readFile(file).then((buffer) => ({ sha256: createHash('sha256').update(buffer).digest('hex').toUpperCase(), bytes: buffer.length }))
}

async function capture(browser, surface, size, theme, index) {
  const context = await browser.newContext({ viewport: size, deviceScaleFactor: 1, reducedMotion: 'reduce', locale: 'en-US' })
  const page = await context.newPage()
  const pageErrors = []
  const consoleErrors = []
  const requests = []
  page.on('pageerror', (error) => pageErrors.push(String(error)))
  page.on('console', (message) => { if (message.type() === 'error') consoleErrors.push(message.text()) })
  await page.addInitScript(() => { try { window.localStorage.clear() } catch {} })
  await page.route('**/api/**', (route) => fixtureRoute(route, requests))
  await page.route(/^https?:\/\/(?!127\.0\.0\.1(?::\d+)?(?:\/|$))/, (route) => route.abort())
  try {
    await waitForSettled(page, surface)
    if (theme === 'light') {
      await page.getByTestId('theme-toggle').click()
      await page.evaluate(() => document.fonts?.ready)
      await page.waitForTimeout(500)
    }
    const geometryA = await geometry(page)
    const stem = `${String(index).padStart(2, '0')}-${surface.id}-${theme}-${size.width}x${size.height}`
    const screenshotA = path.join(here, `${stem}-a.png`)
    const screenshotB = path.join(here, `${stem}-b.png`)
    await page.screenshot({ path: screenshotA, fullPage: true, animations: 'disabled' })
    await page.waitForTimeout(150)
    const geometryB = await geometry(page)
    await page.screenshot({ path: screenshotB, fullPage: true, animations: 'disabled' })
    const [hashA, hashB] = await Promise.all([sha256File(screenshotA), sha256File(screenshotB)])
    const viewport = await page.evaluate(() => ({ width: innerWidth, height: innerHeight, devicePixelRatio, scrollWidth: document.documentElement.scrollWidth, scrollHeight: document.documentElement.scrollHeight }))
    const result = {
      id: stem,
      surface: surface.id,
      route: surface.route,
      selector: surface.selector,
      themeRequested: theme,
      themeObserved: geometryB.theme,
      locale: geometryB.lang,
      viewport,
      screenshotA: { path: screenshotA, ...hashA },
      screenshotB: { path: screenshotB, ...hashB },
      pairByteIdentical: hashA.sha256 === hashB.sha256,
      geometryA,
      geometryB,
      pageErrors,
      consoleErrors,
      requests,
      candidateGolden: screenshotA,
    }
    return result
  } finally {
    await context.close()
  }
}

const browser = await chromium.launch({ headless: true, executablePath: process.env.TW_V2_CHROME || undefined })
const report = {
  status: 'CANDIDATE_GOLDEN / NOT_ACCEPTED',
  acceptance: 'NOT_ACCEPTED',
  scope: 'Local Playwright screenshots from the existing Vite app with an in-memory read-only fixture. A candidate baseline is not an owner-approved canonical golden.',
  origin,
  workspaceId,
  sourceAtCaptureStart: (() => { try { return sourceProvenance() } catch (error) { return { error: String(error) } } })(),
  runtime: { node: process.version, playwrightPackage: require(path.join(webRoot, 'node_modules', 'playwright', 'package.json')).version, browserVersion: browser.version(), userAgent: null },
  fixture: { type: 'offline-in-memory', payloadHashes, rowCount: rows.length, analyticsRows: analyticsFixture.ledger.length, holdoutAccess: false, executionCapability: false, externalNetwork: false },
  states: [],
  policy: {
    settle: 'networkidle, required root visible, fonts ready, reduced-motion, animation/transition suppression, 750ms after injection; 150ms between duplicate captures',
    pairPixel: { channelThreshold: 8, changedRatioLimit: 0.005, purpose: 'duplicate-capture reproducibility only; not cross-revision visual acceptance' },
    geometry: { tolerancePx: 1, invariants: ['viewport width/height', 'devicePixelRatio=1', 'document scrollWidth equals viewport width where no overflow is expected'] },
    candidateSelection: 'first capture (-a) is the candidate image; second capture (-b) is a same-state reproducibility receipt',
    canonicalRule: 'Do not promote without a pinned owner-approved route/state fixture, source revision, browser build, theme/locale, viewport/deviceScaleFactor and independent review.',
  },
}
try {
  await reportRuntimeBrowserUserAgent(browser, report)
  let index = 0
  for (const size of sizes) {
    for (const surface of surfaces) {
      for (const theme of ['dark', 'light']) {
        index += 1
        // capture() owns a short-lived context so each state has a clean storage and fixture lifecycle.
        report.states.push(await capture(browser, surface, size, theme, index))
      }
    }
  }
} finally {
  await browser.close()
}
report.sourceAtCaptureEnd = (() => { try { return sourceProvenance() } catch (error) { return { error: String(error) } } })()
report.sourceStableDuringCapture = JSON.stringify(report.sourceAtCaptureStart) === JSON.stringify(report.sourceAtCaptureEnd)
report.summary = {
  states: report.states.length,
  expectedStates: surfaces.length * sizes.length * 2,
  pairByteIdentical: report.states.filter((state) => state.pairByteIdentical).length,
  pageErrors: report.states.reduce((n, state) => n + state.pageErrors.length, 0),
  consoleErrors: report.states.reduce((n, state) => n + state.consoleErrors.length, 0),
  horizontalOverflowStates: report.states.filter((state) => state.viewport.scrollWidth > state.viewport.width).map((state) => state.id),
  noMutationRequests: report.states.every((state) => state.requests.every((request) => request.endpoint.startsWith('GET '))),
  sourceStableDuringCapture: report.sourceStableDuringCapture,
}
await writeFile(path.join(here, 'runtime.json'), `${JSON.stringify(report, null, 2)}\n`)
await writeFile(path.join(here, 'hashes.json'), `${JSON.stringify(report.states.map((state) => ({ id: state.id, candidate: state.screenshotA, duplicate: state.screenshotB, pairByteIdentical: state.pairByteIdentical })), null, 2)}\n`)
console.log(JSON.stringify({ status: report.status, summary: report.summary, sourceAtCaptureStart: report.sourceAtCaptureStart, sourceAtCaptureEnd: report.sourceAtCaptureEnd }, null, 2))
if (report.summary.pageErrors || report.summary.consoleErrors || report.summary.states !== report.summary.expectedStates || !report.summary.noMutationRequests) process.exitCode = 1

async function reportRuntimeBrowserUserAgent(browserInstance, target) {
  const context = await browserInstance.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 })
  const page = await context.newPage()
  target.runtime.userAgent = await page.evaluate(() => navigator.userAgent)
  await context.close()
}
