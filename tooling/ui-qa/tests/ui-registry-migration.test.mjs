import { createHash } from 'node:crypto'
import { mkdtemp, mkdir, readFile, rm, writeFile, cp } from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'
import test from 'node:test'
import assert from 'node:assert/strict'
import { auditUiRegistry } from '../ui-registry-check.mjs'

const workspace = path.resolve(import.meta.dirname, '../../..')
const systemsRoot = path.resolve(workspace, '..', 'UI-Systems')
function tokenLeaves(document, prefix = []) {
  const leaves = new Map()
  for (const [key, value] of Object.entries(document)) {
    const pathParts = [...prefix, key]
    if (value && typeof value === 'object' && '$value' in value) {
      leaves.set(pathParts.join('.'), value.$value)
    } else if (value && typeof value === 'object') {
      for (const [leafPath, leafValue] of tokenLeaves(value, pathParts)) {
        leaves.set(leafPath, leafValue)
      }
    }
  }
  return leaves
}

async function sha256File(filePath) {
  return createHash('sha256').update(await readFile(filePath)).digest('hex')
}

async function copyConsumerFixture(sourceProject, fixtureProject) {
  await mkdir(path.dirname(fixtureProject), { recursive: true })
  await cp(sourceProject, fixtureProject, { recursive: true })
}

test('1.1.0 keeps existing token values compatible with 1.0.0', async () => {
  const baseDir = path.join(systemsRoot, 'core', 'tokens', 'productivity')
  const [baseLight, baseDark, candidateLight, candidateDark] = await Promise.all([
    readFile(path.join(baseDir, '1.0.0', 'light.tokens.json'), 'utf8'),
    readFile(path.join(baseDir, '1.0.0', 'dark.tokens.json'), 'utf8'),
    readFile(path.join(baseDir, '1.1.0', 'light.tokens.json'), 'utf8'),
    readFile(path.join(baseDir, '1.1.0', 'dark.tokens.json'), 'utf8'),
  ])

  for (const [mode, baseRaw, candidateRaw] of [
    ['light', baseLight, candidateLight],
    ['dark', baseDark, candidateDark],
  ]) {
    const baseLeaves = tokenLeaves(JSON.parse(baseRaw))
    const candidateLeaves = tokenLeaves(JSON.parse(candidateRaw))
    for (const [tokenPath, value] of baseLeaves) {
      assert.equal(
        candidateLeaves.get(tokenPath),
        value,
        `${mode} token changed across the additive 1.0.0 -> 1.1.0 candidate: ${tokenPath}`,
      )
    }
  }
})

test('candidate migration and rollback preserve VI/MT5 1.0.0 pins', async () => {
  const fixtureWorkspace = await mkdtemp(path.join(os.tmpdir(), 'tw-ui-registry-migration-'))
  const candidateProject = path.join(fixtureWorkspace, 'projects', 'candidate-productivity')
  const evidenceDir = path.join(fixtureWorkspace, 'evidence')
  const originalConsumerFiles = [
    path.join(workspace, 'projects', 'mt5-tradingview-backtester', 'ui', 'project-ui.json'),
    path.join(workspace, 'projects', 'vi-dubber', 'ui', 'project-ui.json'),
    path.join(workspace, 'projects', 'mt5-tradingview-backtester', 'foundation_v2', 'web', 'src', 'ui-system.snapshot.css'),
    path.join(workspace, 'projects', 'vi-dubber', 'frontend', 'src', 'ui-system.snapshot.css'),
  ]
  const originalHashes = new Map()
  try {
    for (const file of originalConsumerFiles) originalHashes.set(file, await sha256File(file))

    await copyConsumerFixture(
      path.join(workspace, 'projects', 'mt5-tradingview-backtester', 'ui'),
      path.join(fixtureWorkspace, 'projects', 'mt5-tradingview-backtester', 'ui'),
    )
    await copyConsumerFixture(
      path.join(workspace, 'projects', 'vi-dubber', 'ui'),
      path.join(fixtureWorkspace, 'projects', 'vi-dubber', 'ui'),
    )
    await mkdir(path.join(fixtureWorkspace, 'projects', 'mt5-tradingview-backtester', 'foundation_v2', 'web', 'src'), { recursive: true })
    await mkdir(path.join(fixtureWorkspace, 'projects', 'vi-dubber', 'frontend', 'src'), { recursive: true })
    await Promise.all([
      cp(
        path.join(workspace, 'projects', 'mt5-tradingview-backtester', 'foundation_v2', 'web', 'src', 'ui-system.snapshot.css'),
        path.join(fixtureWorkspace, 'projects', 'mt5-tradingview-backtester', 'foundation_v2', 'web', 'src', 'ui-system.snapshot.css'),
      ),
      cp(
        path.join(workspace, 'projects', 'vi-dubber', 'frontend', 'src', 'ui-system.snapshot.css'),
        path.join(fixtureWorkspace, 'projects', 'vi-dubber', 'frontend', 'src', 'ui-system.snapshot.css'),
      ),
    ])

    await mkdir(evidenceDir, { recursive: true })
    await writeFile(path.join(evidenceDir, 'presentation-state-contract.md'), '# Presentation state contract fixture\n')
    await writeFile(
      path.join(evidenceDir, 'productivity-1.1.0-focused-receipt.json'),
      JSON.stringify({
        schemaVersion: 1,
        status: 'focused-candidate-fixture',
        checks: ['state availability freshness certainty', 'keyboard focus', 'theme light dark'],
        evidence: 'State availability, freshness and certainty are explicit. Keyboard focus is visible. Light and dark theme fixtures are covered.',
      }),
    )

    const candidateSnapshot = path.join(
      systemsRoot,
      'core',
      'tokens',
      'productivity',
      '1.1.0',
      'ui-system.snapshot.css',
    )
    const candidateSnapshotPath = path.join(candidateProject, 'ui', 'ui-system.snapshot.css')
    await mkdir(path.dirname(candidateSnapshotPath), { recursive: true })
    await cp(candidateSnapshot, candidateSnapshotPath)

    const candidateHeader = (await readFile(candidateSnapshot, 'utf8')).split('\n', 1)[0]
    const sourceSha256 = candidateHeader.match(/source-sha256: ([a-f0-9]{64})/i)?.[1]
    assert.ok(sourceSha256, 'candidate snapshot must carry a source SHA-256')
    await writeFile(
      path.join(candidateProject, 'ui', 'project-ui.json'),
      JSON.stringify({
        schemaVersion: 1,
        status: 'candidate-migration',
        sharedUiPins: [{
          system: 'annam-productivity',
          version: '1.1.0',
          sourceSha256,
          snapshot: 'ui/ui-system.snapshot.css',
          scope: ['presentation-state.fixture'],
          contractRef: { path: 'workspace:evidence/presentation-state-contract.md' },
          focusedReceipt: { path: 'workspace:evidence/productivity-1.1.0-focused-receipt.json' },
        }],
      }, null, 2),
    )

    const migrated = await auditUiRegistry({ workspace: fixtureWorkspace, systemsRoot })
    assert.equal(migrated.status, 'ok')
    assert.equal(migrated.summary.pinCount, 3)
    const migratedPins = migrated.projects.flatMap(project => project.sharedUiPins.map(pin => ({ project: project.project, ...pin })))
    assert.deepEqual(
      migratedPins.filter(pin => pin.project.includes('mt5-tradingview-backtester') || pin.project === 'projects/vi-dubber')
        .map(pin => pin.version),
      ['1.0.0', '1.0.0'],
    )
    assert.equal(migratedPins.find(pin => pin.project === 'projects/candidate-productivity')?.version, '1.1.0')

    await rm(candidateProject, { recursive: true, force: true })
    const rolledBack = await auditUiRegistry({ workspace: fixtureWorkspace, systemsRoot })
    assert.equal(rolledBack.status, 'ok')
    assert.equal(rolledBack.summary.pinCount, 2)
    assert.ok(rolledBack.projects.every(project => !project.project.includes('candidate-productivity')))
    const rolledBackPins = rolledBack.projects.flatMap(project => project.sharedUiPins)
    assert.deepEqual(rolledBackPins.map(pin => pin.version), ['1.0.0', '1.0.0'])
  } finally {
    await rm(fixtureWorkspace, { recursive: true, force: true })
    for (const [file, expectedHash] of originalHashes) {
      assert.equal(await sha256File(file), expectedHash, `migration fixture mutated source consumer: ${file}`)
    }
  }
})

test('candidate manifest carries contract and focused receipt references', async () => {
  const fixtureWorkspace = await mkdtemp(path.join(os.tmpdir(), 'tw-ui-registry-manifest-gate-'))
  const fixtureSystemsRoot = path.join(fixtureWorkspace, 'UI-Systems')
  const candidateProject = path.join(fixtureWorkspace, 'projects', 'candidate-productivity')
  const candidateSource = path.join(systemsRoot, 'core', 'tokens', 'productivity', '1.1.0')
  const candidateTarget = path.join(fixtureSystemsRoot, 'core', 'tokens', 'productivity', '1.1.0')
  const contractSource = path.join(systemsRoot, 'core', 'contracts', 'presentation-state', '1.0.0')
  const contractTarget = path.join(fixtureSystemsRoot, 'core', 'contracts', 'presentation-state', '1.0.0')
  const componentSource = path.join(systemsRoot, 'components', 'button', '1.0.0')
  const componentTarget = path.join(fixtureSystemsRoot, 'components', 'button', '1.0.0')
  const receiptRelative = path.join(
    'planning',
    'checkpoints',
    'workspace-next-stage',
    'UI-ECOSYSTEM-PRESENTATION-STATE-2026-09-28',
    'receipt.json',
  )
  try {
    await Promise.all([
      cp(candidateSource, candidateTarget, { recursive: true }),
      cp(contractSource, contractTarget, { recursive: true }),
      cp(componentSource, componentTarget, { recursive: true }),
      cp(
        path.join(workspace, receiptRelative),
        path.join(fixtureWorkspace, receiptRelative),
        { recursive: false },
      ),
    ])
    const candidateSnapshot = path.join(candidateTarget, 'ui-system.snapshot.css')
    const candidateSnapshotPath = path.join(candidateProject, 'ui', 'ui-system.snapshot.css')
    await mkdir(path.dirname(candidateSnapshotPath), { recursive: true })
    await cp(candidateSnapshot, candidateSnapshotPath)
    const candidateHeader = (await readFile(candidateSnapshot, 'utf8')).split('\n', 1)[0]
    const sourceSha256 = candidateHeader.match(/source-sha256: ([a-f0-9]{64})/i)?.[1]
    assert.ok(sourceSha256, 'candidate snapshot must carry a source SHA-256')

    await writeFile(
      path.join(candidateProject, 'ui', 'project-ui.json'),
      JSON.stringify({
        schemaVersion: 1,
        status: 'candidate-migration',
        sharedUiPins: [{
          system: 'annam-productivity',
          version: '1.1.0',
          sourceSha256,
          snapshot: 'ui/ui-system.snapshot.css',
          scope: ['presentation-state.fixture'],
        }],
      }, null, 2),
    )

    const report = await auditUiRegistry({ workspace: fixtureWorkspace, systemsRoot: fixtureSystemsRoot })
    assert.equal(report.status, 'ok')
    assert.equal(report.summary.pinCount, 1)
    assert.equal(report.projects[0].sharedUiPins[0].version, '1.1.0')
  } finally {
    await rm(fixtureWorkspace, { recursive: true, force: true })
  }
})
