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

  const isPlus = item.startsWith("plus_");
  if (c.mode === "subscription" && user) {
    const live = await sql()`select 1 from billing.subscriptions where user_id = ${user.id} and status in ('active','trialing','past_due') limit 1`;
    if (live.length) return json(req, { already: true });
  }
  let trialDays = 0, plusIntentId: string | null = null;
  if (isPlus && user) {
    const rawTrial = typeof body.trial === "string" && body.trial ? body.trial : "";
    if (rawTrial && !/^cs_(test|live)_[A-Za-z0-9]{20,}$/.test(rawTrial)) throw new HttpError(400, "trial_invalid");
    const prev = await sql()`select id, item, workbook_session, state, checkout_session_id from billing.plus_checkouts where user_id = ${user.id} and state in ('reserved','pending') limit 1`;
    if (prev[0]) {
      const p = prev[0];
      if (p.checkout_session_id) {
        const existing = await stripe().checkout.sessions.retrieve(p.checkout_session_id as string).catch(() => null);
        if (existing?.status === "complete") throw new HttpError(409, "checkout_pending");
        if (existing?.status === "open" && p.item === item && (p.workbook_session || "") === rawTrial && existing.url) {
          return json(req, { url: existing.url });
        }
        if (existing?.status === "open") {
          await stripe().checkout.sessions.expire(existing.id).catch(() => null);
        }
      }
      await sql()`delete from billing.plus_checkouts where id = ${p.id} and state in ('reserved','pending')`;
    }
    let r: Record<string, unknown>;
    try {
      const rows = await sql()`select * from billing.reserve_plus_checkout(${user.id}, ${item}, ${lang}, ${rawTrial || null})`;
      r = rows[0];
    } catch (e) {
      const m = String((e as Error)?.message || "");
      if (m.includes("already_active")) return json(req, { already: true });
      if (m.includes("founders_sold_out")) throw new HttpError(409, "founders_sold_out");
      if (m.includes("trial_invalid")) throw new HttpError(409, "trial_invalid");
      throw e;
    }
    plusIntentId = String(r.id);
    trialDays = Number(r.trial_days) || 0;
  }
  const price = await ensurePrice(item);
  const customer = user ? await customerFor(user) : undefined;
  const promo = item === "workbook" && typeof body.code === "string" && /^[A-Za-z0-9]{3,20}$/.test(body.code) ? await ensurePromo(body.code) : null;
  if (!promo && item === "workbook") await ensurePromo("KOMPASS20").catch(() => null); // Code existiert dann auch für manuelle Eingabe
  const mp = managedPayments();
  const back = isPlus ? `${SITE}/app/?lang=${lang}#plus` : item === "report" ? `${SITE}/app/?lang=${lang}#data` : `${SITE}/arbeitsbuch/`;
  let session;
  try {
    session = await stripe().checkout.sessions.create({
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
      ...(c.mode === "subscription" ? { subscription_data: { metadata: { gk_user: user!.id, gk_item: item }, ...(trialDays ? { trial_period_days: trialDays, trial_settings: { end_behavior: { missing_payment_method: "cancel" as const } } } : {}) } } : mp ? {} : { payment_intent_data: { metadata: { gk_item: item, ...(plusIntentId ? { gk_intent: plusIntentId, gk_plus_intent: plusIntentId, gk_user: user!.id } : {}) } } }),
      ...(!mp && Deno.env.get("TOS_CONSENT") === "1" ? { consent_collection: { terms_of_service: "required" } } : {}),
      ...checkoutText(mp, lang === "en"
        ? (isPlus ? (c.mode === "payment" ? "Plus activates immediately for the full period, with no renewal." : (trialDays ? `${trialDays} days free, then the price shown. Cancel anytime in your account.` : "You can cancel anytime in your account. Plus stays active until the end of the paid period.")) : (item === "report" ? "Report generation unlocks right after payment confirmation." : "PDF access starts after your payment has been confirmed."))
        : (isPlus ? (c.mode === "payment" ? "Plus startet sofort für die volle Laufzeit, ohne automatische Verlängerung." : (trialDays ? `${trialDays} Tage kostenlos, danach der angezeigte Preis. Jederzeit im Konto kündbar.` : "Jederzeit kündbar im Konto. Plus bleibt bis zum Ende des bezahlten Zeitraums aktiv.")) : (item === "report" ? "Der Report wird direkt nach Zahlungsbestätigung in der App freigeschaltet." : "Die PDF steht nach bestätigter Zahlung bereit."))),
      metadata: { gk_item: item, ...(plusIntentId ? { gk_intent: plusIntentId, gk_plus_intent: plusIntentId, gk_user: user!.id } : {}) },
    }, plusIntentId ? { idempotencyKey: "gk-plus-" + plusIntentId } : undefined);
  } catch (e) {
    if (plusIntentId) await sql()`delete from billing.plus_checkouts where id = ${plusIntentId}::uuid and state = 'reserved'`.catch(() => {});
    throw e;
  }
  if (plusIntentId) {
    await sql()`update billing.plus_checkouts set state = 'pending', checkout_session_id = ${session.id} where id = ${plusIntentId}::uuid`;
  } else if (c.mode === "payment") {
    await sql()`insert into billing.purchases (checkout_session_id, user_id, email, product, status) values (${session.id}, ${user?.id ?? null}, ${user?.email ?? null}, ${c.product}, 'open') on conflict do nothing`;
  }
  return json(req, { url: session.url });
}));
