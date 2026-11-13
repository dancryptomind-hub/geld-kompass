// POST {item: "plus_monthly"|"plus_yearly"|"workbook"|"report", lang?: "de"|"en", code?: Aktionscode (Arbeitsbuch), trial?: Checkout-ID eines bezahlten Arbeitsbuch-Kaufs} → {url} zur Stripe-Checkout-Seite.
// Plus braucht ein angemeldetes Konto (Freischaltung hängt am Konto). Arbeitsbuch geht auch als Gast.
import { handle, json, HttpError, CATALOG, catalogItem, readJson, rateLimit, ensurePrice, ensurePromo, managedPayments, checkoutText, customerFor, stripe, sql, userFrom, SITE } from "../_shared/billing.ts";

import { releaseError } from "../_shared/release-policy.ts";

Deno.serve(handle(async (req) => {
  if (req.method !== "POST") throw new HttpError(405, "method_not_allowed");
  const body = await readJson(req);
  const found = catalogItem(body.item);
  if (!found) throw new HttpError(400, "unknown_item");
  const item = found.key, c = found.c;
  const release = releaseError(item, { WORKBOOK_ENABLED: Deno.env.get("WORKBOOK_ENABLED"), PLUS_ENABLED: Deno.env.get("PLUS_ENABLED"), REPORT_ENABLED: Deno.env.get("REPORT_ENABLED"), MANAGED_PAYMENTS: Deno.env.get("MANAGED_PAYMENTS"), TOS_CONSENT: Deno.env.get("TOS_CONSENT") });
  if (release) throw new HttpError(503, release);
  await rateLimit(req, "checkout", 10, 600);
  if (c.enabledEnv && Deno.env.get(c.enabledEnv) !== "1") throw new HttpError(404, "not_available");
  const lang = body.lang === "en" ? "en" : "de";
  const user = await userFrom(req);
  if (c.needsUser && (!user || !user.email_confirmed_at)) throw new HttpError(401, "login_required");
  if (user) await rateLimit(req, "checkout_user", 20, 3600, user.id);

  if (c.mode === "subscription" && user) {
    const live = await sql()`select 1 from billing.subscriptions where user_id = ${user.id} and status in ('active','trialing','past_due') limit 1`;
    if (live.length) return json(req, { already: true });
  }
  // Dankeschön für Arbeitsbuch-Käufer: 30 Tage Plus kostenlos, einmal pro Kauf und nur für Konten ohne früheres Abo.
  let trialDays = 0;
  if (c.mode === "subscription" && typeof body.trial === "string" && body.trial) {
    if (!/^cs_(test|live)_[A-Za-z0-9]{20,}$/.test(body.trial)) throw new HttpError(400, "trial_invalid");
    const before = await sql()`select 1 from billing.subscriptions where user_id = ${user!.id} limit 1`;
    if (before.length) throw new HttpError(409, "trial_invalid");
    // Atomar beanspruchen: gleichzeitige Anfragen zweier Konten können denselben Kauf nicht doppelt nutzen.
    const ok = await sql()`update billing.purchases set trial_user_id = ${user!.id} where checkout_session_id = ${body.trial} and product = 'gk_workbook_de' and status = 'paid' and (trial_user_id is null or trial_user_id = ${user!.id}) returning 1`;
    if (!ok.length) throw new HttpError(409, "trial_invalid");
    trialDays = 30;
  }
  const price = await ensurePrice(item);
  const customer = user ? await customerFor(user) : undefined;
  const promo = item === "workbook" && typeof body.code === "string" && /^[A-Za-z0-9]{3,20}$/.test(body.code) ? await ensurePromo(body.code) : null;
  if (!promo && item === "workbook") await ensurePromo("KOMPASS20").catch(() => null); // Code existiert dann auch für manuelle Eingabe
  const mp = managedPayments();
  const back = c.mode === "subscription" ? `${SITE}/app/?lang=${lang}#plus` : `${SITE}/arbeitsbuch/`;
  const session = await stripe().checkout.sessions.create({
    mode: c.mode,
    line_items: [{ price, quantity: 1 }],
    ...(customer ? { customer } : { customer_creation: c.mode === "payment" ? "always" : undefined }),
    client_reference_id: user?.id,
    success_url: `${SITE}/plus/danke/?session_id={CHECKOUT_SESSION_ID}&lang=${lang}`,
    cancel_url: back,
    locale: lang,
    ...(promo ? { discounts: [{ promotion_code: promo }] } : { allow_promotion_codes: true }),
    ...(mp ? { managed_payments: { enabled: true } } : { billing_address_collection: "auto" as const }),
    integration_identifier: "gk_app_checkout_QWMRTZKB",
    ...(c.mode === "subscription" ? { subscription_data: { metadata: { gk_user: user!.id, gk_item: item }, ...(trialDays ? { trial_period_days: trialDays, trial_settings: { end_behavior: { missing_payment_method: "cancel" as const } } } : {}) } } : mp ? {} : { payment_intent_data: { metadata: { gk_item: item } } }),
    ...(Deno.env.get("TOS_CONSENT") === "1" ? { consent_collection: { terms_of_service: "required" } } : {}),
    ...checkoutText(mp, lang === "en"
      ? (c.mode === "payment" ? "PDF access starts after your payment has been confirmed." : (trialDays ? "30 days free, then the price shown. You get a reminder email before the first charge and can cancel anytime in your account." : "You can cancel anytime in your account. Plus stays active until the end of the paid period."))
      : (c.mode === "payment" ? "Die PDF steht nach bestätigter Zahlung bereit." : (trialDays ? "30 Tage kostenlos, danach der angezeigte Preis. Vor der ersten Abbuchung bekommst du eine Erinnerung per E-Mail und kannst jederzeit im Konto kündigen." : "Jederzeit kündbar im Konto. Plus bleibt bis zum Ende des bezahlten Zeitraums aktiv."))),
    metadata: { gk_item: item },
  });
  if (c.mode === "payment") {
    await sql()`insert into billing.purchases (checkout_session_id, user_id, email, product, status) values (${session.id}, ${user?.id ?? null}, ${user?.email ?? null}, ${c.product}, 'open') on conflict do nothing`;
  }
  return json(req, { url: session.url });
}));
