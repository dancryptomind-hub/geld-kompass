const {webkit,chromium}=require('playwright');
const fs=require('fs');
// Exercise the actual checkout consent expression for both payment paths.
const rule=fs.readFileSync('supabase/functions/billing-checkout/index.ts','utf8').split('\n').find(l=>l.includes('consent_collection:'));
if(!rule)throw Error('Checkout consent rule missing');
const consent=new Function('mp','Deno','return '+rule.trim().replace(/^\.\.\./,'').replace(/,$/,''));
for(const requested of ['1','0',undefined])for(const managed of [true,false]){
 const actual=consent(managed,{env:{get:()=>requested}});
 const expected=!managed&&requested==='1'?{consent_collection:{terms_of_service:'required'}}:{};
 if(JSON.stringify(actual)!==JSON.stringify(expected))throw Error('Checkout consent differs for managed='+managed+', requested='+requested);
}

(async()=>{const b=await (process.env.GK_TEST_BROWSER==='webkit'?webkit:chromium).launch();try{
const base=process.env.GK_TEST_BASE||'http://localhost:8765',cfg=fs.readFileSync('billing-config.js','utf8').replace('enabled: false','enabled: true');
for(const lang of ['de','en'])for(const width of [390,1440]){
 const c=await b.newContext({viewport:{width,height:900},serviceWorkers:'block'}),p=await c.newPage(),errors=[];
 p.on('pageerror',e=>errors.push(e.message));await p.route('**/billing-config.js*',r=>r.fulfill({contentType:'text/javascript',body:cfg}));
 await p.route('**/billing-checkout',r=>r.fulfill({contentType:'application/json',headers:{'access-control-allow-origin':'*'},body:JSON.stringify({url:'https://checkout.stripe.com/test-workbook'})}));
 await p.route('https://checkout.stripe.com/**',r=>r.fulfill({body:'<h1>Test checkout</h1>',contentType:'text/html'}));
 await p.goto(base+(lang==='de'?'/arbeitsbuch/':'/en/workbook/')+'?lang='+lang);await p.locator('#abBuy').waitFor({state:'visible'});
 const checks=await p.evaluate(()=>({pages:document.body.innerText.includes('71'),after:document.querySelector('.sample-nav').compareDocumentPosition(document.querySelector('#abBuy'))&Node.DOCUMENT_POSITION_FOLLOWING,overflow:document.documentElement.scrollWidth>innerWidth,old:document.body.innerText.includes('69 Seiten'),payhip:!!document.querySelector('a[href*="payhip"]')}));
 if(!checks.pages||!checks.after||checks.overflow||checks.old||checks.payhip||errors.length)throw new Error(JSON.stringify({lang,width,checks,errors}));
 for(const img of await p.locator('img[loading=lazy]').all()){await img.scrollIntoViewIfNeeded();await img.evaluate(el=>el.decode().catch(()=>{}));}await p.evaluate(()=>window.scrollTo(0,0));await p.screenshot({path:'/tmp/workbook-launch-'+lang+'-'+width+'.png',fullPage:true});
 await p.click('#abBuy');await p.waitForURL('https://checkout.stripe.com/**');
 await c.close();console.log('PASS',lang,width,'71 pages, placement, checkout, CSP');
}
const c=await b.newContext({serviceWorkers:'block'}),p=await c.newPage();await p.route('**/billing-config.js*',r=>r.fulfill({contentType:'text/javascript',body:cfg}));await p.route('**/billing-status?*',r=>r.fulfill({contentType:'application/json',headers:{'access-control-allow-origin':'*'},body:JSON.stringify({kind:'gk_workbook_de',status:'paid',download:'https://example.com/download.pdf'})}));await p.goto(base+'/plus/danke/?session_id=cs_test_'+'a'.repeat(30));await p.locator('#thxState a').waitFor();if(await p.locator('#trialGo').count())throw new Error('Plus trial visible');console.log('PASS paid download shown, no Plus upsell');await c.close();
}finally{await b.close();}})().catch(e=>{console.error(e);process.exit(1)});
