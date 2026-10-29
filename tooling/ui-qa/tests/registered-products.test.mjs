import { mkdtemp, mkdir, writeFile, rm } from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'
import test from 'node:test'
import assert from 'node:assert/strict'
import { auditUiRegistry } from '../ui-registry-check.mjs'

test('registered products exclude retained runtime checkouts', async t => {
  const workspace = await mkdtemp(path.join(os.tmpdir(), 'registered-ui-'))
  t.after(() => rm(workspace, { recursive: true, force: true }))
  for (const name of ['canonical', 'retained-runtime']) {
    const directory = path.join(workspace, 'projects', name, 'ui')
    await mkdir(directory, { recursive: true })
    await writeFile(path.join(directory, 'project-ui.json'),
      name === 'canonical' ? JSON.stringify({ sharedUiPins: [] }) : '{invalid retained config')
  }
  await writeFile(path.join(workspace, '.gitmodules'),
    '[submodule "projects/canonical"]\n path = projects/canonical\n url = https://example.invalid/canonical.git\n')
  const report = await auditUiRegistry({ workspace })
  assert.equal(report.status, 'ok')
  assert.deepEqual(report.projects.map(project => project.project), ['projects/canonical'])
})

test('registered paths cannot escape the projects directory', async t => {
  const workspace = await mkdtemp(path.join(os.tmpdir(), 'registered-ui-'))
  t.after(() => rm(workspace, { recursive: true, force: true }))
  await writeFile(path.join(workspace, '.gitmodules'),
    '[submodule "escape"]\n path = projects/../../outside\n url = https://example.invalid/escape.git\n')
  await assert.rejects(auditUiRegistry({ workspace }), /escapes projects root/)
})
