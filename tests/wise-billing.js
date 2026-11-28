/* Wise Business als zusätzliche Zahlungsalternative neben Stripe:
   1) wiseEnabled: false (Standard) -> #abBuyWise verborgen, #abBuy (Stripe) sichtbar & funktionsfähig.
   2) wiseEnabled: true -> sowohl #abBuy (Stripe) als auch #abBuyWise (Wise Business) sichtbar;
      Wise-Klick ruft wise-checkout auf und verarbeitet sowohl bank_transfer als auch payment_link. */
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const engine = process.env.GK_TEST_BROWSER === 'webkit' ? require('playwright').webkit : chromium;
  const base = process.env.GK_TEST_BASE || 'http://localhost:8765';
  const b = await engine.launch();
  const bad = [];
  const cfg = fs.readFileSync(__dirname + '/../billing-config.js', 'utf8');

  async function openPage(wiseEnabled, wiseResponse) {
    const c = await b.newContext({ viewport: { width: 1280, height: 900 }, serviceWorkers: 'block', locale: 'de-DE' });
    const p = await c.newPage();
    p.errs = [];
    p.on('pageerror', e => p.errs.push(e.message));
    await p.route('**/billing-config.js*', r => r.fulfill({
      contentType: 'text/javascript',
      body: cfg.replace(/wiseEnabled:\s*(true|false)/, 'wiseEnabled: ' + wiseEnabled),
    }));
    p.calls = [];
    await p.route('https://cwznthfefbeglamnwyry.supabase.co/functions/v1/**', r => {
      const u = r.request().url();
      p.calls.push(u.split('/v1/')[1] + ' ' + (r.request().postData() || ''));
      if (/wise-checkout/.test(u)) {
        return r.fulfill({
          contentType: 'application/json',
          headers: { 'access-control-allow-origin': '*' },
          body: JSON.stringify(wiseResponse),
        });
      }
      return r.fulfill({ status: 404, body: '{}' });
    });
    await p.route('https://wise.com/**', r => r.fulfill({ contentType: 'text/html', body: '<h1>Wise Checkout (Test)</h1>' }));
    return p;
  }

  // 1) Standard: wiseEnabled=false -> Wise-Knopf verborgen, Stripe-Knopf sichtbar
  let p = await openPage(false, {});
  await p.goto(base + '/arbeitsbuch/');
  await p.waitForTimeout(400);
  const s1 = await p.evaluate(() => ({
    stripeHidden: document.getElementById('abBuy').hidden,
    wiseHidden: document.getElementById('abBuyWise').hidden,
  }));
  if (s1.stripeHidden || !s1.wiseHidden) bad.push('Standardmodus falsch: ' + JSON.stringify(s1));
  if (p.errs.length) bad.push('JS-Fehler (wise=false): ' + p.errs.join('; '));
  await p.context().close();

  // 2) wiseEnabled=true + Banküberweisung (DE)
  p = await openPage(true, {
    provider: 'wise', mode: 'bank_transfer', item: 'workbook',
    reference: 'GK-WISE-WB-1234ABCD', amount_eur: 9.99, currency: 'EUR',
    beneficiary: 'FreedomByDan LLC', iban: 'BE68539007547034', bic: 'TRWIBEB1XXX',
  });
  await p.goto(base + '/arbeitsbuch/');
  await p.waitForTimeout(400);
  const s2 = await p.evaluate(() => ({
    stripeHidden: document.getElementById('abBuy').hidden,
    wiseHidden: document.getElementById('abBuyWise').hidden,
  }));
  if (s2.stripeHidden || s2.wiseHidden) bad.push('Aktivmodus: Stripe oder Wise fehlt: ' + JSON.stringify(s2));
  await p.click('#abBuyWise');
  await p.waitForTimeout(400);
  const boxText = await p.evaluate(() => document.getElementById('abWiseBox').innerText);
  if (!boxText.includes('GK-WISE-WB-1234ABCD') || !boxText.includes('BE68539007547034')) {
    bad.push('Wise-Überweisungshinweis unvollständig: ' + boxText);
  }
  if (!p.calls.some(c => /wise-checkout .*"item":"workbook"/.test(c))) bad.push('wise-checkout nicht aufgerufen: ' + p.calls);
  if (p.errs.length) bad.push('JS-Fehler (wise bank_transfer): ' + p.errs.join('; '));
  await p.context().close();

  // 3) wiseEnabled=true + Payment Link (EN)
  p = await openPage(true, {
    provider: 'wise', mode: 'payment_link', item: 'workbook',
    reference: 'GK-WISE-WB-99887766', amount_eur: 9.99, currency: 'EUR',
    url: 'https://wise.com/pay/business/test-mock',
  });
  await p.goto(base + '/en/workbook/');
  await p.waitForTimeout(400);
  await p.click('#abBuyWise');
  await p.waitForURL('https://wise.com/**', { timeout: 5000 }).catch(() => bad.push('EN: Keine Weiterleitung zum Wise Payment Link'));
  if (p.errs.length) bad.push('JS-Fehler (wise payment_link): ' + p.errs.join('; '));
  await p.context().close();

  await b.close();
  if (bad.length) { console.error('Wise-Billing FEHLER:', bad); process.exit(1); }
  console.log('Wise-Billing: Standard verborgen (Stripe unverändert), Aktivmodus DE/EN (Banküberweisung + Payment Link) bestanden');
})();
