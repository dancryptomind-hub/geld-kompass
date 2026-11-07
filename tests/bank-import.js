/* Kontoauszug-Import (CSV): Wise (Kontoauszug + Transaktionsexport), DKB, PayPal, Soll/Haben-Spalten müssen immer erkannt werden. */
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const cases = [
  ['bank_wise_statement.csv', 4, [['2026-10-28', 12.5, 'expense', /Grab/], ['2026-10-25', 2500, 'income', /Stripe/], ['2026-10-21', 1049.99, 'expense', /Apple/], ['2026-10-03', 950, 'expense', /Condo/]]],
  ['bank_wise_transactions.csv', 3, [['2026-10-28', 12.5, 'expense', /Grab/], ['2026-10-25', 2500, 'income', /Stripe/], ['2026-10-03', 950, 'expense', /Condo/]]],
  ['bank_wise_de.csv', 2, [['2026-10-28', 12.5, 'expense', /7-Eleven/], ['2026-10-25', 500, 'income', /Payhip/]]],
  ['bank_revolut.csv', 3, [['2026-10-29', 3.5, 'expense', /7-Eleven/], ['2026-10-25', 500, 'income', /Dan/], ['2026-10-03', 950, 'expense', /Vermieter/]]],
  ['bank_revolut_2025.csv', 2, [['2026-10-29', 11.2, 'expense', /Grab/], ['2026-10-25', 1000, 'income', /Stripe/]]],
  ['bank_revolut_es.csv', 2, [['2026-10-29', 45.3, 'expense', /Mercadona/], ['2026-10-25', 500, 'income', /Nómina/]]],
  ['bank_fr.csv', 2, [['2026-10-28', 45.3, 'expense', /CARREFOUR/], ['2026-10-25', 2500, 'income', /SALAIRE/]]],
  ['bank_ohne_kopf.csv', 3, [['2026-10-28', 23.4, 'expense', /Edeka/], ['2026-10-25', 2500, 'income', /Gehalt/], ['2026-10-03', 900, 'expense', /Miete/]]],
  ['bank_excel_utf16.csv', 2, [['2026-10-28', 45.3, 'expense', /REWE/], ['2026-10-25', 2850, 'income', /Gehalt/]]],
  ['bank_dkb.csv', 2, [['2026-10-30', 45.3, 'expense', /REWE/], ['2026-10-28', 2850, 'income', /Firma/]]],
  ['bank_paypal.csv', 1, [['2026-10-29', 9.99, 'expense', /Spotify/]]],
  ['bank_soll_haben.csv', 2, [['2026-10-29', 23.4, 'expense', /TESCO/], ['2026-10-15', 2100, 'income', /SALARY/]]],
];
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 900 } }); const errs = []; p.on('pageerror', e => errs.push(e.message)); const bad = [];
  await p.goto('http://localhost:8765/app/?lang=de'); await p.waitForTimeout(600);
  await p.evaluate(() => { const S = JSON.parse(localStorage.getItem('geldkompass.v3') || '{}'); S.mode = 'own'; S.onboarded = 1; S.own = { entries: [], debts: [], hold: [], items: [] }; localStorage.setItem('geldkompass.v3', JSON.stringify(S)); localStorage.setItem('gk-tour', JSON.stringify({ off: 1, done: 1 })); });
  await p.goto('http://localhost:8765/app/?lang=de#bookings'); await p.waitForTimeout(1200);
  for (const [f, n, exp] of cases) {
    await p.evaluate(() => { const d = document.getElementById('bankCard'); if (d) d.open = true; });
    await p.setInputFiles('#bankFile', { name: f, mimeType: 'text/csv', buffer: fs.readFileSync(path.join(__dirname, 'csv', f)) }); await p.waitForTimeout(700);
    const out = await p.evaluate(() => document.getElementById('bankOut').innerText);
    if (!new RegExp(n + ' Umsätze gefunden').test(out)) { bad.push(f + ': erwartet ' + n + ' Umsätze, bekommen: ' + out.slice(0, 200).replace(/\n/g, ' | ')); continue; }
    const rows = await p.evaluate(() => [...document.querySelectorAll('#bankOut tbody tr')].map(tr => ({ t: tr.innerText, type: tr.querySelector('[data-btype]').value })));
    exp.forEach(([d, amt, type, re]) => {
      const dd = d.slice(8, 10) + '.' + d.slice(5, 7) + '.';
      const r = rows.find(x => x.t.includes(dd) && re.test(x.t));
      if (!r) bad.push(f + ': Zeile ' + d + ' ' + re + ' fehlt');
      else { if (r.type !== type) bad.push(f + ': ' + re + ' Art ' + r.type + ' statt ' + type); const t = r.t.replace(/\s/g, ''), ok = [amt, Math.round(amt), Math.round(amt / 10) * 10].some(v => t.includes(v.toLocaleString('de-DE', { maximumFractionDigits: 2 })) || t.includes(v.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 }))); if (!ok) bad.push(f + ': ' + re + ' Betrag falsch: ' + r.t.replace(/\n/g, ' ')); }
    });
    await p.evaluate(() => { const c = document.querySelector('[data-bank="cancel"]'); if (c) c.click(); });
  }
  if (errs.length) bad.push('JS-Fehler: ' + errs.join(' | '));
  await b.close();
  if (bad.length) { console.error('FEHLER:\n' + bad.join('\n')); process.exit(1); }
  console.log('OK bank-import');
})();
