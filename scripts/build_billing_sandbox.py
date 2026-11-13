"""Build an admin-only integration-test endpoint; never substitute live credentials.
Generated output stays under /tmp; canonical business logic is imported from source.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'supabase/functions'
def once(text,old,new):
    assert text.count(old)==1, f'Expected exactly one source marker: {old[:70]}'
    return text.replace(old,new,1)
shared=(SRC/'_shared/billing.ts').read_text()
shared=once(shared,'Deno.env.get("STRIPE_SECRET_KEY")','Deno.env.get("STRIPE_SANDBOX_SECRET_KEY")')
shared=once(shared,'if (!key) throw new HttpError(503, "stripe_not_configured");','if (!key || !/^(rk|sk)_test_/.test(key)) throw new HttpError(503, "sandbox_key_required");')
shared=once(shared,'export const managedPayments = () => Deno.env.get("MANAGED_PAYMENTS") === "1";','export const managedPayments = () => true;')
parts=[shared,(SRC/'_shared/fulfillment-policy.ts').read_text(),(SRC/'_shared/sandbox-access.ts').read_text()]
for endpoint,label in [('billing-checkout','checkoutHandler'),('billing-status','statusHandler'),('billing-webhook','webhookHandler')]:
    text=(SRC/endpoint/'index.ts').read_text()
    text='\n'.join(line for line in text.splitlines() if not line.startswith('import '))
    text=once(text,'Deno.serve(',f'const {label} = (')
    if endpoint=='billing-checkout':
        # Sandbox is independently admin-gated below. Live release flags remain untouched.
        lines=text.splitlines()
        assert sum('const release = releaseError(' in x for x in lines)==1
        lines=[x for x in lines if 'const release = releaseError(' not in x and 'if (release) throw' not in x]
        text='\n'.join(lines)
        text=once(text,'success_url: `${SITE}/plus/danke/?session_id={CHECKOUT_SESSION_ID}&lang=${lang}`,','success_url: `${SITE}/konto/?sandbox_session={CHECKOUT_SESSION_ID}&lang=${lang}`,')
        text=once(text,'...(!mp && Deno.env.get("TOS_CONSENT") === "1" ? { consent_collection: { terms_of_service: "required" } } : {}),','// Sandbox examines standard Link payment terms; no unverified waiver text.')
        text=text.replace('Digital content: access starts right after payment. By paying you agree that your right of withdrawal ends once the download starts.','PDF access starts after your payment has been confirmed.')
        text=text.replace('Digitaler Inhalt: Der Zugang startet direkt nach der Zahlung. Mit dem Kauf stimmst du zu, dass dein Widerrufsrecht mit Beginn des Downloads erlischt.','Die PDF steht nach bestätigter Zahlung bereit.')
    if endpoint=='billing-status':
        text=once(text,'/^cs_live_[A-Za-z0-9]{20,}$/','/^cs_test_[A-Za-z0-9]{20,}$/')
    if endpoint=='billing-webhook':
        text=once(text,'async (req) => {','async (req: Request) => {')
        text=once(text,'Deno.env.get("STRIPE_WEBHOOK_SECRET")','Deno.env.get("STRIPE_SANDBOX_WEBHOOK_SECRET")')
        text=once(text,'const db = sql();','if (event.livemode) return new Response("wrong_environment", { status: 400 });\n  const db = sql();')
    parts.append(text)
parts.append('''
// Test checkout/status require a freshly verified administrator or the provider's server-side test console.
// The public webhook accepts only signed sandbox events. Test cards must never unlock a public PDF URL.
Deno.serve(handle(async (req: Request) => {
 const url=new URL(req.url),action=url.searchParams.get("action")||(req.headers.has("stripe-signature")?"webhook":null);
 if(action==="webhook")return await webhookHandler(req);
 if(!sandboxService(req.headers.get("authorization")||"",Deno.env.get("SUPABASE_SERVICE_ROLE_KEY"))&&!sandboxProviderSecret(req.headers.get("apikey")||"",Deno.env.get("SUPABASE_SECRET_KEYS"))){
   const user=await userFrom(req);
   if(!sandboxAdmin(user))throw new HttpError(403,"admin_required");
 }
 if(action==="configuration")return json(req,{
   live_api:credentialKind(Deno.env.get("STRIPE_SECRET_KEY")),
   live_webhook:credentialKind(Deno.env.get("STRIPE_WEBHOOK_SECRET")),
   sandbox_api:credentialKind(Deno.env.get("STRIPE_SANDBOX_SECRET_KEY")),
   sandbox_webhook:credentialKind(Deno.env.get("STRIPE_SANDBOX_WEBHOOK_SECRET"))
 });
 if(action==="live-readiness"){
   const key=Deno.env.get("STRIPE_SECRET_KEY");
   if(credentialKind(key)!=="live_api")throw new HttpError(503,"live_key_required");
   // Read-only request: validates the rotated key and price without creating a payment.
   const live=new Stripe(key!,{apiVersion:API_VERSION as Stripe.LatestApiVersion,httpClient:Stripe.createFetchHttpClient()});
   try{
     const prices=await live.prices.list({lookup_keys:["gk_workbook_de_eur"],active:true,limit:1});
     const p=prices.data[0];
     return json(req,{live_api:"accepted",price:p?{live:p.livemode,amount:p.unit_amount,currency:p.currency,tax_behavior:p.tax_behavior,recurring:!!p.recurring}:null});
   }catch(e){
     const err=e as {type?:string;code?:string;statusCode?:number};
     return json(req,{live_api:"rejected",type:err.type||"unknown",code:err.code||"unknown",status:err.statusCode||0},502);
   }
 }
 if(action==="checkout"){
   const body=await readJson(req);
   if(body.item!=="workbook")throw new HttpError(400,"sandbox_workbook_only");
   const copy=new Request(req.url,{method:req.method,headers:req.headers,body:JSON.stringify(body)});
   return await checkoutHandler(copy);
 }
 if(action==="status"){
   if(!/^cs_test_[A-Za-z0-9]{20,}$/.test(url.searchParams.get("session_id")||""))throw new HttpError(400,"sandbox_session_required");
   return await statusHandler(req);
 }
 throw new HttpError(400,"unknown_action");
}));
''')
out=Path('/tmp/gk-functions-ready/billing-sandbox.ts');out.parent.mkdir(exist_ok=True);out.write_text('\n'.join(parts))
print(f'Admin-only sandbox bundle: {out}')
