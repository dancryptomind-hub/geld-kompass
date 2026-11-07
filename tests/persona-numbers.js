/* Beispielprofile: Beträge im Profiltext müssen exakt zu den Kennzahlen passen (in jeder Währung). */
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 900 } }); const errs = []; p.on('pageerror', e => errs.push(e.message)); const bad = [];
  await p.goto('http://localhost:8765/app/?lang=de'); await p.waitForTimeout(800);
  for (const cur of ['EUR', 'USD', 'THB', 'GBP']) {
    for (const k of ['peter', 'rob', 'bella', 'luisa', 'samir', 'viktor', 'helga']) {
      await p.evaluate(([k, cur]) => { const S = JSON.parse(localStorage.getItem('geldkompass.v3') || '{}'); S.mode = 'demo'; S.profile = k; localStorage.setItem('geldkompass.v3', JSON.stringify(S)); localStorage.setItem('geld-kompass-currency', cur); localStorage.setItem('gk-tour', JSON.stringify({ off: 1, done: 1 })); }, [k, cur]);
      await p.goto('http://localhost:8765/app/?lang=de&p=' + k + cur + '#examples'); await p.waitForTimeout(1300);
      const r = await p.evaluate(() => { const h = document.getElementById('pHero'); return { txt: (h.querySelector('p') || {}).innerText || '', inc: ((h.querySelector('.hnums b') || {}).innerText || '') }; });
      const m = r.txt.match(/verdient (?:ebenfalls )?(.+?)(?: und| im Monat|\.\s)/);
      if (!m) { if (/\d\s?[€$£฿]|[€$£฿]\s?\d/.test(r.txt)) bad.push(cur + ' ' + k + ': Betrag im Text nicht geprüft: ' + r.txt.slice(0, 120)); continue; }
      const norm = s => s.replace(/\s/g, '');
      if (norm(m[1]) !== norm(r.inc)) bad.push(cur + ' ' + k + ': Text ' + m[1] + ' ≠ Einkommen ' + r.inc);
    }
  }
  if (errs.length) bad.push('JS-Fehler: ' + errs.join(' | '));
  await b.close();
  if (bad.length) { console.error('FEHLER:\n' + bad.join('\n')); process.exit(1); }
  console.log('OK persona-numbers');
})();
