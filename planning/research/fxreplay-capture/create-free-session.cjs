const path = require('path');
const fs = require('fs');
const { createRequire } = require('module');
const requireFromWeb = createRequire(path.resolve('D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester/foundation_v2/web/package.json'));
const { chromium } = requireFromWeb('playwright');

const profile = 'C:/Users/MIIKEY/AppData/Local/WMReplay/fxreplay-capture-profile';
const outDir = process.argv[2] || 'D:/ANNAM/FXReplayCaptures/free-session-creation-2026-09-30';
const clean = value => String(value ?? '').replace(/\s+/g, ' ').trim();

async function snapshot(page, label) {
  fs.mkdirSync(outDir, { recursive: true });
  await page.screenshot({ path: path.join(outDir, `${label}.png`), fullPage: true });
  fs.writeFileSync(path.join(outDir, `${label}.html`), await page.locator('html').evaluate(node => node.outerHTML));
  console.log(`--- ${label} ---`);
  console.log(JSON.stringify({ url: page.url(), title: await page.title() }, null, 2));
  console.log((await page.locator('body').innerText().catch(() => '')).slice(0, 26000));
  console.log('--- buttons ---');
  for (const [index, el] of (await page.locator('button,[role="button"]').all()).entries()) {
    const item = await el.evaluate((node, index) => ({
      index,
      tag: node.tagName,
      text: (node.innerText || '').replace(/\s+/g, ' ').trim(),
      aria: node.getAttribute('aria-label'),
      title: node.getAttribute('title'),
      disabled: node.hasAttribute('disabled') || node.getAttribute('aria-disabled') === 'true',
      href: node.getAttribute('href'),
      testid: node.getAttribute('data-testid'),
    }), index);
    if (item.text || item.aria || item.title) console.log(JSON.stringify(item));
  }
  console.log('--- inputs ---');
  for (const [index, el] of (await page.locator('input,select,textarea').all()).entries()) {
    console.log(JSON.stringify(await el.evaluate((node, index) => ({
      index, tag: node.tagName, type: node.getAttribute('type'), name: node.getAttribute('name'),
      value: node.getAttribute('value'), placeholder: node.getAttribute('placeholder'),
      aria: node.getAttribute('aria-label'), disabled: node.hasAttribute('disabled'),
    }), index)));
  }
}

(async () => {
  const context = await chromium.launchPersistentContext(profile, {
    headless: true, serviceWorkers: 'block', viewport: { width: 1920, height: 1080 }, locale: 'en-US',
  });
  const page = context.pages()[0] || await context.newPage();
  page.on('console', msg => { if (['error','warning'].includes(msg.type())) console.log(`[console:${msg.type()}] ${clean(msg.text())}`); });
  page.on('pageerror', error => console.log(`[pageerror] ${clean(error.message)}`));
  await page.goto('https://app.fxreplay.com/en-US/auth/testing/dashboard', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(7000);
  await snapshot(page, 'before');
  const start = page.getByRole('button', { name: /Backtesting session/i });
  if (!(await start.count())) throw new Error('Backtesting session button was not found');
  await start.first().click();
  await page.waitForTimeout(1500);
  await snapshot(page, 'after-click');
  await context.close();
})();
