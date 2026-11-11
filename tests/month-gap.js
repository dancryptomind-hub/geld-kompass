/* Monatslücke: ALLE Einnahmen gegen die Ausgaben. Keine Lücke, wenn Einnahmen (inkl. passiver im Monatsschnitt) die Ausgaben decken,
   Investieren erzeugt keine Lücke, echte Lücke wird mit dem richtigen Betrag gezeigt. */
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 900 } }); const errs = []; p.on('pageerror', e => errs.push(e.message)); const bad = [];
  await p.goto('http://localhost:8765/app/?lang=de'); await p.waitForTimeout(800);
  const ym = new Date().toISOString().slice(0, 7) + '-01';
  const own = (entries, extra) => p.evaluate(([entries, extra, ym]) => { const S = JSON.parse(localStorage.getItem('geldkompass.v3') || '{}'); S.mode = 'own'; S.onboarded = 1; S.own = Object.assign({ entries: entries.map((e, i) => Object.assign({ id: 'e' + i, freq: 'monthly', date: ym }, e)), debts: [], hold: [], items: [] }, extra || {}); localStorage.setItem('geldkompass.v3', JSON.stringify(S)); localStorage.setItem('gk-tour', JSON.stringify({ off: 1, done: 1 })); }, [entries, extra, ym]);
  const hero = async q => { await p.goto('http://localhost:8765/app/?lang=de&q=' + q + '#overview'); await p.waitForTimeout(1200); return p.evaluate(() => document.getElementById('hero').innerText + ' || ' + document.getElementById('insights').innerText); };
  // 1) Gehalt + Miete + Zinsen decken die Ausgaben → keine Lücke
  await own([{ title: 'Gehalt', amount: 1500, type: 'income', cat: 'Gehalt' }, { title: 'Miete Wohnung', amount: 900, type: 'income', cat: 'Mieteinnahmen' }, { title: 'Zinsen', amount: 150, type: 'income', cat: 'Zinsen & Dividenden' }, { title: 'Wohnen', amount: 2400, type: 'expense', cat: 'Wohnen & Nebenkosten' }]);
  let h = await hero('a'); if (/Monatslücke/.test(h)) bad.push('Lücke trotz gedeckter Ausgaben (passive Einnahmen zählen nicht): ' + h.slice(0, 200));
  // 2) Investieren ist keine Ausgabe → keine Lücke
  await own([{ title: 'Gehalt', amount: 3000, type: 'income', cat: 'Gehalt' }, { title: 'Wohnen', amount: 2500, type: 'expense', cat: 'Wohnen & Nebenkosten' }, { title: 'ETF', amount: 1000, type: 'invest', cat: 'Sparplan' }]);
  h = await hero('b'); if (/Monatslücke/.test(h)) bad.push('Lücke nur wegen Sparplan: ' + h.slice(0, 200));
  // 3) Echte Lücke: 2.000 Einnahmen, 2.300 Ausgaben → 300 €
  await own([{ title: 'Gehalt', amount: 1800, type: 'income', cat: 'Gehalt' }, { title: 'Dividende', amount: 200, type: 'income', cat: 'Zinsen & Dividenden' }, { title: 'Wohnen', amount: 2300, type: 'expense', cat: 'Wohnen & Nebenkosten' }]);
  h = await hero('c'); if (!/300\s€\s*\n?\s*Monatslücke/.test(h)) bad.push('Echte Lücke falsch: ' + h.slice(0, 200));
  // 4) Immobilie mit Miete (aus dem Vermögen eingetragen) zählt als Einnahme
  await own([{ title: 'Rente', amount: 1200, type: 'income', cat: 'Rente' }, { title: 'Leben', amount: 1800, type: 'expense', cat: 'Lebensmittel' }], { items: [{ id: 'i1', name: 'Wohnung Leipzig', cls: 'Immobilie', value: 200000, re: { use: 'rent', rent: 800, hg: 100, up: 50, ot: 0 } }] });
  h = await hero('d'); if (/Monatslücke/.test(h)) bad.push('Miete aus Immobilie zählt nicht als Einnahme: ' + h.slice(0, 200));
  // 5) Beispielpersonen: wo die Einnahmen die Ausgaben decken, keine Lücke
  for (const k of ['peter', 'rob', 'bella', 'luisa', 'samir', 'viktor', 'helga']) {
    await p.evaluate(k => { const S = JSON.parse(localStorage.getItem('geldkompass.v3')); S.mode = 'demo'; S.profile = k; localStorage.setItem('geldkompass.v3', JSON.stringify(S)); }, k);
    await p.goto('http://localhost:8765/app/?lang=de&p=' + k + '#overview'); await p.waitForTimeout(1100);
    const r = await p.evaluate(() => { const t = document.getElementById('kpis').innerText, n = s => +((t.match(new RegExp(s + '\\s*(-?[\\d.]+)\\s€')) || [0, 'NaN'])[1].replace(/\./g, '')); return { inc: n('Einnahmen'), sp: n('Ausgaben'), gap: /Monatslücke/.test(document.getElementById('hero').innerText) }; });
    if (r.inc >= r.sp && r.gap) bad.push(k + ': Lücke obwohl Einnahmen ' + r.inc + ' ≥ Ausgaben ' + r.sp);
  }
  // 6) Viktor: Dividenden im Monatsschnitt zählen als Einnahme (KPI, Geldfluss Rein/Raus, kein Minus)
  await p.evaluate(() => { const S = JSON.parse(localStorage.getItem('geldkompass.v3')); S.mode = 'demo'; S.profile = 'viktor'; localStorage.setItem('geldkompass.v3', JSON.stringify(S)); });
  await p.goto('http://localhost:8765/app/?lang=de&p=vk#overview'); await p.waitForTimeout(1200);
  const vk = await p.evaluate(() => document.getElementById('kpis').innerText + ' || ' + document.getElementById('flow').innerText);
  const num = re => +(((vk.match(re) || [0, 'NaN'])[1]) + '').replace(/\./g, ''); const vInc = num(/Einnahmen\s*([\d.]+)\s€/), vBooked = num(/gebucht\s*([\d.]+)\s€/), vSp = num(/Ausgaben\s*([\d.]+)\s€/);
  // Betrag hängt an den wöchentlich aktualisierten Dividendendaten, daher Logik statt fester Summe prüfen
  if (!(vInc > vBooked) || !(vInc >= vSp) || !/passiv/.test(vk) || !/Rein/.test(vk) || !/Raus/.test(vk) || !/Übrig/.test(vk) || /Kommt aus dem Vermögen/.test(vk)) bad.push('Viktor: passive Einnahmen nicht als Einnahme gezählt: ' + vk.replace(/\n/g, ' | ').slice(0, 300));
  if (errs.length) bad.push('JS-Fehler: ' + errs.join(' | '));
  await b.close();
  if (bad.length) { console.error('Monatslücke FEHLER', bad); process.exit(1); }
  console.log('Monatslücke: alle Einnahmen (Gehalt, Miete, Zinsen, Dividenden, Rente, Immobilie) gegen Ausgaben, Sparplan ist keine Lücke, echte Lücke mit richtigem Betrag, Beispielpersonen ohne falsche Lücke');
})();
