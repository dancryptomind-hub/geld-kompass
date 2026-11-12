/* Wie im Buch („Wie viel ist genug?“): Bedarf aus dem Vermögen = Ausgaben − Einnahmen von außerhalb des Vermögens.
   Zinsen und Dividenden decken einen Teil davon und werden nicht doppelt abgezogen. Helga: 2.580 − 1.250 Rente = 1.330 €. */
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 900 } });await require('./plus-preview')(p); const errs = []; p.on('pageerror', e => errs.push(e.message)); const bad = [];
  await p.goto('http://localhost:8765/app/?lang=de'); await p.waitForTimeout(500);
  await p.evaluate(() => { const S = JSON.parse(localStorage.getItem('geldkompass.v3') || '{}'); S.mode = 'demo'; S.profile = 'helga'; localStorage.setItem('geldkompass.v3', JSON.stringify(S)); localStorage.setItem('geld-kompass-currency', 'EUR'); localStorage.setItem('gk-tour', JSON.stringify({ off: 1, done: 1 })); });
  await p.goto('http://localhost:8765/app/?lang=de&s=1#stress'); await p.waitForTimeout(2500);
  const dr = await p.evaluate(() => { const x = document.querySelector('.stdraw'); return x ? x.innerText.replace(/\s+/g, ' ') : ''; });
  if (!/Du lebst vom Vermögen: 1\.330 € pro Monat/.test(dr)) bad.push('Bedarf aus dem Vermögen nicht 1.330 €: ' + dr.slice(0, 160));
  if (!/1\.154 € aus Verkäufen/.test(dr)) bad.push('Verkäufe nicht 1.154 €: ' + dr.slice(0, 200));
  const wd = await p.evaluate(() => { const x = document.querySelector('.wdplan'); return x ? x.innerText.replace(/\s+/g, ' ') : ''; });
  if (!/Dein Bedarf aus dem Vermögen: 1\.330 €/.test(wd)) bad.push('Entnahmeplan: Bedarf nicht 1.330 €');
  await p.goto('http://localhost:8765/app/?lang=de&o=1#overview'); await p.waitForTimeout(1500);
  const fl = await p.evaluate(() => document.getElementById('flowInsight').innerText.replace(/\s+/g, ' '));
  if (!/1\.154 € im Monat kommen im Schnitt aus dem Vermögen/.test(fl)) bad.push('Übersicht: Lücke nicht 1.154 €: ' + fl.slice(0, 120));
  if (errs.length) bad.push('JS-Fehler: ' + errs.join(' | '));
  await b.close();
  if (bad.length) { console.error('FEHLER:\n' + bad.join('\n')); process.exit(1); }
  console.log('OK capital-need');
})();
