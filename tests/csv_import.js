// Prüft den Depot-CSV-Import mit Beispiel-Exporten verschiedener Banken und Broker.
const fs=require("fs"),path=require("path"),vm=require("vm");
const root=path.join(__dirname,"..");
const html=fs.readFileSync(path.join(root,"app/index.html"),"utf8");
const src=process.env.CSVIMP?fs.readFileSync(process.env.CSVIMP,"utf8"):html.slice(html.indexOf("/* CSVIMP-START */"),html.indexOf("/* CSVIMP-END */"));
const sl=html.slice(html.indexOf("function searchLocal(q)"));const slSrc=sl.slice(0,sl.indexOf("\nfunction ",10)+1);
const INSTR=JSON.parse(fs.readFileSync(path.join(root,"scripts/instruments.json"),"utf8"));
const ctx={TextDecoder,INSTR,IMAP:{},ISIN:{},console};INSTR.forEach(x=>{ctx.IMAP[x.s]=x;if(x.i)ctx.ISIN[x.i]=x;x._q=(x.n+" "+x.s+" "+(x.i||"")+" "+(x.de||"")+" "+(x.a||"")+" "+x.t).toLowerCase();});
vm.createContext(ctx);vm.runInContext(slSrc+"\n"+src,ctx);
const read=f=>{const b=fs.readFileSync(path.join(__dirname,"csv",f));return ctx.csvDecode?ctx.csvDecode(new Uint8Array(b)):b.toString("utf8");};
let fail=0;const near=(a,b,e)=>Math.abs(a-b)<=(e||0.005*Math.max(1,Math.abs(b)));
function check(file,exp){const r=ctx.parseCSV(read(file),{en:false});if(!r||r.err){console.log("FEHLER",file,r&&r.err);fail++;return;}
  const by={};r.rows.forEach(p=>by[p.isin||p.sym]=p);let ok=true;const msg=[];
  if(exp.trans!=null&&r.trans!==exp.trans){ok=false;msg.push("Modus "+r.trans);}
  if(exp.count!=null&&r.rows.length!==exp.count){ok=false;msg.push("Anzahl "+r.rows.length+" statt "+exp.count);}
  Object.entries(exp.pos).forEach(([k,e])=>{const p=by[k];if(!p){ok=false;msg.push(k+" fehlt");return;}
    if(e.s&&(!p.x||p.x.s!==e.s)){ok=false;msg.push(k+" erkannt als "+(p.x&&p.x.s));}
    if(e.qty!=null&&!near(p.qty,e.qty,1e-6)){ok=false;msg.push(k+" Stück "+p.qty+" statt "+e.qty);}
    if(e.buy!=null&&!near(p.buy,e.buy,0.01)){ok=false;msg.push(k+" Einstand "+p.buy.toFixed(4)+" statt "+e.buy);}
    if(e.cur&&p.cur!==e.cur){ok=false;msg.push(k+" Währung "+p.cur);}
    if(e.div!=null&&!near(p.div,e.div,0.001)){ok=false;msg.push(k+" Dividende "+p.div);}
    if(e.n!=null&&p.n!==e.n){ok=false;msg.push(k+" Buchungen "+p.n+" statt "+e.n);}});
  if(exp.skipped){const s=JSON.stringify(r.skipped);if(s!==JSON.stringify(exp.skipped)){ok=false;msg.push("übersprungen "+s);}}
  console.log((ok?"OK   ":"FEHLER ")+file+(msg.length?" → "+msg.join("; "):"")+"  ["+r.rows.map(p=>(p.x?p.x.s:"?"+p.name)+" "+p.qty).join(", ")+"]");if(!ok)fail++;}
check("comdirect_depot.csv",{trans:false,count:4,pos:{
  IE00B4L5Y983:{s:"EUNL.DE",qty:42,buy:78.55},DE0007164600:{s:"SAP.DE",qty:15,buy:180.2},US0378331005:{s:"AAPL",qty:3.5,buy:150.1234},DE0005557508:{s:"DTE.DE",qty:1250,buy:14.1}}});
check("ing_depot.csv",{trans:false,count:4,pos:{
  IE00BK5BQT80:{s:"VWCE.DE",qty:120,buy:98.45},US1912161007:{s:"KO",qty:25,buy:58.2},US7561091049:{s:"O",qty:40,buy:52.1},DE0008404005:{s:"ALV.DE",qty:8,buy:210.55}}});
check("scalable_transaktionen.csv",{trans:true,count:2,skipped:{"storniert":1,"Einzahlung":1,"Gebühr":1},pos:{
  IE00B4L5Y983:{s:"EUNL.DE",qty:7.046,buy:(2.345*85.30+2.301*86.93+2.4*83.34)/7.046,n:3},US0378331005:{s:"AAPL",qty:3,buy:201.398,div:0.78,n:3}}});
check("traderepublic_transaktionen.csv",{trans:true,count:3,skipped:{"Einzahlung":1},pos:{
  IE00BK5BQT80:{s:"VWCE.DE",qty:1.6103,buy:(0.8123*123.11+0.798*125.31)/1.6103,n:2},XF000BTC0017:{s:"BTC-EUR",qty:0.006,buy:82600},US7561091049:{s:"O",qty:20,buy:51.30,div:3.21,n:2}}});
check("revolut_trading.csv",{trans:true,count:2,skipped:{"Einzahlung":1,"Gebühr":1},pos:{
  KO:{s:"KO",qty:6,buy:61.2,cur:"USD",div:4.85,n:3},MSFT:{s:"MSFT",qty:2.5,buy:(1.5*410+1020)/2.5,cur:"USD"}}});
check("ibkr_activity.csv",{trans:false,count:4,pos:{
  AAPL:{s:"AAPL",qty:12,buy:180.5521,cur:"USD"},O:{s:"O",qty:100,buy:55.12,cur:"USD"},SAP:{s:"SAP.DE",qty:4,buy:170.25,cur:"EUR"},"BRK B":{s:"BRK-B",qty:2,buy:410.1,cur:"USD"}}});
check("dkb_depot_latin1.csv",{trans:false,count:3,pos:{
  DE000BASF111:{s:"BAS.DE",qty:10,buy:52.3},DE0007236101:{s:"SIE.DE",qty:0.25,buy:155},DE0006231004:{s:"IFX.DE",qty:2000,buy:28.111}}});
// Doppelter Import derselben Buchungsliste darf nichts verdoppeln
{const a=ctx.parseCSV(read("scalable_transaktionen.csv"),{});const seen={};a.rows.forEach(p=>p.hashes.forEach(h=>seen[h]=1));const b=ctx.parseCSV(read("scalable_transaktionen.csv"),{seen});
 const ok=b.rows.length===0&&b.dup===6;console.log((ok?"OK   ":"FEHLER ")+"Zweiter Import derselben Datei: "+b.dup+" Buchungen als bereits übernommen erkannt");if(!ok)fail++;}
if(fail){console.log(fail+" Prüfung(en) fehlgeschlagen");process.exit(1);}console.log("Alle CSV-Prüfungen bestanden.");
