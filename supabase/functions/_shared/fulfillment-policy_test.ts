import { purchaseProduct } from './fulfillment-policy.ts';
function eq(a:unknown,b:unknown){if(a!==b)throw new Error(`${a} != ${b}`);}
Deno.test('Nur bestätigte eigene Einmalprodukte erhalten einen Download',()=>{
 const s={mode:'payment',payment_status:'paid',metadata:{gk_item:'workbook'}};
 eq(purchaseProduct(s),'gk_workbook_de');
 eq(purchaseProduct({...s,metadata:{gk_item:'report'}}),'gk_freedom_report');
 for(const metadata of [null,{}, {gk_item:'other'}, {gk_item:'plus_monthly'}])eq(purchaseProduct({...s,metadata}),null);
 for(const payment_status of ['unpaid','unknown',''])eq(purchaseProduct({...s,payment_status}),null);
 eq(purchaseProduct({...s,mode:'subscription'}),null);
 eq(purchaseProduct({...s,payment_status:'no_payment_required'}),'gk_workbook_de');
});
