const path = require('path');
const fs = require('fs');
const { createRequire } = require('module');
const requireFromWeb = createRequire(path.resolve('D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester/foundation_v2/web/package.json'));
const { chromium } = requireFromWeb('playwright');

const profile = 'C:/Users/MIIKEY/AppData/Local/WMReplay/fxreplay-capture-profile';
const sessionId = process.argv[2] || 'aad96b3f-3510-4e1a-bd33-290140058547';
const outDir = process.argv[3] || 'D:/ANNAM/FXReplayCaptures/deep-free-backtest-2026-09-30';
const url = `https://app.fxreplay.com/en-US/auth/testing/v2/sessions/${sessionId}`;
fs.mkdirSync(outDir, { recursive: true });
const clean = value => String(value ?? '').replace(/\s+/g, ' ').trim();
const safeUrl = value => { try { const u = new URL(value); for (const k of [...u.searchParams.keys()]) if (/token|auth|session|user|uid|sid|key|email/i.test(k)) u.searchParams.set(k, '[REDACTED]'); return u.toString(); } catch { return '[INVALID_URL]'; } };

async function save(page, label) {
  await page.screenshot({ path: path.join(outDir, `${label}.png`), fullPage: true, animations: 'disabled' }).catch(() => {});
  fs.writeFileSync(path.join(outDir, `${label}.text.txt`), await page.locator('body').innerText().catch(() => ''));
  fs.writeFileSync(path.join(outDir, `${label}.html`), await page.locator('html').evaluate(node => node.outerHTML).catch(() => ''));
}

(async () => {
  const context = await chromium.launchPersistentContext(profile, { headless: true, serviceWorkers: 'block', viewport: { width: 1920, height: 1080 }, locale: 'en-US' });
  const page = context.pages()[0] || await context.newPage();
  const requests = [];
  const responses = [];
  page.on('request', req => { if (req.url().startsWith('https://app.fxreplay.com') && /order|position|execution|trade/i.test(req.url())) requests.push({ method: req.method(), url: safeUrl(req.url()) }); });
  page.on('response', res => { if (res.url().startsWith('https://app.fxreplay.com') && /order|position|execution|trade/i.test(res.url())) responses.push({ status: res.status(), url: safeUrl(res.url()) }); });
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(9000);
  await page.locator('appcues-experience-container').evaluateAll(nodes => nodes.forEach(node => { node.style.pointerEvents = 'none'; })).catch(() => {});
  // Open the order ticket if it was not restored from the previous scan.
  const orderButton = page.getByRole('button', { name: /^Order$/i });
  if (!(await page.getByLabel('Quantity').count())) {
    await orderButton.first().click({ force: true });
    await page.waitForTimeout(700);
  }
  await save(page, 'order-before-smoke');
  const quantity = page.getByLabel('Quantity');
  if (!(await quantity.count())) throw new Error('Order quantity input not found');
  await quantity.fill('1000');
  const buy = page.getByRole('button', { name: /^Buy$/i }).last();
  await buy.click({ force: true });
  await page.waitForTimeout(400);
  const place = page.getByRole('button', { name: /^Place order$/i }).last();
  if (!(await place.count())) throw new Error('Place order button not found');
  await save(page, 'order-ready');
  await place.click({ force: true });
  await page.waitForTimeout(5000);
  await save(page, 'order-after-place');
  const postPlaceText = await page.locator('body').innerText().catch(() => '');

  // Try to close the single simulated position through the UI. This is a
  // backtest-only position; no broker or live endpoint is used.
  let closeAttempt = 'not attempted';
  const closeButton = page.getByTitle('Close positions');
  if (await closeButton.count()) {
    await closeButton.first().click({ force: true });
    await page.waitForTimeout(800);
    await save(page, 'close-position-dialog');
    const closeText = await page.locator('body').innerText().catch(() => '');
    const candidates = page.getByRole('button', { name: /Close (position|all|trade)|Confirm|Market/i });
    if (await candidates.count()) {
      // Prefer an explicit close-all/confirm action; otherwise leave the
      // position open rather than guessing a destructive control.
      const names = await candidates.allInnerTexts().catch(() => []);
      const target = candidates.filter({ hasText: /Close all|Close position|Confirm/i }).last();
      if (await target.count()) {
        await target.click({ force: true });
        await page.waitForTimeout(4000);
        closeAttempt = `clicked ${names.join(' | ')}`;
      } else closeAttempt = `dialog opened; no explicit close action (${names.join(' | ')})`;
    } else closeAttempt = 'dialog opened; no close control found';
    await save(page, 'order-final');
  }
  const result = { sessionId, url, quantity: '1000', side: 'Buy', postPlaceText: postPlaceText.slice(0, 12000), closeAttempt, requests, responses };
  fs.writeFileSync(path.join(outDir, 'order-smoke-result.json'), JSON.stringify(result, null, 2));
  console.log(JSON.stringify({ sessionId, quantity: '1000', side: 'Buy', closeAttempt, requestCount: requests.length, responseCount: responses.length, tail: postPlaceText.slice(-2500) }, null, 2));
  await context.close();
})();
