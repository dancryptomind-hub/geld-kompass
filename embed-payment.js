(function () {
  'use strict';
  var en = document.documentElement.lang === 'en', interval = 'yr';
  var offer = document.getElementById('gk-seasonal-offer');
  if (!offer) return;
  function campaign(now) {
    var values = {};
    new Intl.DateTimeFormat('en-CA', {timeZone:'Europe/Berlin',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(now).forEach(function(p){values[p.type]=p.value;});
    var day=values.year+values.month+values.day;
    return day >= '20261127' && day <= '20261207' ? 'black' : day >= '20261220' && day <= '20270101' ? 'christmas' : '';
  }
  function render() {
    var active='';
    try { active=campaign(new Date()); } catch(e) { /* Fail closed. */ }
    offer.hidden=!active;
    if (active) {
      document.getElementById('ebOfferTitle').textContent=active==='black' ? (en?'Black Friday offer':'Black-Friday-Angebot') : (en?'Christmas offer':'Weihnachtsangebot');
      var end=active==='black' ? (en?'7 December 2026':'7. Dezember 2026') : (en?'1 January 2027':'1. Januar 2027');
      document.getElementById('ebOfferTerms').textContent=en ? 'Professional: 39 EUR per month for the first 12 months (468 EUR total), or 468 EUR paid once upfront. Available through '+end+', 23:59 Berlin time. Afterwards the current standard price is 79 EUR/month; renewal terms are confirmed in your quote. Offer eligibility is checked before payment.' : 'Professional: 39 EUR pro Monat für die ersten 12 Monate (insgesamt 468 EUR) oder einmalig 468 EUR vorauszahlen. Gültig bis '+end+', 23:59 Uhr Berliner Zeit. Danach aktuell 79 EUR/Monat; Verlängerungsbedingungen werden im Angebot bestätigt. Die Angebotsberechtigung wird vor Zahlung geprüft.';
    }
    document.querySelectorAll('[data-ebbill]').forEach(function(b){b.setAttribute('aria-pressed',String(b.dataset.ebbill===interval));});
    document.querySelectorAll('[data-price-mo]').forEach(function(el){el.textContent=el.getAttribute('data-price-'+interval);});
    document.querySelectorAll('[data-period]').forEach(function(el){el.textContent=interval==='yr'?(en?'One payment for 12 months':'Einmalig für 12 Monate'):(en?'Per month · manually recurring payment':'Pro Monat · selbst wiederkehrend zahlen');});
    document.querySelectorAll('[data-wise]').forEach(function(a){
      var allowed=(a.dataset.wise!=='offer'||!!active)&&(a.dataset.wise!=='agency'||document.getElementById('ebAgencyConsent').checked);
      a.textContent=a.getAttribute('data-label-'+interval);
      a.setAttribute('aria-disabled',String(!allowed));
      if(allowed)a.href=a.getAttribute('data-link-'+interval);else a.removeAttribute('href');
    });
  }
  document.querySelectorAll('[data-ebbill]').forEach(function(b){b.addEventListener('click',function(){interval=b.dataset.ebbill;render();});});
  document.getElementById('ebAgencyConsent').addEventListener('change',render);
  // Recheck expiry even when a page has been left open or restored from browser history.
  document.querySelectorAll('[data-wise]').forEach(function(a){a.addEventListener('click',function(e){render();if(!a.hasAttribute('href'))e.preventDefault();});});
  window.addEventListener('pageshow',render);document.addEventListener('visibilitychange',render);
  render();setInterval(render,30000);
})();
