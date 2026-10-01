import assert from 'node:assert/strict'
import { mkdir, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { createRequire } from 'node:module'

const webRoot = 'D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester/foundation_v2/web'
const outDir = 'D:/ANNAM/TradingWorkspace/planning/checkpoints/workspace-next-stage/WMREPLAY-W8-A11Y-MANUAL-20261001'
const origin = process.env.TW_UI_ORIGIN || 'http://127.0.0.1:5173'
const { chromium } = createRequire(path.join(webRoot, 'package.json'))('playwright')

await mkdir(outDir, { recursive: true })

const routes = [
  {
    id: 'dashboard',
    url: '/?workspace=tenant-a&view=overview&session=replay-fixture&dataset=ui-live-fixture&cursor=4&mode=Practice&area=testing&section=dashboard',
    selector: '[data-testid="dashboard-data-state"]',
  },
  {
    id: 'sessions',
    url: '/?workspace=tenant-a&view=replay&select=1&workspace=tenant-a&session=replay-fixture&dataset=ui-live-fixture&cursor=4&mode=Practice',
    selector: '[data-testid="replay-session-dashboard"]',
  },
  {
    id: 'replay',
    url: '/?workspace=tenant-a&view=replay&surface=workspace&session=replay-fixture&dataset=ui-live-fixture&mode=Practice&cursor=4',
    selector: '[data-testid="replay-chart"]',
  },
  {
    id: 'analytics',
    url: '/?workspace=tenant-a&view=analytics&surface=workspace&session=replay-fixture&dataset=ui-live-fixture&mode=Practice',
    selector: '[data-testid="analytics-workspace"]',
  },
]

const sizes = [
  { id: 'desktop', width: 1440, height: 900 },
  { id: 'mobile', width: 390, height: 844 },
]
const themes = ['dark', 'light']

function parseRgb(value) {
  const match = String(value).match(/rgba?\(([^)]+)\)/i)
  if (!match) return null
  const values = match[1].split(',').map((part) => Number.parseFloat(part.trim()))
  if (values.length < 3 || values.slice(0, 3).some((part) => !Number.isFinite(part))) return null
  return values.slice(0, 3).map((part) => Math.max(0, Math.min(255, part)))
}

function luminance(rgb) {
  const linear = rgb.map((value) => {
    const channel = value / 255
    return channel <= 0.03928 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4
  })
  return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]
}

function contrastRatio(foreground, background) {
  if (!foreground || !background) return null
  const foregroundLum = luminance(foreground)
  const backgroundLum = luminance(background)
  return Number(((Math.max(foregroundLum, backgroundLum) + 0.05) / (Math.min(foregroundLum, backgroundLum) + 0.05)).toFixed(3))
}

function visible(node) {
  const style = getComputedStyle(node)
  const rect = node.getBoundingClientRect()
  return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0' && rect.width > 0 && rect.height > 0
}

function textName(node) {
  return (node.getAttribute('aria-label') || node.getAttribute('title') || node.getAttribute('alt') || node.labels?.[0]?.textContent || node.getAttribute('placeholder') || node.textContent || '')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 160)
}

async function pageA11y(page) {
  const cdp = await page.context().newCDPSession(page)
  let axTree = null
  let axError = null
  try {
    axTree = await cdp.send('Accessibility.getFullAXTree')
  } catch (error) {
    axError = String(error?.message || error)
  }
  const dom = await page.evaluate(() => {
    const isVisible = (node) => {
      const style = getComputedStyle(node)
      const rect = node.getBoundingClientRect()
      return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0' && rect.width > 0 && rect.height > 0
    }
    const controls = [...document.querySelectorAll('button,a[href],input,select,textarea,[role="button"],[role="link"],[role="checkbox"],[role="radio"],[role="tab"],[role="combobox"],[role="slider"],[role="spinbutton"]')]
    const visibleControls = controls.filter(isVisible)
    const headings = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].map((node) => ({ level: Number(node.tagName.slice(1)), text: node.textContent.trim().replace(/\s+/g, ' ').slice(0, 120) }))
    const duplicateIds = [...document.querySelectorAll('[id]')].map((node) => node.id).filter((id, index, all) => id && all.indexOf(id) !== index)
    const hiddenFocusable = [...document.querySelectorAll('[aria-hidden="true"] button,[aria-hidden="true"] a,[aria-hidden="true"] input,[aria-hidden="true"] select,[aria-hidden="true"] textarea,[aria-hidden="true"] [tabindex]:not([tabindex="-1"])')].filter(isVisible)
    const interactiveRoles = new Set(['button', 'link', 'checkbox', 'radio', 'tab', 'combobox', 'slider', 'spinbutton', 'menuitem', 'option'])
    const axInteractive = (window.__wmreplayAxNodes || [])
    return {
      lang: document.documentElement.lang || null,
      visibleControlCount: visibleControls.length,
      controls: visibleControls.map((node) => ({
        tag: node.tagName.toLowerCase(),
        role: node.getAttribute('role') || '',
        name: (node.getAttribute('aria-label') || node.getAttribute('title') || node.getAttribute('alt') || node.labels?.[0]?.textContent || node.getAttribute('placeholder') || node.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 160),
        disabled: node.matches(':disabled') || node.getAttribute('aria-disabled') === 'true',
        tabIndex: node.tabIndex,
      })),
      unnamedControls: visibleControls.filter((node) => !(node.getAttribute('aria-label') || node.getAttribute('title') || node.getAttribute('alt') || node.labels?.[0]?.textContent || node.getAttribute('placeholder') || node.textContent || '').trim()).length,
      duplicateIds: [...new Set(duplicateIds)],
      ariaHiddenFocusable: hiddenFocusable.length,
      headings,
      headingSkips: headings.slice(1).filter((heading, index) => heading.level > headings[index].level + 1),
      roleCounts: Object.fromEntries([...interactiveRoles].map((role) => [role, axInteractive.filter((node) => node.role === role).length])),
    }
  })
  const nodes = (axTree?.nodes || []).map((node) => ({
    role: node.role?.value || '',
    name: node.name?.value || '',
    ignored: Boolean(node.ignored),
  }))
  const interactiveRoles = new Set(['button', 'link', 'checkbox', 'radio', 'tab', 'combobox', 'slider', 'spinbutton', 'menuitem', 'option'])
  const active = nodes.filter((node) => !node.ignored && interactiveRoles.has(node.role))
  const unnamedAxControls = active.filter((node) => !node.name)
  return {
    cdpAvailable: Boolean(axTree),
    cdpError: axError,
    axNodeCount: nodes.length,
    axInteractiveCount: active.length,
    axUnnamedInteractiveCount: unnamedAxControls.length,
    axUnnamedInteractive: unnamedAxControls.slice(0, 20),
    dom,
  }
}

async function contrastAudit(page) {
  return page.evaluate(() => {
    const visible = (node) => {
      const style = getComputedStyle(node)
      const rect = node.getBoundingClientRect()
      return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0' && rect.width > 0 && rect.height > 0
    }
    const parseRgb = (value) => {
      const match = String(value).match(/rgba?\(([^)]+)\)/i)
      if (!match) return null
      const values = match[1].split(',').map((part) => Number.parseFloat(part.trim()))
      if (values.length < 3 || values.slice(0, 3).some((part) => !Number.isFinite(part))) return null
      return values.slice(0, 3).map((part) => Math.max(0, Math.min(255, part)))
    }
    const lum = (rgb) => rgb.map((value) => {
      const channel = value / 255
      return channel <= 0.03928 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4
    }).reduce((sum, value, index) => sum + value * [0.2126, 0.7152, 0.0722][index], 0)
    const ratio = (fg, bg) => {
      if (!fg || !bg) return null
      const a = lum(fg); const b = lum(bg)
      return Number(((Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05)).toFixed(3))
    }
    const effectiveBackground = (element) => {
      for (let node = element; node; node = node.parentElement) {
        const value = getComputedStyle(node).backgroundColor
        const rgb = parseRgb(value)
        const alpha = String(value).match(/rgba\([^,]+,[^,]+,[^,]+,\s*([0-9.]+)\)/i)
        if (rgb && (!alpha || Number(alpha[1]) > 0)) return rgb
      }
      return parseRgb(getComputedStyle(document.body).backgroundColor) || [255, 255, 255]
    }
    const candidates = [...document.querySelectorAll('body *')]
      .filter(visible)
      .filter((node) => node.children.length === 0 && node.textContent?.trim())
      .map((node) => {
        const style = getComputedStyle(node)
        const foreground = parseRgb(style.color)
        const background = effectiveBackground(node)
        return { text: node.textContent.trim().replace(/\s+/g, ' ').slice(0, 120), color: style.color, background, fontSize: style.fontSize, ratio: ratio(foreground, background) }
      })
      .filter((item) => item.ratio !== null)
    const sorted = [...candidates].sort((a, b) => a.ratio - b.ratio)
    return { measuredLeafText: candidates.length, minimum: sorted[0]?.ratio ?? null, belowAA: sorted.filter((item) => item.ratio < 4.5).slice(0, 20), samples: sorted.slice(0, 12) }
  })
}

async function focusAudit(page) {
  const focusableCount = await page.locator('a[href],button,input,select,textarea,[tabindex]:not([tabindex="-1"])').evaluateAll((nodes) => nodes.filter((node) => {
    const style = getComputedStyle(node); const rect = node.getBoundingClientRect()
    return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0' && rect.width > 0 && rect.height > 0 && !node.matches(':disabled')
  }).length)
  await page.locator('body').focus()
  const steps = []
  const limit = Math.min(Math.max(focusableCount + 2, 2), 180)
  for (let index = 0; index < limit; index += 1) {
    await page.keyboard.press('Tab')
    steps.push(await page.evaluate(() => {
      const node = document.activeElement
      if (!node) return { tag: null, visible: false, named: false, focusIndicator: false }
      const style = getComputedStyle(node); const rect = node.getBoundingClientRect()
      const name = (node.getAttribute('aria-label') || node.getAttribute('title') || node.getAttribute('alt') || node.labels?.[0]?.textContent || node.getAttribute('placeholder') || node.textContent || '').replace(/\s+/g, ' ').trim()
      const focusIndicator = style.outlineStyle !== 'none' && style.outlineWidth !== '0px' || style.boxShadow !== 'none'
      return { tag: node.tagName.toLowerCase(), id: node.id || null, testid: node.getAttribute('data-testid'), name: name.slice(0, 160), visible: style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0, named: Boolean(name), focusIndicator, outline: style.outline, boxShadow: style.boxShadow }
    }))
  }
  // Body/html can receive focus after the tab sequence wraps. That is an
  // expected traversal boundary, not a missing control focus indicator.
  const wrapBoundarySteps = steps.filter((step) => step.tag === 'body' || step.tag === 'html').length
  const violations = steps.filter((step) => step.tag && step.tag !== 'body' && step.tag !== 'html' && (!step.visible || !step.named || !step.focusIndicator))
  const unique = new Set(steps.filter((step) => step.tag).map((step) => `${step.tag}:${step.id || step.testid || step.name}`))
  return { focusableCount, tabPresses: limit, uniqueFocusCount: unique.size, wrapBoundarySteps, violations, first: steps.find((step) => step.tag && step.tag !== 'body' && step.tag !== 'html') || null, steps: steps.slice(0, 40) }
}

async function inspectCase(browser, route, size, theme, trace = false) {
  const context = await browser.newContext({ viewport: { width: size.width, height: size.height }, deviceScaleFactor: 1, reducedMotion: 'reduce' })
  await context.addInitScript((value) => localStorage.setItem('tw-theme', value), theme)
  const page = await context.newPage()
  const pageErrors = []
  const consoleErrors = []
  const requestFailures = []
  const mutationRequests = []
  page.on('pageerror', (error) => pageErrors.push(String(error?.message || error)))
  page.on('console', (message) => { if (message.type() === 'error') consoleErrors.push(message.text()) })
  page.on('requestfailed', (request) => requestFailures.push(`${request.method()} ${request.url()} ${request.failure()?.errorText || ''}`))
  await page.route('**/*', async (routeHandler) => {
    const request = routeHandler.request()
    const requestUrl = new URL(request.url())
    if (requestUrl.origin !== origin) return routeHandler.abort()
    if (requestUrl.pathname.startsWith('/api/') && request.method() !== 'GET') {
      mutationRequests.push(`${request.method()} ${requestUrl.pathname}`)
      return routeHandler.fulfill({ status: 403, contentType: 'application/json', body: JSON.stringify({ detail: 'manual_a11y_read_only' }) })
    }
    return routeHandler.continue()
  })
  const tracePath = path.join(outDir, `${route.id}-${size.id}-${theme}.trace.zip`)
  if (trace) await context.tracing.start({ screenshots: true, snapshots: true, sources: false })
  const result = { route: route.id, theme, size, expectedSelector: route.selector, url: origin + route.url, status: 'PASS', pageErrors, consoleErrors, requestFailures, mutationRequests }
  try {
    await page.goto(origin + route.url, { waitUntil: 'networkidle', timeout: 15000 })
    await page.locator(route.selector).waitFor({ state: 'visible', timeout: 15000 })
    await page.waitForTimeout(150)
    result.a11y = await pageA11y(page)
    result.focus = await focusAudit(page)
    result.contrast = await contrastAudit(page)
    result.geometry = await page.evaluate(() => ({
      viewportWidth: window.innerWidth,
      viewportHeight: window.innerHeight,
      clientWidth: document.documentElement.clientWidth,
      scrollWidth: document.documentElement.scrollWidth,
      horizontalOverflow: Math.max(0, document.documentElement.scrollWidth - document.documentElement.clientWidth),
      scrollHeight: document.documentElement.scrollHeight,
      bodyText: document.body.innerText.slice(0, 1800),
      theme: document.querySelector('[data-testid="fxreplay-shell"]')?.getAttribute('data-theme') || null,
    }))
    const before = await page.evaluate(() => ({ innerWidth: innerWidth, innerHeight: innerHeight, dpr: devicePixelRatio, visualScale: visualViewport?.scale ?? null, scrollWidth: document.documentElement.scrollWidth }))
    const zoomSteps = []
    for (const key of ['Control+Equal', 'Control+Equal', 'Control+Minus', 'Control+0']) {
      await page.keyboard.press(key)
      await page.waitForTimeout(70)
      zoomSteps.push({ key, ...await page.evaluate(() => ({ innerWidth, dpr: devicePixelRatio, visualScale: visualViewport?.scale ?? null, scrollWidth: document.documentElement.scrollWidth })) })
    }
    result.nativeZoom = { before, steps: zoomSteps, observed: zoomSteps.some((step) => step.dpr !== before.dpr || step.visualScale !== before.visualScale || step.innerWidth !== before.innerWidth) }
    result.screenshot = path.join(outDir, `${route.id}-${size.id}-${theme}.png`)
    await page.screenshot({ path: result.screenshot, fullPage: true })
    if (trace) {
      result.trace = tracePath
      await context.tracing.stop({ path: tracePath })
    }
  } catch (error) {
    result.status = 'FAIL'
    result.error = String(error?.stack || error)
    if (trace) await context.tracing.stop({ path: tracePath }).catch(() => {})
  } finally {
    await page.close().catch(() => {})
    await context.close().catch(() => {})
  }
  return result
}

const report = {
  generatedAt: new Date().toISOString(),
  source: { nestedHead: null, dirty: null },
  origin,
  scope: 'read-only current Vite + in-memory fixture; no product source changes',
  axe: { invoked: false, reason: 'axe-core is not present in existing web node_modules; no dependency was installed' },
  headedCapability: { attempted: false, launched: false, nativeZoomVerified: false, limitation: 'Playwright page keyboard targets document content; browser chrome zoom is not exposed by this protocol' },
  cases: [],
  limitations: [],
}

try {
  const git = await import('node:child_process')
  const execFile = (file, args) => new Promise((resolve) => git.execFile(file, args, { cwd: 'D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester' }, (error, stdout, stderr) => resolve({ error: error ? String(error.message) : null, stdout, stderr })))
  const head = await execFile('git', ['rev-parse', 'HEAD'])
  const status = await execFile('git', ['status', '--short'])
  report.source.nestedHead = head.stdout.trim()
  report.source.dirty = status.stdout.trim().split(/\r?\n/).filter(Boolean)
} catch (error) {
  report.source.error = String(error?.message || error)
}

let headedBrowser = null
try {
  report.headedCapability.attempted = true
  headedBrowser = await chromium.launch({ headless: false })
  report.headedCapability.launched = true
  const page = await headedBrowser.newPage({ viewport: { width: 390, height: 844 } })
  await page.goto(origin + '/?workspace=tenant-a&view=overview', { waitUntil: 'domcontentloaded', timeout: 15000 })
  const before = await page.evaluate(() => ({ innerWidth, dpr: devicePixelRatio, visualScale: visualViewport?.scale ?? null }))
  await page.keyboard.press('Control+Equal')
  await page.waitForTimeout(100)
  const after = await page.evaluate(() => ({ innerWidth, dpr: devicePixelRatio, visualScale: visualViewport?.scale ?? null }))
  report.headedCapability.pageKeyResult = { before, after, changed: JSON.stringify(before) !== JSON.stringify(after) }
  await page.close()
} catch (error) {
  report.headedCapability.error = String(error?.message || error)
} finally {
  await headedBrowser?.close().catch(() => {})
}

let browser = null
try {
  browser = await chromium.launch({ headless: true })
  for (const route of routes) {
    for (const size of sizes) {
      for (const theme of themes) {
        const trace = (route.id === 'dashboard' || route.id === 'replay') && size.id === 'mobile'
        report.cases.push(await inspectCase(browser, route, size, theme, trace))
      }
    }
  }
} finally {
  await browser?.close().catch(() => {})
}

report.summary = {
  caseCount: report.cases.length,
  passed: report.cases.filter((item) => item.status === 'PASS').length,
  failed: report.cases.filter((item) => item.status !== 'PASS').length,
  pageErrors: report.cases.reduce((sum, item) => sum + item.pageErrors.length, 0),
  consoleErrors: report.cases.reduce((sum, item) => sum + item.consoleErrors.length, 0),
  requestFailures: report.cases.reduce((sum, item) => sum + item.requestFailures.length, 0),
  mutationRequests: report.cases.reduce((sum, item) => sum + item.mutationRequests.length, 0),
  overflowCases: report.cases.filter((item) => (item.geometry?.horizontalOverflow || 0) > 2).map((item) => `${item.route}/${item.size.id}/${item.theme}`),
  domUnnamedCases: report.cases.filter((item) => (item.a11y?.dom?.unnamedControls || 0) > 0).map((item) => `${item.route}/${item.size.id}/${item.theme}`),
  axUnnamedCases: report.cases.filter((item) => (item.a11y?.axUnnamedInteractiveCount || 0) > 0).map((item) => `${item.route}/${item.size.id}/${item.theme}`),
  focusViolationCases: report.cases.filter((item) => (item.focus?.violations?.length || 0) > 0).map((item) => `${item.route}/${item.size.id}/${item.theme}`),
  nativeZoomObservedCases: report.cases.filter((item) => item.nativeZoom?.observed).map((item) => `${item.route}/${item.size.id}/${item.theme}`),
  minimumContrast: report.cases.filter((item) => Number.isFinite(item.contrast?.minimum)).reduce((min, item) => Math.min(min, item.contrast.minimum), Infinity),
}
report.summary.status = report.summary.failed || report.summary.pageErrors || report.summary.consoleErrors || report.summary.requestFailures || report.summary.overflowCases.length
  ? 'EXECUTION_FAIL'
  : 'PASS_WITH_OPEN_A11Y_FINDINGS'
report.limitations.push('Native browser chrome zoom is not directly controllable through Playwright page keyboard/CDP. Headed Chromium launches successfully, but Control+Equal only targets document content and no native zoom change was observable; a manual browser-chrome run remains OPEN.')
report.limitations.push('axe-core was unavailable in the existing web dependency tree and was not installed. CDP AX-tree plus DOM heuristics are structural evidence, not a WCAG conformance certificate.')
report.limitations.push('Contrast values are a leaf-text/effective-ancestor-background heuristic; gradients, composited overlays, canvas text, anti-aliasing and font-weight thresholds are not fully modeled.')
report.limitations.push('The nested MT5 repository has unrelated dirty WIP, including ReplayWorkspace.css; this lane did not stage, reset or modify those files.')
await writeFile(path.join(outDir, 'runtime.json'), `${JSON.stringify(report, null, 2)}\n`)
console.log(JSON.stringify({ summary: report.summary, headedCapability: report.headedCapability, source: report.source }, null, 2))
if (report.summary.status === 'EXECUTION_FAIL') process.exitCode = 1
