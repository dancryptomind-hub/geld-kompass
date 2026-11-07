// Sicherheitstests der Billing-Helfer (CI: deno test). Kein Netz, keine Schlüssel nötig.
import { catalogItem, readJson, HttpError, cors } from "./billing.ts";

function eq(a: unknown, b: unknown, msg: string) { if (JSON.stringify(a) !== JSON.stringify(b)) throw new Error(msg + ": " + JSON.stringify(a)); }

Deno.test("Katalog: nur eigene Einträge, keine Prototyp-Namen", () => {
  for (const bad of ["constructor", "__proto__", "toString", "hasOwnProperty", "", null, 5, {}]) eq(catalogItem(bad), null, "akzeptiert " + String(bad));
  eq(catalogItem("plus_monthly")?.c.amount, 499, "Preis Plus Monat");
  eq(catalogItem("workbook")?.c.amount, 999, "Preis Arbeitsbuch");
});

Deno.test("JSON-Körper: Größenlimit und nur Objekte", async () => {
  const big = new Request("https://x/", { method: "POST", body: "{\"a\":\"" + "x".repeat(9000) + "\"}" });
  let code = "";
  try { await readJson(big); } catch (e) { code = (e as HttpError).code; }
  eq(code, "too_large", "großer Körper");
  eq(await readJson(new Request("https://x/", { method: "POST", body: "[1,2]" })), {}, "Array");
  eq(await readJson(new Request("https://x/", { method: "POST", body: "kaputt" })), {}, "kaputt");
  eq(await readJson(new Request("https://x/", { method: "POST", body: "{\"item\":\"workbook\"}" })), { item: "workbook" }, "normal");
});

Deno.test("CORS: fremde Herkunft bekommt nie ihre eigene Origin zurück", () => {
  const h = (o: string) => cors(new Request("https://x/", { headers: { origin: o } }))["Access-Control-Allow-Origin"];
  eq(h("https://evil.example"), "https://geld-kompass.com", "fremd");
  eq(h("http://localhost:8765"), "https://geld-kompass.com", "localhost");
  eq(h("https://www.geld-kompass.com"), "https://www.geld-kompass.com", "www");
});
