const path = require('path');
const fs = require('fs');
const { createRequire } = require('module');
const requireFromWeb = createRequire(path.resolve('D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester/foundation_v2/web/package.json'));
const { chromium } = requireFromWeb('playwright');

const profile = 'C:/Users/MIIKEY/AppData/Local/WMReplay/fxreplay-capture-profile';
const outDir = process.argv[2] || 'D:/ANNAM/FXReplayCaptures/free-session-2026-09-30';
fs.mkdirSync(outDir, { recursive: true });
const clean = value => String(value ?? '').replace(/\s+/g, ' ').trim();
const sanitizeUrl = value => {
  try {
    const u = new URL(value);
    for (const key of [...u.searchParams.keys()]) {
      if (/token|auth|session|user|uid|cid|sid|signature|key|id/i.test(key)) u.searchParams.set(key, '[REDACTED]');
    }
    return u.toString();
  } catch { return '[INVALID_URL]'; }
};

async function save(page, label) {
  await page.screenshot({ path: path.join(outDir, `${label}.png`), fullPage: true });
  fs.writeFileSync(path.join(outDir, `${label}.html`), await page.locator('html').evaluate(node => node.outerHTML));
  fs.writeFileSync(path.join(outDir, `${label}.text.txt`), await page.locator('body').innerText().catch(() => ''));
}

(async () => {
  const context = await chromium.launchPersistentContext(profile, {
    headless: true, serviceWorkers: 'block', viewport: { width: 1920, height: 1080 }, locale: 'en-US',
  });
  const page = context.pages()[0] || await context.newPage();
  const requests = [];
  const responses = [];
  page.on('request', req => {
    const url = req.url();
    if (url.includes('fxreplay.com') && /session|backtest|symbol/i.test(url)) requests.push({ method: req.method(), url: sanitizeUrl(url) });
  });
  page.on('response', res => {
    const url = res.url();
    if (url.includes('fxreplay.com') && /session|backtest|symbol/i.test(url)) responses.push({ status: res.status(), url: sanitizeUrl(url) });
  });
  await page.goto('https://app.fxreplay.com/en-US/auth/testing/dashboard', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(7000);
  await page.getByRole('button', { name: /Backtesting session/i }).first().click();
  await page.waitForTimeout(800);
  await page.getByPlaceholder('Name your session').fill('WMReplay scan 2026-09-30');
  await page.getByPlaceholder('Type the initial balance').fill('10000');
  const asset = page.getByRole('combobox', { name: 'Type to search for assets' });
  await asset.fill('EURUSD');
  await page.waitForTimeout(800);
  const options = page.locator('[role="option"]').filter({ hasText: /OANDA/i });
  const optionTexts = await options.allInnerTexts().catch(() => []);
  console.log('asset-options', JSON.stringify(optionTexts));
  const oanda = options.filter({ hasText: /Eurusd|EURUSD/i }).first();
  if (!(await oanda.count())) throw new Error('OANDA EURUSD option was not found');
  await oanda.click();
  await page.waitForTimeout(800);
  const dates = page.locator('input.p-datepicker-input');
  if (await dates.count() >= 2) {
    await dates.nth(0).click();
    await page.waitForTimeout(500);
    console.log('date-dialogs', JSON.stringify(await page.locator('[role="dialog"], .p-datepicker').allInnerTexts().catch(() => [])));
    console.log('date-buttons', JSON.stringify(await page.locator('.p-datepicker button,[role="dialog"] button').evaluateAll(nodes => nodes.map(n => ({text:(n.innerText||'').trim(),aria:n.getAttribute('aria-label'),title:n.getAttribute('title')})).filter(x=>x.text||x.aria||x.title))));
    console.log('date-cells', JSON.stringify(await page.locator('.p-datepicker-panel td').evaluateAll(nodes => nodes.map(n => ({text:(n.innerText||'').replace(/\\s+/g,' ').trim(),class:n.className,aria:n.getAttribute('aria-label'),title:n.getAttribute('title')})).filter(x=>x.text))));
    console.log('datepicker-html', (await page.locator('.p-datepicker-panel').first().evaluate(node => node.outerHTML)).slice(0, 12000));
    const startCell = page.locator('.p-datepicker-panel td').filter({ hasText: /^1$/ }).filter({ hasNot: page.locator('.p-datepicker-other-month') }).first();
    if (!(await startCell.count())) throw new Error('datepicker start day cell not found');
    await startCell.click();
    await page.waitForTimeout(300);
    await dates.nth(1).click();
    await page.waitForTimeout(300);
    const endCell = page.locator('.p-datepicker-panel').last().locator('.p-datepicker-day:not(.p-disabled)').filter({ hasText: /^30$/ }).last();
    if (!(await endCell.count())) throw new Error('datepicker end day cell not found');
    await endCell.click();
    await page.waitForTimeout(800);
  }
  const create = page.getByRole('button', { name: /^Create session$/i });
  if (!(await create.count())) throw new Error('Create session button was not found');
  if (await create.isDisabled()) {
    console.log('create-disabled-debug', JSON.stringify({
      body: (await page.locator('body').innerText().catch(() => '')).slice(-10000),
      inputs: await page.locator('input').evaluateAll(nodes => nodes.map(node => ({
        placeholder: node.getAttribute('placeholder'), value: node.value, aria: node.getAttribute('aria-label'),
        invalid: node.getAttribute('aria-invalid'), classes: node.className, min: node.getAttribute('min'), max: node.getAttribute('max'),
        outer: node.classList.contains('p-datepicker-input') ? node.outerHTML : undefined,
      }))),
      tags: await page.locator('p-autocomplete').evaluateAll(nodes => nodes.map(node => ({
        text: node.innerText, value: node.getAttribute('ng-reflect-model'), classes: node.className, outer: node.outerHTML.slice(0, 3000),
      }))),
    }, null, 2));
    await save(page, 'disabled-debug');
    throw new Error('Create session remains disabled after selecting OANDA EURUSD');
  }
  await save(page, 'ready-to-create');
  await create.click();
  await page.waitForTimeout(10000);
  await save(page, 'after-create');
  const result = {
    url: page.url(),
    title: await page.title(),
    bodyText: (await page.locator('body').innerText().catch(() => '')).slice(0, 30000),
    requests,
    responses,
  };
  fs.writeFileSync(path.join(outDir, 'creation-result.json'), JSON.stringify(result, null, 2));
  console.log(JSON.stringify({ url: result.url, title: result.title, bodyText: result.bodyText.slice(0, 8000), requestCount: requests.length, responseCount: responses.length }, null, 2));
  await context.close();
})();
