import fs from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const { chromium } = await import(pathToFileURL('D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester/foundation_v2/web/node_modules/playwright/index.mjs').href)

const origin = 'http://127.0.0.1:5173'
const workspace = 'tenant-a'
const artifactDir = path.dirname(fileURLToPath(import.meta.url))
const contextUrl = `${origin}/?view=journal&workspace=${workspace}&session=session-1&trade=trade-1&dataset=eurusd-h1&cursor=10&cutoff=1710003600&mode=practice&playbook=pb-breakout&playbook_revision=2`
const json = (body, status = 200) => ({
  status,
  contentType: 'application/json',
  headers: { 'access-control-allow-origin': '*' },
  body: JSON.stringify(body),
})

const initialPayload = {
  entry_type: 'observation',
  note: 'Giá phá range nhưng chưa đóng trên vùng.',
  tags: ['fixture', 'create'],
  observation: 'Nến H1 test vùng kháng cự tại cutoff.',
  hypothesis: 'Có thể tiếp diễn nếu đóng trên range.',
  decision: 'Chờ xác nhận.',
  plan: 'Replay thêm một nhịp rồi review.',
  actual_result: null,
  next_action: 'Kiểm chứng nến kế tiếp.',
  overlay_ids: ['annotation-fixture'],
  source: {
    kind: 'replay-trade', id: 'trade-1', session_id: 'session-1', trade_id: 'trade-1',
    dataset_id: 'eurusd-h1', cursor_index: 10, cutoff_timestamp: '1710003600', mode: 'practice',
    playbook_id: 'pb-breakout', playbook_revision: 2,
  },
}

function makeRecord(payload, revision = 1) {
  return {
    record_id: 'journal-fixture-1',
    revision,
    created_at_utc: '2026-10-01T00:00:00Z',
    updated_at_utc: revision === 1 ? '2026-10-01T00:00:00Z' : '2026-10-01T00:02:00Z',
    payload,
  }
}

async function setupPage(context, viewport, requests) {
  const page = await context.newPage()
  await page.setViewportSize(viewport)
  const pageErrors = []
  const consoleErrors = []
  page.on('pageerror', (error) => pageErrors.push(String(error)))
  page.on('console', (message) => { if (message.type() === 'error') consoleErrors.push(message.text()) })
  page.on('request', (request) => {
    if (request.url().includes('/api/')) requests.push({ method: request.method(), pathname: new URL(request.url()).pathname, body: request.postData() || null })
  })
  return { page, pageErrors, consoleErrors }
}

async function runCase(viewport, label) {
  const browserContext = await browser.newContext()
  await browserContext.tracing.start({ screenshots: true, snapshots: true, sources: true })
  const requests = []
  const state = { record: null, getAttempts: 0, createAttempts: 0, revisionAttempts: 0, conflictSeen: false }
  const { page, pageErrors, consoleErrors } = await setupPage(browserContext, viewport, requests)
  await page.route('**/api/**', async (route) => {
    const request = route.request()
    const pathname = new URL(request.url()).pathname
    if (pathname === '/api/v2/journal' && request.method() === 'GET') {
      state.getAttempts += 1
      // First read is deliberately unavailable, then the user-visible retry succeeds.
      if (state.getAttempts === 1) return route.fulfill(json({ detail: 'fixture_journal_unavailable' }, 503))
      return route.fulfill(json({ items: state.record ? [state.record] : [] }))
    }
    if (pathname === '/api/v2/journal' && request.method() === 'POST') {
      state.createAttempts += 1
      const payload = JSON.parse(request.postData() || '{}')
      state.record = makeRecord(payload, 1)
      return route.fulfill(json(state.record, 201))
    }
    if (pathname === '/api/v2/journal/journal-fixture-1/revisions' && request.method() === 'POST') {
      state.revisionAttempts += 1
      const body = JSON.parse(request.postData() || '{}')
      if (state.revisionAttempts === 1) {
        state.conflictSeen = true
        return route.fulfill(json({ detail: 'revision_conflict: expected revision is stale; reload current record' }, 409))
      }
      if (body.expected_revision !== state.record?.revision) {
        return route.fulfill(json({ detail: `revision_conflict: expected ${body.expected_revision}, current ${state.record?.revision}` }, 409))
      }
      state.record = makeRecord(body.payload, state.record.revision + 1)
      return route.fulfill(json(state.record, 200))
    }
    return route.fulfill(json({ detail: `unexpected fixture request ${request.method()} ${pathname}` }, 404))
  })

  const result = { id: `journal-mutation-${label}`, viewport, requests, pageErrors, consoleErrors, assertions: {}, state }
  try {
    await page.goto(contextUrl, { waitUntil: 'domcontentloaded' })
    await page.getByRole('alert').waitFor({ state: 'visible', timeout: 5000 })
    result.assertions.initialErrorVisible = (await page.getByRole('alert').innerText()).includes('fixture_journal_unavailable')
    await page.getByRole('button', { name: 'Thử lại' }).click()
    await page.getByText('0 ghi chú', { exact: false }).waitFor({ state: 'visible', timeout: 5000 })
    result.assertions.retryReadEmpty = state.getAttempts === 2

    await page.getByRole('button', { name: /\+ Ghi chú/ }).click()
    await page.getByRole('textbox', { name: 'Nội dung' }).fill(initialPayload.note)
    await page.getByRole('textbox', { name: 'Điều đã quan sát' }).fill(initialPayload.observation)
    await page.getByRole('textbox', { name: 'Giả thuyết' }).fill(initialPayload.hypothesis)
    await page.getByRole('textbox', { name: 'Quyết định / lý do bỏ qua' }).fill(initialPayload.decision)
    await page.getByRole('textbox', { name: 'Plan dự kiến' }).fill(initialPayload.plan)
    await page.getByRole('textbox', { name: 'Bước tiếp theo' }).fill(initialPayload.next_action)
    await page.getByLabel('Tags').fill(initialPayload.tags.join(', '))
    await page.getByLabel('Overlay liên quan').fill(initialPayload.overlay_ids.join(', '))
    await page.getByRole('button', { name: 'Lưu ghi chú' }).click()
    await page.getByRole('button', { name: /Quan sát Giá phá range nhưng chưa đóng trên vùng/ }).waitFor({ state: 'visible', timeout: 5000 })
    result.assertions.createReadback = state.createAttempts === 1 && state.record?.revision === 1 && (await page.getByText('REVISION 1', { exact: false }).count()) > 0
    await page.screenshot({ path: path.join(artifactDir, `journal-create-${label}.png`), fullPage: true })

    await page.getByRole('button', { name: 'Sửa' }).click()
    await page.getByRole('textbox', { name: 'Nội dung' }).fill('Đã xác nhận breakout sau khi replay thêm một nến.')
    await page.getByRole('button', { name: 'Lưu revision' }).click()
    await page.getByRole('alert').filter({ hasText: 'revision_conflict' }).waitFor({ state: 'visible', timeout: 5000 })
    result.assertions.conflictVisible = state.conflictSeen && (await page.getByRole('alert').innerText()).includes('revision_conflict')
    result.assertions.remainsEditing = (await page.getByRole('button', { name: 'Lưu revision' }).count()) === 1
    await page.screenshot({ path: path.join(artifactDir, `journal-conflict-${label}.png`), fullPage: true })

    await page.getByRole('button', { name: 'Lưu revision' }).click()
    await page.getByRole('button', { name: /Đã xác nhận breakout sau khi replay thêm một nến/ }).waitFor({ state: 'visible', timeout: 5000 })
    result.assertions.revisionRetryReadback = state.revisionAttempts === 2 && state.record?.revision === 2 && (await page.getByText('REVISION 2', { exact: false }).count()) > 0
    result.assertions.formErrorCleared = (await page.getByRole('alert').filter({ hasText: 'revision_conflict' }).count()) === 0
    await page.screenshot({ path: path.join(artifactDir, `journal-readback-${label}.png`), fullPage: true })

    const geometry = await page.evaluate(() => ({ width: innerWidth, scrollWidth: document.body.scrollWidth, height: document.body.scrollHeight }))
    result.geometry = geometry
  } catch (error) {
    result.failure = String(error?.stack || error)
  } finally {
    await browserContext.tracing.stop({ path: path.join(artifactDir, `journal-mutation-${label}.trace.zip`) }).catch(() => {})
    await page.close().catch(() => {})
    await browserContext.close().catch(() => {})
  }
  result.unexpectedApiRequests = requests.filter(({ pathname }) => pathname !== '/api/v2/journal' && pathname !== '/api/v2/journal/journal-fixture-1/revisions')
  result.unexpectedConsoleErrors = consoleErrors.filter((entry) => !entry.includes('503') && !entry.includes('409'))
  result.pass = !result.failure && Object.values(result.assertions).every(Boolean) && result.geometry?.scrollWidth <= result.geometry?.width && pageErrors.length === 0 && result.unexpectedConsoleErrors.length === 0 && result.unexpectedApiRequests.length === 0
  return result
}

const browser = await chromium.launch({ headless: true })
let results
try {
  results = [await runCase({ width: 1440, height: 900 }, '1440'), await runCase({ width: 390, height: 844 }, '390')]
} finally {
  await browser.close()
}
const evidence = {
  origin,
  contextUrl,
  generated_at_utc: new Date().toISOString(),
  contract: 'local Playwright route fixture only; all /api/v2/journal reads/creates/revisions are intercepted; no backend/provider/broker/auth/external call is used',
  cases: results,
}
await fs.writeFile(path.join(artifactDir, 'runtime.json'), JSON.stringify(evidence, null, 2))
for (const result of results) console.log(JSON.stringify({ id: result.id, pass: result.pass, assertions: result.assertions, geometry: result.geometry, requests: result.requests.map(({ method, pathname }) => `${method} ${pathname}`), pageErrors: result.pageErrors.length, unexpectedApiRequests: result.unexpectedApiRequests.length, unexpectedConsoleErrors: result.unexpectedConsoleErrors.length }))
if (results.some((result) => !result.pass)) process.exitCode = 1





