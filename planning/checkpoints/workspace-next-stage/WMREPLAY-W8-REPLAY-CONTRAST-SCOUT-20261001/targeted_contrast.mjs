import { chromium } from '../../../../projects/mt5-tradingview-backtester/foundation_v2/web/node_modules/playwright/index.mjs'
import { writeFile } from 'node:fs/promises'
import path from 'node:path'
const dir = path.resolve('planning/checkpoints/workspace-next-stage/WMREPLAY-W8-REPLAY-CONTRAST-SCOUT-20261001')
const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' })
const page = await context.newPage()
const url = 'http://127.0.0.1:5173/?workspace=tenant-a&view=replay&surface=workspace&session=replay-fixture&dataset=ui-live-fixture&cursor=4&mode=Practice&area=testing&section=dashboard'
const errors=[]
page.on('pageerror', (e)=>errors.push(String(e)))
page.on('console', (m)=>{if(m.type()==='error') errors.push(m.text())})
await page.goto(url,{waitUntil:'networkidle'})
await page.locator('[data-testid="replay-chart"]').waitFor({state:'visible',timeout:15000})
const evaluateTheme = async (theme) => {
  if (theme==='light') { await page.getByTestId('theme-toggle').click(); await page.locator('[data-testid="fxreplay-shell"][data-theme="light"]').waitFor() }
  return page.evaluate(() => {
    const parse=(value)=>{const m=String(value).match(/rgba?\(([^)]+)\)/i);if(!m)return null;const n=m[1].split(',').map(Number.parseFloat);if(n.length<3||n.slice(0,3).some((x)=>!Number.isFinite(x)))return null;const a=n.length>3&&Number.isFinite(n[3])?n[3]:1;return {r:n[0],g:n[1],b:n[2],a}}
    const lum=(c)=>[c.r,c.g,c.b].map((x)=>{const q=x/255;return q<=.03928?q/12.92:((q+.055)/1.055)**2.4}).reduce((s,x,i)=>s+x*[.2126,.7152,.0722][i],0)
    const contrast=(fg,bg)=>{if(!fg||!bg)return null;const a=lum(fg),b=lum(bg);return Number(((Math.max(a,b)+.05)/(Math.min(a,b)+.05)).toFixed(3))}
    const visible=(node)=>{const s=getComputedStyle(node),r=node.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0'&&r.width>0&&r.height>0}
    const bgFor=(element)=>{for(let n=element;n;n=n.parentElement){const s=getComputedStyle(n);const c=parse(s.backgroundColor);if(c&&c.a>0)return {color:c,css:s.backgroundColor,owner:n.className||n.tagName.toLowerCase()}}return {color:parse(getComputedStyle(document.body).backgroundColor)||{r:255,g:255,b:255,a:1},css:getComputedStyle(document.body).backgroundColor,owner:'body-fallback'}}
    const path=(node)=>{const parts=[];for(let n=node;n&&n!==document.body;n=n.parentElement){let part=n.tagName.toLowerCase();if(n.id)part+='#'+n.id;const cls=typeof n.className==='string'?n.className.trim().split(/\s+/).filter(Boolean):[];if(cls.length)part+='.'+cls.slice(0,3).join('.');parts.unshift(part)}return parts.join(' > ')}
    const candidates=[...document.querySelectorAll('body *')].filter(visible).filter((n)=>n.children.length===0&&n.textContent?.trim()).map((node)=>{const s=getComputedStyle(node),bg=bgFor(node),fg=parse(s.color),r=node.getBoundingClientRect();return {text:node.textContent.trim().replace(/\s+/g,' ').slice(0,140),selector:path(node),classes:String(node.className||''),tag:node.tagName.toLowerCase(),color:s.color,background:bg.css,backgroundOwner:bg.owner,ratio:contrast(fg,bg.color),fontSize:s.fontSize,fontWeight:s.fontWeight,rect:{x:Number(r.x.toFixed(1)),y:Number(r.y.toFixed(1)),width:Number(r.width.toFixed(1)),height:Number(r.height.toFixed(1))}}}).filter((x)=>x.ratio!==null&&x.ratio<4.5)
    const selected={}
    for(const selector of ['.chart-symbol-ohlc','.chart-symbol-strip > span:not(.chart-symbol-ohlc)','.replay-evidence-strip > span','.replay-evidence-strip > div strong','.bar-readout-label','.bar-readout-time','.chart-bottom-cursor','.chart-bottom-status','.chart-bottom-status strong','.chart-badge','.unsupported-tools button:disabled','.unsupported-tools button:disabled span','.cutoff-readout small']){
      selected[selector]=[...document.querySelectorAll(selector)].filter(visible).map((node)=>{const s=getComputedStyle(node),bg=bgFor(node),fg=parse(s.color),r=node.getBoundingClientRect();return {text:node.textContent.trim().replace(/\s+/g,' '),color:s.color,background:bg.css,backgroundOwner:bg.owner,ratio:contrast(fg,bg.color),opacity:s.opacity,fontSize:s.fontSize,fontWeight:s.fontWeight,rect:{x:Number(r.x.toFixed(1)),y:Number(r.y.toFixed(1)),width:Number(r.width.toFixed(1)),height:Number(r.height.toFixed(1))}}})
    }
    return {appTheme:document.querySelector('[data-testid="fxreplay-shell"]')?.getAttribute('data-theme'),minimum:candidates[0]?.ratio??null,belowAA:candidates.sort((a,b)=>a.ratio-b.ratio).slice(0,40),selected,viewport:{width:innerWidth,height:innerHeight},overflowX:document.documentElement.scrollWidth-innerWidth}
  })
}
const report={url,errors,themes:[]}
for(const theme of ['dark','light']){const data=await evaluateTheme(theme);report.themes.push({theme,...data});await page.screenshot({path:path.join(dir, `replay-${theme}-1440.png`),fullPage:true})}
await writeFile(path.join(dir, 'targeted-runtime.json'),JSON.stringify(report,null,2)+'\n')
console.log(JSON.stringify({errors, themes:report.themes.map((t)=>({theme:t.theme,appTheme:t.appTheme,minimum:t.minimum,belowAA:t.belowAA.slice(0,8),selected:Object.fromEntries(Object.entries(t.selected).map(([k,v])=>[k,v.map((x)=>({text:x.text,color:x.color,background:x.background,backgroundOwner:x.backgroundOwner,ratio:x.ratio}))])),overflowX:t.overflowX}))},null,2))
await browser.close()

