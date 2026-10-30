/* Gemeinsame Helfer für die Geld-Kompass-Rechner (deutsch und englisch, Sprache aus <html lang>) */
(function(){
'use strict';
var BASE='https://geld-kompass.com/';
var EN=(document.documentElement.lang||'de').slice(0,2)==='en',LANG=EN?'en':'de',LOC=EN?'en-GB':'de-DE';
/* Währung der Rechner: gespeicherte Wahl (gemeinsam mit dem Geld-Kompass) > Region des Browsers > Sprache */
var CURS=['EUR','USD','GBP','CHF','CAD','AUD'],CKEY='geld-kompass-currency',CUR=null;
try{CUR=localStorage.getItem(CKEY);}catch(e){}
if(CURS.indexOf(CUR)<0){var nl=(navigator.language||'').toUpperCase();CUR=/-CH$/.test(nl)?'CHF':/-GB$/.test(nl)?'GBP':/-CA$/.test(nl)?'CAD':/-AU$/.test(nl)?'AUD':EN?(/-US$/.test(nl)?'USD':'USD'):'EUR';}
var eur0,eur2,SYM;
function setFmt(){if(EN)LOC=CUR==='GBP'?'en-GB':'en-US';eur0=new Intl.NumberFormat(LOC,{style:'currency',currency:CUR,maximumFractionDigits:0});eur2=new Intl.NumberFormat(LOC,{style:'currency',currency:CUR,minimumFractionDigits:2,maximumFractionDigits:2});
  SYM=(eur0.formatToParts(1).filter(function(x){return x.type==='currency';})[0]||{value:'€'}).value;}
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
  var url=BASE+path+'?ref=wa&lang='+LANG,plain=BASE+path+'?lang='+LANG;
  var full=text+(EN?'\n\nCheck it yourself (free): ':'\n\nRechne es selbst nach (kostenlos): ')+url;
  el.innerHTML='<a class="btn pri" target="_blank" rel="noopener" href="https://wa.me/?text='+encodeURIComponent(full)+'">'+WA+(EN?'Share on WhatsApp':'Per WhatsApp teilen')+'</a>'+
    '<button class="btn" type="button" data-copy>'+(EN?'Copy link':'Link kopieren')+'</button>';
  el.querySelector('[data-copy]').onclick=function(){var b=this;(navigator.clipboard?navigator.clipboard.writeText(plain):Promise.reject()).then(function(){b.textContent=EN?'Copied ✓':'Kopiert ✓';},function(){prompt(EN?'Copy link:':'Link kopieren:',plain);});};
}
var RUNS=[];
function bind(ids,fn){RUNS.push(fn);ids.forEach(function(id){var e=$(id);if(e){e.addEventListener('input',fn);e.addEventListener('change',fn);}});fn();}
/* Währungsauswahl in jedem Rechner (nicht im Währungs- und Inflationsrechner, die haben eigene Währungen) */
(function(){var box=document.querySelector('.calc');if(!box||$('from')||$('geo'))return;
  var NAMES=EN?{EUR:'Euro (€)',USD:'US dollar ($)',GBP:'British pound (£)',CHF:'Swiss franc (CHF)',CAD:'Canadian dollar (CA$)',AUD:'Australian dollar (A$)'}:{EUR:'Euro (€)',USD:'US-Dollar ($)',GBP:'Britisches Pfund (£)',CHF:'Schweizer Franken (CHF)',CAD:'Kanadischer Dollar (CA$)',AUD:'Australischer Dollar (A$)'};
  var row=document.createElement('div');row.className='curbar';
  row.innerHTML='<label>'+(EN?'Currency':'Währung')+'<select id="gkCur">'+CURS.map(function(c){return '<option value="'+c+'">'+NAMES[c]+'</option>';}).join('')+'</select></label>';
  box.insertBefore(row,box.firstChild);var sel=$('gkCur');sel.value=CUR;
  /* Währungszeichen in Beschriftungen und Schnellwahl-Knöpfen mitführen */
  var nodes=[],w=document.createTreeWalker(box,NodeFilter.SHOW_TEXT),n;while((n=w.nextNode())){if(n.parentNode&&n.parentNode.closest&&n.parentNode.closest('.curbar'))continue;if(n.nodeValue.indexOf('€')>-1)nodes.push([n,n.nodeValue]);}
  function relabel(){nodes.forEach(function(x){x[0].nodeValue=x[1].replace(/€/g,SYM);});}
  relabel();
  sel.addEventListener('change',function(){CUR=sel.value;try{localStorage.setItem(CKEY,CUR);}catch(e){}setFmt();relabel();RUNS.forEach(function(f){try{f();}catch(e){}});});
})();
if('serviceWorker' in navigator){window.addEventListener('load',function(){navigator.serviceWorker.register('/sw.js').catch(function(){});});}
window.GKR={num:num,$:$,val:val,E:E,nf1:nf1,nf0:nf0,monthName:monthName,esc:esc,share:share,bind:bind,BASE:BASE,EN:EN,LANG:LANG};
})();
