/* Auf Anforderung sichtbar; zieht sich bei Nichtbenutzung an den Rand zurück. */
(function(){'use strict';
var idle=null,enter=null,leave=null,root=null,IDLE=12000;
function manual(){try{return localStorage.getItem('gk-guide-hidden')==='1';}catch(e){return false;}}
function busy(){return !!document.querySelector('#gkTour.on')||!!(root&&root.classList.contains('dragging'))||!!(root&&root.contains(document.activeElement)&&document.activeElement.matches(':focus-visible'))||!!(root&&root.querySelector('.gg-menu:not([hidden])'));}
function rest(){clearTimeout(idle);if(!root||manual())return;if(busy()){schedule();return;}root.classList.remove('gg-entering');root.classList.add('gg-leaving');clearTimeout(leave);leave=setTimeout(function(){root.classList.remove('gg-leaving');root.classList.add('gg-resting');},400);var b=root.querySelector('#gkGuideBtn');if(b)b.setAttribute('aria-expanded','false');}
function schedule(){clearTimeout(idle);if(!root||manual()||root.classList.contains('gg-resting'))return;idle=setTimeout(rest,IDLE);}
function wake(){if(!root)return;clearTimeout(leave);root.classList.remove('gg-resting','gg-leaving');if(!manual()){root.classList.remove('gg-entering');void root.offsetWidth;root.classList.add('gg-entering');clearTimeout(enter);enter=setTimeout(function(){root.classList.remove('gg-entering');},700);schedule();}}
function init(){root=document.getElementById('gkGuide');if(!root)return;root.dataset.guidePresence='ready';wake();root.addEventListener('pointerdown',schedule);root.addEventListener('pointerleave',schedule);root.addEventListener('focusout',schedule);document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!document.querySelector('#gkTour.on')&&(root.querySelector('.gg-menu:not([hidden])')||root.contains(document.activeElement))){var m=root.querySelector('.gg-menu');if(m)m.hidden=true;document.dispatchEvent(new Event('gk:guide-close'));var b=root.querySelector('#gkGuideBtn');if(b)b.setAttribute('aria-expanded','false');var active=document.activeElement;if(active&&root.contains(active))active.blur();rest();}});
 document.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('[data-gt]');if(!b)return;var a=b.getAttribute('data-gt');if(a==='show')wake();else if(a==='hide')clearTimeout(idle);else schedule();});
 document.addEventListener('visibilitychange',function(){if(document.hidden)clearTimeout(idle);else schedule();});
 new MutationObserver(function(){schedule();}).observe(root,{childList:true});
 window.GKGuidePresence={wake:wake,rest:rest};}
window.addEventListener('load',function(){setTimeout(init,0);});
})();
