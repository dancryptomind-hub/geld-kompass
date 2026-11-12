/* Prüft den Kompass-Guide: automatischer Start, alle Stationen DE/EN, Schließen + Fortsetzen, Stand gespeichert, Abschalten. */
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const bad = []; const errs = [];
  for (const [lang, w] of [['de', 1280], ['en', 390]]) {
    const c = await b.newContext({ viewport: { width: w, height: 850 } }); const p = await c.newPage(); p.on('pageerror', e => errs.push(e.message));
    await p.goto((process.env.BASE||'http://localhost:8765')+'/app/?tour=1&lang=' + lang + '#overview'); await p.waitForTimeout(2600);
    if (!await p.evaluate(() => document.getElementById('gkTour').classList.contains('on'))) bad.push(lang + ': kein Autostart');
    await p.click('[data-gt="next"]'); await p.waitForTimeout(700); await p.click('[data-gt="next"]'); await p.waitForTimeout(700);
    await p.click('[data-gt="x"]'); await p.waitForTimeout(300);
    const st = await p.evaluate(() => JSON.parse(localStorage.getItem('gk-tour'))); if (st.step !== 2) bad.push(lang + ': Stand nicht gespeichert ' + JSON.stringify(st));
    await p.click('#gkGuideBtn', { force: true }); await p.click('[data-gt="resume"]', { force: true }); await p.waitForTimeout(700);
    const t = await p.$eval('.gt-bub h3', e => e.textContent); if (!t) bad.push(lang + ': fortsetzen');
    const N = await p.evaluate(() => +document.querySelector('#gkTour .gt-prog small').textContent.split('/')[1]); if (N < 15) bad.push(lang + ': Tour zu kurz (' + N + ')');
    const pages = new Set(); for (let i = 2; i < N; i++) { pages.add(await p.evaluate(() => document.querySelector('.page.on').id)); const h = await p.$eval('.gt-bub h3', e => e.textContent); if (!h) bad.push(lang + ' Station ' + i); await p.click('[data-gt="next"]'); await p.waitForTimeout(650); }
    if (pages.size < 10) bad.push(lang + ': Tour zeigt nur ' + pages.size + ' Seiten'); const st2 = await p.evaluate(() => JSON.parse(localStorage.getItem('gk-tour'))); if (!st2.done) bad.push(lang + ': nicht als fertig gespeichert');
    await p.reload(); await p.waitForTimeout(2400); if (await p.evaluate(() => document.getElementById('gkTour') && document.getElementById('gkTour').classList.contains('on'))) bad.push(lang + ': startet nach Abschluss erneut');
    await p.click('#gkGuideBtn', { force: true }); await p.click('#gkGuideMenu [data-gt="plus"]', { force: true }); await p.waitForTimeout(800);
    const pn = await p.evaluate(() => +document.querySelector('#gkTour .gt-prog small').textContent.split('/')[1]); const ppages = new Set();
    for (let i = 0; i < pn; i++) { ppages.add(await p.evaluate(() => document.querySelector('.page.on').id)); if (i > 0 && !(await p.$('#gkTour .gt-extra [data-plus-buy]'))) bad.push(lang + ': Plus-Tour Station ' + i + ' ohne Testen-Knopf'); await p.click('[data-gt="next"]'); await p.waitForTimeout(650); }
    if (pn < 8 || !ppages.has('p-stress') || !ppages.has('p-assets')) bad.push(lang + ': Plus-Tour unvollständig ' + pn + ' ' + [...ppages]);
    await c.close();
  }
  await b.close();
  if (bad.length || errs.length) { console.error('Tour FEHLER', bad, errs); process.exit(1); }
  console.log('Kompass-Guide: Gratis-Tour über alle Seiten + Plus-Tour DE/EN, Schließen, Fortsetzen, Stand und Abschluss gespeichert');
})();
