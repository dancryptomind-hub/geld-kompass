// Read-only server-clock catalog. No purchase, identity or visitor data is stored.
import { catalog } from '../../../whitelabel-policy.mjs';
Deno.serve(req=>{
 const origin=req.headers.get('origin');const headers={'Content-Type':'application/json','Cache-Control':'no-store','Access-Control-Allow-Origin':origin==='https://www.geld-kompass.com'?origin:'https://geld-kompass.com','Access-Control-Allow-Headers':'apikey, content-type','Access-Control-Allow-Methods':'GET, OPTIONS','Vary':'Origin'};
 if(req.method==='OPTIONS')return new Response(null,{status:204,headers});
 if(req.method!=='GET')return new Response(JSON.stringify({error:'method_not_allowed'}),{status:405,headers});
 return new Response(JSON.stringify(catalog()),{headers});
});
