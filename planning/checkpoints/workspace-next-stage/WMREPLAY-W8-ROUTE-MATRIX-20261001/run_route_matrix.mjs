import assert from 'node:assert/strict'
import { spawn } from 'node:child_process'
import { mkdir, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const here = path.dirname(fileURLToPath(import.meta.url))
const webRoot = path.resolve(here, '..', '..', '..', '..', 'projects', 'mt5-tradingview-backtester', 'foundation_v2', 'web')
const { chromium } = await import(pathToFileURL(path.join(webRoot, 'node_modules', 'playwright', 'index.mjs')).href)
const origin = 'http://127.0.0.1:4193'
const rows = Array.from({ length: 30 }, (_, index) => {
  const open = 1.08 + index * 0.0001
  return { timestamp: 1710000000 + index * 60, open, high: open + 0.00025, low: open - 0.0002, close: open + 0.0001, volume: 100 + index }
})
const dataset = { dataset_id: 'matrix-local-fixture', instrument_id: 'EURUSD', timeframe: 'M1', quality_status: 'fixture-only', holdout_access: false, holdout_policy: { mode: 'none' }, row_count: rows.length, provider_id: 'local-fixture', artifact_sha256: 'sha256-matrix-fixture' }
const session = { record_id: 'matrix-session', revision: 1, payload: { dataset_id: dataset.dataset_id, cursor_index: 19, branch_id: 'matrix-branch', parent_session_id: null, status: 'active' }, dataset_sha256: dataset.artifact_sha256, cutoff_timestamp: rows[19].timestamp, visible_rows: rows.slice(0, 20), visible_row_count: 20, total_row_count: rows.length, has_future_rows: true, view_cursor_index: 19, canonical_cursor_index: 19, historical_view: false }
const routes = [
  { id: 'overview', query: 'view=overview', selector: '[data-testid="dashboard-data-state"]' },
  { id: 'sessions', query: 'view=replay&select=1', selector: '[data-testid="replay-session-dashboard"]' },
  { id: 'replay-empty', query: 'view=replay&surface=workspace&select=1', selector: '[data-testid="replay-empty-actions"]' },
  { id: 'replay-loaded', query: 'view=replay&surface=workspace&session=matrix-session', selector: '[data-testid="replay-chart"]' },
  { id: 'replay-error', query: 'view=replay&surface=workspace&session=missing-session', selector: '.replay-error' },
  { id: 'trade', query: 'view=trade&surface=workspace&session=matrix-session', selector: '[data-testid="trade-workspace"]' },
  { id: 'analytics', query: 'view=analytics&surface=workspace', selector: '[data-testid="analytics-workspace"]' },
  { id: 'journal', query: 'view=journal', selector: '[data-testid="journal-workspace"]' },
  { id: 'research', query: 'view=research', selector: '[data-testid="research-root"]' },
  { id: 'data', query: 'view=data', selector: '[data-testid="data-desk-root"]' },
  { id: 'risk', query: 'view=risk', selector: '[data-testid="risk-workspace"]' },
  { id: 'playbook', query: 'view=playbook', selector: '[data-testid="playbook-root"]' },
  { id: 'settings', query: 'view=settings', selector: '[data-testid="settings-workspace"]' },
  { id: 'learn', query: 'view=learn', selector: '.learn-shell' },
  { id: 'prop', query: 'view=testing', selector: '.prop-shell' },
]
const sizes = [{ width: 1440, height: 900 }, { width: 768, height: 900 }, { width: 390, height: 844 }]

function json(body, status = 200) { return { status, contentType: 'application/json', body: JSON.stringify(body) } }
async function waitForServer(stderr) {
  for (let attempt = 0; attempt < 100; attempt += 1) {
    try { if ((await fetch(origin)).ok) return } catch {}
    await new Promise((resolve) => setTimeout(resolve, 100))
  }
  throw new Error(`isolated Vite failed to start: ${stderr.join('')}`)
}
async function fixtureRoute(route, caseId, requests) {
  const request = route.request()
  const url = new URL(request.url())
  const endpoint = `${request.method()} ${url.pathname}`
  requests.push(endpoint)
  assert.equal(request.headers()['x-workspace-id'], 'tenant-matrix', `workspace header: ${endpoint}`)
  assert.equal(request.method(), 'GET', `unexpected mutation: ${endpoint}`)
  let payload = { items: [] }
  let status = 200
  if (url.pathname === '/api/v2/overview') payload = { counts: { datasets: 1, research_jobs: {}, records: {} } }
  else if (url.pathname === '/api/v2/data/datasets') payload = { items: caseId === 'replay-empty' ? [] : [dataset], holdout_access: false }
  else if (url.pathname === '/api/v2/data/providers') payload = { items: [] }
  else if (url.pathname === '/api/v2/replay/sessions') payload = { items: [] }
  else if (url.pathname.startsWith('/api/v2/replay/sessions/')) {
    if (url.pathname === '/api/v2/replay/sessions/matrix-session') payload = session
    else { payload = { detail: 'matrix_fixture_session_not_found' }; status = 503 }
  } else if (url.pathname === '/api/v2/session/status') payload = { status: 'unavailable', authenticated: false, workspace_id: 'tenant-matrix' }
  else if (url.pathname === '/api/v2/connectors/notion/oauth/status') payload = { status: 'unavailable', connected: false }
  else if (url.pathname === '/api/v2/learn/overview') payload = { resources: [], progress: null }
  else if (url.pathname === '/api/v2/learn/glossary') payload = { items: [] }
  else if (url.pathname === '/api/v2/research/engines') payload = { items: [] }
  else if (url.pathname.startsWith('/api/v2/prop/')) payload = { items: [], sessions: [], reports: [] }
  else if (url.pathname === '/api/v2/journal' || url.pathname === '/api/v2/playbooks') payload = { items: [] }
  else if (url.pathname.startsWith('/api/v2/')) payload = { items: [] }
  return route.fulfill(json(payload, status))
}

async function inspect(page, routeCase, size) {
  const selector = page.locator(routeCase.selector)
  await selector.waitFor({ state: 'visible', timeout: 10000 })
  if (routeCase.id === 'replay-loaded') {
    await page.locator('[data-testid="replay-chart"][data-visible-row-count="20"]').waitFor({ timeout: 10000 })
  }
  const metrics = await page.evaluate((rootSelector) => {
    const root = document.querySelector(rootSelector)
    const rect = root?.getBoundingClientRect()
    const html = document.documentElement
    const shell = document.querySelector('[data-testid="fxreplay-shell"]')
    return {
      viewport: { width: innerWidth, height: innerHeight },
      documentWidth: html.scrollWidth,
      overflowX: html.scrollWidth - innerWidth,
      root: rect ? { x: rect.x, width: rect.width, height: rect.height } : null,
      shellClass: shell?.className || '',
      heading: document.querySelector('main h1')?.textContent?.trim() || document.querySelector('h1')?.textContent?.trim() || '',
      chartRows: document.querySelector('[data-testid="replay-chart"]')?.getAttribute('data-visible-row-count') || null,
      chartWidth: document.querySelector('[data-testid="replay-chart"]')?.getBoundingClientRect().width || null,
      hasBrokerLock: document.body.innerText.includes('Broker locked') || document.body.innerText.includes('không gửi lệnh'),
    }
  }, routeCase.selector)
  assert.ok(metrics.root && metrics.root.width > 0, `${routeCase.id}/${size.width}: root missing`)
  assert.ok(metrics.overflowX <= 2, `${routeCase.id}/${size.width}: horizontal overflow ${metrics.overflowX}`)
  if (routeCase.id === 'replay-loaded') {
    assert.equal(metrics.chartRows, '20')
    assert.equal(metrics.hasBrokerLock, true)
    if (size.width === 390) assert.ok(metrics.chartWidth > 250, `390 chart width ${metrics.chartWidth}`)
  }
  return metrics
}

async function main() {
  await mkdir(here, { recursive: true })
  const stderr = []
  const server = spawn(process.execPath, [path.join(webRoot, 'node_modules', 'vite', 'bin', 'vite.js'), '--host', '127.0.0.1', '--port', '4193', '--strictPort'], { cwd: webRoot, stdio: ['ignore', 'pipe', 'pipe'] })
  server.stderr.on('data', (data) => stderr.push(String(data)))
  let browser
  let context
  const results = []
  const unexpected = []
  const transitions = []
  const trace = path.join(here, 'route-matrix-trace.zip')
  try {
    await waitForServer(stderr)
    browser = await chromium.launch({ headless: true })
    context = await browser.newContext({ viewport: sizes[0], reducedMotion: 'reduce' })
    await context.tracing.start({ screenshots: true, snapshots: true, sources: false })
    for (const size of sizes) {
      for (const routeCase of routes) {
        const page = await context.newPage()
        const errors = []
        const consoleErrors = []
        const requests = []
        page.on('pageerror', (error) => errors.push(String(error)))
        page.on('console', (message) => { if (message.type() === 'error') consoleErrors.push(message.text()) })
        await page.addInitScript(() => window.localStorage.clear())
        await page.route('**/api/**', (route) => fixtureRoute(route, routeCase.id, requests))
        await page.route(/^https?:\/\/(?!127\.0\.0\.1:4193)/, (route) => route.abort())
        try {
          await page.setViewportSize(size)
          await page.goto(`${origin}/?${routeCase.query}&workspace=tenant-matrix`, { waitUntil: 'domcontentloaded' })
          const metrics = await inspect(page, routeCase, size)
          const unexpectedConsoleErrors = consoleErrors.filter((message) => !(routeCase.id === 'replay-error' && /Failed to load resource.*503/.test(message)))
          assert.deepEqual(errors, [], `${routeCase.id}/${size.width}: page errors`)
          assert.deepEqual(unexpectedConsoleErrors, [], `${routeCase.id}/${size.width}: console errors`)
          if (size.width === 390 || routeCase.id === 'replay-loaded' && size.width === 1440) await page.screenshot({ path: path.join(here, `${routeCase.id}-${size.width}.png`), fullPage: true })
          results.push({ id: routeCase.id, width: size.width, status: 'PASS', metrics, requests, pageErrors: errors, consoleErrors: unexpectedConsoleErrors })
        } catch (error) {
          unexpected.push({ id: routeCase.id, width: size.width, error: String(error), requests, pageErrors: errors, consoleErrors })
          results.push({ id: routeCase.id, width: size.width, status: 'FAIL', requests, pageErrors: errors, consoleErrors })
        } finally { await page.close() }
      }
    }
    const journey = await context.newPage()
    const journeyErrors = []
    const journeyRequests = []
    let journeyMode = 'journey'
    journey.on('pageerror', (error) => journeyErrors.push(String(error)))
    journey.on('console', (message) => { if (message.type() === 'error') journeyErrors.push(message.text()) })
    await journey.route('**/api/**', (route) => fixtureRoute(route, journeyMode, journeyRequests))
    await journey.setViewportSize({ width: 390, height: 844 })
    try {
      await journey.goto(`${origin}/?view=overview&workspace=tenant-matrix`, { waitUntil: 'domcontentloaded' })
      await journey.getByTestId('dashboard-data-state').waitFor()
      const themeBefore = await journey.getByTestId('fxreplay-shell').getAttribute('data-theme')
      await journey.getByTestId('theme-toggle').click()
      const themeAfter = await journey.getByTestId('fxreplay-shell').getAttribute('data-theme')
      assert.notEqual(themeAfter, themeBefore)
      await journey.reload({ waitUntil: 'domcontentloaded' })
      assert.equal(await journey.getByTestId('fxreplay-shell').getAttribute('data-theme'), themeAfter)
      transitions.push({ id: 'theme-toggle-reload', status: 'PASS', from: themeBefore, to: themeAfter })

      await journey.locator('.fx-dashboard-card').first().click()
      await journey.getByTestId('replay-session-dashboard').waitFor()
      transitions.push({ id: 'dashboard-to-sessions', status: 'PASS', url: journey.url() })

      await journey.locator('.fx-subnav-link').filter({ hasText: 'Analytics' }).click()
      await journey.getByTestId('analytics-session-dashboard').waitFor()
      await journey.getByText('Show demo data').click()
      await journey.getByTestId('analytics-demo').waitFor()
      transitions.push({ id: 'sessions-to-analytics-demo', status: 'PASS', url: journey.url(), demoLabeled: true })

      journeyMode = 'replay-empty'
      await journey.goto(`${origin}/?view=replay&surface=workspace&select=1&workspace=tenant-matrix`, { waitUntil: 'domcontentloaded' })
      await journey.getByTestId('replay-empty-actions').waitFor()
      await journey.getByText('Mở Data Desk →').click()
      await journey.getByTestId('data-desk-root').waitFor()
      transitions.push({ id: 'replay-empty-to-data', status: 'PASS', url: journey.url() })

      journeyMode = 'journey'
      await journey.goto(`${origin}/?view=replay&surface=workspace&session=matrix-session&workspace=tenant-matrix`, { waitUntil: 'domcontentloaded' })
      await journey.getByTestId('replay-chart').waitFor()
      await journey.locator('.fx-subnav-link').filter({ hasText: 'Sessions' }).click()
      await journey.getByTestId('replay-session-dashboard').waitFor()
      transitions.push({ id: 'replay-chart-to-sessions', status: 'PASS', url: journey.url() })
      assert.deepEqual(journeyErrors, [], 'journey page/console errors')
    } catch (error) {
      unexpected.push({ id: 'journey', width: 390, error: String(error), pageErrors: journeyErrors, requests: journeyRequests })
      transitions.push({ id: 'journey', status: 'FAIL' })
    } finally { await journey.close() }
    const report = { status: unexpected.length ? 'FAIL' : 'PASS', scope: 'local Playwright fixture route matrix, not integrated product acceptance', origin, sizes, routeCount: routes.length, caseCount: results.length, passed: results.filter((item) => item.status === 'PASS').length, failed: unexpected.length, transitions, results, failures: unexpected }
    await writeFile(path.join(here, 'runtime.json'), `${JSON.stringify(report, null, 2)}\n`)
    console.log(JSON.stringify({ status: report.status, routeCount: report.routeCount, caseCount: report.caseCount, passed: report.passed, failed: report.failed, transitions, failures: unexpected }, null, 2))
    if (unexpected.length) process.exitCode = 1
  } finally {
    await context?.tracing.stop({ path: trace }).catch(() => {})
    await context?.close().catch(() => {})
    await browser?.close().catch(() => {})
    server.kill('SIGTERM')
    if (stderr.length) process.stderr.write(stderr.join(''))
  }
}

main().catch((error) => { console.error(error); process.exitCode = 1 })
