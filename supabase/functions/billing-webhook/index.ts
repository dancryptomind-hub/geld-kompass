// Stripe-Webhook: einzige Quelle der Wahrheit für Freischaltung, Verlängerung, Kündigung, Erstattung, Streitfall und Betrugswarnung.
// Signatur wird geprüft, jedes Ereignis nur einmal verarbeitet (billing.webhook_events).
import type Stripe from "npm:stripe@23.1.0";
import { purchaseProduct } from "../_shared/fulfillment-policy.ts";
import { stripe, cryptoProvider, sql, syncSubscription, refreshEntitlement } from "../_shared/billing.ts";

async function setPurchase(pi: string | null | undefined, status: string) {
  if (!pi) return;
  await sql()`select billing.block_payment(${pi}, ${status})`;
  const affected = await sql()`select user_id from billing.plus_checkouts where payment_intent_id = ${pi}`;
  for (const r of affected) if (r.user_id) await refreshEntitlement(r.user_id as string);
}
async function fulfill(s: Stripe.Checkout.Session) {
  const intent = s.metadata?.gk_intent || s.metadata?.gk_plus_intent || "";
  if (s.mode === "subscription") {
    const sub = typeof s.subscription === "string" ? s.subscription : s.subscription?.id;
    if (sub) {
      await syncSubscription(sub);
      if (intent && /^[0-9a-f-]{36}$/.test(intent)) {
        await sql()`update billing.plus_checkouts set state = 'complete', checkout_session_id = ${s.id} where id = ${intent}::uuid and item in ('plus_monthly','plus_yearly')`;
      }
    }
    return;
  }
  if (s.mode === "payment" && intent && ["plus_5y", "plus_10y"].includes(s.metadata?.gk_item || "")) {
    if (!["paid", "no_payment_required"].includes(s.payment_status)) return;
    const pi = (typeof s.payment_intent === "string" ? s.payment_intent : s.payment_intent?.id) || s.id;
    let paidAt = new Date((s.created || Math.floor(Date.now() / 1000)) * 1000);
    if (pi.startsWith("pi_")) {
      const payment = await stripe().paymentIntents.retrieve(pi, { expand: ["latest_charge"] }).catch(() => null);
      const charge = payment?.latest_charge;
      if (charge && typeof charge !== "string" && charge.paid && charge.created) paidAt = new Date(charge.created * 1000);
    }
    const rows = await sql()`select billing.fulfill_plus_checkout(${intent}::uuid, ${s.id}, ${pi}, ${paidAt}) as uid`;
    if (rows[0]?.uid) await refreshEntitlement(rows[0].uid as string);
    return;
  }
  const product = purchaseProduct(s);
  if (!product) return; // Keine Freigabe für unbezahlte oder fremde Checkout-Sitzungen.
  const pi = typeof s.payment_intent === "string" ? s.payment_intent : s.payment_intent?.id || null;
  const email = s.customer_details?.email || null;
  await sql()`select billing.fulfill_purchase(${s.id}, ${pi}, ${email}, ${product}, ${s.amount_total}, ${s.currency})`;
}
function subFromInvoice(inv: Stripe.Invoice): string | null {
  const d = inv.parent?.subscription_details?.subscription;
  return typeof d === "string" ? d : d?.id || null;
}

Deno.serve(async (req) => {
  if (req.method !== "POST") return new Response("method_not_allowed", { status: 405 });
  const secret = Deno.env.get("STRIPE_WEBHOOK_SECRET");
  const sig = req.headers.get("stripe-signature");
  if (!secret || !sig) return new Response("not_configured", { status: 400 });
  const raw = await req.text();
  let event: Stripe.Event;
  try { event = await stripe().webhooks.constructEventAsync(raw, sig, secret, undefined, cryptoProvider); }
  catch { return new Response("bad_signature", { status: 400 }); }

  const db = sql();
  const seen = await db`insert into billing.webhook_events (id, type) values (${event.id}, ${event.type}) on conflict (id) do update set type = excluded.type returning processed_at`;
  if (seen[0]?.processed_at) return new Response("duplicate", { status: 200 });
  try {
    const o = event.data.object as unknown;
    switch (event.type) {
      case "checkout.session.completed":
      case "checkout.session.async_payment_succeeded":
        await fulfill(o as Stripe.Checkout.Session); break;
      case "checkout.session.expired": {
        const sess = o as Stripe.Checkout.Session;
        const intent = sess.metadata?.gk_intent || sess.metadata?.gk_plus_intent || "";
        if (intent && /^[0-9a-f-]{36}$/.test(intent)) {
          await db`update billing.plus_checkouts set state = 'expired' where id = ${intent}::uuid and (checkout_session_id is null or checkout_session_id = ${sess.id}) and state in ('reserved','pending')`;
        }
        break;
      }
      case "checkout.session.async_payment_failed": {
        const sess = o as Stripe.Checkout.Session;
        const intent = sess.metadata?.gk_intent || sess.metadata?.gk_plus_intent || "";
        await db`update billing.purchases set status = 'failed' where checkout_session_id = ${sess.id} and status = 'open'`;
        if (intent && /^[0-9a-f-]{36}$/.test(intent)) {
          await db`update billing.plus_checkouts set state = 'failed' where id = ${intent}::uuid and state in ('reserved','pending')`;
        }
        break;
      }
      case "customer.subscription.created":
      case "customer.subscription.updated":
      case "customer.subscription.deleted":
      case "customer.subscription.paused":
      case "customer.subscription.resumed":
        await syncSubscription((o as Stripe.Subscription).id); break;
      case "invoice.paid":
      case "invoice.payment_failed": {
        const sub = subFromInvoice(o as Stripe.Invoice); if (sub) await syncSubscription(sub); break; }
      case "charge.refunded": {
        const ch = o as Stripe.Charge; if (ch.refunded) await setPurchase(typeof ch.payment_intent === "string" ? ch.payment_intent : ch.payment_intent?.id, "refunded"); break; }
      case "charge.dispute.created": {
        const dp = o as Stripe.Dispute; await setPurchase(typeof dp.payment_intent === "string" ? dp.payment_intent : dp.payment_intent?.id, "disputed");
        console.warn("Streitfall eröffnet", dp.id); break; }
      case "radar.early_fraud_warning.created": {
        const w = o as Stripe.Radar.EarlyFraudWarning; await setPurchase(typeof w.payment_intent === "string" ? w.payment_intent : w.payment_intent?.id, "flagged");
        console.warn("Frühe Betrugswarnung", w.id); break; }
    }
    await db`update billing.webhook_events set processed_at = now() where id = ${event.id}`;
    return new Response("ok", { status: 200 });
  } catch (e) {
    console.error("webhook failed", event.type, (e as Error)?.message);
    return new Response("retry", { status: 500 });
  }
});
