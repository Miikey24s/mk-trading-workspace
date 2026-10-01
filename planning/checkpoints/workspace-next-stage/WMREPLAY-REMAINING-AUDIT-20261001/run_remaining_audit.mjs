import fs from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
const { chromium } = await import(pathToFileURL(path.resolve(process.cwd(), 'node_modules/playwright/index.mjs')).href)
function pathToFileURL(value) { return new URL("file:///" + value.replaceAll("\\\\", "/")) }

const origin = 'http://127.0.0.1:5173'
const workspace = 'tenant-a'
const artifactDir = path.dirname(fileURLToPath(import.meta.url))
const cases = [
  {
    id: 'data-empty',
    url: '/?view=data&workspace=tenant-a',
    ready: '[data-testid="data-desk-root"]',
    fixture: {
      '/api/v2/data/datasets': { items: [] },
      '/api/v2/data/providers': { items: [] },
    },
    assertions: ['data-desk-root', 'data-desk-import', 'data-desk-empty'],
  },
  {
    id: 'data-selected',
    url: '/?view=data&workspace=tenant-a&dataset=eurusd-h1',
    ready: '[data-testid="data-desk-root"]',
    fixture: {
      '/api/v2/data/datasets': { items: [{ dataset_id: 'eurusd-h1', provider_id: 'local', instrument_id: 'EURUSDm', timeframe: 'H1', row_count: 100, first_timestamp: 1710000000, last_timestamp: 1710036000, quality_status: 'verified', artifact_sha256: 'a'.repeat(64), holdout_access: false, holdout_policy: { mode: 'none' }, source: { provider: 'local', license_use: 'test', retrieved_at_utc: '2026-09-30T00:00:00Z' }, instrument_spec: { contract_size: 100000 } }] },
      '/api/v2/data/providers': { items: [{ provider_id: 'local', display_name: 'Local', capability: { connection_mode: 'offline', entitlement_status: 'unverified' } }] },
    },
    assertions: ['data-desk-root', 'dataset-details', 'data-desk-import'],
  },
  {
    id: 'research-empty',
    url: '/?view=research&workspace=tenant-a',
    ready: '[data-testid="research-root"]',
    fixture: {
      '/api/v2/data/datasets': { items: [] },
      '/api/v2/research/engines': { items: [] },
    },
    assertions: ['research-root', 'research-data-context', 'research-quality-takeaway', 'research-run-form'],
  },
  {
    id: 'research-selected',
    url: '/?view=research&workspace=tenant-a&dataset=eurusd-h1',
    ready: '[data-testid="research-root"]',
    fixture: {
      '/api/v2/data/datasets': { items: [{ dataset_id: 'eurusd-h1', provider_id: 'local', instrument_id: 'EURUSDm', timeframe: 'H1', row_count: 100, first_timestamp: 1710000000, last_timestamp: 1710036000, quality_status: 'verified', artifact_sha256: 'a'.repeat(64), holdout_access: false, holdout_policy: { mode: 'none' }, source: { provider: 'local' }, instrument_spec: { contract_size: 100000 } }] },
      '/api/v2/research/engines': { items: [{ engine_id: 'reference', available: false }] },
    },
    assertions: ['research-root', 'research-data-context', 'research-quality-takeaway', 'research-run-form'],
  },
  {
    id: 'journal-empty',
    url: '/?view=journal&workspace=tenant-a',
    ready: '[data-testid="journal-workspace"]',
    fixture: { '/api/v2/journal': { items: [] } },
    assertions: ['journal-workspace'],
  },
  {
    id: 'journal-context',
    url: '/?view=journal&workspace=tenant-a&session=session-1&trade=trade-1&cursor=10',
    ready: '[data-testid="journal-workspace"]',
    fixture: { '/api/v2/journal': { items: [] } },
    assertions: ['journal-workspace'],
  },
  {
    id: 'trade-empty',
    url: '/?view=trade&workspace=tenant-a',
    ready: '[data-testid="trade-workspace"]',
    fixture: { '/api/v2/data/datasets': { items: [] } },
    assertions: ['trade-workspace', 'trade-simulator-banner'],
  },
  {
    id: 'risk-idle',
    url: '/?view=risk&workspace=tenant-a',
    ready: '[data-testid="risk-workspace"]',
    fixture: {},
    assertions: ['risk-workspace'],
  },
  {
    id: 'playbook-empty',
    url: '/?view=playbook&workspace=tenant-a',
    ready: '[data-testid="playbook-root"]',
    fixture: { '/api/v2/playbooks': { items: [] } },
    assertions: ['playbook-root', 'playbook-empty'],
  },
  {
    id: 'playbook-selected',
    url: '/?view=playbook&workspace=tenant-a&playbook=pb-1',
    ready: '[data-testid="playbook-root"]',
    fixture: {
      '/api/v2/playbooks': { items: [{ record_id: 'pb-1', revision: 2, created_at_utc: '2026-09-30T00:00:00Z', updated_at_utc: '2026-09-30T01:00:00Z', payload: { name: 'Breakout', status: 'draft', execution_capability: 'manual-only', rules: { entry: 'close' } } }] },
      '/api/v2/playbooks/pb-1/revisions': { items: [{ revision: 1, payload: { name: 'Breakout', status: 'draft', rules: { entry: 'open' } } }, { revision: 2, payload: { name: 'Breakout', status: 'draft', rules: { entry: 'close' } } }] },
    },
    assertions: ['playbook-root', 'playbook-summary', 'playbook-diff'],
  },
]

function fixtureResponse(data, status = 200) {
  return { status, contentType: 'application/json', body: JSON.stringify(data), headers: { 'access-control-allow-origin': '*' } }
}

const browser = await chromium.launch({ headless: true })
const results = []
try {
  for (const item of cases) {
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
    const consoleErrors = []
    const pageErrors = []
    const requests = []
    page.on('console', (message) => { if (message.type() === 'error') consoleErrors.push(message.text()) })
    page.on('pageerror', (error) => pageErrors.push(String(error)))
    page.on('request', (request) => { if (request.url().includes('/api/')) requests.push({ method: request.method(), url: new URL(request.url()).pathname }) })
    await page.route('**/api/**', async (route) => {
      const pathname = new URL(route.request().url()).pathname
      const fixture = item.fixture[pathname]
      if (fixture !== undefined) return route.fulfill(fixtureResponse(fixture))
      return route.fulfill(fixtureResponse({ detail: `unmocked ${pathname}` }, 404))
    })
    await page.goto(`${origin}${item.url}`, { waitUntil: 'domcontentloaded' })
    await page.waitForSelector(item.ready, { timeout: 5000 })
    await page.waitForTimeout(150)
    const observed = await page.evaluate((assertions) => {
      const body = document.body
      const ids = Object.fromEntries(assertions.map((id) => [id, Boolean(document.querySelector(`[data-testid="${id}"]`))]))
      const visibleText = body.innerText.slice(0, 5000)
      return { ids, title: document.title, h1: document.querySelector('h1')?.textContent?.trim() || '', width: innerWidth, scrollWidth: body.scrollWidth, height: body.scrollHeight, visibleText }
    }, item.assertions)
    await page.screenshot({ path: path.join(artifactDir, `${item.id}-1440.png`), fullPage: true })
    await page.setViewportSize({ width: 768, height: 1024 })
    await page.waitForTimeout(100)
    const tablet = await page.evaluate(() => ({ width: innerWidth, scrollWidth: document.body.scrollWidth, height: document.body.scrollHeight }))
    await page.screenshot({ path: path.join(artifactDir, `${item.id}-768.png`), fullPage: true })
    await page.setViewportSize({ width: 390, height: 844 })
    await page.waitForTimeout(100)
    const mobile = await page.evaluate(() => ({ width: innerWidth, scrollWidth: document.body.scrollWidth, height: document.body.scrollHeight }))
    await page.screenshot({ path: path.join(artifactDir, `${item.id}-390.png`), fullPage: true })
    results.push({ id: item.id, url: item.url, observed, tablet, mobile, consoleErrors, pageErrors, requests, pass: Object.values(observed.ids).every(Boolean) && observed.scrollWidth <= observed.width && tablet.scrollWidth <= tablet.width && mobile.scrollWidth <= mobile.width && pageErrors.length === 0 })
    await page.close()
  }
} finally {
  await browser.close()
}
await fs.writeFile(path.join(artifactDir, 'audit-results.json'), JSON.stringify({ origin, generated_at_utc: new Date().toISOString(), cases: results }, null, 2))
for (const result of results) console.log(JSON.stringify({ id: result.id, pass: result.pass, h1: result.observed.h1, desktopOverflow: result.observed.scrollWidth - result.observed.width, tabletOverflow: result.tablet.scrollWidth - result.tablet.width, mobileOverflow: result.mobile.scrollWidth - result.mobile.width, consoleErrors: result.consoleErrors.length, pageErrors: result.pageErrors.length, requests: result.requests }))
if (results.some((result) => !result.pass)) process.exitCode = 1





