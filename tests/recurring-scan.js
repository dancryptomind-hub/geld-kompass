/* Prüft die automatische Erkennung von Abos/Fixkosten aus einmaligen Buchungen (z. B. Kontoauszug-Import). */
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 900 } }); const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  await p.goto('http://localhost:8765/app/?lang=de#recurring'); await p.waitForTimeout(1500);
  await p.evaluate(() => {
    const S = JSON.parse(localStorage.getItem('geldkompass.v3') || '{}'); const ym = k => { const d = new Date(); d.setDate(15); d.setMonth(d.getMonth() - k); return d.toISOString().slice(0, 10); };
    const e = []; let i = 0; const add = (t, a, type, cat, k) => e.push({ id: 'x' + (i++), title: t, amount: a, type, cat, freq: 'once', date: ym(k) });
    for (let k = 0; k < 4; k++) { add('NETFLIX.COM ' + (1000 + k), 13.99, 'expense', 'Abos & Streaming', k); add('Miete Wohnung Mai ' + k, 750, 'expense', 'Wohnen & Nebenkosten', k); }
    add('Supermarkt REWE', 40, 'expense', 'Lebensmittel', 0); add('Supermarkt REWE', 95, 'expense', 'Lebensmittel', 1); add('Supermarkt REWE', 12, 'expense', 'Lebensmittel', 2);
    add('Gym Fit', 30, 'expense', 'Freizeit & Hobby', 5); add('Gym Fit', 30, 'expense', 'Freizeit & Hobby', 6); add('Gym Fit', 30, 'expense', 'Freizeit & Hobby', 7);
    S.mode = 'own'; S.onboarded = 1; S.own = S.own || {}; S.own.entries = e; S.own.debts = S.own.debts || []; S.own.items = S.own.items || []; S.own.hold = S.own.hold || [];
    localStorage.setItem('geldkompass.v3', JSON.stringify(S));
  });
  await p.reload(); await p.waitForTimeout(1500);
  const rows = await p.$$eval('#recScan .rsrow b', x => x.map(y => y.textContent));
  const ok1 = rows.length === 2 && rows.some(r => /NETFLIX/.test(r)) && rows.some(r => /Miete/.test(r));
  await p.click('[data-rsgo]'); await p.waitForTimeout(500);
  const st = await p.evaluate(() => { const S = JSON.parse(localStorage.getItem('geldkompass.v3')); return S.own.entries.filter(e => e.freq === 'monthly').map(e => e.title + '|' + e.amount + '|' + e.date.slice(0, 7)); });
  const next = await p.evaluate(() => { const d = new Date(); d.setDate(1); d.setMonth(d.getMonth() + 1); return d.toISOString().slice(0, 7); });
  const ok2 = st.length === 2 && st.every(x => x.endsWith('|' + next));
  const hidden = await p.$eval('#recScan', e => e.hidden);
  await b.close();
  if (!ok1 || !ok2 || !hidden || errs.length) { console.error('Abo-Erkennung FEHLER', { rows, st, hidden, errs }); process.exit(1); }
  console.log('Abo-Erkennung: 2 von 4 Mustern erkannt (Supermarkt und altes Abo ignoriert), monatlich ab nächstem Monat übernommen');
})();
