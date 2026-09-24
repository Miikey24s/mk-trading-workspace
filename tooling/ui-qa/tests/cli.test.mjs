import { test } from 'node:test'
import assert from 'node:assert/strict'
import { localOrigin, cliRequest, doctor, PLAN } from '../qa.mjs'

test('allows explicit loopback origins, rejects remote/credentialed/path inputs', () => {
  assert.equal(localOrigin('http://127.0.0.1:12345'), 'http://127.0.0.1:12345')
  assert.equal(localOrigin('http://[::1]:12345'), 'http://[::1]:12345')
  for (const input of ['https://example.com', 'http://user:pass@localhost:123', 'file:///tmp/x',
    'http://localhost', 'http://localhost:123/api', 'http://localhost:123/?token=secret']) {
    assert.throws(() => localOrigin(input))
  }
})

test('requires a task-specific session and rejects global or personal-browser operations', () => {
  const request = cliRequest(['--session', 'tw-test', '--origin', 'http://127.0.0.1:12345', '--', 'open', 'http://127.0.0.1:12345/'])
  assert.equal(request.session, 'tw-test')
  for (const command of [['kill-all'], ['close-all'], ['delete-data'], ['attach'], ['state-load', 'auth.json'],
    ['open', 'http://127.0.0.1:12345/', '--persistent'], ['install'], ['webmcp-call', 'trade']]) {
    assert.throws(() => cliRequest(['--session', 'tw-test', '--', ...command]))
  }
  assert.throws(() => cliRequest(['--session', '../bad', '--', 'close']))
  assert.throws(() => cliRequest(['--session', 'tw-test', '--', 'goto', 'https://example.com']))
})

test('doctor uses one canonical plan and does not evaluate product acceptance', () => {
  assert.throws(() => doctor(PLAN + '.copy'))
  const result = doctor()
  assert.equal(result.plan, PLAN)
  assert.equal(result.productAcceptance, 'NOT_EVALUATED')
  assert.equal(result.broker, 'NOT_CONTACTED')
})

test('command arguments cannot select another worker browser session', () => {
  for (const override of [['-s=tw-other'], ['-s', 'tw-other'], ['--session=tw-other'], ['--session', 'tw-other']]) {
    assert.throws(() => cliRequest(['--session', 'tw-own', '--', 'snapshot', ...override]), /cannot override/)
  }
  assert.deepEqual(cliRequest(['--session', 'tw-own', '--', 'snapshot', '--depth=3']).command,
    ['snapshot', '--depth=3'])
})
