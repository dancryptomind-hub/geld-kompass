// Confirmed fixed monthly market prices. Amounts are in currency minor units.
export const MARKETS = Object.freeze({EUR:[7900,19900,39900],GBP:[7900,19900,39900],CHF:[7900,19900,39900],USD:[8900,21900,44900],CAD:[11900,29900,59900]});
export const WINDOWS = Object.freeze([
 {id:'black_friday_2026',start:'2026-11-26T23:00:00Z',end:'2026-12-07T23:00:00Z',label:'Black Friday',endDate:'07.12.2026'},
 {id:'christmas_2026',start:'2026-12-19T23:00:00Z',end:'2027-01-01T23:00:00Z',label:'Christmas Special',endDate:'01.01.2027'}
]);
export function offerAt(now) {
 const n=Number(now); if(!Number.isFinite(n)) throw new Error('invalid_time');
 return WINDOWS.find(w=>n>=Date.parse(w.start)&&n<Date.parse(w.end))||null;
}
export function currencyForCountry(country){
 return ({DE:'EUR',AT:'EUR',LU:'EUR',CH:'CHF',GB:'GBP',CA:'CAD',US:'USD',AE:'USD'})[String(country||'').toUpperCase()]||'EUR';
}
export function catalog(now=Date.now()) {
 const offer=offerAt(now);
 return {version:1,generatedAt:new Date(now).toISOString(),validUntil:new Date(Math.min(now+60000,offer?Date.parse(offer.end):Infinity)).toISOString(),prices:MARKETS,taxBehavior:'inclusive',checkoutEnabled:false,
 offer:offer?{...offer,currency:'EUR',plan:'professional',amount:3900,regularAmount:7900,monthlyPayments:12,timezone:'Europe/Berlin'}:null};
}
export function quote(plan,currency,now=Date.now()) {
 if(!['professional','business','agency'].includes(plan)||!Object.hasOwn(MARKETS,currency))throw new Error('invalid_selection');
 const regular=MARKETS[currency][['professional','business','agency'].indexOf(plan)];
 const offer=plan==='professional'&&currency==='EUR'?offerAt(now):null;
 return {plan,currency,regularAmount:regular,amount:offer?3900:regular,discountPayments:offer?12:0,from:plan==='agency',taxBehavior:'inclusive',offer};
}
// Explicit allowlist: foreign subscriptions must never be imported into private Plus.
export function isPrivatePlusSubscription(sub){
 const items=sub?.items?.data;
 return Array.isArray(items)&&items.length===1&&['gk_plus_monthly_eur','gk_plus_yearly_eur'].includes(items[0]?.price?.lookup_key)&&
 (typeof items[0].price.product==='string'?items[0].price.product:items[0].price.product?.id)==='gk_plus';
}
