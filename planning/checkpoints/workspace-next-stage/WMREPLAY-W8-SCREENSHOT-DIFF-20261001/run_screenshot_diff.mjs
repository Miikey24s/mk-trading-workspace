import { mkdir, writeFile } from 'node:fs/promises'
import { createRequire } from 'node:module'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const artifactDir = path.dirname(fileURLToPath(import.meta.url))
const webDir = path.resolve(artifactDir, '../../../../projects/mt5-tradingview-backtester/foundation_v2/web')
const origin = 'http://127.0.0.1:5173'
const { chromium } = createRequire(import.meta.url)(path.join(webDir, 'node_modules', 'playwright'))

await mkdir(artifactDir, { recursive: true })

function largeAnalytics(count = 5000) {
  const ledger = Array.from({ length: count }, (_, index) => {
    const pnl = index % 3 === 0 ? 12 : index % 3 === 1 ? -7 : 0
    const close = new Date(Date.UTC(2024, 0, 1) + index * 86_400_000).toISOString()
    return {
      trade_id: `large-${String(index + 1).padStart(5, '0')}`,
      open_time_utc: close,
      close_time_utc: close,
      net_pnl: pnl,
      realized_r: pnl / 10,
      side: index % 2 ? 'sell' : 'buy',
      source: { session_id: 'large-fixture' },
    }
  })
  let balance = 1000
  const curve = ledger.map((trade) => ({ trade_id: trade.trade_id, closed_trade_balance: (balance += trade.net_pnl) }))
  return {
    schema_version: 'analytics-read-model-v1',
    analytics_available: true,
    stale: false,
    provenance: { dataset_id: 'w8-screenshot-diff', dataset_sha256: 'sha-dataset', protocol_sha256: 'sha-protocol', metrics_schema_version: 'metrics-v2', split: 'research', playbook_id: 'fixture', status: 'fresh' },
    scope: { selected_trade_count: count, total_trade_count: count, observed_range: { first_close_utc: ledger[0].close_time_utc, last_close_utc: ledger.at(-1).close_time_utc }, balance_curve_scope: 'closed trades' },
    metrics: { closed_trade_count: count, net_pnl: ledger.reduce((sum, row) => sum + row.net_pnl, 0), closed_trade_balance_curve: curve, closed_trade_balance_max_drawdown: 7, definitions: { net_pnl: { question: 'Net result?', unit: 'account units', formula: 'sum(net_pnl)', source: 'ledger', version: 'v1' } } },
    ledger,
  }
}

const overviewFixture = { schema_version: 'overview-v1', counts: { datasets: 1, research_jobs: { completed: 1 }, records: { journal: 0, sessions: 1 } } }
const analyticsFixture = largeAnalytics()
const sessionFixture = { items: [], total: 0 }
const datasetFixture = { items: [] }

function json(route, status, payload) {
  return route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(payload) })
}

async function waitForStable(page, route) {
  await page.goto(`${origin}${route}`, { waitUntil: 'networkidle' })
  if (route.includes('job=large-fixture')) await page.getByText('N = 5.000', { exact: true }).waitFor({ timeout: 15_000 })
  await page.waitForTimeout(900)
  await page.evaluate(() => document.fonts?.ready)
  await page.addStyleTag({ content: '*,:before,:after{animation:none!important;transition:none!important;caret-color:transparent!important;scroll-behavior:auto!important}' })
  await page.waitForTimeout(250)
}

function stableSelectors() {
  return ['#root', '.fx-shell', '.fx-topbar', '.fx-rail', '.fx-content', '.fx-content main', 'h1', '[role="tablist"]', 'tbody', '.analytics-hero', '.rd-panel-head']
}

async function geometry(page) {
  return page.evaluate((selectors) => {
    const rect = (node) => {
      if (!node) return null
      const r = node.getBoundingClientRect()
      return { x: Number(r.x.toFixed(3)), y: Number(r.y.toFixed(3)), width: Number(r.width.toFixed(3)), height: Number(r.height.toFixed(3)) }
    }
    const result = {}
    for (const selector of selectors) {
      const nodes = [...document.querySelectorAll(selector)]
      result[selector] = nodes.slice(0, 4).map(rect)
    }
    return {
      viewport: { width: window.innerWidth, height: window.innerHeight },
      document: { scrollWidth: document.documentElement.scrollWidth, scrollHeight: document.documentElement.scrollHeight },
      selectors: result,
    }
  }, stableSelectors())
}

async function captureState(context, definition) {
  const page = await context.newPage()
  await page.setViewportSize({ width: definition.width, height: definition.height })
  await page.addInitScript(() => { try { window.localStorage.clear() } catch {} })
  const pageErrors = []
  const consoleErrors = []
  await page.emulateMedia({ reducedMotion: 'reduce' })
  page.on('pageerror', (error) => pageErrors.push(String(error)))
  page.on('console', (message) => { if (message.type() === 'error') consoleErrors.push(message.text()) })
  await page.route('**/api/**', async (route) => {
    const requestUrl = new URL(route.request().url())
    if (route.request().method() !== 'GET') return json(route, 405, { detail: 'method not allowed in read-only screenshot fixture' })
    if (requestUrl.pathname === '/api/v2/overview') return json(route, 200, overviewFixture)
    if (requestUrl.pathname === '/api/v2/replay/sessions') return json(route, 200, sessionFixture)
    if (requestUrl.pathname === '/api/v2/data/datasets') return json(route, 200, datasetFixture)
    if (requestUrl.pathname === '/api/v2/journal') return json(route, 200, { items: [] })
    if (requestUrl.pathname.endsWith('/analytics')) return json(route, 200, analyticsFixture)
    return json(route, 503, { detail: 'fixture unavailable' })
  })
  await waitForStable(page, definition.route)
  if (definition.theme === 'light') {
    const toggle = page.getByTestId('theme-toggle')
    if (!(await toggle.count())) throw new Error(`missing theme toggle for ${definition.id}`)
    await toggle.click()
    await page.waitForTimeout(500)
    await page.evaluate(() => document.fonts?.ready)
    await page.waitForTimeout(250)
  }
  const runA = path.join(artifactDir, `${definition.id}-a.png`)
  const runB = path.join(artifactDir, `${definition.id}-b.png`)
  const geometryA = await geometry(page)
  await page.screenshot({ path: runA, fullPage: true, animations: 'disabled' })
  await page.waitForTimeout(120)
  const geometryB = await geometry(page)
  await page.screenshot({ path: runB, fullPage: true, animations: 'disabled' })
  const state = {
    id: definition.id,
    route: definition.route,
    theme: definition.theme,
    viewport: { width: definition.width, height: definition.height },
    screenshots: [runA, runB],
    geometryA,
    geometryB,
    pageErrors,
    consoleErrors,
    title: await page.title(),
    lang: await page.locator('html').getAttribute('lang'),
    themeValue: await page.locator('html').getAttribute('data-tw-theme'),
    textFingerprint: (await page.locator('body').innerText()).replace(/\s+/g, ' ').trim().slice(0, 600),
  }
  await page.close()
  return state
}

const states = [
  { id: 'overview-dark-1440x900', route: '/?view=overview&workspace=w8-screenshot-diff', theme: 'dark', width: 1440, height: 900 },
  { id: 'overview-dark-390x844', route: '/?view=overview&workspace=w8-screenshot-diff', theme: 'dark', width: 390, height: 844 },
  { id: 'overview-light-1440x900', route: '/?view=overview&workspace=w8-screenshot-diff', theme: 'light', width: 1440, height: 900 },
  { id: 'overview-light-390x844', route: '/?view=overview&workspace=w8-screenshot-diff', theme: 'light', width: 390, height: 844 },
  { id: 'analytics-dark-1440x900', route: '/?view=analytics&workspace=w8-screenshot-diff&job=large-fixture', theme: 'dark', width: 1440, height: 900 },
  { id: 'analytics-dark-390x844', route: '/?view=analytics&workspace=w8-screenshot-diff&job=large-fixture', theme: 'dark', width: 390, height: 844 },
  { id: 'analytics-light-1440x900', route: '/?view=analytics&workspace=w8-screenshot-diff&job=large-fixture', theme: 'light', width: 1440, height: 900 },
  { id: 'analytics-light-390x844', route: '/?view=analytics&workspace=w8-screenshot-diff&job=large-fixture', theme: 'light', width: 390, height: 844 },
]

const browser = await chromium.launch({ headless: true, executablePath: process.env.TW_V2_CHROME || undefined })
const context = await browser.newContext()
const result = {
  method: {
    pixel: { channelThreshold: 8, criterion: 'pixel is changed when max RGB channel absolute difference > 8', acceptableRatio: 0.005, note: 'threshold tolerates anti-aliasing/subpixel raster noise; identical-state screenshots are the baseline pair, not a product visual golden.' },
    geometry: { perCoordinateTolerancePx: 1, criterion: 'all captured stable selector rect coordinates/dimensions remain within 1 CSS px', acceptableRatio: 0, note: 'viewport/document dimensions are exact invariants.' },
    transition: 'prefers-reduced-motion=reduce plus injected animation/transition/caret suppression; fonts awaited; 900 ms settle before capture and 120 ms between pair.'
  },
  states: [],
  server: { origin, reused: true },
  fixture: { overview: overviewFixture, analyticsRows: analyticsFixture.ledger.length },
}
try {
  await context.tracing.start({ screenshots: true, snapshots: true, sources: true })
  for (const definition of states) {
    result.states.push(await captureState(context, definition))
  }
  await context.tracing.stop({ path: path.join(artifactDir, 'screenshot-diff.trace.zip') })
} finally {
  await browser.close()
}
await writeFile(path.join(artifactDir, 'runtime.json'), JSON.stringify(result, null, 2))
console.log(JSON.stringify(result, null, 2))
if (result.states.some((state) => state.pageErrors.length || state.consoleErrors.length)) process.exitCode = 1


