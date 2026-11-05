/* Konten und Besitz: Buchungsverlauf (Zinsen zählen als Einnahme), Immobilie mit Miete und Kosten, passive Einnahmen ohne Gehalt, Investiert zeigt Bestand. */
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 900 } }); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('http://localhost:8765/app/?lang=de#overview'); await p.waitForTimeout(1200);
  await p.evaluate(() => {
    const S = JSON.parse(localStorage.getItem('geldkompass.v3') || '{}'); S.mode = 'own'; S.onboarded = 1; S.own = S.own || {};
    S.own.entries = [{ id: 'm', title: 'Lebensmittel', amount: 600, type: 'expense', cat: 'Lebensmittel', freq: 'monthly', date: '2026-01-01' }];
    S.own.items = [{ id: 'tg', name: 'Tagesgeld', value: 10000, cls: 'Tagesgeld / Notgroschen' }, { id: 'im', name: 'Wohnung Leipzig', value: 200000, cls: 'Immobilie' }];
    S.own.hold = [{ id: 'h1', s: 'KO', qty: 100, buy: 50, price: 60 }]; S.own.debts = [];
    localStorage.setItem('geldkompass.v3', JSON.stringify(S)); localStorage.setItem('gk-tour', JSON.stringify({ off: 1, done: 1 }));
  });
  await p.reload(); await p.waitForTimeout(1800);
  const k0 = await p.evaluate(() => document.querySelector('#kpis').innerText);
  // Zinsen auf Tagesgeld buchen über den Bearbeiten-Dialog
  await p.evaluate(() => { location.hash = 'assets'; }); await p.waitForTimeout(1000);
  await p.click('[data-edit="item"][data-id="tg"]', { force: true }); await p.waitForTimeout(300);
  await p.selectOption('#edItK', 'int'); await p.fill('#edItA', '25');
  await p.evaluate(() => document.querySelector('#editDlg form, #editDlg').querySelector('[type=submit], .btn.pri').click()); await p.waitForTimeout(600);
  // Immobilie vermieten
  await p.click('[data-edit="item"][data-id="im"]', { force: true }); await p.waitForTimeout(300);
  const reVisible = await p.evaluate(() => !document.querySelector('#edReBox').hidden);
  await p.selectOption('#edReUse', 'rent'); await p.fill('#edReRent', '900'); await p.fill('#edReHg', '150'); await p.fill('#edReUp', '100'); await p.fill('#edReOt', '50');
  await p.evaluate(() => document.querySelector('#editDlg').querySelector('[type=submit], .btn.pri').click()); await p.waitForTimeout(600);
  const st = await p.evaluate(() => { const S = JSON.parse(localStorage.getItem('geldkompass.v3')); const tg = S.own.items.find(x => x.id === 'tg'); return { val: tg.value, tx: (tg.tx || []).map(t => t.k + ':' + t.a).join(','), auto: S.own.entries.filter(e => e.aKey).map(e => e.type + ':' + e.amount).sort().join(',') }; });
  const bal = await p.evaluate(() => document.querySelector('#balTable').innerText);
  await p.evaluate(() => { location.hash = 'overview'; }); await p.waitForTimeout(1000);
  const k1 = await p.evaluate(() => document.querySelector('#kpis').innerText);
  await b.close();
  const bad = [], f = x => x.replace(/\n/g, ' | ');
  if (!/Investiert \(Bestand\)\s*6\.000/.test(k0)) bad.push('Investiert sollte den Depotbestand 6.000 € zeigen: ' + f(k0));
  if (st.val !== 10025 || !/open:10000,int:25/.test(st.tx)) bad.push('Tagesgeld-Verlauf falsch: ' + JSON.stringify(st));
  if (!reVisible) bad.push('Immobilien-Felder werden nicht angezeigt');
  if (st.auto !== 'expense:100,expense:150,expense:50,income:25,income:900') bad.push('Automatische Buchungen falsch: ' + st.auto);
  if (!/Miete 900\s€ · Kosten 300\s€ · netto 600\s€/.test(bal)) bad.push('Bilanz zeigt Miete/Kosten nicht: ' + f(bal).slice(0, 300));
  if (!/Einnahmen\s*925/.test(k1)) bad.push('Einnahmen sollten Miete + Zinsen = 925 € sein: ' + f(k1));
  if (!/nur passive Einnahmen/.test(k1)) bad.push('Ohne Gehalt wird das Leben von passiven Einnahmen nicht erkannt: ' + f(k1));
  if (!/Ausgaben\s*900/.test(k1)) bad.push('Ausgaben sollten 600 + 300 Immobilienkosten = 900 € sein: ' + f(k1));
  if (!/Passives Einkommen/.test(k1) || !/Miete 900/.test(k1)) bad.push('Passives Einkommen ohne Miete: ' + f(k1));
  if (bad.length || errs.length) { console.error('Konten-Verlauf FEHLER', bad, errs); process.exit(1); }
  console.log('Konten und Besitz: Verlauf, Zinsen als Einnahme, Immobilie mit Miete/Kosten, passive Einnahmen ohne Gehalt, Investiert-Bestand');
})();
