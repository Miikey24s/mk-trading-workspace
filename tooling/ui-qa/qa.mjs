import { execFile } from 'node:child_process'
import { createHash, randomUUID } from 'node:crypto'
import fs from 'node:fs'
import path from 'node:path'
import { createRequire } from 'node:module'
import { fileURLToPath } from 'node:url'
import { promisify } from 'node:util'

const exec = promisify(execFile)
export const KIT = path.dirname(fileURLToPath(import.meta.url))
export const ROOT = path.resolve(KIT, '../..')
export const PLAN = path.join(ROOT, 'planning/mt5-tradingview-backtester/PRODUCT-COMPLETION-PLAN.md')
const require = createRequire(import.meta.url)
const readJson = file => JSON.parse(fs.readFileSync(file, 'utf8'))
const hash = file => createHash('sha256').update(fs.readFileSync(file)).digest('hex')

export function browserPath() {
  if (process.env.TW_UI_QA_CHROMIUM) return process.env.TW_UI_QA_CHROMIUM
  const full = require('@playwright/test').chromium.executablePath()
  // The Windows headless fixture must use the headless-shell distribution,
  // matching Playwright's default headless launch rather than forcing full Chrome.
  if (process.platform === 'win32') {
    const shell = full.replace(/chromium-(\d+)[\\/].+$/, 'chromium_headless_shell-$1/chrome-headless-shell-win64/chrome-headless-shell.exe')
    if (shell !== full && fs.existsSync(shell)) return shell
  }
  return full
}

export function localOrigin(value) {
  const url = new URL(value)
  if (url.protocol !== 'http:' || !['127.0.0.1', 'localhost', '[::1]'].includes(url.hostname)
      || !url.port || url.username || url.password || url.search || url.hash || url.pathname !== '/') {
    throw new Error('Use an explicit loopback http origin with port, no credentials/path/query.')
  }
  return url.origin
}

export function cliRequest(args) {
  const split = args.indexOf('--')
  if (split < 0) throw new Error('CLI requires --session tw-TASK [--origin URL] -- COMMAND')
  let session
  const origins = []
  for (let i = 0; i < split; i += 2) {
    const value = args[i + 1]
    if (!value || i + 1 >= split) throw new Error('Missing option value')
    if (args[i] === '--session' && !session) session = value
    else if (args[i] === '--origin') origins.push(localOrigin(value))
    else throw new Error(`Unknown/duplicate option: ${args[i]}`)
  }
  if (!/^tw-[a-z0-9][a-z0-9-]{0,43}$/.test(session || '')) throw new Error('Use a unique tw-TASK session name')
  const command = args.slice(split + 1)
  const allowed = new Set(['open', 'close', 'goto', 'reload', 'snapshot', 'find', 'click', 'dblclick',
    'fill', 'type', 'press', 'hover', 'select', 'check', 'uncheck', 'resize', 'screenshot',
    'console', 'requests', 'eval', 'run-code', 'tracing-start', 'tracing-stop', 'tab-list',
    'tab-select', 'set-color-scheme', 'set-reduced-motion'])
  if (!allowed.has(command[0])) throw new Error('Command is not in the scoped UI-QA command set')
  if (command.slice(1).some(a => /^(?:-s|--session)(?:=|$)/.test(a))) {
    throw new Error('Session is owned by --session before the separator; command cannot override it')
  }
  if (command.slice(1).some(a => /^--(?:config|profile|persistent|cdp|extension|headed|browser|storage-state)(?:=|$)/.test(a))) {
    throw new Error('Do not attach to personal profiles or override the isolated browser configuration')
  }
  if (command[0] === 'open' && (command.length !== 2 || !origins.length)) {
    throw new Error('Open requires one URL and explicit --origin allowlist')
  }
  if (['open', 'goto'].includes(command[0])) {
    const url = new URL(command[1])
    localOrigin(url.origin)
    if (url.username || url.password) throw new Error('Credentials in URLs are not allowed')
  }
  return { session, origins: [...new Set(origins)], command }
}

export function doctor(plan = PLAN) {
  if (path.resolve(plan) !== PLAN) throw new Error('Pass the canonical PRODUCT-COMPLETION-PLAN.md, not a copied plan')
  const paths = [PLAN,
    path.join(path.dirname(PLAN), 'EXECUTION-ENTRYPOINT.md'),
    path.join(path.dirname(PLAN), 'UI-AUTONOMY-FIGMA-PROP-PLAN.md'),
    path.join(ROOT, 'projects/mt5-tradingview-backtester/AGENTS.md'),
    path.join(ROOT, 'projects/mt5-tradingview-backtester/.agents/skills/trading-ui-qa/SKILL.md'),
    path.join(KIT, 'README.md'), path.join(KIT, 'playwright.config.mjs'), path.join(KIT, 'package-lock.json')]
  const missing = paths.filter(file => !fs.existsSync(file))
  const packages = {}
  for (const name of ['@playwright/cli', '@playwright/test']) {
    try { packages[name] = require(`${name}/package.json`).version } catch { missing.push(`dependency:${name}`) }
  }
  let chromium = null
  try { chromium = browserPath(); if (!fs.existsSync(chromium)) missing.push('chromium executable') }
  catch { missing.push('chromium resolution') }
  return { scope: 'tooling-readiness-only', ready: missing.length === 0, missing, node: process.version,
    packages, chromium, plan: PLAN, readNext: paths.slice(1, 6),
    planSha256: fs.existsSync(PLAN) ? hash(PLAN) : null,
    productAcceptance: 'NOT_EVALUATED', broker: 'NOT_CONTACTED',
    note: 'Read the operational RESUME/ledger linked by the entrypoint; this CLI never updates task state.' }
}

async function runNode(file, args, options = {}) {
  try {
    const result = await exec(process.execPath, [file, ...args], {
      cwd: KIT, windowsHide: true, timeout: 60000, maxBuffer: 4 * 1024 * 1024, ...options,
    })
    return { ...result, code: 0 }
  } catch (error) {
    return { stdout: error.stdout || '', stderr: error.stderr || error.message,
      code: Number.isInteger(error.code) ? error.code : 1 }
  }
}

export async function runCli(args) {
  const { session, origins, command } = cliRequest(args)
  const directory = path.join(KIT, 'artifacts/cli', session)
  const configFile = path.join(directory, 'config.json')
  if (command[0] === 'open') {
    if (!origins.includes(new URL(command[1]).origin)) throw new Error('Opening URL outside allowlist')
    if (!fs.existsSync(browserPath())) throw new Error('Chromium missing; doctor first. No automatic download.')
    fs.mkdirSync(directory, { recursive: true })
    const config = { browser: { browserName: 'chromium', isolated: true,
      launchOptions: { executablePath: browserPath(), headless: true },
      contextOptions: { serviceWorkers: 'block', viewport: { width: 1440, height: 900 } } },
      outputDir: directory, outputMode: 'file', network: { allowedOrigins: origins },
      timeouts: { action: 5000, navigation: 15000 } }
    if (fs.existsSync(configFile)) {
      if (JSON.stringify(readJson(configFile)) !== JSON.stringify(config)) {
        throw new Error('Existing session config differs; choose a new task/attempt session')
      }
    } else fs.writeFileSync(configFile, JSON.stringify(config, null, 2), { flag: 'wx' })
  } else if (!fs.existsSync(configFile)) throw new Error('Unknown session; open a new scoped session first')
  const config = readJson(configFile)
  if (command[0] === 'goto' && !config.network.allowedOrigins.includes(new URL(command[1]).origin)) {
    throw new Error('Navigation URL outside session allowlist')
  }
  const tail = command[0] === 'open' ? [...command, `--config=${configFile}`] : command
  const result = await runNode(require.resolve('@playwright/cli/playwright-cli.js'), [`-s=${session}`, ...tail])
  // Some agent-facing commands print a structured error but return exit 0.
  if (/^### Error\b/m.test(result.stdout) || /Assertion failed:/.test(result.stderr)) result.code = 1
  return { ...result, session, artifacts: directory }
}

export async function smoke(forceFailure = false) {
  const info = doctor()
  if (!info.ready) throw new Error(`Tooling not ready: ${info.missing.join(', ')}`)
  const runId = `smoke-${new Date().toISOString().replace(/[:.]/g, '-')}-${randomUUID().slice(0, 8)}`
  const directory = path.join(KIT, 'artifacts', runId)
  fs.mkdirSync(directory, { recursive: true })
  const result = await runNode(require.resolve('@playwright/test/cli'), ['test', '--config', path.join(KIT, 'playwright.config.mjs')], {
    env: { ...process.env, TW_UI_QA_RUN_DIR: directory, TW_UI_QA_FORCE_FAILURE: forceFailure ? '1' : '0' },
  })
  fs.writeFileSync(path.join(directory, 'console.log'), result.stdout + result.stderr)
  const reportFile = path.join(directory, 'results.json')
  const report = fs.existsSync(reportFile) ? readJson(reportFile) : null
  const passed = result.code === 0 && report?.stats?.expected > 0 && report.stats.unexpected === 0
    && report.stats.skipped === 0 && report.stats.flaky === 0
  const receipt = { schemaVersion: 1, runId, scope: 'TOOLING_SYNTHETIC_ONLY', status: passed ? 'PASS' : 'FAIL',
    exitCode: result.code || (passed ? 0 : 1), stats: report?.stats || null, injectedFailure: forceFailure,
    packages: info.packages, node: info.node, chromium: info.chromium,
    planSha256: info.planSha256, sourceHashes: Object.fromEntries(['qa.mjs', 'playwright.config.mjs',
      'fixtures/server.mjs', 'fixtures/index.html', 'smoke/fixture.spec.mjs', 'package-lock.json']
      .map(file => [file, hash(path.join(KIT, file))])),
    report: reportFile, artifacts: directory, productAcceptance: 'NOT_EVALUATED',
    broker: 'NOT_CONTACTED', figma: 'NOT_CONTACTED' }
  fs.writeFileSync(path.join(directory, 'receipt.json'), JSON.stringify(receipt, null, 2))
  return receipt
}

async function main(args) {
  const [mode, ...rest] = args
  if (mode === 'doctor') {
    if (rest.length && (rest.length !== 2 || rest[0] !== '--plan')) throw new Error('doctor [--plan PATH]')
    const result = doctor(rest[1] || PLAN)
    console.log(JSON.stringify(result, null, 2)); process.exitCode = result.ready ? 0 : 1
  } else if (mode === 'smoke') {
    if (rest.length && (rest.length !== 1 || rest[0] !== '--inject-failure')) throw new Error('smoke [--inject-failure]')
    const result = await smoke(rest[0] === '--inject-failure')
    console.log(JSON.stringify(result, null, 2)); process.exitCode = result.exitCode
  } else if (mode === 'cli') {
    const result = await runCli(rest)
    process.stdout.write(result.stdout); process.stderr.write(result.stderr); process.exitCode = result.code
  } else {
    console.log('UI QA: doctor [--plan PATH] | smoke [--inject-failure] | cli --session tw-TASK [--origin URL] -- COMMAND')
    if (mode && !['help', '--help'].includes(mode)) process.exitCode = 2
  }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main(process.argv.slice(2)).catch(error => { console.error(error.message); process.exitCode = 1 })
}
