/* Bezahlweg (Stripe über Supabase Edge Functions), mit nachgestellten Server-Antworten:
   ausgeschaltet keine Kaufknöpfe, eingeschaltet Plus-Fenster (Jahr vorausgewählt), Anmelde-Hinweis ohne Konto,
   Weiterleitung zur Stripe-Checkout-Seite, Danke-Seite für Plus und Arbeitsbuch-Download, Arbeitsbuch-Kaufknopf. */
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const b = await chromium.launch(); const bad = [];
  const cfg = fs.readFileSync(__dirname + '/../billing-config.js', 'utf8');
  async function page(enabled, statusBody) {
    const c = await b.newContext({ viewport: { width: 1280, height: 900 }, serviceWorkers: 'block', locale: 'de-DE' }); const p = await c.newPage(); p.errs = []; p.on('pageerror', e => p.errs.push(e.message));
    await p.route('**/billing-config.js*', r => r.fulfill({ contentType: 'text/javascript', body: enabled ? cfg.replace('enabled: false', 'enabled: true') : cfg }));
    p.calls = [];
    await p.route('https://cwznthfefbeglamnwyry.supabase.co/functions/v1/**', r => { const u = r.request().url(); p.calls.push(u.split('/v1/')[1] + ' ' + (r.request().postData() || '')); if (/billing-checkout/.test(u)) return r.fulfill({ contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ url: 'https://checkout.stripe.com/c/pay/cs_test_mock' }) }); if (/billing-status/.test(u)) return r.fulfill({ contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify(statusBody || {}) }); return r.fulfill({ status: 404, body: '{}' }); });
    await p.route('https://checkout.stripe.com/**', r => r.fulfill({ contentType: 'text/html', body: '<h1>Stripe Checkout (Test)</h1>' }));
    return p;
  }
  // 1) ausgeschaltet
  let p = await page(false);
  await p.goto('http://localhost:8765/app/?lang=de#plus'); await p.waitForTimeout(1500);
  let d = await p.evaluate(() => { const x = document.getElementById('plusDlg'); return x ? { open: x.open, dis: x.querySelector('#plusGo').disabled, msg: x.querySelector('#plusMsg').innerText } : null; });
  if (!d || !d.open || !d.dis || !/eingerichtet/.test(d.msg)) bad.push('Ausgeschaltet: Plus-Fenster falsch: ' + JSON.stringify(d));
  await p.goto('http://localhost:8765/arbeitsbuch/'); await p.waitForTimeout(600);
  if (!(await p.evaluate(() => document.getElementById('abBuy').hidden))) bad.push('Ausgeschaltet: Arbeitsbuch-Kaufknopf sichtbar');
  // 2) eingeschaltet, ohne Konto
  p = await page(true);
  await p.goto('http://localhost:8765/app/?lang=de#plus'); await p.waitForTimeout(1500);
  if (p.errs.length) console.log('ERRS', p.errs); d = await p.evaluate(() => { const x = document.getElementById('plusDlg'); if (!x) return { yearly: false, text: 'kein Dialog ' + location.hash + ' ' + !!window.GK_BILLING }; return { yearly: x.querySelector('input[value=plus_yearly]').checked, text: x.innerText }; });
  if (!d.yearly || !/39,00\s€ pro Jahr/.test(d.text) || !/4,99\s€ pro Monat/.test(d.text) || !/3,25\s€ im Monat/.test(d.text)) bad.push('Plus-Fenster Preise/Vorauswahl falsch: ' + d.text.replace(/\n/g, ' | ').slice(0, 300));
  await p.click('#plusGo'); await p.waitForTimeout(800);
  const login = await p.evaluate(() => document.getElementById('plusMsg').innerText);
  if (!/melde dich zuerst an/.test(login)) bad.push('Ohne Konto kein Anmelde-Hinweis: ' + login);
  if (p.calls.some(c => /billing-checkout/.test(c))) bad.push('Plus-Checkout ohne Konto aufgerufen');
  // Arbeitsbuch als Gast → Stripe Checkout
  await p.goto('http://localhost:8765/arbeitsbuch/'); await p.waitForTimeout(600);
  if (await p.evaluate(() => document.getElementById('abBuy').hidden)) bad.push('Eingeschaltet: Arbeitsbuch-Kaufknopf fehlt');
  else { await p.click('#abBuy'); await p.waitForURL('https://checkout.stripe.com/**', { timeout: 5000 }).catch(() => bad.push('Keine Weiterleitung zu Stripe Checkout')); if (!p.calls.some(c => /billing-checkout .*"item":"workbook"/.test(c))) bad.push('Arbeitsbuch-Checkout falsch aufgerufen: ' + p.calls); }
  // Aktionslink ?code=KOMPASS20 → Preis 7,99 € angezeigt und Code an den Server übergeben
  p = await page(true);
  await p.goto('http://localhost:8765/arbeitsbuch/?code=kompass20'); await p.waitForTimeout(600);
  const pr = await p.evaluate(() => document.getElementById('abBuy').innerText + ' | ' + (document.querySelector('.abcode') || {}).innerText);
  if (!/7,99/.test(pr) || !/KOMPASS20/.test(pr)) bad.push('Aktionslink zeigt keinen Rabatt: ' + pr);
  await p.click('#abBuy'); await p.waitForURL('https://checkout.stripe.com/**', { timeout: 5000 }).catch(() => {});
  if (!p.calls.some(c => /"code":"KOMPASS20"/.test(c))) bad.push('Aktionscode nicht an Checkout übergeben: ' + p.calls);
  // 3) Danke-Seite
  p = await page(true, { kind: 'gk_workbook_de', status: 'paid', download: 'https://example.com/arbeitsbuch.pdf?token=x' });
  await p.goto('http://localhost:8765/plus/danke/?lang=de&session_id=cs_test_' + 'a'.repeat(30)); await p.waitForTimeout(1500);
  const wb = await p.evaluate(() => { const a = document.querySelector('#thxState a'); return a ? a.href : document.getElementById('thxState').innerText; });
  if (!/arbeitsbuch\.pdf/.test(wb)) bad.push('Danke-Seite ohne Download: ' + wb);
  p = await page(true, { kind: 'plus', status: 'active' });
  await p.goto('http://localhost:8765/plus/danke/?lang=de&session_id=cs_test_' + 'b'.repeat(30)); await p.waitForTimeout(1500);
  if (!/Plus ist aktiv/.test(await p.evaluate(() => document.getElementById('thxState').innerText))) bad.push('Danke-Seite: Plus nicht bestätigt');
  // Dankeschön: nach dem Arbeitsbuch-Kauf 30 Tage Plus gratis → Link in die App, Plus-Fenster zeigt das Angebot
  p = await page(true, { kind: 'gk_workbook_de', status: 'paid', download: 'https://example.com/arbeitsbuch.pdf?token=x' });
  const sid = 'cs_test_' + 'c'.repeat(30);
  await p.goto('http://localhost:8765/plus/danke/?lang=de&session_id=' + sid); await p.waitForTimeout(1500);
  const tg = await p.evaluate(() => { const a = document.getElementById('trialGo'); return a ? a.getAttribute('href') : ''; });
  if (!tg.includes('trial=' + sid) || !/30 Tage kostenlos/.test(await p.evaluate(() => document.getElementById('thxState').innerText))) bad.push('Danke-Seite ohne 30-Tage-Angebot: ' + tg);
  else { await p.goto('http://localhost:8765' + tg); await p.waitForTimeout(1500);
    const td = await p.evaluate(() => { const x = document.getElementById('plusDlg'); return x ? x.querySelector('#plusGo').innerText + ' | ' + ((x.querySelector('.plustrial') || {}).innerText || '') : 'kein Dialog'; });
    if (!/30 Tage kostenlos starten/.test(td) || !/ersten 30 Tage sind kostenlos/.test(td)) bad.push('Plus-Fenster zeigt das Gratis-Angebot nicht: ' + td); }
  p = await page(true, { kind: 'plus', status: 'trialing' });
  await p.goto('http://localhost:8765/plus/danke/?lang=de&session_id=' + 'cs_test_' + 'd'.repeat(30)); await p.waitForTimeout(1500);
  if (!/30 Tage Plus laufen/.test(await p.evaluate(() => document.getElementById('thxState').innerText))) bad.push('Danke-Seite: Testphase nicht bestätigt');
  await b.close();
  if (bad.length) { console.error('Bezahlweg FEHLER', bad); process.exit(1); }
  console.log('Bezahlweg: ausgeschaltet ohne Kaufknöpfe, Plus-Fenster (Jahr vorausgewählt, 39 € / 4,99 €), Anmeldung nötig, Arbeitsbuch-Checkout, Danke-Seite mit Download und Plus-Bestätigung, 30 Tage Plus gratis für Arbeitsbuch-Käufer');
})();
