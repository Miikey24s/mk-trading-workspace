import fs from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const { chromium } = await import(pathToFileURL(path.resolve(process.cwd(), 'projects/mt5-tradingview-backtester/foundation_v2/web/node_modules/playwright/index.mjs')).href)

const origin = 'http://127.0.0.1:5173'
const workspace = 'tenant-a'
const artifactDir = path.dirname(fileURLToPath(import.meta.url))
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
  source: { provider: 'local', license_use: 'fixture-only' },
  instrument_spec: { contract_size: 100000 },
}
const catalog = { items: [dataset] }
const engines = { items: [{ id: 'nautilus', available: true }] }
const result = {
  job_id: 'job-research-fixture',
  dataset_sha256: dataset.artifact_sha256,
  metrics_schema_version: 'research-v1',
  trade_count: 2,
  metrics: {
    net_pnl: 42.5,
    win_rate_pct: 50,
    closed_trade_balance_max_drawdown: 18,
    closed_trade_balance_curve: [
      { closed_trade_balance: 10000 },
      { closed_trade_balance: 10042.5 },
    ],
  },
}

const json = (body, status = 200) => ({
  status,
  contentType: 'application/json',
  body: JSON.stringify(body),
  headers: { 'access-control-allow-origin': '*' },
})

const job = (status, overrides = {}) => ({
  job_id: 'job-research-fixture',
  dataset_id: dataset.dataset_id,
  status,
  attempt_no: 1,
  updated_at_utc: '2026-10-01T00:00:00Z',
  ...overrides,
})

function settle(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

async function makePage(context) {
  const page = await context.newPage()
  const pageErrors = []
  const consoleErrors = []
  const requests = []
  const responses = []
  page.on('pageerror', (error) => pageErrors.push(String(error)))
  page.on('console', (message) => { if (message.type() === 'error') consoleErrors.push(message.text()) })
  page.on('request', (request) => {
    if (!request.url().includes('/api/')) return
    let body = null
    try { body = request.postDataJSON() } catch { body = request.postData() || null }
    requests.push({ method: request.method(), pathname: new URL(request.url()).pathname, body })
  })
  page.on('response', (response) => {
    if (response.url().includes('/api/')) responses.push({ method: response.request().method(), pathname: new URL(response.url()).pathname, status: response.status() })
  })
  return { page, pageErrors, consoleErrors, requests, responses }
}

async function viewportSnapshot(page) {
  return page.evaluate(() => ({
    width: innerWidth,
    height: innerHeight,
    scrollWidth: document.documentElement.scrollWidth,
    bodyScrollWidth: document.body.scrollWidth,
    pageHeight: document.documentElement.scrollHeight,
    overflow: Math.max(0, document.documentElement.scrollWidth - innerWidth),
    status: document.querySelector('[data-testid="research-status"]')?.textContent?.trim() || '',
    text: document.body.innerText.slice(0, 4500),
  }))
}

async function capture(page, name) {
  await page.screenshot({ path: path.join(artifactDir, `${name}.png`), fullPage: true })
  return viewportSnapshot(page)
}

async function routeFixture(page, scenario) {
  await page.route('**/api/**', async (route) => {
    const request = route.request()
    const pathname = new URL(request.url()).pathname
    const method = request.method()
    if (method === 'GET' && pathname === '/api/v2/data/datasets') return route.fulfill(json(catalog))
    if (method === 'GET' && pathname === '/api/v2/research/engines') return route.fulfill(json(engines))
    if (method === 'POST' && pathname === '/api/v2/research/jobs') {
      scenario.createCalls += 1
      const payload = request.postDataJSON()
      scenario.createBodies.push(payload)
      if (scenario.kind === 'conflict') return route.fulfill(json({ detail: 'active_research_job_conflict' }, 409))
      return route.fulfill(json(job('running')))
    }
    if (method === 'GET' && pathname === '/api/v2/research/jobs/job-research-fixture/checkpoint') {
      scenario.checkpointCalls += 1
      return route.fulfill(json({ progress: { fraction: scenario.kind === 'complete' ? 0.55 : 0.2 }, phase: 'fixture-running', attempt_no: 1 }))
    }
    if (method === 'GET' && pathname === '/api/v2/research/jobs/job-research-fixture') {
      scenario.jobGets += 1
      if (scenario.kind === 'complete') {
        if (scenario.jobGets === 1) return route.fulfill(json(job('running')))
        return route.fulfill(json(job('completed', { result })))
      }
      if (scenario.kind === 'cancel') return route.fulfill(json(scenario.cancelCalls > 0 ? job('canceled', { error_code: 'cancelled_by_user' }) : job('running')))
      return route.fulfill(json(job('running')))
    }
    if (method === 'POST' && pathname === '/api/v2/research/jobs/job-research-fixture/cancel') {
      scenario.cancelCalls += 1
      if (scenario.kind === 'cancel') return route.fulfill(json(job('canceled', { error_code: 'cancelled_by_user' })))
      return route.fulfill(json({ detail: 'cancel_conflict' }, 409))
    }
    return route.fulfill(json({ detail: `unexpected ${method} ${pathname}` }, 404))
  })
}

async function runComplete(browser) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } })
  await context.tracing.start({ screenshots: true, snapshots: true, sources: true })
  const { page, pageErrors, consoleErrors, requests, responses } = await makePage(context)
  const scenario = { kind: 'complete', createCalls: 0, cancelCalls: 0, jobGets: 0, checkpointCalls: 0, createBodies: [] }
  await routeFixture(page, scenario)
  await page.goto(`${origin}/?view=research&workspace=${workspace}`, { waitUntil: 'domcontentloaded' })
  await page.getByTestId('research-run-form').waitFor({ state: 'visible', timeout: 5000 })
  await page.getByLabel('Starting balance').fill('12500')
  await page.getByTestId('research-run-submit').click()
  await page.getByTestId('research-cancel').waitFor({ state: 'visible', timeout: 5000 })
  const runningDesktop = await capture(page, 'submit-running-1440')
  await page.setViewportSize({ width: 390, height: 844 })
  const runningMobile = await capture(page, 'submit-running-390')
  await page.getByTestId('research-result').waitFor({ state: 'visible', timeout: 7000 })
  const completeMobile = await capture(page, 'submit-completed-390')
  await page.setViewportSize({ width: 1440, height: 900 })
  const completeDesktop = await capture(page, 'submit-completed-1440')
  const observed = { runningDesktop, runningMobile, completeDesktop, completeMobile }
  const pass = scenario.createCalls === 1 && scenario.jobGets >= 2 && scenario.checkpointCalls >= 1 && observed.completeDesktop.status === 'Hoàn tất' && Object.values(observed).every((item) => item.overflow === 0) && pageErrors.length === 0 && consoleErrors.length === 0
  await page.close()
  await context.tracing.stop({ path: path.join(artifactDir, 'research-mutation.trace.zip') })
  await context.close()
  return { id: 'submit-running-completed', scenario, observed, requests, responses, pageErrors, consoleErrors, pass }
}

async function runCancel(browser) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } })
  const { page, pageErrors, consoleErrors, requests, responses } = await makePage(context)
  const scenario = { kind: 'cancel', createCalls: 0, cancelCalls: 0, jobGets: 0, checkpointCalls: 0, createBodies: [] }
  await routeFixture(page, scenario)
  await page.goto(`${origin}/?view=research&workspace=${workspace}`, { waitUntil: 'domcontentloaded' })
  await page.getByTestId('research-run-form').waitFor({ state: 'visible', timeout: 5000 })
  await page.getByTestId('research-run-submit').click()
  await page.getByTestId('research-cancel').waitFor({ state: 'visible', timeout: 5000 })
  const runningDesktop = await capture(page, 'cancel-running-1440')
  await page.setViewportSize({ width: 390, height: 844 })
  const runningMobile = await capture(page, 'cancel-running-390')
  await page.setViewportSize({ width: 1440, height: 900 })
  await page.getByTestId('research-cancel').click()
  await page.getByTestId('research-terminal-result').waitFor({ state: 'visible', timeout: 5000 })
  const canceledDesktop = await capture(page, 'cancel-canceled-1440')
  await page.setViewportSize({ width: 390, height: 844 })
  const canceledMobile = await capture(page, 'cancel-canceled-390')
  const observed = { runningDesktop, canceledDesktop, canceledMobile }
  const pass = scenario.createCalls === 1 && scenario.cancelCalls === 1 && canceledDesktop.status === 'Đã hủy' && Object.values(observed).every((item) => item.overflow === 0) && pageErrors.length === 0 && consoleErrors.length === 0
  await page.close()
  await context.close()
  return { id: 'cancel-running-job', scenario, observed, requests, responses, pageErrors, consoleErrors, pass }
}

async function runConflict(browser) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } })
  const { page, pageErrors, consoleErrors, requests, responses } = await makePage(context)
  const scenario = { kind: 'conflict', createCalls: 0, cancelCalls: 0, jobGets: 0, checkpointCalls: 0, createBodies: [] }
  await routeFixture(page, scenario)
  await page.goto(`${origin}/?view=research&workspace=${workspace}`, { waitUntil: 'domcontentloaded' })
  await page.getByTestId('research-run-form').waitFor({ state: 'visible', timeout: 5000 })
  await page.getByTestId('research-run-submit').click()
  await page.getByTestId('research-job-retry').waitFor({ state: 'visible', timeout: 5000 })
  const conflictDesktop = await capture(page, 'conflict-409-1440')
  await page.setViewportSize({ width: 390, height: 844 })
  const conflictMobile = await capture(page, 'conflict-409-390')
  const observed = { conflictDesktop, conflictMobile }
  const unexpectedConsoleErrors = consoleErrors.filter((entry) => !entry.includes('status of 409'))
  const pass = scenario.createCalls === 1 && scenario.cancelCalls === 0 && responses.some((item) => item.method === 'POST' && item.pathname === '/api/v2/research/jobs' && item.status === 409) && conflictDesktop.text.includes('active_research_job_conflict') && Object.values(observed).every((item) => item.overflow === 0) && pageErrors.length === 0 && unexpectedConsoleErrors.length === 0
  await page.close()
  await context.close()
  return { id: 'create-conflict-409', scenario, observed, requests, responses, pageErrors, consoleErrors, unexpectedConsoleErrors, pass }
}

await fs.mkdir(artifactDir, { recursive: true })
const browser = await chromium.launch({ headless: true })
let results
try {
  results = [await runComplete(browser), await runCancel(browser), await runConflict(browser)]
} finally {
  await browser.close()
}
const payload = { origin, workspace, generated_at_utc: new Date().toISOString(), fixture_only: true, results }
await fs.writeFile(path.join(artifactDir, 'runtime.json'), JSON.stringify(payload, null, 2), 'utf8')
for (const item of results) console.log(JSON.stringify({ id: item.id, pass: item.pass, pageErrors: item.pageErrors.length, consoleErrors: item.consoleErrors.length, unexpectedConsoleErrors: item.unexpectedConsoleErrors?.length || 0, requests: item.requests.length, responses: item.responses.length, statuses: Object.fromEntries(Object.entries(item.observed).map(([key, value]) => [key, value.status])) }))
if (results.some((item) => !item.pass)) process.exitCode = 1
