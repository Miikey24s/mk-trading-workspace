import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { randomUUID } from 'node:crypto'
import { runCli, KIT } from '../qa.mjs'
import { startFixture } from '../fixtures/server.mjs'

const session = `tw-cli-smoke-${randomUUID().slice(0, 8)}`
const fixture = await startFixture()
const excluded = await startFixture()
const results = []
let opened = false
const directory = path.join(KIT, 'artifacts/cli', session)
async function call(command, origins = []) {
  const args = ['--session', session, ...origins.flatMap(origin => ['--origin', origin]), '--', ...command]
  const result = await runCli(args)
  results.push({ command: command[0], code: result.code })
  assert.equal(result.code, 0, result.stderr + result.stdout)
  return result.stdout
}
try {
  // Treat even a failed open as possibly started: close this exact session in finally.
  opened = true
  await call(['open', fixture.url], [fixture.url])
  await call(['fill', "getByLabel('Tên phiên thử công cụ')", 'CLI fixture có dấu'])
  await call(['click', "getByRole('button', { name: 'Lưu bản thử' })"])
  await call(['reload'])
  assert.match(await call(['eval', "document.querySelector('[role=status]').textContent"]), /Đã lưu: CLI fixture có dấu/)
  await call(['snapshot', '--depth=3'])
  await call(['screenshot'])
  // Confirm an otherwise reachable local origin receives no browser request.
  assert.equal((await fetch(excluded.url)).status, 200)
  const before = excluded.requests
  await call(['eval', `async () => { try { await fetch('${excluded.url}'); return 'unexpected'; } catch { return 'blocked'; } }`])
  assert.equal(excluded.requests, before)
  assert(fs.readdirSync(directory).some(name => name.endsWith('.png')), 'screenshot not saved')
} catch (error) {
  process.exitCode = 1
  results.push({ error: error.message })
} finally {
  if (opened) {
    try { await call(['close']) } catch (error) { process.exitCode = 1; results.push({ cleanupError: error.message }) }
  }
  await fixture.close(); await excluded.close()
  const receipt = { scope: 'TOOLING_CLI_SYNTHETIC_ONLY', session, status: process.exitCode ? 'FAIL' : 'PASS',
    results, artifacts: directory, productAcceptance: 'NOT_EVALUATED', broker: 'NOT_CONTACTED' }
  fs.mkdirSync(directory, { recursive: true })
  fs.writeFileSync(path.join(directory, 'cli-smoke-receipt.json'), JSON.stringify(receipt, null, 2))
  console.log(JSON.stringify(receipt, null, 2))
}
