import { mkdtemp, mkdir, writeFile } from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'
import test from 'node:test'
import assert from 'node:assert/strict'
import { auditUiRegistry } from '../ui-registry-check.mjs'

test('audits every consumer and reports bounded partial adoption', async () => {
  const report = await auditUiRegistry({
    workspace: path.resolve(import.meta.dirname, '../../..'),
    systemsRoot: 'D:/ANNAM/UI-Systems',
  })
  assert.equal(report.status, 'ok')
  assert.equal(report.summary.pinCount, 2)
  assert.equal(report.summary.partialProjects, 2)
  const pinned = report.projects
    .flatMap(project => project.sharedUiPins.map(pin => ({ project: project.project, ...pin })))
  assert.deepEqual(pinned.map(pin => pin.system), ['annam-productivity', 'annam-productivity'])
  assert.ok(pinned.every(pin => pin.adoption === 'partial' && pin.scope.length > 0))
  assert.ok(pinned.every(pin => /^[a-f0-9]{64}$/.test(pin.snapshotSha256)))
})
test('rejects a candidate pin without contract and focused receipt evidence', async () => {
  const workspace = await mkdtemp(path.join(os.tmpdir(), 'tw-ui-registry-workspace-'))
  const systemsRoot = await mkdtemp(path.join(os.tmpdir(), 'tw-ui-registry-systems-'))
  const projectRoot = path.join(workspace, 'projects', 'candidate-consumer')
  const tokenRoot = path.join(systemsRoot, 'core', 'tokens', 'candidate', '1.0.0')
  await mkdir(path.join(projectRoot, 'ui'), { recursive: true })
  await mkdir(tokenRoot, { recursive: true })
  await writeFile(path.join(tokenRoot, 'light.tokens.json'), JSON.stringify({ color: { '$type': 'color' } }))
  await writeFile(path.join(tokenRoot, 'manifest.json'), JSON.stringify({
    schemaVersion: 1,
    name: 'candidate-system',
    version: '1.0.0',
    status: 'candidate',
    modes: { light: { file: 'light.tokens.json', selector: ':root' } },
    cssVariables: {},
  }))
  await writeFile(path.join(projectRoot, 'ui', 'project-ui.json'), JSON.stringify({
    schemaVersion: 1,
    status: 'exploration',
    sharedUiPins: [{
      system: 'candidate-system',
      version: '1.0.0',
      sourceSha256: '0'.repeat(64),
      snapshot: 'missing.css',
      scope: ['candidate.slice'],
    }],
  }))

  const report = await auditUiRegistry({ workspace, systemsRoot })
  assert.equal(report.status, 'error')
  assert.ok(report.errors.some(error => error.includes('candidate requires an existing token contract reference')))
  assert.ok(report.errors.some(error => error.includes('candidate requires an existing focused promotion receipt')))
})

test('rejects a malformed shared pin registry instead of treating it as no adoption', async () => {
  const workspace = await mkdtemp(path.join(os.tmpdir(), 'tw-ui-registry-workspace-'))
  const systemsRoot = await mkdtemp(path.join(os.tmpdir(), 'tw-ui-registry-systems-'))
  const projectRoot = path.join(workspace, 'projects', 'malformed-consumer')
  await mkdir(path.join(projectRoot, 'ui'), { recursive: true })
  await writeFile(path.join(projectRoot, 'ui', 'project-ui.json'), JSON.stringify({
    schemaVersion: 1,
    status: 'exploration',
    sharedUiPins: { system: 'annam-productivity', version: '1.0.0' },
  }))

  const report = await auditUiRegistry({ workspace, systemsRoot })
  assert.equal(report.status, 'error')
  assert.ok(report.errors.some(error => error.includes('sharedUiPins must be an array when declared')))
})

