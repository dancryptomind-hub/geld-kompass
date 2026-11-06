// POST → {url} zum Stripe-Kundenportal (Abo kündigen, Zahlungsart, Rechnungen). Nur für angemeldete Konten.
import { handle, json, HttpError, stripe, sql, userFrom, SITE } from "../_shared/billing.ts";

async function portalConfig(): Promise<string | undefined> {
  const s = stripe();
  const list = await s.billingPortal.configurations.list({ is_default: true, active: true, limit: 1 });
  if (list.data[0]) return undefined;
  const cfg = await s.billingPortal.configurations.create({
    business_profile: { headline: "Geld-Kompass Pro" },
    features: {
      customer_update: { enabled: true, allowed_updates: ["email", "address"] },
      invoice_history: { enabled: true },
      payment_method_update: { enabled: true },
      subscription_cancel: { enabled: true, mode: "at_period_end" },
    },
  }, { idempotencyKey: "gk_portal_config_v1" });
  return cfg.id;
}

Deno.serve(handle(async (req) => {
  if (req.method !== "POST") throw new HttpError(405, "method_not_allowed");
  const user = await userFrom(req);
  if (!user) throw new HttpError(401, "login_required");
  const body = await req.json().catch(() => ({}));
  const lang = body.lang === "en" ? "en" : "de";
  const rows = await sql()`select stripe_customer_id from billing.customers where user_id = ${user.id}`;
  if (!rows[0]) throw new HttpError(404, "no_customer");
  const configuration = await portalConfig();
  const session = await stripe().billingPortal.sessions.create({ customer: rows[0].stripe_customer_id as string, return_url: `${SITE}/app/?lang=${lang}#data`, locale: lang, ...(configuration ? { configuration } : {}) });
  return json(req, { url: session.url });
}));
