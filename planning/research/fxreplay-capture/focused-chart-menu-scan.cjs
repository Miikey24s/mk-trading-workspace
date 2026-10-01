const fs=require('fs'),path=require('path');
const {createRequire}=require('module');
const req=createRequire(path.resolve('D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester/foundation_v2/web/package.json'));
const {chromium}=req('playwright');
const profile='C:/Users/MIIKEY/AppData/Local/WMReplay/fxreplay-capture-profile';
const out='D:/ANNAM/FXReplayCaptures/deep-free-backtest-2026-09-30/chart-menu-focused-2026-09-30';
const url='https://app.fxreplay.com/en-US/auth/testing/v2/sessions/aad96b3f-3510-4e1a-bd33-290140058547';
fs.mkdirSync(out,{recursive:true});
const clean=s=>String(s??'').replace(/\\s+/g,' ').trim();
async function visibleControls(page){return await page.locator('button,[role="button"],[role="menuitem"],[role="option"],[role="tab"],[role="dialog"],[role="listbox"],input').evaluateAll(ns=>ns.map((n,i)=>{const r=n.getBoundingClientRect(),s=getComputedStyle(n);return {i,tag:n.tagName,role:n.getAttribute('role'),text:clean(n.innerText).slice(0,180),title:n.getAttribute('title'),aria:n.getAttribute('aria-label'),value:n.value||null,visible:!!(r.width&&r.height&&s.visibility!=='hidden'&&s.display!=='none'),rect:{x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width),h:Math.round(r.height)},cls:typeof n.className==='string'?n.className:''};}).filter(x=>x.visible));}
async function save(page,label,meta){
  const safe=label.replace(/[^a-z0-9._-]+/gi,'_');
  await page.screenshot({path:path.join(out,`${safe}.png`),fullPage:true,animations:'disabled'}).catch(()=>{});
  const text=await page.locator('body').innerText().catch(()=>''),html=await page.locator('html').evaluate(n=>n.outerHTML).catch(()=>''), controls=await visibleControls(page).catch(()=>[]);
  fs.writeFileSync(path.join(out,`${safe}.text.txt`),text); fs.writeFileSync(path.join(out,`${safe}.html`),html); fs.writeFileSync(path.join(out,`${safe}.controls.json`),JSON.stringify({label,url:page.url(),meta,controls},null,2));
  return {label,text:clean(text),controls:controls.filter(x=>x.visible)};
}
async function clickVisible(page,loc){const count=await loc.count(); for(let i=0;i<count;i++){if(await loc.nth(i).isVisible().catch(()=>false)){await loc.nth(i).click({force:true,timeout:8000});return true;}}return false;}
async function dismiss(page){await page.keyboard.press('Escape').catch(()=>{});await page.waitForTimeout(350);}
(async()=>{
 const c=await chromium.launchPersistentContext(profile,{headless:true,serviceWorkers:'block',viewport:{width:1920,height:1080},locale:'en-US'});
 const p=c.pages()[0]||await c.newPage();
 const errors=[];p.on('pageerror',e=>errors.push(clean(e.message)));p.on('console',m=>{if(m.type()==='error')errors.push(clean(m.text()));});
 await p.goto(url,{waitUntil:'domcontentloaded',timeout:60000});await p.waitForTimeout(9000);await p.locator('appcues-experience-container').evaluateAll(ns=>ns.forEach(n=>n.style.pointerEvents='none')).catch(()=>{});
 const results=[];results.push(await save(p,'00-baseline',{kind:'baseline'}));
 const cases=[
  ['interval', 'button[title="Interval"]'],
  ['chart-type', 'button[title^="Chart type:"]'],
  ['indicators','button[title="Indicators"]'],
  ['order-flow','button[title^="Order Flow"]'],
  ['analytics','button[title="Analytics"]'],
  ['compare-symbol','button[title="Compare symbol"]'],
  ['layout-options','button[title="Layout options"]'],
  ['sync-chart','button[title="Sync Chart"]'],
  ['keyboard-shortcuts','button[title="Keyboard shortcuts"]'],
  ['code-editor','button[title="Code Editor"]'],
  ['symbol-menu','button[title="Symbol menu"]'],
  ['timezone','button[title="Time zone"]'],
  ['go-to-date','button[title="Go to"]'],
  ['draw-cursors','button[aria-label="Expand Cursors tools"]'],
  ['draw-trend','button[aria-label^="Expand Trend line tools"]'],
  ['draw-fibonacci','button[aria-label^="Expand Fibonacci"]'],
  ['draw-patterns','button[aria-label^="Expand Patterns"]'],
  ['draw-projections','button[aria-label^="Expand Projections"]'],
  ['draw-shapes','button[aria-label^="Expand Geometric"]'],
  ['draw-text','button[aria-label^="Expand Text & Notes"]'],
  ['draw-emojis','button[aria-label^="Expand Emojis"]'],
  ['draw-magnet','button[aria-label="Choose magnet mode"]'],
  ['draw-hide-options','button[aria-label="Hide options"]'],
  ['draw-sync-options','button[aria-label="Sync options"]'],
  ['draw-remove-options','button[aria-label="Remove options"]'],
  ['dock-add','button[title="Dock a panel"]']
 ];
 for(const [name,selector] of cases){
   await dismiss(p);
   const ok=await clickVisible(p,p.locator(selector));
   await p.waitForTimeout(550);
   const r=await save(p,name,{selector,clicked:ok});results.push(r);
   if(!ok)errors.push(`${name}: visible control not found`);
 }
 await dismiss(p);results.push(await save(p,'99-final',{kind:'final'}));
 fs.writeFileSync(path.join(out,'focused-summary.json'),JSON.stringify({generatedAt:new Date().toISOString(),url,results:results.map(r=>({label:r.label,bodyText:r.text.slice(0,15000),overlayControls:r.controls.filter(x=>x.rect.y<550&&x.rect.x>300)})),errors},null,2));
 console.log(JSON.stringify({out,caseCount:cases.length,results:results.length,errors},null,2));
 await c.close();
})();
