import assert from 'node:assert/strict'
import { mkdir } from 'node:fs/promises'
import path from 'node:path'
import { createRequire } from 'node:module'

const webRoot = 'D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester/foundation_v2/web'
const { chromium } = createRequire(path.join(webRoot, 'package.json'))('playwright')

const origin = process.env.TW_UI_ORIGIN || 'http://127.0.0.1:5173'
const evidenceDir = path.dirname(new URL(import.meta.url).pathname).replace(/^\/(\w):/, '$1:')
await mkdir(evidenceDir, { recursive: true })

const browser = await chromium.launch({ headless: true })
const checks = []
try {
  for (const width of [1440, 390]) {
    const page = await browser.newPage({ viewport: { width, height: width === 390 ? 844 : 900 } })
    const errors = []
    page.on('console', (message) => { if (message.type() === 'error') errors.push(message.text()) })

    await page.goto(`${origin}/?workspace=tenant-a&view=overview`, { waitUntil: 'networkidle' })
    await page.getByTestId('dashboard-inventory').waitFor()
    const dashboardOverflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)
    assert.ok(dashboardOverflow <= 2, `dashboard overflow ${width}px: ${dashboardOverflow}`)
    await page.screenshot({ path: path.join(evidenceDir, `dashboard-${width}.png`), fullPage: true })
    checks.push({ route: 'overview', width, dashboardInventory: await page.getByTestId('dashboard-inventory').innerText(), overflow: dashboardOverflow })

    await page.goto(`${origin}/?workspace=tenant-a&view=replay&surface=workspace&session=replay-fixture&dataset=ui-live-fixture&mode=Practice`, { waitUntil: 'networkidle' })
    await page.getByTestId('replay-chart').waitFor()
    const replayOverflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)
    assert.ok(replayOverflow <= 2, `replay overflow ${width}px: ${replayOverflow}`)
    assert.equal(await page.getByTestId('replay-chart').getAttribute('data-visible-row-count'), '5')
    assert.match(await page.getByTestId('replay-lock').innerText(), /Broker locked/i)
    assert.match(await page.locator('.replay-evidence-strip').innerText(), /tương lai đang ẩn/i)
    await page.screenshot({ path: path.join(evidenceDir, `replay-${width}.png`), fullPage: true })
    checks.push({ route: 'replay', width, visibleRows: 5, overflow: replayOverflow })

    const unexpectedErrors = errors.filter((message) => !/favicon|404.*research|fixture_job_not_found/i.test(message))
    assert.deepEqual(unexpectedErrors, [], `${width}px unexpected console errors`)
    await page.close()
  }
} finally {
  await browser.close()
}

console.log(JSON.stringify({ status: 'PASS', fixture: 'ui-live-offline', checks }, null, 2))
