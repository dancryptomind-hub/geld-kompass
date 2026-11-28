// Wise Business Webhook-Empfänger (balances#credit / transfers#state-change).
// Prüft RSA-SHA256-Signatur (X-Signature-SHA256) gegen WISE_WEBHOOK_PUBLIC_KEY und markiert passende
// billing.wise_payments-Einträge idempotent als bezahlt. Stripe (billing-webhook) bleibt unverändert.
import { sql } from "../_shared/billing.ts";
import { extractWiseReference, verifyWiseSignature } from "../_shared/wise.ts";

Deno.serve(async (req) => {
  if (req.method !== "POST") return new Response("method_not_allowed", { status: 405 });
  const pubKey = Deno.env.get("WISE_WEBHOOK_PUBLIC_KEY") || "";
  if (!pubKey) return new Response("wise_webhook_not_configured", { status: 503 });

  const sig = req.headers.get("x-signature-sha256") || "";
  const raw = await req.text();
  if (raw.length > 65536) return new Response("too_large", { status: 413 });

  const valid = await verifyWiseSignature(raw, sig, pubKey);
  if (!valid) return new Response("invalid_signature", { status: 401 });

  let evt: Record<string, unknown>;
  try {
    evt = JSON.parse(raw) as Record<string, unknown>;
  } catch {
    return new Response("invalid_json", { status: 400 });
  }

  const eventType = String(evt.event_type || "");
  if (eventType !== "balances#credit" && eventType !== "transfers#state-change") {
    return new Response("ignored", { status: 200 });
  }

  const data = (evt.data && typeof evt.data === "object" ? evt.data : {}) as Record<string, unknown>;
  const currency = String(data.currency || "EUR").toUpperCase();
  const amountNum = Number(data.amount || 0);
  const amountCents = Math.round(amountNum * 100);
  const transferId = String(
    (data.resource && typeof data.resource === "object" ? (data.resource as Record<string, unknown>).id : "") ||
    data.transfer_id ||
    evt.subscription_id ||
    "",
  );
  const ref = extractWiseReference(
    String(data.reference || data.payment_reference || data.description || raw),
  );
  if (!ref || currency !== "EUR" || amountCents <= 0) {
    return new Response("no_matching_reference", { status: 200 });
  }

  await sql()`
    update billing.wise_payments
    set status = 'paid',
        wise_transfer_id = coalesce(wise_transfer_id, ${transferId || null}),
        paid_at = coalesce(paid_at, now())
    where reference = ${ref}
      and currency = 'EUR'
      and amount_cents <= ${amountCents}
      and status = 'pending'
  `;

  return new Response("ok", { status: 200 });
});
