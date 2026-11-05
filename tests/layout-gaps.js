/* Prüft alle App-Seiten auf Lücken: Karten nebeneinander müssen am Computer gleich hoch sein (Dans Vorgabe 04.11.2026). */
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const bad = [];
  for (const w of [1024, 1440]) for (const lang of ['de', 'en']) {
    const p = await b.newPage({ viewport: { width: w, height: 900 } });
    await p.goto((process.env.BASE||'http://localhost:8765')+'/app/?lang=' + lang + '#overview'); await p.waitForTimeout(2000);
    const pages = await p.evaluate(() => [...document.querySelectorAll('section.page')].map(s => s.id.slice(2)));
    for (const pg of pages) {
      await p.evaluate(x => { location.hash = x; }, pg); await p.waitForTimeout(500);
      const r = await p.evaluate(() => { const s = document.querySelector('section.page.on'); if (!s) return []; const out = [];
        s.querySelectorAll(':scope > .g2').forEach(g => { const rows = {}; [...g.children].filter(c => c.offsetParent).forEach(c => { const bb = c.getBoundingClientRect(); const k = Math.round(bb.top); (rows[k] = rows[k] || []).push(bb.height); });
          Object.values(rows).forEach(h => { if (h.length > 1 && Math.max(...h) - Math.min(...h) > 4) out.push(h.map(Math.round).join(' vs ')); }); });
        return out; });
      r.forEach(x => bad.push(w + ' ' + lang + ' ' + pg + ': ' + x));
    }
    await p.close();
  }
  await b.close();
  if (bad.length) { console.error('Lücken zwischen Karten:\n' + bad.join('\n')); process.exit(1); }
  console.log('Layout: keine Lücken zwischen Kartenpaaren (1024/1440 px, DE/EN)');
})();
