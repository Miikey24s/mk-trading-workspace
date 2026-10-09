// Existing string tokens remain byte-compatible with pinned snapshots.
export function cssTokenValue(document, tokenPath, visited = new Set()) {
  if (visited.has(tokenPath)) throw new Error(`cyclic token reference: ${tokenPath}`)
  const parts = tokenPath.split('.')
  let node = document, type
  for (const key of parts) {
    type = node?.$type || type
    node = node?.[key]
  }
  type = node?.$type || type
  if (!node || !('$value' in node)) throw new Error(`missing token: ${tokenPath}`)
  const value = node.$value
  if (typeof value === 'string') {
    const reference = value.match(/^\{([^{}]+)\}$/)
    if (!reference) return value
    return cssTokenValue(document, reference[1], new Set([...visited, tokenPath]))
  }
  if (type === 'number' && Number.isFinite(value)) return String(value)
  if ((type === 'dimension' || type === 'duration') && Number.isFinite(value?.value)) {
    const units = type === 'dimension' ? ['px', 'rem'] : ['ms', 's']
    if (units.includes(value.unit)) return `${value.value}${value.unit}`
  }
  if (type === 'cubicBezier' && Array.isArray(value) && value.length === 4 && value.every(Number.isFinite)) {
    return `cubic-bezier(${value.join(', ')})`
  }
  throw new Error(`unsupported CSS token: ${tokenPath}`)
}
