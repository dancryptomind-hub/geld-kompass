// Geld-Kompass Plus · liefert die Smart-TV-Edition (.zip) NUR an:
//  - angemeldete, bestätigte Konten mit app_metadata.gk_admin === true ODER aktivem app_metadata.gk_plus (vom Stripe-Webhook gesetzt)
// app_metadata kann nur der Server schreiben. Niemals öffentlich oder im Cache ablegen.
import { createClient } from "npm:@supabase/supabase-js@2.49.4";
import postgres from "npm:postgres@3.4.5";

const ORIGINS = ["https://geld-kompass.com", "https://www.geld-kompass.com"];

function cors(req: Request): Record<string, string> {
  const o = req.headers.get("origin") || "";
  return {
    "Access-Control-Allow-Origin": ORIGINS.includes(o) ? o : ORIGINS[0],
    "Access-Control-Allow-Headers": "authorization, apikey, content-type, x-client-info",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Vary": "Origin",
  };
}

function deny(req: Request, status: number, code: string) {
  return new Response(JSON.stringify({ error: code }), {
    status,
    headers: { ...cors(req), "Content-Type": "application/json", "Cache-Control": "no-store" },
  });
}

let _sql: ReturnType<typeof postgres> | null = null;
const sql = () => (_sql ||= postgres(Deno.env.get("SUPABASE_DB_URL")!, { prepare: false, max: 2 }));
const admin = () =>
  createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, {
    auth: { persistSession: false, autoRefreshToken: false },
  });

async function checkAccess(req: Request): Promise<{ status: number; code?: string; userId?: string }> {
  const h = req.headers.get("authorization") || "";
  const token = h.toLowerCase().startsWith("bearer ") ? h.slice(7).trim() : "";
  if (!token || token.split(".").length !== 3) return { status: 401, code: "login_required" };
  const { data, error } = await admin().auth.getUser(token);
  const u = data?.user;
  if (error || !u || u.is_anonymous || !u.email_confirmed_at) return { status: 401, code: "login_required" };
  const m = (u.app_metadata || {}) as Record<string, unknown>;
  if (m.gk_admin === true) return { status: 200, userId: u.id };
  const p = m.gk_plus as { active?: boolean; until?: number } | undefined;
  if (p && p.active === true && Number(p.until) > Date.now()) return { status: 200, userId: u.id };
  return { status: 403, code: "plus_required" };
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors(req) });
  if (req.method !== "GET") return deny(req, 405, "method_not_allowed");
  try {
    const auth = await checkAccess(req);
    if (auth.status !== 200) return deny(req, auth.status, auth.code || "forbidden");

    const infoOnly = new URL(req.url).searchParams.get("info") === "1";
    const rows = await sql()`
      select version, filename, sha256, size_bytes, zip_b64
      from gk_private.tv_release
      order by updated_at desc
      limit 1
    `;
    if (!rows.length) return deny(req, 404, "release_not_found");
    const r = rows[0];
    if (infoOnly) {
      return new Response(
        JSON.stringify({
          ok: true,
          plus: true,
          version: r.version,
          filename: r.filename,
          sha256: r.sha256,
          sizeBytes: Number(r.size_bytes),
        }),
        { status: 200, headers: { ...cors(req), "Content-Type": "application/json", "Cache-Control": "private, no-store" } }
      );
    }

    const bytes = Uint8Array.from(atob(r.zip_b64 as string), (c) => c.charCodeAt(0));
    return new Response(bytes, {
      status: 200,
      headers: {
        ...cors(req),
        "Content-Type": "application/zip",
        "Content-Disposition": `attachment; filename="${String(r.filename)}"`,
        "Content-Length": String(bytes.length),
        "Cache-Control": "private, no-store",
        "X-Content-Type-Options": "nosniff",
      },
    });
  } catch (e) {
    console.error("tv-download", (e as Error)?.message);
    return deny(req, 500, "server_error");
  }
});
