#!/usr/bin/env python3
"""Baut die Seiten zum Einbinden der Rechner: /einbinden/ (DE) und /en/embed/ (EN).
Website-Betreiber wählen Rechner, Sprache und Währung, sehen eine Live-Vorschau und kopieren den iframe-Code."""
import json, os
BASE = 'https://geld-kompass.com/'
LOGO = '<img class="gk-logo" src="/icons/logo-badge.webp?v=3" alt="" aria-hidden="true" width="34" height="34">'
# (DE-Pfad, DE-Name, EN-Pfad, EN-Name, Starthöhe)
CALC = [
    ('sparplan-rechner', 'Sparplan-Rechner', 'savings-plan-calculator', 'Savings plan calculator', 860),
    ('notgroschen-rechner', 'Notgroschen-Rechner', 'emergency-fund-calculator', 'Emergency fund calculator', 700),
    ('freiheitstage-rechner', 'Freiheitstage-Rechner', 'freedom-days-calculator', 'Freedom days calculator', 700),
    ('schuldenfrei-rechner', 'Schuldenfrei-Rechner', 'debt-free-calculator', 'Debt-free calculator', 820),
    ('schneeball-lawine-rechner', 'Schneeball oder Lawine?', 'debt-snowball-avalanche-calculator', 'Snowball or avalanche?', 900),
    ('vier-prozent-regel-rechner', '4-Prozent-Regel-Rechner', '4-percent-rule-calculator', '4 percent rule calculator', 760),
    ('kreditkarten-rechner', 'Kreditkarten-Rechner', 'credit-card-payoff-calculator', 'Credit card payoff calculator', 760),
    ('inflationsrechner', 'Inflationsrechner', 'inflation-calculator', 'Inflation calculator', 700),
    ('abo-als-aktie', 'Konsument oder Eigentümer?', 'subscription-as-investment', 'Consumer or owner?', 760),
    ('waehrungsrechner', 'Währungsrechner', 'currency-converter', 'Currency converter', 640),
    ('steuern-nach-wohnsitz', 'Steuern nach Wohnsitz', 'taxes-by-residence', 'Taxes by residence', 980),
]
T = {
 'de': dict(title='Finanzrechner kostenlos oder White-Label auf deiner Website einbinden | Geld-Kompass Pro',
   desc='Binde 11 fertige Finanzrechner (Sparplan, Schulden, Steuern in 91 Ländern, Währung) in 2 Minuten ein: kostenlos mit Hinweis oder als White-Label im eigenen Branding ab 39 €/Monat.',
   eb='Für Finanzblogs, Berater, Kanzleien & Verlage', h1='Verwandle stille Blog-Leser in begeisterte Leads – in 2 Minuten live.',
   lead='Agentur-Eigenentwicklung kostet 3.500–15.000 €. Baukästen haben keine fertige deutsche Finanz- und Steuerlogik. Binde unsere 11 geprüften Finanzrechner sofort per HTML-Schnipsel ein: kostenlos mit Hinweis – oder komplett im eigenen Branding ab 1,28 € am Tag.',
   calc='Rechner', lang='Sprache', cur='Währung', copy='Code kopieren', copied='Kopiert ✓', code='Dein Einbettungscode', prev='Live-Vorschau',
   how='In 3 Schritten auf deiner Website', steps=['Rechner, Sprache, Währung und Farben wählen.', 'Code kopieren und als HTML-Block in deine Seite einfügen (WordPress, Webflow, Wix, Jimdo, HTML).', 'Fertig. Die Höhe passt sich auf Desktop & Handy automatisch an – null Wartung, null Cookies.'],
   faq=[('Wie viel spart mir das gegenüber Eigenentwicklung oder US-Baukästen?', 'Eine individuelle Programmierung von 11 Rechnern mit EZB-Devisen, Eurostat-Inflation und 91-Länder-Steuerdaten kostet bei Agenturen schnell 3.500–15.000 € plus Wartung. Allgemeine Funnel-Baukästen kosten 49–600 €/Monat für Branding-Entfernung ohne fertige Finanzmathematik. Mit White-Label Pro startest du schlüsselfertig ab 39 €/Monat (jährlich) bzw. 1,28 € pro Tag.'),
        ('Kostet die Basis-Einbindung wirklich 0 €?', 'Ja. Die Standard-Version ist dauerhaft kostenlos. Unter dem Rechner bleibt ein dezenter Hinweis „Bereitgestellt von Geld-Kompass Pro“ sichtbar.'),
        ('Geht das problemlos in WordPress, Webflow, Wix oder HTML?', 'Ja. Du kopierst genau zwei Zeilen HTML (Block „Individuelles HTML“), fertig. Es werden keine Cookies gesetzt und keine Besucherdaten an Dritte übertragen – ideal für strenge DSGVO-Anforderungen.'),
        ('Was passiert bei neuen Kursen, Steuersätzen oder Zinsen?', 'In allen Tarifen laufen die Daten-Updates im Hintergrund automatisch weiter. Du hast null Wartungsaufwand.'),
        ('Kann ich White-Label erst risikofrei auf meiner Domain testen?', 'Ja. Schreib uns kurz deine Domain und Markenfarbe – du bekommst vorab deine persönliche White-Label-Testvorschau, bevor die Lizenz startet. Monatliche Tarife sind jederzeit kündbar.')],
   faqh='Häufige Fragen & Einwände geklärt', home='/', app='Zum Geld-Kompass Pro', appurl='/app/', sw='English', swurl='/en/embed/?lang=en', all='Alle Rechner', allurl='/rechner/',
   logo='Geld-<span>Kompass</span> <span class="pro">Pro</span>',
   foot='<a href="/impressum/">Impressum</a> · <a href="/datenschutz/">Datenschutz</a> · Geld-Kompass Pro · © FreedomByDan · Allgemeine Finanzbildung, keine Anlage-, Steuer- oder Rechtsberatung.'),
 'en': dict(title='Embed free or white-label finance calculators on your site | Money Compass Pro',
   desc='Embed 11 ready-made finance calculators (compound interest, debt payoff, 91-country tax compare, FX) in 2 minutes: free with attribution or clean white-label from €39/month.',
   eb='For finance blogs, advisers, agencies & publishers', h1='Turn passive readers into qualified leads — live in 2 minutes.',
   lead='Custom agency calculators cost $3,500–$15,000+. Generic builders charge $49–$600/month to remove branding and still ship empty formulas. Embed 11 battle-tested finance & tax calculators with one snippet: free with credit, or 100% in your own brand from €1.28 a day.',
   calc='Calculator', lang='Language', cur='Currency', copy='Copy code', copied='Copied ✓', code='Your embed code', prev='Live preview',
   how='Live on your site in 3 steps', steps=['Pick calculator, language, currency and theme.', 'Copy the code and paste it into a Custom HTML block (WordPress, Webflow, Ghost, Squarespace).', 'Done. Responsive height adjusts automatically on mobile & desktop — zero maintenance, zero cookies.'],
   faq=[('How does the price compare to custom dev or generic SaaS builders?', 'Custom building 11 calculators with ECB exchange feeds, official inflation data and 91-country tax profiles easily costs $3,500–$15,000+ upfront. General SaaS builders (Outgrow Business, involve.me Grow) cost $49–$600+/mo just to hide their logo while leaving the maths up to you. White-Label Pro starts at €39/mo (billed annually, ~€1.28/day) completely turnkey.'),
        ('Is the standard embed really free?', 'Yes. Free forever for websites, blogs and schools as long as the small “Powered by Geld-Kompass Pro” link remains visible.'),
        ('Does it work in WordPress, Webflow, Ghost or custom HTML?', 'Yes. Paste the two-line snippet anywhere. Zero tracking cookies and zero personal data leaves the visitor’s browser — clean for GDPR compliance.'),
        ('Who maintains exchange rates, inflation and tax tables?', 'All updates happen automatically in the background across every tier. Zero developer hours needed on your side.'),
        ('Can I preview White-Label with my brand before paying?', 'Yes. Send your website URL and brand colour and receive a custom live preview before your subscription starts. Monthly plans can be cancelled anytime.')],
   faqh='Frequently asked questions', home='/?lang=en', app='Open the Money Compass Pro', appurl='/app/?lang=en', sw='Deutsch', swurl='/einbinden/?lang=de', all='All calculators', allurl='/en/calculators/',
   logo='Money <span>Compass</span> <span class="pro">Pro</span>',
   foot='<a href="/impressum/?lang=en">Legal notice</a> · <a href="/datenschutz/?lang=en">Privacy</a> · Money Compass Pro · © FreedomByDan · General financial education, not investment, tax or legal advice.'),
}
CSS = """.eb-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.4fr);gap:18px;align-items:start}
@media(max-width:820px){.eb-grid{grid-template-columns:1fr}}
.eb-form label{display:block;margin:0 0 12px;font-weight:600}
.eb-form select{display:block;width:100%;margin-top:6px;padding:10px 12px;border-radius:10px;border:1px solid var(--line);background:var(--card2);color:var(--ink);font:inherit;font-size:16px}
.eb-form select option{background:var(--card);color:var(--ink)}.eb-form select:focus,.eb-code:focus{outline:2px solid var(--gold);outline-offset:1px}
.eb-code{width:100%;min-height:150px;font:12.5px/1.5 ui-monospace,Menlo,Consolas,monospace;padding:12px;border-radius:10px;border:1px solid var(--line);background:var(--card2);color:var(--ink);resize:vertical;box-sizing:border-box}
.eb-btn{margin-top:10px;width:100%;padding:12px 16px;border:0;border-radius:12px;background:linear-gradient(135deg,#f0c56a,#c99227);color:#1a1405;font-weight:800;font-size:1rem;cursor:pointer}
.eb-prev{border:1px dashed var(--line);border-radius:14px;padding:10px;background:var(--bg)}
.eb-prev iframe{display:block;width:100%;border:0;min-height:400px;border-radius:10px}
.eb-steps{counter-reset:s;list-style:none;padding:0}.eb-steps li{counter-increment:s;padding:6px 0 6px 38px;position:relative}
.eb-steps li:before{content:counter(s);position:absolute;left:0;top:4px;width:26px;height:26px;border-radius:50%;background:#c99227;color:#1a1405;font-weight:800;display:grid;place-items:center;font-size:.85rem}
.eb-lic{margin-top:14px;padding:14px 16px;border-radius:14px;border:1px solid rgba(227,181,90,.45);background:linear-gradient(135deg,rgba(227,181,90,.12),rgba(227,181,90,.03))}
.eb-tiers{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(220px,100%),1fr));gap:14px;margin:16px 0 22px}.eb-tiers>div{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:18px;display:flex;flex-direction:column}.eb-tiers>div.eb-tier-pro{border:2px solid var(--gold);background:linear-gradient(135deg,rgba(227,181,90,.16),rgba(227,181,90,.03));box-shadow:0 18px 40px -22px rgba(227,181,90,.35)}.eb-tiers h3{margin:0 0 6px;font-size:1.1rem;color:var(--gold);display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap}.eb-badge{font-size:.7rem;text-transform:uppercase;letter-spacing:.06em;padding:3px 9px;border-radius:999px;background:var(--gold);color:#1a1405;font-weight:800}.eb-price{margin:6px 0 4px;font-family:Playfair,Georgia,serif;font-size:2rem;line-height:1.15;color:var(--ink);font-variant-numeric:tabular-nums}.eb-price small{font-family:inherit;font-size:.9rem;color:var(--muted);font-weight:500}.eb-subprice{font-size:.82rem;color:var(--muted);margin:0 0 10px;min-height:1.4em}.eb-tiers ul{margin:8px 0 16px;padding-left:18px;color:var(--muted);font-size:.9rem;flex:1}.eb-tiers li{margin-bottom:5px}.eb-cta{display:inline-block;text-align:center;padding:11px 14px;border-radius:10px;font-weight:800;text-decoration:none;border:1px solid var(--gold);color:var(--gold)}.eb-tiers>div.eb-tier-pro .eb-cta{background:linear-gradient(135deg,#f0c56a,#c99227);color:#1a1405;border-color:transparent}.eb-bill{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:10px 0 6px}.eb-bill button{border:1px solid var(--line);background:var(--card2);color:var(--muted);border-radius:999px;padding:7px 14px;font:inherit;font-size:.85rem;font-weight:700;cursor:pointer}.eb-bill button[aria-pressed=true]{border-color:var(--gold);color:#1a1405;background:var(--gold)}.eb-save{font-size:.8rem;color:#5bc7a0;font-weight:700}.eb-anchor{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(210px,100%),1fr));gap:10px;margin:12px 0 16px}.eb-anchor div{border:1px solid var(--line);border-radius:12px;padding:12px 14px;background:var(--card2);font-size:.86rem}.eb-anchor b{display:block;color:var(--ink);margin-bottom:3px}.eb-anchor span{color:var(--muted)}.eb-anchor div.best{border-color:rgba(91,199,160,.55)}.eb-anchor div.best b{color:#5bc7a0}.eb-risk{border-left:3px solid #5bc7a0;background:var(--card2);border-radius:0 12px 12px 0;padding:12px 16px;margin:12px 0 22px;font-size:.9rem}.eb-copyrow{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-top:8px}.eb-copyinq{border:1px dashed var(--line);background:transparent;color:var(--gold);border-radius:9px;padding:7px 12px;font:inherit;font-size:.82rem;font-weight:700;cursor:pointer}
.eb-mode{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 10px}.eb-mode button{border:1px solid var(--line);background:var(--card2);color:var(--muted);border-radius:999px;padding:6px 12px;font:inherit;font-size:.82rem;font-weight:700;cursor:pointer}.eb-mode button[aria-pressed=true]{border-color:var(--gold);color:var(--gold);background:rgba(227,181,90,.1)}.eb-wl{display:none;align-items:center;justify-content:space-between;gap:10px;padding:10px 12px;border-radius:10px;margin-bottom:8px;background:linear-gradient(135deg,#1d4ed8,#0f766e);color:#fff;font-size:.85rem}.eb-prev.wl .eb-wl{display:flex}.eb-prev.wl{border-style:solid;border-color:rgba(56,189,248,.45)}.eb-prev.wl .eb-framebox{overflow:hidden;border-radius:10px}.eb-prev.wl iframe{margin-bottom:-46px}"""

CSS += """
/* Keep tariff cards independent of the global .pro logo badge. */
.eb-tiers{grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.eb-tiers>div{min-width:0;border-width:2px;padding:18px;display:grid;grid-template-rows:subgrid;grid-row:span 5;row-gap:10px}
.eb-tiers>div.eb-tier-pro{background:linear-gradient(135deg,rgba(227,181,90,.16),rgba(227,181,90,.03));color:var(--ink)}
.eb-tiers h3{margin:0;align-content:start;align-items:start;line-height:1.4}
.eb-price,.eb-subprice{margin:0}
.eb-tiers ul{margin:0;padding-left:18px;line-height:1.55}
.eb-tiers .eb-cta{align-self:stretch;display:flex;align-items:center;justify-content:center;min-height:66px;line-height:1.35;overflow-wrap:anywhere}
.eb-anchor{grid-template-columns:repeat(3,minmax(0,1fr));align-items:stretch}
.eb-anchor>div{min-width:0;display:grid;grid-template-rows:subgrid;grid-row:span 2;row-gap:6px}
.eb-anchor b{margin:0}
.eb-grid>div{min-width:0}
.eb-cta:focus-visible,.eb-bill button:focus-visible,.eb-mode button:focus-visible,.eb-btn:focus-visible,.eb-copyinq:focus-visible{outline:2px solid var(--ink);outline-offset:4px}
#ebPricing,#ebCode{scroll-margin-top:110px}
@media(max-width:700px){.eb-tiers,.eb-anchor{grid-template-columns:minmax(0,1fr)}.eb-tiers>div,.eb-anchor>div{grid-row:auto;grid-template-rows:none}.eb-tiers .eb-cta{min-height:48px}.eb-wl{flex-wrap:wrap}}
"""

def page(lang):
    t = T[lang]; en = lang == 'en'
    url = BASE + ('en/embed/' if en else 'einbinden/')
    opts = ''.join('<option value="%d">%s</option>' % (i, c[3] if en else c[1]) for i, c in enumerate(CALC))
    data = json.dumps([[c[0], c[1], c[2], c[3], c[4]] for c in CALC], ensure_ascii=False)
    lic = ('<div class="eb-lic"><b>Want zero attribution &amp; your own brand?</b><br>Remove the “Powered by” badge, match your brand colours and logo from <b>€39/mo</b> (yearly, ~€1.28/day). <a href="#ebPricing">Compare licence tiers ↓</a> · <a href="/en/calculators/">All 11 calculators</a></div>' if en else
           '<div class="eb-lic"><b>Ohne Hinweis &amp; komplett in deinem Branding?</b><br>Entferne den Hinweis-Banner und passe Farben &amp; Logo an – schlüsselfertig ab <b>39 €/Monat</b> (jährlich, ca. 1,28 €/Tag). <a href="#ebPricing">Pakete &amp; Preise ansehen ↓</a> · <a href="/rechner/">Alle 11 Rechner</a></div>')
    faq = ''.join('<details><summary>%s</summary><p>%s</p></details>' % q for q in t['faq'])
    ld = json.dumps({"@context": "https://schema.org", "@type": "WebPage", "name": t['h1'], "url": url, "inLanguage": lang, "description": t['desc']}, ensure_ascii=False)
    js = """(function(){var C=%s,L='%s';var $=function(i){return document.getElementById(i);};
 function code(){var c=C[+$('ebCalc').value],l=$('ebLang').value,cur=$('ebCur').value,path=l==='en'?'/en/calculators/'+c[2]+'/':'/rechner/'+c[0]+'/',name=l==='en'?c[3]:c[1];
  var th=$('ebTheme').value,qs='?embed=1'+(cur?'&cur='+cur:'')+(th?'&theme='+th:''),src='https://geld-kompass.com'+path+qs;
  $('ebCode').value='<iframe data-gk src="'+src+'" title="'+name+' · Geld-Kompass Pro" loading="lazy" style="width:100%%;max-width:760px;height:'+c[4]+'px;border:0;border-radius:12px"></iframe>\\n<script src="https://geld-kompass.com/embed.js" async></'+'script>';
  var f=$('ebFrame'),p=path+qs;if(f.getAttribute('src')!==p){f.style.height=c[4]+'px';f.setAttribute('src',p);}}
 ['ebCalc','ebLang','ebCur','ebTheme'].forEach(function(i){$(i).addEventListener('change',code);});
 $('ebCopy').addEventListener('click',function(){var t=$('ebCode'),b=this,done=function(){b.textContent='%s';setTimeout(function(){b.textContent='%s';},1800);};
  if(navigator.clipboard)navigator.clipboard.writeText(t.value).then(done,function(){t.select();document.execCommand('copy');done();});else{t.select();document.execCommand('copy');done();}});
 $('ebCode').addEventListener('focus',function(){this.select();});
 document.querySelectorAll('[data-ebmode]').forEach(function(b){b.addEventListener('click',function(){var wl=b.getAttribute('data-ebmode')==='wl';document.querySelectorAll('[data-ebmode]').forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false');});var box=$('ebPrevBox');if(box)box.classList.toggle('wl',wl);});});
 var bill='yr';document.querySelectorAll('[data-ebbill]').forEach(function(b){b.addEventListener('click',function(){bill=b.getAttribute('data-ebbill');document.querySelectorAll('[data-ebbill]').forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false');});document.querySelectorAll('[data-p-yr]').forEach(function(el){el.innerHTML=bill==='yr'?el.getAttribute('data-p-yr'):el.getAttribute('data-p-mo');});document.querySelectorAll('[data-s-yr]').forEach(function(el){el.textContent=bill==='yr'?el.getAttribute('data-s-yr'):el.getAttribute('data-s-mo');});document.querySelectorAll('[data-mail-yr]').forEach(function(a){a.href=bill==='yr'?a.getAttribute('data-mail-yr'):a.getAttribute('data-mail-mo');});});});
 document.querySelectorAll('[data-eb-inq]').forEach(function(b){b.addEventListener('click',function(){var txt=L==='en'?'Hello Dan,\\n\\nI would like to book the White-Label ('+(bill==='yr'?'€39/mo annual':'€49/mo monthly')+') / Team licence for my domain: [YOUR-DOMAIN.COM]\\nBrand accent colour: [#HEX]\\n\\nPlease send a live preview link.\\nBest regards':'Hallo Dan,\\n\\nich möchte gerne eine White-Label-Rechner-Lizenz ('+(bill==='yr'?'Pro 39 €/Monat jährlich':'Pro 49 €/Monat monatlich')+') für folgende Domain nutzen: [DEINE-DOMAIN.DE]\\nWunschfarbe: [#HEX]\\n\\nBitte schick mir vorab die persönliche Testvorschau.\\nViele Grüße';if(navigator.clipboard)navigator.clipboard.writeText(txt).then(function(){var old=b.textContent;b.textContent=L==='en'?'Copied inquiry text ✓':'Anfrage-Text kopiert ✓';setTimeout(function(){b.textContent=old;},2200);});});});
 code();})();""" % (data, lang, t['copied'], t['copy'])
    og_img = BASE + ('screens/desktop-en.webp' if en else 'screens/desktop-de.webp')
    tiers = (
        '<h2 id="ebPricing">B2B Licences &amp; Transparent Pricing</h2>'
        '<div class="eb-anchor">'
        '<div><b>Custom Agency Build</b><span>€3,500–€15,000+ upfront plus manual tax &amp; rate updates</span></div>'
        '<div><b>Generic SaaS Builders</b><span>$49–$600/month for branding removal with empty maths</span></div>'
        '<div class="best"><b>Money Compass White-Label</b><span>11 turnkey finance &amp; tax calculators from €39/mo (~€1.28/day)</span></div>'
        '</div>'
        '<div class="eb-bill" role="group" aria-label="Billing interval">'
        '<button type="button" data-ebbill="yr" aria-pressed="true">Annual billing (save 20%)</button>'
        '<button type="button" data-ebbill="mo" aria-pressed="false">Monthly billing</button>'
        '<span class="eb-save">Founding partner rate: locked for the first 25 websites</span>'
        '</div>'
        '<div class="eb-tiers">'
        '<div><h3>Free Embed</h3><div class="eb-price">€0 <small>/ forever</small></div><p class="eb-subprice">Ideal for testing and personal blogs</p><ul><li>All 11 calculators immediately (DE &amp; EN)</li><li>Automatic height &amp; 320px mobile layout</li><li>Zero tracking cookies · GDPR-clean</li><li>Small “Powered by Geld-Kompass Pro” credit</li></ul><a class="eb-cta" href="#ebCode">Copy code above ↑</a></div>'
        '<div class="eb-tier-pro"><h3>White-Label Pro <span class="eb-badge">Most Popular</span></h3><div class="eb-price" data-p-yr="€39 <small>/ mo</small>" data-p-mo="€49 <small>/ mo</small>">€39 <small>/ mo</small></div><p class="eb-subprice" data-s-yr="€468 billed yearly · only €1.28/day (save €120)" data-s-mo="Cancel monthly anytime · €49/mo">€468 billed yearly · only €1.28/day (save €120)</p><ul><li>Zero third-party badge — 100% your brand</li><li>Custom brand colours, font &amp; logo header</li><li>Up to 3 websites / client subdomains included</li><li>Automatic ECB FX, Eurostat HICP &amp; 91-country tax updates</li></ul><a class="eb-cta" href="mailto:kontakt@geld-kompass.com?subject=White-Label%20Pro%20(Annual%20€39/mo)&body=Domain:%20%0ABrand%20colour:" data-mail-yr="mailto:kontakt@geld-kompass.com?subject=White-Label%20Pro%20(Annual%20€39/mo)&body=Domain:%20%0ABrand%20colour:" data-mail-mo="mailto:kontakt@geld-kompass.com?subject=White-Label%20Pro%20(Monthly%20€49/mo)&body=Domain:%20%0ABrand%20colour:">Request preview &amp; activate →</a></div>'
        '<div><h3>Advisory Team &amp; Agency</h3><div class="eb-price" data-p-yr="€119 <small>/ mo</small>" data-p-mo="€149 <small>/ mo</small>">€119 <small>/ mo</small></div><p class="eb-subprice" data-s-yr="€1,428 billed yearly · unlimited sites" data-s-mo="Cancel monthly anytime · €149/mo">€1,428 billed yearly · unlimited sites</p><ul><li>Unlimited client domains &amp; adviser sub-pages</li><li>Custom CSS styling &amp; bespoke lead CTA links</li><li>1 custom calculator setup per year on request</li><li>Optional self-hosted ZIP bundle &amp; priority email support</li></ul><a class="eb-cta" href="mailto:kontakt@geld-kompass.com?subject=Team%20%26%20Agency%20Licence%20(Annual)&body=Domains:%20" data-mail-yr="mailto:kontakt@geld-kompass.com?subject=Team%20%26%20Agency%20Licence%20(Annual)&body=Domains:%20" data-mail-mo="mailto:kontakt@geld-kompass.com?subject=Team%20%26%20Agency%20Licence%20(Monthly)&body=Domains:%20">Request agency quote →</a></div>'
        '</div>'
        '<div class="eb-risk"><b>Zero-risk preview guarantee:</b> Receive a live White-Label preview tailored to your domain and brand colours before paying your first invoice. One new client or retainer pays back an entire year of White-Label Pro.<div class="eb-copyrow"><button type="button" class="eb-copyinq" data-eb-inq="1">Copy ready inquiry text for email/webmail</button><span>Send to <b>kontakt@geld-kompass.com</b></span></div></div>' if en else
        '<h2 id="ebPricing">Lizenz-Pakete &amp; transparente Preise</h2>'
        '<div class="eb-anchor">'
        '<div><b>Agentur-Eigenentwicklung</b><span>3.500–15.000 € einmalig plus laufende Wartung für Steuern &amp; Kurse</span></div>'
        '<div><b>Generische Baukästen (Outgrow &amp; Co.)</b><span>49–600 €/Monat nur für Logo-Entfernung ohne fertige Finanzmathematik</span></div>'
        '<div class="best"><b>Geld-Kompass White-Label</b><span>11 fertige Profi-Rechner inkl. Daten-Updates ab 39 €/Mo. (ca. 1,28 €/Tag)</span></div>'
        '</div>'
        '<div class="eb-bill" role="group" aria-label="Abrechnungszeitraum">'
        '<button type="button" data-ebbill="yr" aria-pressed="true">Jährlich zahlen (20 % sparen)</button>'
        '<button type="button" data-ebbill="mo" aria-pressed="false">Monatlich kündbar</button>'
        '<span class="eb-save">Gründungspartner-Vorteil: Einstiegspreis für die ersten 25 Websites gesichert</span>'
        '</div>'
        '<div class="eb-tiers">'
        '<div><h3>Kostenlos (Standard)</h3><div class="eb-price">0 € <small>/ dauerhaft</small></div><p class="eb-subprice">Ideal zum Testen &amp; für Einsteiger-Blogs</p><ul><li>Alle 11 Rechner sofort nutzbar (DE &amp; EN)</li><li>Automatische Höhe &amp; 320px-Handy-Layout</li><li>Null Cookies · ohne Banner DSGVO-sauber</li><li>Dezenter Hinweis „Bereitgestellt von Geld-Kompass Pro“</li></ul><a class="eb-cta" href="#ebCode">Code oben kopieren ↑</a></div>'
        '<div class="eb-tier-pro"><h3>White-Label Pro <span class="eb-badge">Empfohlen</span></h3><div class="eb-price" data-p-yr="39 € <small>/ Mo.</small>" data-p-mo="49 € <small>/ Mo.</small>">39 € <small>/ Mo.</small></div><p class="eb-subprice" data-s-yr="468 € jährlich · nur 1,28 €/Tag (120 € gespart)" data-s-mo="Monatlich jederzeit kündbar · 49 €/Monat">468 € jährlich · nur 1,28 €/Tag (120 € gespart)</p><ul><li>Ohne Hinweis-Banner – 100 % deine eigene Marke</li><li>Eigene Akzentfarben, Logo-Kopfzeile &amp; Schrift</li><li>Bis zu 3 Websites / Domains inklusive</li><li>Automatische EZB-Kurse, Eurostat-Inflation &amp; 91 Länder</li></ul><a class="eb-cta" href="mailto:kontakt@geld-kompass.com?subject=White-Label%20Pro%20Lizenz%20(39€/Mo%20jährlich)&body=Website/Domain:%20%0AMarkenfarbe:" data-mail-yr="mailto:kontakt@geld-kompass.com?subject=White-Label%20Pro%20Lizenz%20(39€/Mo%20jährlich)&body=Website/Domain:%20%0AMarkenfarbe:" data-mail-mo="mailto:kontakt@geld-kompass.com?subject=White-Label%20Pro%20Lizenz%20(49€/Mo%20monatlich)&body=Website/Domain:%20%0AMarkenfarbe:">Vorschau anfordern &amp; starten →</a></div>'
        '<div><h3>Kanzlei &amp; Teams</h3><div class="eb-price" data-p-yr="119 € <small>/ Mo.</small>" data-p-mo="149 € <small>/ Mo.</small>">119 € <small>/ Mo.</small></div><p class="eb-subprice" data-s-yr="1.428 € jährlich · unbegrenzte Domains" data-s-mo="Monatlich jederzeit kündbar · 149 €/Monat">1.428 € jährlich · unbegrenzte Domains</p><ul><li>Unbegrenzte Kunden-Domains &amp; Berater-Seiten</li><li>Eigenes CSS &amp; individuelle Lead-Ziel-Buttons</li><li>1 Wunschrechner / Parameter-Anpassung inklusive</li><li>Optionales Self-Hosting-Paket &amp; Prioritäts-Support</li></ul><a class="eb-cta" href="mailto:kontakt@geld-kompass.com?subject=Kanzlei-%20%26%20Team-Lizenz%20(jährlich)&body=Anzahl%20Domains:%20" data-mail-yr="mailto:kontakt@geld-kompass.com?subject=Kanzlei-%20%26%20Team-Lizenz%20(jährlich)&body=Anzahl%20Domains:%20" data-mail-mo="mailto:kontakt@geld-kompass.com?subject=Kanzlei-%20%26%20Team-Lizenz%20(monatlich)&body=Anzahl%20Domains:%20">Team-Angebot anfragen →</a></div>'
        '</div>'
        '<div class="eb-risk"><b>Risiko-Umkehr · erst testen, dann zahlen:</b> Du erhältst vor der ersten Rechnung eine persönliche Live-Testvorschau in deinen Farben für deine Domain. Schon ein einziger zusätzlicher Kundenauftrag oder Lead über deine Website bezahlt die gesamte Jahreslizenz mehrfach zurück.<div class="eb-copyrow"><button type="button" class="eb-copyinq" data-eb-inq="1">Fertigen Anfrage-Text kopieren (für Webmail / GMX / Gmail)</button><span>Senden an <b>kontakt@geld-kompass.com</b></span></div></div>'
    )
    return f"""<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<script>(function(){{var K='geld-kompass-lang',q=new URLSearchParams(location.search).get('lang'),w=q;if(q==='de'||q==='en'){{try{{localStorage.setItem(K,q);}}catch(e){{}}}}else{{try{{w=localStorage.getItem(K);}}catch(e){{}}}}if((w==='de'||w==='en')&&w!=='{lang}')location.replace('{'/einbinden/' if en else '/en/embed/'}'+location.search+location.hash);}})();</script>
<title>{t['title']}</title><meta name="description" content="{t['desc']}">
<link rel="canonical" href="{url}"><link rel="alternate" hreflang="de" href="{BASE}einbinden/"><link rel="alternate" hreflang="en" href="{BASE}en/embed/"><link rel="alternate" hreflang="x-default" href="{BASE}einbinden/">
<meta name="theme-color" content="#0E1730"><meta property="og:type" content="website"><meta property="og:title" content="{t['title']}"><meta property="og:description" content="{t['desc']}"><meta property="og:url" content="{url}"><meta property="og:image" content="{og_img}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{t['title']}"><meta name="twitter:description" content="{t['desc']}"><meta name="twitter:image" content="{og_img}">
<link rel="stylesheet" href="/rechner/rechner.css"><link rel="manifest" href="/manifest.webmanifest">
<link rel="icon" type="image/png" sizes="32x32" href="/icons/favicon-32.png?v=3"><link rel="apple-touch-icon" href="/icons/apple-touch-icon.png?v=3">
<script type="application/ld+json">{ld}</script>
<style>{CSS}</style>
<link rel=stylesheet href=/visuals.css?v20261104a><script src=/visuals.js?v20261104a></script></head><body data-page-lang="{lang}">
<header class="top"><div class="wrap"><a class="logo" href="{t['home']}">{LOGO}<b>{t['logo']}</b></a><nav><a href="{t['allurl']}">{t['all']}</a> · <a class="langsw" href="{t['swurl']}">{t['sw']}</a></nav></div></header>
<main class="wrap">
<div class="eyebrow">{t['eb']}</div>
<h1>{t['h1']}</h1>
<p class="lead">{t['lead']}</p>
<section class="card"><div class="eb-grid"><div class="eb-form">
<label>{t['calc']}<select id="ebCalc">{opts}</select></label>
<label>{t['lang']}<select id="ebLang"><option value="de"{'' if en else ' selected'}>Deutsch</option><option value="en"{' selected' if en else ''}>English</option></select></label>
<label>{t['cur']}<select id="ebCur"><option value="">{'Automatic' if en else 'Automatisch'}</option><option value="EUR"{'' if en else ' selected'}>EUR €</option><option value="USD"{' selected' if en else ''}>USD $</option><option value="GBP">GBP £</option><option value="CHF">CHF</option><option value="CAD">CAD</option><option value="AUD">AUD</option></select></label>
<label>{'Design' if en else 'Farben'}<select id="ebTheme"><option value="light" selected>{'Light (white websites)' if en else 'Hell (für helle Websites)'}</option><option value="dark">{'Dark' if en else 'Dunkel'}</option><option value="">{'Follow visitor setting' if en else 'Wie Gerät des Besuchers'}</option></select></label>
<label>{t['code']}<textarea id="ebCode" class="eb-code" readonly spellcheck="false"></textarea></label>
<button type="button" class="eb-btn" id="ebCopy">{t['copy']}</button>
{lic}
</div><div><h2 style="margin-top:0">{t['prev']}</h2><div class="eb-mode" role="group" aria-label="{'Preview style' if en else 'Vorschau-Ansicht'}"><button type="button" data-ebmode="std" aria-pressed="true">{'Free embed' if en else 'Kostenlos (Standard)'}</button><button type="button" data-ebmode="wl" aria-pressed="false">{'White-Label demo' if en else 'White-Label-Vorschau'}</button></div><div class="eb-prev" id="ebPrevBox"><div class="eb-wl"><b>{'Sample Advisory Ltd · Custom Brand' if en else 'Muster Finanzberatung · Dein Design'}</b><span>{'No badge · own colours' if en else 'Ohne Hinweis · eigene Farben'}</span></div><div class="eb-framebox"><iframe data-gk id="ebFrame" title="{t['prev']}"></iframe></div></div></div></div></section>
<h2>{t['how']}</h2><ol class="eb-steps">{''.join('<li>%s</li>' % s for s in t['steps'])}</ol>
{tiers}
<h2>{t['faqh']}</h2>{faq}
</main>
<footer><div class="wrap">{t['foot']}</div></footer>
<script src="/embed.js"></script>
<script>{js}</script>
<!-- Cloudflare Web Analytics (ohne Cookies, keine personenbezogenen Daten) --><script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token": "d5b51a031e8c4e26b08ad199a6bfd2da"}}'></script>
</body></html>
"""

for lang, d in (('de', 'einbinden'), ('en', 'en/embed')):
    os.makedirs(d, exist_ok=True)
    open(d + '/index.html', 'w').write(page(lang))
print('ok')

# Einheitlicher Rahmen (Kopfzeile, Fuß, ui.css) für alle öffentlichen Seiten
import importlib.util as _ilu, os as _os
_sp = _ilu.spec_from_file_location('unify_chrome', _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'unify_chrome.py')); _m = _ilu.module_from_spec(_sp); _sp.loader.exec_module(_m); _m.run()
