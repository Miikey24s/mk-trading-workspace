import { createHash } from 'node:crypto'
import { readdir, readFile, stat } from 'node:fs/promises'
import path from 'node:path'
import process from 'node:process'
import { fileURLToPath } from 'node:url'

const DEFAULT_WORKSPACE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..')

function sha256(value) {
  return createHash('sha256').update(value).digest('hex')
}
function normalizePath(value) {
  return value.replaceAll('\\', '/')
}

function isInside(parent, candidate) {
  const relative = path.relative(path.resolve(parent), path.resolve(candidate))
  return relative === '' || (relative !== '..' && !relative.startsWith(`..${path.sep}`) && !path.isAbsolute(relative))
}

async function exists(file) {
  try {
    await stat(file)
    return true
  } catch {
    return false
  }
}

async function walk(root, predicate) {
  const found = []
  async function visit(directory) {
    let entries
    try {
      entries = await readdir(directory, { withFileTypes: true })
    } catch {
      return
    }
    for (const entry of entries) {
      if (entry.name === '.git' || entry.name === 'node_modules' || entry.name === 'dist' || entry.name === '__pycache__') continue
      const candidate = path.join(directory, entry.name)
      if (entry.isDirectory()) await visit(candidate)
      else if (predicate(candidate, entry.name)) found.push(candidate)
    }
  }
  await visit(root)
  return found.sort()
}

async function readSourceGraph(manifestPath) {
  const manifestRaw = await readFile(manifestPath)
  const manifest = JSON.parse(manifestRaw.toString('utf8'))
  const manifestDir = path.dirname(manifestPath)
  const sources = [{ relative: path.basename(manifestPath), raw: manifestRaw }]
  const modes = []
  for (const [modeName, mode] of Object.entries(manifest.modes || {})) {
    if (!mode || typeof mode.file !== 'string' || typeof mode.selector !== 'string') {
      throw new Error(`invalid mode declaration: ${modeName}`)
    }
    const file = path.resolve(manifestDir, mode.file)
    if (!isInside(manifestDir, file) && !isInside(path.resolve(manifestDir, '..', '..', '..', '..'), file)) {
      throw new Error(`mode file escapes token package: ${mode.file}`)
    }
    const raw = await readFile(file)
    sources.push({ relative: normalizePath(mode.file), raw })
    modes.push({ modeName, selector: mode.selector, document: JSON.parse(raw.toString('utf8')) })
  }

  const components = []
  for (const component of manifest.components || []) {
    if (!component || typeof component.contractFile !== 'string' || typeof component.styleFile !== 'string') {
      throw new Error('invalid component declaration')
    }
    const contractPath = path.resolve(manifestDir, component.contractFile)
    const stylePath = path.resolve(manifestDir, component.styleFile)
    const contractRaw = await readFile(contractPath)
    const styleRaw = await readFile(stylePath)
    sources.push({ relative: normalizePath(component.contractFile), raw: contractRaw })
    sources.push({ relative: normalizePath(component.styleFile), raw: styleRaw })
    components.push(styleRaw.toString('utf8').trim())
  }

  const sourceHash = createHash('sha256')
  for (const source of sources) {
    sourceHash.update(normalizePath(source.relative))
    sourceHash.update('\0')
    sourceHash.update(source.raw)
    sourceHash.update('\0')
  }

  return { manifest, manifestDir, modes, components, sourceSha256: sourceHash.digest('hex') }
}

function tokenValue(document, tokenPath) {
  const node = tokenPath.split('.').reduce((current, key) => current?.[key], document)
  if (!node || typeof node.$value !== 'string') throw new Error(`missing string token: ${tokenPath}`)
  return node.$value
}

function renderSnapshot(graph) {
  const blocks = graph.modes.map(({ selector, document }) => {
    const modeDeclarations = Object.entries(graph.manifest.cssVariables || {})
      .map(([tokenPath, cssVariable]) => `  ${cssVariable}: ${tokenValue(document, tokenPath)};`)
      .join('\n')
    return `${selector} {\n${modeDeclarations}\n}`
  })
  // Keep this header and block ordering byte-for-byte compatible with the
  // canonical exporter.
  return [
    `/* annam-ui: ${graph.manifest.name}@${graph.manifest.version}; source-sha256: ${graph.sourceSha256}; generated: deterministic */`,
    ...blocks,
    ...graph.components,
    '',
  ].join('\n\n')
}

async function discoverManifests(systemsRoot) {
  const manifests = await walk(path.join(systemsRoot, 'core', 'tokens'), (file, name) => name === 'manifest.json')
  const result = new Map()
  for (const file of manifests) {
    try {
      const graph = await readSourceGraph(file)
      const key = `${graph.manifest.name}@${graph.manifest.version}`
      if (result.has(key)) throw new Error(`duplicate token manifest ${key}`)
      result.set(key, { file, graph })
    } catch (error) {
      // Keep malformed manifests discoverable as a normal validation error
      // instead of hiding them from a registry audit.
      result.set(`__invalid__${file}`, { file, error })
    }
  }
  return result
}

function resolveProjectRoot(configPath) {
  return path.dirname(path.dirname(configPath))
}

function resolveSnapshot(projectRoot, snapshot) {
  if (typeof snapshot !== 'string' || !snapshot.trim() || path.isAbsolute(snapshot)) return null
  const resolved = path.resolve(projectRoot, snapshot)
  return isInside(projectRoot, resolved) ? resolved : null
}

function resolveReference(reference, manifestDir, workspace) {
  const value = typeof reference === 'string' ? reference : reference?.path
  if (!value || typeof value !== 'string') return null
  if (path.isAbsolute(value)) return path.resolve(value)
  if (value.startsWith('workspace:')) return path.resolve(workspace, value.slice('workspace:'.length))
  return path.resolve(manifestDir, value)
}

async function validateCandidateGate({ pin, graph, workspace }) {
  if (graph.manifest.status !== 'candidate') return []
  const errors = []
  const contract = pin.contractRef || graph.manifest.contractRef || graph.manifest.contract
  const receipt = pin.focusedReceipt || graph.manifest.focusedReceipt || graph.manifest.promotionReceipt
  const contractPath = resolveReference(contract, graph.manifestDir, workspace)
  if (!contractPath || !(await exists(contractPath))) {
    errors.push('candidate requires an existing token contract reference (`contractRef.path`)')
  }
  const receiptPath = resolveReference(receipt, graph.manifestDir, workspace)
  if (!receiptPath || !(await exists(receiptPath))) {
    errors.push('candidate requires an existing focused promotion receipt (`focusedReceipt.path`)')
    return errors
  }
  const rawChecks = receipt?.checks || receipt?.coverage || graph.manifest.promotionChecks || []
  const metadataChecks = Array.isArray(rawChecks) ? rawChecks : []
  const declared = new Set(metadataChecks.map(value => String(value).toLowerCase()))
  const content = (await readFile(receiptPath, 'utf8')).toLowerCase()
  const required = {
    state: ['state', 'availability', 'freshness', 'certainty'],
    keyboard: ['keyboard', 'focus'],
    theme: ['theme', 'light', 'dark'],
  }
  for (const [name, needles] of Object.entries(required)) {
    const declaredMatch = !declared.size || needles.some(needle => [...declared].some(value => value.includes(needle)))
    const contentMatch = needles.some(needle => content.includes(needle))
    if (!declaredMatch || !contentMatch) errors.push(`candidate receipt is missing focused ${name} QA evidence`)
  }
  return errors
}

async function validatePin({ pin, projectRoot, manifestRegistry, workspace }) {
  const errors = []
  const scope = Array.isArray(pin?.scope) ? pin.scope.filter(value => typeof value === 'string' && value.trim()) : []
  if (!pin || typeof pin !== 'object') return { errors: ['sharedUiPins entry must be an object'], scope, adoption: 'invalid' }
  for (const field of ['system', 'version', 'sourceSha256', 'snapshot']) {
    if (typeof pin[field] !== 'string' || !pin[field].trim()) errors.push(`pin.${field} is required`)
  }
  if (!scope.length) errors.push('pin.scope must contain at least one non-empty scope')
  if (typeof pin.sourceSha256 === 'string' && !/^[a-f0-9]{64}$/i.test(pin.sourceSha256)) errors.push('pin.sourceSha256 must be a SHA-256 hex string')
  if (errors.length) return { errors, scope, adoption: 'invalid' }

  const key = `${pin.system}@${pin.version}`
  const entry = manifestRegistry.get(key)
  if (!entry) {
    errors.push(`token manifest not found: ${key}`)
    return { errors, scope, adoption: 'invalid' }
  }
  if (entry.error) {
    errors.push(`token manifest is invalid: ${entry.error.message}`)
    return { errors, scope, adoption: 'invalid' }
  }
  const { graph } = entry
  if (pin.sourceSha256.toLowerCase() !== graph.sourceSha256) errors.push(`source hash drift for ${key}: pin=${pin.sourceSha256} actual=${graph.sourceSha256}`)
  const snapshotPath = resolveSnapshot(projectRoot, pin.snapshot)
  if (!snapshotPath) {
    errors.push('pin.snapshot must be a project-relative path that stays inside the project')
  } else if (!(await exists(snapshotPath))) {
    errors.push(`snapshot does not exist: ${pin.snapshot}`)
  } else {
    const actual = await readFile(snapshotPath)
    const expected = Buffer.from(renderSnapshot(graph), 'utf8')
    if (!actual.equals(expected)) errors.push(`snapshot content drift for ${key}: ${sha256(actual)} != ${sha256(expected)}`)
  }
  errors.push(...await validateCandidateGate({ pin, graph, workspace }))
  return {
    errors,
    system: pin.system,
    version: pin.version,
    scope,
    snapshot: pin.snapshot,
    snapshotSha256: snapshotPath && await exists(snapshotPath) ? sha256(await readFile(snapshotPath)) : null,
    sourceSha256: graph.sourceSha256,
    adoption: 'partial',
  }
}

export async function auditUiRegistry({ workspace = DEFAULT_WORKSPACE, systemsRoot = path.resolve(workspace, '..', 'UI-Systems') } = {}) {
  const projectsRoot = path.join(workspace, 'projects')
  const configPaths = await walk(projectsRoot, (file, name) => name === 'project-ui.json' && path.basename(path.dirname(file)) === 'ui')
  const registry = await discoverManifests(systemsRoot)
  const projects = []
  const errors = []
  for (const configPath of configPaths) {
    const projectRoot = resolveProjectRoot(configPath)
    let config
    try {
      config = JSON.parse(await readFile(configPath, 'utf8'))
    } catch (error) {
      errors.push(`${configPath}: invalid JSON (${error.message})`)
      continue
    }
    // A missing pin list means the project has not adopted a shared system.
    // A present, malformed list is registry drift and must be visible instead
    // of being silently reported as `adoption: none`.
    const hasSharedUiPins = Object.prototype.hasOwnProperty.call(config, 'sharedUiPins')
    if (hasSharedUiPins && !Array.isArray(config.sharedUiPins)) {
      errors.push(`${configPath}: sharedUiPins must be an array when declared`)
    }
    const pins = Array.isArray(config.sharedUiPins) ? config.sharedUiPins : []
    const projectPins = []
    for (const pin of pins) {
      const result = await validatePin({ pin, projectRoot, manifestRegistry: registry, workspace })
      projectPins.push(result)
      for (const error of result.errors) errors.push(`${configPath}: ${error}`)
    }
    const adoption = pins.length === 0 ? 'none' : (config.globalUiSystem && config.globalUiSystemVersion ? 'declared' : 'partial')
    projects.push({ project: path.relative(workspace, projectRoot).replaceAll('\\', '/'), config: path.relative(workspace, configPath).replaceAll('\\', '/'), status: config.status || 'unknown', adoption, sharedUiPins: projectPins })
  }
  return {
    status: errors.length ? 'error' : 'ok',
    workspace: path.resolve(workspace),
    systemsRoot: path.resolve(systemsRoot),
    projects,
    summary: {
      projectCount: projects.length,
      pinCount: projects.reduce((count, project) => count + project.sharedUiPins.length, 0),
      errorCount: errors.length,
      partialProjects: projects.filter(project => project.adoption === 'partial').length,
    },
    errors,
  }
}

function parseArgs(args) {
  const options = { workspace: DEFAULT_WORKSPACE, systemsRoot: null, json: false }
  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index]
    if (arg === '--workspace') options.workspace = path.resolve(args[++index] || '')
    else if (arg === '--systems-root') options.systemsRoot = path.resolve(args[++index] || '')
    else if (arg === '--json') options.json = true
    else if (arg === '--help' || arg === '-h') options.help = true
    else throw new Error(`unknown argument: ${arg}`)
  }
  if (!options.systemsRoot) options.systemsRoot = path.resolve(options.workspace, '..', 'UI-Systems')
  return options
}

async function main(args) {
  const options = parseArgs(args)
  if (options.help) {
    console.log('ui-registry-check [--workspace PATH] [--systems-root PATH] [--json]')
    return
  }
  const report = await auditUiRegistry(options)
  console.log(JSON.stringify(report, null, 2))
  if (report.status !== 'ok') process.exitCode = 1
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main(process.argv.slice(2)).catch(error => { console.error(error.message); process.exitCode = 1 })
}

