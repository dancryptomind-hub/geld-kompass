/* 24 Monate Kontoauszug (Wise-Format) importieren: alle Umsätze kommen an, Miete/Dividenden werden erkannt,
   der Monatsbericht lässt sich bis zum ersten importierten Monat zurückklicken und zeigt dort die richtigen Zahlen.
   Eine Depot-Dividende, die auch im Kontoauszug steht, zählt nur einmal. */
const { chromium } = require('playwright');
const pad = n => String(n).padStart(2, '0');
(async () => {
  const now = new Date(); const months = [];
  for (let k = 23; k >= 0; k--) { const d = new Date(now.getFullYear(), now.getMonth() - k, 1); months.push(d.getFullYear() + '-' + pad(d.getMonth() + 1)); }
  const dmy = (ym, day) => pad(day) + '-' + ym.slice(5, 7) + '-' + ym.slice(0, 4);
  let csv = '"TransferWise ID",Date,"Date Time",Amount,Currency,Description,"Payment Reference","Running Balance","Exchange From","Exchange To","Exchange Rate","Payer Name","Payee Name","Payee Account Number",Merchant,"Card Last Four Digits","Card Holder Full Name",Attachment,Note,"Total fees","Exchange To Amount"\n';
  let n = 0; const today = now.toISOString().slice(0, 10);
  months.forEach((ym, i) => {
    const add = (day, amt, desc, payer, payee) => { if (ym + '-' + pad(day) > today) return; n++; csv += `T-${i}-${day},${dmy(ym, day)},"${dmy(ym, day)} 10:00:00.000",${amt.toFixed(2)},EUR,"${desc}",,0,,,,"${payer || ''}","${payee || ''}",,,,,,,0.00,\n`; };
    add(1, 2000, 'Received money from Firma GmbH Gehalt', 'Firma GmbH');
    add(1, -900, 'Sent money to Vermieter', '', 'Vermieter');
    add(3, 650, 'Mieteinnahme Wohnung Leipzig', 'Mieter Schulz');
    add(5, -120.5, 'Card transaction REWE', '', 'REWE');
    if ([3, 6, 9, 12].includes(+ym.slice(5, 7))) add(15, 40, 'Dividende Allianz', 'Depotbank');
  });
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 900 } }); const errs = []; p.on('pageerror', e => errs.push(e.message)); const bad = [];
  await p.goto('http://localhost:8765/app/?lang=de'); await p.waitForTimeout(600);
  await p.evaluate(() => { const S = JSON.parse(localStorage.getItem('geldkompass.v3') || '{}'); S.mode = 'own'; S.onboarded = 1; S.calc = {}; S.own = { entries: [], debts: [], hold: [], items: [] }; localStorage.setItem('geldkompass.v3', JSON.stringify(S)); localStorage.setItem('gk-tour', JSON.stringify({ off: 1, done: 1 })); localStorage.setItem('geld-kompass-currency', 'EUR'); });
  await p.goto('http://localhost:8765/app/?lang=de#bookings'); await p.waitForTimeout(1200);
  await p.evaluate(() => { document.getElementById('bankCard').open = true; });
  await p.setInputFiles('#bankFile', { name: 'wise_2jahre.csv', mimeType: 'text/csv', buffer: Buffer.from(csv, 'utf8') }); await p.waitForTimeout(900);
  const out = await p.evaluate(() => document.getElementById('bankOut').innerText);
  if (!new RegExp(n + ' Umsätze gefunden').test(out)) bad.push('Import: erwartet ' + n + ' Umsätze: ' + out.slice(0, 160));
  const cats = await p.evaluate(() => [...document.querySelectorAll('#bankOut tbody tr')].map(tr => tr.innerText.replace(/\s+/g, ' ').slice(0, 40) + '=' + tr.querySelector('[data-bcat]').value));
  if (!cats.some(x => /Mieter Schulz/.test(x) && /=Mieteinnahmen$/.test(x))) bad.push('Mieteinnahme nicht erkannt');
  if (!cats.some(x => /Firma GmbH/.test(x) && /=Gehalt$/.test(x))) bad.push('Gehalt nicht erkannt');
  if (!cats.some(x => /Depotbank/.test(x) && /=Zinsen & Dividenden$/.test(x))) bad.push('Dividende nicht erkannt');
  await p.click('[data-bank="go"]'); await p.waitForTimeout(800);
  // Depot-Position mit derselben Dividende im ältesten Quartalsmonat → darf nicht doppelt zählen
  const q = months.find(m => [3, 6, 9, 12].includes(+m.slice(5, 7)));
  await p.evaluate(q => { const S = JSON.parse(localStorage.getItem('geldkompass.v3')); S.own.hold = [{ id: 'h1', s: 'ALV.DE', qty: 2, buy: 250, tx: [{ d: q + '-15', k: 'div', a: 46 }] }]; S.calc.mr = q; localStorage.setItem('geldkompass.v3', JSON.stringify(S)); }, q);
  await p.goto('http://localhost:8765/app/?lang=de&r=1#overview'); await p.waitForTimeout(1500);
  const num = s => { const m = s.match(/Einnahmen\s*([\d.]+)\s€/); return m ? +m[1].replace(/\./g, '') : NaN; };
  let mr = await p.evaluate(() => document.getElementById('mrCard').innerText);
  if (num(mr) !== 2690) bad.push('Quartalsmonat ' + q + ': Einnahmen ' + num(mr) + ' statt 2.690 (Gehalt + Miete + Dividende einmal): ' + mr.slice(0, 200).replace(/\n/g, ' | '));
  // bis zum ersten Monat zurück, davor gesperrt
  await p.selectOption('#mrCard [data-mrpick]', months[0]); await p.waitForTimeout(600);
  mr = await p.evaluate(() => document.getElementById('mrCard').innerText);
  const exp0 = 2650 + ([3, 6, 9, 12].includes(+months[0].slice(5, 7)) ? 40 : 0);
  if (num(mr) !== exp0) bad.push('Erster Monat ' + months[0] + ': Einnahmen ' + num(mr) + ' statt ' + exp0);
  const dis = await p.evaluate(() => document.querySelector('#mrCard [data-mr="-1"]').disabled);
  if (!dis) bad.push('Vormonat-Knopf vor dem ersten Datenmonat nicht gesperrt');
  const opts = await p.evaluate(() => document.querySelectorAll('#mrCard [data-mrpick] option').length);
  if (opts !== 24) bad.push('Monatsauswahl hat ' + opts + ' statt 24 Monate');
  // einen Monat vor: Knopf funktioniert
  await p.click('#mrCard [data-mr="1"]'); await p.waitForTimeout(500);
  const sel = await p.evaluate(() => document.querySelector('#mrCard [data-mrpick]').value);
  if (sel !== months[1]) bad.push('Weiter-Knopf: ' + sel + ' statt ' + months[1]);
  if (errs.length) bad.push('JS-Fehler: ' + errs.join(' | '));
  await b.close();
  if (bad.length) { console.error('FEHLER:\n' + bad.join('\n')); process.exit(1); }
  console.log('OK history-report (' + n + ' Umsätze, 24 Monate)');
})();
