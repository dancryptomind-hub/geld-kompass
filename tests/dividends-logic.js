/* Dividenden-Logik: erhaltene Dividenden aus der Depot-Historie erscheinen in Einnahmen (ohne Doppelzählung), Depot-Kennzahlen und Bilanz. */
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 900 } }); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto((process.env.BASE||'http://localhost:8765')+'/app/?lang=de#overview'); await p.waitForTimeout(1500);
  const ym = await p.evaluate(() => { const d = new Date(); return d.toISOString().slice(0, 7); });
  await p.evaluate((ym) => {
    const S = JSON.parse(localStorage.getItem('geldkompass.v3') || '{}'); S.mode = 'own'; S.onboarded = 1; S.own = S.own || {};
    S.own.entries = [{ id: 'g', title: 'Gehalt', amount: 2000, type: 'income', cat: 'Gehalt', freq: 'monthly', date: '2026-01-01' },
      { id: 'dv1', title: 'Dividende Coca-Cola', amount: 12.5, type: 'income', cat: 'Zinsen & Dividenden', freq: 'once', date: ym + '-02' }];
    S.own.hold = [{ id: 'h1', s: 'KO', qty: 25, buy: 58, tx: [{ d: ym + '-02', k: 'div', a: 12.5 }, { d: ym + '-05', k: 'div', a: 7.5 }] }];
    S.own.items = []; S.own.debts = []; localStorage.setItem('geldkompass.v3', JSON.stringify(S));
  }, ym);
  await p.reload(); await p.waitForTimeout(2000);
  const inc = await p.evaluate(() => document.querySelector('#kpis').innerText);
  const syn = await p.evaluate(() => { const S = JSON.parse(localStorage.getItem('geldkompass.v3')); return S.own.entries.filter(e => /Dividende/.test(e.title)).map(e => e.amount + '|' + (e.divKey ? 'auto' : 'manuell')); });
  await p.reload(); await p.waitForTimeout(1500);
  const syn2 = await p.evaluate(() => JSON.parse(localStorage.getItem('geldkompass.v3')).own.entries.filter(e => /Dividende/.test(e.title)).length);
  const aud = await p.evaluate(() => { const o = document.querySelector('#auditCard'); return o ? o.innerText : 'kein auditCard'; });
  await p.evaluate(() => { location.hash = 'assets'; }); await p.waitForTimeout(1200);
  const kp = await p.evaluate(() => document.querySelector('#assetKpis').innerText), bal = await p.evaluate(() => document.querySelector('#balTable').innerText), dep = await p.evaluate(() => document.querySelector('#depotTable').innerText);
  await b.close();
  const bad = [];
  if (!/2\.020/.test(inc)) bad.push('Einnahmen sollten 2.000 + 12,50 gebuchte + 7,50 nur in der Historie = 2.020 € sein: ' + inc.replace(/\n/g, ' | ').slice(0, 120));
  if (!/davon 20\s€ Dividenden/.test(inc)) bad.push('Übersicht nennt den Dividenden-Anteil der Einnahmen nicht: ' + inc.replace(/\n/g, ' | ').slice(0, 200));
  if (!/Passives Einkommen/.test(inc)) bad.push('KPI Passives Einkommen fehlt');
  if (syn.join(',') !== '12.5|manuell,7.5|auto' || syn2 !== 2) bad.push('Dividende nicht genau einmal als Buchung angelegt: ' + syn.join(',') + ' / ' + syn2);
  if (!/Dividenden: /.test(aud)) bad.push('Verhaltens-Audit kennt die Dividenden nicht: ' + aud);
  if (!/Dividenden/.test(kp)) bad.push('Depot-Kennzahl Dividenden fehlt');
  if (!/Dividenden: /.test(bal)) bad.push('Bilanz zeigt keine Dividenden je Position');
  if (!/\+20\s€ Dividenden/.test(dep)) bad.push('Depot-Tabelle zeigt erhaltene Dividenden nicht: ' + dep.replace(/\n/g, ' | ').slice(0, 200));
  if (bad.length || errs.length) { console.error('Dividenden-Logik FEHLER', bad, errs); process.exit(1); }
  console.log('Dividenden-Logik: Einnahmen ohne Doppelzählung, Depot-Kennzahl, Tabelle und Bilanz zeigen Dividenden');
})();
