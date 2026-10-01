import assert from 'node:assert/strict'
import { mkdir } from 'node:fs/promises'
import path from 'node:path'
import { createRequire } from 'node:module'

const webRoot = 'D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester/foundation_v2/web'
const { chromium } = createRequire(path.join(webRoot, 'package.json'))('playwright')
const origin = process.env.TW_UI_ORIGIN || 'http://127.0.0.1:5173'
const outputDir = path.dirname(new URL(import.meta.url).pathname).replace(/^\/(\w):/, '$1:')
await mkdir(outputDir, { recursive: true })

function relativeLuminance([r, g, b]) {
  const channel = (value) => { const v = value / 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4 }
  return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)
}

function contrastRatio(foreground, background) {
  const a = relativeLuminance(foreground)
  const b = relativeLuminance(background)
  return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05)
}

const browser = await chromium.launch({ headless: true })
const report = []
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
  const consoleErrors = []
  page.on('console', (message) => { if (message.type() === 'error') consoleErrors.push(message.text()) })
  for (const theme of ['dark', 'light']) {
    for (const width of [1440, 390]) {
      await page.setViewportSize({ width, height: width === 390 ? 844 : 900 })
      await page.goto(`${origin}/?workspace=tenant-a&view=replay&surface=workspace&session=replay-fixture&dataset=ui-live-fixture&mode=Practice&cursor=3`, { waitUntil: 'networkidle' })
      await page.getByTestId('replay-history-view').waitFor()
      const toggle = page.getByTestId('theme-toggle')
      const expectedLight = theme === 'light'
      const currentLight = (await toggle.getAttribute('aria-pressed')) === 'true'
      if (currentLight !== expectedLight) await toggle.click()
      await page.getByTestId('replay-history-view').waitFor()
      const result = await page.evaluate(() => {
        const relativeLuminance = ([r, g, b]) => {
          const channel = (value) => { const v = value / 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4 }
          return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)
        }
        const parseRgb = (value) => { const match = String(value).match(/rgba?\(([^)]+)\)/); return match ? match[1].split(',').slice(0, 3).map((item) => Number.parseFloat(item.trim())) : null }
        const effectiveBackground = (element) => {
          let current = element
          while (current) {
            const color = getComputedStyle(current).backgroundColor
            const rgb = parseRgb(color)
            if (rgb && !(rgb.length === 4 && rgb[3] === 0) && color !== 'rgba(0, 0, 0, 0)') return rgb
            current = current.parentElement
          }
          return [255, 255, 255]
        }
        const items = [...document.querySelectorAll('.replay-history-banner strong, .replay-history-banner span')].map((element) => {
          const style = getComputedStyle(element)
          const foreground = parseRgb(style.color)
          const background = effectiveBackground(element)
          return { text: element.textContent?.trim() || '', color: style.color, background, ratio: foreground && background ? Number(((Math.max(relativeLuminance(foreground), relativeLuminance(background)) + 0.05) / (Math.min(relativeLuminance(foreground), relativeLuminance(background)) + 0.05)).toFixed(3)) : null }
        })
        return { theme: document.querySelector('[data-testid="fxreplay-shell"]')?.getAttribute('data-theme'), items, overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth }
      })
      assert.equal(result.theme, theme)
      assert.equal(result.overflow, 0)
      assert.equal(result.items.length, 3)
      assert.ok(result.items.every((item) => item.ratio >= 4.5), `${theme}/${width} contrast ratios: ${JSON.stringify(result.items)}`)
      const filename = `replay-contrast-${theme}-${width}.png`
      await page.screenshot({ path: path.join(outputDir, filename), fullPage: true })
      report.push({ theme, width, ...result, screenshot: filename })
    }
  }
  assert.deepEqual(consoleErrors, [])
} finally {
  await browser.close()
}
await import('node:fs/promises').then(({ writeFile }) => writeFile(path.join(outputDir, 'report.json'), JSON.stringify({ status: 'PASS', source_change: false, report }, null, 2)))
console.log(JSON.stringify({ status: 'PASS', source_change: false, report }, null, 2))
