const assert = require('node:assert/strict');
const BT = require(process.env.PLAYWRIGHT_MODULE || 'playwright')[process.env.GK_BROWSER || 'chromium'];
const BASE = process.env.BASE || 'http://localhost:8765';
(async () => {
  const browser = await BT.launch();
  try {
    for (const lang of ['de','en']) for (const width of [320,1440]) {
      const ctx = await browser.newContext({viewport:{width,height:900},serviceWorkers:'block'});
      await ctx.route('**/*', r => new URL(r.request().url()).origin === new URL(BASE).origin ? r.continue() : r.abort());
      const page = await ctx.newPage(), errors = [];
      page.on('pageerror', e => errors.push(e.message));
      await page.goto(BASE+'/app/?lang='+lang+'#overview');
      const button = page.locator('#gkGuideBtn');
      await button.waitFor();
      assert.equal(await button.locator('svg.wanderer').count(),1,'chosen wanderer replaces coin');
      const image = button.locator('image').first();
      const url = await image.getAttribute('href');
      const res = await ctx.request.get(BASE+url);
      assert.equal(res.status(),200); assert.ok((await res.body()).length>8000);
      assert.ok(!/Kompi/.test(await button.getAttribute('aria-label')));
      const rect = await button.boundingBox();
      assert.ok(rect.height>rect.width,'full figure stays in portrait proportions');
      await button.click();
      await page.locator('#gkGuideMenu').waitFor({state:'visible'});
      assert.equal(await button.getAttribute('aria-expanded'),'true');
      assert.ok(!/Kompi/.test(await page.locator('#gkGuideMenu').innerText()));
      await page.waitForTimeout(400);
      await page.screenshot({path:'/tmp/gk-wanderer-'+lang+'-'+width+'.png'});
      await button.click();
      const box=await button.boundingBox();
      await page.mouse.move(box.x+box.width/2,box.y+box.height/2);
      await page.mouse.down(); await page.mouse.move(Math.max(50,box.x-120),200,{steps:12}); await page.mouse.up();
      assert.ok(await page.evaluate(()=>localStorage.getItem('gk-guide-pos')),'dragged position saved');
      await page.waitForTimeout(450); await button.click();
      await page.locator('[data-gt="hide"]').click();
      await page.locator('.gg-tab').waitFor({state:'visible'});
      assert.equal(await button.isVisible(),false);
      await page.reload(); await page.locator('.gg-tab').click();
      await button.waitFor({state:'visible'});
      const restored=await button.boundingBox();
      assert.ok(restored.y>=0 && restored.y+restored.height<=900,'restored figure stays fully visible');
      await button.click(); await page.locator('[data-gt="start"]').click();
      await page.locator('#gkTour.on .gt-av .wanderer').waitFor();
      await page.waitForTimeout(1200);
      await page.screenshot({path:'/tmp/gk-wanderer-tour-'+lang+'-'+width+'.png'});
      await ctx.close();
      assert.deepEqual(errors,[]);
      console.log(lang+' '+width+': transparent wanderer, open, drag, hide, restore and tutorial avatar');
    }
    const ctx=await browser.newContext({viewport:{width:390,height:850},reducedMotion:'reduce'});
    const p=await ctx.newPage();await p.goto(BASE+'/app/?lang=de#overview');
    await p.locator('.wanderer').first().waitFor();
    const active=await p.locator('.wanderer').first().evaluate(e=>e.getAnimations({subtree:true}).filter(a=>a.playState==='running').length);
    assert.equal(active,0,'reduced motion disables all character animation');
    await ctx.close();
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
