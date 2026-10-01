import assert from 'node:assert/strict'
import { spawn } from 'node:child_process'
import { mkdir, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const here = path.dirname(fileURLToPath(import.meta.url))
const webRoot = path.resolve(here, '..', '..', '..', '..', 'projects', 'mt5-tradingview-backtester', 'foundation_v2', 'web')
const evidenceDir = path.resolve(here)
const viteBin = path.join(webRoot, 'node_modules', 'vite', 'bin', 'vite.js')
const { chromium } = await import(pathToFileURL(path.join(webRoot, 'node_modules', 'playwright', 'index.mjs')).href)
const origin = 'http://127.0.0.1:4187'
const fixtureRows = Array.from({ length: 5000 }, (_, index) => {
  const timestamp = 1710000000 + (index * 60)
  const base = 1.08 + (Math.sin(index / 37) * 0.002) + (index * 0.000001)
  const open = base
  const close = base + Math.sin(index / 7) * 0.00035
  const high = Math.max(open, close) + 0.00022
  const low = Math.min(open, close) - 0.00022
  return { timestamp, open, high, low, close, volume: 100 + (index % 500) }
})
const session = {
  record_id: 'chart-5000-fixture',
  revision: 1,
  payload: {
    dataset_id: 'ui-chart-5000-fixture',
    cursor_index: fixtureRows.length - 1,
    branch_id: 'chart-5000-branch',
    parent_session_id: null,
    status: 'completed',
  },
}

function view() {
  const visible = fixtureRows.slice(0, session.payload.cursor_index + 1)
  return {
    ...session,
    dataset_sha256: 'sha256-chart-5000-fixture',
    cutoff_timestamp: visible.at(-1).timestamp,
    visible_rows: visible,
    visible_row_count: visible.length,
    total_row_count: fixtureRows.length,
    has_future_rows: false,
    view_cursor_index: session.payload.cursor_index,
    canonical_cursor_index: session.payload.cursor_index,
    historical_view: false,
  }
}

function fulfillJson(route, status, payload) {
  return route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(payload) })
}

async function waitForServer() {
  for (let attempt = 0; attempt < 100; attempt += 1) {
    try {
      const response = await fetch(origin)
      if (response.ok) return
    } catch {}
    await new Promise((resolve) => setTimeout(resolve, 100))
  }
  throw new Error('Vite server did not start')
}

async function geometry(page) {
  return page.evaluate(() => {
    const rect = (selector) => {
      const node = document.querySelector(selector)
      if (!node) return null
      const box = node.getBoundingClientRect()
      const style = getComputedStyle(node)
      return { x: box.x, y: box.y, width: box.width, height: box.height, display: style.display, overflowX: style.overflowX }
    }
    const canvases = [...document.querySelectorAll('[data-testid="replay-chart"] canvas')].map((node) => ({ width: node.width, height: node.height, cssWidth: node.getBoundingClientRect().width, cssHeight: node.getBoundingClientRect().height }))
    const html = document.documentElement
    return {
      viewport: { width: window.innerWidth, height: window.innerHeight },
      shellClass: document.querySelector('[data-testid="fxreplay-shell"]')?.className || '',
      shell: rect('[data-testid="fxreplay-shell"]'),
      rail: rect('.fx-rail'),
      main: rect('.fx-main'),
      content: rect('.fx-content'),
      chartFrame: rect('.chart-frame'),
      chartCanvas: rect('.chart-canvas'),
      chart: rect('[data-testid="replay-chart"]'),
      canvasCount: canvases.length,
      canvases,
      overflow: html.scrollWidth - window.innerWidth,
      visibleRows: document.querySelector('[data-testid="replay-chart"]')?.getAttribute('data-visible-row-count'),
      bodyTextHasFuturePrice: document.body.innerText.includes('1,081234'),
    }
  })
}

async function main() {
  await mkdir(evidenceDir, { recursive: true })
  const server = spawn(process.execPath, [viteBin, '--host', '127.0.0.1', '--port', '4187', '--strictPort'], { cwd: webRoot, stdio: ['ignore', 'pipe', 'pipe'] })
  const serverErrors = []
  server.stderr.on('data', (chunk) => serverErrors.push(String(chunk)))
  let browser
  let page
  let context
  let tracePath = path.join(evidenceDir, 'chart-5000-trace.zip')
  try {
    await waitForServer()
    browser = await chromium.launch({ headless: true })
    context = await browser.newContext({ viewport: { width: 1440, height: 900 } })
    page = await context.newPage()
    await page.addInitScript(() => {
      window.__chartW8 = { longTasks: [], navStart: performance.now() }
      try {
        new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) window.__chartW8.longTasks.push({ startTime: entry.startTime, duration: entry.duration })
        }).observe({ type: 'longtask', buffered: true })
      } catch {}
    })
    const consoleErrors = []
    page.on('console', (message) => {
      if (message.type() === 'error') consoleErrors.push(message.text())
    })
    await page.route('**/api/v2/replay/sessions/**', async (route) => {
      if (route.request().method() !== 'GET') return fulfillJson(route, 405, { detail: 'method_not_allowed' })
      const url = new URL(route.request().url())
      const id = decodeURIComponent(url.pathname.split('/').filter(Boolean)[4] || '')
      if (id !== session.record_id) return fulfillJson(route, 404, { detail: 'replay_not_found' })
      return fulfillJson(route, 200, view())
    })
    await page.route('**/api/v2/data/datasets**', async (route) => {
      if (route.request().method() !== 'GET') return fulfillJson(route, 405, { detail: 'method_not_allowed' })
      return fulfillJson(route, 200, { items: [{ dataset_id: 'ui-chart-5000-fixture', instrument_id: 'EURUSD', timeframe: 'M1', quality_status: 'verified', holdout_status: 'locked', row_count: fixtureRows.length, provider_id: 'local-fixture', artifact_sha256: 'sha256-chart-5000-fixture' }] })
    })
    await context.tracing.start({ screenshots: true, snapshots: true, sources: false })
    const navStart = Date.now()
    await page.goto(`${origin}/?view=replay&workspace=tenant-chart&session=${session.record_id}&surface=workspace`, { waitUntil: 'domcontentloaded' })
    await page.getByTestId('replay-chart').waitFor()
    await page.waitForTimeout(300)
    const chartReadyMs = Date.now() - navStart
    const desktopGeometry = await geometry(page)
    assert.equal(desktopGeometry.visibleRows, '5000')
    assert.equal(desktopGeometry.canvasCount >= 1, true)
    assert.equal(desktopGeometry.bodyTextHasFuturePrice, false)
    const chartBox = await page.getByTestId('replay-chart').boundingBox()
    assert.ok(chartBox && chartBox.width > 500 && chartBox.height > 300)
    const moveStart = performance.now()
    for (let index = 0; index < 180; index += 1) {
      const x = chartBox.x + 16 + ((chartBox.width - 32) * (index / 179))
      const y = chartBox.y + 40 + ((chartBox.height - 80) * ((index * 17) % 100) / 100)
      await page.mouse.move(x, y)
    }
    await page.waitForTimeout(250)
    const moveDurationMs = performance.now() - moveStart
    const desktopPerf = await page.evaluate(() => ({
      longTasks: window.__chartW8.longTasks,
      performanceEntries: performance.getEntriesByType('measure').map((entry) => ({ name: entry.name, duration: entry.duration })),
      domNodes: document.querySelectorAll('*').length,
      heapUsed: performance.memory?.usedJSHeapSize ?? null,
    }))
    await page.screenshot({ path: path.join(evidenceDir, 'chart-5000-desktop-1440.png'), fullPage: true })

    await page.setViewportSize({ width: 390, height: 900 })
    await page.waitForTimeout(250)
    const mobileGeometry = await geometry(page)
    assert.equal(mobileGeometry.visibleRows, '5000')
    const mobileCanvasReadable = Boolean(mobileGeometry.chart && mobileGeometry.chart.width > 250 && mobileGeometry.chart.height > 250)
    assert.ok(mobileGeometry.overflow <= 2)
    await page.screenshot({ path: path.join(evidenceDir, 'chart-5000-mobile-390.png'), fullPage: true })

    const unexpectedConsoleErrors = consoleErrors.filter((message) => !/Failed to load resource.*409/.test(message))
    const longTasks = desktopPerf.longTasks || []
    const maxLongTaskMs = longTasks.reduce((max, item) => Math.max(max, item.duration), 0)
    const report = {
      status: 'PASS_WITH_OPEN_GATES',
      fixture: { id: session.record_id, rows: fixtureRows.length, source: 'local Playwright route interception', cutoff: session.payload.cursor_index },
      route: `${origin}/?view=replay&workspace=tenant-chart&session=${session.record_id}&surface=workspace`,
      browser: 'Chromium headless via Playwright',
      viewports: { desktop: desktopGeometry, mobile: mobileGeometry },
      throughput: { chartReadyMs, pointerMoves: 180, moveDurationMs, longTaskCount: longTasks.length, maxLongTaskMs, domNodes: desktopPerf.domNodes, heapUsed: desktopPerf.heapUsed },
      safety: { visibleRowsOnly: desktopGeometry.visibleRows === String(fixtureRows.length), futureTextLeak: desktopGeometry.bodyTextHasFuturePrice, consoleErrors: unexpectedConsoleErrors },
      screenshots: ['chart-5000-desktop-1440.png', 'chart-5000-mobile-390.png'],
      trace: path.basename(tracePath),
      conclusions: {
        chartCanvasVisible: desktopGeometry.canvasCount >= 1 && desktopGeometry.chart.width > 500 && desktopGeometry.chart.height > 300,
        mobileCanvasVisible: mobileCanvasReadable,
        fullBleedProven: desktopGeometry.shellClass.includes('is-chart-workspace') && desktopGeometry.rail?.display === 'none',
        fullBleedOpenGate: 'SHELL_SKELETON_MODE=true keeps the product rail and standard shell; chartWorkspace full-bleed branch is not active in this build.',
        mobileCanvasOpenGate: mobileCanvasReadable ? null : '390px chart remains visible but is narrower than 250 CSS px because the normal shell/rail path is active; compact full-bleed workspace is not proven.',
        longSessionLimit: 'This bounded fixture measures one 5000-row mount and 180 pointer moves; it is not a 60fps frame/heap acceptance or long-duration soak.',
      },
    }
    await writeFile(path.join(evidenceDir, 'runtime.json'), `${JSON.stringify(report, null, 2)}\n`)
    console.log(JSON.stringify(report, null, 2))
  } finally {
    await context?.tracing.stop({ path: tracePath }).catch(() => {})
    await context?.close().catch(() => {})
    await browser?.close().catch(() => {})
    server.kill('SIGTERM')
    if (serverErrors.length) process.stderr.write(serverErrors.join(''))
  }
}

main().catch((error) => {
  console.error(error)
  process.exitCode = 1
})


