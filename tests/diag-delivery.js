const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const base='http://localhost:8765';
for(const lang of ['de']){const c=await b.newContext({viewport:{width:390,height:844},serviceWorkers:'block'}),p=await c.newPage();let calls=0;const log=[];
p.on('console',m=>log.push('console '+m.type()+': '+m.text().slice(0,200)));p.on('pageerror',e=>log.push('pageerror '+e.message));p.on('requestfailed',r=>log.push('failed '+r.url().slice(0,120)+' '+(r.failure()||{}).errorText));
await p.addInitScript(()=>{const real=window.setTimeout;window.setTimeout=(fn,ms,...args)=>real(fn,ms===1500||ms===4000?0:ms,...args);});
await p.route('**/billing-status?*',r=>{calls++;return r.abort('failed');});
p.on('request',r=>{if(/billing/.test(r.url()))log.push('req '+r.url().slice(0,160));});
await p.goto(base+'/plus/danke/?lang='+lang+'&session_id=cs_live_'+'x'.repeat(30));
for(let t=0;t<12;t++){await p.waitForTimeout(1000);console.log('t='+t+' calls='+calls+' state='+JSON.stringify((await p.locator('#thxState').innerText()).slice(0,140)));}
console.log(log.slice(0,40).join('\n'));await c.close();}
await b.close();})();
