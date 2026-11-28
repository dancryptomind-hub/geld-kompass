import {MARKETS,currencyForCountry} from '/whitelabel-policy.mjs';
const EN=document.documentElement.lang==='en', select=document.getElementById('wlCurrency'), box=document.getElementById('wlOffer'), note=document.getElementById('wlCountryNote');
const endpoint='https://cwznthfefbeglamnwyry.supabase.co/functions/v1/whitelabel-offer';
let currentOffer=null,manual=false,expiry;
function money(amount,cur){return new Intl.NumberFormat(EN?'en-GB':'de-DE',{style:'currency',currency:cur,maximumFractionDigits:0}).format(amount/100);}
function render(){
 const cur=select.value;
 document.querySelectorAll('[data-wl-price]').forEach(el=>{const plan=el.dataset.wlPrice,i=['professional','business','agency'].indexOf(plan);el.textContent=(plan==='agency'?(EN?'from ':'ab '):'')+money(i<0?0:(plan==='professional'&&cur==='EUR'&&currentOffer?3900:MARKETS[cur][i]),cur);});
 document.querySelectorAll('[data-wl-inquiry]').forEach(a=>{a.href='mailto:kontakt@geld-kompass.com?subject='+encodeURIComponent('White-Label '+a.dataset.wlInquiry+' · '+cur);});
 const o=currentOffer;box.hidden=!(o&&cur==='EUR');
 if(!box.hidden)box.textContent=o.label+': '+(EN?'€39 per month for the first 12 monthly payments, then currently €79 per month. New agreements through ':'39 € pro Monat für die ersten 12 monatlichen Zahlungen, danach derzeit 79 € pro Monat. Neue Abschlüsse bis einschließlich ')+o.endDate+(EN?', 23:59 Europe/Berlin. Includes applicable indirect taxes.':', 23:59 Uhr Europe/Berlin. Einschließlich anfallender indirekter Steuern.');
}
async function refresh(){
 clearTimeout(expiry);currentOffer=null;render();
 try{
  const started=performance.now();
  const r=await fetch(endpoint,{cache:'no-store',headers:{apikey:'sb_publishable_OAzhy63__bAdBHq7H7NqUA_RqxB_qhc'}});
  if(!r.ok)throw new Error('unavailable');const data=await r.json();
  const ttl=Date.parse(data.validUntil)-Date.parse(data.generatedAt)-(performance.now()-started);
  if(data.version!==1||ttl<=0||ttl>60000||JSON.stringify(data.prices)!==JSON.stringify(MARKETS))throw new Error('invalid_catalog');
  const o=data.offer;
  if(o&&o.currency==='EUR'&&o.plan==='professional'&&o.amount===3900&&o.regularAmount===7900&&o.monthlyPayments===12)currentOffer=o;
  render();expiry=setTimeout(()=>{currentOffer=null;render();refresh();},Math.min(ttl,45000));
 }catch{expiry=setTimeout(refresh,60000);}
}
select.addEventListener('change',()=>{manual=true;render();});
render();refresh();
// Same-origin country preselection. The response is never saved or logged.
fetch('/cdn-cgi/trace',{cache:'no-store'}).then(r=>r.ok?r.text():Promise.reject()).then(text=>{
 const country=(text.match(/^loc=([A-Z]{2})$/m)||[])[1];if(!country)return;
 if(!manual)select.value=currencyForCountry(country);
 note.textContent=EN?'Currency suggested by country; you can change it at any time. Other countries default to EUR.':'Währung nach Land vorausgewählt; jederzeit änderbar. Für andere Länder gilt EUR als Standard.';render();
}).catch(()=>{note.textContent=EN?'Default: EUR. Choose your preferred billing currency.':'Standard: EUR. Wähle deine gewünschte Abrechnungswährung.';});
document.addEventListener('visibilitychange',()=>{if(!document.hidden)refresh();});
