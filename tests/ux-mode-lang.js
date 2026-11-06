/* Bedienung: Sprache bleibt gewählt (Links ?lang=… überschreiben sie nicht), Umschalten Beispiel/eigene Zahlen bleibt auf der Seite,
   Eingabefenster pausiert die Tour, Beispiel wechselt beim Öffnen, Beispiele komplett ausblendbar. */
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 900 } }); const errs = []; p.on('pageerror', e => errs.push(e.message));
  const bad = [];
  await p.goto('http://localhost:8765/app/'); await p.waitForTimeout(800);
  await p.evaluate(() => { localStorage.clear(); localStorage.setItem('geld-kompass-lang', 'de'); localStorage.setItem('gk-tour', JSON.stringify({ off: 1, done: 1 })); });
  await p.goto('http://localhost:8765/app/?quelle=app&lang=en'); await p.waitForTimeout(1200);
  if (await p.evaluate(() => window.GK_LANG) !== 'de') bad.push('Startlink mit ?lang=en hat die gewählte Sprache Deutsch überschrieben');
  // Umschalten bleibt auf der Seite
  for (const pg of ['assets', 'nomad', 'stress']) {
    await p.goto('http://localhost:8765/app/?lang=de&s=' + pg + '#' + pg); await p.waitForTimeout(1000);
    await p.evaluate(() => { const S = JSON.parse(localStorage.getItem('geldkompass.v3')); S.onboarded = 1; localStorage.setItem('geldkompass.v3', JSON.stringify(S)); });
    await p.reload(); await p.waitForTimeout(1000);
    const before = await p.evaluate(() => document.querySelector('.page.on') && document.querySelector('.page.on').id);
    await p.click('#modeBtn', { force: true }); await p.waitForTimeout(500);
    await p.click('#modeBtn', { force: true }); await p.waitForTimeout(500);
    const after = await p.evaluate(() => document.querySelector('.page.on') && document.querySelector('.page.on').id);
    if (before !== after) bad.push('Umschalten springt von ' + before + ' nach ' + after);
  }
  // Tour pausiert, wenn das Eingabefenster aufgeht
  await p.evaluate(() => { localStorage.removeItem('geldkompass.v3'); localStorage.setItem('gk-tour', JSON.stringify({ step: 0 })); });
  await p.goto('http://localhost:8765/app/?lang=de&tour=1'); await p.waitForTimeout(2000);
  const tourOn = await p.evaluate(() => document.querySelector('#gkTour.on') !== null);
  await p.click('#modeBtn', { force: true }); await p.waitForTimeout(600);
  const st = await p.evaluate(() => ({ dlg: document.getElementById('onbDlg').open, tour: document.querySelector('#gkTour.on') !== null, lock: document.documentElement.classList.contains('gt-lock') }));
  if (!tourOn || !st.dlg || st.tour || st.lock) bad.push('Eingabefenster und Tour blockieren sich: ' + JSON.stringify({ tourOn, ...st }));
  await p.fill('#onbInc', '2800'); await p.click('#onbForm button[type=submit]'); await p.waitForTimeout(500);
  if (await p.evaluate(() => document.getElementById('onbDlg').open)) bad.push('Eingabefenster schließt nicht');
  // Beispiel wechselt beim Öffnen
  await p.evaluate(() => { localStorage.removeItem('geldkompass.v3'); localStorage.setItem('gk-tour', JSON.stringify({ off: 1, done: 1 })); });
  const seen = new Set();
  for (let i = 0; i < 3; i++) { await p.goto('http://localhost:8765/app/?lang=de&rotate=1&i=' + i); await p.waitForTimeout(900); seen.add(await p.evaluate(() => JSON.parse(localStorage.getItem('geldkompass.v3')).profile)); }
  if (seen.size < 3) bad.push('Beispiel wechselt beim Öffnen nicht: ' + [...seen]);
  // Beispiele ausblenden
  await p.goto('http://localhost:8765/app/?lang=de&x=data#data'); await p.waitForTimeout(900);
  await p.check('#noDemoChk', { force: true }); await p.waitForTimeout(500);
  await p.goto('http://localhost:8765/app/?lang=de&rotate=1&x=2'); await p.waitForTimeout(900);
  const nd = await p.evaluate(() => ({ mode: JSON.parse(localStorage.getItem('geldkompass.v3')).mode, nav: !!document.querySelector('#navGroups [data-page="examples"]'), btn: document.getElementById('modeBtn').hidden }));
  if (nd.mode !== 'own' || nd.nav || !nd.btn) bad.push('Beispiele lassen sich nicht ausblenden: ' + JSON.stringify(nd));
  await b.close();
  if (bad.length || errs.length) { console.error('Bedienung FEHLER', bad, errs); process.exit(1); }
  console.log('Bedienung: Sprache bleibt, Umschalten bleibt auf Depot/Nomaden/Stresstest, Eingabefenster pausiert Tour, Beispiel wechselt, Beispiele ausblendbar');
})();
