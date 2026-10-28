/* Eurostat HICP: annual change of the all-items index, ECOICOP v2. No key required. */
(function(root,factory){var api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.GeldInflation=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 var base='https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/prc_hicp_minr';
 function url(geo){return base+'?lang=DE&freq=M&unit=RCH_A&coicop18=TOTAL&geo='+encodeURIComponent(geo)+'&lastTimePeriod=12';}
 function parse(data,geo,checked){
  if(!data||!Array.isArray(data.id)||!Array.isArray(data.size)||!data.dimension||!data.value)throw new Error('Ungültige Eurostat-Antwort');
  var dims=data.id,sizes=data.size,select={freq:'M',unit:'RCH_A',coicop18:'TOTAL',geo:geo};
  if(!dims.includes('time')||!dims.includes('coicop18'))throw new Error('Falsche Datenreihe');
  function position(dim,key){var c=data.dimension[dim],idx=c&&c.category&&c.category.index;
   if(!idx||(Array.isArray(idx)?idx.indexOf(key)<0:!Object.prototype.hasOwnProperty.call(idx,key)))throw new Error('Fehlender Filter '+dim+': '+key);
   return Array.isArray(idx)?idx.indexOf(key):idx[key];}
  Object.keys(select).forEach(function(dim){if(!dims.includes(dim))throw new Error('Fehlende Dimension '+dim);position(dim,select[dim]);});
  var times=data.dimension.time.category.index,periods=Array.isArray(times)?times:Object.keys(times),best=null;
  periods.sort().forEach(function(period){
   if(!/^\d{4}-(0[1-9]|1[0-2])$/.test(period)||period>new Date(checked||Date.now()).toISOString().slice(0,7))return;
   var offset=0;
   dims.forEach(function(dim,i){var pos=dim==='time'?position(dim,period):select[dim]!=null?position(dim,select[dim]):sizes[i]===1?0:null;
    if(pos==null)throw new Error('Mehrdeutige Datenreihe '+dim);offset=offset*sizes[i]+pos;});
   var value=data.value[offset];
   if(typeof value==='number'&&Number.isFinite(value))best={rate:value,period:period,source:'Eurostat · HVPI',series:'prc_hicp_minr',unit:'Veränderung zum Vorjahresmonat in %',checked:checked||new Date().toISOString(),sourceUpdated:data.updated||null,url:url(geo),status:data.status&&data.status[offset]||null};
  });
  if(!best)throw new Error('Keine gültige Beobachtung');return best;
 }
 function choose(current,candidate){if(!candidate)return current;if(!current||candidate.period>=current.period)return candidate;return current;}
 function ageMonths(period,now){var d=new Date(now||Date.now());return d.getUTCFullYear()*12+d.getUTCMonth()-(Number(period.slice(0,4))*12+Number(period.slice(5,7))-1);}
 return {url:url,parse:parse,choose:choose,ageMonths:ageMonths};
});
