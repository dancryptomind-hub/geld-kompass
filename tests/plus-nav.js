/* Ohne Plus: Plus-Seiten (Stresstest, Nomaden) stehen nicht in der Leiste, stattdessen „Plus entdecken“ mit echter Vorschau (Beispielpersonen).
   Direktaufruf #stress und ?tour=plus öffnen die Vorschau. Mit Plus: Seiten in der Leiste, „Schnellleiste anpassen“, Plus-Tour in der App. */
const { chromium } = require('playwright'); const plusPreview = require('./plus-preview.js'); const BASE = 'http://localhost:8765';
(async () => {
  const b = await chromium.launch(); const bad = []; const errs = [];
  const setup = async p => { await p.goto(BASE + '/app/?lang=de'); await p.evaluate(() => { const S = JSON.parse(localStorage.getItem('geldkompass.v3') || '{}'); S.mode = 'own'; S.onboarded = 1; localStorage.setItem('geldkompass.v3', JSON.stringify(S)); localStorage.setItem('gk-tour', JSON.stringify({ off: 1, done: 1 })); }); };
  for (const w of [1280, 390]) {
    const p = await b.newPage({ viewport: { width: w, height: 900 } }); p.on('pageerror', e => errs.push(e.message)); await setup(p);
    await p.goto(BASE + '/app/?lang=de&n=' + w + '#overview'); await p.waitForTimeout(2200);
    const nav = await p.evaluate(() => ({ pages: [...document.querySelectorAll('#navGroups [data-page]')].map(x => x.getAttribute('data-page')), mnav: [...document.querySelectorAll('#mnav [data-page]')].map(x => x.getAttribute('data-page')), demo: !!document.querySelector('#navGroups [data-plus-demo]'), labels: [...document.querySelectorAll('#navGroups .navlabel')].map(x => x.textContent) }));
    if (nav.pages.includes('stress') || nav.pages.includes('nomad') || nav.mnav.includes('stress')) bad.push(w + ': Plus-Seite ohne Plus in der Leiste ' + JSON.stringify(nav));
    if (!nav.demo) bad.push(w + ': „Plus entdecken“ fehlt');
    if (nav.labels.join('|') !== 'Mein Geld|Planen|Plus|Lernen|Einstellungen') bad.push(w + ': Gruppen ' + nav.labels.join('|'));
    if (w === 1280) {
      await p.click('#navGroups [data-plus-demo]'); await p.waitForTimeout(900);
      const d = await p.evaluate(() => { const g = document.getElementById('pdDlg'); return { open: !!(g && g.open), tabs: g ? g.querySelectorAll('.pdtabs button').length : 0, src: g && g.querySelector('iframe') ? g.querySelector('iframe').getAttribute('src') : '', cta: !!(g && g.querySelector('[data-plus-buy="demo"]')), who: g ? (g.querySelector('.pdwho') || {}).textContent : '' }; });
      if (!d.open || d.tabs !== 8 || !/plus-demo\.de\.html#stress$/.test(d.src) || !d.cta || !/Leon/.test(d.who)) bad.push('Vorschau: ' + JSON.stringify(d));
      for (let i = 1; i < 8; i++) { await p.click('#pdDlg [data-pd="next"]').catch(() => {}); await p.waitForTimeout(250); }
      const last = await p.evaluate(() => document.querySelector('#pdDlg iframe').getAttribute('src'));
      if (!/beispiel-report\.de\.html$/.test(last)) bad.push('Letzte Station nicht der Beispiel-Report: ' + last);
      const fr = await p.evaluate(async () => { const r = await fetch('/app/plus-demo.de.html'); const t = await r.text(); return ['stress', 'wd', 'cashflow', 'audit', 'tax', 'alarm', 'nomad'].filter(id => !t.includes('id="' + id + '"')); });
      if (fr.length) bad.push('Vorschau-Abschnitte fehlen: ' + fr.join(','));
      await p.click('#pdDlg [data-pd="close"]');
      await p.goto(BASE + '/app/?lang=de&s=1#stress'); await p.waitForTimeout(4200);
      const s = await p.evaluate(() => ({ page: document.querySelector('.page.on').id, open: !!(document.getElementById('pdDlg') || {}).open }));
      if (s.page !== 'p-overview' || !s.open) bad.push('#stress ohne Plus: ' + JSON.stringify(s));
      await p.goto(BASE + '/app/?lang=de&tour=plus'); await p.waitForTimeout(4500);
      if (!(await p.evaluate(() => !!(document.getElementById('pdDlg') || {}).open))) bad.push('?tour=plus öffnet keine Vorschau');
    }
    await p.close();
  }
  const c = await b.newContext({ viewport: { width: 1280, height: 900 } }); const p = await c.newPage(); p.on('pageerror', e => errs.push(e.message));
  if (await plusPreview(p)) {
    await setup(p); await p.goto(BASE + '/app/?lang=de&q=1#overview'); await p.waitForTimeout(2600);
    const nav = await p.evaluate(() => ({ pages: [...document.querySelectorAll('#navGroups [data-page]')].map(x => x.getAttribute('data-page')), demo: !!document.querySelector('#navGroups [data-plus-demo]'), mn: !!document.querySelector('#navGroups [data-goto="mnavSet"]') }));
    if (!nav.pages.includes('stress') || !nav.pages.includes('nomad') || nav.demo || !nav.mn) bad.push('Mit Plus: ' + JSON.stringify(nav));
    await p.click('#gkGuideBtn', { force: true }); await p.click('#gkGuideMenu [data-gt="plus"]', { force: true }); await p.waitForTimeout(900);
    const t = await p.evaluate(() => ({ on: document.getElementById('gkTour').classList.contains('on'), demo: !!(document.getElementById('pdDlg') || {}).open }));
    if (!t.on || t.demo) bad.push('Mit Plus: Plus-Tour startet nicht in der App ' + JSON.stringify(t));
    console.log('Plus-Teil geprüft');
  } else console.log('Plus-Teil übersprungen (kein PLUS_BUNDLE)');
  await b.close();
  if (errs.length) bad.push('JS-Fehler: ' + errs.join(' | '));
  if (bad.length) { console.error('FEHLER:\n' + bad.join('\n')); process.exit(1); }
  console.log('OK plus-nav');
})();
