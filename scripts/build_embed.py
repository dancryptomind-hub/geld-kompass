#!/usr/bin/env python3
"""Baut die Seiten zum Einbinden der Rechner: /einbinden/ (DE) und /en/embed/ (EN).
Website-Betreiber wählen Rechner, Sprache und Währung, sehen eine Live-Vorschau und kopieren den iframe-Code."""
import json, os
from pathlib import Path
CONTENT = json.loads(Path(__file__).with_name("embed-content.json").read_text())
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
T = {'de': {'title': 'Finanzrechner kostenlos oder White-Label auf deiner Website einbinden | Geld-Kompass Pro', 'desc': '11 einbettbare Finanzrechner in Deutsch und Englisch. Kostenlos mit Anbieterhinweis oder als White-Label-Lizenz für Berater, Unternehmen und Agenturen.', 'eb': 'Für Finanzblogs, Berater, Kanzleien & Verlage', 'h1': 'Interaktive Finanzrechner für deine Website – in deiner Marke.', 'lead': '11 einbettbare Finanzrechner in Deutsch und Englisch. Kostenlos mit Anbieterhinweis oder als White-Label-Lizenz für Berater, Unternehmen und Agenturen.', 'calc': 'Rechner', 'lang': 'Sprache', 'cur': 'Währung', 'copy': 'Code kopieren', 'copied': 'Kopiert ✓', 'code': 'Dein Einbettungscode', 'prev': 'Live-Vorschau', 'how': 'In 3 Schritten auf deiner Website', 'steps': ['Rechner, Sprache, Währung und Farben wählen.', 'Code kopieren und als HTML-Block in deine Seite einfügen (WordPress, Webflow, Wix, Jimdo, HTML).', 'Vorschau und Einbindung auf deiner Website prüfen. Das Embed-Skript unterstützt die automatische Höhenanpassung.'], 'faq': [['Welche Rechner sind enthalten?', 'Die 11 im Konfigurator auswählbaren Rechner: Sparplan, Notgroschen, Freiheitstage, Schuldenfrei, Schneeball/Lawine, 4-Prozent-Regel, Kreditkarten, Inflation, Konsument oder Eigentümer, Währung und Steuern nach Wohnsitz. Die vollständige Geld-Kompass-App und der Dividenden-Kalender sind nicht Bestandteil dieser Embed-Lizenz.'], ['Welche Daten und Berechnungen werden verwendet?', 'Die Rechner zeigen Modellrechnungen und ihre jeweiligen Eingaben, Annahmen bzw. Quellen. Der <a href="/rechner/inflationsrechner/">Inflationsrechner</a> verwendet Eurostat-HVPI-Jahresdurchschnitte, der <a href="/rechner/waehrungsrechner/">Währungsrechner</a> zeigt den Datenstand der Wechselkurse und der <a href="/rechner/steuern-nach-wohnsitz/">Steuervergleich</a> führt Länderreferenzen und Quellen auf. Aktualität und Abdeckung bitte jeweils am angezeigten Datenstand prüfen. Keine Garantie für Echtzeitdaten oder individuelle Steuerergebnisse.'], ['Wie funktioniert Datenschutz?', 'Siehe <a href="/datenschutz/">Datenschutzhinweise</a>. Die rechtliche Bewertung der Einbindung hängt auch von deiner Website, Konfiguration und Rechtsordnung ab. Prüfe erforderliche Hinweise und Einwilligungen vor Veröffentlichung.'], ['Kann ich vorab testen?', 'Ja, sende uns Website und gewünschte Rechner. Eine individuelle Vorschau kann vor Abschluss angefragt werden.'], ['Wie werden Preise und Lizenz vereinbart?', 'Die Monatsbeträge enthalten anfallende indirekte Steuern. Umfang, Laufzeit und Kündigung werden vor der Bestellung vereinbart. Individuelle Einrichtung, Beratung, zusätzliche Rechner und Selbsthosting gehören nicht zur digitalen Standardlizenz.']], 'faqh': 'Häufige Fragen & Einwände geklärt', 'home': '/', 'app': 'Zum Geld-Kompass Pro', 'appurl': '/app/', 'sw': 'English', 'swurl': '/en/embed/?lang=en', 'all': 'Alle Rechner', 'allurl': '/rechner/', 'logo': 'Geld-<span>Kompass</span> <span class="pro">Pro</span>', 'foot': '<a href="/impressum/">Impressum</a> · <a href="/datenschutz/">Datenschutz</a> · Geld-Kompass Pro · © FreedomByDan · Allgemeine Finanzbildung, keine Anlage-, Steuer- oder Rechtsberatung.'}, 'en': {'title': 'Embed free or white-label finance calculators on your site | Money Compass Pro', 'desc': '11 embeddable financial calculators in English and German. Free with attribution or white-label licensing for advisers, businesses and agencies.', 'eb': 'For finance blogs, advisers, agencies & publishers', 'h1': 'Interactive financial calculators for your website — in your brand.', 'lead': '11 embeddable financial calculators in English and German. Free with attribution or white-label licensing for advisers, businesses and agencies.', 'calc': 'Calculator', 'lang': 'Language', 'cur': 'Currency', 'copy': 'Copy code', 'copied': 'Copied ✓', 'code': 'Your embed code', 'prev': 'Live preview', 'how': 'Live on your site in 3 steps', 'steps': ['Pick calculator, language, currency and theme.', 'Copy the code and paste it into a Custom HTML block (WordPress, Webflow, Ghost, Squarespace).', 'Check the preview and integration on your website. The embed script supports automatic height adjustment.'], 'faq': [['Which calculators are included?', 'The 11 calculators listed in the configurator: Savings plan, emergency fund, freedom days, debt-free, snowball/avalanche, 4% rule, credit card payoff, inflation, consumer or owner, currency converter and taxes by residence. The full Money Compass app and dividend calendar are not included in the embed licence.'], ['What data and calculation methods are used?', 'Calculators provide model estimates with their respective inputs, assumptions or sources. The <a href="/en/calculators/inflation-calculator/">inflation calculator</a> uses annual-average Eurostat HICP data, the <a href="/en/calculators/currency-converter/">currency converter</a> displays the exchange-rate data timestamp, and <a href="/en/calculators/taxes-by-residence/">taxes by residence</a> lists country references and sources. Check the displayed data date and coverage. No guarantee of real-time data or individual tax outcomes.'], ['What about privacy?', 'See the <a href="/datenschutz/?lang=en">privacy notice</a>. Compliance also depends on your website, configuration and applicable jurisdiction. Check required notices and consent before publishing.'], ['Can I try before buying?', 'Yes, send us your website and preferred calculators to request a custom preview before committing.'], ['How are pricing and licensing agreed?', 'Monthly amounts include applicable indirect taxes. Scope, term and cancellation are agreed before ordering. Bespoke setup, consulting, additional calculators and self-hosting are not part of the standard digital licence.']], 'faqh': 'Frequently asked questions', 'home': '/?lang=en', 'app': 'Open the Money Compass Pro', 'appurl': '/app/?lang=en', 'sw': 'Deutsch', 'swurl': '/einbinden/?lang=de', 'all': 'All calculators', 'allurl': '/en/calculators/', 'logo': 'Money <span>Compass</span> <span class="pro">Pro</span>', 'foot': '<a href="/impressum/?lang=en">Legal notice</a> · <a href="/datenschutz/?lang=en">Privacy</a> · Money Compass Pro · © FreedomByDan · General financial education, not investment, tax or legal advice.'}}
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
.eb-mode{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 10px}.eb-mode button{border:1px solid var(--line);background:var(--card2);color:var(--muted);border-radius:999px;padding:6px 12px;font:inherit;font-size:.82rem;font-weight:700;cursor:pointer}.eb-mode button[aria-pressed=true]{border-color:var(--gold);color:var(--gold);background:rgba(227,181,90,.1)}.eb-wl{display:none;align-items:center;justify-content:space-between;gap:10px;padding:10px 12px;border-radius:10px;margin-bottom:8px;background:linear-gradient(135deg,#1d4ed8,#0f766e);color:#fff;font-size:.85rem}.eb-prev.wl .eb-wl{display:flex}.eb-prev.wl{border-style:solid;border-color:rgba(56,189,248,.45)}.eb-prev.wl .eb-framebox{overflow:hidden;border-radius:10px}"""

CSS += """
/* Keep tariff cards independent of the global .pro logo badge. */
.eb-tiers{grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
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
    lic = CONTENT[lang]['lic']
    faq = ''.join('<details><summary>%s</summary><p>%s</p></details>' % tuple(q) for q in t['faq'])
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
 code();})();""" % (data, lang, t['copied'], t['copy'])
    og_img = BASE + ('screens/desktop-en.webp' if en else 'screens/desktop-de.webp')
    tiers = CONTENT[lang]['tiers']
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
</div><div><h2 style="margin-top:0">{t['prev']}</h2><div class="eb-mode" role="group" aria-label="{'Preview style' if en else 'Vorschau-Ansicht'}"><button type="button" data-ebmode="std" aria-pressed="true">{'Free embed' if en else 'Kostenlos (Standard)'}</button><button type="button" data-ebmode="wl" aria-pressed="false">{'White-Label demo' if en else 'White-Label-Vorschau'}</button></div><div class="eb-prev" id="ebPrevBox"><div class="eb-wl"><b>{'Sample Advisory Ltd · Custom Brand' if en else 'Muster Finanzberatung · Dein Design'}</b><span>{'Branding example · standard calculator' if en else 'Markenbeispiel · Standardrechner'}</span></div><div class="eb-framebox"><iframe data-gk id="ebFrame" title="{t['prev']}"></iframe></div></div><p class="eb-demo-note">{'Design example only. The embed code remains the free standard version with attribution. White-label use requires a separate domain licence.' if en else 'Gestaltungsbeispiel. Der Einbettungscode bleibt die kostenlose Standardversion mit Anbieterhinweis. White-Label-Nutzung erfordert eine gesonderte Domainlizenz.'}</p></div></div></section>
<h2>{t['how']}</h2><ol class="eb-steps">{''.join('<li>%s</li>' % s for s in t['steps'])}</ol>
{tiers}
<h2>{t['faqh']}</h2>{faq}
</main>
<footer><div class="wrap">{t['foot']}</div></footer>
<script src="/embed.js"></script>
<script type="module" src="/whitelabel-pricing.js"></script>
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
_sp = _ilu.spec_from_file_location('unify_chrome', _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'unify_chrome.py')); _m = _ilu.module_from_spec(_sp); _sp.loader.exec_module(_m)
import sys as _sys
_sys.path.insert(0, str(Path(__file__).parent))
import csp as _csp
for _rel in ('einbinden/index.html', 'en/embed/index.html'):
    _path = Path(_rel)
    _m.process(str(_path.resolve()))
    _path.write_text(_csp.build(_rel, _path.read_text()))
