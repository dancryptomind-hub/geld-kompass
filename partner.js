/* Partner-Links und E-Mail-Liste des Geld-Kompass.
   Solange ein Eintrag null ist, wird an dieser Stelle NICHTS angezeigt.
   Eintragen, sobald Impressum steht und das Partnerprogramm bestätigt ist, z. B.:
   broker: {url:'https://…', name:'Name', de:'Text deutsch', en:'English text'}
   newsletter: {action:'https://…/subscribe', field:'EMAIL'}   (Formular-Adresse des E-Mail-Anbieters)
   Plätze auf den Seiten: <div data-partner="broker"></div> usw. */
window.GK_PARTNER = {
  broker: null,      /* App: Sparplan-Rechner („Sparplan anlegen“) */
  fx: null,          /* Währungsrechner (App und Rechnerseiten): Geld ins Ausland senden */
  kredit: null,      /* App: „Umschulden prüfen“ */
  newsletter: null   /* App „Zum Buch“ und Rechnerseiten: Arbeitsbuch-PDF gegen E-Mail */
};
(function(){
  var P=window.GK_PARTNER;
  function en(){return (document.documentElement.lang||'de').slice(0,2)==='en';}
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function render(root){(root||document).querySelectorAll('[data-partner]').forEach(function(box){var k=box.getAttribute('data-partner'),c=P[k];if(!c){box.innerHTML='';box.hidden=true;return;}box.hidden=false;
    if(k==='newsletter'){box.innerHTML='<form class="gk-news" action="'+esc(c.action)+'" method="post" target="_blank"><b>'+(en()?'Free workbook pages (German) + monthly money check by email':'Kostenlose Arbeitsbuch-Seiten + monatlicher Geld-Check per E-Mail')+'</b><div class="gk-news-row"><input type="email" name="'+esc(c.field||'EMAIL')+'" required placeholder="'+(en()?'Your email':'Deine E-Mail')+'" autocomplete="email"><button type="submit">'+(en()?'Sign up':'Eintragen')+'</button></div><small>'+(en()?'No spam, unsubscribe any time. See our':'Kein Spam, jederzeit abmeldbar. Mehr in der')+' <a href="/datenschutz/">'+(en()?'privacy notice':'Datenschutzerklärung')+'</a>.</small></form>';return;}
    box.innerHTML='<div class="gk-partner"><span class="gk-ad">'+(en()?'Partner link':'Partner-Link')+'</span><p>'+esc(en()?(c.en||c.de):c.de)+'</p><a href="'+esc(c.url)+'" target="_blank" rel="noopener sponsored">'+esc(c.name)+' →</a><small>'+(en()?'We may earn a commission. The price stays the same for you. Not investment advice.':'Wir erhalten ggf. eine Provision, für dich ändert sich der Preis nicht. Keine Anlageberatung.')+'</small></div>';});}
  window.GK_partnerRender=render;
  var css=document.createElement('style');css.textContent='.gk-partner,.gk-news{border:1px dashed rgba(227,181,90,.45);border-radius:12px;padding:12px 14px;margin-top:12px;display:flex;flex-direction:column;gap:6px;font-size:.9rem}.gk-ad{font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;color:#e3b55a;font-weight:700}.gk-partner p{margin:0}.gk-partner a{color:#e3b55a;font-weight:700}.gk-partner small,.gk-news small{opacity:.7;font-size:.75rem}.gk-news-row{display:flex;gap:8px;flex-wrap:wrap}.gk-news input{flex:1 1 200px;padding:9px 11px;border-radius:9px;border:1px solid rgba(128,128,128,.4);background:transparent;color:inherit}.gk-news button{padding:9px 14px;border-radius:9px;border:0;background:#e3b55a;color:#1b1407;font-weight:800}';
  document.head.appendChild(css);
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){render();});else render();
})();
