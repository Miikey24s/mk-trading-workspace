#!/usr/bin/env node

// Remove API/account identifiers from a capture-manifest network log. Static
// resource records remain intact because they are the useful reference data.

import fs from 'node:fs/promises';
import path from 'node:path';

const PRIVATE_PATH = /\/(?:api|auth-identity)(?:\/|$)|\/(?:identity|token|session[-_]?cookie|billing|payment|checkout)(?:\/|$)/i;
const PRIVATE_QUERY = /^(?:auth|code|key|token|secret|password|user[_-]?id|email)$/i;
const TRACKING_PATH = /\/(?:ute2|analytics|measurement|conversion)(?:\/|$)/i;

function redactUrl(rawUrl) {
  try {
    const url = new URL(rawUrl);
    if (PRIVATE_PATH.test(url.pathname)) return `${url.origin}/[REDACTED_API_URL]`;
    for (const key of url.searchParams.keys()) if (PRIVATE_QUERY.test(key)) url.searchParams.set(key, '[REDACTED]');
    return url.toString();
  } catch { return '[REDACTED_URL]'; }
}

async function main() {
  const file = process.argv[2];
  if (!file || process.argv.includes('--help') || process.argv.includes('-h')) {
    console.log('Usage: node sanitize-manifest.mjs <capture-manifest.json>');
    process.exit(file ? 0 : 1);
  }
  const input = path.resolve(file);
  const manifest = JSON.parse(await fs.readFile(input, 'utf8'));
  manifest.network = (manifest.network || []).map((record) => {
    const rawUrl = record.url || '';
    const tracking = TRACKING_PATH.test(rawUrl);
    if (tracking) return { ...record, url: '[REDACTED_TRACKING_URL]', captured: false, reason: 'tracking-url' };
    const url = redactUrl(rawUrl);
    return {
      ...record,
      url,
      ...(url.includes('[REDACTED_API_URL]') ? { captured: false, reason: 'sensitive-url' } : {}),
    };
  });
  manifest.networkCount = manifest.network.length;
  const temp = `${input}.sanitized.tmp`;
  await fs.writeFile(temp, `${JSON.stringify(manifest, null, 2)}\n`, 'utf8');
  await fs.rename(temp, input);
  console.log(`Sanitized network log: ${input}`);
}

main().catch((error) => { console.error(`Manifest sanitization failed: ${error.stack || error.message}`); process.exitCode = 1; });

