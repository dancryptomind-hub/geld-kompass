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

Deno.test('Rabatt verwendet das tatsächlich zum Preis gehörende Produkt', async () => {
  const { ensurePromo } = await import('./billing.ts');
  let targets: string[] = [];
  const fake = {
    prices: {list: async()=>({data:[{id:'price_existing',product:'prod_dashboard',currency:'eur',unit_amount:999,tax_behavior:'inclusive',recurring:null}]})},
    promotionCodes: {list:async()=>({data:[]}),create:async()=>({id:'promo_correct'})},
    coupons: {retrieve:async()=>{throw new Error('missing')},create:async(p:{applies_to:{products:string[]}})=>{targets=p.applies_to.products;return {id:'coupon_correct'}}},
    products: {retrieve:async()=>{throw new Error('Unnötiger Zugriff auf abweichendes Produkt')},create:async()=>{throw new Error('Kein zweites Produkt anlegen')}}
  };
  eq(await ensurePromo('KOMPASS20',fake as never),'promo_correct','Rabatt-ID');
  eq(targets,['prod_dashboard'],'Tatsächliches Produkt statt interner Kennung');
});

Deno.test('Vorhandener Arbeitsbuch-Preis muss 9,99 EUR inklusive Steuer sein', async () => {
 const {ensurePrice}=await import('./billing.ts');
 const base={id:'price_existing',product:'prod_dashboard',currency:'eur',unit_amount:999,tax_behavior:'inclusive',recurring:null};
 const fake=(p:unknown)=>({prices:{list:async()=>({data:[p]})}} as never);
 eq(await ensurePrice('workbook',fake(base)),'price_existing','korrekter Preis');
 for(const p of [{...base,currency:'usd'},{...base,unit_amount:1999},{...base,tax_behavior:'exclusive'},{...base,recurring:{interval:'month'}}]){
  let rejected=false;
  try{await ensurePrice('workbook',fake(p));}catch(e){rejected=(e as HttpError).code==='price_configuration_mismatch';}
  eq(rejected,true,'falschen gespeicherten Preis sperren');
 }
});

Deno.test('Managed Payments verwendet ausschließlich die Standardtexte von Link', async () => {
 const { checkoutText } = await import('./billing.ts');
 eq(checkoutText(true, 'Eigener Text'), {}, 'Keine nicht unterstützten Zusatztexte');
 eq(checkoutText(false, 'Kündbar'), {custom_text:{submit:{message:'Kündbar'}}}, 'Standard-Checkout behält seinen Text');
});
