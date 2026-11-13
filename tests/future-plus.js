/* Plus „Zukunft & Szenarien“: Schneeball-Prognose, Was-wäre-wenn, Umzugs-Rechner, Jahresrückblick (PDF) rechnen und reagieren auf Eingaben.
   Ohne Plus: Seite nicht in der Leiste, #future öffnet die Vorschau bei der Schneeball-Prognose. */
const { chromium } = require('playwright'); const plusPreview = require('./plus-preview.js'); const BASE = 'http://localhost:8765';
(async () => {
  const b = await chromium.launch(); const bad = []; const errs = [];
  { const p = await b.newPage({ viewport: { width: 1280, height: 900 } }); p.on('pageerror', e => errs.push(e.message));
    await p.goto(BASE + '/app/?lang=de'); await p.evaluate(() => { const S = JSON.parse(localStorage.getItem('geldkompass.v3') || '{}'); S.mode = 'own'; S.onboarded = 1; localStorage.setItem('geldkompass.v3', JSON.stringify(S)); localStorage.setItem('gk-tour', JSON.stringify({ off: 1, done: 1 })); });
    await p.goto(BASE + '/app/?lang=de&f=1#future'); await p.waitForTimeout(4300);
    const r = await p.evaluate(() => ({ nav: !!document.querySelector('#navGroups [data-page="future"]'), page: document.querySelector('.page.on').id, cur: (document.querySelector('#pdDlg .pdst[aria-current] b') || {}).textContent, src: (document.querySelector('#pdDlg iframe') || {}).src }));
    if (r.nav || r.page !== 'p-overview' || r.cur !== 'Schneeball-Prognose' || !/plus-demo\.de\.html#snow$/.test(r.src || '')) bad.push('Ohne Plus: ' + JSON.stringify(r));
    await p.close(); }
  const c = await b.newContext({ viewport: { width: 1280, height: 900 } }); const p = await c.newPage(); p.on('pageerror', e => errs.push(e.message));
  if (await plusPreview(p)) {
    await p.goto(BASE + '/app/?lang=de'); await p.evaluate(() => { const S = JSON.parse(localStorage.getItem('geldkompass.v3') || '{}'); S.mode = 'demo'; S.profile = 'peter'; S.onboarded = 1; localStorage.setItem('geldkompass.v3', JSON.stringify(S)); localStorage.setItem('gk-tour', JSON.stringify({ off: 1, done: 1 })); localStorage.setItem('geld-kompass-currency', 'EUR'); });
    await p.goto(BASE + '/app/?lang=de&f=2#future'); await p.waitForTimeout(3500);
    const txt = id => p.evaluate(id => document.getElementById(id).innerText, id);
    const on = await p.evaluate(() => document.querySelector('.page.on').id); if (on !== 'p-future') bad.push('Plus: Seite nicht offen: ' + on);
    const nav = await p.evaluate(() => !!document.querySelector('#navGroups [data-page="future"]')); if (!nav) bad.push('Plus: Zukunft fehlt in der Leiste');
    const s1 = await txt('futSnow'); if (!/Schneeball-Prognose[\s\S]*deckt|trägt/.test(s1) || !/Passiv \/ Monat/i.test(s1)) bad.push('Schneeball: ' + s1.slice(0, 160));
    await p.fill('#fuSnSv', '1500'); await p.waitForTimeout(900); const s2 = await txt('futSnow'); if (s2 === s1) bad.push('Schneeball reagiert nicht auf Sparrate');
    await p.click('[data-fu-yrs="10"]'); await p.waitForTimeout(500); if (!(await p.evaluate(() => document.querySelector('[data-fu-yrs="10"]').getAttribute('aria-pressed') === 'true'))) bad.push('Schneeball: Zeitraum-Knopf');
    const sc = await txt('futScen'); if (!/Heute[\s\S]*Alles zusammen/.test(sc) || !/Jahre früher/.test(sc)) bad.push('Szenarien: ' + sc.slice(0, 200));
    const mv1 = await txt('futMove'); await p.selectOption('#fuMvTo', 'PT'); await p.waitForTimeout(700); const mv2 = await txt('futMove');
    if (!/Portugal/.test(mv2) || mv1 === mv2 || !/Umzug hat sich bezahlt/.test(mv2)) bad.push('Umzug: ' + mv2.slice(0, 200));
    const yr = await txt('futYear'); if (!/Eingenommen[\s\S]*Sparquote[\s\S]*Ziele fürs nächste Jahr/.test(yr)) bad.push('Jahresrückblick: ' + yr.slice(0, 200));
    await p.click('#fuYrPdf'); await p.waitForTimeout(600);
    const pdf = await p.evaluate(() => { const o = document.getElementById('frDlg'); return o && !o.hidden ? o.innerText.slice(0, 3000) : ''; });
    if (!/Dein Jahresrückblick[\s\S]*Monat für Monat[\s\S]*Ziele/.test(pdf)) bad.push('PDF-Ansicht: ' + pdf.slice(0, 160));
    await p.setViewportSize({ width: 360, height: 800 }); await p.click('[data-fr-close]').catch(() => {}); await p.waitForTimeout(400);
    if (await p.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1)) bad.push('Zukunft-Seite zu breit bei 360 px');
    console.log('Plus-Teil geprüft');
  } else console.log('Plus-Teil übersprungen (kein PLUS_BUNDLE)');
  await b.close();
  if (errs.length) bad.push('JS-Fehler: ' + errs.join(' | '));
  if (bad.length) { console.error('FEHLER:\n' + bad.join('\n')); process.exit(1); }
  console.log('OK future-plus');
})();
