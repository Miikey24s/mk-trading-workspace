const path = require('path');
const { createRequire } = require('module');

const webPackage = path.resolve(
  'D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester/foundation_v2/web/package.json',
);
const requireFromWeb = createRequire(webPackage);
const { chromium } = requireFromWeb('playwright');

const profile = 'C:/Users/MIIKEY/AppData/Local/WMReplay/fxreplay-capture-profile';
const url = process.argv[2] || 'https://app.fxreplay.com/en-US/auth/testing/dashboard';

function clean(value) {
  return String(value ?? '').replace(/\s+/g, ' ').trim();
}

(async () => {
  const context = await chromium.launchPersistentContext(profile, {
    headless: true,
    serviceWorkers: 'block',
    viewport: { width: 1920, height: 1080 },
    locale: 'en-US',
  });
  const page = context.pages()[0] || await context.newPage();
  page.on('console', msg => console.log(`[console:${msg.type()}] ${clean(msg.text())}`));
  page.on('pageerror', error => console.log(`[pageerror] ${clean(error.message)}`));
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(7000);
  console.log(JSON.stringify({ url: page.url(), title: await page.title() }, null, 2));
  console.log('--- BODY ---');
  console.log((await page.locator('body').innerText().catch(() => '')).slice(0, 24000));
  console.log('--- BUTTONS ---');
  for (const [index, el] of (await page.locator('button, [role="button"]').all()).entries()) {
    const item = await el.evaluate((node, index) => ({
      index,
      tag: node.tagName,
      text: (node.innerText || '').replace(/\s+/g, ' ').trim(),
      aria: node.getAttribute('aria-label'),
      title: node.getAttribute('title'),
      disabled: node.hasAttribute('disabled') || node.getAttribute('aria-disabled') === 'true',
      testid: node.getAttribute('data-testid'),
      href: node.getAttribute('href'),
    }), index);
    if (item.text || item.aria || item.title) console.log(JSON.stringify(item));
  }
  console.log('--- LINKS ---');
  for (const [index, el] of (await page.locator('a').all()).entries()) {
    const item = await el.evaluate((node, index) => ({
      index,
      text: (node.innerText || '').replace(/\s+/g, ' ').trim(),
      href: node.getAttribute('href'),
      aria: node.getAttribute('aria-label'),
      title: node.getAttribute('title'),
    }), index);
    if (item.text || item.aria || item.title) console.log(JSON.stringify(item));
  }
  console.log('--- INPUTS ---');
  for (const [index, el] of (await page.locator('input, select, textarea').all()).entries()) {
    const item = await el.evaluate((node, index) => ({
      index,
      tag: node.tagName,
      type: node.getAttribute('type'),
      name: node.getAttribute('name'),
      value: node.getAttribute('value'),
      placeholder: node.getAttribute('placeholder'),
      aria: node.getAttribute('aria-label'),
      disabled: node.hasAttribute('disabled'),
    }), index);
    console.log(JSON.stringify(item));
  }
  console.log('--- DIALOGS ---');
  for (const [index, el] of (await page.locator('[role="dialog"], dialog').all()).entries()) {
    console.log(JSON.stringify({ index, text: clean(await el.innerText().catch(() => '')) }));
  }
  await context.close();
})();
