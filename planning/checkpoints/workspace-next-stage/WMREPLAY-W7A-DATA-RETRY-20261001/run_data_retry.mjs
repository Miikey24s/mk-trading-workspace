import assert from 'node:assert/strict'
import { mkdir, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const playwrightModule = pathToFileURL('D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester/foundation_v2/web/node_modules/playwright/index.mjs').href
const { chromium } = await import(playwrightModule)

const origin = 'http://127.0.0.1:5173'
const artifactDir = path.dirname(fileURLToPath(import.meta.url))
await mkdir(artifactDir, { recursive: true })

const dataset = {
  dataset_id: 'eurusd-h1',
  provider_id: 'local',
  instrument_id: 'EURUSDm',
  timeframe: 'H1',
  row_count: 100,
  first_timestamp: 1710000000,
  last_timestamp: 1710036000,
  quality_status: 'verified',
  artifact_sha256: 'a'.repeat(64),
  holdout_access: false,
  holdout_policy: { mode: 'none' },
  source: { provider: 'local', license_use: 'test' },
  instrument_spec: { contract_size: 100000 },
}

const json = (body, status = 200) => ({
  status,
  contentType: 'application/json',
  body: JSON.stringify(body),
})

const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 })
await context.tracing.start({ screenshots: true, snapshots: true, sources: true })
const page = await context.newPage()
const requests = []
const pageErrors = []
const consoleErrors = []
let datasetAttempts = 0
let providerAttempts = 0

page.on('pageerror', (error) => pageErrors.push(String(error)))
page.on('console', (message) => {
  if (message.type() === 'error') consoleErrors.push(message.text())
})
page.on('request', (request) => {
  const requestUrl = new URL(request.url())
  if (requestUrl.pathname.startsWith('/api/')) {
    requests.push({ method: request.method(), pathname: requestUrl.pathname })
  }
})

await page.route('**/api/**', async (route) => {
  const requestUrl = new URL(route.request().url())
  if (requestUrl.pathname === '/api/v2/data/datasets') {
    datasetAttempts += 1
    return route.fulfill(datasetAttempts === 1
      ? json({ detail: 'fixture_catalog_unavailable' }, 503)
      : json({ items: [dataset], total: 1, holdout_access: false }))
  }
  if (requestUrl.pathname === '/api/v2/data/providers') {
    providerAttempts += 1
    return route.fulfill(json({ items: [{ provider_id: 'local', capabilities: {}, readiness: { connection_mode: 'offline', entitlement_status: 'unverified', production_ready: false, network_access: false } }] }))
  }
  return route.fulfill(json({ detail: `unexpected_route:${requestUrl.pathname}` }, 404))
})

await page.goto(`${origin}/?view=data&workspace=tenant-a`, { waitUntil: 'domcontentloaded' })
await page.getByTestId('data-desk-retry').waitFor({ state: 'visible', timeout: 5000 })
const errorText = await page.getByRole('alert').innerText()
assert.match(errorText, /fixture_catalog_unavailable/)
assert.equal(await page.getByTestId('data-desk-retry').isDisabled(), false)

await page.getByTestId('data-desk-retry').click()
await page.getByTestId('data-desk-dataset-table').waitFor({ state: 'visible', timeout: 5000 })
const readyText = await page.getByTestId('data-desk-dataset-table').innerText()
assert.match(readyText, /eurusd-h1/)
assert.equal(datasetAttempts, 2)
assert.equal(providerAttempts, 2)

await page.screenshot({ path: path.join(artifactDir, 'data-retry-1440.png'), fullPage: true })
await page.setViewportSize({ width: 390, height: 844 })
await page.screenshot({ path: path.join(artifactDir, 'data-retry-390.png'), fullPage: true })

const exhaustionPage = await context.newPage()
let exhaustionDatasetAttempts = 0
let exhaustionProviderAttempts = 0
exhaustionPage.on('pageerror', (error) => pageErrors.push(String(error)))
exhaustionPage.on('console', (message) => {
  if (message.type() === 'error') consoleErrors.push(message.text())
})
exhaustionPage.on('request', (request) => {
  const requestUrl = new URL(request.url())
  if (requestUrl.pathname.startsWith('/api/')) {
    requests.push({ method: request.method(), pathname: requestUrl.pathname, case: 'exhaustion' })
  }
})
await exhaustionPage.route('**/api/**', async (route) => {
  const requestUrl = new URL(route.request().url())
  if (requestUrl.pathname === '/api/v2/data/datasets') {
    exhaustionDatasetAttempts += 1
    return route.fulfill(json({ detail: 'fixture_catalog_still_unavailable' }, 503))
  }
  if (requestUrl.pathname === '/api/v2/data/providers') {
    exhaustionProviderAttempts += 1
    return route.fulfill(json({ items: [] }))
  }
  return route.fulfill(json({ detail: `unexpected_route:${requestUrl.pathname}` }, 404))
})
await exhaustionPage.goto(`${origin}/?view=data&workspace=tenant-a`, { waitUntil: 'domcontentloaded' })
for (let retryIndex = 0; retryIndex < 3; retryIndex += 1) {
  await exhaustionPage.getByTestId('data-desk-retry').click()
  await exhaustionPage.getByRole('alert').waitFor({ state: 'visible', timeout: 5000 })
}
const exhaustedRetry = exhaustionPage.getByTestId('data-desk-retry')
assert.equal(await exhaustedRetry.isDisabled(), true)
assert.match(await exhaustionPage.getByRole('alert').innerText(), /Đã thử lại 3 lần/)
assert.equal(exhaustionDatasetAttempts, 4)
assert.equal(exhaustionProviderAttempts, 4)
await exhaustionPage.setViewportSize({ width: 390, height: 844 })
await exhaustedRetry.scrollIntoViewIfNeeded()
await exhaustionPage.screenshot({ path: path.join(artifactDir, 'data-retry-exhausted-alert-390.png'), fullPage: false })

const unexpectedConsoleErrors = consoleErrors.filter((entry) => !/status of 503/.test(entry))
const nonGetRequests = requests.filter((request) => request.method !== 'GET')
const result = {
  id: 'data-catalog-503-retry-200',
  origin,
  attempts: { datasets: datasetAttempts, providers: providerAttempts },
  exhaustedAttempts: { datasets: exhaustionDatasetAttempts, providers: exhaustionProviderAttempts },
  errorText,
  readyText,
  requests,
  nonGetRequests,
  pageErrors,
  consoleErrors,
  unexpectedConsoleErrors,
  screenshots: ['data-retry-1440.png', 'data-retry-390.png', 'data-retry-exhausted-alert-390.png'],
  trace: 'data-retry.trace.zip',
}

await page.close()
await exhaustionPage.close()
await context.tracing.stop({ path: path.join(artifactDir, 'data-retry.trace.zip') })
await context.close()
await browser.close()
await writeFile(path.join(artifactDir, 'retry-results.json'), JSON.stringify({ generated_at_utc: new Date().toISOString(), ...result }, null, 2))
console.log(JSON.stringify({ id: result.id, attempts: result.attempts, nonGetRequests: result.nonGetRequests.length, pageErrors: result.pageErrors.length, unexpectedConsoleErrors: result.unexpectedConsoleErrors.length }))

if (pageErrors.length || unexpectedConsoleErrors.length || nonGetRequests.length || datasetAttempts !== 2 || providerAttempts !== 2 || exhaustionDatasetAttempts !== 4 || exhaustionProviderAttempts !== 4) {
  process.exitCode = 1
}
