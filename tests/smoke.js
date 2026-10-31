/* Automatischer Test vor jeder Veröffentlichung (GitHub Actions, Workflow „Tests“).
   Fehler im JavaScript einer Seite = Test rot = Seite geht NICHT live.
   Deutsche Reste auf englischen Seiten werden nur gemeldet (Warnung), nicht blockiert.
   Lokal: python3 -m http.server 8765 & node tests/smoke.js */
const {chromium}=require('playwright');
const BASE=process.env.BASE||'http://localhost:8765';
const PAGES=['/','/start/','/buchbegruessung/','/arbeitsbuch/','/impressum/','/datenschutz/','/rechner/','/en/calculators/'];
const fs=require('fs');
for(const d of fs.readdirSync('rechner',{withFileTypes:true}))if(d.isDirectory())PAGES.push('/rechner/'+d.name+'/');
for(const d of fs.readdirSync('en/calculators',{withFileTypes:true}))if(d.isDirectory())PAGES.push('/en/calculators/'+d.name+'/');
const GER=/[äöüßÄÖÜ]|\b(und|nicht|deine?n?|oder|wird|sind|Monat|Jahre|Schulden|Ausgaben|Einnahmen)\b/;
(async()=>{const b=await chromium.launch();let fail=[],warn=new Set();
 for(const lang of ['de','en']){const c=await b.newContext({locale:lang==='en'?'en-US':'de-DE',serviceWorkers:'block'});
  await c.route(/^https?:\/\/(?!localhost)/,r=>r.abort());/* keine Netzanfragen nach außen: Test bleibt stabil */
  const p=await c.newPage();let cur='';p.on('pageerror',e=>fail.push(lang+' '+cur+': '+e.message));
  const list=PAGES.concat(['/app/?lang='+lang]);
  for(const u of list){cur=u;await p.goto(BASE+u+(u.includes('?')?'':'?lang='+lang),{waitUntil:'load'});await p.waitForTimeout(500);
   if(/\/(rechner|en\/calculators)\/[^/]+\/$/.test(u)&&!/waehrungs|euro-in|-in-euro|currency|eur-to|-to-eur|bitcoin|btc/.test(u)){const big=await p.evaluate(()=>{const e=document.querySelector('#big')||document.querySelector('#res');return e?e.textContent.trim():null;});if(big===null||big==='')fail.push(lang+' '+u+': Rechner zeigt kein Ergebnis');}
   if(lang==='en'&&!/^\/rechner\//.test(u)){const t=await p.evaluate(()=>{const o=[];const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;while((n=w.nextNode())){const pa=n.parentNode;if(!pa||/SCRIPT|STYLE/.test(pa.nodeName)||pa.closest('[data-l="de"]'))continue;const v=n.nodeValue.trim();if(v)o.push(v);}return o;});
    t.filter(x=>GER.test(x)&&!/Der einfache Weg|BAföG|Deutsch/.test(x)).forEach(x=>warn.add(u+' » '+x.slice(0,90)));}}
  if(lang==='de'){/* App: eigene Daten, alle Bereiche, Bearbeiten-Dialog */
   cur='/app/ (eigene Daten)';await p.goto(BASE+'/app/?lang=de');await p.waitForTimeout(800);
   for(const pg of ['overview','bookings','debts','assets','plan','recurring','calc','examples','book','data']){await p.evaluate(pg=>{location.hash=pg;},pg);await p.waitForTimeout(250);}}
  await c.close();}
 await b.close();
 if(warn.size){console.log('::warning::'+warn.size+' mögliche deutsche Reste auf englischen Seiten');[...warn].slice(0,40).forEach(w=>console.log('  '+w));}
 if(fail.length){console.log('FEHLER:');fail.forEach(f=>console.log('::error::'+f));process.exit(1);}
 console.log('OK: '+(PAGES.length+1)+' Seiten je Sprache ohne JavaScript-Fehler');})();
