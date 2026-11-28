/* Bezahlwege des Geld-Kompass Pro: Stripe (aktiv) + optional Wise Business (zusätzliche Alternative, erst bei wiseEnabled:true sichtbar).
   Keine geheimen Schlüssel in diese Datei: alle Stripe- und Wise-Schlüssel liegen ausschließlich als Supabase-Secrets vor. */
window.GK_BILLING = Object.freeze({
  enabled: true,
  plusEnabled: true,
  reportEnabled: true,
  wiseEnabled: false,
  providers: Object.freeze({ stripe: true, wise: false }),
  mode: "live",
  functions: "https://cwznthfefbeglamnwyry.supabase.co/functions/v1/",
  apikey: "sb_publishable_OAzhy63__bAdBHq7H7NqUA_RqxB_qhc",
  prices: { plus_monthly: 4.99, plus_yearly: 39, plus_5y: 149, plus_10y: 249, workbook: 9.99, report: 14.99, whitelabel_pro_yearly: 468, whitelabel_pro_monthly: 49, whitelabel_team_yearly: 1428, whitelabel_team_monthly: 149 }
});
/* Gemeinsamer Aufruf für App, Arbeitsbuch-Seite und Danke-Seite */
window.GK_billingCall = function (fn, opts) {
  var B = window.GK_BILLING, o = opts || {}, h = { apikey: B.apikey, "Content-Type": "application/json" };
  if (o.token) h.Authorization = "Bearer " + o.token;
  return fetch(B.functions + fn + (o.query || ""), { method: o.body ? "POST" : "GET", headers: h, body: o.body ? JSON.stringify(o.body) : undefined })
    .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { j._status = r.status; return j; }); });
};
