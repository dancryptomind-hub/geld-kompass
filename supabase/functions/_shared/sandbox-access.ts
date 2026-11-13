// Nur nach serverseitiger Auth-Prüfung (auth.getUser) verwenden, niemals mit Browserangaben.
export function sandboxAdmin(user: unknown): boolean {
 if(!user||typeof user!=='object')return false;
 const u=user as {id?:unknown;email_confirmed_at?:unknown;is_anonymous?:unknown;app_metadata?:{gk_admin?:unknown}};
 return !!u.id&&!!u.email_confirmed_at&&u.is_anonymous!==true&&u.app_metadata?.gk_admin===true;
}
export function sandboxService(authorization:string,secret:string|undefined):boolean {
 return !!secret&&authorization==='Bearer '+secret;
}
// Moderne Supabase-Testkonsole sendet ihren bestehenden Secret-Key im apikey-Header.
export function sandboxProviderSecret(value:string,stored:string|undefined):boolean {
 if(!value.startsWith('sb_secret_')||!stored)return false;
 try{
  const keys=JSON.parse(stored);
  return !!keys&&typeof keys==='object'&&!Array.isArray(keys)&&Object.values(keys).some(k=>typeof k==='string'&&k===value);
 }catch{return false;}
}
export function credentialKind(value:string|undefined):string {
 if(!value)return 'missing';
 if(/^(sk|rk)_test_[A-Za-z0-9_]{16,}$/.test(value))return 'test_api';
 if(/^(sk|rk)_live_[A-Za-z0-9_]{16,}$/.test(value))return 'live_api';
 if(/^whsec_[A-Za-z0-9_]{16,}$/.test(value))return 'webhook';
 return 'invalid';
}
