/* Stripe-Bezahlweg des Geld-Kompass Pro. enabled:false = keine Kaufknöpfe sichtbar (Stripe noch nicht eingerichtet).
   Erst auf true stellen, wenn STRIPE_SECRET_KEY und STRIPE_WEBHOOK_SECRET in Supabase gesetzt sind und ein Testkauf geklappt hat.
   Keine geheimen Schlüssel in diese Datei: der öffentliche Stripe-Schlüssel wird für Checkout nicht gebraucht. */
window.GK_BILLING = Object.freeze({
  enabled: false,
  mode: "test",
  functions: "https://cwznthfefbeglamnwyry.supabase.co/functions/v1/",
  apikey: "sb_publishable_OAzhy63__bAdBHq7H7NqUA_RqxB_qhc",
  prices: { plus_monthly: 4.99, plus_yearly: 39, plus_5y: 149, plus_10y: 249, founders: 100, workbook: 9.99, report: 14.99 }
});
/* Gemeinsamer Aufruf für App, Arbeitsbuch-Seite und Danke-Seite */
window.GK_billingCall = function (fn, opts) {
  var B = window.GK_BILLING, o = opts || {}, h = { apikey: B.apikey, "Content-Type": "application/json" };
  if (o.token) h.Authorization = "Bearer " + o.token;
  return fetch(B.functions + fn + (o.query || ""), { method: o.body ? "POST" : "GET", headers: h, body: o.body ? JSON.stringify(o.body) : undefined })
    .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { j._status = r.status; return j; }); });
};
