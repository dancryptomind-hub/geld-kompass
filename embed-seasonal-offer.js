(function () {
  'use strict';
  var box = document.getElementById('gk-seasonal-offer');
  if (!box) return;
  function berlinDay(now) {
    var parts = new Intl.DateTimeFormat('en-CA', { timeZone: 'Europe/Berlin', year: 'numeric', month: '2-digit', day: '2-digit' }).formatToParts(now);
    var values = {};
    parts.forEach(function (part) { values[part.type] = part.value; });
    return values.year + values.month + values.day;
  }
  function refresh() {
    var day;
    try { day = berlinDay(new Date()); } catch (e) { box.hidden = true; return; }
    var black = day >= '20261127' && day <= '20261207';
    var christmas = day >= '20261220' && day <= '20270101';
    if (!black && !christmas) { box.hidden = true; box.replaceChildren(); return; }
    var english = document.documentElement.lang === 'en';
    var label = black ? (english ? 'Black Friday offer' : 'Black-Friday-Angebot') : (english ? 'Christmas special' : 'Weihnachts-Special');
    var date = black ? (english ? '7 December 2026' : '7. Dezember 2026') : (english ? '1 January 2027' : '1. Januar 2027');
    var lead = document.createElement('b');
    lead.textContent = label + ': ';
    var text = document.createTextNode(english
      ? 'Professional for €39 per month for the first 12 months (€468 total). Available through ' + date + ', 23:59 Berlin time. Afterwards the standard price currently shown is €79 per month; renewal terms and applicable taxes are confirmed in your quote. EUR offer.'
      : 'Professional für 39 € pro Monat in den ersten 12 Monaten (insgesamt 468 €). Gültig bis ' + date + ', 23:59 Uhr Berliner Zeit. Danach beträgt der aktuell ausgewiesene Standardpreis 79 € pro Monat; Verlängerungsbedingungen und anwendbare Steuern werden im Angebot bestätigt. Angebot in EUR.');
    var link = document.createElement('a');
    link.textContent = english ? ' Enquire about the offer' : ' Angebot anfragen';
    link.href = 'mailto:kontakt@geld-kompass.com?subject=' + encodeURIComponent(label + ' Professional') + '&body=' + encodeURIComponent(english ? 'Company:\nWebsite(s):\nPreferred currency:\n' : 'Unternehmen:\nWebsite(s):\nWunschwährung:\n');
    box.replaceChildren(lead, text, link);
    box.hidden = false;
  }
  refresh();
  setInterval(refresh, 60000);
})();
