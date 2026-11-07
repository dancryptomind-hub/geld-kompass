/* Sicherheit: XSS-Prüfung. Schadcode in allen Eingabewegen darf nie als HTML/Skript im Seitenbaum landen:
   gespeicherte Daten (localStorage/Backup), Teilen-Links, Bank-/Depot-CSV, Antworten fremder Kursdienste.
   Die CSP würde Skripte zusätzlich blocken – dieser Test prüft die erste Verteidigungslinie (esc) ohne sie zu verlassen:
   gezählt werden eingeschleuste Elemente mit data-xss, egal ob ihr Skript lief.
   Lokal: python3 -m http.server 8765 & node tests/security-xss.js */
const {chromium}=require('playwright');const BASE=process.env.BASE||'http://localhost:8765';
const P='"\'><img src=x data-xss onerror=window.__x=1><svg data-xss onload=window.__x=1>';
const fixture={v:4,chv:2,mode:'own',onboarded:1,own:{cur:'EUR',
 entries:[{id:'e1',title:'Lohn '+P,amount:3000,type:'income',cat:'Gehalt',freq:'monthly',date:'2020-01-01',note:P},{id:'e2',title:'Miete '+P,amount:900,type:'expense',cat:'Miete',freq:'monthly',date:'2020-01-01'},{id:'e3',title:P,amount:12,type:'expense',cat:P,freq:'monthly',date:'2024-03-01'}],
 items:[{id:'i1',name:'Konto '+P,side:'Aktiva',value:10000,cls:'Girokonto'},{id:'i2',name:P,side:'Passiva',value:500,cls:P}],
 debts:[{id:'d1',name:'Kredit '+P,balance:5000,rate:5,min:150}],
 hold:[{id:'h1',s:'AAPL',qty:2,name:'Apple '+P,tx:[]},{id:'h2',s:P,qty:1,name:P,online:false,price:10,tx:[]}],cache:{}},
 calc:{wi:{title:P,amt:7.5,per:'week',years:13}}};
const X=P.replace(/;/g,',');
const csvDepot='Datum;Typ;Wertpapier;ISIN;Anzahl;Kurs;Betrag;Gebühren;Steuern\n15.01.2026;Kauf;Fonds '+X+';IE00BK5BQT80;1;100,00;-100,00;0,00;0,00\n16.01.2026;Kauf;'+X+';XX'+X+';2;10,00;-20,00;0,00;0,00\n';
const csvBank='Buchungstag;Empfänger;Verwendungszweck;Betrag\n01.03.2024;'+P.replace(/;/g,',')+';Abo '+P.replace(/;/g,',')+';-9,99\n01.04.2024;'+P.replace(/;/g,',')+';Abo '+P.replace(/;/g,',')+';-9,99\n01.05.2024;'+P.replace(/;/g,',')+';Abo;-9,99\n';
const yahoo={quotes:[{symbol:'EVIL"><img src=x data-xss>',shortname:P,quoteType:'EQUITY',exchDisp:P},{symbol:'AAPL',longname:P,quoteType:'ETF',exchange:P}]};
let fail=[];
async function count(p,where){const r=await p.evaluate(()=>({n:document.querySelectorAll('[data-xss]').length,x:!!window.__x})).catch(()=>({n:0,x:false}));if(r.n||r.x)fail.push(where+': '+r.n+' eingeschleuste Elemente'+(r.x?' + Skript ausgeführt':''));}
(async()=>{const b=await chromium.launch();
 for(const lang of ['de','en']){
  const c=await b.newContext({serviceWorkers:'block'});
  await c.route('**/*',r=>{const u=r.request().url();if(u.startsWith(BASE))return r.continue();
   if(u.includes('finance/search'))return r.fulfill({contentType:'application/json',body:JSON.stringify(yahoo)});
   if(u.includes('finance/chart'))return r.fulfill({contentType:'application/json',body:JSON.stringify({chart:{result:[{meta:{regularMarketPrice:1,currency:P}}]}})});
   if(u.includes('coingecko'))return r.fulfill({contentType:'application/json',body:JSON.stringify({bitcoin:{eur:P}})});
   return r.abort();});
  await c.addInitScript(f=>{if(!sessionStorage.getItem('seeded')){localStorage.setItem('geldkompass.v3',JSON.stringify(f));localStorage.setItem('geld-kompass-currency','EUR');sessionStorage.setItem('seeded','1');}},fixture);
  const p=await c.newPage();p.on('dialog',d=>{fail.push(lang+': Dialog geöffnet ('+d.message().slice(0,40)+')');d.dismiss();});
  await p.goto(BASE+'/app/?lang='+lang);await p.waitForTimeout(1200);
  for(const pg of ['overview','bookings','debts','assets','plan','recurring','calc','examples','book','data','plus','nomad']){await p.evaluate(pg=>{location.hash=pg;},pg);await p.waitForTimeout(350);await count(p,lang+' gespeicherte Daten #'+pg);}
  // Depot-Suche mit gefälschter Antwort eines Kursdienstes
  await p.evaluate(()=>{location.hash='assets';});await p.waitForTimeout(300);
  if(await p.locator('#vSym').count()){await p.evaluate(()=>{const e=document.getElementById('vSym');if(e){e.closest('.hide')&&e.closest('.hide').classList.remove('hide');}});
   await p.fill('#vSym','evilcorp').catch(()=>{});await p.waitForTimeout(300);
   const on=p.locator('[data-online]');if(await on.count())await on.first().click({force:true}).catch(()=>{});await p.waitForTimeout(800);await count(p,lang+' Online-Suche (Kursdienst-Antwort)');}
  // CSV-Importe
  for(const [id,txt,name] of [['csvFile',csvDepot,'depot.csv'],['bankFile',csvBank,'bank.csv']]){if(await p.locator('#'+id).count()){await p.setInputFiles('#'+id,{name,mimeType:'text/csv',buffer:Buffer.from(txt,'utf8')}).catch(e=>fail.push(id+': '+e.message));await p.waitForTimeout(900);await count(p,lang+' CSV-Import '+id);}}
  // Teilen-Link der App
  const share={v:1,kind:'wi',currency:'EUR',values:{title:P.slice(0,190),amt:5,per:'day',years:10,symbol:'IWDA',rate:7,worldRate:7}};
  const q=await c.newPage();await q.goto(BASE+'/app/?lang='+lang+'#wiCard&gk='+encodeURIComponent(JSON.stringify(share)));await q.waitForTimeout(1200);await count(q,lang+' Teilen-Link App');
  // Teilen-Links der Rechner (alle Werte als Text mit Schadcode)
  for(const r of ['/rechner/sparplan-rechner/','/rechner/euro-in-baht/','/rechner/abo-als-aktie/','/en/calculators/inflation-calculator/']){
   const vals={};['a','b','c','d','amt','rate','years','title','from','to','name','x'].forEach(k=>vals[k]=P);
   await q.goto(BASE+r+'?lang='+lang+'#gk='+encodeURIComponent(JSON.stringify({v:1,kind:'form',currency:P,values:vals})));await q.waitForTimeout(700);await count(q,lang+' Teilen-Link '+r);}
  await c.close();}
 await b.close();
 if(fail.length){console.log('FEHLER:');[...new Set(fail)].forEach(f=>console.log('::error::'+f));process.exit(1);}
 console.log('OK: keine eingeschleusten Elemente in gespeicherten Daten, Teilen-Links, CSV-Importen und Kursdienst-Antworten');})();
