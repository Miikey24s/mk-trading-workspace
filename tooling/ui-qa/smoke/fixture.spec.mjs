import { test, expect } from '@playwright/test'
import { startFixture } from '../fixtures/server.mjs'

let fixture
test.beforeAll(async () => { fixture = await startFixture() })
test.afterAll(async () => { await fixture?.close() })
test.beforeEach(async ({ context, page }) => {
  await context.route('**/*', route => new URL(route.request().url()).origin === fixture.url
    ? route.continue() : route.abort('blockedbyclient'))
  await page.goto(fixture.url, { waitUntil: 'domcontentloaded' })
})

test('form works and fixture state survives reload', async ({ page }) => {
  await page.getByLabel('Tên phiên thử công cụ').fill('Phiên QA có dấu')
  await page.getByRole('button', { name: 'Lưu bản thử' }).click()
  await expect(page.getByRole('status')).toHaveText('Đã lưu: Phiên QA có dấu')
  await page.reload()
  await expect(page.getByRole('status')).toHaveText('Đã lưu: Phiên QA có dấu')
})

test('invalid input fails visibly without a success record', async ({ page }) => {
  await page.getByRole('button', { name: 'Lưu bản thử' }).click()
  await expect(page.getByRole('alert')).toHaveText('Cần nhập tên phiên.')
  await expect(page.getByRole('status')).toHaveText('Chưa có dữ liệu')
})

test('layout and canvas evidence are inspectable, not a visual approval', async ({ page }, info) => {
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
  const box = await page.locator('canvas').boundingBox()
  expect(box.width).toBeGreaterThan(250)
  expect(box.height).toBeGreaterThanOrEqual(150)
  await expect(page.getByTestId('scope')).toContainText('FIXTURE GIẢ')
  await page.screenshot({ path: info.outputPath('fixture.png'), fullPage: true })
  if (process.env.TW_UI_QA_FORCE_FAILURE === '1') {
    await expect(page.getByRole('status')).toHaveText('INTENTIONAL_FAILURE_PROBE', { timeout: 200 })
  }
})

test('outbound request is blocked in the isolated fixture browser', async ({ page }) => {
  const excluded = await startFixture()
  try {
    expect((await fetch(excluded.url)).status).toBe(200)
    const before = excluded.requests
    const outcome = await page.evaluate(async url => {
      try { await fetch(url); return 'unexpected-success' } catch { return 'blocked' }
    }, excluded.url)
    expect(outcome).toBe('blocked')
    expect(excluded.requests).toBe(before)
  } finally { await excluded.close() }
})
