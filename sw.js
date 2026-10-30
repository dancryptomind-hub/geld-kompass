/* Geld-Kompass Service Worker: App-Installation und Offline-Nutzung.
   Seiten und Daten: zuerst aus dem Netz (immer aktuell), offline aus dem Speicher.
   Schriften und Symbole: aus dem Speicher (ändern sich selten). */
var VERSION = 'gk-2026-10-31-1';
var CORE = ['/', '/app/', '/i18n.js', '/inflation.js', '/journey.js', '/journey-ui.js', '/retirement.js',
  '/data/markets.json', '/data/hicp_annual.json', '/manifest.webmanifest',
  '/assets/Figtree-400.ttf', '/assets/Figtree-600.ttf', '/assets/Figtree-700.ttf', '/assets/Figtree-800.ttf', '/assets/PlayfairDisplay-700.ttf',
  '/icons/icon-192.png', '/icons/icon-512.png', '/start/', '/buchbegruessung/', '/site.css', '/rechner/', '/rechner/rechner.css', '/rechner/rechner.js'];
self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(VERSION).then(function (c) {
    return Promise.all(CORE.map(function (u) { return c.add(u).catch(function () {}); }));
  }).then(function () { return self.skipWaiting(); }));
});
self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k !== VERSION; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});
self.addEventListener('fetch', function (e) {
  var req = e.request, url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== self.location.origin) return;
  var stat = /\.(ttf|png|jpg|svg|ico)$/.test(url.pathname);
  if (stat) {
    e.respondWith(caches.match(req).then(function (hit) {
      return hit || fetch(req).then(function (res) { var cp = res.clone(); caches.open(VERSION).then(function (c) { c.put(req, cp); }); return res; });
    }));
    return;
  }
  e.respondWith(fetch(req).then(function (res) {
    if (res.ok) { var cp = res.clone(); caches.open(VERSION).then(function (c) { c.put(req, cp); }); }
    return res;
  }).catch(function () {
    return caches.match(req, { ignoreSearch: true }).then(function (hit) {
      return hit || (req.mode === 'navigate' ? caches.match(url.pathname.indexOf('/app') === 0 ? '/app/' : '/') : Response.error());
    });
  }));
});
