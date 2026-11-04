/* Geld-Kompass Pro: Rechner zum Einbetten. Passt die Höhe eingebetteter Rechner automatisch an. */
(function(){if(window.__gkEmbed)return;window.__gkEmbed=1;
window.addEventListener('message',function(e){if(!/^https:\/\/(www\.)?geld-kompass\.com$/.test(e.origin)&&e.origin!==location.origin)return;var d=e.data;if(!d||d.gk!=='h'||!(d.h>100))return;
  var f=document.querySelectorAll('iframe[data-gk]');for(var i=0;i<f.length;i++){if(f[i].contentWindow===e.source){f[i].style.height=Math.min(4000,d.h)+'px';break;}}});})();
