const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { createRequire } = require('module');
const requireFromWeb = createRequire(path.resolve('D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester/foundation_v2/web/package.json'));
const { chromium } = requireFromWeb('playwright');

const profile = 'C:/Users/MIIKEY/AppData/Local/WMReplay/fxreplay-capture-profile';
const sessionId = process.argv[2] || 'aad96b3f-3510-4e1a-bd33-290140058547';
const outDir = process.argv[3] || 'D:/ANNAM/FXReplayCaptures/deep-free-backtest-2026-09-30';
const origin = 'https://app.fxreplay.com';
const chartUrl = `${origin}/en-US/auth/testing/v2/sessions/${sessionId}`;
fs.mkdirSync(outDir, { recursive: true });

const clean = value => String(value ?? '').replace(/\s+/g, ' ').trim();
function safeUrl(value) {
  try {
    const u = new URL(value);
    for (const key of [...u.searchParams.keys()]) {
      if (/token|auth|session|user|uid|cid|sid|signature|key|email/i.test(key)) u.searchParams.set(key, '[REDACTED]');
    }
    return u.toString();
  } catch { return '[INVALID_URL]'; }
}
function safeName(value) { return value.replace(/[^a-z0-9._-]+/gi, '_').slice(0, 160); }
function hash(value) { return crypto.createHash('sha256').update(value).digest('hex'); }

async function saveState(page, label, network) {
  const safe = safeName(label);
  await page.screenshot({ path: path.join(outDir, `${safe}.png`), fullPage: true, animations: 'disabled' }).catch(() => {});
  await page.screenshot({ path: path.join(outDir, `${safe}.viewport.png`), fullPage: false, animations: 'disabled' }).catch(() => {});
  const html = await page.locator('html').evaluate(node => node.outerHTML).catch(() => '');
  const text = await page.locator('body').innerText().catch(() => '');
  fs.writeFileSync(path.join(outDir, `${safe}.html`), html);
  fs.writeFileSync(path.join(outDir, `${safe}.text.txt`), text);
  let aria = '';
  try { aria = await page.locator('body').ariaSnapshot(); } catch { aria = 'ariaSnapshot unavailable'; }
  fs.writeFileSync(path.join(outDir, `${safe}.aria.yml`), aria);
  const geometry = await page.locator('button, [role="button"], input, [role="dialog"], canvas, svg, a').evaluateAll(nodes => nodes.map((node, index) => {
    const rect = node.getBoundingClientRect();
    return {
      index, tag: node.tagName, text: (node.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 180),
      aria: node.getAttribute('aria-label'), title: node.getAttribute('title'), role: node.getAttribute('role'),
      href: node.getAttribute('href'),
      rect: { x: Math.round(rect.x), y: Math.round(rect.y), width: Math.round(rect.width), height: Math.round(rect.height) },
    };
  }));
  fs.writeFileSync(path.join(outDir, `${safe}.geometry.json`), JSON.stringify({ url: page.url(), geometry }, null, 2));
  const screenshotBytes = fs.readFileSync(path.join(outDir, `${safe}.viewport.png`));
  network.screenshots.push({ label, file: `${safe}.viewport.png`, sha256: hash(screenshotBytes) });
  console.log(`[saved] ${label} url=${page.url()} text=${text.length}`);
}

async function closeOverlays(page) {
  await page.keyboard.press('Escape').catch(() => {});
  await page.waitForTimeout(250);
}

async function clickState(page, label, locator, network) {
  try {
    if (!(await locator.count())) { network.skipped.push({ label, reason: 'not found' }); return; }
    // Appcues occasionally leaves a transparent tour layer over the chart. It is
    // external UI chrome; disabling its pointer interception keeps the scan
    // read-only while allowing the real control to be inspected.
    await page.locator('appcues-experience-container').evaluateAll(nodes => nodes.forEach(node => { node.style.pointerEvents = 'none'; })).catch(() => {});
    await locator.first().click({ timeout: 8000, force: true });
    await page.waitForTimeout(600);
    await saveState(page, label, network);
    await closeOverlays(page);
  } catch (error) {
    network.errors.push({ label, error: clean(error.message) });
  }
}

async function routeState(page, route, network) {
  try {
    await page.goto(`${origin}${route}`, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(7000);
    await saveState(page, route.replaceAll('/', '_').replace(/^_/, ''), network);
  } catch (error) {
    network.errors.push({ label: route, error: clean(error.message) });
  }
}

(async () => {
  const network = { requests: [], responses: [], sockets: [], screenshots: [], skipped: [], errors: [] };
  const context = await chromium.launchPersistentContext(profile, {
    headless: true, serviceWorkers: 'block', viewport: { width: 1920, height: 1080 }, locale: 'en-US',
  });
  const page = context.pages()[0] || await context.newPage();
  page.on('request', request => {
    if (request.url().startsWith(origin)) network.requests.push({ method: request.method(), url: safeUrl(request.url()), resourceType: request.resourceType() });
  });
  page.on('response', response => {
    if (response.url().startsWith(origin)) network.responses.push({ status: response.status(), url: safeUrl(response.url()), resourceType: response.request().resourceType(), contentType: response.headers()['content-type'] || '' });
  });
  page.on('websocket', socket => {
    network.sockets.push({ url: safeUrl(socket.url()) });
  });
  page.on('console', message => {
    if (['error', 'warning'].includes(message.type())) network.errors.push({ label: `console:${message.type()}`, error: clean(message.text()).slice(0, 500) });
  });
  page.on('pageerror', error => network.errors.push({ label: 'pageerror', error: clean(error.message).slice(0, 500) }));

  await page.goto(chartUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(9000);
  await saveState(page, 'chart-baseline', network);

  const byTitle = title => page.getByTitle(title);
  const byAria = label => page.getByRole('button', { name: label });
  const byText = label => page.getByRole('button', { name: new RegExp(`^${label}$`, 'i') });

  // Read-only chart controls. Do not draw, delete, save, or submit.
  await clickState(page, 'chart-interval-menu', byTitle('Interval'), network);
  await clickState(page, 'chart-type-menu', page.locator('button[title^="Chart type:"]'), network);
  await clickState(page, 'indicators-panel', byTitle('Indicators'), network);
  await clickState(page, 'order-flow-panel', byTitle(/Order Flow/), network);
  await clickState(page, 'analytics-panel', byTitle('Analytics'), network);
  await clickState(page, 'compare-symbol-panel', byTitle('Compare symbol'), network);
  await clickState(page, 'symbol-menu', byTitle('Symbol menu'), network);
  await clickState(page, 'layout-options', byTitle('Layout options'), network);
  await clickState(page, 'chart-settings', page.locator('button[aria-label="Settings"]'), network);
  await clickState(page, 'keyboard-shortcuts', byTitle('Keyboard shortcuts'), network);
  await clickState(page, 'go-to-date', byTitle('Go to'), network);
  await clickState(page, 'time-zone-menu', byTitle('Time zone'), network);
  await clickState(page, 'positions-orders', byTitle('Show positions and orders'), network);
  await clickState(page, 'order-ticket', page.getByRole('button', { name: /^Order$/i }), network);
  await clickState(page, 'object-tree', byText('Object tree'), network);
  await clickState(page, 'watchlist', byText('Watchlist'), network);
  await clickState(page, 'journal', byText('Journal'), network);
  await clickState(page, 'news', byText('News'), network);
  await clickState(page, 'replay-next-candle', byAria('Next candle'), network);
  await clickState(page, 'replay-controls', byAria('Timeframe'), network);
  await clickState(page, 'bar-replay', byAria('Bar replay'), network);
  await clickState(page, 'bar-replay-closed', byAria('Bar replay'), network);

  // The route surfaces are read-only; do not open upgrade, prop-firm creation, delete, or payment flows.
  for (const route of [
    '/en-US/auth/testing/dashboard',
    '/en-US/auth/testing/sessions',
    '/en-US/auth/testing/trades',
    '/en-US/auth/testing/analytics-backtesting',
    '/en-US/auth/testing/analytics-prop-firm',
  ]) await routeState(page, route, network);

  // Back to the created chart and record the final stable state.
  await page.goto(chartUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(7000);
  await saveState(page, 'chart-final', network);

  network.requestCount = network.requests.length;
  network.responseCount = network.responses.length;
  network.socketCount = network.sockets.length;
  network.uniqueResponseUrls = [...new Set(network.responses.map(item => item.url))].sort();
  fs.writeFileSync(path.join(outDir, 'network-manifest.json'), JSON.stringify(network, null, 2));
  fs.writeFileSync(path.join(outDir, 'scan-summary.json'), JSON.stringify({
    sessionId, chartUrl, generatedAt: new Date().toISOString(),
    routeCount: 6, interactionCount: network.screenshots.length - 6,
    requestCount: network.requestCount, responseCount: network.responseCount, socketCount: network.socketCount,
    screenshots: network.screenshots, skipped: network.skipped, errors: network.errors,
  }, null, 2));
  console.log(JSON.stringify({ sessionId, chartUrl, screenshots: network.screenshots.length, requestCount: network.requestCount, responseCount: network.responseCount, socketCount: network.socketCount, skipped: network.skipped, errors: network.errors.slice(0, 12) }, null, 2));
  await context.close();
})();
