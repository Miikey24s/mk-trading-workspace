#!/usr/bin/env node

/**
 * Read-only, route-focused capture for a logged-in FXReplay browser session.
 *
 * The script intentionally does not automate login, submit forms, create/delete
 * sessions, place orders, or save a browser profile inside the output folder.
 * It records static same-origin resources, an optionally redacted API fixture
 * set, rendered route snapshots, safe menu interactions, and a sanitized HAR.
 */

import { createHash } from 'node:crypto';
import { createRequire } from 'node:module';
import { createInterface } from 'node:readline/promises';
import { stdin as input, stdout as output } from 'node:process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import fs from 'node:fs/promises';

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));

const DEFAULT_ROUTES = [
  { id: 'home', path: '' },
  { id: 'testing-dashboard', path: 'auth/testing/dashboard' },
  { id: 'testing-v2-dashboard', path: 'auth/testing/v2/dashboard' },
  { id: 'testing-sessions', path: 'auth/testing/sessions' },
  { id: 'testing-v2-sessions', path: 'auth/testing/v2/sessions' },
  { id: 'testing-trades', path: 'auth/testing/trades' },
  { id: 'testing-analytics-backtesting', path: 'auth/testing/analytics-backtesting' },
  { id: 'testing-analytics-prop-firm', path: 'auth/testing/analytics-prop-firm' },
  { id: 'live', path: 'auth/live' },
  { id: 'live-trades', path: 'auth/live/trades' },
  { id: 'live-calendar', path: 'auth/live/calendar' },
  { id: 'strategies', path: 'auth/strategies' },
  { id: 'strategies-my-strategies', path: 'auth/strategies/my-strategies' },
  { id: 'education', path: 'auth/education' },
  { id: 'settings', path: 'auth/settings' },
  { id: 'settings-subscription', path: 'auth/settings/subscription' },
  { id: 'settings-journal-live', path: 'auth/settings/journal-live' },
];

const SENSITIVE_KEY = /(?:^|[-_])(authorization|cookie|set-cookie|password|passwd|secret|token|id[-_]?token|access[-_]?token|refresh[-_]?token|api[-_]?key|client[-_]?secret|session[-_]?cookie|csrf|xsrf|auth)(?:$|[-_])/i;
// `/en-US/auth/testing/...` is a public application route and must remain
// capturable. Restrict the auth exclusion to identity/token endpoints instead
// of treating every frontend route containing `/auth/` as a credential URL.
const SENSITIVE_URL = /(?:\/(?:identity|token|session[-_]?cookie|billing|payment|checkout)(?:\/|$)|\/auth(?:entication)?\/(?:api|v\d|token|login|logout)(?:\/|$)|firebase|hcaptcha|oauth|sso|[?&](?:token|key|code|secret|password|auth)=)/i;
const UNSAFE_CONTROL = /(?:delete|remove|logout|sign\s*out|new\s+session|create\s+session|save|submit|send|place\s+order|buy|sell|checkout|upgrade|connect\s+broker|disconnect)/i;

function printHelp() {
  console.log(`\nFXReplay read-only capture\n\nUsage:\n  node capture.mjs --base-url https://app.fxreplay.com/en-US/ --out D:\\captures\\fxreplay\n\nOptions:\n  --base-url <url>       Same-origin FXReplay entry URL (default: https://app.fxreplay.com/en-US/)\n  --out <dir>            Capture output directory (default: ./fxreplay-capture/<timestamp>)\n  --profile <dir>        Persistent browser profile outside the repo\n  --routes-file <json>   JSON array of {id,path,interactions?}; overrides default route list\n  --routes <csv>         Route paths or ids, comma separated\n  --include-api          Save GET JSON API bodies after redacting secret-like keys\n  --headless             Run headless (interactive login needs the default headed mode)\n  --no-prompt            Do not wait for manual login confirmation\n  --help                 Show this help\n\nThe script never fills credentials and skips destructive controls. Keep the output\nfolder and persistent profile outside Git; the capture may contain account data.\n`);
}

function parseArgs(argv) {
  const args = {
    baseUrl: 'https://app.fxreplay.com/en-US/',
    // Keep the default outside any repository: captures can contain rendered
    // account data even when --include-api is not enabled.
    out: path.join(process.env.LOCALAPPDATA || process.env.TEMP || process.cwd(), 'WMReplay', 'fxreplay-captures', timestamp()),
    profile: path.join(process.env.LOCALAPPDATA || process.env.TEMP || process.cwd(), 'WMReplay', 'fxreplay-capture-profile'),
    routesFile: null,
    routes: null,
    includeApi: false,
    headless: false,
    noPrompt: false,
  };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--help' || arg === '-h') {
      printHelp();
      process.exit(0);
    }
    if (arg === '--include-api') {
      args.includeApi = true;
      continue;
    }
    if (arg === '--headless') {
      args.headless = true;
      continue;
    }
    if (arg === '--no-prompt') {
      args.noPrompt = true;
      continue;
    }
    const [key, inlineValue] = arg.split('=', 2);
    const value = inlineValue ?? argv[++i];
    if (!value) throw new Error(`Missing value for ${key}`);
    if (key === '--base-url') args.baseUrl = value;
    else if (key === '--out') args.out = path.resolve(value);
    else if (key === '--profile') args.profile = path.resolve(value);
    else if (key === '--routes-file') args.routesFile = path.resolve(value);
    else if (key === '--routes') args.routes = value.split(',').map((x) => x.trim()).filter(Boolean);
    else throw new Error(`Unknown option: ${key}`);
  }
  return args;
}

function timestamp() {
  return new Date().toISOString().replace(/[:.]/g, '-');
}

function sha256(value) {
  return createHash('sha256').update(value).digest('hex');
}

function sha1(value) {
  return createHash('sha1').update(value).digest('hex');
}

function redactValue(value, key = '') {
  if (SENSITIVE_KEY.test(key)) return '[REDACTED]';
  if (Array.isArray(value)) return value.map((item) => redactValue(item));
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.entries(value).map(([childKey, childValue]) => [childKey, redactValue(childValue, childKey)]));
  }
  return value;
}

function redactUrl(rawUrl) {
  try {
    const url = new URL(rawUrl);
    for (const key of url.searchParams.keys()) {
      if (SENSITIVE_KEY.test(key) || /^(?:auth|code|key|token|secret|password)$/i.test(key)) {
        url.searchParams.set(key, '[REDACTED]');
      }
    }
    return url.toString();
  } catch {
    return rawUrl;
  }
}

function redactHeaders(headers = []) {
  return headers
    .filter((header) => !SENSITIVE_KEY.test(header.name))
    .map((header) => ({ ...header, value: SENSITIVE_KEY.test(header.name) ? '[REDACTED]' : header.value }));
}

function safeSegment(value) {
  return decodeURIComponent(value || 'index')
    .replace(/[<>:"/\\|?*\x00-\x1f]/g, '_')
    .replace(/\.+$/g, '_')
    .slice(0, 180) || 'index';
}

function routeDirectoryName(id) {
  return id.replace(/[^a-z0-9._-]+/gi, '-').replace(/^-+|-+$/g, '') || 'route';
}

function contentExtension(contentType, urlPath) {
  const pathExt = path.extname(urlPath.split('?')[0]);
  if (pathExt && pathExt.length <= 12) return pathExt;
  const mime = contentType.toLowerCase().split(';', 1)[0];
  return {
    'text/html': '.html',
    'text/css': '.css',
    'text/javascript': '.js',
    'application/javascript': '.js',
    'application/json': '.json',
    'application/manifest+json': '.json',
    'application/wasm': '.wasm',
    'image/svg+xml': '.svg',
    'image/png': '.png',
    'image/jpeg': '.jpg',
    'image/webp': '.webp',
    'font/woff2': '.woff2',
    'font/woff': '.woff',
  }[mime] || '.bin';
}

function loadPlaywright() {
  const candidates = [
    process.env.PLAYWRIGHT_PACKAGE,
    'playwright',
    path.join(process.cwd(), 'node_modules', 'playwright'),
    path.join(SCRIPT_DIR, 'node_modules', 'playwright'),
    path.resolve(SCRIPT_DIR, '../../../projects/mt5-tradingview-backtester/foundation_v2/web/node_modules/playwright'),
  ].filter(Boolean);
  const errors = [];
  for (const candidate of candidates) {
    try {
      const requireFromCwd = createRequire(path.join(process.cwd(), 'package.json'));
      return requireFromCwd(candidate);
    } catch (error) {
      errors.push(`${candidate}: ${error.message}`);
    }
  }
  throw new Error(`Playwright is not available. Install it with npm install -D playwright, or set PLAYWRIGHT_PACKAGE.\n${errors.join('\n')}`);
}

function routeFromCliValue(value, index) {
  const byId = DEFAULT_ROUTES.find((route) => route.id === value);
  if (byId) return { ...byId };
  return { id: value.replace(/[^a-z0-9]+/gi, '-').replace(/^-+|-+$/g, '') || `route-${index + 1}`, path: value };
}

async function readJson(file) {
  return JSON.parse(await fs.readFile(file, 'utf8'));
}

async function loadRoutes(args, baseUrl) {
  let routes = DEFAULT_ROUTES;
  if (args.routesFile) {
    const loaded = await readJson(args.routesFile);
    if (!Array.isArray(loaded)) throw new Error('--routes-file must contain a JSON array');
    routes = loaded;
  } else if (args.routes) {
    routes = args.routes.map(routeFromCliValue);
  }
  const origin = new URL(baseUrl).origin;
  return routes.map((route, index) => {
    if (!route || typeof route.path !== 'string') throw new Error(`Invalid route at index ${index}`);
    const url = new URL(route.path, baseUrl);
    if (url.origin !== origin) throw new Error(`Route ${route.id || index} leaves the base origin: ${url.href}`);
    return { id: route.id || `route-${index + 1}`, path: route.path, url: url.href, interactions: route.interactions || [] };
  });
}

function isSameOrigin(url, origin) {
  try { return new URL(url).origin === origin; } catch { return false; }
}

function shouldCaptureApi(response, includeApi) {
  if (!includeApi || response.request().method() !== 'GET') return false;
  const url = response.url();
  if (SENSITIVE_URL.test(url)) return false;
  const type = response.request().resourceType();
  return type === 'xhr' || type === 'fetch';
}

function isStaticResource(response) {
  const type = response.request().resourceType();
  if (['document', 'script', 'stylesheet', 'image', 'font', 'manifest', 'worker', 'wasm', 'texttrack'].includes(type)) return true;
  // Sourcemaps, fonts and worker files are sometimes requested as fetch/XHR;
  // classify them by extension so route capture does not silently omit them.
  try {
    const pathname = new URL(response.url()).pathname;
    if (/\/(?:api|session\/api|auth-identity\/api|trading\/api)(?:\/|$)/i.test(pathname)) return false;
    return /\.(?:css|js|map|mjs|svg|png|jpe?g|webp|gif|ico|woff2?|ttf|otf|wasm|json)$/i.test(pathname);
  } catch {
    return false;
  }
}

function normalizeUrlKey(rawUrl) {
  try {
    const url = new URL(rawUrl);
    return `${url.origin}${url.pathname}${url.search}`;
  } catch {
    return rawUrl;
  }
}

async function captureResponse(response, state) {
  const url = response.url();
  if (!isSameOrigin(url, state.origin)) return;
  const request = response.request();
  const staticResource = isStaticResource(response);
  const apiResource = shouldCaptureApi(response, state.includeApi);
  if (!staticResource && !apiResource) {
    state.network.push({ url: redactUrl(url), method: request.method(), resourceType: request.resourceType(), status: response.status(), captured: false, reason: 'non-static-or-api' });
    return;
  }
  if (SENSITIVE_URL.test(url)) {
    state.network.push({ url: '[SENSITIVE_URL_REDACTED]', method: request.method(), resourceType: request.resourceType(), status: response.status(), captured: false, reason: 'sensitive-url' });
    return;
  }
  const key = `${normalizeUrlKey(url)}|${response.status()}`;
  // Static assets are immutable for a deployment, while the same API URL can
  // legitimately return different session/filter fixtures on different
  // routes. API responses are deduplicated only after their body hash exists.
  if (staticResource && state.seen.has(key)) return;
  const contentType = response.headers()['content-type'] || '';
  let body;
  try {
    body = await response.body();
  } catch (error) {
    state.network.push({ url: redactUrl(url), method: request.method(), resourceType: request.resourceType(), status: response.status(), captured: false, reason: `body-read-failed:${error.message}` });
    return;
  }
  const maxBytes = apiResource ? 2 * 1024 * 1024 : 20 * 1024 * 1024;
  if (body.byteLength > maxBytes) {
    state.network.push({ url: redactUrl(url), method: request.method(), resourceType: request.resourceType(), status: response.status(), bytes: body.byteLength, captured: false, reason: 'body-too-large' });
    return;
  }
  let bodyToWrite = body;
  let redacted = false;
  if (apiResource && /(?:application\/json|text\/json)/i.test(contentType)) {
    try {
      bodyToWrite = Buffer.from(`${JSON.stringify(redactValue(JSON.parse(body.toString('utf8'))), null, 2)}\n`, 'utf8');
      redacted = true;
    } catch {
      state.network.push({ url: redactUrl(url), method: request.method(), resourceType: request.resourceType(), status: response.status(), bytes: body.byteLength, captured: false, reason: 'api-json-parse-failed' });
      return;
    }
  }
  if (apiResource) {
    const apiKey = `${key}|${sha256(bodyToWrite)}`;
    if (state.seen.has(apiKey)) return;
    state.seen.add(apiKey);
  }
  const parsed = new URL(url);
  const segments = parsed.pathname.split('/').filter(Boolean).map(safeSegment);
  const originalBase = safeSegment(segments.pop() || 'index');
  const querySuffix = parsed.search ? `--q-${sha1(parsed.search).slice(0, 10)}` : '';
  const bodySuffix = apiResource ? `--body-${sha256(bodyToWrite).slice(0, 12)}` : '';
  // Keep deployed extensions (`main.js`, `styles.css`) instead of producing
  // noisy `main.js.js` filenames. Extensionless resources still get one from
  // their response MIME type so the archive remains easy to inspect.
  const hasExtension = Boolean(path.extname(originalBase));
  const filename = `${originalBase}${querySuffix}${bodySuffix}${hasExtension ? '' : contentExtension(contentType, parsed.pathname)}`;
  const resourceDir = path.join(state.resourcesDir, safeSegment(parsed.hostname), ...segments);
  await fs.mkdir(resourceDir, { recursive: true });
  const filePath = path.join(resourceDir, filename);
  await fs.writeFile(filePath, bodyToWrite);
  if (staticResource) state.seen.add(key);
  const record = {
    url: redactUrl(url),
    exactUrl: redactUrl(url),
    method: request.method(),
    resourceType: request.resourceType(),
    status: response.status(),
    contentType,
    bytes: bodyToWrite.byteLength,
    sha256: sha256(bodyToWrite),
    sha1: sha1(bodyToWrite),
    redacted,
    path: path.relative(state.outputDir, filePath).replaceAll(path.sep, '/'),
  };
  state.resources.push(record);
  state.resourceByUrl.set(normalizeUrlKey(url), record);
  state.network.push({ ...record, captured: true });
}

async function flushPending(state) {
  const pending = state.pending.splice(0);
  await Promise.allSettled(pending);
}

async function detectLogin(page) {
  const url = page.url();
  const text = (await page.locator('body').innerText({ timeout: 4_000 }).catch(() => '')).slice(0, 40_000);
  return /(?:sign\s*in|log\s*in|continue with google|create account|forgot password)/i.test(`${url}\n${text}`);
}

async function waitForManualLogin(page, noPrompt) {
  if (noPrompt || !(await detectLogin(page))) return false;
  console.log(`\nFXReplay đang yêu cầu đăng nhập tại ${page.url()}.`);
  console.log('Hãy đăng nhập thủ công trong cửa sổ browser. Script không đọc hoặc điền mật khẩu.');
  const rl = createInterface({ input, output });
  await rl.question('Sau khi thấy Testing/FXReplay, nhấn Enter để tiếp tục capture... ');
  rl.close();
  if (await detectLogin(page)) {
    throw new Error('Trang vẫn có vẻ đang ở màn đăng nhập; dừng để không ghi capture sai.');
  }
  return true;
}

async function savePageState(page, state, routeId, suffix = 'page') {
  const routeDir = path.join(state.routesDir, routeDirectoryName(routeId));
  await fs.mkdir(routeDir, { recursive: true });
  const base = path.join(routeDir, suffix);
  await page.evaluate(() => document.fonts?.ready).catch(() => {});
  await page.screenshot({ path: `${base}.png`, fullPage: true, animations: 'disabled' }).catch(() => {});
  await fs.writeFile(`${base}.html`, await page.content(), 'utf8');
  const text = await page.locator('body').innerText({ timeout: 4_000 }).catch(() => '');
  await fs.writeFile(`${base}.txt`, text, 'utf8');
  const aria = await page.locator('body').ariaSnapshot({ timeout: 4_000 }).catch(() => '');
  await fs.writeFile(`${base}.aria.yml`, aria || '', 'utf8');
  const geometry = await page.locator('body').evaluate((body) => Array.from(body.querySelectorAll('header,nav,aside,main,h1,h2,h3,button,[role="dialog"],[role="tab"],[role="tabpanel"]')).slice(0, 400).map((element) => {
    const rect = element.getBoundingClientRect();
    return {
      tag: element.tagName.toLowerCase(),
      role: element.getAttribute('role'),
      text: (element.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 240),
      x: Math.round(rect.x), y: Math.round(rect.y), width: Math.round(rect.width), height: Math.round(rect.height),
    };
  }).filter((item) => item.width > 0 && item.height > 0)).catch(() => []);
  await fs.writeFile(`${base}.geometry.json`, `${JSON.stringify(geometry, null, 2)}\n`, 'utf8');
  const meta = {
    routeId,
    url: redactUrl(page.url()),
    title: await page.title().catch(() => ''),
    viewport: page.viewportSize(),
    capturedAt: new Date().toISOString(),
  };
  await fs.writeFile(`${base}.json`, `${JSON.stringify(meta, null, 2)}\n`, 'utf8');
}

async function clickSafeInteraction(page, interaction, state, routeId, index) {
  const label = interaction.label || `interaction-${index + 1}`;
  const selectors = Array.isArray(interaction.selectors) ? interaction.selectors : [interaction.selector || interaction.text].filter(Boolean);
  if (!selectors.length) return { label, status: 'skipped', reason: 'no-selector' };
  for (const selector of selectors) {
    let locator;
    try {
      locator = selector.startsWith('text=') || selector.startsWith('role=') ? page.locator(selector) : page.locator(selector);
      const count = await locator.count();
      if (!count) continue;
      const candidate = locator.first();
      const text = `${await candidate.innerText().catch(() => '')} ${await candidate.getAttribute('aria-label').catch(() => '')}`.trim();
      if (UNSAFE_CONTROL.test(`${label} ${text}`)) return { label, status: 'skipped', reason: 'unsafe-control' };
      await candidate.scrollIntoViewIfNeeded().catch(() => {});
      await candidate.click({ timeout: 3_000 });
      await page.waitForTimeout(450);
      await savePageState(page, state, routeId, `interaction-${String(index + 1).padStart(2, '0')}-${routeDirectoryName(label)}`);
      await page.keyboard.press('Escape').catch(() => {});
      return { label, status: 'clicked', selector, text };
    } catch (error) {
      state.logs.push({ routeId, label, selector, error: error.message });
    }
  }
  return { label, status: 'not-found' };
}

async function captureNgsw(page, state) {
  const candidates = [
    new URL('ngsw.json', state.baseUrl).href,
    new URL('/ngsw.json', state.baseUrl).href,
  ];
  let payload;
  let sourceUrl;
  for (const candidate of candidates) {
    const result = await page.evaluate(async (url) => {
      try {
        const response = await fetch(url, { credentials: 'include' });
        if (!response.ok) return { ok: false, status: response.status };
        return { ok: true, status: response.status, text: await response.text() };
      } catch (error) {
        return { ok: false, error: error.message };
      }
    }, candidate).catch(() => ({ ok: false }));
    if (result.ok) {
      try {
        payload = JSON.parse(result.text);
        sourceUrl = candidate;
        break;
      } catch {
        // Try the next candidate.
      }
    }
  }
  if (!payload) {
    state.ngsw = { found: false, candidates };
    return;
  }
  const ngswPath = path.join(state.outputDir, 'ngsw.json');
  await fs.writeFile(ngswPath, `${JSON.stringify(payload, null, 2)}\n`, 'utf8');
  const expected = new Set(Object.keys(payload.hashTable || {}));
  for (const group of payload.assetGroups || []) {
    for (const file of group.resources?.files || []) expected.add(file);
    for (const url of group.resources?.urls || []) expected.add(url);
  }
  const capturedByUrl = new Map();
  for (const resource of state.resources) capturedByUrl.set(normalizeUrlKey(resource.exactUrl), resource);
  const missing = [];
  const mismatched = [];
  for (const expectedPath of expected) {
    let absolute;
    try { absolute = new URL(expectedPath, sourceUrl).href; } catch { continue; }
    const key = normalizeUrlKey(absolute);
    const found = capturedByUrl.get(key);
    if (!found) {
      missing.push(expectedPath);
      continue;
    }
    const expectedSha1 = payload.hashTable?.[expectedPath];
    if (expectedSha1 && found.sha1 && expectedSha1 !== found.sha1) mismatched.push({ path: expectedPath, expected: expectedSha1, actual: found.sha1 });
  }
  state.ngsw = {
    found: true,
    sourceUrl,
    hashTableEntries: Object.keys(payload.hashTable || {}).length,
    expectedResourceEntries: expected.size,
    capturedSameOriginBodies: state.resources.length,
    missingCount: missing.length,
    missing,
    mismatchedCount: mismatched.length,
    mismatched,
  };
  await fs.writeFile(path.join(state.outputDir, 'ngsw-report.json'), `${JSON.stringify(state.ngsw, null, 2)}\n`, 'utf8');
}

function sanitizeHar(har, allowedOrigin) {
  const clone = JSON.parse(JSON.stringify(har));
  // Keep the exported HAR first-party only. The raw temporary HAR is removed
  // after sanitization, so tracker/auth-provider URLs do not escape the run.
  clone.log.entries = (clone.log?.entries || []).filter((entry) => isSameOrigin(entry.request?.url || '', allowedOrigin));
  for (const entry of clone.log.entries) {
    if (entry.request) {
      entry.request.url = redactUrl(entry.request.url);
      entry.request.headers = redactHeaders(entry.request.headers);
      if (Array.isArray(entry.request.queryString)) {
        entry.request.queryString = entry.request.queryString.map((item) => ({
          ...item,
          value: SENSITIVE_KEY.test(item.name) || /^(?:auth|code|key|token|secret|password)$/i.test(item.name) ? '[REDACTED]' : item.value,
        }));
      }
      if (entry.request.postData) {
        const url = entry.request.url;
        entry.request.postData = SENSITIVE_URL.test(url) ? undefined : { mimeType: entry.request.postData.mimeType, text: '[POST_DATA_OMITTED]' };
      }
      delete entry.request.cookies;
    }
    if (entry.response) {
      entry.response.headers = redactHeaders(entry.response.headers);
      delete entry.response.cookies;
    }
  }
  return clone;
}

async function finalizeHar(tempHar, outputHar, allowedOrigin) {
  try {
    const parsed = JSON.parse(await fs.readFile(tempHar, 'utf8'));
    await fs.writeFile(outputHar, `${JSON.stringify(sanitizeHar(parsed, allowedOrigin), null, 2)}\n`, 'utf8');
    await fs.rm(tempHar, { force: true });
    return true;
  } catch (error) {
    console.warn(`HAR sanitize failed: ${error.message}`);
    return false;
  }
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const baseUrl = new URL(args.baseUrl);
  if (!/^https?:$/.test(baseUrl.protocol)) throw new Error('--base-url must use http(s)');
  const routes = await loadRoutes(args, baseUrl.href);
  await fs.mkdir(args.out, { recursive: true });
  const state = {
    outputDir: args.out,
    resourcesDir: path.join(args.out, 'resources'),
    routesDir: path.join(args.out, 'routes'),
    origin: baseUrl.origin,
    baseUrl: baseUrl.href,
    includeApi: args.includeApi,
    resources: [],
    resourceByUrl: new Map(),
    network: [],
    logs: [],
    pending: [],
    seen: new Set(),
    ngsw: null,
  };
  await fs.mkdir(state.resourcesDir, { recursive: true });
  await fs.mkdir(state.routesDir, { recursive: true });
  const playwright = loadPlaywright();
  const tempHar = path.join(args.out, '.capture.har.tmp');
  const finalHar = path.join(args.out, 'capture.har');
  let context;
  let page;
  const startedAt = new Date().toISOString();
  try {
    context = await playwright.chromium.launchPersistentContext(args.profile, {
      headless: args.headless,
      viewport: { width: 1920, height: 1080 },
      recordHar: { path: tempHar, content: 'omit', mode: 'full' },
      // Keep the capture honest: service-worker cache hits would hide the
      // resources that a clean browser actually needs to load.
      serviceWorkers: 'block',
      acceptDownloads: false,
    });
    page = context.pages()[0] || await context.newPage();
    page.on('response', (response) => {
      state.pending.push(captureResponse(response, state));
    });
    await page.goto(baseUrl.href, { waitUntil: 'domcontentloaded', timeout: 45_000 });
    await page.waitForTimeout(1_500);
    await waitForManualLogin(page, args.noPrompt);
    await page.waitForTimeout(1_000);
    for (const route of routes) {
      const started = Date.now();
      const record = { id: route.id, path: route.path, url: route.url, status: 'started', interactions: [], startedAt: new Date().toISOString() };
      try {
        await page.goto(route.url, { waitUntil: 'domcontentloaded', timeout: 45_000 });
        await page.waitForTimeout(1_500);
        if (await detectLogin(page)) {
          record.status = 'login-required';
          await waitForManualLogin(page, args.noPrompt);
        }
        await savePageState(page, state, route.id);
        const interactions = route.interactions.length ? route.interactions : [
          { label: 'open-session-picker', selectors: ['[aria-label*="Select session" i]', 'button:has-text("Select session")'] },
          { label: 'open-filters', selectors: ['button:has-text("Filter")', 'button:has-text("Type")', '[aria-label*="filter" i]'] },
          { label: 'open-analytics-menu', selectors: ['button:has-text("Analytics")', '[aria-label*="analytics" i]'] },
        ];
        for (let index = 0; index < interactions.length; index += 1) {
          record.interactions.push(await clickSafeInteraction(page, interactions[index], state, route.id, index));
        }
        await flushPending(state);
        record.status = 'captured';
      } catch (error) {
        record.status = 'failed';
        record.error = error.message;
        state.logs.push({ routeId: route.id, error: error.message });
      }
      record.durationMs = Date.now() - started;
      record.finishedAt = new Date().toISOString();
      state.logs.push(record);
      console.log(`[${record.status}] ${route.id} (${record.durationMs}ms)`);
    }
    await flushPending(state);
    await captureNgsw(page, state);
  } finally {
    if (context) await context.close().catch(() => {});
    await finalizeHar(tempHar, finalHar, state.origin);
  }
  const finishedAt = new Date().toISOString();
  for (const resource of state.resources) {
    const filePath = path.join(state.outputDir, resource.path);
    try {
      resource.sha1 = sha1(await fs.readFile(filePath));
    } catch {
      // Preserve the manifest record; the missing file is surfaced by verification.
    }
  }
  const manifest = {
    schemaVersion: 1,
    kind: 'fxreplay-read-only-capture',
    baseUrl: state.baseUrl,
    origin: state.origin,
    startedAt,
    finishedAt,
    includeApi: state.includeApi,
    routeCount: routes.length,
    routes: state.logs,
    resourceCount: state.resources.length,
    resources: state.resources,
    networkCount: state.network.length,
    network: state.network,
    ngsw: state.ngsw,
    safety: {
      loginAutomated: false,
      destructiveControlsClicked: false,
      profilePath: args.profile,
      harHeadersSanitized: true,
      apiBodiesRedacted: state.includeApi,
    },
  };
  await fs.writeFile(path.join(args.out, 'capture-manifest.json'), `${JSON.stringify(manifest, null, 2)}\n`, 'utf8');
  console.log(`\nCapture complete: ${args.out}`);
  console.log(`Resources: ${state.resources.length}; routes: ${routes.length}; HAR: ${finalHar}`);
  if (state.ngsw?.found) console.log(`ngsw expected: ${state.ngsw.expectedResourceEntries}; missing: ${state.ngsw.missingCount}; mismatched: ${state.ngsw.mismatchedCount}`);
}

main().catch((error) => {
  console.error(`Capture failed: ${error.stack || error.message}`);
  process.exitCode = 1;
});

