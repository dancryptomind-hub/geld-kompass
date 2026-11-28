import {strict as a} from 'node:assert';
import {offerAt,currencyForCountry,quote,catalog,isPrivatePlusSubscription} from '../whitelabel-policy.mjs';
const at=s=>Date.parse(s);
for(const [time,expected] of [
 ['2026-11-26T22:59:59.999Z',null],['2026-11-26T23:00:00.000Z','black_friday_2026'],
 ['2026-12-07T22:59:59.999Z','black_friday_2026'],['2026-12-07T23:00:00.000Z',null],
 ['2026-12-19T22:59:59.999Z',null],['2026-12-19T23:00:00.000Z','christmas_2026'],
 ['2027-01-01T22:59:59.999Z','christmas_2026'],['2027-01-01T23:00:00.000Z',null]])a.equal(offerAt(at(time))?.id||null,expected,time);
for(const [cc,c] of Object.entries({DE:'EUR',AT:'EUR',LU:'EUR',CH:'CHF',GB:'GBP',CA:'CAD',US:'USD',AE:'USD',TH:'EUR',FR:'EUR'}))a.equal(currencyForCountry(cc),c);
const expected={EUR:[7900,19900,39900],GBP:[7900,19900,39900],CHF:[7900,19900,39900],USD:[8900,21900,44900],CAD:[11900,29900,59900]};
for(const [c,prices] of Object.entries(expected))for(const [i,p] of ['professional','business','agency'].entries()){
 a.equal(quote(p,c,at('2026-12-10T00:00:00Z')).amount,prices[i]);
 const q=quote(p,c,at('2026-11-28T12:00:00Z'));a.equal(q.amount,c==='EUR'&&i===0?3900:prices[i]);a.equal(q.discountPayments,c==='EUR'&&i===0?12:0);a.equal(q.from,i===2);
}
a.throws(()=>quote('professional','AUD'));a.throws(()=>quote('__proto__','EUR'));a.throws(()=>offerAt(NaN));
const wrap=(product,lookup)=>({items:{data:[{price:{product,lookup_key:lookup}}]}});
a.equal(isPrivatePlusSubscription(wrap('gk_plus','gk_plus_monthly_eur')),true);
a.equal(isPrivatePlusSubscription(wrap('gk_plus','gk_plus_yearly_eur')),true);
a.equal(isPrivatePlusSubscription(wrap('gk_whitelabel_professional','gk_plus_monthly_eur')),false);
a.equal(isPrivatePlusSubscription(wrap('gk_whitelabel_business','gk_whitelabel_business_monthly_eur')),false);
a.equal(isPrivatePlusSubscription({metadata:{gk_user:'spoofed'},items:{data:[]}}),false);
const near=catalog(at('2026-12-07T22:59:50Z'));a.equal(near.validUntil,'2026-12-07T23:00:00.000Z');a.equal(near.checkoutEnabled,false);
console.log('Policy: 8 time boundaries, 10 countries, 30 price/promotion cases, 5 product isolation cases passed. No Stripe billing simulation.');
