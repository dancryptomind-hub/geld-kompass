/* Gemeinsame Helfer für die Geld-Kompass-Rechner */
(function(){
'use strict';
var BASE='https://geld-kompass.com/';
var eur0=new Intl.NumberFormat('de-DE',{style:'currency',currency:'EUR',maximumFractionDigits:0});
var eur2=new Intl.NumberFormat('de-DE',{style:'currency',currency:'EUR',minimumFractionDigits:2,maximumFractionDigits:2});
var nf1=new Intl.NumberFormat('de-DE',{maximumFractionDigits:1});
var nf0=new Intl.NumberFormat('de-DE',{maximumFractionDigits:0});
var MON=['Januar','Februar','März','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember'];
function num(v){if(typeof v==='number')return v;v=String(v==null?'':v).trim().replace(/\s|€|%/g,'');if(v.indexOf(',')>-1)v=v.replace(/\./g,'').replace(',','.');var n=parseFloat(v);return isFinite(n)?n:0;}
function $(id){return document.getElementById(id);}
function val(id){return num($(id).value);}
function E(x){return (Math.abs(x)>=1000||Math.abs(x-Math.round(x))<0.005)?eur0.format(x):eur2.format(x);}
function monthName(offset){var d=new Date();d.setDate(1);d.setMonth(d.getMonth()+Math.round(offset));return MON[d.getMonth()]+' '+d.getFullYear();}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
var WA='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3a9 9 0 0 0-7.8 13.5L3 21l4.6-1.2A9 9 0 1 0 12 3z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>';
/* Teilen: Text + Link zur Rechnerseite. Persönliche Zahlen teilt nur, wer klickt. */
function share(el,text,path){
  var url=BASE+path+'?ref=wa';
  var full=text+'\n\nRechne es selbst nach (kostenlos): '+url;
  el.innerHTML='<a class="btn pri" target="_blank" rel="noopener" href="https://wa.me/?text='+encodeURIComponent(full)+'">'+WA+'Per WhatsApp teilen</a>'+
    '<button class="btn" type="button" data-copy>Link kopieren</button>';
  el.querySelector('[data-copy]').onclick=function(){var b=this,u=BASE+path;(navigator.clipboard?navigator.clipboard.writeText(u):Promise.reject()).then(function(){b.textContent='Kopiert ✓';},function(){prompt('Link kopieren:',u);});};
}
function bind(ids,fn){ids.forEach(function(id){var e=$(id);if(e){e.addEventListener('input',fn);e.addEventListener('change',fn);}});fn();}
if('serviceWorker' in navigator){window.addEventListener('load',function(){navigator.serviceWorker.register('/sw.js').catch(function(){});});}
window.GKR={num:num,$:$,val:val,E:E,nf1:nf1,nf0:nf0,monthName:monthName,esc:esc,share:share,bind:bind,BASE:BASE};
})();
