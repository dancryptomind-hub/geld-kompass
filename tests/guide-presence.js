const assert=require('node:assert/strict');
const BT=require(process.env.PLAYWRIGHT_MODULE||'playwright')[process.env.GK_BROWSER||'chromium'];
const BASE=process.env.BASE||'http://localhost:8765';
(async()=>{const b=await BT.launch();try{for(const lang of ['de','en']){
const c=await b.newContext({viewport:{width:390,height:850},serviceWorkers:'block'});
await c.route('**/*',r=>r.request().url().startsWith(BASE)?r.continue():r.abort());
const p=await c.newPage();const errors=[];p.on('pageerror',e=>errors.push(e.message));
await p.clock.install();await p.goto(BASE+'/app/?lang='+lang+'#bookings');await p.waitForTimeout(300);
const root=p.locator('#gkGuide');assert.equal(await root.getAttribute('data-guide-presence'),'ready');
await p.clock.fastForward(13000);
await p.locator('#gkGuide.gg-resting').waitFor();assert.equal(await p.locator('#gkGuideBtn').isVisible(),false);
assert.equal(await p.evaluate(()=>localStorage.getItem('gk-guide-hidden')),null,'automatic retreat is not permanent hiding');
await p.locator('.gg-tab').click();await p.locator('#gkGuideBtn').waitFor({state:'visible'});
await p.locator('#gkGuideBtn').click();await p.clock.fastForward(20000);
assert.equal(await p.locator('#gkGuideMenu').isVisible(),true,'active menu stays available');
await p.keyboard.press('Escape');await p.clock.fastForward(500);assert.equal(await p.locator('#gkGuideBtn').isVisible(),false);
assert.deepEqual(errors,[]);await c.close();console.log(lang+': retreats automatically, returns on request, stays while in use, Escape dismisses');
}}finally{await b.close()}})().catch(e=>{console.error(e);process.exitCode=1});
