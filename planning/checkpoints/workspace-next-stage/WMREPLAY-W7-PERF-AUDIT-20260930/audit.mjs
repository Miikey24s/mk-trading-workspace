import { spawn } from 'node:child_process'
import { mkdir, writeFile } from 'node:fs/promises'
import { createRequire } from 'node:module'
import path from 'node:path'

const here = 'D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester/foundation_v2/web'
const out = 'D:/ANNAM/TradingWorkspace/planning/checkpoints/workspace-next-stage/WMREPLAY-W7-PERF-AUDIT-20260930'
const origin = 'http://127.0.0.1:5173'
const vite = path.join(here, 'node_modules', 'vite', 'bin', 'vite.js')
const { chromium } = createRequire(import.meta.url)(path.join(here, 'node_modules', 'playwright'))
await mkdir(out, { recursive: true })

function largeAnalytics(count = 5000) {
  const ledger = Array.from({ length: count }, (_, index) => {
    const pnl = index % 3 === 0 ? 12 : index % 3 === 1 ? -7 : 0
    const close = new Date(Date.UTC(2024, 0, 1) + index * 86_400_000).toISOString()
    return { trade_id: `large-${String(index + 1).padStart(5, '0')}`, open_time_utc: close, close_time_utc: close, net_pnl: pnl, realized_r: pnl / 10, side: index % 2 ? 'sell' : 'buy', source: { session_id: 'large-fixture' } }
  })
  let balance = 1000
  const curve = ledger.map((trade) => ({ trade_id: trade.trade_id, closed_trade_balance: (balance += trade.net_pnl) }))
  return {
    schema_version: 'analytics-read-model-v1',
    analytics_available: true,
    stale: false,
    provenance: { dataset_id: 'w7-large-fixture', dataset_sha256: 'sha-dataset', protocol_sha256: 'sha-protocol', metrics_schema_version: 'metrics-v2', split: 'research', playbook_id: 'fixture', status: 'fresh' },
    scope: { selected_trade_count: count, total_trade_count: count, observed_range: { first_close_utc: ledger[0].close_time_utc, last_close_utc: ledger.at(-1).close_time_utc }, balance_curve_scope: 'closed trades' },
    metrics: { closed_trade_count: count, net_pnl: ledger.reduce((sum, row) => sum + row.net_pnl, 0), closed_trade_balance_curve: curve, closed_trade_balance_max_drawdown: 7, definitions: { net_pnl: { question: 'Net result?', unit: 'account units', formula: 'sum(net_pnl)', source: 'ledger', version: 'v1' } } },
    ledger,
  }
}

const analyticsFixture = largeAnalytics()
const overviewFixture = { schema_version: 'overview-v1', counts: { datasets: 1, research_jobs: { completed: 1 }, records: { journal: 0, sessions: 1 } } }
const sessionFixture = { items: [], total: 0 }
const datasetFixture = { items: [] }

async function waitForServer() {
  for (let i = 0; i < 100; i += 1) {
    try { if ((await fetch(origin)).ok) return } catch {}
    await new Promise((resolve) => setTimeout(resolve, 100))
  }
  throw new Error('vite server did not start')
}

function json(route, status, payload) { return route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(payload) }) }

let server = null
const serverErrors = []
let browser
const report = { server: { port: 5173, reused: true }, routes: [], largeFixture: { requestedRows: analyticsFixture.ledger.length }, observations: [], errors: [] }
try {
  try { await fetch(origin) } catch {
    server = spawn(process.execPath, [vite, '--host', '127.0.0.1', '--port', '4190', '--strictPort'], { cwd: here, stdio: ['ignore', 'pipe', 'pipe'] })
    server.stderr.on('data', (chunk) => serverErrors.push(String(chunk)))
  }
  await waitForServer()
  browser = await chromium.launch({ headless: true, executablePath: process.env.TW_V2_CHROME || undefined })
  async function auditRoute(name, url, opts = {}) {
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
    const pageErrors = []
    const consoleErrors = []
    const tracePath = path.join(out, `${name}.trace.zip`)
    if (url.includes('job=large-fixture')) await page.context().tracing.start({ screenshots: true, snapshots: true })
    await page.addInitScript(() => {
      window.__w7LongTasks = []
      window.__w7NavStart = performance.now()
      try { new PerformanceObserver((list) => { for (const entry of list.getEntries()) window.__w7LongTasks.push({ duration: entry.duration, startTime: entry.startTime }) }).observe({ type: 'longtask', buffered: true }) } catch {}
    })
    page.on('pageerror', (error) => pageErrors.push(String(error)))
    page.on('console', (message) => { if (message.type() === 'error') consoleErrors.push(message.text()) })
    await page.route('**/api/**', async (route) => {
      const request = route.request()
      const requestUrl = new URL(request.url())
      if (requestUrl.pathname === '/api/v2/overview') return json(route, 200, overviewFixture)
      if (requestUrl.pathname === '/api/v2/replay/sessions') return json(route, 200, sessionFixture)
      if (requestUrl.pathname === '/api/v2/data/datasets') return json(route, 200, datasetFixture)
      if (requestUrl.pathname === '/api/v2/journal') return json(route, 200, { items: [] })
      if (requestUrl.pathname.endsWith('/analytics')) return json(route, 200, analyticsFixture)
      if (requestUrl.pathname.endsWith('/analytics.csv')) return route.fulfill({ status: 200, contentType: 'text/csv', body: 'trade_id,net_pnl\n' })
      return json(route, 503, { detail: 'fixture unavailable' })
    })
    const start = Date.now()
    await page.goto(`${origin}${url}`, { waitUntil: 'networkidle' })
    if (url.includes('job=large-fixture')) await page.getByText('N = 5.000', { exact: true }).waitFor({ timeout: 10000 })
    await page.waitForTimeout(500)
    const base = await page.evaluate(() => {
      const rect = (node) => { if (!node) return null; const r = node.getBoundingClientRect(); return { x: r.x, y: r.y, width: r.width, height: r.height } }
      const named = (node) => Boolean(node.getAttribute('aria-label') || node.getAttribute('title') || node.textContent.trim() || node.getAttribute('alt'))
      const allText = [...document.querySelectorAll('body *')].filter((node) => node.children.length === 0 && node.textContent.trim()).slice(0, 80)
      return {
        domNodes: document.querySelectorAll('*').length,
        bodyHeight: document.body.scrollHeight,
        scrollWidth: document.documentElement.scrollWidth,
        viewportWidth: window.innerWidth,
        unnamedButtons: [...document.querySelectorAll('button')].filter((node) => !named(node)).length,
        unnamedLinks: [...document.querySelectorAll('a')].filter((node) => !named(node)).length,
        focusable: document.querySelectorAll('button,a,input,select,textarea,[tabindex]:not([tabindex="-1"])').length,
        rootLang: document.documentElement.lang,
        theme: document.documentElement.dataset.twTheme,
        routeHeading: document.querySelector('h1,h2')?.textContent?.trim() || '',
        tableRows: document.querySelectorAll('tbody tr').length,
        canvasCount: document.querySelectorAll('canvas').length,
        svgCount: document.querySelectorAll('svg').length,
        scrollContainers: [...document.querySelectorAll('*')].map((node) => ({ selector: String(node.className || node.tagName).slice(0, 100), clientHeight: node.clientHeight, scrollHeight: node.scrollHeight, overflowY: getComputedStyle(node).overflowY })).filter((item) => item.scrollHeight > item.clientHeight + 4).sort((a, b) => b.scrollHeight - a.scrollHeight).slice(0, 8),
        firstTextSamples: allText.map((node) => node.textContent.trim().slice(0, 80)),
        root: rect(document.querySelector('#root')),
      }
    })
    const readContrast = () => page.evaluate(() => {
      const parse = (value) => { const m = value.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(',').map((part) => Number.parseFloat(part.trim())); return p.length >= 3 ? { rgb: p.slice(0, 3), alpha: p.length > 3 ? p[3] : 1 } : null }
      const luminance = (rgb) => { if (!rgb) return null; const c = rgb.map((v) => v / 255).map((v) => v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4); return .2126 * c[0] + .7152 * c[1] + .0722 * c[2] }
      const ratio = (fg, bg) => { const a = luminance(fg?.rgb); const b = luminance(bg?.rgb); return a === null || b === null ? null : (Math.max(a, b) + .05) / (Math.min(a, b) + .05) }
      const bodyBg = parse(getComputedStyle(document.body).backgroundColor)
      return ['h1', 'h2', 'p', 'button', 'a'].map((selector) => { const node = document.querySelector(selector); if (!node) return { selector, missing: true }; const style = getComputedStyle(node); const fg = parse(style.color); const rawBg = parse(style.backgroundColor); const bg = rawBg && rawBg.alpha > 0 ? rawBg : bodyBg; return { selector, text: node.textContent.trim().slice(0, 50), fg: style.color, bg: style.backgroundColor, ratio: ratio(fg, bg) } })
    })
    const themes = {}
    const themeToggle = page.getByTestId('theme-toggle')
    if (await themeToggle.count()) {
      themes.before = await page.evaluate(() => ({ root: document.documentElement.dataset.twTheme, bg: getComputedStyle(document.body).backgroundColor }))
      themes.contrastBefore = await readContrast()
      await themeToggle.click()
      await page.waitForTimeout(50)
      themes.after = await page.evaluate(() => ({ root: document.documentElement.dataset.twTheme, bg: getComputedStyle(document.body).backgroundColor }))
      themes.contrastAfter = await readContrast()
    }
    const zooms = {}
    for (const [scale, width] of [[1.25, 1152], [2, 720]]) {
      await page.setViewportSize({ width, height: 900 })
      await page.waitForTimeout(50)
      zooms[scale] = await page.evaluate(() => ({ scrollWidth: document.documentElement.scrollWidth, viewportWidth: window.innerWidth, overflow: document.documentElement.scrollWidth > window.innerWidth + 2, bodyHeight: document.body.scrollHeight }))
    }
    await page.setViewportSize({ width: 1440, height: 900 })
    const keyboard = await page.evaluate(() => {
      const first = document.querySelector('button,a,input,select,textarea,[tabindex]:not([tabindex="-1"])')
      if (!first) return { first: '', visible: false }
      first.focus()
      const style = getComputedStyle(first)
      return { first: first.getAttribute('aria-label') || first.textContent.trim().slice(0, 60), visible: document.activeElement === first, outline: style.outlineStyle, outlineWidth: style.outlineWidth, boxShadow: style.boxShadow }
    })
    let longSession = null
    if (url.includes('job=large-fixture')) {
      const outcome = page.getByLabel('Analytics outcome')
      const before = await page.evaluate(() => ({ nodes: document.querySelectorAll('*').length, rows: document.querySelectorAll('tbody tr').length, heap: performance.memory?.usedJSHeapSize ?? null }))
      for (let i = 0; i < 10; i += 1) {
        await outcome.selectOption(i % 2 ? 'win' : 'loss')
        await page.waitForTimeout(120)
      }
      const after = await page.evaluate(() => ({ nodes: document.querySelectorAll('*').length, rows: document.querySelectorAll('tbody tr').length, heap: performance.memory?.usedJSHeapSize ?? null }))
      longSession = { iterations: 10, before, after, nodeDelta: after.nodes - before.nodes, heapDelta: after.heap !== null && before.heap !== null ? after.heap - before.heap : null }
    }
    const perf = await page.evaluate(() => ({ navMs: Math.round(performance.now() - window.__w7NavStart), longTasks: window.__w7LongTasks, maxLongTaskMs: Math.max(0, ...window.__w7LongTasks.map((item) => item.duration)), resourceCount: performance.getEntriesByType('resource').length }))
    const screenshot = path.join(out, `${name}-1440.png`)
    await page.screenshot({ path: screenshot, fullPage: true })
    const viewports = {}
    for (const [width, height] of [[1280, 800], [768, 1024], [390, 844]]) {
      await page.setViewportSize({ width, height })
      await page.waitForTimeout(40)
      viewports[width] = await page.evaluate(() => ({ scrollWidth: document.documentElement.scrollWidth, viewportWidth: window.innerWidth, overflow: document.documentElement.scrollWidth > window.innerWidth + 2, bodyHeight: document.body.scrollHeight }))
    }
    if (url.includes('job=large-fixture')) await page.context().tracing.stop({ path: tracePath })
    report.routes.push({ name, url, base, themes, zooms, keyboard, perf, longSession, viewports, screenshot, trace: url.includes('job=large-fixture') ? tracePath : null, pageErrors, consoleErrors, elapsedMs: Date.now() - start })
    await page.close()
  }

  await auditRoute('overview-small', '/?view=overview&workspace=w7-perf')
  await auditRoute('analytics-large-5000', '/?view=analytics&workspace=w7-perf&job=large-fixture')
  await auditRoute('live-denied', '/?view=live&workspace=w7-perf')
} catch (error) {
  report.errors.push(String(error?.stack || error))
} finally {
  if (browser) await browser.close()
  if (server) {
    server.kill()
    await new Promise((resolve) => server.once('exit', resolve))
  }
}
report.server.stderr = serverErrors
await writeFile(path.join(out, 'metrics.json'), JSON.stringify(report, null, 2))
console.log(JSON.stringify(report, null, 2))
if (report.errors.length || report.routes.some((route) => route.pageErrors.length)) process.exitCode = 1
