#!/usr/bin/env node

/**
 * Fill a route capture with the remaining same-origin public files listed by
 * FXReplay's ngsw.json. This is deliberately separate from capture.mjs so a
 * route-focused capture can finish quickly and this larger download remains an
 * explicit, rate-limited step.
 *
 * It never submits forms, calls API endpoints, follows third-party URLs, or
 * writes browser state. The persistent profile is used only for the existing
 * browser context/cookies; static manifest resources are fetched read-only.
 */

import { createHash } from 'node:crypto';
import { createRequire } from 'node:module';
import path from 'node:path';
import fs from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const SENSITIVE_URL = /(?:\/(?:identity|token|session[-_]?cookie|billing|payment|checkout)(?:\/|$)|\/auth(?:entication)?\/(?:api|v\d|token|login|logout)(?:\/|$)|\/(?:firebase|hcaptcha|oauth|sso)(?:\/|$)|[?&](?:token|key|code|secret|password|auth)=)/i;

function printHelp() {
  console.log(`\nFill FXReplay public manifest resources\n\nUsage:\n  node fill-manifest.mjs --out D:\\ANNAM\\FXReplayCaptures\\fresh-2026-09-30 --profile <private-profile>\n\nOptions:\n  --out <dir>              Existing capture directory containing ngsw.json\n  --profile <dir>          Persistent profile outside the repo\n  --base-url <url>         Base URL (default: read from capture-manifest.json)\n  --concurrency <n>        Parallel static requests (default: 4)\n  --delay-ms <n>           Minimum delay per worker (default: 100)\n  --limit <n>              Maximum missing URLs to request (default: 10000)\n  --help                   Show this help\n\nOnly same-origin static manifest entries are fetched. Auth/API/third-party URLs are skipped.\n`);
}

function parseArgs(argv) {
  const args = {
    out: null,
    profile: path.join(process.env.LOCALAPPDATA || process.env.TEMP || process.cwd(), 'WMReplay', 'fxreplay-capture-profile'),
    baseUrl: null,
    concurrency: 4,
    delayMs: 100,
    limit: 10_000,
  };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--help' || arg === '-h') { printHelp(); process.exit(0); }
    const [key, inlineValue] = arg.split('=', 2);
    const value = inlineValue ?? argv[++i];
    if (value === undefined || value === '') throw new Error(`Missing value for ${key}`);
    if (key === '--out') args.out = path.resolve(value);
    else if (key === '--profile') args.profile = path.resolve(value);
    else if (key === '--base-url') args.baseUrl = value;
    else if (key === '--concurrency') args.concurrency = Math.max(1, Math.min(16, Number(value)));
    else if (key === '--delay-ms') args.delayMs = Math.max(0, Number(value));
    else if (key === '--limit') args.limit = Math.max(0, Number(value));
    else throw new Error(`Unknown option: ${key}`);
  }
  if (!args.out) throw new Error('--out is required');
  if (!Number.isFinite(args.concurrency) || !Number.isFinite(args.delayMs) || !Number.isFinite(args.limit)) throw new Error('Numeric options must be finite');
  return args;
}

function loadPlaywright() {
  const candidates = [
    process.env.PLAYWRIGHT_PACKAGE,
    'playwright',
    path.join(process.cwd(), 'node_modules', 'playwright'),
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
  throw new Error(`Playwright is not available. Set PLAYWRIGHT_PACKAGE or install it in the tooling project.\n${errors.join('\n')}`);
}

function sha(value, algorithm) { return createHash(algorithm).update(value).digest('hex'); }
function safeSegment(value) { return decodeURIComponent(value || 'index').replace(/[<>:"/\\|?*\x00-\x1f]/g, '_').replace(/\.+$/g, '_').slice(0, 180) || 'index'; }
function normalize(rawUrl) {
  const url = new URL(rawUrl);
  return `${url.origin}${url.pathname}${url.search}`;
}
function extFor(contentType, pathname) {
  const ext = path.extname(pathname);
  if (ext && ext.length <= 12) return ext;
  const mime = contentType.toLowerCase().split(';', 1)[0];
  return ({
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
  })[mime] || '.bin';
}

async function readJson(file) { return JSON.parse(await fs.readFile(file, 'utf8')); }
async function sleep(ms) { if (ms > 0) await new Promise((resolve) => setTimeout(resolve, ms)); }

function manifestPaths(ngsw) {
  const values = new Set(Object.keys(ngsw.hashTable || {}));
  for (const group of ngsw.assetGroups || []) {
    for (const file of group.resources?.files || []) values.add(file);
    for (const url of group.resources?.urls || []) values.add(url);
  }
  return [...values];
}

function makeTargetPath(outputDir, rawUrl, contentType) {
  const parsed = new URL(rawUrl);
  const segments = parsed.pathname.split('/').filter(Boolean).map(safeSegment);
  const original = safeSegment(segments.pop() || 'index');
  const query = parsed.search ? `--q-${sha(parsed.search, 'sha1').slice(0, 10)}` : '';
  const filename = `${original}${query}${path.extname(original) ? '' : extFor(contentType, parsed.pathname)}`;
  return path.join(outputDir, 'resources', safeSegment(parsed.hostname), ...segments, filename);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const manifestFile = path.join(args.out, 'capture-manifest.json');
  const ngswFile = path.join(args.out, 'ngsw.json');
  const capture = await readJson(manifestFile);
  const ngsw = await readJson(ngswFile);
  const baseUrl = new URL(args.baseUrl || capture.baseUrl);
  const expected = manifestPaths(ngsw);
  const existing = new Set((capture.resources || []).map((resource) => normalize(resource.exactUrl || resource.url)));
  const targets = [];
  const skipped = [];
  for (const entry of expected) {
    let url;
    try { url = new URL(entry, baseUrl); } catch { skipped.push({ entry, reason: 'invalid-url' }); continue; }
    if (url.origin !== baseUrl.origin) { skipped.push({ entry, reason: 'third-party' }); continue; }
    if (SENSITIVE_URL.test(url.href)) { skipped.push({ entry, reason: 'sensitive-url' }); continue; }
    // ngsw.json is already the service-worker's static-resource inventory.
    // Do not impose an extension allowlist: FXReplay also ships WAV/CSV/MD,
    // Monaco declaration files, and extensionless static entries.
    const key = normalize(url.href);
    if (existing.has(key)) continue;
    targets.push({ entry, url: url.href });
  }
  const selected = targets.slice(0, args.limit);
  console.log(`Manifest entries: ${expected.length}; already captured: ${existing.size}; selected: ${selected.length}; skipped: ${skipped.length}`);
  if (!selected.length) { console.log('Nothing to fill.'); return; }

  const playwright = loadPlaywright();
  const context = await playwright.chromium.launchPersistentContext(args.profile, {
    headless: true,
    serviceWorkers: 'block',
    acceptDownloads: false,
  });
  const results = [];
  let cursor = 0;
  const worker = async (workerId) => {
    while (true) {
      const index = cursor++;
      if (index >= selected.length) return;
      const target = selected[index];
      if (index > 0) await sleep(args.delayMs);
      try {
        const response = await context.request.get(target.url, { timeout: 30_000, failOnStatusCode: false, maxRedirects: 5 });
        const status = response.status();
        if (status !== 200) {
          results.push({ ...target, status, captured: false, reason: 'http-status' });
          continue;
        }
        const contentType = response.headers()['content-type'] || '';
        const body = await response.body();
        const filePath = makeTargetPath(args.out, target.url, contentType);
        await fs.mkdir(path.dirname(filePath), { recursive: true });
        await fs.writeFile(filePath, body);
        const record = {
          url: target.url,
          exactUrl: target.url,
          method: 'GET',
          resourceType: 'manifest-fill',
          status,
          contentType,
          bytes: body.byteLength,
          sha256: sha(body, 'sha256'),
          sha1: sha(body, 'sha1'),
          manifestPath: target.entry,
          path: path.relative(args.out, filePath).replaceAll(path.sep, '/'),
        };
        results.push({ ...record, captured: true });
        capture.resources.push(record);
      } catch (error) {
        results.push({ ...target, captured: false, reason: `request-failed:${error.message}` });
      }
      if ((index + 1) % 100 === 0) console.log(`filled ${index + 1}/${selected.length}`);
    }
  };
  try {
    await Promise.all(Array.from({ length: args.concurrency }, (_, index) => worker(index)));
  } finally {
    await context.close().catch(() => {});
  }

  const capturedByUrl = new Map(capture.resources.map((resource) => [normalize(resource.exactUrl || resource.url), resource]));
  const missing = [];
  const mismatched = [];
  for (const entry of expected) {
    let absolute;
    try { absolute = new URL(entry, baseUrl).href; } catch { continue; }
    const record = capturedByUrl.get(normalize(absolute));
    if (!record) { missing.push(entry); continue; }
    const expectedSha1 = ngsw.hashTable?.[entry];
    if (expectedSha1 && record.sha1 && expectedSha1 !== record.sha1) mismatched.push({ path: entry, expected: expectedSha1, actual: record.sha1 });
  }
  const report = {
    generatedAt: new Date().toISOString(),
    baseUrl: baseUrl.href,
    expectedCount: expected.length,
    selectedCount: selected.length,
    capturedCount: results.filter((result) => result.captured).length,
    failedCount: results.filter((result) => !result.captured).length,
    missingCount: missing.length,
    mismatchedCount: mismatched.length,
    skippedCount: skipped.length,
    missing,
    mismatched,
    skipped,
    results,
  };
  await fs.writeFile(path.join(args.out, 'manifest-fill-report.json'), `${JSON.stringify(report, null, 2)}\n`, 'utf8');
  const ngswReportFile = path.join(args.out, 'ngsw-report.json');
  try {
    const ngswReport = await readJson(ngswReportFile);
    ngswReport.capturedSameOriginBodies = capture.resources.length;
    ngswReport.missingCount = missing.length;
    ngswReport.missing = missing;
    ngswReport.mismatchedCount = mismatched.length;
    ngswReport.mismatched = mismatched;
    await fs.writeFile(ngswReportFile, `${JSON.stringify(ngswReport, null, 2)}\n`, 'utf8');
  } catch {
    // The separate fill report remains authoritative if the route report is absent.
  }
  capture.resourceCount = capture.resources.length;
  capture.manifestFill = { generatedAt: report.generatedAt, ...report, results: undefined, skipped: undefined, missing: undefined, mismatched: undefined };
  await fs.writeFile(manifestFile, `${JSON.stringify(capture, null, 2)}\n`, 'utf8');
  console.log(`\nManifest fill complete: captured ${report.capturedCount}; failed ${report.failedCount}; missing ${report.missingCount}; mismatched ${report.mismatchedCount}`);
}

main().catch((error) => { console.error(`Manifest fill failed: ${error.stack || error.message}`); process.exitCode = 1; });

