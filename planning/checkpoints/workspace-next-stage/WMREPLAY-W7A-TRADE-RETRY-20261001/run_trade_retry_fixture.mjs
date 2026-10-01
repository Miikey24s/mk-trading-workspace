import assert from 'node:assert/strict'
import { mkdir, writeFile } from 'node:fs/promises'
import { spawn } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const artifactDir = path.dirname(fileURLToPath(import.meta.url))
const here = path.resolve(artifactDir, '..', '..', '..', '..', 'projects', 'mt5-tradingview-backtester', 'foundation_v2', 'web')
const origin = 'http://127.0.0.1:4178'
const viteBin = path.join(here, 'node_modules', 'vite', 'bin', 'vite.js')
const pathToFileURL = (value) => new URL(`file:///${value.replaceAll('\\', '/')}`)
const { chromium } = await import(pathToFileURL(path.join(here, 'node_modules', 'playwright', 'index.mjs')).href)

const rows = [
  { timestamp: 1760000000, open: 1.0800, high: 1.0810, low: 1.0796, close: 1.0804, volume: 100 },
  { timestamp: 1760003600, open: 1.0804, high: 1.0816, low: 1.0801, close: 1.0810, volume: 110 },
]
const instrument = {
  instrument_id: 'EURUSD', asset_class: 'fx', base_ccy: 'EUR', quote_ccy: 'USD', account_ccy: 'USD',
  tick_size: '0.0001', pip_size: '0.0001', contract_size: '100000', quantity_min: '0.01', quantity_step: '0.01',
  effective_from_utc: '2026-01-01T00:00:00Z', effective_to_utc: '',
}
const posts = []
const requests = []
let scenario = 'retry'
let replayAttempts = 0
let datasetAttempts = 0

const sessionView = (id) => ({
  record_id: id,
  revision: 1,
  dataset_sha256: 'fixture-trade-retry-sha256',
  cutoff_timestamp: rows.at(-1).timestamp,
  visible_rows: rows,
  visible_row_count: rows.length,
  total_row_count: rows.length,
  has_future_rows: false,
  view_cursor_index: rows.length - 1,
  canonical_cursor_index: rows.length - 1,
  historical_view: false,
  payload: { dataset_id: 'ui-trade-retry-fixture', cursor_index: rows.length - 1, branch_id: `${id}-branch`, parent_session_id: null, status: 'paused', execution: null },
})

async function fulfill(route, status, payload) {
  await route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(payload) })
}

async function waitForServer() {
  for (let index = 0; index < 80; index += 1) {
    try {
      if ((await fetch(origin)).ok) return
    } catch {}
    await new Promise((resolve) => setTimeout(resolve, 100))
  }
  throw new Error('Vite did not start')
}

function workspaceUrl(id) {
  return `${origin}/?workspace=tenant-ui&view=trade&surface=workspace&session=${id}&dataset=ui-trade-retry-fixture&mode=Practice`
}

async function overflow(page) {
  return page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth)
}

async function waitUntilRetryButtonSettled(page, testId) {
  await page.waitForFunction((id) => {
    const button = document.querySelector(`[data-testid="${id}"]`)
    return Boolean(button && !button.disabled && button.offsetParent !== null)
  }, testId)
}

async function exhaustRetry(page, testId) {
  for (let attempt = 0; attempt < 3; attempt += 1) {
    await page.getByTestId(testId).click()
    if (attempt < 2) await waitUntilRetryButtonSettled(page, testId)
  }
  const button = page.getByTestId(testId)
  assert.equal(await button.isDisabled(), true, `${testId} must stop after three retries`)
  assert.equal(await button.innerText(), 'Đã hết lượt thử')
}

const server = spawn(process.execPath, [viteBin, '--host', '127.0.0.1', '--port', '4178', '--strictPort'], { cwd: here, stdio: ['ignore', 'pipe', 'pipe'] })
const serverErrors = []
server.stderr.on('data', (chunk) => serverErrors.push(String(chunk)))
let browser
let context
let page
const consoleErrors = []
try {
  await mkdir(artifactDir, { recursive: true })
  await waitForServer()
  browser = await chromium.launch({ headless: true })
  context = await browser.newContext({ viewport: { width: 1440, height: 900 } })
  await context.tracing.start({ screenshots: true, snapshots: true, sources: true })
  page = await context.newPage()
  page.on('console', (message) => { if (message.type() === 'error') consoleErrors.push(message.text()) })
  page.on('pageerror', (error) => consoleErrors.push(`pageerror:${error.message}`))
  page.on('request', (request) => {
    const url = new URL(request.url())
    if (url.pathname.startsWith('/api/')) requests.push({ method: request.method(), path: url.pathname })
  })
  await page.route('**/api/v2/data/datasets', async (route) => {
    requests.push({ method: route.request().method(), path: '/api/v2/data/datasets', scenario })
    if (route.request().method() !== 'GET') return fulfill(route, 405, { detail: 'method_not_allowed' })
    datasetAttempts += 1
    if (scenario === 'cap' || datasetAttempts === 1) return fulfill(route, 503, { detail: 'fixture_dataset_unavailable' })
    return fulfill(route, 200, { items: [{ dataset_id: 'ui-trade-retry-fixture', instrument_id: 'EURUSD', timeframe: 'H1', timeframe_seconds: 3600, quality_status: 'verified', holdout_status: 'locked', row_count: rows.length, instrument_spec: instrument }] })
  })
  await page.route('**/api/v2/replay/sessions/**', async (route) => {
    const request = route.request()
    const url = new URL(request.url())
    const pieces = url.pathname.split('/').filter(Boolean)
    const id = decodeURIComponent(pieces[4] || '')
    if (request.method() !== 'GET') {
      posts.push({ method: request.method(), path: url.pathname })
      return fulfill(route, 405, { detail: 'fixture_read_only' })
    }
    replayAttempts += 1
    if (scenario === 'cap' || replayAttempts === 1) return fulfill(route, 503, { detail: 'fixture_replay_unavailable' })
    return fulfill(route, 200, sessionView(id))
  })

  // Initial 503 responses must be visible as unknown context, without a
  // fabricated instrument or simulator defaults, and both GETs must recover.
  scenario = 'retry'
  replayAttempts = 0
  datasetAttempts = 0
  await page.goto(workspaceUrl('trade-retry'), { waitUntil: 'domcontentloaded' })
  await page.getByTestId('trade-replay-retry').waitFor()
  await page.getByTestId('trade-dataset-retry').waitFor()
  assert.equal(posts.length, 0, 'read-state fixture must not invoke simulator POSTs')
  await page.getByTestId('trade-replay-retry').click()
  await page.getByTestId('trade-context-unknown').waitFor()
  assert.match(await page.locator('[data-testid="trade-context-unknown"]').innerText(), /unavailable/i)
  assert.match(await page.locator('.trade-context-strip').innerText(), /Chưa xác định.*Unavailable/s)
  assert.equal(await page.getByRole('button', { name: 'Khởi tạo local simulator' }).count(), 0, 'unknown context must stay blocked')
  assert.equal(await overflow(page), 0)
  await page.screenshot({ path: path.join(artifactDir, 'trade-unknown-1440.png'), fullPage: true })

  await page.getByTestId('trade-dataset-retry').click()
  await page.getByRole('button', { name: 'Khởi tạo local simulator' }).waitFor()
  assert.match(await page.locator('.trade-context-strip').innerText(), /EURUSD.*Verified/s)
  assert.equal(posts.length, 0, 'successful GET recovery must remain read-only')
  await page.setViewportSize({ width: 390, height: 844 })
  assert.equal(await overflow(page), 0)
  await page.screenshot({ path: path.join(artifactDir, 'trade-ready-390.png'), fullPage: true })

  // A persistent GET failure must stop at the explicit three-retry bound.
  scenario = 'cap'
  replayAttempts = 0
  datasetAttempts = 0
  await page.goto(workspaceUrl('trade-cap'), { waitUntil: 'domcontentloaded' })
  await page.getByTestId('trade-replay-retry').waitFor()
  await page.getByTestId('trade-dataset-retry').waitFor()
  await exhaustRetry(page, 'trade-replay-retry')
  await exhaustRetry(page, 'trade-dataset-retry')
  assert.equal(await page.getByRole('button', { name: 'Khởi tạo local simulator' }).count(), 0, 'failed replay must stay blocked')
  assert.equal(await overflow(page), 0)
  await page.screenshot({ path: path.join(artifactDir, 'trade-retry-cap-390.png'), fullPage: true })

  const unexpectedConsoleErrors = consoleErrors.filter((message) => !/503/.test(message))
  assert.deepEqual(unexpectedConsoleErrors, [])
  assert.deepEqual(posts, [])
  const runtime = {
    status: 'PASS',
    fixture: 'local-intercepted-trade-read-error-retry',
    origin,
    checks: [
      'replay_and_dataset_503_are_explicit_unknown_states',
      'both_gets_recover_on_single_retry',
      'persistent_get_failures_stop_after_three_retries',
      'simulator_context_stays_blocked_when_unknown',
      'no_simulator_or_broker_posts',
      'responsive_1440_390_no_overflow',
    ],
    attempts: { retry: { replay: 2, dataset: 2 }, cap: { replay: replayAttempts, dataset: datasetAttempts } },
    requests,
    post_count: posts.length,
    console_errors: consoleErrors,
    server_errors: serverErrors,
    screenshots: ['trade-unknown-1440.png', 'trade-ready-390.png', 'trade-retry-cap-390.png', 'trade-retry-trace.zip'],
  }
  await writeFile(path.join(artifactDir, 'runtime.json'), JSON.stringify(runtime, null, 2) + '\n')
  console.log(JSON.stringify(runtime, null, 2))
} finally {
  if (context) {
    try { await context.tracing.stop({ path: path.join(artifactDir, 'trade-retry-trace.zip') }) } catch {}
  }
  await page?.close().catch(() => {})
  await context?.close().catch(() => {})
  await browser?.close().catch(() => {})
  server.kill()
}
