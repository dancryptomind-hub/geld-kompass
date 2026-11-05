/* Unabhängige Rechenfälle: gleiches Wertpapier in mehreren Wallets/Brokern. */
const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
const html=fs.readFileSync('app/index.html','utf8');
function extract(name){const start=html.indexOf('function '+name+'(');assert.ok(start>=0,name+' vorhanden');let end=html.indexOf('\nfunction ',start+1);if(end<0)end=html.length;return html.slice(start,end);}
const holdings=[{s:'BTC',name:'Bitcoin',qty:31,price:1000,t:'Krypto',src:'Wallet'},{s:'BTC',name:'Bitcoin',qty:20.2,price:1000,t:'Krypto',src:'Broker'},{s:'WORLD',name:'Weltfonds',qty:48.8,price:1000,t:'ETF'}];
const ctx={D:()=>({hold:holdings}),holdInfo:h=>({name:h.name,t:h.t,value:h.qty*h.price,price:h.price,cost:null,pl:null}),S:{mode:'own',own:{realized:[]}},IMAP:{},num:x=>Number(x)||0,LG:(de,en)=>de,esc:x=>x,pct:x=>(x*100).toFixed(1)+' %',E:x=>x.toFixed(2),nf1:{format:String},priceOf:()=>0,fdate:x=>x};vm.createContext(ctx);
if(html.includes('function portfolioGroups('))vm.runInContext(extract('portfolioGroups'),ctx);
vm.runInContext(extract('auditCalc'),ctx);let a=ctx.auditCalc();
assert.equal(a.tot,100000);assert.ok(Math.abs(a.topSh-.512)<1e-12,'Bitcoin gesamt: 51,2 %, nicht nur eine Wallet');
let finding=a.F.find(x=>x.t==='Klumpenrisiko');assert.ok(finding.d.includes('51.2 %'));assert.ok(finding.d.includes('25600.00'),'50 % Verlust auf ALLE Bitcoin-Bestände');
holdings.splice(0,holdings.length,{s:'BTC',name:'Bitcoin',qty:100,price:10,t:'Krypto'});a=ctx.auditCalc();assert.equal(a.topSh,1);assert.ok(a.F.some(x=>x.t==='Klumpenrisiko'),'Einzelposition mit 100 % nicht übersehen');
holdings.push({s:'UNKNOWN',name:'Ohne Kurs',qty:10,price:0,t:'Aktie'});a=ctx.auditCalc();assert.equal(a.tot,1000,'Fehlender Kurs verdünnt Anteil nicht');
if(ctx.portfolioGroups){let rows=[{h:{s:'BTC',src:'A'},name:'Bitcoin',t:'Krypto',value:20,pl:5,cost:15},{h:{s:'BTC',src:'B'},name:'Bitcoin',t:'Krypto',value:30,pl:10,cost:20}];const g=ctx.portfolioGroups(rows);assert.equal(g.length,1);assert.equal(g[0].v,50);assert.equal(g[0].pl,15);assert.equal(g[0].cost,35);}
console.log('Audit: mehrere Wallets korrekt zusammengeführt, 51,2 %, voller Verlustbetrag, Einzelwert und fehlender Kurs geprüft');
ctx.FXCRYPTO={BTC:1,ETH:1};vm.runInContext(extract('fxSymbol'),ctx);assert.equal(ctx.fxSymbol('USD','EUR').s,'FX_IDC:USDEUR');assert.equal(ctx.fxSymbol('THB','GBP').s,'FX_IDC:THBGBP','Kein stiller Austausch gegen EUR');
console.log('Währungspaare: USD/EUR und Kreuzkurs verwenden die gewählte Richtung');
