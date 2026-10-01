import { spawn } from 'node:child_process'
import { mkdir, writeFile } from 'node:fs/promises'
import { createRequire } from 'node:module'
import path from 'node:path'

const here = 'D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester/foundation_v2/web'
const out = 'D:/ANNAM/TradingWorkspace/planning/checkpoints/workspace-next-stage/WMREPLAY-W8-HEAP-FRAME-SOAK-20261001'
const origin = 'http://127.0.0.1:5173'
const vite = path.join(here, 'node_modules', 'vite', 'bin', 'vite.js')
const { chromium } = createRequire(import.meta.url)(path.join(here, 'node_modules', 'playwright'))

await mkdir(out, { recursive: true })

function largeAnalytics(count = 5000) {
  const ledger = Array.from({ length: count }, (_, index) => {
    const pnl = index % 3 === 0 ? 12 : index % 3 === 1 ? -7 : 0
    const close = new Date(Date.UTC(2024, 0, 1) + index * 86_400_000).toISOString()
    return {
      trade_id: `w8-large-${String(index + 1).padStart(5, '0')}`,
      open_time_utc: close,
      close_time_utc: close,
      net_pnl: pnl,
      realized_r: pnl / 10,
      side: index % 2 ? 'sell' : 'buy',
      source: { session_id: 'w8-large-heap-frame' },
    }
  })
  let balance = 1000
  const curve = ledger.map((trade) => ({ trade_id: trade.trade_id, closed_trade_balance: (balance += trade.net_pnl) }))
  return {
    schema_version: 'analytics-read-model-v1',
    analytics_available: true,
    stale: false,
    provenance: {
      dataset_id: 'w8-large-heap-frame-fixture',
      dataset_sha256: 'sha-w8-dataset',
      protocol_sha256: 'sha-w8-protocol',
      metrics_schema_version: 'metrics-v2',
      split: 'research',
      playbook_id: 'fixture',
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
      definitions: { net_pnl: { question: 'Net result?', unit: 'account units', formula: 'sum(net_pnl)', source: 'ledger', version: 'v1' },
      },
    },
    ledger,
  }
}

const analyticsFixture = largeAnalytics()
const overviewFixture = { schema_version: 'overview-v1', counts: { datasets: 1, research_jobs: { completed: 1 }, records: { journal: 0, sessions: 1 } } }
const sessionFixture = { items: [], total: 0 }
const datasetFixture = { items: [] }

function json(route, status, payload) {
  return route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(payload) })
}

async function waitForServer(url) {
  for (let i = 0; i < 100; i += 1) {
    try {
      if ((await fetch(url)).ok) return
    } catch {}
    await new Promise((resolve) => setTimeout(resolve, 100))
  }
  throw new Error(`vite server did not start at ${url}`)
}

const report = {
  scope: {
    fixture: 'w8-large-heap-frame-fixture',
    requestedRows: analyticsFixture.ledger.length,
    iterations: 3600,
    dwellMs: 1000,
    expectedDurationSeconds: 3900,
    route: '/?view=analytics&workspace=w8-heap-frame&job=large-fixture',
    sourceChanged: false,
    externalCalls: false,
  },
  thresholds: {
    maxLongTaskMs: 200,
    p95FrameIntervalMs: 50,
    minFrameSampleCount: 300,
    maxDomDelta: 10,
    maxHeapDeltaBytes: 12 * 1024 * 1024,
    maxHeapGrowthPerMinuteBytes: 8 * 1024 * 1024,
    maxUnexpectedPageErrors: 0,
    maxHorizontalOverflowPx: 2,
  },
  run: {},
  errors: [],
}

let server = null
let browser = null
let page = null
const serverErrors = []
const startedAt = new Date().toISOString()
let activeOrigin = origin
try {
  try {
    await waitForServer(origin)
  } catch {
    const fallbackOrigin = 'http://127.0.0.1:4191'
    server = spawn(process.execPath, [vite, '--host', '127.0.0.1', '--port', '4191', '--strictPort'], { cwd: here, stdio: ['ignore', 'pipe', 'pipe'] })
    server.stderr.on('data', (chunk) => serverErrors.push(String(chunk)))
    await waitForServer(fallbackOrigin)
    activeOrigin = fallbackOrigin
  }
  browser = await chromium.launch({
    headless: true,
    executablePath: process.env.TW_V2_CHROME || undefined,
    args: ['--js-flags=--expose-gc'],
  })
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } })
  page = await context.newPage()
  const pageErrors = []
  const consoleErrors = []
  page.on('pageerror', (error) => pageErrors.push(String(error)))
  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push(message.text())
  })
  await page.addInitScript(() => {
    window.__w8 = {
      startedAt: performance.now(),
      longTasks: [],
      frameIntervals: [],
      frameTimestamps: [],
      heapSamples: [],
      domSamples: [],
      rafLast: null,
      rafHandle: null,
    }
    try {
      new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) window.__w8.longTasks.push({ duration: entry.duration, startTime: entry.startTime })
      }).observe({ type: 'longtask', buffered: true })
    } catch {}
    const tick = (timestamp) => {
      const state = window.__w8
      if (state.rafLast !== null) state.frameIntervals.push(timestamp - state.rafLast)
      state.rafLast = timestamp
      state.frameTimestamps.push(timestamp)
      if (state.frameTimestamps.length > 12000) {
        state.frameTimestamps.shift()
        state.frameIntervals.shift()
      }
      state.rafHandle = requestAnimationFrame(tick)
    }
    const state = window.__w8
    state.rafHandle = requestAnimationFrame(tick)
  })
  await page.route('**/api/**', async (route) => {
    const requestUrl = new URL(route.request().url())
    if (requestUrl.pathname === '/api/v2/overview') return json(route, 200, overviewFixture)
    if (requestUrl.pathname === '/api/v2/replay/sessions') return json(route, 200, sessionFixture)
    if (requestUrl.pathname === '/api/v2/data/datasets') return json(route, 200, datasetFixture)
    if (requestUrl.pathname === '/api/v2/journal') return json(route, 200, { items: [] })
    if (requestUrl.pathname.endsWith('/analytics')) return json(route, 200, analyticsFixture)
    if (requestUrl.pathname.endsWith('/analytics.csv')) return route.fulfill({ status: 200, contentType: 'text/csv', body: 'trade_id,net_pnl\n' })
    return json(route, 503, { detail: 'fixture unavailable' })
  })

  const routeUrl = `${activeOrigin}/?view=analytics&workspace=w8-heap-frame&job=large-fixture`
  const navigationStarted = Date.now()
  await page.goto(routeUrl, { waitUntil: 'networkidle' })
  await page.getByText('N = 5.000', { exact: true }).waitFor({ timeout: 10000 })
  await page.waitForTimeout(500)
  const warmupTrace = path.join(out, 'analytics-stress-warmup.trace.zip')
  await context.tracing.start({ screenshots: true, snapshots: true })
  const outcome = page.getByLabel('Analytics outcome')
  const side = page.getByLabel('Analytics side')
  const nextPage = page.getByRole('button', { name: 'Trang sau' })
  const previousPage = page.getByRole('button', { name: 'Trang trước' })
  const selectorState = { outcome: await outcome.count(), side: await side.count(), nextPage: await nextPage.count(), previousPage: await previousPage.count() }
  const initial = await page.evaluate(() => {
    const memory = performance.memory?.usedJSHeapSize ?? null
    const gc = typeof window.gc === 'function'
    if (gc) window.gc()
    return {
      navMs: Math.round(performance.now() - window.__w8.startedAt),
      nodes: document.querySelectorAll('*').length,
      rows: document.querySelectorAll('tbody tr').length,
      heap: memory,
      scrollWidth: document.documentElement.scrollWidth,
      viewportWidth: window.innerWidth,
      gcExposed: gc,
    }
  })
  await page.evaluate(() => new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve))))
  const sessionStarted = Date.now()
  const sampleEvery = 15
  const samples = []
  const interactionErrors = []
  for (let i = 0; i < report.scope.iterations; i += 1) {
    try {
      await outcome.selectOption(i % 3 === 0 ? 'all' : i % 2 ? 'win' : 'loss')
      if (i % 2 === 0) await side.selectOption(i % 4 === 0 ? 'all' : i % 3 === 0 ? 'buy' : 'sell')
      if (i % 5 === 0 && await nextPage.isEnabled()) await nextPage.click()
      if (i % 5 === 2 && await previousPage.isEnabled()) await previousPage.click()
      if (i % 10 === 0) {
        await page.evaluate((offset) => {
          const node = document.querySelector('.fx-content')
          if (node) node.scrollTop = offset
        }, (i * 137) % 3200)
      }
      await page.evaluate(() => new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve))))
    } catch (error) {
      interactionErrors.push({ iteration: i, error: String(error) })
    }
    if (i % sampleEvery === 0 || i === report.scope.iterations - 1) {
      const sample = await page.evaluate((iteration) => {
        const state = window.__w8
        const heap = performance.memory?.usedJSHeapSize ?? null
        const gc = typeof window.gc === 'function'
        if (gc) window.gc()
        const afterGcHeap = performance.memory?.usedJSHeapSize ?? null
        state.heapSamples.push({ iteration, heap, afterGcHeap })
        state.domSamples.push({ iteration, nodes: document.querySelectorAll('*').length, rows: document.querySelectorAll('tbody tr').length })
        return {
          iteration,
          elapsedMs: Math.round(performance.now() - state.startedAt),
          heap,
          afterGcHeap,
          nodes: document.querySelectorAll('*').length,
          rows: document.querySelectorAll('tbody tr').length,
          scrollWidth: document.documentElement.scrollWidth,
          viewportWidth: window.innerWidth,
        }
      }, i)
      samples.push(sample)
    }
    if (i === 39) await context.tracing.stop({ path: warmupTrace })
    await page.waitForTimeout(report.scope.dwellMs)
  }
  await page.waitForTimeout(1000)
  const final = await page.evaluate(() => {
    const state = window.__w8
    const memory = performance.memory?.usedJSHeapSize ?? null
    const gc = typeof window.gc === 'function'
    if (gc) window.gc()
    return {
      elapsedMs: Math.round(performance.now() - state.startedAt),
      nodes: document.querySelectorAll('*').length,
      rows: document.querySelectorAll('tbody tr').length,
      heap: memory,
      afterGcHeap: performance.memory?.usedJSHeapSize ?? null,
      longTasks: state.longTasks,
      frameIntervals: state.frameIntervals,
      frameTimestamps: state.frameTimestamps.length,
      heapSamples: state.heapSamples,
      domSamples: state.domSamples,
      scrollWidth: document.documentElement.scrollWidth,
      viewportWidth: window.innerWidth,
      activeElement: document.activeElement?.getAttribute('aria-label') || document.activeElement?.textContent?.trim().slice(0, 80) || '',
    }
  })
  const frameIntervals = final.frameIntervals.filter((value) => Number.isFinite(value) && value > 0)
  const sortedFrames = [...frameIntervals].sort((a, b) => a - b)
  const quantile = (values, q) => values.length ? values[Math.min(values.length - 1, Math.floor((values.length - 1) * q))] : null
  const maxLongTaskMs = Math.max(0, ...final.longTasks.map((entry) => entry.duration))
  const p95FrameIntervalMs = quantile(sortedFrames, 0.95)
  const maxFrameIntervalMs = Math.max(0, ...frameIntervals)
  const firstHeap = samples.find((sample) => sample.heap !== null)?.afterGcHeap ?? samples.find((sample) => sample.heap !== null)?.heap ?? null
  const lastHeap = [...samples].reverse().find((sample) => sample.afterGcHeap !== null)?.afterGcHeap ?? [...samples].reverse().find((sample) => sample.heap !== null)?.heap ?? null
  const elapsedSessionMs = Date.now() - sessionStarted
  const heapDeltaBytes = firstHeap !== null && lastHeap !== null ? lastHeap - firstHeap : null
  const heapGrowthPerMinuteBytes = heapDeltaBytes === null || elapsedSessionMs <= 0 ? null : heapDeltaBytes / (elapsedSessionMs / 60000)
  const nodeValues = samples.map((sample) => sample.nodes)
  const maxDomDelta = nodeValues.length ? Math.max(...nodeValues) - Math.min(...nodeValues) : null
  const horizontalOverflowPx = Math.max(0, final.scrollWidth - final.viewportWidth)
  const verdicts = {
    longTasks: maxLongTaskMs <= report.thresholds.maxLongTaskMs,
    frameP95: p95FrameIntervalMs !== null && p95FrameIntervalMs <= report.thresholds.p95FrameIntervalMs,
    frameSampleCount: frameIntervals.length >= report.thresholds.minFrameSampleCount,
    domDelta: maxDomDelta !== null && maxDomDelta <= report.thresholds.maxDomDelta,
    heapDelta: heapDeltaBytes === null || heapDeltaBytes <= report.thresholds.maxHeapDeltaBytes,
    heapRate: heapGrowthPerMinuteBytes === null || heapGrowthPerMinuteBytes <= report.thresholds.maxHeapGrowthPerMinuteBytes,
    pageErrors: pageErrors.length <= report.thresholds.maxUnexpectedPageErrors,
    horizontalOverflow: horizontalOverflowPx <= report.thresholds.maxHorizontalOverflowPx,
    interactions: interactionErrors.length === 0,
  }
  report.run = {
    startedAt,
    navigation: { elapsedMs: Date.now() - navigationStarted, selectorState, initial },
    session: { elapsedSessionMs, requestedIterations: report.scope.iterations, completedIterations: report.scope.iterations - interactionErrors.length, dwellMs: report.scope.dwellMs, samples, interactionErrors },
    final: {
      nodes: final.nodes,
      rows: final.rows,
      heap: final.heap,
      afterGcHeap: final.afterGcHeap,
      maxLongTaskMs,
      longTaskCount: final.longTasks.length,
      frameSampleCount: frameIntervals.length,
      p95FrameIntervalMs,
      maxFrameIntervalMs,
      heapDeltaBytes,
      heapGrowthPerMinuteBytes,
      maxDomDelta,
      horizontalOverflowPx,
      pageErrors,
      consoleErrors,
      frameIntervalsSummary: { minMs: quantile(sortedFrames, 0), medianMs: quantile(sortedFrames, 0.5), p95Ms: p95FrameIntervalMs, maxMs: maxFrameIntervalMs },
      longTasks: final.longTasks,
    },
    thresholds: report.thresholds,
    verdicts,
    warmupTrace,
  }
  await page.screenshot({ path: path.join(out, 'analytics-stress-final-1440.png'), fullPage: true })
  await page.setViewportSize({ width: 390, height: 844 })
  await page.waitForTimeout(100)
  const mobile = await page.evaluate(() => ({ scrollWidth: document.documentElement.scrollWidth, viewportWidth: window.innerWidth, overflow: document.documentElement.scrollWidth > window.innerWidth + 2, nodes: document.querySelectorAll('*').length, rows: document.querySelectorAll('tbody tr').length }))
  report.run.mobile = mobile
  await page.screenshot({ path: path.join(out, 'analytics-stress-final-390.png'), fullPage: true })
  report.run.verdicts.mobileOverflow = !mobile.overflow
} catch (error) {
  report.errors.push(String(error?.stack || error))
} finally {
  if (page) await page.close().catch(() => {})
  if (browser) await browser.close().catch(() => {})
  if (server) {
    server.kill()
    await new Promise((resolve) => server.once('exit', resolve))
  }
}
report.server = { reused: !server, fallbackStarted: Boolean(server), stderr: serverErrors }
report.finishedAt = new Date().toISOString()
await writeFile(path.join(out, 'metrics.json'), JSON.stringify(report, null, 2))
await writeFile(path.join(out, 'run-output.txt'), JSON.stringify(report, null, 2))
console.log(JSON.stringify(report, null, 2))
if (report.errors.length || report.run?.verdicts && Object.values(report.run.verdicts).some((value) => value === false)) process.exitCode = 1
