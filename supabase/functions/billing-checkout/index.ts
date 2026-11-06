// POST {item: "plus_monthly"|"plus_yearly"|"workbook"|"report", lang?: "de"|"en"} → {url} zur Stripe-Checkout-Seite.
// Plus braucht ein angemeldetes Konto (Freischaltung hängt am Konto). Arbeitsbuch geht auch als Gast.
import { handle, json, HttpError, CATALOG, ensurePrice, customerFor, stripe, sql, userFrom, SITE } from "../_shared/billing.ts";

Deno.serve(handle(async (req) => {
  if (req.method !== "POST") throw new HttpError(405, "method_not_allowed");
  const body = await req.json().catch(() => ({}));
  const item = String(body.item || "") as keyof typeof CATALOG;
  const c = CATALOG[item];
  if (!c) throw new HttpError(400, "unknown_item");
  if (c.enabledEnv && Deno.env.get(c.enabledEnv) !== "1") throw new HttpError(404, "not_available");
  const lang = body.lang === "en" ? "en" : "de";
  const user = await userFrom(req);
  if (c.needsUser && (!user || !user.email_confirmed_at)) throw new HttpError(401, "login_required");

  if (c.mode === "subscription" && user) {
    const live = await sql()`select 1 from billing.subscriptions where user_id = ${user.id} and status in ('active','trialing','past_due') limit 1`;
    if (live.length) return json(req, { already: true });
  }
  const price = await ensurePrice(item);
  const customer = user ? await customerFor(user) : undefined;
  const back = c.mode === "subscription" ? `${SITE}/app/?lang=${lang}#plus` : `${SITE}/arbeitsbuch/`;
  const session = await stripe().checkout.sessions.create({
    mode: c.mode,
    line_items: [{ price, quantity: 1 }],
    ...(customer ? { customer } : { customer_creation: c.mode === "payment" ? "always" : undefined }),
    client_reference_id: user?.id,
    success_url: `${SITE}/plus/danke/?session_id={CHECKOUT_SESSION_ID}&lang=${lang}`,
    cancel_url: back,
    locale: lang,
    allow_promotion_codes: true,
    billing_address_collection: "auto",
    integration_identifier: "gk_app_checkout_QWMRTZKB",
    ...(c.mode === "subscription" ? { subscription_data: { metadata: { gk_user: user!.id, gk_item: item } } } : { payment_intent_data: { metadata: { gk_item: item } } }),
    ...(Deno.env.get("TOS_CONSENT") === "1" ? { consent_collection: { terms_of_service: "required" } } : {}),
    custom_text: { submit: { message: lang === "en"
      ? (c.mode === "payment" ? "Digital content: access starts right after payment. By paying you agree that your right of withdrawal ends once the download starts." : "You can cancel anytime in your account. Plus stays active until the end of the paid period.")
      : (c.mode === "payment" ? "Digitaler Inhalt: Der Zugang startet direkt nach der Zahlung. Mit dem Kauf stimmst du zu, dass dein Widerrufsrecht mit Beginn des Downloads erlischt." : "Jederzeit kündbar im Konto. Plus bleibt bis zum Ende des bezahlten Zeitraums aktiv.") } },
    metadata: { gk_item: item },
  });
  if (c.mode === "payment") {
    await sql()`insert into billing.purchases (checkout_session_id, user_id, email, product, status) values (${session.id}, ${user?.id ?? null}, ${user?.email ?? null}, ${c.product}, 'open') on conflict do nothing`;
  }
  return json(req, { url: session.url });
}));
