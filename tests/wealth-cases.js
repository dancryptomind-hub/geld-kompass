/* Jede Finanzlage: Rentier (Viktor), Ruhestand vom Ersparten (Helga), Immobilie direkt beim Eintragen, Gesamtvermögen im Depot,
   kein leerer Audit-Bereich bei allen Beispielpersonen und unveränderte Arbeitsbuch-Werte von Luisa (2.300 € / 2.503 €). */
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 900 } }); const errs = []; p.on('pageerror', e => errs.push(e.message));
  const bad = [], f = x => String(x).replace(/\n/g, ' | ').slice(0, 300);
  await p.goto('http://localhost:8765/app/?lang=de'); await p.waitForTimeout(800);
  const setDemo = k => p.evaluate(k => { const S = JSON.parse(localStorage.getItem('geldkompass.v3') || '{}'); S.mode = 'demo'; S.profile = k; S.onboarded = 1; localStorage.setItem('geldkompass.v3', JSON.stringify(S)); localStorage.setItem('gk-tour', JSON.stringify({ off: 1, done: 1 })); }, k);
  for (const k of ['peter', 'rob', 'bella', 'luisa', 'samir', 'viktor', 'helga']) {
    await setDemo(k); await p.goto('http://localhost:8765/app/?lang=de&p=' + k + '#audit'); await p.waitForTimeout(1300);
    const a = await p.evaluate(() => [...document.querySelectorAll('#auditCard .auattributes button')].map(x => x.innerText.replace(/\n/g, ' ')).join(' / '));
    if (!a || /–/.test(a)) bad.push(k + ': Audit-Bereich ohne Wert: ' + a);
  }
  await setDemo('luisa'); await p.goto('http://localhost:8765/app/?lang=de&p=lu#overview'); await p.waitForTimeout(1200);
  const lu = await p.evaluate(() => document.querySelector('#kpis').innerText);
  if (!/Einnahmen\s*2\.300\s€/.test(lu) || !/Ausgaben\s*2\.503\s€/.test(lu)) bad.push('Luisa weicht vom Arbeitsbuch ab: ' + f(lu));
  await setDemo('viktor'); await p.goto('http://localhost:8765/app/?lang=de&p=vi#overview'); await p.waitForTimeout(1300);
  const vk = await p.evaluate(() => document.querySelector('#kpis').innerText + ' || ' + document.querySelector('#flowInsight').innerText);
  if (!/nur passive Einnahmen/.test(vk) || !/passiven Einnahmen tragen/.test(vk) || !/Miete/.test(vk)) bad.push('Viktor (Rentier) falsch: ' + f(vk));
  await p.goto('http://localhost:8765/app/?lang=de&p=vi2#assets'); await p.waitForTimeout(1300);
  const ds = await p.evaluate(() => document.querySelector('#depotDonut').innerText);
  if (!/Gesamtvermögen/.test(ds) || !/Immobilie/.test(ds) || !/Tagesgeld/.test(ds)) bad.push('Depot-Aufteilung ohne Gesamtvermögen/Immobilie: ' + f(ds));
  await setDemo('helga'); await p.goto('http://localhost:8765/app/?lang=de&p=he#overview'); await p.waitForTimeout(1300);
  const hk = await p.evaluate(() => document.querySelector('#kpis').innerText + ' || ' + document.querySelector('#flowInsight').innerText);
  if (!/reicht ≈ \d/.test(hk) || !/aus dem Vermögen/.test(hk)) bad.push('Helga: Vermögensverzehr nicht sichtbar: ' + f(hk));
  await p.goto('http://localhost:8765/app/?lang=de&p=he2#stress'); await p.waitForTimeout(1300);
  const hs = await p.evaluate(() => { const x = document.querySelector('.stdraw'); return x ? x.innerText : ''; });
  if (!/Mit 2 % Rendite/.test(hs) || !/4-%-Regel/.test(hs)) bad.push('Stresstest zeigt keine Reichweite: ' + f(hs));
  // eigene Daten: Immobilie direkt beim Eintragen
  await p.evaluate(() => { const S = JSON.parse(localStorage.getItem('geldkompass.v3')); S.mode = 'own'; S.own = { entries: [], items: [], hold: [], debts: [] }; localStorage.setItem('geldkompass.v3', JSON.stringify(S)); });
  await p.goto('http://localhost:8765/app/?lang=de&p=own#assets'); await p.waitForTimeout(1300);
  const hidden0 = await p.evaluate(() => document.querySelector('#iRe').hidden);
  await p.click('[data-item="Immobilie"]', { force: true }); await p.waitForTimeout(200);
  const shown = await p.evaluate(() => !document.querySelector('#iRe').hidden);
  await p.fill('#iVal', '300000'); await p.click('[data-iuse="rent"]', { force: true }); await p.fill('#iReRent', '1100'); await p.fill('#iReHg', '200');
  await p.click('#itemForm button[type=submit]', { force: true }); await p.waitForTimeout(800);
  const it = await p.evaluate(() => { const S = JSON.parse(localStorage.getItem('geldkompass.v3')); return JSON.stringify({ re: S.own.items[0] && S.own.items[0].re, e: S.own.entries.map(e => e.type + ':' + e.amount).sort() }); });
  if (!hidden0 || !shown) bad.push('Immobilien-Fragen erscheinen nicht direkt beim Antippen');
  if (!/"use":"rent","rent":1100,"hg":200/.test(it) || !/expense:200/.test(it) || !/income:1100/.test(it)) bad.push('Immobilie aus dem Schnell-Eintrag nicht verbucht: ' + it);
  await b.close();
  if (bad.length || errs.length) { console.error('Finanzlagen FEHLER', bad, errs); process.exit(1); }
  console.log('Finanzlagen: alle 7 Beispielpersonen mit vollständigem Audit, Rentier, Vermögensverzehr mit Reichweite, Immobilie direkt beim Eintragen, Gesamtvermögen, Arbeitsbuch-Werte unverändert');
})();
