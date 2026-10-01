import { createRequire } from 'node:module'
import { mkdir, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const checkpointDir = path.dirname(fileURLToPath(import.meta.url))
const webDir = path.resolve(checkpointDir, '../../../../projects/mt5-tradingview-backtester/foundation_v2/web')
const { chromium } = createRequire(import.meta.url)(path.join(webDir, 'node_modules', 'playwright'))
const origin = process.env.WMREPLAY_ORIGIN || 'http://127.0.0.1:5173'
await mkdir(checkpointDir, { recursive: true })

const browser = await chromium.launch({ headless: true, executablePath: process.env.TW_V2_CHROME || undefined })
const context = await browser.newContext({ viewport: { width: 1440, height: 900 } })
const page = await context.newPage()
const requests = []
const errors = []
page.on('request', request => {
  if (request.url().includes('/api/')) requests.push({ method: request.method(), url: request.url() })
})
page.on('pageerror', error => errors.push(String(error)))
page.on('console', message => { if (message.type() === 'error') errors.push(`console:${message.text()}`) })
await page.goto(`${origin}/?view=overview&workspace=tenant-a`, { waitUntil: 'networkidle' })
await page.waitForTimeout(300)
const before = await page.evaluate(() => ({
  status: document.querySelector('[data-testid="dashboard-data-state"]')?.textContent?.trim() || '',
  metrics: [...document.querySelectorAll('[data-testid="dashboard-performance"] .fx-dashboard-metric > strong')].map(node => node.textContent?.trim()),
  charts: [...document.querySelectorAll('[data-testid="dashboard-performance"] .fx-dashboard-chart-empty p')].map(node => node.textContent?.trim()),
  scope: [...document.querySelectorAll('.fx-dashboard-filter')].map(node => ({ text: node.textContent.trim(), pressed: node.getAttribute('aria-pressed') })),
  overflow: document.documentElement.scrollWidth - window.innerWidth,
}))
const filters = page.locator('.fx-dashboard-filter')
if (await filters.count() !== 2) throw new Error(`expected 2 scope buttons, got ${await filters.count()}`)
await filters.nth(1).click()
await page.waitForTimeout(250)
const after = await page.evaluate(() => ({
  status: document.querySelector('[data-testid="dashboard-data-state"]')?.textContent?.trim() || '',
  metrics: [...document.querySelectorAll('[data-testid="dashboard-performance"] .fx-dashboard-metric > strong')].map(node => node.textContent?.trim()),
  charts: [...document.querySelectorAll('[data-testid="dashboard-performance"] .fx-dashboard-chart-empty p')].map(node => node.textContent?.trim()),
  scope: [...document.querySelectorAll('.fx-dashboard-filter')].map(node => ({ text: node.textContent.trim(), pressed: node.getAttribute('aria-pressed') })),
  overflow: document.documentElement.scrollWidth - window.innerWidth,
}))
await page.screenshot({ path: path.join(checkpointDir, 'dashboard-perf-audit-1440.png'), fullPage: true })
await page.setViewportSize({ width: 390, height: 844 })
await page.waitForTimeout(250)
const mobile = await page.evaluate(() => ({
  status: document.querySelector('[data-testid="dashboard-data-state"]')?.textContent?.trim() || '',
  metrics: [...document.querySelectorAll('[data-testid="dashboard-performance"] .fx-dashboard-metric > strong')].map(node => node.textContent?.trim()),
  charts: [...document.querySelectorAll('[data-testid="dashboard-performance"] .fx-dashboard-chart-empty p')].map(node => node.textContent?.trim()),
  scope: [...document.querySelectorAll('.fx-dashboard-filter')].map(node => ({ text: node.textContent.trim(), pressed: node.getAttribute('aria-pressed') })),
  viewport: { width: window.innerWidth, height: window.innerHeight },
  document: { scrollWidth: document.documentElement.scrollWidth, scrollHeight: document.documentElement.scrollHeight },
}))
await page.screenshot({ path: path.join(checkpointDir, 'dashboard-perf-audit-390.png'), fullPage: true })
const health = await fetch('http://127.0.0.1:8010/health').then(response => response.json())
const overview = await fetch('http://127.0.0.1:8010/api/v2/overview', { headers: { 'X-Workspace-Id': 'tenant-a' } }).then(response => response.json())
const report = { origin, route: `${origin}/?view=overview&workspace=tenant-a`, requests, before, after, mobile, errors, health, overview }
await writeFile(path.join(checkpointDir, 'report.json'), `${JSON.stringify(report, null, 2)}\n`)
await browser.close()
console.log(JSON.stringify({ status: 'PASS', requests, before, after, mobile, errors, health, overview }, null, 2))
