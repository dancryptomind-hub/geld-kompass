/* Steuern nach Wohnsitz: Übersicht und Länderseiten (DE/EN) rechnen, verlinken einander, sind in der Sitemap und passen aufs Handy. */
const { chromium } = require('playwright'); const fs = require('fs'); const BASE = 'http://localhost:8765';
(async () => {
  const bad = []; const d = JSON.parse(fs.readFileSync('data/tax-residence.json', 'utf8')); const n = Object.keys(d.countries).length;
  if (n < 80) bad.push('Nur ' + n + ' Länder');
  const sm = fs.readFileSync('sitemap.xml', 'utf8');
  for (const c of Object.keys(d.countries)) { const de = 'rechner/steuern-nach-wohnsitz/' + d.slugs[c] + '/index.html', en = 'en/calculators/taxes-by-residence/' + d.slugs_en[c] + '/index.html';
    for (const f of [de, en]) { if (!fs.existsSync(f)) bad.push('fehlt: ' + f); else if (!sm.includes('https://geld-kompass.com/' + f.replace('index.html', ''))) bad.push('nicht in Sitemap: ' + f); } }
  const b = await chromium.launch(); const errs = [];
  for (const [u, w, exp] of [['/rechner/steuern-nach-wohnsitz/', 1280, /Deutschland[\s\S]*Obergrenze gesamt/], ['/rechner/steuern-nach-wohnsitz/thailand/', 390, /Thailand[\s\S]*Deutschland/], ['/en/calculators/taxes-by-residence/portugal/?lang=en', 1280, /Portugal[\s\S]*Upper estimate/], ['/rechner/steuern-nach-wohnsitz/?embed=1&c=GE&vs=AE', 700, /Georgien[\s\S]*Vereinigte Arabische Emirate/]]) {
    const p = await b.newPage({ viewport: { width: w, height: 900 } }); p.on('pageerror', e => errs.push(u + ': ' + e.message));
    await p.goto(BASE + u); await p.waitForTimeout(1300);
    const r = await p.evaluate(() => ({ out: document.getElementById('txOut').innerText, ovf: document.documentElement.scrollWidth > innerWidth + 1, ld: document.querySelectorAll('script[type="application/ld+json"]').length, canon: !!document.querySelector('link[rel=canonical]') }));
    if (!exp.test(r.out)) bad.push(u + ': Ergebnis falsch: ' + r.out.slice(0, 120));
    if (r.ovf) bad.push(u + ': zu breit bei ' + w);
    if (r.ld < 3 || !r.canon) bad.push(u + ': SEO-Daten fehlen');
    await p.fill('#txInc', '100000'); await p.waitForTimeout(200);
    const after = await p.evaluate(() => document.getElementById('txOut').innerText);
    if (after === r.out) bad.push(u + ': Eingabe ändert nichts');
    await p.close();
  }
  await b.close();
  if (errs.length) bad.push('JS-Fehler: ' + errs.join(' | '));
  if (bad.length) { console.error('FEHLER:\n' + bad.slice(0, 20).join('\n')); process.exit(1); }
  console.log('OK tax-pages (' + n + ' Länder, DE/EN)');
})();
