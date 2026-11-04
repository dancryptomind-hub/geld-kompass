const assert=require('node:assert/strict');
const BT=require(process.env.PLAYWRIGHT_MODULE||'playwright')[process.env.GK_BROWSER||'chromium'];
const BASE=process.env.BASE||'http://localhost:8765';
(async()=>{const browser=await BT.launch();try{for(const lang of ['de','en'])for(const mode of ['valid','missing-browser','expired']){
 const c=await browser.newContext({serviceWorkers:'block'}),p=await c.newPage();let recover=0,exchanges=0,updates=0;const errors=[];p.on('pageerror',e=>errors.push(e.message));
 const user={id:'b4ed186c-f50d-4b1e-9726-b5e915b5cc77',email:'callback@example.com',email_confirmed_at:'2026-01-01T00:00:00Z',aud:'authenticated',role:'authenticated',app_metadata:{},user_metadata:{}};
 const jwt=['eyJhbGciOiJIUzI1NiJ9',Buffer.from(JSON.stringify({sub:user.id,exp:Math.floor(Date.now()/1000)+3600})).toString('base64url'),'fixture'].join('.');
 await c.addInitScript(()=>localStorage.setItem('geldkompass.v3','financial-data-must-stay-local'));
 await c.route('**/*',r=>{const url=r.request().url();if(url.includes('cwznthfefbeglamnwyry.supabase.co')){
  const body=r.request().postDataJSON();assert.ok(!JSON.stringify(body).includes('financial-data-must-stay-local'));
  let data=user,status=200;if(url.includes('/recover')){recover++;assert.ok(body.code_challenge.length>=43);data={};}
  if(url.includes('/token')){exchanges++;assert.ok(body.code_verifier.length>=43);assert.equal(body.auth_code,'fixture-code');if(mode==='expired'){status=400;data={code:'flow_state_expired',msg:'Expired test code'};}else data={access_token:jwt,refresh_token:'fixture-refresh',expires_in:3600,token_type:'bearer',user};}
  if(r.request().method()==='PUT'){updates++;assert.equal(body.password,'new-fixture-password');}
  return r.fulfill({status,headers:{'access-control-allow-origin':'*','access-control-allow-headers':'*'},json:data});
 }return url.startsWith(BASE)?r.continue():r.abort();});
 await p.goto(BASE+'/konto/?lang='+lang);await p.locator('#forgot').click();await p.locator('#email').fill(user.email);await p.locator('#submit').click();await p.locator('#status').filter({hasText:/Falls ein Konto|If an account/}).waitFor();assert.equal(recover,1);
 if(mode==='missing-browser')await p.evaluate(()=>Object.keys(localStorage).filter(k=>k.startsWith('gk.account')).forEach(k=>localStorage.removeItem(k)));
 await p.goto(BASE+'/konto/?lang='+lang+'&code=fixture-code');
 if(mode==='valid'){
  await p.locator('#submit').filter({hasText:/Neues Passwort speichern|Save new password/}).waitFor();assert.equal(exchanges,1);assert.equal(await p.locator('#signedIn').isVisible(),false);await p.reload();await p.locator('#submit').filter({hasText:/Neues Passwort speichern|Save new password/}).waitFor();await p.locator('#password').fill('new-fixture-password');await p.locator('#submit').click();await p.locator('#signedIn').waitFor({state:'visible'});assert.equal(updates,1);
 }else{
  await p.locator('#status').filter({hasText:/Einmalcode|one-time code/}).waitFor();assert.equal(await p.locator('#submit').textContent(),lang==='de'?'Code anfordern':'Request code');assert.equal(await p.locator('#signedIn').isVisible(),false);assert.equal(updates,0);assert.equal(exchanges,mode==='expired'?1:0);
 }
 assert.equal(new URL(p.url()).searchParams.has('code'),false);assert.equal(await p.evaluate(()=>localStorage.getItem('geldkompass.v3')),'financial-data-must-stay-local');assert.deepEqual(errors,[]);console.log(lang+' '+mode+': PKCE callback, password setup or explicit recovery error checked');await c.close();
}}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
