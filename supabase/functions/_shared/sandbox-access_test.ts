import { sandboxAdmin, sandboxService } from './sandbox-access.ts';
function eq(a:unknown,b:unknown){if(a!==b)throw new Error(`${a} != ${b}`);}
Deno.test('Sandbox-Auslieferung ausschließlich für bestätigte Administratoren',()=>{
 const good={id:'owner',email_confirmed_at:'confirmed',is_anonymous:false,app_metadata:{gk_admin:true}};
 eq(sandboxAdmin(good),true);
 for(const u of [null,{}, {...good,app_metadata:{}},{...good,app_metadata:{gk_admin:'true'}},{...good,email_confirmed_at:''},{...good,is_anonymous:true},{...good,id:''},{...good,app_metadata:{},user_metadata:{gk_admin:true}}])eq(sandboxAdmin(u),false);
});
Deno.test('Service-Test nur mit exakt vorhandenem Serverzugang',()=>{
 eq(sandboxService('Bearer fixture-server-token','fixture-server-token'),true);
 for(const secret of [undefined,''])eq(sandboxService('Bearer '+secret,secret),false);
 eq(sandboxService('Bearer wrong','fixture-server-token'),false);
 eq(sandboxService('fixture-server-token','fixture-server-token'),false);
});

Deno.test('Anbieter-Testkonsole akzeptiert nur hinterlegte serverseitige Secret-Keys',async()=>{
 const {sandboxProviderSecret}=await import('./sandbox-access.ts');
 const stored=JSON.stringify({default:'sb_secret_fixture_server_only'});
 eq(sandboxProviderSecret('sb_secret_fixture_server_only',stored),true);
 for(const value of ['','sb_publishable_fixture','sb_secret_wrong'])eq(sandboxProviderSecret(value,stored),false);
 for(const stored of [undefined,'{}','null','[]','broken'])eq(sandboxProviderSecret('sb_secret_fixture_server_only',stored),false);
});
Deno.test('Konfigurationstest meldet nur die Art, niemals Geheimwerte',async()=>{
 const {credentialKind}=await import('./sandbox-access.ts');
 eq(credentialKind(undefined),'missing');
 eq(credentialKind('sk_test_fixture_0123456789'),'test_api');
 eq(credentialKind('rk_live_fixture_0123456789'),'live_api');
 eq(credentialKind('whsec_fixture_0123456789'),'webhook');
 for(const value of ['sk_test_...','••••••••','STRIPE_SANDBOX_SECRET_KEY','123456',' sk_test_fixture_0123456789'])eq(credentialKind(value),'invalid');
});
