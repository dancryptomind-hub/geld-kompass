/* Versionierte Rechnerwerte im Linkfragment; keine vollständigen Tracker-Daten. */
(function(){'use strict';
function read(){try{var raw=new URLSearchParams(location.hash.slice(1)).get('gk');if(!raw||raw.length>50000)return null;var d=JSON.parse(raw);return d&&d.v===1&&d.values&&typeof d.values==='object'&&!Array.isArray(d.values)?d:null;}catch(e){return null;}}
function link(path,data,lang,ref){var u=new URL(path,'https://geld-kompass.com/');u.searchParams.set('lang',lang);if(ref)u.searchParams.set('ref',ref);if(data){var d={v:1,values:data.values||{},currency:data.currency||'',kind:data.kind||'form'};var h=u.hash.slice(1);u.hash=(h?h+'&':'')+'gk='+encodeURIComponent(JSON.stringify(d));}return u.href;}
function number(x,min,max){return typeof x==='number'&&Number.isFinite(x)&&x>=min&&x<=max;}
function app(d){if(!d||!['wi','inflation'].includes(d.kind)||!/^[A-Z]{3}$/.test(d.currency))return null;var v=d.values;
 if(d.kind==='wi'){if(typeof v.title!=='string'||v.title.length>200||!number(v.amt,0,1e12)||!['day','week','month'].includes(v.per)||!number(v.years,1,40)||typeof v.symbol!=='string'||v.symbol.length>40||!number(v.rate,-100,100)||!number(v.worldRate,-100,100))return null;}
 if(d.kind==='inflation'&&!number(v.rate,-99,100))return null;
 return d;}
window.GKShareState={read:read,link:link,app:app};
})();
