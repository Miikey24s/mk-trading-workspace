
import { spawn } from 'node:child_process'
import { mkdir, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { createRequire } from 'node:module'

const here = 'D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester/foundation_v2/web'
const out = 'D:/ANNAM/TradingWorkspace/planning/checkpoints/workspace-next-stage/WMREPLAY-W8-NATIVE-ZOOM-20261001'
const origin = 'http://127.0.0.1:4201'
const vite = path.join(here, 'node_modules', 'vite', 'bin', 'vite.js')
const chromePath = process.env.TW_V2_CHROME || 'C:/Program Files/Google/Chrome/Application/chrome.exe'
const { chromium } = createRequire(import.meta.url)(path.join(here, 'node_modules', 'playwright'))
await mkdir(out, { recursive: true })

function json(route, status, payload) {
  return route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(payload) })
}
function overview() {
  return { schema_version: 'overview-v1', counts: { datasets: 1, research_jobs: { completed: 1 }, records: { journal: 0, sessions: 1 } } }
}
async function waitForServer() {
  for (let i = 0; i < 100; i += 1) {
    try { if ((await fetch(origin)).ok) return } catch {}
    await new Promise((resolve) => setTimeout(resolve, 100))
  }
  throw new Error('vite server did not start')
}
const serverErrors = []
let server = null
let browser = null
const report = {
  schema_version: 'native-browser-zoom-v1',
  generated_at: new Date().toISOString(),
  environment: { platform: process.platform, node: process.version, chromePath, headed: true, playwright: 'existing local dependency', no_new_dependencies: true },
  server: { origin, started_by_script: false, stderr: [] },
  cases: [],
  errors: [],
}
try {
  try { await fetch(origin) } catch {
    server = spawn(process.execPath, [vite, '--host', '127.0.0.1', '--port', '4201', '--strictPort'], { cwd: here, stdio: ['ignore', 'pipe', 'pipe'] })
    report.server.started_by_script = true
    server.stderr.on('data', (chunk) => serverErrors.push(String(chunk)))
  }
  await waitForServer()
  browser = await chromium.launch({ headless: false, executablePath: chromePath, args: ['--disable-gpu'] })
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 })
  await context.tracing.start({ screenshots: true, snapshots: true })
  const page = await context.newPage()
  const pageErrors = []
  const consoleErrors = []
  page.on('pageerror', (error) => pageErrors.push(String(error)))
  page.on('console', (message) => { if (message.type() === 'error') consoleErrors.push(message.text()) })
  await page.route('**/api/**', async (route) => {
    const request = route.request()
    if (request.method() !== 'GET') return json(route, 405, { detail: 'read_only_native_zoom_fixture' })
    const requestUrl = new URL(request.url())
    if (requestUrl.pathname === '/api/v2/overview') return json(route, 200, overview())
    if (requestUrl.pathname.endsWith('/analytics')) return json(route, 200, { schema_version: 'analytics-read-model-v1', analytics_available: false, stale: true, ledger: [] })
    if (requestUrl.pathname === '/api/v2/session/status') return json(route, 200, { authenticated: false, state: 'local_only' })
    return json(route, 200, { items: [], total: 0, state: 'empty' })
  })
  await page.goto(origin + '/?view=overview&workspace=native-zoom-w8', { waitUntil: 'networkidle' })
  await page.waitForTimeout(400)
  await page.screenshot({ path: path.join(out, 'headed-before-1440.png'), fullPage: true })
  const state = () => page.evaluate(() => {
    const root = document.documentElement
    const vv = window.visualViewport
    const active = document.activeElement
    const rect = active?.getBoundingClientRect?.()
    return {
      innerWidth: window.innerWidth,
      innerHeight: window.innerHeight,
      outerWidth: window.outerWidth,
      outerHeight: window.outerHeight,
      devicePixelRatio: window.devicePixelRatio,
      visualScale: vv?.scale ?? null,
      visualWidth: vv?.width ?? null,
      visualHeight: vv?.height ?? null,
      scrollWidth: root.scrollWidth,
      clientWidth: root.clientWidth,
      bodyHeight: document.body.scrollHeight,
      overflow: root.scrollWidth > root.clientWidth + 2,
      activeTag: active?.tagName || '',
      activeName: active?.getAttribute?.('aria-label') || active?.textContent?.trim().slice(0, 80) || '',
      activeRect: rect ? { x: rect.x, y: rect.y, width: rect.width, height: rect.height } : null,
    }
  })
  const before = await state()
  await page.mouse.click(720, 450)
  const keys = ['Control+Equal', 'Control+Shift+Equal', 'Control+Equal', 'Control+0']
  const steps = []
  for (const key of keys) {
    await page.keyboard.press(key)
    await page.waitForTimeout(600)
    const s = await state()
    steps.push({ key, state: s })
    await page.screenshot({ path: path.join(out, 'headed-' + key.replace(/[^A-Za-z0-9]+/g, '_') + '-' + steps.length + '.png'), fullPage: true })
  }
  const after = await state()
  report.cases.push({ name: 'overview-headed-chrome', url: origin + '/?view=overview&workspace=native-zoom-w8', viewport: { width: 1440, height: 900 }, before, steps, after, pageErrors, consoleErrors })
  await context.tracing.stop({ path: path.join(out, 'headed-overview.trace.zip') })
  await context.close()
} catch (error) {
  report.errors.push(String(error?.stack || error))
} finally {
  if (browser) await browser.close().catch(() => {})
  if (server) { server.kill(); await new Promise((resolve) => { server.once('exit', resolve); setTimeout(resolve, 1000) }) }
}
report.server.stderr = serverErrors
report.summary = {
  headed_launch_succeeded: report.cases.length > 0,
  native_zoom_observed: report.cases.some((entry) => entry.steps.some((step) => step.state.devicePixelRatio !== entry.before.devicePixelRatio || step.state.visualScale !== entry.before.visualScale || step.state.innerWidth !== entry.before.innerWidth)),
  reset_returned_baseline: report.cases.every((entry) => {
    const first = entry.before
    const last = entry.after
    return first.devicePixelRatio === last.devicePixelRatio && first.visualScale === last.visualScale && first.innerWidth === last.innerWidth
  }),
  overflow_after_steps: report.cases.flatMap((entry) => entry.steps.filter((step) => step.state.overflow).map((step) => ({ name: entry.name, key: step.key }))),
  page_errors: report.cases.reduce((n, entry) => n + entry.pageErrors.length, 0),
  console_errors: report.cases.reduce((n, entry) => n + entry.consoleErrors.length, 0),
}
await writeFile(path.join(out, 'headed-runtime.json'), JSON.stringify(report, null, 2))
console.log(JSON.stringify(report, null, 2))
if (report.errors.length || report.summary.page_errors) process.exitCode = 1




