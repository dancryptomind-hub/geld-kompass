/* Steuern nach Wohnsitz: Länderwerte (Spitzensatz Einkommensteuer, Satz für Kapitalerträge) vergleichen und mit eigenen Beträgen grob einordnen.
   Daten: /data/tax-residence.json (öffentliche Länderreferenzen mit Quellen). Orientierung, keine Steuerberatung. Sprache aus <html lang>. */
(function(){
'use strict';
var G=window.GKR,EN=(document.documentElement.lang||'de').slice(0,2)==='en',L=EN?1:0,DATA=null,box=document.getElementById('tx');
if(!box||!G)return;
var T=EN?{none:'– no comparison –',inc:'Income tax',cap:'Capital gains',top:'top rate',ref:'Reference rate',calcI:'Income tax at the top rate',calcC:'Tax on capital income',calcS:'Upper estimate in total',vary:'depends on income type',low:'Your actual tax is usually lower because of allowances and progressive brackets.',src:'Sources',chk:'Checked',err:'The country data is not available right now. Please try again later.',share1:'Taxes by residence: ',share2:' versus ',page:'Country page'}
       :{none:'– kein Vergleich –',inc:'Einkommensteuer',cap:'Kapitalerträge',top:'Spitzensatz',ref:'Referenzsatz',calcI:'Einkommensteuer zum Spitzensatz',calcC:'Steuer auf Kapitalerträge',calcS:'Obergrenze gesamt',vary:'je nach Ertragsart',low:'Deine tatsächliche Steuer ist wegen Freibeträgen und Stufentarif meist niedriger.',src:'Quellen',chk:'Geprüft',err:'Die Länderdaten sind gerade nicht erreichbar. Bitte später erneut versuchen.',share1:'Steuern nach Wohnsitz: ',share2:' im Vergleich zu ',page:'Länderseite'};
var SRC_EN=[['Einkommensteuergesetz','Income Tax Act'],['Einkommensteuer','Income tax'],['Private Kapitalgewinne','Private capital gains'],['Kapitalgewinne','Capital gains'],['Veräußerungsgewinne','Capital gains'],['Finanzministerium','Ministry of Finance'],['Tarife','Rates']];
function srcLabel(s){if(!EN)return s;SRC_EN.forEach(function(x){s=s.split(x[0]).join(x[1]);});return s;}
function maxRate(s){var m=String(s||'').replace(/,/g,'.').match(/\d+(\.\d+)?/g);if(!m)return null;return Math.max.apply(null,m.map(Number))/100;}
function nm(c){return DATA.countries[c].name[L];}
function card(c,inc,cap){var x=DATA.countries[c],ri=maxRate(x.incomeDisplay[0]),rc=maxRate(x.capitalDisplay[0]),ti=ri==null?null:inc*ri,tc=rc==null?null:cap*rc,sum=(ti||0)+(tc||0);
  var href=(EN?'/en/calculators/taxes-by-residence/':'/rechner/steuern-nach-wohnsitz/')+((EN?DATA.slugs_en:DATA.slugs)[c]||'')+'/';
  return '<div class="txc"><h3>'+G.esc(nm(c))+'</h3>'+
   '<div class="res"><div><span>'+T.inc+' · '+T.top+'</span><b class="gold">'+G.esc(x.incomeDisplay[L])+'</b></div><div><span>'+T.cap+' · '+T.ref+'</span><b class="gold">'+G.esc(x.capitalDisplay[L])+'</b></div></div>'+
   '<div class="res"><div><span>'+T.calcI+'</span><b>'+(ti==null?'–':G.E(ti))+'</b></div><div><span>'+T.calcC+'</span><b>'+(tc==null?T.vary:G.E(tc))+'</b></div><div><span>'+T.calcS+'</span><b class="neg">'+G.E(sum)+'</b></div></div>'+
   '<p class="note">'+G.esc(x.note[L])+'</p><p class="note">'+T.src+': '+x.sources.map(function(s){return '<a href="'+G.esc(s.url)+'" target="_blank" rel="noopener nofollow">'+G.esc(srcLabel(s.label))+'</a>';}).join(' · ')+' · '+T.chk+' '+G.esc(x.checked)+(box.getAttribute('data-c')===c?'':' · <a href="'+href+'">'+T.page+'</a>')+'</p></div>';}
function opts(sel,blank){var cs=Object.keys(DATA.countries).sort(function(a,b){return nm(a).localeCompare(nm(b),EN?'en':'de');});
  sel.innerHTML=(blank?'<option value="">'+T.none+'</option>':'')+cs.map(function(c){return '<option value="'+c+'">'+G.esc(nm(c))+'</option>';}).join('');}
function run(){if(!DATA)return;var a=G.$('txA').value,b=G.$('txB').value,inc=G.val('txInc'),cap=G.val('txCap');
  G.$('txOut').innerHTML='<div class="txgrid'+(b&&b!==a?' two':'')+'">'+card(a,inc,cap)+(b&&b!==a?card(b,inc,cap):'')+'</div><p class="note">'+T.low+'</p>';
  G.share(G.$('share'),T.share1+nm(a)+' ('+DATA.countries[a].incomeDisplay[L]+' / '+DATA.countries[a].capitalDisplay[L]+')'+(b&&b!==a?T.share2+nm(b)+' ('+DATA.countries[b].incomeDisplay[L]+' / '+DATA.countries[b].capitalDisplay[L]+')':''),(EN?'en/calculators/taxes-by-residence/':'rechner/steuern-nach-wohnsitz/'));}
fetch('/data/tax-residence.json',{cache:'no-cache'}).then(function(r){return r.json();}).then(function(d){DATA=d;opts(G.$('txA'),false);opts(G.$('txB'),true);
  G.$('txA').value=box.getAttribute('data-c')||(EN?'TH':'DE');G.$('txB').value=box.getAttribute('data-cmp')||'';
  var q=new URLSearchParams(location.search);if(DATA.countries[q.get('c')])G.$('txA').value=q.get('c');if(DATA.countries[q.get('vs')])G.$('txB').value=q.get('vs');
  try{G.restore(['txA','txB']);}catch(e){}run();}).catch(function(){G.$('txOut').innerHTML='<p class="note">'+T.err+'</p>';});
G.bind(['txA','txB','txInc','txCap'],run);
})();
