/* Einkommensquellen (Kapitel 11): Gehalt, Miete (Immobilie), Dividenden (gebucht, 12 Monate) und Zinsen (Konto) werden nach Art gebündelt,
   als Monatsschnitt gezählt und nichts doppelt. Ohne Daten: Hinweis statt Fehler. */
const { chromium } = require('playwright'); const BASE = 'http://localhost:8765';
const pad = n => String(n).padStart(2, '0');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 900 } }); const errs = []; p.on('pageerror', e => errs.push(e.message)); const bad = [];
  const now = new Date(), ym = k => { const d = new Date(now.getFullYear(), now.getMonth() - k, 1); return d.getFullYear() + '-' + pad(d.getMonth() + 1); };
  const entries = [{ id: 'g', title: 'Gehalt', amount: 2500, type: 'income', cat: 'Gehalt', freq: 'monthly', date: ym(14) + '-01' }];
  for (let k = 2; k <= 11; k += 3) entries.push({ id: 'dv' + k, title: 'Dividende Allianz', amount: 120, type: 'income', cat: 'Zinsen & Dividenden', freq: 'once', date: ym(k) + '-15', imp: 1 });
  const tx = [{ d: ym(13) + '-01', k: 'open', a: 5000 }]; for (let k = 1; k <= 12; k++) tx.push({ d: ym(k) + '-28', k: 'int', a: 10 });
  const items = [{ id: 'i1', name: 'Tagesgeld', value: 5000, cls: 'cash', tx }, { id: 'i2', name: 'Wohnung Leipzig', value: 150000, cls: 'realestate', re: { use: 'rent', rent: 600, hg: 0, up: 0, ot: 0, since: ym(14) } }];
  await p.goto(BASE + '/app/?lang=de'); await p.waitForTimeout(600);
  const set = own => p.evaluate(own => { const S = JSON.parse(localStorage.getItem('geldkompass.v3') || '{}'); S.mode = 'own'; S.onboarded = 1; S.own = own; localStorage.setItem('geldkompass.v3', JSON.stringify(S)); localStorage.setItem('gk-tour', JSON.stringify({ off: 1, done: 1 })); localStorage.setItem('geld-kompass-currency', 'EUR'); }, own);
  await set({ entries, debts: [], hold: [], items });
  await p.goto(BASE + '/app/?lang=de&r=1#calc'); await p.waitForTimeout(1500);
  const r = await p.evaluate(() => { document.getElementById('r-einkommen').open = true; return { txt: document.getElementById('incOut').innerText }; });
  for (const w of ['Gehalt', 'Mieteinnahmen', 'Dividenden', 'Zinsen']) if (!r.txt.includes(w)) bad.push('Quelle fehlt: ' + w + ' | ' + r.txt.slice(0, 200).replace(/\n/g, ' '));
  if (!/Dividenden\s*40\s€/.test(r.txt)) bad.push('Dividenden nicht 40 € im Monatsschnitt (4 × 120 € / 12): ' + r.txt.slice(0, 200).replace(/\n/g, ' '));
  if (!/Mieteinnahmen\s*600\s€/.test(r.txt) || !/Gehalt\s*2\.500\s€/.test(r.txt)) bad.push('Gehalt/Miete falsch');
  if (!/3\.1(49|50)\s€/.test(r.txt)) bad.push('Summe nicht 2.500 + 600 + 40 + Zinsen: ' + r.txt.slice(0, 120).replace(/\n/g, ' '));
  if (!/Quellen\s*4/.test(r.txt)) bad.push('Nicht 4 Quellen');
  await set({ entries: [], debts: [], hold: [], items: [] });
  await p.goto(BASE + '/app/?lang=de&r=2#calc'); await p.waitForTimeout(1200);
  const e = await p.evaluate(() => { document.getElementById('r-einkommen').open = true; return document.getElementById('incOut').textContent; });
  if (!/Keine Einnahmen/.test(e)) bad.push('Leerer Zustand fehlt: ' + e.slice(0, 80));
  if (errs.length) bad.push('JS-Fehler: ' + errs.join(' | '));
  await b.close();
  if (bad.length) { console.error('FEHLER:\n' + bad.join('\n')); process.exit(1); }
  console.log('OK income-sources');
})();
