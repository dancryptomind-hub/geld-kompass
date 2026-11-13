// Opening workbook sales must not expose unfinished Plus/report checkout paths.
const {chromium}=require('playwright'),fs=require('fs');
(async()=>{const b=await chromium.launch();try{
 const base=process.env.GK_TEST_BASE||'http://127.0.0.1:8799';
 const source=fs.readFileSync('billing-config.js','utf8');
 for(const plus of [false,true]){
  const c=await b.newContext({serviceWorkers:'block',viewport:{width:390,height:844}}),p=await c.newPage();let checkout=0;
  const cfg=source.replace(/enabled: (true|false)/,'enabled: true').replace(/plusEnabled: (true|false)/,'plusEnabled: '+plus);
  await p.route('**/billing-config.js*',r=>r.fulfill({contentType:'application/javascript',body:cfg}));
  await p.route('**/billing-checkout',r=>{checkout++;return r.fulfill({status:503,body:'{}',contentType:'application/json',headers:{'access-control-allow-origin':'*'}});});
  await p.goto(base+'/app/?lang=de#plus');await p.locator('#plusGo').waitFor();
  const disabled=await p.locator('#plusGo').isDisabled();
  if(disabled===plus)throw Error('Plus gate wrong while workbook enabled: '+plus);
  if(!plus)await p.screenshot({path:'/tmp/gk-workbook-only-plus-closed.png',fullPage:true});
  if(!plus){await p.evaluate(()=>document.querySelector('#plusForm').dispatchEvent(new Event('submit',{bubbles:true,cancelable:true})));if(checkout)throw Error('Closed Plus sends checkout');}
  await p.evaluate(()=>{const state=JSON.parse(localStorage.getItem('geldkompass.v3')||'{}');state.mode='own';localStorage.setItem('geldkompass.v3',JSON.stringify(state));});
  await p.goto(base+'/app/?lang=de&wb_check=own#data');
  await p.locator('#frCard').filter({hasText:'Dein Freiheits-Report'}).waitFor();
  if(!(await p.locator('#frCard').innerText()).includes('Bald erhältlich'))throw Error('Own-data state did not load');
  const report=await p.locator('[data-fr-buy]').count();
  if(report)throw Error('Unfinished report checkout exposed');
  if(!plus)await p.locator('#frCard').screenshot({path:'/tmp/gk-workbook-only-report-closed.png'});
  await c.close();console.log('PASS workbook enabled, Plus '+plus+', report closed');
 }
}finally{await b.close();}})().catch(e=>{console.error(e);process.exit(1)});
