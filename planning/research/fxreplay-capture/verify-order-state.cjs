const path = require('path');
const fs = require('fs');
const { createRequire } = require('module');
const requireFromWeb = createRequire(path.resolve('D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester/foundation_v2/web/package.json'));
const { chromium } = requireFromWeb('playwright');
const profile = 'C:/Users/MIIKEY/AppData/Local/WMReplay/fxreplay-capture-profile';
const outDir = process.argv[2] || 'D:/ANNAM/FXReplayCaptures/deep-free-backtest-2026-09-30';
const url = 'https://app.fxreplay.com/en-US/auth/testing/v2/sessions/aad96b3f-3510-4e1a-bd33-290140058547';
(async()=>{
  const context=await chromium.launchPersistentContext(profile,{headless:true,serviceWorkers:'block',viewport:{width:1920,height:1080},locale:'en-US'});
  const page=context.pages()[0]||await context.newPage();
  await page.goto(url,{waitUntil:'domcontentloaded',timeout:60000}); await page.waitForTimeout(9000);
  await page.locator('appcues-experience-container').evaluateAll(ns=>ns.forEach(n=>n.style.pointerEvents='none')).catch(()=>{});
  const show=page.getByTitle('Show positions and orders'); if(await show.count()) { await show.first().click({force:true}); await page.waitForTimeout(1000); }
  const text=await page.locator('body').innerText(); fs.writeFileSync(path.join(outDir,'order-state-verify.text.txt'),text); await page.screenshot({path:path.join(outDir,'order-state-verify.png'),fullPage:true});
  console.log(JSON.stringify({hasOpenPosition:/OANDA:EURUSD\s+Buy\s+1 lot/.test(text),hasNoData:/No data available/.test(text),tail:text.slice(-4000)},null,2)); await context.close();
})();
