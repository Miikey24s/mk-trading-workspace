#!/usr/bin/env node

// One-shot sanitizer for an existing HAR. Useful when a capture was started
// with an older crawler version. It keeps first-party request metadata only;
// cookies, credential headers, request bodies, and third-party entries are
// removed before replacing the original file.

import fs from 'node:fs/promises';
import path from 'node:path';

const SENSITIVE_HEADER = /^(?:authorization|proxy-authorization|cookie|set-cookie|x-api-key|x-auth-token|x-csrf-token|x-xsrf-token|password|passwd|secret|token|id[-_]?token|access[-_]?token|refresh[-_]?token|client[-_]?secret|session[-_]?cookie)$/i;
const SENSITIVE_QUERY = /^(?:auth|code|key|token|secret|password|client_secret|access_token|refresh_token)$/i;

function redactUrl(rawUrl) {
  try {
    const url = new URL(rawUrl);
    for (const key of url.searchParams.keys()) if (SENSITIVE_QUERY.test(key)) url.searchParams.set(key, '[REDACTED]');
    return url.toString();
  } catch { return rawUrl; }
}

function safeHeaders(headers = []) {
  return headers.filter((header) => !SENSITIVE_HEADER.test(header.name || ''));
}

function parseArgs(argv) {
  const input = argv[0];
  if (!input || argv.includes('--help') || argv.includes('-h')) {
    console.log('Usage: node sanitize-har.mjs <capture.har> [allowed-origin]');
    process.exit(input ? 0 : 1);
  }
  return { input: path.resolve(input), origin: argv[1] || null };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const har = JSON.parse(await fs.readFile(args.input, 'utf8'));
  const entries = har.log?.entries || [];
  const origin = args.origin || (entries[0]?.request?.url ? new URL(entries[0].request.url).origin : null);
  if (!origin) throw new Error('Cannot determine allowed origin; pass it as the second argument');
  har.log.entries = entries.filter((entry) => {
    try {
      const url = new URL(entry.request?.url || '');
      return (url.protocol === 'http:' || url.protocol === 'https:') && url.origin === origin;
    } catch { return false; }
  });
  for (const entry of har.log.entries) {
    if (entry.request) {
      entry.request.url = redactUrl(entry.request.url);
      entry.request.headers = safeHeaders(entry.request.headers);
      delete entry.request.cookies;
      delete entry.request.postData;
    }
    if (entry.response) {
      entry.response.headers = safeHeaders(entry.response.headers);
      delete entry.response.cookies;
    }
  }
  const temp = `${args.input}.sanitized.tmp`;
  await fs.writeFile(temp, `${JSON.stringify(har, null, 2)}\n`, 'utf8');
  await fs.rename(temp, args.input);
  console.log(`Sanitized ${har.log.entries.length} first-party HAR entries: ${args.input}`);
}

main().catch((error) => { console.error(`HAR sanitization failed: ${error.stack || error.message}`); process.exitCode = 1; });

