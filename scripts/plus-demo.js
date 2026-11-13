/* Erzeugt die Plus-Vorschau (app/plus-demo.de.html, app/plus-demo.en.html): fertig gerenderte Plus-Ansichten mit Beispielpersonen.
   Enthält nur HTML/CSS (keinen Plus-Code, keine Skripte). Aufruf lokal mit Plus-Code aus dem privaten Repo:
   PLUS_BUNDLE=…/dist/plus.js node scripts/plus-demo.js   (Server: python3 -m http.server 8765 im Repo) */
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const plusPreview = require('../tests/plus-preview.js'); const BASE = 'http://localhost:8765'; const ROOT = path.join(__dirname, '..');
const pad = n => String(n).padStart(2, '0'); const now = new Date(); const dAgo = k => { const d = new Date(now); d.setDate(d.getDate() - k); return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); };
const ST = [
  { id: 'audit', prof: 'viktor', page: 'assets', sel: '#auditCard' },
  { id: 'stress', prof: 'peter', page: 'stress', sel: '#stressOut' },
  { id: 'wd', prof: 'helga', page: 'stress', sel: '#stressOut .wdplan', alt: '#stressOut' },
  { id: 'snow', prof: 'peter', page: 'future', sel: '#futSnow' },
  { id: 'scen', prof: 'peter', page: 'future', sel: '#futScen' },
  { id: 'move', prof: 'peter', page: 'future', sel: '#futMove' },
  { id: 'year', prof: 'peter', page: 'future', sel: '#futYear' },
  { id: 'cashflow', prof: 'viktor', page: 'assets', sel: '#cashflowBox' },
  { id: 'tax', prof: 'viktor', page: 'assets', sel: '#taxBox' },
  { id: 'alarm', prof: 'viktor', page: 'assets', sel: '#alarmBox', alarm: 1 },
  { id: 'nomad', prof: 'viktor', page: 'nomad', sel: '#nomadOut', nomad: 1 }
];
(async () => {
  if (!process.env.PLUS_BUNDLE) { console.error('PLUS_BUNDLE fehlt'); process.exit(1); }
  const b = await chromium.launch(); const out = {};
  for (const lang of ['de', 'en']) {
    const c = await b.newContext({ viewport: { width: 1180, height: 1000 }, serviceWorkers: 'block', locale: lang === 'de' ? 'de-DE' : 'en-US' }); const p = await c.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
    const html = fs.readFileSync(path.join(ROOT, 'app/index.html'), 'utf8').replace(/<meta http-equiv="Content-Security-Policy"[^>]*>/, '').replace('function D(){', 'window.__gkBuild=function(k){return JSON.parse(JSON.stringify(buildProfile(k)));};function D(){');
    await p.route(/\/app\/(\?.*)?$/, r => r.fulfill({ contentType: 'text/html; charset=utf-8', body: html }));
    await plusPreview(p);
    await p.goto(BASE + '/app/?lang=' + lang); await p.waitForTimeout(1500);
    let styles = null; out[lang] = { secs: [] };
    for (const st of ST) {
      await p.evaluate(([st, stays]) => { const S = JSON.parse(localStorage.getItem('geldkompass.v3') || '{}'); S.mode = 'demo'; S.profile = st.prof; localStorage.setItem('geldkompass.v3', JSON.stringify(S)); }, [st, null]);
      await p.goto(BASE + '/app/?lang=' + lang + '&g=' + st.id); await p.waitForTimeout(1200);
      await p.evaluate(([st, stays]) => { const d = window.__gkBuild(st.prof); const S = JSON.parse(localStorage.getItem('geldkompass.v3')); d.entries = d.entries || []; d.debts = d.debts || []; d.hold = d.hold || []; d.items = d.items || [];
        if (st.alarm) d.hold.slice(0, 3).forEach((h, i) => { const px = +h.buy || 100; h.alarm = i === 1 ? { dn: Math.round(px * 0.85) } : { up: Math.round(px * 1.4) }; });
        if (st.nomad) { d.stays = stays; d.nomad = { base: 'DE', eu: 1 }; }
        S.mode = 'own'; S.onboarded = 1; S.own = d; S.calc = S.calc || {}; localStorage.setItem('geldkompass.v3', JSON.stringify(S)); localStorage.setItem('gk-tour', JSON.stringify({ off: 1, done: 1 })); localStorage.setItem('geld-kompass-currency', 'EUR'); },
        [st, [{ d: dAgo(300), c: 'TH' }, { d: dAgo(214), c: 'VN' }, { d: dAgo(170), c: 'PT' }, { d: dAgo(120), c: 'ES' }, { d: dAgo(75), c: 'GE' }, { d: dAgo(20), c: 'TH' }]]);
      await p.goto(BASE + '/app/?lang=' + lang + '&h=' + st.id + '#' + st.page); await p.waitForTimeout(2600);
      const r = await p.evaluate(st => { let el = document.querySelector(st.sel) || (st.alt && document.querySelector(st.alt)); if (!el || !el.innerHTML.trim()) return null;
        el.querySelectorAll('details').forEach(x => x.open = true);
        const chain = []; let a = el.parentElement; while (a && a !== document.body) { chain.unshift({ t: a.tagName.toLowerCase(), c: a.className || '' }); a = a.parentElement; }
        const css = [...document.querySelectorAll('style')].map(s => s.textContent).join('\n'); const links = [...document.querySelectorAll('link[rel=stylesheet]')].map(l => l.getAttribute('href'));
        return { html: el.outerHTML, chain, css, links, root: { cls: document.documentElement.className, theme: document.documentElement.getAttribute('data-theme') || '' }, body: document.body.className }; }, st);
      if (!r) { console.error('LEER: ' + lang + ' ' + st.id); process.exit(1); }
      styles = styles || r; out[lang].secs.push({ id: st.id, ...r });
    }
    if (errs.length) { console.error('JS-Fehler ' + lang + ': ' + errs.join(' | ')); process.exit(1); }
    out[lang].styles = styles; await c.close();
  }
  await b.close();
  const clean = h => h.replace(/<script[\s\S]*?<\/script>/gi, '').replace(/\son[a-z]+="[^"]*"/gi, '').replace(/<iframe[\s\S]*?<\/iframe>/gi, '').replace(/\sid="/g, ' data-pid="').replace(/<(input|select|textarea|button)\b/gi, '<$1 disabled tabindex="-1"').replace(/\shref="(?!https?:)[^"]*"/gi, ' href="#"');
  for (const lang of ['de', 'en']) {
    const S0 = out[lang].styles;
    const css = S0.css.replace(/<\/style/gi, '');
    const wrap = s => { const open = s.chain.map(x => '<' + x.t + ' class="pdw ' + x.c.replace(/\b(open|hide|gt-hl)\b/g, '') + (x.c.includes('page') ? ' on' : '') + '">').join(''); const close = s.chain.slice().reverse().map(x => '</' + x.t + '>').join(''); return '<section class="pdsec" id="' + s.id + '">' + open + clean(s.html) + close + '</section>'; };
    const page = `<!doctype html>
<html lang="${lang}" class="${S0.root.cls}"${S0.root.theme ? ' data-theme="' + S0.root.theme + '"' : ''}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>${lang === 'de' ? 'Geld-Kompass Plus · Vorschau' : 'Money Compass Plus · Preview'}</title>
${S0.links.map(h => '<link rel="stylesheet" href="' + h + '">').join('\n')}
<style>${css}
.pdsec{display:none;padding:14px}.pdsec:target{display:block}body{background:var(--bg,#f6f4ee);margin:0}
.pdsec .page{display:block!important;padding:0!important;margin:0!important}.pdsec main,.pdsec .main{padding:0!important;margin:0!important;max-width:none!important}
.pdsec a,.pdsec button,.pdsec input,.pdsec select,.pdsec textarea,.pdsec summary,.pdsec label{pointer-events:none!important}
.pdsec [data-partner],.pdsec .gt-hl{display:none!important}
.pdw{display:block!important;width:auto!important;max-width:880px!important;grid-template-columns:none!important;columns:auto!important;position:static!important;margin:0 auto!important;padding:0!important;border:0!important;background:none!important;box-shadow:none!important}</style>
</head>
<body class="${S0.body}">
${out[lang].secs.map(wrap).join('\n')}
</body>
</html>
`;
    fs.writeFileSync(path.join(ROOT, 'app', 'plus-demo.' + lang + '.html'), page);
    console.log('app/plus-demo.' + lang + '.html', Math.round(page.length / 1024) + ' KB', out[lang].secs.map(s => s.id + ':' + Math.round(s.html.length / 1024) + 'KB').join(' '));
  }
})();
