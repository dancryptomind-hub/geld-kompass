/* Independent browser contract checks: the approved amounts and URLs are literal fixtures. */
const assert=require('node:assert/strict');
const {chromium,webkit}=require('playwright');
module.exports=async function(){
 const b=await (process.env.GK_TEST_BROWSER==='webkit'?webkit:chromium).launch();
 const expected={offer:['cIxQo-Xjki8teco','eBtVofz-S2LN06I',39],professional:['9X8ex7Pmhl3odzA','0-8F2xEeYpop_j4',79],business:['PzKOsnQNGVKkWWM','ZI40RxbNtwrhNXs',199],agency:['55fP7X4zWIbfSAg','n_WNk78aPCp8nM4',399]};
 const base=process.env.GK_TEST_BASE||'http://localhost:8765';
 try{
 for(const lang of ['de','en'])for(const width of [320,390,820,1440]){
  const c=await b.newContext({viewport:{width,height:1000},serviceWorkers:'block'});
  await c.route('**/*',r=>r.request().url().startsWith(base)?r.continue():r.abort());
  const p=await c.newPage();const errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.clock.install({time:new Date('2026-11-28T12:00:00Z')});
  await p.goto(base+(lang==='de'?'/einbinden/':'/en/embed/')+'?lang='+lang,{waitUntil:'domcontentloaded',timeout:90000});
  await p.locator('[data-wise=professional][aria-disabled=false]').waitFor();
  assert.equal(await p.locator('[data-wise=agency]').getAttribute('href'),null);
  await p.locator('#ebAgencyConsent').check();
  for(const [idx,interval] of ['mo','yr'].entries()){
   await p.locator('[data-ebbill='+interval+']').click();
   for(const [key,[mo,yr,amount]] of Object.entries(expected)){
    const a=p.locator('[data-wise='+key+']');
    assert.equal(await a.getAttribute('href'),'https://wise.com/pay/r/'+[mo,yr][idx]);
    assert.ok((await a.innerText()).includes(String(amount*(idx?12:1))));
   }
   assert.equal(await p.locator('[data-ebbill='+interval+']').getAttribute('aria-pressed'),'true');
   assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true,lang+' '+width+' overflow');
   if(process.env.GK_EMBED_SCREENSHOTS){await p.locator('#ebPricing').scrollIntoViewIfNeeded();await p.screenshot({path:process.env.GK_EMBED_SCREENSHOTS+'/'+lang+'-'+width+'-'+interval+'.png',fullPage:true});}
  }
  await p.locator('#ebAgencyConsent').uncheck();assert.equal(await p.locator('[data-wise=agency]').getAttribute('href'),null);
  for(const [instant,visible] of [['2026-11-26T22:59:59Z',false],['2026-11-26T23:00:00Z',true],['2026-12-07T22:59:59Z',true],['2026-12-07T23:00:00Z',false],['2026-12-19T22:59:59Z',false],['2026-12-19T23:00:00Z',true],['2027-01-01T22:59:59Z',true],['2027-01-01T23:00:00Z',false]]){
   await p.clock.setSystemTime(new Date(instant));
   await p.locator('[data-ebbill=mo]').click();
   assert.equal(await p.locator('#gk-seasonal-offer').isVisible(),visible,instant);
   assert.equal(!!(await p.locator('[data-wise=offer]').getAttribute('href')),visible,instant+' offer href');
  }
  assert.deepEqual(errors,[]);await c.close();
 }
 console.log('Embed EUR: DE/EN, 4 widths, monthly/yearly, eight exact links, Agency consent, all Berlin campaign boundaries passed.');
 }finally{await b.close();}
};
if(require.main===module)module.exports().catch(e=>{console.error(e);process.exit(1);});
