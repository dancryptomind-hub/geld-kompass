// GET ?session_id=cs_… → Kaufstatus für die Danke-Seite. Freischaltung passiert NUR im Webhook; hier wird nur gelesen.
// Bezahltes Arbeitsbuch: zeitlich begrenzter Download-Link aus dem privaten Speicher „downloads“.
import { handle, json, HttpError, rateLimit, sql, admin, stripe } from "../_shared/billing.ts";

const FILES: Record<string, string> = { gk_workbook_de: "arbeitsbuch-de.pdf" };

Deno.serve(handle(async (req) => {
  if (req.method !== "GET") throw new HttpError(405, "method_not_allowed");
  await rateLimit(req, "status", 60, 600);
  const id = new URL(req.url).searchParams.get("session_id") || "";
  if (!/^cs_live_[A-Za-z0-9]{20,}$/.test(id)) throw new HttpError(400, "bad_session");
  const rows = await sql()`select product, status from billing.purchases where checkout_session_id = ${id}`;
  if (!rows[0]) {
    const s = await stripe().checkout.sessions.retrieve(id);
    if (s.mode === "subscription") {
      const sub = typeof s.subscription === "string" ? s.subscription : s.subscription?.id;
      const live = sub ? await sql()`select status from billing.subscriptions where stripe_subscription_id = ${sub}` : [];
      return json(req, { kind: "plus", status: live[0]?.status || (s.status === "complete" ? "processing" : s.status) });
    }
    throw new HttpError(404, "not_found");
  }
  const p = rows[0], out: Record<string, unknown> = { kind: p.product, status: p.status };
  if (p.status === "paid" && FILES[p.product as string]) {
    const { data, error } = await admin().storage.from("downloads").createSignedUrl(FILES[p.product as string], 3600, { download: true });
    out.download = error ? null : data?.signedUrl;
    if (error) out.note = "file_missing";
  }
  return json(req, out);
}));
