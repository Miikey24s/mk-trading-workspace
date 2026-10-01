import { pathToFileURL } from 'node:url'
const { chromium } = await import(pathToFileURL('D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester/foundation_v2/web/node_modules/playwright/index.mjs').href)
import { mkdir, writeFile } from 'node:fs/promises'
import path from 'node:path'

const origin = 'http://127.0.0.1:5173'
const artifactDir = path.dirname(new URL(import.meta.url).pathname).replace(/^\/(.)\:/, '$1:')
await mkdir(artifactDir, { recursive: true })
const dataset = {
  dataset_id: 'eurusd-h1', provider_id: 'local', instrument_id: 'EURUSDm', timeframe: 'H1', row_count: 100,
  first_timestamp: 1710000000, last_timestamp: 1710036000, quality_status: 'verified', artifact_sha256: 'a'.repeat(64),
  holdout_access: false, holdout_policy: { mode: 'none' }, source: { provider: 'local', license_use: 'test' },
  instrument_spec: { contract_size: 100000 },
}
const engines = { items: [{ id: 'reference', available: false }] }
const completedJob = {
  job_id: 'job-1', dataset_id: dataset.dataset_id, status: 'completed', attempt_no: 1, updated_at_utc: '2026-10-01T00:00:00Z',
  result: { job_id: 'job-1', dataset_sha256: dataset.artifact_sha256, metrics_schema_version: 'research-v1', trade_count: 0, metrics: { net_pnl: null, win_rate_pct: null, closed_trade_balance_max_drawdown: null } },
}
const json = (body, status = 200) => ({ status, contentType: 'application/json', body: JSON.stringify(body) })

async function setupPage() {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
  const pageErrors = []
  const consoleErrors = []
  const requests = []
  page.on('pageerror', (error) => pageErrors.push(String(error)))
  page.on('console', (message) => { if (message.type() === 'error') consoleErrors.push(message.text()) })
  page.on('request', (request) => { if (request.url().includes('/api/')) requests.push({ method: request.method(), pathname: new URL(request.url()).pathname }) })
  return { page, pageErrors, consoleErrors, requests }
}

async function runDataCase() {
  const { page, pageErrors, consoleErrors, requests } = await setupPage()
  let datasetAttempts = 0
  await page.route('**/api/**', async (route) => {
    const pathname = new URL(route.request().url()).pathname
    if (pathname === '/api/v2/data/datasets') {
      datasetAttempts += 1
      return route.fulfill(datasetAttempts === 1 ? json({ detail: 'fixture_catalog_unavailable' }, 503) : json({ items: [dataset] }))
    }
    if (pathname === '/api/v2/data/providers') return route.fulfill(json({ items: [] }))
    return route.fulfill(json({ detail: `unexpected ${pathname}` }, 404))
  })
  await page.goto(`${origin}/?view=data&workspace=tenant-a`, { waitUntil: 'domcontentloaded' })
  await page.getByTestId('data-desk-retry').waitFor({ state: 'visible', timeout: 5000 })
  const errorText = await page.getByRole('alert').innerText()
  await page.getByTestId('data-desk-retry').click()
  await page.getByTestId('data-desk-dataset-table').waitFor({ state: 'visible', timeout: 5000 })
  const readyText = await page.getByTestId('data-desk-dataset-table').innerText()
  await page.screenshot({ path: path.join(artifactDir, 'data-retry-1440.png'), fullPage: true })
  await page.setViewportSize({ width: 390, height: 844 })
  await page.screenshot({ path: path.join(artifactDir, 'data-retry-390.png'), fullPage: true })
  const result = { id: 'data-catalog-503-retry-200', datasetAttempts, errorText, readyText, requests, pageErrors, consoleErrors, unexpectedConsoleErrors: consoleErrors.filter((entry) => !entry.includes('status of 503')) }
  await page.close()
  return result
}

async function runResearchCatalogCase() {
  const { page, pageErrors, consoleErrors, requests } = await setupPage()
  let datasetAttempts = 0
  await page.route('**/api/**', async (route) => {
    const pathname = new URL(route.request().url()).pathname
    if (pathname === '/api/v2/data/datasets') {
      datasetAttempts += 1
      return route.fulfill(datasetAttempts === 1 ? json({ detail: 'fixture_catalog_unavailable' }, 503) : json({ items: [dataset] }))
    }
    if (pathname === '/api/v2/research/engines') return route.fulfill(json(engines))
    return route.fulfill(json({ detail: `unexpected ${pathname}` }, 404))
  })
  await page.goto(`${origin}/?view=research&workspace=tenant-a`, { waitUntil: 'domcontentloaded' })
  await page.getByTestId('research-catalog-retry').waitFor({ state: 'visible', timeout: 5000 })
  const errorText = await page.getByRole('alert').innerText()
  await page.getByTestId('research-catalog-retry').click()
  await page.getByTestId('research-run-form').waitFor({ state: 'visible', timeout: 5000 })
  const readyText = await page.getByTestId('research-run-form').innerText()
  await page.screenshot({ path: path.join(artifactDir, 'research-catalog-retry-1440.png'), fullPage: true })
  await page.setViewportSize({ width: 390, height: 844 })
  await page.screenshot({ path: path.join(artifactDir, 'research-catalog-retry-390.png'), fullPage: true })
  const result = { id: 'research-catalog-503-retry-200', datasetAttempts, errorText, readyText, requests, pageErrors, consoleErrors, unexpectedConsoleErrors: consoleErrors.filter((entry) => !entry.includes('status of 503')) }
  await page.close()
  return result
}

async function runResearchJobCase() {
  const { page, pageErrors, consoleErrors, requests } = await setupPage()
  let jobAttempts = 0
  await page.route('**/api/**', async (route) => {
    const pathname = new URL(route.request().url()).pathname
    if (pathname === '/api/v2/research/jobs/job-1') {
      jobAttempts += 1
      return route.fulfill(jobAttempts === 1 ? json({ detail: 'fixture_job_unavailable' }, 503) : json(completedJob))
    }
    return route.fulfill(json({ detail: `unexpected ${pathname}` }, 404))
  })
  await page.goto(`${origin}/?view=research&workspace=tenant-a&job=job-1&dataset=eurusd-h1`, { waitUntil: 'domcontentloaded' })
  await page.getByTestId('research-job-retry').waitFor({ state: 'visible', timeout: 5000 })
  const errorText = await page.getByRole('alert').innerText()
  await page.getByTestId('research-job-retry').click()
  await page.getByTestId('research-result').waitFor({ state: 'visible', timeout: 5000 })
  const readyText = await page.getByTestId('research-result').innerText()
  await page.screenshot({ path: path.join(artifactDir, 'research-job-retry-1440.png'), fullPage: true })
  await page.setViewportSize({ width: 390, height: 844 })
  await page.screenshot({ path: path.join(artifactDir, 'research-job-retry-390.png'), fullPage: true })
  const result = { id: 'research-job-503-retry-200', jobAttempts, errorText, readyText, requests, pageErrors, consoleErrors, unexpectedConsoleErrors: consoleErrors.filter((entry) => !entry.includes('status of 503')) }
  await page.close()
  return result
}

const browser = await chromium.launch({ headless: true })
let results
try {
  results = [await runDataCase(), await runResearchCatalogCase(), await runResearchJobCase()]
} finally {
  await browser.close()
}
await writeFile(path.join(artifactDir, 'retry-results.json'), JSON.stringify({ origin, generated_at_utc: new Date().toISOString(), results }, null, 2))
for (const result of results) console.log(JSON.stringify({ id: result.id, attempts: result.datasetAttempts || result.jobAttempts, pageErrors: result.pageErrors.length, consoleErrors: result.consoleErrors.length, unexpectedConsoleErrors: result.unexpectedConsoleErrors.length, requests: result.requests }))
if (results.some((result) => result.pageErrors.length || result.unexpectedConsoleErrors.length || (result.datasetAttempts || result.jobAttempts) !== 2)) process.exitCode = 1


