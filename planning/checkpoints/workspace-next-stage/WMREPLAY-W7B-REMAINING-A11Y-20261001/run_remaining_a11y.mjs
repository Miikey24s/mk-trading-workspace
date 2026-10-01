import { pathToFileURL } from 'node:url'
const { chromium } = await import(pathToFileURL('D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester/foundation_v2/web/node_modules/playwright/index.mjs').href)
import { mkdir, writeFile } from 'node:fs/promises'
import path from 'node:path'

const checkpoint = 'D:/ANNAM/TradingWorkspace/planning/checkpoints/workspace-next-stage/WMREPLAY-W7B-REMAINING-A11Y-20261001'
const origin = 'http://127.0.0.1:5173'
const routes = [
  { id: 'data', query: 'view=data', selector: '[data-testid="data-desk-root"]' },
  { id: 'research', query: 'view=research', selector: '[data-testid="research-root"]' },
  { id: 'journal', query: 'view=journal', selector: '[data-testid="journal-workspace"]' },
  { id: 'trade', query: 'view=trade&surface=workspace', selector: '[data-testid="trade-workspace"]' },
  { id: 'risk', query: 'view=risk', selector: '[data-testid="risk-workspace"]' },
  { id: 'playbook', query: 'view=playbook', selector: '[data-testid="playbook-root"]' },
]
const sizes = [{ id: '1440', width: 1440, height: 900 }, { id: '768', width: 768, height: 900 }, { id: '390', width: 390, height: 844 }]
await mkdir(checkpoint, { recursive: true })
await mkdir(path.join(checkpoint, 'screenshots'), { recursive: true })

async function inspectPage(page) {
  return page.evaluate(() => {
    const visible = (node) => {
      if (!node || node.closest('[aria-hidden="true"]')) return false
      const style = getComputedStyle(node)
      if (style.display === 'none' || style.visibility === 'hidden') return false
      const rect = node.getBoundingClientRect()
      return rect.width > 0 && rect.height > 0
    }
    const accessibleName = (node) => {
      const labelledBy = node.getAttribute('aria-labelledby')
      if (labelledBy) {
        const text = labelledBy.split(/\s+/).map((id) => document.getElementById(id)?.textContent?.trim() || '').filter(Boolean).join(' ')
        if (text) return text
      }
      for (const attr of ['aria-label', 'title']) {
        const value = node.getAttribute(attr)?.trim()
        if (value) return value
      }
      if ('labels' in node && node.labels?.length) {
        const text = Array.from(node.labels).map((item) => item.textContent?.trim() || '').filter(Boolean).join(' ')
        if (text) return text
      }
      const text = node.textContent?.replace(/\s+/g, ' ').trim()
      if (text) return text.slice(0, 180)
      return node.getAttribute('placeholder')?.trim() || ''
    }
    const selector = 'button, input, select, textarea, a[href], [role="button"], [role="link"], [role="checkbox"], [role="radio"], [role="tab"], [role="switch"], [tabindex]:not([tabindex="-1"])'
    const unnamed = []
    const controls = []
    for (const node of document.querySelectorAll(selector)) {
      if (!visible(node) || node.disabled) continue
      const name = accessibleName(node)
      const role = node.getAttribute('role') || node.tagName.toLowerCase()
      const dataTestId = node.getAttribute('data-testid') || ''
      controls.push({ role, name, dataTestId, tag: node.tagName.toLowerCase() })
      if (!name) unnamed.push({ role, dataTestId, tag: node.tagName.toLowerCase(), html: node.outerHTML.slice(0, 220) })
    }
    const headings = Array.from(document.querySelectorAll('h1,h2,h3,h4,h5,h6')).filter(visible).map((node) => ({ level: Number(node.tagName.slice(1)), text: node.textContent?.replace(/\s+/g, ' ').trim() || '' }))
    const headingSkips = []
    for (let i = 1; i < headings.length; i += 1) if (headings[i].level > headings[i - 1].level + 1) headingSkips.push([headings[i - 1], headings[i]])
    const ids = Array.from(document.querySelectorAll('[id]')).map((node) => node.id).filter(Boolean)
    const duplicateIds = ids.filter((id, i) => ids.indexOf(id) !== i)
    const ariaRefs = []
    for (const node of document.querySelectorAll('[aria-labelledby],[aria-describedby],[aria-controls],[aria-owns]')) {
      for (const attr of ['aria-labelledby', 'aria-describedby', 'aria-controls', 'aria-owns']) {
        const value = node.getAttribute(attr)
        if (!value) continue
        for (const id of value.split(/\s+/).filter(Boolean)) if (!document.getElementById(id)) ariaRefs.push({ attr, id, tag: node.tagName.toLowerCase() })
      }
    }
    const html = document.documentElement
    const shell = document.querySelector('[data-testid="fxreplay-shell"]')
    const root = document.querySelector('main') || document.querySelector('[data-testid]')
    return {
      viewport: { width: innerWidth, height: innerHeight },
      documentWidth: html.scrollWidth,
      overflowX: Math.max(0, html.scrollWidth - innerWidth),
      root: root ? { width: root.getBoundingClientRect().width, height: root.getBoundingClientRect().height } : null,
      shellTheme: shell?.getAttribute('data-theme') || null,
      headingCount: headings.length,
      headings,
      headingSkips,
      duplicateIds: [...new Set(duplicateIds)],
      ariaRefs,
      controlsCount: controls.length,
      unnamed,
      controls,
      hasMain: Boolean(document.querySelector('main')),
      hasLang: document.documentElement.getAttribute('lang') || null,
    }
  })
}

const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({ viewport: sizes[0], reducedMotion: 'reduce', locale: 'vi-VN' })
await context.tracing.start({ screenshots: true, snapshots: true, sources: false })
const results = []
const blockedExternal = []
const failures = []

for (const size of sizes) {
  for (const routeCase of routes) {
    const page = await context.newPage()
    const pageErrors = []
    const consoleErrors = []
    const responses = []
    const mutations = []
    page.on('pageerror', (error) => pageErrors.push(String(error)))
    page.on('console', (message) => { if (message.type() === 'error') consoleErrors.push(message.text()) })
    page.on('request', (request) => {
      const requestUrl = request.url()
      if (/^https?:\/\//.test(requestUrl) && !/^https?:\/\/127\.0\.0\.1(?::\d+)?(?:\/|$)/.test(requestUrl)) blockedExternal.push({ route: routeCase.id, size: size.id, url: requestUrl })
      if (!['GET', 'HEAD', 'OPTIONS'].includes(request.method())) mutations.push({ method: request.method(), url: requestUrl })
    })
    page.on('response', (response) => { if (response.status() >= 400) responses.push({ status: response.status(), url: response.url() }) })
    await page.addInitScript(() => { if (!sessionStorage.getItem('a11y-initialized')) { localStorage.clear(); sessionStorage.setItem('a11y-initialized', '1') } })
    await page.route(/^https?:\/\/(?!127\.0\.0\.1(?::\d+)?(?:\/|$))/, (request) => request.abort())
    let darkMetrics = null
    let lightMetrics = null
    const focusSequence = []
    try {
      await page.setViewportSize({ width: size.width, height: size.height })
      await page.goto(origin + '/?' + routeCase.query + '&workspace=tenant-a', { waitUntil: 'domcontentloaded' })
      await page.locator(routeCase.selector).waitFor({ state: 'visible' })
      await page.waitForTimeout(500)
      darkMetrics = await inspectPage(page)
      if (size.width === 1440 || size.width === 390) await page.screenshot({ path: path.join(checkpoint, 'screenshots', routeCase.id + '-' + size.id + '-dark.png'), fullPage: true })
      const themeToggle = page.getByTestId('theme-toggle')
      if (await themeToggle.count()) {
        await themeToggle.click()
        await page.locator(routeCase.selector).waitFor({ state: 'visible' })
        await page.waitForTimeout(120)
        lightMetrics = await inspectPage(page)
        if (size.width === 1440 || size.width === 390) await page.screenshot({ path: path.join(checkpoint, 'screenshots', routeCase.id + '-' + size.id + '-light.png'), fullPage: true })
        if (darkMetrics.shellTheme === lightMetrics.shellTheme) throw new Error('theme did not change ' + darkMetrics.shellTheme)
      } else lightMetrics = { skipped: true }
      await page.reload({ waitUntil: 'domcontentloaded' })
      await page.locator(routeCase.selector).waitFor({ state: 'visible' })
      const reloadTheme = await page.locator('[data-testid="fxreplay-shell"]').getAttribute('data-theme')
      if (lightMetrics.shellTheme && reloadTheme !== lightMetrics.shellTheme) throw new Error('theme did not persist after reload: ' + reloadTheme + ' vs ' + lightMetrics.shellTheme)
      const tabCount = await page.locator('button:visible, input:visible, select:visible, textarea:visible, a[href]:visible, [role="button"]:visible, [role="link"]:visible, [tabindex]:not([tabindex="-1"]):visible').count()
      for (let i = 0; i < Math.min(tabCount + 2, 80); i += 1) {
        await page.keyboard.press('Tab')
        focusSequence.push(await page.evaluate(() => {
          const node = document.activeElement
          return node ? { tag: node.tagName.toLowerCase(), id: node.id || '', testId: node.getAttribute('data-testid') || '', name: node.getAttribute('aria-label') || node.textContent?.trim().slice(0, 80) || '' } : null
        }))
      }
      const metrics = { route: routeCase.id, viewport: size, dark: darkMetrics, light: lightMetrics, persistedTheme: reloadTheme, focus: { attempted: focusSequence.length, distinct: new Set(focusSequence.map((item) => JSON.stringify(item))).size, tail: focusSequence.slice(-4) }, pageErrors, consoleErrors, responses, mutations }
      results.push(metrics)
      const bad = []
      for (const mode of [darkMetrics, lightMetrics]) {
        if (!mode || mode.skipped) continue
        if (!mode.root || mode.root.width <= 0) bad.push('root missing')
        if (mode.overflowX > 2) bad.push('overflow ' + mode.overflowX + 'px')
        if (mode.unnamed.length) bad.push(mode.unnamed.length + ' unnamed controls')
        if (mode.duplicateIds.length) bad.push('duplicate ids ' + mode.duplicateIds.join(','))
        if (mode.ariaRefs.length) bad.push('broken aria refs ' + mode.ariaRefs.length)
        if (mode.headingSkips.length) bad.push('heading skips ' + mode.headingSkips.length)
      }
      if (pageErrors.length) bad.push('page errors ' + pageErrors.length)
      if (mutations.length) bad.push('mutations ' + mutations.length)
      if (bad.length) failures.push({ route: routeCase.id, viewport: size.id, bad, consoleErrors, responses, details: { dark: darkMetrics, light: lightMetrics } })
    } catch (error) {
      failures.push({ route: routeCase.id, viewport: size.id, bad: [String(error)], pageErrors, consoleErrors, responses, mutations })
      results.push({ route: routeCase.id, viewport: size, error: String(error), pageErrors, consoleErrors, responses, mutations, dark: darkMetrics, light: lightMetrics })
    } finally { await page.close() }
  }
}
const tracePath = path.join(checkpoint, 'remaining-a11y-trace.zip')
await context.tracing.stop({ path: tracePath })
await context.close()
await browser.close()
const report = { status: failures.length ? 'FINDINGS' : 'PASS', generatedAt: new Date().toISOString(), origin, routes: routes.map(({ id, query, selector }) => ({ id, query, selector })), sizes, resultCount: results.length, failureCount: failures.length, blockedExternal, results, failures }
await writeFile(path.join(checkpoint, 'runtime.json'), JSON.stringify(report, null, 2) + '\n')
console.log(JSON.stringify({ status: report.status, resultCount: report.resultCount, failureCount: report.failureCount, blockedExternal: blockedExternal.length, failures: failures.map(({ route, viewport, bad, responses, consoleErrors }) => ({ route, viewport, bad, responses, consoleErrors })) }, null, 2))



