import { releaseError } from './release-policy.ts';
function eq(a:unknown,b:unknown){if(a!==b)throw new Error(`${a} != ${b}`);}
Deno.test('Keine Verkäufe ohne ausdrückliche Freigabe',()=>{
 for(const item of ['workbook','plus_monthly','plus_yearly','report'])eq(releaseError(item,{}),'not_available');
});
Deno.test('Arbeitsbuch-Setup schaltet Plus und Report frei, solange kein 0-Schalter sperrt',()=>{
 const e={WORKBOOK_ENABLED:'1',MANAGED_PAYMENTS:'1',TOS_CONSENT:'1'};
 for(const item of ['workbook','plus_monthly','plus_yearly','report'])eq(releaseError(item,e),null);
 eq(releaseError('plus_yearly',{...e,PLUS_ENABLED:'0'}),'not_available');
 eq(releaseError('report',{...e,REPORT_ENABLED:'0'}),'not_available');
});
Deno.test('Arbeitsbuch benötigt eingerichtete Steuer- und Zustimmungsabläufe',()=>{
 eq(releaseError('workbook',{WORKBOOK_ENABLED:'1'}),'workbook_setup_incomplete');
 eq(releaseError('workbook',{WORKBOOK_ENABLED:'1',MANAGED_PAYMENTS:'1'}),'workbook_setup_incomplete');
 eq(releaseError('plus_yearly',{WORKBOOK_ENABLED:'1'}),'not_available');
});
