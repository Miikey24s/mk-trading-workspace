import assert from 'node:assert/strict'
import { spawn } from 'node:child_process'
import { mkdir, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const here = path.dirname(fileURLToPath(import.meta.url))
const webRoot = path.resolve(here, '../../../../projects/mt5-tradingview-backtester/foundation_v2/web')
const viteBin = path.join(webRoot, 'node_modules/vite/bin/vite.js')
const { chromium } = await import(pathToFileURL(path.join(webRoot, 'node_modules/playwright/index.mjs')).href)
const origin = 'http://127.0.0.1:4199'
const fixtureId = 'fullbleed-spike-fixture'
const cutoffIndex = 3999
const rows = Array.from({ length: 5000 }, (_, i) => {
  const open = i > cutoffIndex ? 9.999999 : 1.08 + Math.sin(i / 37) * .002 + i * .000001
  const close = open + Math.sin(i / 7) * .00035
  return { timestamp: 1710000000 + i * 60, open, close, high: Math.max(open, close) + .00022, low: Math.min(open, close) - .00022, volume: 100 + i % 500 }
})
const session = { record_id: fixtureId, revision: 1, payload: { dataset_id: 'fullbleed-local-fixture', cursor_index: cutoffIndex, branch_id: 'spike-branch', parent_session_id: null, status: 'completed' } }
const replayView = () => ({ ...session, dataset_sha256: 'sha256-local-fullbleed', cutoff_timestamp: rows[cutoffIndex].timestamp, visible_rows: rows.slice(0, cutoffIndex + 1), visible_row_count: cutoffIndex + 1, total_row_count: rows.length, has_future_rows: false, view_cursor_index: cutoffIndex, canonical_cursor_index: cutoffIndex, historical_view: false })
const json = (route, status, value) => route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(value) })

async function waitForServer(server, stderr) {
  for (let i = 0; i < 100; i++) {
    if (server.exitCode !== null) break
    try { if ((await fetch(origin)).ok) return } catch {}
    await new Promise(resolve => setTimeout(resolve, 100))
  }
  throw new Error(`Isolated Vite failed to start: ${stderr.join('')}`)
}

async function measure(page) {
  return page.evaluate((cutoffIndex) => {
    const box = selector => {
      const e = document.querySelector(selector)
      if (!e) return null
      const r = e.getBoundingClientRect(), s = getComputedStyle(e)
      return { x: r.x, y: r.y, width: r.width, height: r.height, display: s.display, overflowX: s.overflowX, overflowY: s.overflowY, scrollWidth: e.scrollWidth, clientWidth: e.clientWidth }
    }
    const visible = e => { const r = e.getBoundingClientRect(), s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none' }
    const controls = [...document.querySelectorAll('.fx-chart-topbar a,.fx-chart-topbar button,.chart-bottom-bar button,.chart-tool-rail button,.chart-utility-rail button')].filter(visible)
    const controlBoxes = controls.map(e => { const r = e.getBoundingClientRect(); return { name: (e.getAttribute('aria-label') || e.title || e.textContent || '').trim(), x: r.x, right: r.right, y: r.y, bottom: r.bottom, disabled: e.disabled === true } })
    const topbar = document.querySelector('.fx-chart-topbar')?.getBoundingClientRect()
    const clippedTopbarControls = controlBoxes.filter(c => topbar && c.y < topbar.bottom && (c.x < topbar.left || c.right > topbar.right || c.y < topbar.top || c.bottom > topbar.bottom))
    const overlappingTopbarControls = controlBoxes.filter(c => topbar && c.y < topbar.bottom).flatMap((a, i, all) => all.slice(i + 1).filter(b => Math.min(a.right, b.right) - Math.max(a.x, b.x) > 2 && Math.min(a.bottom, b.bottom) - Math.max(a.y, b.y) > 2).map(b => `${a.name} / ${b.name}`))
    return {
      viewport: { width: innerWidth, height: innerHeight },
      shellClass: document.querySelector('[data-testid="fxreplay-shell"]')?.className,
      shell: box('[data-testid="fxreplay-shell"]'), topbar: box('.fx-chart-topbar'), topbarLeft: box('.fx-chart-topbar-left'), topbarActions: box('.fx-chart-topbar-actions'),
      rail: box('.fx-rail'), main: box('.fx-main'), content: box('.fx-content'), context: box('.replay-contextbar'), toolbar: box('.replay-toolbar'),
      chartFrame: box('.chart-frame'), chart: box('[data-testid="replay-chart"]'), chartCanvas: box('.chart-canvas'), bottomBar: box('.chart-bottom-bar'),
      canvasCount: document.querySelectorAll('[data-testid="replay-chart"] canvas').length,
      visibleRows: document.querySelector('[data-testid="replay-chart"]')?.getAttribute('data-visible-row-count'),
      futureMarkerInText: document.body.innerText.includes('9.999999'),
      cutoffVisible: document.body.innerText.includes('Decision cutoff') || document.body.innerText.includes(`#${cutoffIndex}`),
      brokerLockVisible: document.body.innerText.toLowerCase().includes('broker locked'),
      documentOverflowX: Math.max(0, document.documentElement.scrollWidth - innerWidth), documentOverflowY: Math.max(0, document.documentElement.scrollHeight - innerHeight),
      controlCount: controlBoxes.length, controlBoxes, clippedTopbarControls, overlappingTopbarControls,
      controlsOutsideViewport: controlBoxes.filter(c => c.x < 0 || c.right > innerWidth || c.y < 0 || c.bottom > innerHeight),
      inaccessibleTopbarControls: controlBoxes.filter(c => topbar && c.y < topbar.bottom && c.x >= topbar.left && c.right <= topbar.right && document.elementFromPoint(Math.min(c.right - 2, Math.max(c.x + 2, (c.x + c.right) / 2)), (c.y + c.bottom) / 2)?.closest('button,a')?.getAttribute('aria-label') !== c.name).map(c => c.name),
    }
  }, cutoffIndex)
}

async function main() {
  await mkdir(here, { recursive: true })
  const stderr = [], server = spawn(process.execPath, [viteBin, '--host', '127.0.0.1', '--port', '4199', '--strictPort'], { cwd: webRoot, stdio: ['ignore', 'pipe', 'pipe'] })
  server.stderr.on('data', chunk => stderr.push(String(chunk)))
  let browser, context, page
  const trace = path.join(here, 'fullbleed-trace.zip')
  const requests = [], errors = [], transforms = []
  try {
    await waitForServer(server, stderr)
    browser = await chromium.launch({ headless: true })
    context = await browser.newContext({ viewport: { width: 1440, height: 900 }, locale: 'vi-VN', timezoneId: 'Asia/Ho_Chi_Minh', serviceWorkers: 'block', reducedMotion: 'reduce' })
    await context.tracing.start({ screenshots: true, snapshots: true, sources: false })
    page = await context.newPage()
    page.on('pageerror', error => errors.push(`page: ${error.message}`))
    page.on('console', message => { if (message.type() === 'error') errors.push(`console: ${message.text()}`) })
    await page.addInitScript(() => {
      window.__spikeLongTasks = []
      try { new PerformanceObserver(list => list.getEntries().forEach(entry => window.__spikeLongTasks.push(entry.duration))).observe({ type: 'longtask', buffered: true }) } catch {}
    })
    await page.route('**/*', async route => {
      const url = new URL(route.request().url())
      requests.push({ method: route.request().method(), url: url.pathname })
      if (url.origin !== origin || url.pathname.startsWith('/api/')) return route.abort()
      return route.continue()
    })
    await page.route('**/api/v2/replay/sessions/**', route => {
      const request = route.request(), url = new URL(request.url())
      requests.push({ method: request.method(), url: url.pathname })
      if (request.method() !== 'GET') return json(route, 405, { detail: 'fixture_read_only' })
      const id = decodeURIComponent(url.pathname.split('/').filter(Boolean)[4] || '')
      return id === fixtureId ? json(route, 200, replayView()) : json(route, 404, { detail: 'replay_not_found' })
    })
    await page.route('**/api/v2/replay/sessions', route => {
      const request = route.request()
      requests.push({ method: request.method(), url: new URL(request.url()).pathname })
      if (request.method() !== 'GET') return json(route, 405, { detail: 'fixture_read_only' })
      return json(route, 200, { items: [] })
    })
    await page.route('**/api/v2/data/datasets**', route => {
      const request = route.request()
      requests.push({ method: request.method(), url: new URL(request.url()).pathname })
      if (request.method() !== 'GET') return json(route, 405, { detail: 'fixture_read_only' })
      return json(route, 200, { items: [{ dataset_id: 'fullbleed-local-fixture', instrument_id: 'EURUSD', timeframe: 'M1', quality_status: 'verified', holdout_status: 'locked', row_count: rows.length, provider_id: 'local-fixture', artifact_sha256: 'sha256-local-fullbleed' }] })
    })
    await page.route('**/src/FxReplayShell.jsx*', async route => {
      const response = await route.fetch(), original = await response.text()
      const pattern = /SHELL_SKELETON_MODE\s*=\s*true/g
      const count = [...original.matchAll(pattern)].length
      assert.equal(count, 1, 'exactly one shell mode assignment must be transformed')
      transforms.push({ url: route.request().url(), count, originalBytes: original.length })
      return route.fulfill({ response, body: original.replace(pattern, 'SHELL_SKELETON_MODE = false') })
    })
    const url = `${origin}/?view=replay&workspace=tenant-fullbleed&session=${fixtureId}&surface=workspace`
    const start = Date.now()
    await page.goto(url, { waitUntil: 'domcontentloaded' })
    await page.getByTestId('replay-chart').waitFor()
    await page.waitForTimeout(350)
    const mountMs = Date.now() - start
    const desktop = await measure(page)
    assert.equal(transforms.length, 1)
    assert.ok(desktop.shellClass.includes('is-chart-workspace'))
    assert.equal(desktop.visibleRows, String(cutoffIndex + 1))
    assert.equal(desktop.futureMarkerInText, false)
    await page.screenshot({ path: path.join(here, 'fullbleed-1440.png'), fullPage: true })
    const pointerStart = performance.now(), chart = await page.getByTestId('replay-chart').boundingBox()
    for (let i = 0; i < 180; i++) await page.mouse.move(chart.x + 20 + (chart.width - 40) * i / 179, chart.y + 40 + (chart.height - 80) * (i * 17 % 100) / 100)
    const pointerMs = performance.now() - pointerStart
    const perf = await page.evaluate(() => ({ longTasks: window.__spikeLongTasks, heapUsed: performance.memory?.usedJSHeapSize ?? null }))
    await page.setViewportSize({ width: 768, height: 900 }); await page.waitForTimeout(300)
    const tablet = await measure(page)
    await page.screenshot({ path: path.join(here, 'fullbleed-768.png'), fullPage: true })
    await page.setViewportSize({ width: 390, height: 844 }); await page.waitForTimeout(300)
    const mobile = await measure(page)
    await page.screenshot({ path: path.join(here, 'fullbleed-390.png'), fullPage: true })
    const firstFocus = await page.keyboard.press('Tab').then(() => page.evaluate(() => ({ tag: document.activeElement?.tagName, name: document.activeElement?.getAttribute('aria-label') || document.activeElement?.textContent?.trim() })))
    await page.keyboard.press('?')
    const helpOpened = await page.getByRole('dialog').isVisible().catch(() => false)
    await page.keyboard.press('Escape')
    const helpClosed = !(await page.getByRole('dialog').isVisible().catch(() => false))
    const backHref = await page.getByRole('link', { name: 'Quay lại Sessions' }).getAttribute('href')
    await page.getByRole('link', { name: 'Quay lại Sessions' }).click()
    await page.waitForTimeout(200)
    const backRoute = { url: page.url(), chartVisible: await page.getByTestId('replay-chart').isVisible().catch(() => false), shellClass: await page.getByTestId('fxreplay-shell').getAttribute('class') }
    await page.goBack({ waitUntil: 'domcontentloaded' })
    await page.getByTestId('replay-chart').waitFor()
    const restored = await measure(page)
    const unexpectedErrors = errors.filter(message => !/Failed to load resource.*404/.test(message))
    const report = {
      status: 'SPIKE_NON_ACCEPTANCE', sourceModeUnchanged: true, transform: transforms, fixture: { rows: rows.length, cutoffIndex, visibleRows: cutoffIndex + 1, futureRows: rows.length - cutoffIndex - 1, futureMarker: '9.999999' },
      route: url, viewports: { desktop, tablet, mobile }, keyboardRoute: { firstFocus, helpOpened, helpClosed, backHref, backRoute, restoredFullBleed: restored.shellClass.includes('is-chart-workspace'), restoredRows: restored.visibleRows },
      throughput: { mountMs, pointerMoves: 180, pointerMs, longTaskCount: perf.longTasks.length, maxLongTaskMs: Math.max(0, ...perf.longTasks), heapUsed: perf.heapUsed },
      network: { requests, externalOrUnmockedApiRequests: requests.filter(r => !r.url.startsWith('/api/v2/replay/sessions') && !r.url.startsWith('/api/v2/data/datasets') && r.url.startsWith('/api/')), nonGetRequests: requests.filter(r => r.method !== 'GET') },
      errors: unexpectedErrors, screenshots: ['fullbleed-1440.png', 'fullbleed-768.png', 'fullbleed-390.png'], trace: path.basename(trace),
    }
    await writeFile(path.join(here, 'runtime.json'), `${JSON.stringify(report, null, 2)}\n`)
    console.log(JSON.stringify({ status: report.status, viewports: Object.fromEntries(Object.entries(report.viewports).map(([k, v]) => [k, { chart: v.chart, overflow: v.documentOverflowX, clippedTopbar: v.clippedTopbarControls, overlap: v.overlappingTopbarControls, cutoffVisible: v.cutoffVisible, brokerLockVisible: v.brokerLockVisible }])), keyboardRoute: report.keyboardRoute, throughput: report.throughput, errors: report.errors }, null, 2))
  } finally {
    await context?.tracing.stop({ path: trace }).catch(() => {})
    await context?.close().catch(() => {})
    await browser?.close().catch(() => {})
    server.kill('SIGTERM')
    if (stderr.length) process.stderr.write(stderr.join(''))
  }
}

main().catch(error => { console.error(error); process.exitCode = 1 })
