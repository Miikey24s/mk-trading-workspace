const fs = require('fs');
const path = require('path');
const { createRequire } = require('module');
const requireFromWeb = createRequire(path.resolve('D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester/foundation_v2/web/package.json'));
const { chromium } = requireFromWeb('playwright');

const profile = 'C:/Users/MIIKEY/AppData/Local/WMReplay/fxreplay-capture-profile';
const sessionId = process.argv[2] || 'aad96b3f-3510-4e1a-bd33-290140058547';
const outDir = process.argv[3] || 'D:/ANNAM/FXReplayCaptures/deep-free-backtest-2026-09-30/chart-menu-verified-2026-09-30';
const url = `https://app.fxreplay.com/en-US/auth/testing/v2/sessions/${sessionId}`;
fs.mkdirSync(outDir, { recursive: true });

const compact = value => String(value ?? '').replace(/\s+/g, ' ').trim();
const safeName = value => value.replace(/[^a-z0-9._-]+/gi, '_').slice(0, 120);
const visible = async locator => {
  const n = await locator.count();
  for (let i = 0; i < n; i++) if (await locator.nth(i).isVisible().catch(() => false)) return locator.nth(i);
  return null;
};

async function visibleNodes(page, selector) {
  return page.locator(selector).evaluateAll(nodes => nodes.map((node, index) => {
    const rect = node.getBoundingClientRect();
    const style = getComputedStyle(node);
    return {
      index,
      tag: node.tagName,
      role: node.getAttribute('role'),
      aria: node.getAttribute('aria-label'),
      expanded: node.getAttribute('aria-expanded'),
      title: node.getAttribute('title'),
      text: (node.innerText || node.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 500),
      className: typeof node.className === 'string' ? node.className.slice(0, 240) : '',
      visible: rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden',
      rect: { x: Math.round(rect.x), y: Math.round(rect.y), width: Math.round(rect.width), height: Math.round(rect.height) },
    };
  }).filter(item => item.visible));
}

async function snapshot(page, label, beforeText, beforeControls, metadata) {
  const safe = safeName(label);
  const text = await page.locator('body').innerText().catch(() => '');
  const controls = await visibleNodes(page, 'button,[role="button"],[role="menuitem"],[role="option"],[role="dialog"],[role="menu"],[role="listbox"],[role="tab"],input');
  const overlayCandidates = await visibleNodes(page, '[role="dialog"],[role="menu"],[role="listbox"],[data-popper-placement],[class*="dropdown"],[class*="popover"],[class*="menu"]');
  await page.screenshot({ path: path.join(outDir, `${safe}.png`), fullPage: false, animations: 'disabled' }).catch(() => {});
  fs.writeFileSync(path.join(outDir, `${safe}.text.txt`), text);
  fs.writeFileSync(path.join(outDir, `${safe}.html`), await page.locator('html').evaluate(node => node.outerHTML).catch(() => ''));
  fs.writeFileSync(path.join(outDir, `${safe}.state.json`), JSON.stringify({ label, url: page.url(), metadata, bodyChanged: compact(text) !== compact(beforeText), bodyText: text, controls, overlayCandidates }, null, 2));
  const changedControls = controls.filter(current => {
    const previous = beforeControls.find(item => item.tag === current.tag && item.title === current.title && item.aria === current.aria && item.text === current.text);
    return !previous;
  });
  return {
    label,
    selector: metadata.selector,
    clicked: metadata.clicked,
    bodyChanged: compact(text) !== compact(beforeText),
    beforeLength: beforeText.length,
    afterLength: text.length,
    overlayCandidates: overlayCandidates.filter(item => item.text || item.role),
    newVisibleControls: changedControls.slice(0, 80),
    ariaExpanded: controls.filter(item => item.expanded !== null),
  };
}

async function closeMenus(page) {
  await page.keyboard.press('Escape').catch(() => {});
  await page.waitForTimeout(300);
}

(async () => {
  const context = await chromium.launchPersistentContext(profile, {
    headless: true,
    viewport: { width: 1920, height: 1080 },
    locale: 'en-US',
  });
  const page = context.pages()[0] || await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(compact(error.message).slice(0, 500)));
  page.on('console', message => { if (['error', 'warning'].includes(message.type())) errors.push(`${message.type()}: ${compact(message.text()).slice(0, 500)}`); });
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(10000);
  await page.locator('appcues-experience-container').evaluateAll(nodes => nodes.forEach(node => { node.style.pointerEvents = 'none'; })).catch(() => {});
  // Start from a wide, uncluttered chart so top-toolbar menus are actually
  // rendered as interactive controls instead of being collapsed behind panels.
  const orderFlowCollapse = page.locator('button[aria-label="Collapse the order flow panel"]');
  if (await orderFlowCollapse.count() && await orderFlowCollapse.first().isVisible().catch(() => false)) await orderFlowCollapse.first().click({ force: true }).catch(() => {});
  const closePanels = page.locator('[aria-label^="Close "]');
  for (let i = 0, n = await closePanels.count(); i < n; i++) if (await closePanels.nth(i).isVisible().catch(() => false)) await closePanels.nth(i).click({ force: true }).catch(() => {});
  await page.waitForTimeout(800);

  const cases = [
    ['interval', 'button[title="Interval"]'],
    ['chart-type', 'button[title^="Chart type:"]'],
    ['indicators', 'button[title="Indicators"]'],
    ['order-flow', 'button[title^="Order Flow"]'],
    ['analytics', 'button[title="Analytics"]'],
    ['compare-symbol', 'button[title="Compare symbol"]'],
    ['symbol-menu', 'button[title="Symbol menu"]'],
    ['layout-options', 'button[title="Layout options"]'],
    ['chart-settings', 'button[aria-label="Settings"]'],
    ['keyboard-shortcuts', 'button[title="Keyboard shortcuts"]'],
    ['go-to-date', 'button[title="Go to"]'],
    ['timezone', 'button[title="Time zone"]'],
    ['positions-orders', 'button[title="Show positions and orders"]'],
    ['draw-cursors', 'button[aria-label="Expand Cursors tools"]'],
    ['draw-trend', 'button[aria-label^="Expand Trend line tools"]'],
    ['draw-fibonacci', 'button[aria-label^="Expand Fibonacci"]'],
    ['draw-patterns', 'button[aria-label^="Expand Patterns"]'],
    ['draw-projections', 'button[aria-label^="Expand Projections"]'],
    ['draw-shapes', 'button[aria-label^="Expand Geometric"]'],
    ['draw-text', 'button[aria-label^="Expand Text & Notes"]'],
    ['draw-emojis', 'button[aria-label^="Expand Emojis"]'],
  ];

  const results = [];
  const baselineText = await page.locator('body').innerText();
  const baselineControls = await visibleNodes(page, 'button,[role="button"],[role="menuitem"],[role="option"],[role="dialog"],[role="menu"],[role="listbox"],[role="tab"],input');
  fs.writeFileSync(path.join(outDir, 'baseline.state.json'), JSON.stringify({ url: page.url(), bodyText: baselineText, controls: baselineControls }, null, 2));
  await page.screenshot({ path: path.join(outDir, 'baseline.png'), fullPage: false, animations: 'disabled' }).catch(() => {});

  for (const [label, selector] of cases) {
    await closeMenus(page);
    const beforeText = await page.locator('body').innerText();
    const beforeControls = await visibleNodes(page, 'button,[role="button"],[role="menuitem"],[role="option"],[role="dialog"],[role="menu"],[role="listbox"],[role="tab"],input');
    const target = await visible(page.locator(selector));
    let clicked = false;
    let clickError = null;
    if (target) {
      try {
        // The headless Chromium runtime displays a non-DOM graphics warning
        // over the first toolbar row. Dispatching the DOM click keeps the
        // interaction on the real Angular control while bypassing that visual
        // overlay; it does not submit or mutate an order.
        await target.dispatchEvent('click');
        clicked = true;
      } catch (error) { clickError = compact(error.message); }
    }
    await page.waitForTimeout(900);
    const result = await snapshot(page, label, beforeText, beforeControls, { selector, clicked, clickError });
    results.push(result);
  }

  await closeMenus(page);
  const summary = {
    generatedAt: new Date().toISOString(),
    sessionId,
    url,
    results,
    errors,
    note: 'Only read-only chart controls were clicked. Order, save, delete, upgrade and prop-firm creation were intentionally skipped.',
  };
  fs.writeFileSync(path.join(outDir, 'focused-menu-summary.json'), JSON.stringify(summary, null, 2));
  console.log(JSON.stringify({ outDir, cases: cases.length, clicked: results.filter(item => item.clicked).length, changed: results.filter(item => item.bodyChanged).length, errors: errors.slice(0, 12) }, null, 2));
  await context.close();
})();
