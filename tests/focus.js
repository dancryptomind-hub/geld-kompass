/* Die App passt sich der Lage an: nur Schulden → keine Dividenden-/Depot-Werkzeuge; vermögend → weniger Schulden-Werkzeuge. */
const { chromium } = require('playwright');
const exp = { peter: 'normal', rob: 'debt', luisa: 'debt', samir: 'debt', viktor: 'wealth', helga: 'wealth' };
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 900 } }); const errs = []; p.on('pageerror', e => errs.push(e.message)); const bad = [];
  await p.goto('http://localhost:8765/app/?lang=de'); await p.waitForTimeout(500);
  for (const [k, f] of Object.entries(exp)) {
    await p.evaluate(k => { const S = JSON.parse(localStorage.getItem('geldkompass.v3') || '{}'); S.mode = 'demo'; S.profile = k; localStorage.setItem('geldkompass.v3', JSON.stringify(S)); localStorage.setItem('gk-tour', JSON.stringify({ off: 1, done: 1 })); }, k);
    await p.goto('http://localhost:8765/app/?lang=de&f=' + k + '#assets'); await p.waitForTimeout(1300);
    const r = await p.evaluate(() => { const v = id => getComputedStyle(document.getElementById(id)).display !== 'none'; return { f: document.documentElement.dataset.focus, cal: v('cashflowBox'), tax: v('taxBox'), letter: v('letterCard'), refi: v('refiCard'), nav: [...document.querySelectorAll('[data-page="debts"]')].some(x => getComputedStyle(x).display !== 'none') }; });
    if (r.f !== f) bad.push(k + ': Fokus ' + r.f + ' statt ' + f);
    if (f === 'debt' && (r.cal || r.tax)) bad.push(k + ': Dividenden-Kalender/Steuer sichtbar trotz nur Schulden');
    if (f !== 'debt' && !r.cal) bad.push(k + ': Dividenden-Kalender fehlt');
    if (f === 'wealth' && (r.letter || r.refi)) bad.push(k + ': Gläubigerbrief/Umschulden sichtbar trotz Vermögen');
    if (f !== 'wealth' && !r.letter) bad.push(k + ': Gläubigerbrief fehlt');
    if (k === 'helga' && r.nav) bad.push('helga: Schulden-Bereich sichtbar obwohl keine Schulden');
    if (k === 'viktor' && !r.nav) bad.push('viktor: Baufinanzierung muss im Schulden-Bereich bleiben');
  }
  if (errs.length) bad.push('JS-Fehler: ' + errs.join(' | '));
  await b.close();
  if (bad.length) { console.error('FEHLER:\n' + bad.join('\n')); process.exit(1); }
  console.log('OK focus');
})();
