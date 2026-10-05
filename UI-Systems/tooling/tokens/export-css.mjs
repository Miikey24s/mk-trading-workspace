import { createHash } from 'node:crypto'
import { readFile, writeFile } from 'node:fs/promises'
import path from 'node:path'
import process from 'node:process'

function usage() {
  throw new Error('usage: node tooling/tokens/export-css.mjs <manifest.json> --out <snapshot.css>')
}

const args = process.argv.slice(2)
const manifestArg = args[0]
const outIndex = args.indexOf('--out')
if (!manifestArg || outIndex < 0 || !args[outIndex + 1]) usage()

const manifestPath = path.resolve(manifestArg)
const manifestDir = path.dirname(manifestPath)
const outputPath = path.resolve(args[outIndex + 1])
const manifestRaw = await readFile(manifestPath)
const manifest = JSON.parse(manifestRaw.toString('utf8'))

function tokenValue(document, tokenPath) {
  const node = tokenPath.split('.').reduce((current, key) => current?.[key], document)
  if (!node || typeof node.$value !== 'string') {
    throw new Error('missing string token: ' + tokenPath)
  }
  return node.$value
}

const sourceFiles = [{ relative: path.basename(manifestPath), raw: manifestRaw }]
const modes = []
for (const [modeName, mode] of Object.entries(manifest.modes)) {
  const absolute = path.resolve(manifestDir, mode.file)
  const raw = await readFile(absolute)
  sourceFiles.push({ relative: mode.file, raw })
  modes.push({ modeName, selector: mode.selector, document: JSON.parse(raw.toString('utf8')) })
}

const componentStyles = []
for (const component of manifest.components ?? []) {
  const contractPath = path.resolve(manifestDir, component.contractFile)
  const stylePath = path.resolve(manifestDir, component.styleFile)
  const contractRaw = await readFile(contractPath)
  const styleRaw = await readFile(stylePath)
  sourceFiles.push({ relative: component.contractFile, raw: contractRaw })
  sourceFiles.push({ relative: component.styleFile, raw: styleRaw })
  componentStyles.push(styleRaw.toString('utf8').trim())
}

const hash = createHash('sha256')
for (const source of sourceFiles) {
  hash.update(source.relative.replaceAll('\\', '/'))
  hash.update('\0')
  hash.update(source.raw)
  hash.update('\0')
}
const sourceSha256 = hash.digest('hex')

const blocks = modes.map(({ selector, document }) => {
  const declarations = Object.entries(manifest.cssVariables)
    .map(([tokenPath, cssVariable]) => '  ' + cssVariable + ': ' + tokenValue(document, tokenPath) + ';')
    .join('\n')
  return selector + ' {\n' + declarations + '\n}'
})

const snapshot = [
  '/* annam-ui: ' + manifest.name + '@' + manifest.version + '; source-sha256: ' + sourceSha256 + '; generated: deterministic */',
  ...blocks,
  ...componentStyles,
  '',
].join('\n\n')

await writeFile(outputPath, snapshot, 'utf8')
process.stdout.write(JSON.stringify({
  name: manifest.name,
  version: manifest.version,
  sourceSha256,
  output: outputPath,
}) + '\n')
