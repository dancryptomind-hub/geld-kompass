/* Gemeinsame Helfer für die Geld-Kompass-Rechner (deutsch und englisch, Sprache aus <html lang>) */
(function(){
'use strict';
var BASE='https://geld-kompass.com/';
var EN=(document.documentElement.lang||'de').slice(0,2)==='en',LANG=EN?'en':'de',LOC=EN?'en-GB':'de-DE';
/* Währung der Rechner: gespeicherte Wahl (gemeinsam mit dem Geld-Kompass Pro) > Region des Browsers > Sprache */
var SHARED=window.GKShareState.read();
var CURS=['EUR','USD','GBP','CHF','CAD','AUD'],CKEY='geld-kompass-currency',CUR=null;
try{CUR=localStorage.getItem(CKEY);}catch(e){}
if(CURS.indexOf(CUR)<0){var nl=(navigator.language||'').toUpperCase();CUR=/-CH$/.test(nl)?'CHF':/-GB$/.test(nl)?'GBP':/-CA$/.test(nl)?'CAD':/-AU$/.test(nl)?'AUD':EN?(/-US$/.test(nl)?'USD':'USD'):'EUR';}
if(SHARED&&'EUR,USD,GBP,CHF,JPY,CNY,CAD,AUD,NZD,SEK,NOK,DKK,ISK,PLN,CZK,HUF,RON,BGN,RSD,TRY,UAH,RUB,GEL,AMD,AZN,KZT,AED,SAR,QAR,ILS,EGP,MAD,ZAR,NGN,KES,INR,LKR,THB,VND,MYR,SGD,IDR,PHP,KHR,LAK,HKD,TWD,KRW,BRL,MXN,ARS,CLP,COP,PEN'.split(',').includes(SHARED.currency)){CUR=SHARED.currency;if(!CURS.includes(CUR))CURS.push(CUR);}
var eur0,eur2,SYM;
function setFmt(){if(EN)LOC=CUR==='GBP'?'en-GB':'en-US';eur0=new Intl.NumberFormat(LOC,{style:'currency',currency:CUR,maximumFractionDigits:0});eur2=new Intl.NumberFormat(LOC,{style:'currency',currency:CUR,minimumFractionDigits:2,maximumFractionDigits:2});
  SYM=(eur0.formatToParts(1).filter(function(x){return x.type==='currency';})[0]||{value:'€'}).value;}
/* Einbetten (?embed=1): Währung aus ?cur= */
var QS=new URLSearchParams(location.search),EMBED=QS.get('embed')==='1';(function(){var qc=(QS.get('cur')||'').toUpperCase();if(CURS.indexOf(qc)>-1)CUR=qc;})();
setFmt();
var nf1=new Intl.NumberFormat(LOC,{maximumFractionDigits:1});
var nf0=new Intl.NumberFormat(LOC,{maximumFractionDigits:0});
var MON=EN?['January','February','March','April','May','June','July','August','September','October','November','December']:['Januar','Februar','März','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember'];
/* Zahlen lesen: deutsch "1.234,56", englisch "1,234.56"; einzelnes Komma oder einzelner Punkt gilt als Dezimaltrenner */
function num(v){if(typeof v==='number')return v;v=String(v==null?'':v).trim().replace(/\s|€|%|\$|£/g,'');
  if(v.indexOf(',')>-1&&v.indexOf('.')>-1){v=EN?v.replace(/,/g,''):v.replace(/\./g,'').replace(',','.');}
  else if(v.indexOf(',')>-1){v=(EN&&/^\d{1,3}(,\d{3})+$/.test(v))?v.replace(/,/g,''):v.replace(',','.');}
  var n=parseFloat(v);return isFinite(n)?n:0;}
function $(id){return document.getElementById(id);}
function val(id){return num($(id).value);}
function E(x){return (Math.abs(x)>=1000||Math.abs(x-Math.round(x))<0.005)?eur0.format(x):eur2.format(x);}
function monthName(offset){var d=new Date();d.setDate(1);d.setMonth(d.getMonth()+Math.round(offset));return MON[d.getMonth()]+' '+d.getFullYear();}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
var WA='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3a9 9 0 0 0-7.8 13.5L3 21l4.6-1.2A9 9 0 1 0 12 3z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>';
/* Teilen: Text + Link zur Rechnerseite. Der Link trägt die Sprache des Absenders (lang=de/en),
   damit die Seite beim Empfänger in derselben Sprache öffnet. Persönliche Zahlen teilt nur, wer klickt. */
function share(el,text,path){
  var data={values:{},currency:CUR};document.querySelectorAll('.calc input[id],.calc select[id]').forEach(function(e){if(!['password','hidden','file'].includes(e.type))data.values[e.id]=e.value;});
  var url=GKShareState.link(path,data,LANG,'wa'),plain=GKShareState.link(path,data,LANG);
  var full=text+(EN?'\n\nCheck it yourself (free): ':'\n\nRechne es selbst nach (kostenlos): ')+url;
  el.innerHTML='<a class="btn pri" target="_blank" rel="noopener" href="https://wa.me/?text='+encodeURIComponent(full)+'">'+WA+(EN?'Share on WhatsApp':'Per WhatsApp teilen')+'</a>'+
    '<button class="btn" type="button" data-copy>'+(EN?'Copy link':'Link kopieren')+'</button>';
  el.querySelector('[data-copy]').onclick=function(){var b=this;(navigator.clipboard?navigator.clipboard.writeText(plain):Promise.reject()).then(function(){b.textContent=EN?'Copied ✓':'Kopiert ✓';},function(){prompt(EN?'Copy link:':'Link kopieren:',plain);});};
}
var RUNS=[];
function restore(ids){if(!SHARED)return;ids.forEach(function(id){var e=$(id),v=SHARED.values[id];if(!e||!e.closest('.calc')||typeof v!=='string'||v.length>200||['password','hidden','file'].includes(e.type))return;
 if(e.tagName==='SELECT'&&!Array.from(e.options).some(function(o){return o.value===v;}))return;
 if(e.tagName==='INPUT'&&e.inputMode&&v!==''&&!/^[+\-]?\d[\d., ]*(?:e[+\-]?\d+)?$/i.test(v))return;e.value=v;});}
function sharedNote(){if(!SHARED||$('gkSharedNote'))return;var box=document.querySelector('.calc');if(!box)return;var p=document.createElement('p');p.id='gkSharedNote';p.className='note';p.textContent=EN?'Shared calculation: the sender’s inputs are loaded. Exchange rates and other current data may change.':'Geteilte Berechnung: Die Eingaben des Absenders sind geladen. Wechselkurse und andere aktuelle Daten können sich ändern.';box.prepend(p);}
restore(Array.from(document.querySelectorAll('.calc input[id],.calc select[id]')).map(function(e){return e.id;}));
function bind(ids,fn){restore(ids);sharedNote();RUNS.push(fn);ids.forEach(function(id){var e=$(id);if(e){e.addEventListener('input',fn);e.addEventListener('change',fn);}});fn();}
/* Währungsauswahl in jedem Rechner (nicht im Währungs- und Inflationsrechner, die haben eigene Währungen) */
(function(){var box=document.querySelector('.calc');if(!box||$('from')||$('geo'))return;
  var NAMES=EN?{EUR:'Euro (€)',USD:'US dollar ($)',GBP:'British pound (£)',CHF:'Swiss franc (CHF)',CAD:'Canadian dollar (CA$)',AUD:'Australian dollar (A$)'}:{EUR:'Euro (€)',USD:'US-Dollar ($)',GBP:'Britisches Pfund (£)',CHF:'Schweizer Franken (CHF)',CAD:'Kanadischer Dollar (CA$)',AUD:'Australischer Dollar (A$)'};
  var row=document.createElement('div');row.className='curbar';
  row.innerHTML='<label>'+(EN?'Currency':'Währung')+'<select id="gkCur">'+CURS.map(function(c){return '<option value="'+c+'">'+(NAMES[c]||c)+'</option>';}).join('')+'</select></label>';
  box.insertBefore(row,box.firstChild);var sel=$('gkCur');sel.value=CUR;
  /* Währungszeichen in Beschriftungen und Schnellwahl-Knöpfen mitführen */
  var nodes=[],w=document.createTreeWalker(box,NodeFilter.SHOW_TEXT),n;while((n=w.nextNode())){if(n.parentNode&&n.parentNode.closest&&n.parentNode.closest('.curbar'))continue;if(n.nodeValue.indexOf('€')>-1)nodes.push([n,n.nodeValue]);}
  function relabel(){nodes.forEach(function(x){x[0].nodeValue=x[1].replace(/€/g,SYM);});}
  relabel();
  sel.addEventListener('change',function(){CUR=sel.value;try{localStorage.setItem(CKEY,CUR);}catch(e){}setFmt();relabel();RUNS.forEach(function(f){try{f();}catch(e){}});});
})();
/* Eine Quelle (Gemini Phase 1): eigene Zahlen aus dem Geld-Kompass Pro auf Knopfdruck übernehmen. Liest nur die Kurzfassung auf diesem Gerät. */
(function(){if(SHARED)return;var box=document.querySelector('.calc');if(!box)return;var G=null;try{G=JSON.parse(localStorage.getItem('geld-kompass-summary')||'null');}catch(e){}if(!G||G.v!==1)return;
  function cv(v){var a=G.rates&&G.rates[CUR],b=G.rcur||1;if(G.cur===CUR||!a)return v;return Math.round(v/b*a);}
  var path=location.pathname,D=G.debts||[],totB=D.reduce(function(s,x){return s+x.b;},0),totP=D.reduce(function(s,x){return s+x.p;},0),wr=totB?D.reduce(function(s,x){return s+x.b*x.r;},0)/totB:0,save=Math.max(0,G.surplus)+Math.max(0,G.invest);
  var M=null;
  if(/sparplan|savings-plan/.test(path))M={rate:cv(Math.max(G.invest,save)||G.invest),start:cv(G.depot)};
  else if(/notgroschen|emergency-fund/.test(path))M={cost:cv(G.spend),have:cv(G.liquid),save:cv(Math.max(0,G.surplus))};
  else if(/freiheitstage|freedom-days/.test(path))M={assets:cv(G.aktiva),debts:cv(totB),spend:cv(G.spend),save:cv(save)};
  else if(/schuldenfrei|debt-free/.test(path)){if(!D.length)return;M={debt:cv(totB),rate:Math.round(wr*10)/10,pay:cv(totP),extra:cv(Math.max(0,G.surplus))};}
  else if(/schneeball|snowball/.test(path)){if(!D.length)return;M={budget:cv(totP+Math.max(0,G.surplus))};for(var i=0;i<4;i++){var x=D[i];M['b'+(i+1)]=x?cv(x.b):0;M['r'+(i+1)]=x?x.r:0;M['m'+(i+1)]=x?cv(x.p):0;}}
  else if(/vier-prozent|4-percent/.test(path))M={spend:cv(G.spend),have:cv(G.liquid+G.depot),save:cv(save)};
  else if(/kreditkarten|credit-card/.test(path)){var c=D.filter(function(x){return x.k==='card';})[0];if(!c)return;M={bal:cv(c.b),apr:c.r,fix:cv(c.p)};}
  if(!M)return;var keys=Object.keys(M).filter(function(k){return $(k);});if(!keys.length)return;
  var bar=document.createElement('div');bar.className='gkfill';
  bar.innerHTML='<div><b>'+(EN?'Use your numbers from Geld-Kompass Pro':'Deine Zahlen aus dem Geld-Kompass Pro übernehmen')+'</b><small>'+(EN?'From your app on this device, as of ':'Aus deiner App auf diesem Gerät, Stand ')+esc(G.at)+(EN?'. Nothing is sent.':'. Es wird nichts gesendet.')+'</small></div><button type="button" class="gkfill-b">'+(EN?'Fill in':'Übernehmen')+'</button>';
  var cb=box.querySelector('.curbar');box.insertBefore(bar,cb?cb.nextSibling:box.firstChild);
  bar.querySelector('button').addEventListener('click',function(){keys.forEach(function(k){var el=$(k);el.value=String(M[k]).replace('.',EN?'.':',');if(el.type==='number')el.value=M[k];el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));});RUNS.forEach(function(f){try{f();}catch(e){}});bar.classList.add('done');bar.querySelector('button').textContent=EN?'Filled ✓':'Übernommen ✓';});
  var st=document.createElement('style');st.textContent='.gkfill{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;margin:0 0 14px;padding:12px 14px;border-radius:14px;border:1px solid rgba(227,181,90,.55);background:linear-gradient(135deg,rgba(245,213,143,.14),rgba(201,146,39,.06))}.gkfill b{display:block}.gkfill small{opacity:.75;font-size:.8rem}.gkfill-b{border:0;border-radius:10px;padding:9px 16px;font-weight:800;background:linear-gradient(135deg,#f5d58f,#c99227);color:#0e1730;cursor:pointer}.gkfill.done{border-color:rgba(111,207,151,.6)}';document.head.appendChild(st);
})();
/* Rechner zum Einbetten (Idee 7): ?embed=1 zeigt nur den Rechner, meldet die Höhe an die einbettende Seite und verlinkt dezent zurück */
(function(){if(!EMBED)return;var d=document.documentElement;d.classList.add('gk-embed');var host='';try{host=document.referrer?new URL(document.referrer).hostname:'';}catch(e){}
  var st=document.createElement('style');st.textContent=(QS.get('theme')==='light'?':root.gk-embed{--bg:#F6F3EC;--card:#FFFFFF;--card2:#F1ECE0;--ink:#14203A;--muted:#5A6580;--line:rgba(184,134,47,.35);--gold:#B8862F;--good:#1E8A64;--bad:#C2493C;color-scheme:light}':QS.get('theme')==='dark'?':root.gk-embed{--bg:#0E1730;--card:#16244A;--card2:#1B2C57;--gold:#E2B65A;--ink:#F4F1EA;--muted:#A9B2C6;--line:rgba(226,182,90,.28);--good:#5BC7A0;--bad:#F08A7E;color-scheme:dark}':'')+'.gk-embed body{background:var(--bg)}.gk-embed header.top,.gk-embed footer,.gk-embed .gkfill,.gk-embed .share,.gk-embed [data-partner],.gk-embed main>*:not(.calc):not(h1):not(.gkpow){display:none!important}.gk-embed main.wrap{padding:10px 12px 6px;max-width:none}.gk-embed h1{font-size:1.15rem;margin:0 0 10px;line-height:1.25}.gkpow{display:flex;justify-content:center;margin:14px 0 4px}.gkpow a{display:inline-flex;align-items:center;gap:10px;padding:7px 16px 7px 7px;border-radius:999px;border:1px solid var(--line);background:linear-gradient(135deg,rgba(226,182,90,.16),rgba(226,182,90,.04)),var(--card);color:var(--ink);text-decoration:none;box-shadow:0 6px 18px -10px rgba(0,0,0,.45);transition:transform .15s,box-shadow .15s}.gkpow a:hover,.gkpow a:focus-visible{transform:translateY(-1px);box-shadow:0 10px 24px -10px rgba(226,182,90,.55)}.gkpow img{width:30px;height:30px;border-radius:50%;flex:none}.gkpow span{display:flex;flex-direction:column;line-height:1.2;text-align:left}.gkpow small{font-size:.68rem;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}.gkpow b{font-size:.92rem;font-weight:800;color:var(--ink)}.gkpow b i{font-style:normal;color:var(--gold)}.gkpow em{font-style:normal;font-size:.72rem;color:var(--muted)}';document.head.appendChild(st);
  var main=document.querySelector('main');if(main){var p=document.createElement('div');p.className='gkpow';var home=EN?'/app/?lang=en':'/app/';p.innerHTML='<a href="https://geld-kompass.com'+home+(home.indexOf('?')>-1?'&':'?')+'ref=embed'+(host?'&host='+encodeURIComponent(host):'')+'" target="_blank" rel="noopener"><img src="/icons/logo-badge.webp?v=3" alt=""><span><small>'+(EN?'Powered by':'Bereitgestellt von')+'</small><b>Geld-<i>Kompass</i> Pro</b><em>'+(EN?'Free money app · no sign-up':'Kostenlose Finanz-App · ohne Anmeldung')+'</em></span></a>';main.appendChild(p);
    document.querySelectorAll('main a[href^="/"],main a[href^="https://geld-kompass.com"]').forEach(function(a){if(!a.target)a.target='_blank';});}
  function post(){try{parent.postMessage({gk:'h',h:Math.ceil(document.documentElement.scrollHeight)},'*');}catch(e){}}
  post();window.addEventListener('load',post);if(window.ResizeObserver)new ResizeObserver(post).observe(document.body);setInterval(post,1500);
})();
if('serviceWorker' in navigator){window.addEventListener('load',function(){navigator.serviceWorker.register('/sw.js').catch(function(){});});}
window.GKR={num:num,$:$,val:val,E:E,nf1:nf1,nf0:nf0,monthName:monthName,esc:esc,share:share,bind:bind,restore:restore,BASE:BASE,EN:EN,LANG:LANG};
})();
