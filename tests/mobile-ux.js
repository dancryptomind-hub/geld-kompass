/* Handy: kompakte Schulden-Tabellen, 60-Sekunden-Fenster als eigener Bildschirm (Hintergrund gesperrt, kein Tastatur-Sprung, Schließen frei),
   feste untere Leiste ohne Federn, Plus-Schnellleiste anpassbar. */
const { chromium, devices } = require('playwright');
(async () => {
  const b = await chromium.launch(); const c = await b.newContext({ ...devices['iPhone 13'] });if(!(await require('./plus-preview')(c))){console.log('übersprungen: Plus-Code nur in der CI des privaten Repos');process.exit(0);} const p = await c.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message)); const bad = [];
  await p.goto('http://localhost:8765/app/?lang=de'); await p.waitForTimeout(600);
  await p.evaluate(() => { const S = JSON.parse(localStorage.getItem('geldkompass.v3') || '{}'); S.mode = 'demo'; S.profile = 'rob'; S.onboarded = 1; localStorage.setItem('geldkompass.v3', JSON.stringify(S)); localStorage.setItem('gk-tour', JSON.stringify({ off: 1, done: 1 })); });
  await p.goto('http://localhost:8765/app/?lang=de&m=1#debts'); await p.waitForTimeout(1500);
  for (const sel of ['#debtHelp .mcards', '#dpCompare']) {
    const r = await p.evaluate(s => { const e = document.querySelector(s); if (!e || !e.offsetParent) return null; const t = e.querySelector('tr:not(:first-child)') || e.querySelector('tbody tr'); return { h: e.getBoundingClientRect().height, w: e.scrollWidth, vw: innerWidth, head: e.querySelector('thead') ? getComputedStyle(e.querySelector('thead')).display : 'none' }; }, sel);
    if (!r) bad.push(sel + ' nicht sichtbar'); else if (r.h > 450 || r.w > r.vw || r.head !== 'none') bad.push(sel + ' auf dem Handy zu lang oder zu breit: ' + JSON.stringify(r));
  }
  const bar = await p.evaluate(() => ({ t: getComputedStyle(document.getElementById('mnav')).transform, os: getComputedStyle(document.documentElement).overscrollBehaviorY }));
  if (bar.t === 'none' || bar.os !== 'none') bad.push('Untere Leiste nicht fest verankert: ' + JSON.stringify(bar));
  await p.evaluate(() => { const S = JSON.parse(localStorage.getItem('geldkompass.v3')); S.onboarded = 0; S.own = { entries: [], items: [], hold: [], debts: [] }; localStorage.setItem('geldkompass.v3', JSON.stringify(S)); });
  await p.goto('http://localhost:8765/app/?lang=de&m=2#overview'); await p.waitForTimeout(1200);
  await p.tap('#modeBtn'); await p.waitForTimeout(600);
  const m = await p.evaluate(() => { const d = document.getElementById('onbDlg'), r = d.getBoundingClientRect(); return { open: d.open, lock: document.documentElement.classList.contains('gk-modal'), focusInput: document.activeElement && document.activeElement.tagName === 'INPUT', full: Math.round(r.height) >= innerHeight - 2 && Math.round(r.width) >= innerWidth - 2, scrolls: d.scrollHeight > d.clientHeight, x: (() => { const x = document.getElementById('onbX').getBoundingClientRect(); return x.width >= 40 && x.top >= 0; })() }; });
  if (!m.open || !m.lock || m.focusInput || !m.full || !m.x) bad.push('60-Sekunden-Fenster auf dem Handy: ' + JSON.stringify(m));
  await p.tap('#onbX'); await p.waitForTimeout(300);
  const after = await p.evaluate(() => ({ open: document.getElementById('onbDlg').open, lock: document.documentElement.classList.contains('gk-modal') }));
  if (after.open || after.lock) bad.push('Nach dem Schließen bleibt die Seite gesperrt: ' + JSON.stringify(after));
  await p.goto('http://localhost:8765/app/?lang=de&m=3#data'); await p.waitForTimeout(1200);
  await p.selectOption('[data-mnav="1"]', 'stress'); await p.waitForTimeout(300);
  await p.reload(); await p.waitForTimeout(1000);
  const nav = await p.evaluate(() => document.getElementById('mnav').innerText.replace(/\n/g, '|'));
  if (nav !== 'Start|Stresstest|Schulden|Depot|Mehr') bad.push('Schnellleiste nicht anpassbar: ' + nav);
  // Profit-Hebel: dreimal „Abos“ über das Menü → Vorschlag für die Leiste
  for (let i = 0; i < 3; i++) { await p.tap('[data-menu]'); await p.waitForTimeout(250); await p.click('#navGroups [data-page="recurring"]', { force: true }); await p.waitForTimeout(400); await p.click('#navGroups [data-page="overview"]', { force: true }).catch(() => {}); await p.waitForTimeout(200); }
  await p.waitForTimeout(800);
  const nudge = await p.evaluate(() => { const n = document.getElementById('mnavNudge'); return n ? n.innerText : ''; });
  if (!/Abos/.test(nudge)) bad.push('Kein Leisten-Vorschlag nach dreimal „Abos“: ' + nudge);
  else { await p.tap('[data-nudge-add]'); await p.waitForTimeout(400); const nav2 = await p.evaluate(() => document.getElementById('mnav').innerText.replace(/\n/g, '|')); if (!/Abos/.test(nav2)) bad.push('Vorschlag hat Abos nicht in die Leiste gelegt: ' + nav2); }
  await b.close();
  if (bad.length || errs.length) { console.error('Handy FEHLER', bad, errs); process.exit(1); }
  console.log('Handy: kompakte Schulden-Tabellen, 60-Sekunden-Fenster als Vollbild mit Sperre und Schließen, feste Leiste, Plus-Schnellleiste');
})();
