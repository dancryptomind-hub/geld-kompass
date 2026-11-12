/* Kostenloses Konto: Schulden-Plan, Abos & Gewohnheiten und Ziele nur mit Konto (eigener Modus). Startseite zeigt den klaren Weg: erst Konto, dann Plus. */
const { chromium } = require('playwright'); const BASE = 'http://localhost:8765';
(async () => {
  const b = await chromium.launch(); const bad = [];
  for (const kind of ['gast', 'konto']) {
    const c = await b.newContext({ viewport: { width: 1280, height: 900 }, serviceWorkers: 'block' });
    await c.addInitScript(() => { Object.defineProperty(navigator, 'webdriver', { get: () => false }); try { const S = { mode: 'own', onboarded: 1, own: { entries: [{ id: 'e1', title: 'Gehalt', amount: 2500, type: 'income', cat: 'Gehalt', freq: 'monthly', date: '2026-01-01' }], debts: [{ id: 'd1', name: 'Kredit', bal: 3000, rate: 9, pay: 150, kind: 'consumer' }], hold: [], items: [] } }; if (!localStorage.getItem('geldkompass.v3')) localStorage.setItem('geldkompass.v3', JSON.stringify(S)); localStorage.setItem('gk-tour', JSON.stringify({ off: 1, done: 1 })); } catch (e) {} });
    await c.route('**/*', r => { const u = r.request().url(); if (u.startsWith(BASE)) return r.continue();
      if (u.includes('/auth/v1/user')) return kind === 'konto' ? r.fulfill({ json: { id: 'u1', email: 'a@b.de', email_confirmed_at: '2026-01-01', app_metadata: {}, user_metadata: {}, aud: 'authenticated' } }) : r.fulfill({ status: 401, json: { msg: 'no' } });
      return r.abort(); });
    if (kind === 'konto') await c.addInitScript(() => { const exp = Math.floor(Date.now() / 1000) + 3600; localStorage.setItem('gk.account.v1', JSON.stringify({ access_token: 'eyJhbGciOiJIUzI1NiJ9.' + btoa(JSON.stringify({ sub: 'u1', exp })) + '.x', refresh_token: 'r', expires_at: exp, expires_in: 3600, token_type: 'bearer', user: { id: 'u1', email: 'a@b.de', aud: 'authenticated', app_metadata: {}, user_metadata: {} } })); });
    const p = await c.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
    await p.goto(BASE + '/app/?lang=de#debts'); await p.waitForTimeout(2500);
    const r = await p.evaluate(() => ({ gate: !!document.querySelector('#p-debts > .accgate'), plan: (() => { const x = document.getElementById('planCard'); return x ? getComputedStyle(x).display !== 'none' : null; })(), href: (document.querySelector('#p-debts .accgate a.btn.pri') || {}).getAttribute ? document.querySelector('#p-debts .accgate a.btn.pri').getAttribute('href') : '' }));
    await p.goto(BASE + '/app/?lang=de&x=1#overview'); await p.waitForTimeout(2000);
    const cta = await p.evaluate(() => (document.getElementById('gkCta') || {}).innerText || '');
    if (kind === 'gast') {
      if (!r.gate || r.plan) bad.push('Gast: Schulden-Plan nicht gesperrt ' + JSON.stringify(r));
      if (!/action=signup&next=debts/.test(r.href)) bad.push('Gast: Registrieren-Link falsch: ' + r.href);
      if (!/Kostenloses Konto/.test(cta)) bad.push('Gast: Startseite ohne Konto-Hinweis: ' + cta.slice(0, 80));
    } else {
      if (r.gate || r.plan === false) bad.push('Konto: Schulden-Plan gesperrt ' + JSON.stringify(r));
      if (!/7 Tage kostenlos/.test(cta)) bad.push('Konto: Startseite ohne Plus-Hinweis: ' + cta.slice(0, 80));
    }
    if (errs.length) bad.push(kind + ' JS-Fehler: ' + errs.join(' | '));
    await c.close();
  }
  await b.close();
  if (bad.length) { console.error('FEHLER:\n' + bad.join('\n')); process.exit(1); }
  console.log('OK account-gate');
})();
