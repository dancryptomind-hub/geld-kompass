import { releaseError } from './release-policy.ts';
function eq(a:unknown,b:unknown){if(a!==b)throw new Error(`${a} != ${b}`);}
Deno.test('Keine Verkäufe ohne ausdrückliche Freigabe',()=>{
 for(const item of ['workbook','plus_monthly','plus_yearly','report'])eq(releaseError(item,{}),'not_available');
});
Deno.test('Arbeitsbuch-Freigabe öffnet keine Abos oder Reports',()=>{
 const e={WORKBOOK_ENABLED:'1',MANAGED_PAYMENTS:'1',TOS_CONSENT:'1'};
 eq(releaseError('workbook',e),null);
 for(const item of ['plus_monthly','plus_yearly','report'])eq(releaseError(item,e),'not_available');
});
Deno.test('Arbeitsbuch benötigt eingerichtete Steuer- und Zustimmungsabläufe',()=>{
 eq(releaseError('workbook',{WORKBOOK_ENABLED:'1'}),'workbook_setup_incomplete');
 eq(releaseError('workbook',{WORKBOOK_ENABLED:'1',MANAGED_PAYMENTS:'1'}),'workbook_setup_incomplete');
});
