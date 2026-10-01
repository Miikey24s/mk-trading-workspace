const path = require('path');
const fs = require('fs');
const { createRequire } = require('module');
const requireFromWeb = createRequire(path.resolve('D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester/foundation_v2/web/package.json'));
const { chromium } = requireFromWeb('playwright');

const profile = 'C:/Users/MIIKEY/AppData/Local/WMReplay/fxreplay-capture-profile';
const outDir = process.argv[2] || 'D:/ANNAM/FXReplayCaptures/free-session-2026-09-30';
fs.mkdirSync(outDir, { recursive: true });
const clean = value => String(value ?? '').replace(/\s+/g, ' ').trim();
const safeFile = value => String(value).replace(/[^a-z0-9._-]+/gi, '_').slice(0, 180);

async function save(page, label) {
  await page.screenshot({ path: path.join(outDir, `${label}.png`), fullPage: true });
  fs.writeFileSync(path.join(outDir, `${label}.html`), await page.locator('html').evaluate(node => node.outerHTML));
  fs.writeFileSync(path.join(outDir, `${label}.text.txt`), await page.locator('body').innerText().catch(() => ''));
}

async function visibleSummary(page) {
  const body = await page.locator('body').innerText().catch(() => '');
  console.log(JSON.stringify({ url: page.url(), title: await page.title(), body: body.slice(0, 20000) }, null, 2));
  const items = await page.locator('[role="option"], [role="listbox"] *, p, li').evaluateAll(nodes => nodes.map(node => ({
    role: node.getAttribute('role'), text: (node.innerText || '').replace(/\s+/g, ' ').trim(),
  })).filter(x => x.text).slice(-120));
  console.log('--- visible list/option text ---');
  for (const item of items) console.log(JSON.stringify(item));
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
    if (url.includes('fxreplay.com') && /api|session|backtest/i.test(url)) requests.push({ method: req.method(), url, postData: req.postData() });
  });
  page.on('response', async res => {
    const url = res.url();
    if (url.includes('fxreplay.com') && /api|session|backtest/i.test(url)) responses.push({ status: res.status(), url });
  });
  await page.goto('https://app.fxreplay.com/en-US/auth/testing/dashboard', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(7000);
  await page.getByRole('button', { name: /Backtesting session/i }).first().click();
  await page.waitForTimeout(1000);
  await page.getByPlaceholder('Name your session').fill('WMReplay scan 2026-09-30');
  await page.getByPlaceholder('Type the initial balance').fill('10000');
  const assetInput = page.getByRole('combobox', { name: 'Type to search for assets' });
  await assetInput.fill('EURUSD');
  await page.waitForTimeout(1200);
  await save(page, 'asset-search');
  await visibleSummary(page);
  console.log('--- network before asset selection ---');
  console.log(JSON.stringify({ requests, responses }, null, 2));
  await context.close();
})();
