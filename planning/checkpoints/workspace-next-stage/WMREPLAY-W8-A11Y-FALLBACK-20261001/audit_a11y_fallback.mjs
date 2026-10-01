import { createRequire } from 'node:module'
import { mkdir, writeFile } from 'node:fs/promises'
import path from 'node:path'

const require = createRequire('D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester/foundation_v2/web/package.json')
const { chromium } = require('playwright')

const base = 'http://127.0.0.1:5173'
const outDir = path.resolve('D:/ANNAM/TradingWorkspace/planning/checkpoints/workspace-next-stage/WMREPLAY-W8-A11Y-FALLBACK-20261001')
await mkdir(outDir, { recursive: true })
const routes = [
  { name: 'dashboard', url: '/?workspace=tenant-a&view=overview&area=testing&section=dashboard', expected: ['Dashboard', 'Backtesting'] },
  { name: 'replay', url: '/?workspace=tenant-a&view=replay&session=replay-fixture&dataset=ui-live-fixture&surface=compact&cursor=3', expected: ['Replay', 'EURUSD'] },
]
const viewports = [
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'mobile', width: 390, height: 844 },
]
const themes = ['dark', 'light']

function contrast(rgb1, rgb2) {
  const parse = (v) => {
    const m = v.match(/rgba?\\(([^)]+)\\)/)
    if (!m) return null
    const p = m[1].split(',').map((x) => Number.parseFloat(x.trim()))
    if (p.length < 3 || p.some((x) => !Number.isFinite(x))) return null
    return p.slice(0, 3).map((x) => x / 255)
  }
  const a = parse(rgb1); const b = parse(rgb2)
  if (!a || !b) return null
  const lum = (c) => c.map((x) => x <= 0.03928 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4).reduce((s, x, i) => s + x * [0.2126, 0.7152, 0.0722][i], 0)
  const [la, lb] = [lum(a), lum(b)].sort((x, y) => y - x)
  return (la + 0.05) / (lb + 0.05)
}

const browser = await chromium.launch({ headless: true })
const report = { generated_at: new Date().toISOString(), browser: 'chromium-headless-playwright', routes: [], limitations: [] }
for (const route of routes) {
  for (const viewport of viewports) {
    for (const theme of themes) {
    const page = await browser.newPage({ viewport: { width: viewport.width, height: viewport.height }, deviceScaleFactor: 1 })
    await page.addInitScript((value) => localStorage.setItem('tw-theme', value), theme)
    const consoleErrors = []
    const pageErrors = []
    page.on('console', (msg) => { if (msg.type() === 'error') consoleErrors.push(msg.text()) })
    page.on('pageerror', (error) => pageErrors.push(String(error?.message || error)))
    await page.goto(base + route.url, { waitUntil: 'networkidle' })
    await page.waitForTimeout(120)
    const snapshot = await page.evaluate(({ routeName, width, height }) => {
      const contrast = (rgb1, rgb2) => {
        const parse = (v) => {
          const m = v.match(/rgba?\(([^)]+)\)/)
          if (!m) return null
          const p = m[1].split(',').map((x) => Number.parseFloat(x.trim()))
          if (p.length < 3 || p.some((x) => !Number.isFinite(x))) return null
          return p.slice(0, 3).map((x) => x / 255)
        }
        const a = parse(rgb1); const b = parse(rgb2)
        if (!a || !b) return null
        const lum = (c) => c.map((x) => x <= 0.03928 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4).reduce((s, x, i) => s + x * [0.2126, 0.7152, 0.0722][i], 0)
        const [la, lb] = [lum(a), lum(b)].sort((x, y) => y - x)
        return (la + 0.05) / (lb + 0.05)
      }
      const visible = (el) => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none' }
      const focusable = [...document.querySelectorAll('a[href],button,input,select,textarea,[tabindex]:not([tabindex="-1"])')].filter(visible)
      const allText = [...document.querySelectorAll('body *')].filter(visible).filter((el) => el.children.length === 0 && el.textContent?.trim())
      const effectiveBackground = (el) => {
        for (let node = el; node; node = node.parentElement) {
          const bg = getComputedStyle(node).backgroundColor
          const alpha = bg.match(/rgba\([^,]+,[^,]+,[^,]+,\s*([0-9.]+)\)/i)
          if (!alpha || Number(alpha[1]) > 0) return bg
        }
        return getComputedStyle(document.body).backgroundColor
      }
      const styleFor = (el) => { const s = getComputedStyle(el); return { color: s.color, backgroundColor: s.backgroundColor, effectiveBackground: effectiveBackground(el), outline: s.outline, outlineColor: s.outlineColor, boxShadow: s.boxShadow, fontSize: s.fontSize } }
      const major = [...document.querySelectorAll('button,a,[role="button"],input,select,textarea')].filter(visible).slice(0, 80).map((el) => ({ tag: el.tagName, role: el.getAttribute('role'), name: (el.getAttribute('aria-label') || el.innerText || el.getAttribute('title') || el.getAttribute('placeholder') || '').trim().replace(/\\s+/g, ' ').slice(0, 120), disabled: el.matches(':disabled') || el.getAttribute('aria-disabled') === 'true', style: styleFor(el) }))
      const textContrast = allText.slice(0, 200).map((el) => ({ text: el.textContent.trim().replace(/\\s+/g, ' ').slice(0, 100), style: styleFor(el), ratio: contrast(styleFor(el).color, styleFor(el).effectiveBackground) })).filter((x) => x.ratio !== null)
      return {
        route: routeName, viewport: { width, height }, url: location.href,
        title: document.title,
        bodyText: document.body.innerText.slice(0, 1800),
        viewport: { innerWidth, innerHeight, clientWidth: document.documentElement.clientWidth, scrollWidth: document.documentElement.scrollWidth, clientHeight: document.documentElement.clientHeight, scrollHeight: document.documentElement.scrollHeight, visualScale: window.visualViewport?.scale ?? null },
        focusableCount: focusable.length,
        focusables: focusable.map((el) => ({ tag: el.tagName, text: (el.innerText || el.getAttribute('aria-label') || el.getAttribute('title') || '').trim().replace(/\\s+/g, ' ').slice(0, 90), tabIndex: el.tabIndex, disabled: el.matches(':disabled') || el.getAttribute('aria-disabled') === 'true' })),
        major,
        unlabeledControls: major.filter((x) => ['BUTTON','A','INPUT','SELECT','TEXTAREA'].includes(x.tag) && !x.name),
        textContrast,
      }
    }, { routeName: route.name, width: viewport.width, height: viewport.height })

    const key = `${route.name}-${viewport.name}-${theme}`
    const keyboard = await page.evaluate(() => { document.body.focus(); return true })
    const focusSteps = []
    for (let i = 0; i < Math.min(snapshot.focusableCount + 2, 120); i += 1) {
      await page.keyboard.press('Tab')
      focusSteps.push(await page.evaluate(() => {
        const el = document.activeElement
        if (!el) return { tag: null }
        const s = getComputedStyle(el)
        const r = el.getBoundingClientRect()
        return { tag: el.tagName, id: el.id || null, testid: el.getAttribute('data-testid'), text: (el.innerText || el.getAttribute('aria-label') || el.getAttribute('title') || '').trim().replace(/\\s+/g, ' ').slice(0, 90), tabIndex: el.tabIndex, visible: r.width > 0 && r.height > 0, focusVisible: s.outlineStyle !== 'none' || s.outlineWidth !== '0px' || s.boxShadow !== 'none', outline: s.outline, boxShadow: s.boxShadow }
      }))
    }
    const repeatTarget = route.name === 'replay' ? page.getByTestId('branch-replay') : page.getByRole('link', { name: /sessions/i }).first()
    const targetCount = await repeatTarget.count()
    let keyboardAction = { targetCount, invoked: false, before: null, after: null }
    if (targetCount > 0) {
      keyboardAction.before = await page.evaluate(() => ({ active: document.activeElement?.getAttribute('data-testid') || document.activeElement?.textContent?.trim().slice(0, 80) }))
      await repeatTarget.focus()
      keyboardAction.before = await page.evaluate(() => ({ active: document.activeElement?.getAttribute('data-testid') || document.activeElement?.textContent?.trim().slice(0, 80) }))
      await page.keyboard.press('Enter')
      keyboardAction.invoked = true
      await page.waitForTimeout(150)
      keyboardAction.after = await page.evaluate(() => ({ url: location.href, active: document.activeElement?.getAttribute('data-testid') || document.activeElement?.textContent?.trim().slice(0, 80) })).catch((error) => ({ navigation: String(error?.message || error) }))
    }
    const contrastSummary = {
      measured: snapshot.textContrast.length,
      min: snapshot.textContrast.length ? Math.min(...snapshot.textContrast.map((x) => x.ratio)) : null,
      belowAA: snapshot.textContrast.filter((x) => x.ratio < 4.5).slice(0, 12),
    }
    await page.screenshot({ path: path.join(outDir, `${key}.png`), fullPage: true })
    report.routes.push({ key, url: route.url, viewport, snapshot, keyboard: { focusSteps, keyboardAction }, contrastSummary, consoleErrors, pageErrors })
    await page.close()
    }
  }
}
report.limitations.push('Native browser Ctrl+/- zoom was not observable through the headless Playwright capability; visualViewport.scale stayed at 1.0. Width-based fallback was exercised at 390px, while native 125%/200% zoom remains open.')
report.limitations.push('Contrast extraction is a fallback heuristic using each leaf text element\'s direct computed backgroundColor; transparent/inherited backgrounds and canvas text are not fully resolved. Automated axe-core was not installed or invoked.')
await writeFile(path.join(outDir, 'report.json'), JSON.stringify(report, null, 2))
console.log(JSON.stringify({ routes: report.routes.length, errors: report.routes.flatMap((x) => [...x.consoleErrors, ...x.pageErrors]), routeSummaries: report.routes.map((x) => ({ key: x.key, focusableCount: x.snapshot.focusableCount, unlabeled: x.snapshot.unlabeledControls.length, overflow: x.snapshot.viewport.scrollWidth > x.snapshot.viewport.clientWidth, contrastMin: x.contrastSummary.min, contrastBelowAA: x.contrastSummary.belowAA.length, keyboardAction: x.keyboard.keyboardAction })) }, null, 2))
await browser.close()
