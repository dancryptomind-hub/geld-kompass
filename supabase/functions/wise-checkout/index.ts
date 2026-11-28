// POST { item: "workbook"|"report"|"plus_yearly"|"plus_5y"|"plus_10y"|"whitelabel_...", lang?: "de"|"en" }
// → Wise Business Zahlungsanweisung (Payment Link oder Banküberweisung mit eindeutiger Referenz).
// Stripe (billing-checkout) bleibt vollständig unverändert erhalten.
import { handle, json, HttpError, readJson, rateLimit, sql, userFrom } from "../_shared/billing.ts";
import { buildWiseReference, resolveWiseInstruction, wiseCatalogItem, wiseEnabledError } from "../_shared/wise.ts";

Deno.serve(handle(async (req) => {
  if (req.method !== "POST") throw new HttpError(405, "method_not_allowed");
  const env = {
    WISE_ENABLED: Deno.env.get("WISE_ENABLED"),
    WISE_PAYMENT_LINKS_JSON: Deno.env.get("WISE_PAYMENT_LINKS_JSON"),
    WISE_ACCOUNT_IBAN: Deno.env.get("WISE_ACCOUNT_IBAN"),
    WISE_ACCOUNT_HOLDER: Deno.env.get("WISE_ACCOUNT_HOLDER"),
    WISE_ACCOUNT_BIC: Deno.env.get("WISE_ACCOUNT_BIC"),
  };
  const disabled = wiseEnabledError(env);
  if (disabled) throw new HttpError(503, disabled);

  const body = await readJson(req);
  const found = wiseCatalogItem(body.item);
  if (!found) throw new HttpError(400, "unknown_item");

  await rateLimit(req, "wise_checkout", 10, 600);
  const lang = body.lang === "en" ? "en" : "de";
  const user = await userFrom(req);
  if (found.item.needsUser && (!user || !user.email_confirmed_at)) {
    throw new HttpError(401, "login_required");
  }
  if (user) await rateLimit(req, "wise_checkout_user", 20, 3600, user.id);

  const reference = buildWiseReference(found.item.code);
  const instruction = resolveWiseInstruction(found.key, found.item, reference, env);
  if (!instruction) throw new HttpError(503, "wise_not_configured");

  await sql()`
    insert into billing.wise_payments (reference, user_id, item, amount_cents, currency, mode, status, lang)
    values (${reference}, ${user?.id ?? null}, ${found.key}, ${found.item.amountCents}, ${found.item.currency}, ${instruction.mode}, 'pending', ${lang})
  `;

  return json(req, instruction, 200);
}));
