// Stripe-Webhook: einzige Quelle der Wahrheit für Freischaltung, Verlängerung, Kündigung, Erstattung, Streitfall und Betrugswarnung.
// Signatur wird geprüft, jedes Ereignis nur einmal verarbeitet (billing.webhook_events).
import type Stripe from "npm:stripe@23.1.0";
import { stripe, cryptoProvider, sql, syncSubscription } from "../_shared/billing.ts";

async function setPurchase(pi: string | null | undefined, status: string) {
  if (!pi) return;
  await sql()`update billing.purchases set status = ${status} where payment_intent_id = ${pi}`;
}
async function fulfill(s: Stripe.Checkout.Session) {
  if (s.mode === "subscription") { const sub = typeof s.subscription === "string" ? s.subscription : s.subscription?.id; if (sub) await syncSubscription(sub); return; }
  if (s.payment_status === "unpaid") return; // verzögerte Zahlungsarten: erst bei async_payment_succeeded
  const pi = typeof s.payment_intent === "string" ? s.payment_intent : s.payment_intent?.id || null;
  const email = s.customer_details?.email || null;
  await sql()`insert into billing.purchases (checkout_session_id, email, product, amount_total, currency, status, payment_intent_id, fulfilled_at)
    values (${s.id}, ${email}, ${String(s.metadata?.gk_item === "report" ? "gk_freedom_report" : "gk_workbook_de")}, ${s.amount_total}, ${s.currency}, 'paid', ${pi}, now())
    on conflict (checkout_session_id) do update set status = 'paid', amount_total = excluded.amount_total, currency = excluded.currency,
      payment_intent_id = excluded.payment_intent_id, email = coalesce(billing.purchases.email, excluded.email), fulfilled_at = coalesce(billing.purchases.fulfilled_at, now())`;
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
      case "checkout.session.async_payment_failed":
        await db`update billing.purchases set status = 'failed' where checkout_session_id = ${(o as Stripe.Checkout.Session).id}`; break;
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
