import { pathToFileURL } from 'node:url'
import { mkdir, writeFile } from 'node:fs/promises'
import path from 'node:path'

const { chromium } = await import(pathToFileURL('D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester/foundation_v2/web/node_modules/playwright/index.mjs').href)

const origin = 'http://127.0.0.1:5173'
const artifactDir = path.dirname(new URL(import.meta.url).pathname).replace(/^\/(.)\:/, '$1:')
await mkdir(artifactDir, { recursive: true })

const csvText = [
  'time,open,high,low,close',
  '2026-01-01T00:00:00Z,1.10000,1.10100,1.09900,1.10050',
  '2026-01-01T01:00:00Z,1.10050,1.10200,1.10000,1.10150',
  '',
].join('\n')

const baselineDataset = {
  dataset_id: 'dataset-baseline',
  provider_id: 'local-csv',
  instrument_id: 'EURUSDm',
  timeframe: 'H1',
  row_count: 2,
  first_timestamp: 1767225600,
  last_timestamp: 1767229200,
  quality_status: 'fixture-only',
  artifact_sha256: '1'.repeat(64),
  normalized_sha256: '2'.repeat(64),
  holdout_access: false,
  holdout_policy: { mode: 'none' },
  source: { provider: 'local-csv', license_use: 'fixture', retrieved_at_utc: '2026-01-01T00:00:00Z' },
  instrument_spec: { contract_size: 100000 },
  transform_version: 'fixture-v1',
}

const importedDataset = {
  ...baselineDataset,
  dataset_id: 'dataset-imported-fixture',
  artifact_sha256: '3'.repeat(64),
  normalized_sha256: '4'.repeat(64),
  source: { provider: 'local-csv', license_use: 'user-supplied-local', retrieved_at_utc: '2026-10-01T00:00:00Z' },
}

const preview = {
  dataset_id: importedDataset.dataset_id,
  row_count: 2,
  unique_row_count: 2,
  available_range: { from_utc: 1767225600, to_utc: 1767229200 },
  quality: { disposition: 'pass', duplicates: 0, out_of_order: 0, gaps: [], overlapping_intervals: 0 },
  raw_sha256: '5'.repeat(64),
  normalized_sha256: importedDataset.normalized_sha256,
}

const providers = [{
  provider_id: 'local-csv',
  capabilities: { read_history: false, read_holdout: false },
  readiness: { production_ready: false, connection_mode: 'offline', entitlement_status: 'unverified', network_access: false },
}]

const json = (body, status = 200) => ({ status, contentType: 'application/json', body: JSON.stringify(body) })

async function setupCase(viewport) {
  const context = await browser.newContext({ viewport })
  await context.tracing.start({ screenshots: true, snapshots: true, sources: true })
  const page = await context.newPage()
  const pageErrors = []
  const consoleErrors = []
  const requests = []
  page.on('pageerror', (error) => pageErrors.push(String(error)))
  page.on('console', (message) => { if (message.type() === 'error') consoleErrors.push(message.text()) })
  page.on('request', (request) => {
    if (request.url().includes('/api/')) {
      let body = null
      try { body = request.postDataJSON() } catch { /* GET or non-JSON */ }
      requests.push({ method: request.method(), pathname: new URL(request.url()).pathname, body })
    }
  })
  return { context, page, pageErrors, consoleErrors, requests }
}

async function chooseCsv(page, name = 'eurusd-fixture.csv') {
  const chooserPromise = page.waitForEvent('filechooser')
  await page.getByTestId('data-desk-file-input').click()
  const chooser = await chooserPromise
  await chooser.setFiles({ name, mimeType: 'text/csv', buffer: Buffer.from(csvText, 'utf8') })
  await page.getByTestId('data-desk-file-state').waitFor({ state: 'visible', timeout: 5000 })
}

function assertCommon(result, label) {
  if (result.pageErrors.length) throw new Error(`${label}: page errors: ${result.pageErrors.join('; ')}`)
  if (result.unexpectedConsoleErrors?.length) throw new Error(`${label}: console errors: ${result.unexpectedConsoleErrors.join('; ')}`)
  if (result.unexpectedRequests.length) throw new Error(`${label}: unexpected requests: ${JSON.stringify(result.unexpectedRequests)}`)
}

async function runSuccessCase() {
  const result = await setupCase({ width: 1440, height: 900 })
  let catalogRows = []
  let previewAttempts = 0
  let importAttempts = 0
  let datasetReads = 0
  await result.page.route('**/api/**', async (route) => {
    const request = route.request()
    const pathname = new URL(request.url()).pathname
    if (request.headers()['x-workspace-id'] !== 'tenant-a') throw new Error(`missing tenant workspace header for ${pathname}`)
    if (pathname === '/api/v2/data/datasets') {
      datasetReads += 1
      return route.fulfill(json({ items: catalogRows, holdout_access: false }))
    }
    if (pathname === '/api/v2/data/providers') return route.fulfill(json({ items: providers }))
    if (pathname === '/api/v2/data/csv/preview') {
      previewAttempts += 1
      const body = request.postDataJSON()
      if (body?.csv_text !== csvText) throw new Error('preview payload did not preserve browser CSV text')
      return route.fulfill(json({ schema_version: 'u2-data-desk-preview-view-v1', workspace_id: 'tenant-a', execution_capability: false, preview }))
    }
    if (pathname === '/api/v2/data/csv/import') {
      importAttempts += 1
      const body = request.postDataJSON()
      if (body?.csv_text !== csvText) throw new Error('import payload did not preserve browser CSV text')
      catalogRows = [importedDataset]
      return route.fulfill(json({ schema_version: 'u2-data-desk-import-view-v1', execution_capability: false, dataset: importedDataset }, 201))
    }
    return route.fulfill(json({ detail: `unexpected ${request.method()} ${pathname}` }, 404))
  })

  await result.page.goto(`${origin}/?view=data&workspace=tenant-a`, { waitUntil: 'domcontentloaded' })
  await result.page.getByTestId('data-desk-import').waitFor({ state: 'visible', timeout: 5000 })
  await chooseCsv(result.page)
  const prePreviewState = await result.page.getByTestId('data-desk-file-state').innerText()
  if (!prePreviewState.includes('Chưa gửi lên server')) throw new Error(`unexpected pre-preview state: ${prePreviewState}`)

  await result.page.getByTestId('data-desk-preview-button').click()
  await result.page.getByTestId('data-desk-quality-report').waitFor({ state: 'visible', timeout: 5000 })
  const previewText = await result.page.getByTestId('data-desk-quality-report').innerText()
  if (!previewText.includes('2') || !previewText.includes('Đạt kiểm tra cơ bản')) throw new Error(`preview did not show expected quality: ${previewText}`)
  const previewRequest = result.requests.find((request) => request.pathname === '/api/v2/data/csv/preview')
  if (!previewRequest || previewRequest.method !== 'POST') throw new Error('preview POST was not observed')

  const initialDatasetReads = datasetReads
  await result.page.getByTestId('data-desk-import-button').click()
  await result.page.getByTestId('data-desk-import-success').waitFor({ state: 'visible', timeout: 5000 })
  await result.page.getByTestId('data-desk-dataset-table').waitFor({ state: 'visible', timeout: 5000 })
  const successText = await result.page.getByTestId('data-desk-import-success').innerText()
  const readbackText = await result.page.getByTestId('data-desk-dataset-table').innerText()
  if (!successText.includes(importedDataset.dataset_id) || !readbackText.includes(importedDataset.dataset_id)) throw new Error('import success/readback did not show imported dataset')

  await result.page.screenshot({ path: path.join(artifactDir, 'data-import-success-1440.png'), fullPage: true })
  await result.page.setViewportSize({ width: 390, height: 844 })
  const mobileMetrics = await result.page.evaluate(() => {
    const panelTitle = document.querySelector('.rd-import-panel .rd-panel-head > div')
    const reportHead = document.querySelector('.rd-import-report-head')
    return {
      viewportWidth: window.innerWidth,
      documentScrollWidth: document.documentElement.scrollWidth,
      panelTitleWidth: panelTitle?.getBoundingClientRect().width || 0,
      reportHeadWidth: reportHead?.getBoundingClientRect().width || 0,
    }
  })
  if (mobileMetrics.documentScrollWidth > mobileMetrics.viewportWidth || mobileMetrics.panelTitleWidth < 100 || mobileMetrics.reportHeadWidth < 100) throw new Error(`mobile geometry regression: ${JSON.stringify(mobileMetrics)}`)
  await result.page.screenshot({ path: path.join(artifactDir, 'data-import-success-390.png'), fullPage: true })
  const unexpectedRequests = result.requests.filter((request) => ![
    'GET /api/v2/data/datasets', 'GET /api/v2/data/providers',
    'POST /api/v2/data/csv/preview', 'POST /api/v2/data/csv/import',
  ].includes(`${request.method} ${request.pathname}`))
  result.unexpectedRequests = unexpectedRequests
  result.datasetReads = datasetReads
  result.previewAttempts = previewAttempts
  result.importAttempts = importAttempts
  result.prePreviewState = prePreviewState
  result.previewText = previewText
  result.successText = successText
  result.readbackText = readbackText
  result.readbackObservedAfterImport = datasetReads > initialDatasetReads && readbackText.includes(importedDataset.dataset_id)
  result.mobileMetrics = mobileMetrics
  result.unexpectedConsoleErrors = result.consoleErrors
  if (previewAttempts !== 1 || importAttempts !== 1 || !result.readbackObservedAfterImport) {
    console.error(JSON.stringify({ debug: 'success-readback', previewAttempts, importAttempts, datasetReads, initialDatasetReads, requests: result.requests, readbackText }))
    throw new Error('success flow did not perform exactly one preview, one import and a post-import readback')
  }
  assertCommon(result, 'success')
  await result.context.tracing.stop({ path: path.join(artifactDir, 'data-import-success.trace.zip') })
  await result.page.close()
  await result.context.close()
  return result
}

async function runRollbackCase() {
  const result = await setupCase({ width: 1440, height: 900 })
  let catalogRows = [baselineDataset]
  let previewAttempts = 0
  let importAttempts = 0
  let datasetReads = 0
  await result.page.route('**/api/**', async (route) => {
    const request = route.request()
    const pathname = new URL(request.url()).pathname
    if (request.headers()['x-workspace-id'] !== 'tenant-a') throw new Error(`missing tenant workspace header for ${pathname}`)
    if (pathname === '/api/v2/data/datasets') {
      datasetReads += 1
      return route.fulfill(json({ items: catalogRows, holdout_access: false }))
    }
    if (pathname === '/api/v2/data/providers') return route.fulfill(json({ items: providers }))
    if (pathname === '/api/v2/data/csv/preview') {
      previewAttempts += 1
      return route.fulfill(json({ schema_version: 'u2-data-desk-preview-view-v1', workspace_id: 'tenant-a', execution_capability: false, preview }))
    }
    if (pathname === '/api/v2/data/csv/import') {
      importAttempts += 1
      return route.fulfill(json({ detail: 'fixture_import_conflict' }, 409))
    }
    return route.fulfill(json({ detail: `unexpected ${request.method()} ${pathname}` }, 404))
  })

  await result.page.goto(`${origin}/?view=data&workspace=tenant-a`, { waitUntil: 'domcontentloaded' })
  await result.page.getByTestId('data-desk-import').waitFor({ state: 'visible', timeout: 5000 })
  await chooseCsv(result.page, 'eurusd-conflict-fixture.csv')
  await result.page.getByTestId('data-desk-preview-button').click()
  await result.page.getByTestId('data-desk-quality-report').waitFor({ state: 'visible', timeout: 5000 })
  const readsBeforeImport = datasetReads
  await result.page.getByTestId('data-desk-import-button').click()
  await result.page.getByTestId('data-desk-import-error').waitFor({ state: 'visible', timeout: 5000 })
  const errorText = await result.page.getByTestId('data-desk-import-error').innerText()
  const tableText = await result.page.getByTestId('data-desk-dataset-table').innerText()
  if (!errorText.includes('fixture_import_conflict')) throw new Error(`rollback error was not surfaced: ${errorText}`)
  if (!tableText.includes(baselineDataset.dataset_id) || tableText.includes(importedDataset.dataset_id)) throw new Error(`catalog changed after failed import: ${tableText}`)
  if (datasetReads !== readsBeforeImport) throw new Error('failed import unexpectedly triggered catalog readback')
  const reportStillVisible = await result.page.getByTestId('data-desk-quality-report').isVisible()
  if (!reportStillVisible) throw new Error('quality preview was lost after failed import; user cannot inspect rollback context')

  await result.page.screenshot({ path: path.join(artifactDir, 'data-import-rollback-1440.png'), fullPage: true })
  await result.page.setViewportSize({ width: 390, height: 844 })
  const mobileMetrics = await result.page.evaluate(() => {
    const panelTitle = document.querySelector('.rd-import-panel .rd-panel-head > div')
    const reportHead = document.querySelector('.rd-import-report-head')
    return {
      viewportWidth: window.innerWidth,
      documentScrollWidth: document.documentElement.scrollWidth,
      panelTitleWidth: panelTitle?.getBoundingClientRect().width || 0,
      reportHeadWidth: reportHead?.getBoundingClientRect().width || 0,
    }
  })
  if (mobileMetrics.documentScrollWidth > mobileMetrics.viewportWidth || mobileMetrics.panelTitleWidth < 100 || mobileMetrics.reportHeadWidth < 100) throw new Error(`mobile geometry regression: ${JSON.stringify(mobileMetrics)}`)
  await result.page.screenshot({ path: path.join(artifactDir, 'data-import-rollback-390.png'), fullPage: true })
  const unexpectedRequests = result.requests.filter((request) => ![
    'GET /api/v2/data/datasets', 'GET /api/v2/data/providers',
    'POST /api/v2/data/csv/preview', 'POST /api/v2/data/csv/import',
  ].includes(`${request.method} ${request.pathname}`))
  result.unexpectedRequests = unexpectedRequests
  result.datasetReads = datasetReads
  result.previewAttempts = previewAttempts
  result.importAttempts = importAttempts
  result.errorText = errorText
  result.catalogAfterFailure = tableText
  result.previewRetainedAfterFailure = reportStillVisible
  result.noCatalogReadbackAfterFailure = datasetReads === readsBeforeImport
  result.mobileMetrics = mobileMetrics
  result.unexpectedConsoleErrors = result.consoleErrors.filter((entry) => !entry.includes('status of 409'))
  assertCommon(result, 'rollback')
  await result.context.tracing.stop({ path: path.join(artifactDir, 'data-import-rollback.trace.zip') })
  await result.page.close()
  await result.context.close()
  return result
}

const browser = await chromium.launch({ headless: true })
let results
try {
  results = { success: await runSuccessCase(), rollback: await runRollbackCase() }
} finally {
  await browser.close()
}

const serializable = JSON.parse(JSON.stringify({
  origin,
  generated_at_utc: new Date().toISOString(),
  contract: {
    workspace: 'tenant-a',
    endpoints: ['/api/v2/data/datasets', '/api/v2/data/providers', '/api/v2/data/csv/preview', '/api/v2/data/csv/import'],
    execution_capability: false,
    external_network: false,
    broker_or_provider_access: false,
  },
  results,
}, (key, value) => key === 'context' || key === 'page' ? undefined : value))
await writeFile(path.join(artifactDir, 'data-mutation-results.json'), JSON.stringify(serializable, null, 2))
for (const [id, result] of Object.entries(results)) {
  console.log(JSON.stringify({ id, previewAttempts: result.previewAttempts, importAttempts: result.importAttempts, datasetReads: result.datasetReads, pageErrors: result.pageErrors.length, consoleErrors: result.consoleErrors.length, unexpectedRequests: result.unexpectedRequests.length }))
}
if (Object.values(results).some((result) => result.pageErrors.length || result.consoleErrors.length || result.unexpectedRequests.length || result.previewAttempts !== 1 || result.importAttempts !== 1)) process.exitCode = 1
