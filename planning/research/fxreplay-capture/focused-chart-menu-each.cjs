const fs = require('fs');
const path = require('path');
const { createRequire } = require('module');
const req = createRequire(path.resolve('D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester/foundation_v2/web/package.json'));
const { chromium } = req('playwright');
const profile = 'C:/Users/MIIKEY/AppData/Local/WMReplay/fxreplay-capture-profile';
const url = 'https://app.fxreplay.com/en-US/auth/testing/v2/sessions/aad96b3f-3510-4e1a-bd33-290140058547';
const out = 'D:/ANNAM/FXReplayCaptures/deep-free-backtest-2026-09-30/chart-menu-verified-each-2026-09-30';
fs.mkdirSync(out, { recursive: true });
const clean = value => String(value ?? '').replace(/\s+/g, ' ').trim();
const cases = [
  ['interval', 'button[title="Interval"]'],
  ['chart-type', 'button[title^="Chart type:"]'],
  ['indicators', 'button[title="Indicators"]'],
  ['order-flow', 'button[title^="Order Flow"]'],
  ['analytics', 'button[title="Analytics"]'],
  ['compare-symbol', 'button[title="Compare symbol"]'],
  ['layout-options', 'button[title="Layout options"]'],
  ['keyboard-shortcuts', 'button[title="Keyboard shortcuts"]'],
  ['symbol-menu', 'button[title="Symbol menu"]'],
  ['go-to-date', 'button[title="Go to"]'],
  ['timezone', 'button[title="Time zone"]'],
  ['draw-cursors', 'button[aria-label="Expand Cursors tools"]'],
  ['draw-trend', 'button[aria-label^="Expand Trend line tools"]'],
  ['draw-fibonacci', 'button[aria-label^="Expand Fibonacci"]'],
  ['draw-patterns', 'button[aria-label^="Expand Patterns"]'],
  ['draw-projections', 'button[aria-label^="Expand Projections"]'],
  ['draw-shapes', 'button[aria-label^="Expand Geometric"]'],
  ['draw-text', 'button[aria-label^="Expand Text & Notes"]'],
  ['draw-emojis', 'button[aria-label^="Expand Emojis"]'],
];
async function visibleNodes(page) {
  return page.locator('button,[role="button"],[role="menuitem"],[role="option"],[role="dialog"],[role="menu"],[role="listbox"],[role="tab"],input').evaluateAll(nodes => nodes.map((node, index) => {
    const rect = node.getBoundingClientRect(); const style = getComputedStyle(node);
    return { index, tag: node.tagName, role: node.getAttribute('role'), aria: node.getAttribute('aria-label'), title: node.getAttribute('title'), text: (node.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 700), expanded: node.getAttribute('aria-expanded'), className: typeof node.className === 'string' ? node.className.slice(0, 240) : '', visible: rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden', rect: { x: Math.round(rect.x), y: Math.round(rect.y), width: Math.round(rect.width), height: Math.round(rect.height) } };
  }).filter(item => item.visible));
}
async function resetPanels(page) {
  await page.locator('appcues-experience-container').evaluateAll(nodes => nodes.forEach(node => { node.style.pointerEvents = 'none'; })).catch(() => {});
  const collapse = page.locator('button[aria-label="Collapse the order flow panel"]');
  if (await collapse.count() && await collapse.first().isVisible().catch(() => false)) await collapse.first().click({ force: true }).catch(() => {});
  const closePanels = page.locator('[aria-label^="Close "]');
  for (let i = 0, n = await closePanels.count(); i < n; i++) if (await closePanels.nth(i).isVisible().catch(() => false)) await closePanels.nth(i).click({ force: true }).catch(() => {});
  await page.waitForTimeout(500);
}
async function capture(page, label, selector, clicked, clickError) {
  const safe = label.replace(/[^a-z0-9._-]+/gi, '_');
  const body = await page.locator('body').innerText().catch(() => '');
  const controls = await visibleNodes(page);
  const overlays = controls.filter(item => ['menu', 'menuitem', 'dialog', 'listbox', 'option'].includes(item.role));
  await page.screenshot({ path: path.join(out, `${safe}.png`), fullPage: false, animations: 'disabled' }).catch(() => {});
  fs.writeFileSync(path.join(out, `${safe}.text.txt`), body);
  fs.writeFileSync(path.join(out, `${safe}.html`), await page.locator('html').evaluate(node => node.outerHTML).catch(() => ''));
  fs.writeFileSync(path.join(out, `${safe}.state.json`), JSON.stringify({ label, selector, clicked, clickError, url: page.url(), bodyText: body, controls, overlays }, null, 2));
  return { label, selector, clicked, clickError, bodyText: body, overlays, visibleControls: controls.filter(item => item.rect.y < 700 || ['menu', 'menuitem', 'dialog', 'listbox', 'option'].includes(item.role)) };
}
(async () => {
  const context = await chromium.launchPersistentContext(profile, { headless: true, viewport: { width: 1920, height: 1080 }, locale: 'en-US' });
  const page = context.pages()[0] || await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(`pageerror: ${clean(error.message).slice(0, 500)}`));
  page.on('console', message => { if (['error', 'warning'].includes(message.type())) errors.push(`${message.type()}: ${clean(message.text()).slice(0, 500)}`); });
  const results = [];
  for (const [label, selector] of cases) {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(8500);
    await resetPanels(page);
    const before = await page.locator('body').innerText().catch(() => '');
    const target = await page.locator(selector).filter({ visible: true }).first();
    let clicked = false; let clickError = null;
    if (await target.count()) {
      try { await target.dispatchEvent('click'); clicked = true; } catch (error) { clickError = clean(error.message); }
    } else clickError = 'visible target not found';
    await page.waitForTimeout(1000);
    const item = await capture(page, label, selector, clicked, clickError);
    item.beforeLength = before.length; item.bodyChanged = item.bodyText.length !== before.length;
    results.push(item);
    console.log(label, JSON.stringify({ clicked, changed: item.bodyChanged, overlays: item.overlays.map(x => `${x.role}:${x.text.slice(0, 180)}`) }));
  }
  fs.writeFileSync(path.join(out, 'focused-menu-summary.json'), JSON.stringify({ generatedAt: new Date().toISOString(), url, results: results.map(item => ({ label: item.label, selector: item.selector, clicked: item.clicked, clickError: item.clickError, bodyChanged: item.bodyChanged, beforeLength: item.beforeLength, afterLength: item.bodyText.length, overlays: item.overlays, visibleControls: item.visibleControls })), errors }, null, 2));
  console.log(JSON.stringify({ out, caseCount: cases.length, clicked: results.filter(item => item.clicked).length, changed: results.filter(item => item.bodyChanged).length, errors: errors.slice(0, 12) }, null, 2));
  await context.close();
})();
