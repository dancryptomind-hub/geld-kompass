/* Smart-TV-Edition (/tv/): ausschließlich ab aktivem Geld-Kompass Plus oder Admin herunterladbar.
   Gäste und Free-Konten (auch gefälschtes user_metadata.gk_plus) erhalten keinen Download-Button. */
const assert = require('node:assert/strict');
const BT = require(process.env.PLAYWRIGHT_MODULE || 'playwright')[process.env.GK_BROWSER || 'chromium'];
const BASE = process.env.BASE || 'http://localhost:8765';

(async () => {
  const b = await BT.launch();
  try {
    const cases = [
      { name: 'guest', session: false, meta: {} },
      { name: 'forged-user-meta', session: true, meta: {}, userMeta: { gk_plus: { active: true, until: Date.now() + 864e5 } } },
      { name: 'expired-plus', session: true, meta: { gk_plus: { active: true, until: Date.now() - 1000 } } },
      { name: 'active-plus', session: true, meta: { gk_plus: { active: true, until: Date.now() + 864e5 } } }
    ];
    for (const tc of cases) {
      const c = await b.newContext({ viewport: { width: 1280, height: 900 }, serviceWorkers: 'block' });
      const user = {
        id: 'u-' + tc.name,
        email: tc.name + '@example.com',
        email_confirmed_at: '2026-01-01T00:00:00Z',
        aud: 'authenticated',
        role: 'authenticated',
        app_metadata: tc.meta,
        user_metadata: tc.userMeta || {}
      };
      const jwt = ['eyJhbGciOiJIUzI1NiJ9', Buffer.from(JSON.stringify({ sub: user.id, exp: Math.floor(Date.now() / 1000) + 3600 })).toString('base64url'), 'sig'].join('.');
      let dlCalls = 0;
      if (tc.session) {
        await c.addInitScript(({ user, jwt }) => {
          localStorage.setItem('gk.account.v1', JSON.stringify({
            access_token: jwt,
            refresh_token: 'r',
            expires_at: Math.floor(Date.now() / 1000) + 3600,
            expires_in: 3600,
            token_type: 'bearer',
            user
          }));
        }, { user, jwt });
      }
      await c.route('**/*', r => {
        const u = r.request().url();
        if (u.endsWith('/konto/config.js')) {
          return r.fulfill({ contentType: 'application/javascript', body: 'window.GK_ACCOUNT_CONFIG={url:"https://cwznthfefbeglamnwyry.supabase.co",key:"fixture-key",registrationOpen:true};' });
        }
        if (u.includes('/auth/v1/user')) {
          return r.fulfill({ headers: { 'access-control-allow-origin': '*', 'access-control-allow-headers': '*' }, json: user });
        }
        if (u.includes('/functions/v1/tv-download')) {
          dlCalls++;
          if (tc.name === 'active-plus') {
            if (u.includes('info=1')) {
              return r.fulfill({ headers: { 'access-control-allow-origin': '*', 'access-control-allow-headers': '*' }, json: { ok: true, plus: true, version: '1.0.0', filename: 'Geld-Kompass-Pro-TV.zip', sizeBytes: 14348 } });
            }
            return r.fulfill({ status: 200, headers: { 'access-control-allow-origin': '*', 'access-control-allow-headers': '*' }, contentType: 'application/zip', body: Buffer.from('PK\x03\x04mock') });
          }
          return r.fulfill({ status: 403, headers: { 'access-control-allow-origin': '*', 'access-control-allow-headers': '*' }, json: { error: 'plus_required' } });
        }
        return u.startsWith(BASE) ? r.continue() : r.abort();
      });

      const p = await c.newPage();
      const errs = [];
      p.on('pageerror', e => errs.push(e.message));
      await p.goto(BASE + '/tv/?lang=de');
      await p.waitForTimeout(800);

      if (tc.name === 'active-plus') {
        await p.locator('#tvDownloadBtn').waitFor({ state: 'visible', timeout: 4000 });
        await p.click('#tvDownloadBtn');
        await p.locator('#tvMsg').filter({ hasText: /Geld-Kompass-Pro-TV\.zip/ }).waitFor({ timeout: 3000 });
        assert.ok(dlCalls >= 2, 'tv-download info + zip fetched');
      } else {
        assert.equal(await p.locator('#tvDownloadBtn').count(), 0, tc.name + ' must NOT see download button');
      }
      assert.deepEqual(errs, [], tc.name + ' zero pageerrors');
      await c.close();
    }
    console.log('OK tv-plus-gate: guest, forged, expired blocked; active Plus unlocked');
  } finally {
    await b.close();
  }
})().catch(e => { console.error(e); process.exitCode = 1; });
