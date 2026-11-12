/* Freiheits-Report: Beispiel-Report im Beispielmodus, Report mit eigenen Zahlen (Vorschau offen),
   Inhalt (Kennzahlen, Schritte, Hinweis), Druckansicht blendet die App aus, Danke-Seite schaltet nach Kauf frei. */
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const b = await chromium.launch(); const bad = [];
  const c = await b.newContext({ viewport: { width: 1280, height: 900 }, serviceWorkers: 'block', locale: 'de-DE' });await require('./plus-preview')(c);
  const p = await c.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.addInitScript(() => { try { localStorage.setItem('gk-tour', JSON.stringify({ off: 1, done: 1 })); } catch (e) {} });
  await p.goto('http://localhost:8765/app/?lang=de#data'); await p.waitForTimeout(1500);
  const card = await p.evaluate(() => (document.getElementById('frCard') || {}).innerText || '');
  if (!/Freiheits-Report/.test(card) || !/Beispiel-Report ansehen/.test(card)) bad.push('Report-Karte im Beispielmodus falsch: ' + card.slice(0, 200));
  await p.click('#frCard [data-fr-open]'); await p.waitForTimeout(500);
  const doc = await p.evaluate(() => { const d = document.querySelector('#frDlg .frdoc'); return d && !document.getElementById('frDlg').hidden ? d.innerText : ''; });
  for (const w of ['Dein Freiheits-Report', 'Freiheit auf einen Blick', 'Freiheitstage', 'Dein Monat', 'Dein Vermögen', 'Dein Weg zur Freiheit', 'Deine nächsten 3 Schritte', 'keine Anlage-', 'Beispiel mit Beispielzahlen'])
    if (!doc.includes(w)) bad.push('Report ohne „' + w + '“');
  if (/NaN|undefined|Infinity/.test(doc)) bad.push('Report enthält kaputte Werte: ' + (doc.match(/.{30}(NaN|undefined|Infinity).{10}/) || [''])[0]);
  const ns = await p.evaluate(() => document.querySelectorAll('#frDlg .frsteps li').length); if (ns < 1 || ns > 3) bad.push('Schritte: ' + ns);
  await p.emulateMedia({ media: 'print' });
  const pr = await p.evaluate(() => ({ app: [...document.body.children].filter(e => e.id !== 'frDlg' && e.tagName !== 'SCRIPT' && getComputedStyle(e).display !== 'none').map(e => e.tagName + '#' + e.id), bar: getComputedStyle(document.querySelector('.frbar')).display }));
  if (pr.app.length || pr.bar !== 'none') bad.push('Druckansicht zeigt App oder Leiste: ' + JSON.stringify(pr));
  await p.emulateMedia({ media: 'screen' });
  await p.click('[data-fr-close]'); if (!(await p.evaluate(() => document.getElementById('frDlg').hidden))) bad.push('Schließen geht nicht');
  // Eigene Zahlen: in der Vorschau offen → „Report erstellen“
  await p.evaluate(() => { const st = JSON.parse(localStorage.getItem('geldkompass.v3')); st.mode = 'own'; localStorage.setItem('geldkompass.v3', JSON.stringify(st)); });
  await p.goto('http://localhost:8765/app/?lang=de#report'); await p.waitForTimeout(1500);
  const own = await p.evaluate(() => { const d = document.getElementById('frDlg'); return d && !d.hidden ? d.innerText : 'zu'; });
  if (/NaN|undefined/.test(own)) bad.push('Leerer eigener Report mit kaputten Werten: ' + (own.match(/.{30}(NaN|undefined).{10}/) || [''])[0]);
  if (!/Dein Freiheits-Report/.test(own)) bad.push('#report öffnet keinen Report: ' + own.slice(0, 120));
  // Englisch (gespeicherte Sprachwahl hat Vorrang vor ?lang)
  await p.evaluate(() => localStorage.setItem('geld-kompass-lang', 'en'));
  await p.goto('http://localhost:8765/app/?lang=en#data'); await p.waitForTimeout(1200);
  await p.click('#frCard [data-fr-open]').catch(() => {}); await p.waitForTimeout(400);
  const en = await p.evaluate(() => (document.querySelector('#frDlg .frdoc') || {}).innerText || '');
  if (!/Your freedom report/.test(en) || /Freiheit auf einen Blick/.test(en)) bad.push('Englischer Report falsch: ' + en.slice(0, 150) + ' | ' + await p.evaluate(() => (document.getElementById('frCard') || {}).innerText));
  // Danke-Seite nach Report-Kauf
  const cfg = fs.readFileSync(__dirname + '/../billing-config.js', 'utf8');
  const q = await c.newPage();
  await q.route('**/billing-config.js*', r => r.fulfill({ contentType: 'text/javascript', body: cfg.replace('enabled: false', 'enabled: true') }));
  await q.route('https://cwznthfefbeglamnwyry.supabase.co/functions/v1/**', r => r.fulfill({ contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ kind: 'gk_freedom_report', status: 'paid' }) }));
  const sid = 'cs_test_' + 'r'.repeat(30);
  await q.goto('http://localhost:8765/plus/danke/?lang=de&session_id=' + sid); await q.waitForTimeout(1500);
  const th = await q.evaluate(() => ({ t: document.getElementById('thxState').innerText, a: (document.querySelector('#thxState a') || {}).href || '', k: localStorage.getItem('gk-report-ok') }));
  if (!/Report jetzt erstellen|Create report now/.test(th.t) || !/#report/.test(th.a) || th.k !== sid) bad.push('Danke-Seite Report falsch: ' + JSON.stringify(th));
  if (errs.length) bad.push('JS-Fehler: ' + errs.join(' | '));
  await b.close();
  if (bad.length) { console.error('Freiheits-Report FEHLER', bad); process.exit(1); }
  console.log('Freiheits-Report: Beispiel-Report, eigener Report über #report, alle Abschnitte ohne kaputte Werte, Druckansicht ohne App, Englisch, Danke-Seite schaltet nach Kauf frei');
})();
