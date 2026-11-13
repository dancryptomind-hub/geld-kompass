const {chromium,webkit}=require('playwright');
(async()=>{
 const browser=await (process.env.GK_TEST_BROWSER==='webkit'?webkit:chromium).launch();
 const base=process.env.GK_TEST_BASE||'http://127.0.0.1:8799';
 const failed=[];
 try{
 for(const lang of ['de','en'])for(const scenario of ['failed','refunded','disputed','flagged','network','pending','foreign']){
  const c=await browser.newContext({viewport:{width:390,height:844},serviceWorkers:'block'}),p=await c.newPage();let calls=0,recovered=false;
  await p.addInitScript(()=>{const real=window.setTimeout;window.setTimeout=(fn,ms,...args)=>real(fn,ms===1500||ms===4000?0:ms,...args);});
  await p.route('**/billing-status?*',r=>{calls++;if(recovered)return r.fulfill({contentType:'application/json',headers:{'access-control-allow-origin':'*'},body:JSON.stringify({kind:'gk_workbook_de',status:'paid',download:'https://example.com/workbook.pdf'})});if(scenario==='network')return r.abort('failed');return r.fulfill({contentType:'application/json',headers:{'access-control-allow-origin':'*'},body:JSON.stringify({kind:scenario==='foreign'?'other_product':'gk_workbook_de',status:scenario==='foreign'?'paid':scenario==='pending'?'open':scenario,download:scenario==='foreign'?'https://example.com/foreign.pdf':undefined})});});
  await p.goto(base+'/plus/danke/?lang='+lang+'&session_id=cs_live_'+'x'.repeat(30));
  if(['network','pending'].includes(scenario))await p.waitForFunction(()=>!document.querySelector('#thxState .spin'),null,{timeout:5000}).catch(()=>{});
  else await p.waitForTimeout(500);
  const text=await p.locator('#thxState').innerText(),links=await p.locator('#thxState a').allTextContents();
  if(lang==='en'&&(await p.locator('main').innerText()).includes('Zahlungsbeleg'))failed.push({lang,scenario,error:'Receipt sentence remains German'});
  const patterns={failed:lang==='de'?/fehlgeschlagen/:/failed/i,refunded:lang==='de'?/erstattet/:/refunded/i,disputed:lang==='de'?/strittig/:/disputed/i,flagged:lang==='de'?/geprüft/:/review/i,network:lang==='de'?/erneut versuchen/i:/try again/i,pending:lang==='de'?/erneut versuchen/i:/try again/i,foreign:lang==='de'?/zuordnen/:/identify/i};
  if(!patterns[scenario].test(text)||await p.locator('#thxState .spin').count()||await p.locator('#thxState a[href*="foreign.pdf"]').count())failed.push({lang,scenario,text,calls,links});
  else console.log('PASS',lang,scenario);
  if(['network','pending'].includes(scenario)){
   recovered=true;await p.locator('#thxRetry').click();await p.locator('#thxState a[href*="workbook.pdf"]').waitFor({timeout:5000});console.log('PASS',lang,scenario,'recovery to paid download');
   await p.screenshot({path:'/tmp/gk-delivery-'+lang+'-paid.png',fullPage:true});
  }else if(scenario==='disputed')await p.screenshot({path:'/tmp/gk-delivery-'+lang+'-disputed.png',fullPage:true});
  await c.close();
 }
 }finally{await browser.close();}
 if(failed.length)throw new Error(JSON.stringify(failed,null,2));
})().catch(e=>{console.error(e);process.exit(1)});
