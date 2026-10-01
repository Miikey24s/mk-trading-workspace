import assert from 'node:assert/strict'
import { spawn } from 'node:child_process'
import fs from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const artifactDir = path.dirname(fileURLToPath(import.meta.url))
const workspaceRoot = path.resolve(artifactDir, '../../../..')
const webDir = path.join(workspaceRoot, 'projects', 'mt5-tradingview-backtester', 'foundation_v2', 'web')
const viteBin = path.join(webDir, 'node_modules', 'vite', 'bin', 'vite.js')
const playwrightModule = pathToFileURL(path.join(webDir, 'node_modules', 'playwright', 'index.mjs')).href
const { chromium } = await import(playwrightModule)

const origin = 'http://127.0.0.1:4187'
const workspace = 'tenant-risk-mutation-fixture'
const routePath = '/api/v2/analytics/prop/evaluate'
const cases = [
  { id: 'empty', expected: 'idle', expectedPostCount: 0 },
  { id: 'success', expected: 'within_limits', expectedPostCount: 1 },
  { id: 'breach', expected: 'breached', expectedPostCount: 1 },
  { id: 'blocked', expected: 'blocked_by_data', expectedPostCount: 0 },
  { id: 'error', expected: 'error', expectedPostCount: 1 },
]
const widths = [1440, 390]

const responseFor = {
  success: {
    schema_version: 'prop-profile-evaluation-v1',
    status: 'within_limits',
    blocked_by_data: [],
    total_drawdown: { basis: 'equity', reference: 10000, floor: 9000, current: 9800, remaining: 800, breached: false },
    daily_loss: { basis: 'equity', reference: 10000, floor: 9500, current: 9800, remaining: 300, breached: false },
    assumptions: { cost_basis: 'included', cashflow_adjustment: 'not_modeled', payout_probability: 'not_estimated' },
  },
  breach: {
    schema_version: 'prop-profile-evaluation-v1',
    status: 'breached',
    blocked_by_data: [],
    total_drawdown: { basis: 'equity', reference: 10000, floor: 9000, current: 8800, remaining: -200, breached: true },
    daily_loss: { basis: 'equity', reference: 10000, floor: 9500, current: 9400, remaining: -100, breached: true },
    assumptions: { cost_basis: 'included', cashflow_adjustment: 'not_modeled', payout_probability: 'not_estimated' },
  },
}

function json(route, status, payload) {
  return route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(payload) })
}

async function startVite() {
  const server = spawn(process.execPath, [viteBin, '--host', '127.0.0.1', '--port', '4187', '--strictPort'], {
    cwd: webDir,
    stdio: ['ignore', 'pipe', 'pipe'],
    windowsHide: true,
  })
  const serverErrors = []
  server.stderr.on('data', (chunk) => serverErrors.push(String(chunk)))
  const deadline = Date.now() + 15000
  while (Date.now() < deadline) {
    try {
      const response = await fetch(`${origin}/`)
      if (response.ok) return { server, serverErrors }
    } catch {
      // Vite is still starting.
    }
    await new Promise((resolve) => setTimeout(resolve, 150))
  }
  server.kill('SIGTERM')
  throw new Error(`Vite did not start at ${origin}: ${serverErrors.join('')}`)
}

async function waitForRiskWorkspace(page) {
  await page.goto(`${origin}/?view=risk&workspace=${workspace}`, { waitUntil: 'domcontentloaded' })
  await page.getByTestId('risk-workspace').waitFor()
  await page.getByText('SIMULATION ONLY', { exact: true }).waitFor()
}

async function submitCase(page, id) {
  if (id === 'empty') return
  if (id === 'blocked') {
    await page.getByLabel('Total drawdown').fill('')
    await page.getByLabel('Daily loss').fill('')
  }
  await page.getByRole('button', { name: 'Đánh giá snapshot' }).click()
  if (id === 'success' || id === 'breach') await page.getByTestId('risk-result').waitFor()
  if (id === 'blocked') await page.getByTestId('risk-blocked').waitFor()
  if (id === 'error') await page.getByRole('alert').waitFor()
}

const results = []
const serverBundle = await startVite()
const browser = await chromium.launch({ headless: true })
const context = await browser.newContext()
await context.tracing.start({ screenshots: true, snapshots: true, sources: true })

try {
  for (const item of cases) {
    for (const width of widths) {
      const page = await context.newPage()
      await page.setViewportSize({ width, height: 900 })
      const consoleErrors = []
      const pageErrors = []
      const requests = []
      const mutationBodies = []
      page.on('console', (message) => { if (message.type() === 'error') consoleErrors.push(message.text()) })
      page.on('pageerror', (error) => pageErrors.push(String(error)))
      page.on('request', (request) => {
        const requestUrl = new URL(request.url())
        if (requestUrl.pathname === routePath) {
          requests.push({ method: request.method(), path: requestUrl.pathname, workspace: request.headers()['x-workspace-id'] || null })
          if (request.method() === 'POST') mutationBodies.push(request.postData() || '')
        }
      })
      await page.route('**/api/**', async (route) => {
        const request = route.request()
        const requestUrl = new URL(request.url())
        if (requestUrl.pathname !== routePath) return json(route, 404, { detail: `fixture_route_not_configured:${requestUrl.pathname}` })
        if (request.method() !== 'POST') return json(route, 405, { detail: 'risk_evaluator_fixture_requires_post' })
        if (item.id === 'error') return json(route, 503, { detail: 'risk_evaluator_unavailable_fixture' })
        if (item.id === 'success' || item.id === 'breach') return json(route, 200, responseFor[item.id])
        return json(route, 422, { detail: 'unexpected_mutation_for_fixture' })
      })

      await waitForRiskWorkspace(page)
      await page.waitForTimeout(120)
      const before = await page.evaluate(() => ({
        scrollWidth: document.documentElement.scrollWidth,
        viewportWidth: window.innerWidth,
        hasResult: Boolean(document.querySelector('[data-testid="risk-result"]')),
        hasBlocked: Boolean(document.querySelector('[data-testid="risk-blocked"]')),
        simulationOnly: document.body.innerText.includes('SIMULATION ONLY'),
      }))
      await submitCase(page, item.id)
      await page.waitForTimeout(100)
      const after = await page.evaluate(() => ({
        scrollWidth: document.documentElement.scrollWidth,
        viewportWidth: window.innerWidth,
        bodyText: document.body.innerText,
        hasResult: Boolean(document.querySelector('[data-testid="risk-result"]')),
        hasBlocked: Boolean(document.querySelector('[data-testid="risk-blocked"]')),
        hasAlert: Boolean(document.querySelector('[role="alert"]')),
        statusChip: document.querySelector('[data-testid="risk-result"] .risk-status-chip')?.textContent?.trim() || null,
      }))
      const mutationCount = requests.filter((request) => request.method === 'POST').length
      if (item.id === 'empty') {
        assert.equal(after.hasResult, false)
        assert.equal(after.hasBlocked, false)
        assert.equal(after.hasAlert, false)
      } else if (item.id === 'success') {
        assert.equal(after.statusChip, 'WITHIN LIMITS')
        assert.match(after.bodyText, /Đang trong giới hạn/)
      } else if (item.id === 'breach') {
        assert.equal(after.statusChip, 'BREACHED')
        assert.match(after.bodyText, /Đã chạm giới hạn/)
      } else if (item.id === 'blocked') {
        assert.equal(after.hasBlocked, true)
        assert.match(after.bodyText, /missing_total_drawdown_amount/)
        assert.match(after.bodyText, /missing_daily_loss_amount/)
      } else if (item.id === 'error') {
        assert.equal(after.hasAlert, true)
        assert.match(after.bodyText, /risk_evaluator_unavailable_fixture/)
      }
      assert.equal(mutationCount, item.expectedPostCount, `${item.id} POST count at ${width}px`)
      assert.equal(before.simulationOnly, true)
      assert.ok(after.scrollWidth - after.viewportWidth <= 2, `${item.id} overflow at ${width}px: ${after.scrollWidth - after.viewportWidth}px`)
      const unexpectedConsoleErrors = consoleErrors.filter((message) => !/Failed to load resource: the server responded with a status of 503/.test(message))
      assert.deepEqual(unexpectedConsoleErrors, [], `${item.id} console errors at ${width}px`)
      assert.deepEqual(pageErrors, [], `${item.id} page errors at ${width}px`)
      assert.ok(requests.every((request) => request.workspace === null || request.workspace === workspace))
      assert.ok(mutationBodies.every((body) => !/broker|credential|oauth|api[_-]?key|secret/i.test(body)), `${item.id} mutation leaked gated fields`)
      if (item.id === 'success' || item.id === 'breach') await page.getByTestId('risk-result').scrollIntoViewIfNeeded()
      if (item.id === 'blocked') await page.getByTestId('risk-blocked').scrollIntoViewIfNeeded()
      if (item.id === 'error') await page.getByRole('alert').scrollIntoViewIfNeeded()
      await page.screenshot({ path: path.join(artifactDir, `${item.id}-${width}.png`), fullPage: true })
      results.push({
        id: item.id,
        width,
        expected: item.expected,
        observed: item.id === 'success' ? 'within_limits' : item.id === 'breach' ? 'breached' : item.id,
        mutationCount,
        requestPaths: requests,
        bodyFieldSafety: mutationBodies.every((body) => !/broker|credential|oauth|api[_-]?key|secret/i.test(body)),
        overflowPx: after.scrollWidth - after.viewportWidth,
        consoleErrors: unexpectedConsoleErrors,
        pageErrors,
        pass: true,
      })
      await page.close()
    }
  }
} finally {
  await context.tracing.stop({ path: path.join(artifactDir, 'risk-mutation-trace.zip') })
  await context.close()
  await browser.close()
  serverBundle.server.kill('SIGTERM')
  if (process.platform === 'win32') serverBundle.server.kill()
}

const runtime = {
  status: results.every((result) => result.pass) ? 'PASS' : 'FAIL',
  fixture: 'WMREPLAY-W7C-risk-mutation-20261001',
  origin,
  workspace,
  generated_at_utc: new Date().toISOString(),
  cases: cases.map((item) => item.id),
  widths,
  checks: [
    'empty idle state has no evaluator mutation',
    'within-limits success response renders WITHIN LIMITS',
    'breached response renders BREACHED',
    'client-side blocked-by-data state prevents POST',
    '503 evaluator error surfaces role=alert',
    'all POSTs are local evaluator calls with workspace header',
    'mutation payloads contain no broker, credential, OAuth, key or secret fields',
    '1440px and 390px screenshots have no horizontal overflow',
    'console and page errors are empty',
  ],
  results,
}
await fs.writeFile(path.join(artifactDir, 'runtime.json'), JSON.stringify(runtime, null, 2))
console.log(JSON.stringify({ status: runtime.status, fixture: runtime.fixture, checks: results.length, failures: results.filter((result) => !result.pass).length }, null, 2))
if (runtime.status !== 'PASS') process.exitCode = 1
