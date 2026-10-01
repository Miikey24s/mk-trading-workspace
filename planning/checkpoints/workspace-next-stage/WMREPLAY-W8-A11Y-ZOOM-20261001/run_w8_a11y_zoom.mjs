import { spawn } from 'node:child_process'
import { mkdir, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { createRequire } from 'node:module'

const here = 'D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester/foundation_v2/web'
const out = 'D:/ANNAM/TradingWorkspace/planning/checkpoints/workspace-next-stage/WMREPLAY-W8-A11Y-ZOOM-20261001'
const origin = 'http://127.0.0.1:4192'
const vite = path.join(here, 'node_modules', 'vite', 'bin', 'vite.js')
const { chromium } = createRequire(import.meta.url)(path.join(here, 'node_modules', 'playwright'))

await mkdir(out, { recursive: true })

function overview() {
  return { schema_version: 'overview-v1', counts: { datasets: 1, research_jobs: { completed: 1 }, records: { journal: 0, sessions: 1 } } }
}

function analytics() {
  const ledger = Array.from({ length: 120 }, (_, index) => {
    const pnl = index % 3 === 0 ? 12 : index % 3 === 1 ? -7 : 0
    const close = new Date(Date.UTC(2024, 0, 1) + index * 86_400_000).toISOString()
    return { trade_id: `w8-${index + 1}`, open_time_utc: close, close_time_utc: close, net_pnl: pnl, realized_r: pnl / 10, side: index % 2 ? 'sell' : 'buy', source: { session_id: 'w8-fixture' } }
  })
  let balance = 1000
  return {
    schema_version: 'analytics-read-model-v1', analytics_available: true, stale: false,
    provenance: { dataset_id: 'w8-fixture', dataset_sha256: 'sha-w8', protocol_sha256: 'sha-protocol', metrics_schema_version: 'metrics-v2', split: 'research', playbook_id: 'fixture', status: 'fresh' },
    scope: { selected_trade_count: ledger.length, total_trade_count: ledger.length, observed_range: { first_close_utc: ledger[0].close_time_utc, last_close_utc: ledger.at(-1).close_time_utc }, balance_curve_scope: 'closed trades' },
    metrics: { closed_trade_count: ledger.length, net_pnl: ledger.reduce((sum, row) => sum + row.net_pnl, 0), closed_trade_balance_curve: ledger.map((row) => ({ trade_id: row.trade_id, closed_trade_balance: (balance += row.net_pnl) })), closed_trade_balance_max_drawdown: 7, definitions: { net_pnl: { question: 'Net result?', unit: 'account units', formula: 'sum(net_pnl)', source: 'ledger', version: 'v1' } } },
    ledger,
  }
}

function json(route, status, payload) {
  return route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(payload) })
}

async function waitForServer() {
  for (let i = 0; i < 100; i += 1) {
    try { if ((await fetch(origin)).ok) return } catch {}
    await new Promise((resolve) => setTimeout(resolve, 100))
  }
  throw new Error('vite server did not start')
}

function visible(node) {
  const style = getComputedStyle(node)
  const rect = node.getBoundingClientRect()
  return style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0
}

async function inspectA11y(page) {
  const client = await page.context().newCDPSession(page)
  let tree = null
  let treeError = null
  try { tree = await client.send('Accessibility.getFullAXTree') } catch (error) { treeError = String(error?.message || error) }
  const dom = await page.evaluate(() => {
    const isVisible = (node) => {
      const style = getComputedStyle(node)
      const rect = node.getBoundingClientRect()
      return style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0
    }
    const controls = [...document.querySelectorAll('button,a,input,select,textarea,[role="button"],[role="link"],[role="checkbox"],[role="radio"],[role="tab"]')]
    const labelOf = (node) => (node.getAttribute('aria-label') || node.getAttribute('title') || node.getAttribute('alt') || node.labels?.[0]?.textContent || node.textContent || '').replace(/\s+/g, ' ').trim()
    const headings = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].map((node) => ({ level: Number(node.tagName.slice(1)), text: node.textContent.trim().slice(0, 100) }))
    const headingSkips = headings.slice(1).filter((heading, index) => heading.level > headings[index].level + 1)
    const ariaHiddenFocusable = [...document.querySelectorAll('[aria-hidden="true"] button,[aria-hidden="true"] a,[aria-hidden="true"] input,[aria-hidden="true"] select,[aria-hidden="true"] textarea,[aria-hidden="true"] [tabindex]:not([tabindex="-1"])')].filter(isVisible).length
    return {
      duplicateIds: [...document.querySelectorAll('[id]')].map((node) => node.id).filter((id, index, all) => id && all.indexOf(id) !== index),
      controls: controls.filter(isVisible).map((node) => ({ tag: node.tagName.toLowerCase(), role: node.getAttribute('role') || '', name: labelOf(node).slice(0, 120), disabled: node.hasAttribute('disabled') || node.getAttribute('aria-disabled') === 'true' })),
      unnamedControls: controls.filter(isVisible).filter((node) => !labelOf(node)),
      headings,
      headingSkips,
      ariaHiddenFocusable,
      landmarkCount: document.querySelectorAll('main,nav,header,footer,aside,[role="main"],[role="navigation"],[role="banner"],[role="complementary"]').length,
      lang: document.documentElement.lang,
    }
  })
  const axNodes = tree?.nodes || []
  const axSummary = axNodes.map((node) => ({ role: node.role?.value || '', name: node.name?.value || '', ignored: Boolean(node.ignored) })).filter((node) => !node.ignored)
  return { cdpAvailable: Boolean(tree), cdpError: treeError, nodeCount: axSummary.length, roleCounts: Object.fromEntries([...new Set(axSummary.map((node) => node.role))].map((role) => [role, axSummary.filter((node) => node.role === role).length])), sample: axSummary.slice(0, 40), dom: { ...dom, unnamedControls: dom.unnamedControls.length } }
}

async function inspectPage(browser, name, url, viewport) {
  const context = await browser.newContext({ viewport, deviceScaleFactor: 1 })
  const page = await context.newPage()
  const pageErrors = []
  const consoleErrors = []
  const tracePath = path.join(out, `${name}-${viewport.width}.trace.zip`)
  page.on('pageerror', (error) => pageErrors.push(String(error)))
  page.on('console', (message) => { if (message.type() === 'error') consoleErrors.push(message.text()) })
  await context.tracing.start({ screenshots: true, snapshots: true })
  await page.route('**/api/**', async (route) => {
    const request = route.request()
    const requestUrl = new URL(request.url())
    const method = request.method()
    if (method !== 'GET') return json(route, 405, { detail: 'read_only_w8_fixture' })
    if (requestUrl.pathname === '/api/v2/overview') return json(route, 200, overview())
    if (requestUrl.pathname.endsWith('/analytics')) return json(route, 200, analytics())
    if (requestUrl.pathname.endsWith('/analytics.csv')) return route.fulfill({ status: 200, contentType: 'text/csv', body: 'trade_id,net_pnl\nw8-1,12\n' })
    if (requestUrl.pathname === '/api/v2/replay/sessions') return json(route, 200, { items: [], total: 0 })
    if (requestUrl.pathname === '/api/v2/data/datasets') return json(route, 200, { items: [], total: 0 })
    if (requestUrl.pathname === '/api/v2/journal') return json(route, 200, { items: [] })
    if (requestUrl.pathname === '/api/v2/live/status') return json(route, 200, { state: 'unavailable', reason: 'offline_fixture' })
    if (requestUrl.pathname === '/api/v2/session/status') return json(route, 200, { authenticated: false, state: 'local_only' })
    if (requestUrl.pathname.endsWith('/learn/overview')) return json(route, 200, { courses: [], glossary_terms: [], resources: [] })
    if (requestUrl.pathname.endsWith('/learn/glossary')) return json(route, 200, { items: [] })
    return json(route, 200, { items: [], total: 0, state: 'empty' })
  })
  await page.goto(`${origin}${url}`, { waitUntil: 'networkidle' })
  await page.waitForTimeout(300)
  const beforeZoom = await page.evaluate(() => ({ innerWidth: window.innerWidth, innerHeight: window.innerHeight, dpr: window.devicePixelRatio, visualScale: window.visualViewport?.scale ?? null, scrollWidth: document.documentElement.scrollWidth, bodyHeight: document.body.scrollHeight }))
  const a11y = await inspectA11y(page)
  const screenshot = path.join(out, `${name}-${viewport.width}.png`)
  await page.screenshot({ path: screenshot, fullPage: true })
  const zoom = { attempted: true, before: beforeZoom, steps: [] }
  for (const key of ['Control+Equal', 'Control+Equal', 'Control+0']) {
    await page.keyboard.press(key)
    await page.waitForTimeout(100)
    zoom.steps.push({ key, state: await page.evaluate(() => ({ innerWidth: window.innerWidth, dpr: window.devicePixelRatio, visualScale: window.visualViewport?.scale ?? null, scrollWidth: document.documentElement.scrollWidth, overflow: document.documentElement.scrollWidth > window.innerWidth + 2 })) })
  }
  await page.setViewportSize({ width: viewport.width, height: viewport.height })
  const zoomProxies = {}
  for (const [label, width] of [['125-percent-css-viewport', Math.round(viewport.width / 1.25)], ['200-percent-css-viewport', Math.round(viewport.width / 2)]]) {
    await page.setViewportSize({ width, height: viewport.height })
    zoomProxies[label] = await page.evaluate(() => ({ viewportWidth: window.innerWidth, scrollWidth: document.documentElement.scrollWidth, overflow: document.documentElement.scrollWidth > window.innerWidth + 2, bodyHeight: document.body.scrollHeight }))
  }
  await page.setViewportSize({ width: viewport.width, height: viewport.height })
  const final = await page.evaluate(() => {
    const isVisible = (node) => { const style = getComputedStyle(node); const rect = node.getBoundingClientRect(); return style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0 }
    return { scrollWidth: document.documentElement.scrollWidth, viewportWidth: window.innerWidth, overflow: document.documentElement.scrollWidth > window.innerWidth + 2, focusables: [...document.querySelectorAll('button,a,input,select,textarea,[tabindex]:not([tabindex="-1"])')].filter(isVisible).length }
  })
  await page.keyboard.press('Tab')
  await page.waitForTimeout(40)
  const focus = await page.evaluate(() => {
    const node = document.activeElement
    const rect = node?.getBoundingClientRect()
    const style = node ? getComputedStyle(node) : null
    return { tag: node?.tagName || '', name: node?.getAttribute('aria-label') || node?.textContent?.trim().slice(0, 80) || '', visible: Boolean(node && style && style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0), outline: style?.outlineStyle || '' }
  })
  await context.tracing.stop({ path: tracePath })
  await context.close()
  return { name, url, viewport, screenshot, tracePath, beforeZoom, zoom, zoomProxies, final, focus, a11y, pageErrors, consoleErrors }
}

let server = null
const serverErrors = []
let browser = null
const report = { generatedAt: new Date().toISOString(), tool: 'Playwright + Chromium CDP', axeCore: { installed: false, reason: 'axe-core is not present in the existing node_modules; no package was installed' }, server: { origin, startedByScript: false }, routes: [], errors: [] }
try {
  try { await fetch(origin) } catch {
    server = spawn(process.execPath, [vite, '--host', '127.0.0.1', '--port', '4192', '--strictPort'], { cwd: here, stdio: ['ignore', 'pipe', 'pipe'] })
    report.server.startedByScript = true
    server.stderr.on('data', (chunk) => serverErrors.push(String(chunk)))
  }
  await waitForServer()
  browser = await chromium.launch({ headless: true, executablePath: process.env.TW_V2_CHROME || undefined })
  const cases = [
    ['overview', '/?view=overview&workspace=w8-a11y', { width: 1440, height: 900 }],
    ['analytics', '/?view=analytics&workspace=w8-a11y&job=w8-fixture', { width: 1440, height: 900 }],
    ['replay', '/?view=replay&surface=workspace&workspace=w8-a11y&session=w8-fixture&dataset=w8-fixture&cursor=3&mode=Practice', { width: 390, height: 844 }],
  ]
  for (const [name, url, viewport] of cases) report.routes.push(await inspectPage(browser, name, url, viewport))
} catch (error) {
  report.errors.push(String(error?.stack || error))
} finally {
  if (browser) await browser.close()
  if (server) { server.kill(); await new Promise((resolve) => server.once('exit', resolve)) }
}
report.server.stderr = serverErrors
report.summary = {
  pageErrors: report.routes.reduce((sum, route) => sum + route.pageErrors.length, 0),
  consoleErrors: report.routes.reduce((sum, route) => sum + route.consoleErrors.length, 0),
  overflowCases: report.routes.filter((route) => route.final.overflow).map((route) => route.name),
  nativeZoomObserved: report.routes.some((route) => route.zoom.steps.some((step) => step.state.dpr !== route.zoom.before.dpr || step.state.visualScale !== route.zoom.before.visualScale)),
  unnamedControlCases: report.routes.filter((route) => route.a11y.dom.unnamedControls > 0).map((route) => ({ name: route.name, count: route.a11y.dom.unnamedControls })),
  ariaHiddenFocusableCases: report.routes.filter((route) => route.a11y.dom.ariaHiddenFocusable > 0).map((route) => ({ name: route.name, count: route.a11y.dom.ariaHiddenFocusable })),
  headingSkipCases: report.routes.filter((route) => route.a11y.dom.headingSkips.length > 0).map((route) => ({ name: route.name, headings: route.a11y.dom.headingSkips })),
}
await writeFile(path.join(out, 'runtime.json'), JSON.stringify(report, null, 2))
console.log(JSON.stringify(report, null, 2))
if (report.errors.length || report.summary.pageErrors) process.exitCode = 1
