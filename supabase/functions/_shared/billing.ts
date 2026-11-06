// Geld-Kompass Pro · gemeinsame Stripe-Helfer für alle Billing-Funktionen.
// Schlüssel kommen ausschließlich aus Supabase-Secrets (STRIPE_SECRET_KEY als eingeschränkter rk_…-Schlüssel, STRIPE_WEBHOOK_SECRET).
import Stripe from "npm:stripe@23.1.0";
import postgres from "npm:postgres@3.4.5";
import { createClient, type User } from "npm:@supabase/supabase-js@2.49.4";

export const API_VERSION = "2026-10-28.endive";
export const SITE = "https://geld-kompass.com";
const ORIGINS = [SITE, "https://www.geld-kompass.com", "http://localhost:8765"];

export class HttpError extends Error {
  constructor(public status: number, public code: string) { super(code); }
}

let _stripe: Stripe | null = null;
export function stripe(): Stripe {
  const key = Deno.env.get("STRIPE_SECRET_KEY");
  if (!key) throw new HttpError(503, "stripe_not_configured");
  if (!_stripe) _stripe = new Stripe(key, { apiVersion: API_VERSION as Stripe.LatestApiVersion, httpClient: Stripe.createFetchHttpClient(), appInfo: { name: "geld-kompass", url: SITE } });
  return _stripe;
}
export const cryptoProvider = Stripe.createSubtleCryptoProvider();

let _sql: ReturnType<typeof postgres> | null = null;
export function sql() {
  if (!_sql) _sql = postgres(Deno.env.get("SUPABASE_DB_URL")!, { prepare: false, max: 3 });
  return _sql;
}
export function admin() {
  return createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false, autoRefreshToken: false } });
}

export async function userFrom(req: Request): Promise<User | null> {
  const h = req.headers.get("authorization") || "";
  const token = h.toLowerCase().startsWith("bearer ") ? h.slice(7).trim() : "";
  if (!token || token.split(".").length !== 3) return null;
  const { data, error } = await admin().auth.getUser(token);
  if (error || !data?.user || data.user.is_anonymous) return null;
  return data.user;
}

export function cors(req: Request): Record<string, string> {
  const o = req.headers.get("origin") || "";
  return {
    "Access-Control-Allow-Origin": ORIGINS.includes(o) ? o : SITE,
    "Access-Control-Allow-Headers": "authorization, content-type, apikey, x-client-info",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Vary": "Origin",
  };
}
export function json(req: Request, body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { ...cors(req), "Content-Type": "application/json" } });
}
export function handle(fn: (req: Request) => Promise<Response>) {
  return async (req: Request) => {
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors(req) });
    try { return await fn(req); }
    catch (e) {
      if (e instanceof HttpError) return json(req, { error: e.code }, e.status);
      console.error("billing error", (e as Error)?.message);
      return json(req, { error: "server_error" }, 500);
    }
  };
}

/* Katalog: eine Product-ID je Angebot, Preisvarianten (Monat/Jahr) am selben Produkt. Preise brutto (inklusive Steuer). */
export const PRODUCTS: Record<string, { name: string; description: string }> = {
  gk_plus: { name: "Geld-Kompass Plus", description: "Alle Plus-Funktionen: Entnahmeplan, Dividendenkalender, Steuer- und Nomaden-Modus, Kursalarme, eigene Schnellleiste." },
  gk_workbook_de: { name: "Arbeitsbuch „Der einfache Weg zur Finanziellen Freiheit“ (PDF)", description: "69 Seiten Übungen zu allen 16 Kapiteln, digital zum Ausdrucken oder Beschriften." },
  gk_freedom_report: { name: "Freiheits-Report (PDF)", description: "Dein persönlicher Report aus deinen Geld-Kompass-Zahlen." },
};
export const CATALOG: Record<string, { lookup: string; product: string; amount: number; interval?: "month" | "year"; mode: "subscription" | "payment"; needsUser: boolean; enabledEnv?: string }> = {
  plus_monthly: { lookup: "gk_plus_monthly_eur", product: "gk_plus", amount: 499, interval: "month", mode: "subscription", needsUser: true },
  plus_yearly: { lookup: "gk_plus_yearly_eur", product: "gk_plus", amount: 3900, interval: "year", mode: "subscription", needsUser: true },
  workbook: { lookup: "gk_workbook_de_eur", product: "gk_workbook_de", amount: 999, mode: "payment", needsUser: false },
  report: { lookup: "gk_freedom_report_eur", product: "gk_freedom_report", amount: 1499, mode: "payment", needsUser: false, enabledEnv: "REPORT_ENABLED" },
};

export async function ensurePrice(item: keyof typeof CATALOG): Promise<string> {
  const c = CATALOG[item], s = stripe();
  const found = await s.prices.list({ lookup_keys: [c.lookup], active: true, limit: 1 });
  if (found.data[0]) return found.data[0].id;
  try { await s.products.retrieve(c.product); }
  catch { await s.products.create({ id: c.product, name: PRODUCTS[c.product].name, description: PRODUCTS[c.product].description }, { idempotencyKey: "prod_" + c.product }); }
  const p = await s.prices.create({
    product: c.product, currency: "eur", unit_amount: c.amount, lookup_key: c.lookup, tax_behavior: "inclusive",
    ...(c.interval ? { recurring: { interval: c.interval } } : {}),
  }, { idempotencyKey: "price_" + c.lookup });
  return p.id;
}

export async function customerFor(user: User): Promise<string> {
  const db = sql();
  const rows = await db`select stripe_customer_id from billing.customers where user_id = ${user.id}`;
  if (rows[0]) return rows[0].stripe_customer_id as string;
  const c = await stripe().customers.create({ email: user.email || undefined, metadata: { gk_user: user.id } }, { idempotencyKey: "cust_" + user.id });
  await db`insert into billing.customers (user_id, stripe_customer_id) values (${user.id}, ${c.id}) on conflict (user_id) do nothing`;
  const again = await db`select stripe_customer_id from billing.customers where user_id = ${user.id}`;
  return again[0].stripe_customer_id as string;
}

/* Abo-Zustand aus Stripe lesen, speichern und als app_metadata.gk_plus am Konto setzen (nur Server darf app_metadata schreiben). */
export async function syncSubscription(subId: string) {
  const s = stripe(), db = sql();
  const sub = await s.subscriptions.retrieve(subId);
  const customerId = typeof sub.customer === "string" ? sub.customer : sub.customer.id;
  const owner = await db`select user_id from billing.customers where stripe_customer_id = ${customerId}`;
  const userId: string | null = (owner[0]?.user_id as string) || (sub.metadata?.gk_user as string) || null;
  const item = sub.items.data[0];
  const end = item?.current_period_end ? new Date(item.current_period_end * 1000) : null;
  const lookup = item?.price?.lookup_key || null, interval = item?.price?.recurring?.interval || null;
  await db`insert into billing.subscriptions (stripe_subscription_id, user_id, stripe_customer_id, status, price_lookup_key, interval, current_period_end, cancel_at_period_end, updated_at)
    values (${sub.id}, ${userId}, ${customerId}, ${sub.status}, ${lookup}, ${interval}, ${end}, ${!!sub.cancel_at_period_end}, now())
    on conflict (stripe_subscription_id) do update set user_id = excluded.user_id, status = excluded.status, price_lookup_key = excluded.price_lookup_key,
      interval = excluded.interval, current_period_end = excluded.current_period_end, cancel_at_period_end = excluded.cancel_at_period_end, updated_at = now()`;
  if (userId) await refreshEntitlement(userId);
}
export async function refreshEntitlement(userId: string) {
  const rows = await sql()`select status, interval, current_period_end, cancel_at_period_end from billing.subscriptions where user_id = ${userId} order by current_period_end desc nulls last`;
  const live = rows.find((r) => ["active", "trialing", "past_due"].includes(r.status as string));
  const until = live?.current_period_end ? new Date(live.current_period_end as Date).getTime() + 3 * 864e5 : 0; // 3 Tage Kulanz für Zahlungswiederholungen
  const gk_plus = live ? { active: true, status: live.status, interval: live.interval, until, cancel_at_period_end: !!live.cancel_at_period_end } : { active: false, status: rows[0]?.status || "none", until: 0 };
  const { data } = await admin().auth.admin.getUserById(userId);
  const meta = { ...(data?.user?.app_metadata || {}), gk_plus };
  await admin().auth.admin.updateUserById(userId, { app_metadata: meta });
}
