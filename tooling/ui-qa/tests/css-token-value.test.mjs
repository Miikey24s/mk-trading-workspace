import test from 'node:test'
import assert from 'node:assert/strict'
import { cssTokenValue } from '../../../UI-Systems/tooling/tokens/css-value.mjs'

test('portable typed tokens resolve to CSS without changing existing string values', () => {
  const tokens={ color:{$type:'color',old:{$value:'#fff'}}, dimension:{$type:'dimension',control:{$value:{value:36,unit:'px'}}},
    duration:{$type:'duration',hover:{$value:{value:120,unit:'ms'}}}, easing:{$type:'cubicBezier',enter:{$value:[0.16,1,0.3,1]}},
    alias:{$value:'{dimension.control}'}, weight:{$type:'number',$value:500} }
  assert.equal(cssTokenValue(tokens,'color.old'),'#fff')
  assert.equal(cssTokenValue(tokens,'alias'),'36px')
  assert.equal(cssTokenValue(tokens,'duration.hover'),'120ms')
  assert.equal(cssTokenValue(tokens,'easing.enter'),'cubic-bezier(0.16, 1, 0.3, 1)')
  assert.equal(cssTokenValue(tokens,'weight'),'500')
})
test('missing, cyclic and malformed tokens cannot silently generate CSS', () => {
  const tokens={a:{$value:'{b}'},b:{$value:'{a}'},bad:{$type:'dimension',$value:{value:36,unit:'banana'}}}
  for (const path of ['missing','a','bad']) assert.throws(() => cssTokenValue(tokens,path))
})
