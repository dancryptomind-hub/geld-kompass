/* Sicherheit: Content-Security-Policy.
   1) Jede Seite hat den aktuellen CSP-Tag (python3 scripts/csp.py --check).
   2) Keine Seite verletzt ihre CSP beim Laden und Durchklicken (sonst wäre eine Funktion live kaputt).
   3) Keine Inline-Handler (onclick= usw.) im Code, die die CSP blockieren würde.
   Lokal: python3 -m http.server 8765 & node tests/csp.js */
const {chromium}=require('playwright');const {execFileSync}=require('child_process');const fs=require('fs');
const BASE=process.env.BASE||'http://localhost:8765';let fail=[];
try{console.log(execFileSync('python3',['scripts/csp.py','--check']).toString().trim());}catch(e){console.log(String(e.stdout||e.message));fail.push('CSP-Tag fehlt oder veraltet');}
const app=fs.readFileSync('app/index.html','utf8');
const inl=app.match(/["'][^"']*\son(click|error|load|change|input|submit|mouseover|focus|blur|keydown|keyup)=/g);if(inl)fail.push('Inline-Handler in app/index.html: '+inl.slice(0,3).join(' | '));
if(!app.includes('window.onload=function(){window.print();}'))console.log('Hinweis: Druckfenster-Skript geändert – EXTRA in scripts/csp.py anpassen');
const pages=execFileSync('git',['ls-files','*.html']).toString().split('\n').filter(f=>f&&!/^(scripts|tests|vendor)\//.test(f)&&!/^google/.test(f)).map(f=>'/'+f.replace(/index\.html$/,''));
const fixture={v:4,chv:2,mode:'own',onboarded:1,own:{cur:'EUR',entries:[{id:'e1',title:'Gehalt',amount:3000,type:'income',cat:'Gehalt',freq:'monthly',date:'2020-01-01'}],items:[{id:'i1',name:'Reserve',side:'Aktiva',value:10000,cls:'Girokonto'}],debts:[],hold:[{id:'h1',s:'AAPL',qty:2,tx:[]}],cache:{}}};
(async()=>{const b=await chromium.launch();
 await Promise.all(['de','en'].map(async(lang)=>{const c=await b.newContext({serviceWorkers:'block'});
  await c.route('**/*',r=>r.request().url().startsWith(BASE)?r.continue():r.abort());
  await c.addInitScript(()=>{window.__csp=[];document.addEventListener('securitypolicyviolation',e=>window.__csp.push(e.violatedDirective+' '+(e.blockedURI||'inline')+' '+(e.sourceFile||'').replace(location.origin,'')+':'+e.lineNumber));});
  const p=await c.newPage();
  const visit=async(u,extra)=>{await p.goto(BASE+u+(u.includes('?')?'&':'?')+'lang='+lang,{waitUntil:'load'}).catch(()=>{});await p.waitForTimeout(400);if(extra)await extra();const v=await p.evaluate(()=>window.__csp||[]);v.forEach(x=>fail.push(lang+' '+u+': '+x));};
  for(const u of pages)await visit(u);
  await c.addInitScript(f=>{if(!localStorage.getItem('gk-csp-seeded')){localStorage.setItem('geldkompass.v3',JSON.stringify(f));localStorage.setItem('gk-csp-seeded','1');}},fixture);
  await visit('/app/',async()=>{for(const pg of ['overview','bookings','debts','assets','plan','recurring','calc','examples','book','data','plus']){await p.evaluate(pg=>{location.hash=pg;},pg);await p.waitForTimeout(250);}});
  await c.close();}));
 await b.close();
 if(fail.length){console.log('FEHLER:');[...new Set(fail)].slice(0,60).forEach(f=>console.log('::error::'+f));process.exit(1);}
 console.log('OK: '+pages.length+' Seiten je Sprache ohne CSP-Verletzung');})();
