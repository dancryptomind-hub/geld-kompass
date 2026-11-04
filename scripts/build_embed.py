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
]
T = {
 'de': dict(title='Finanzrechner kostenlos auf deiner Website einbinden | Geld-Kompass Pro',
   desc='Binde Sparplan-, Schulden-, Notgroschen- und weitere Finanzrechner kostenlos in deinen Blog oder deine Website ein. Code kopieren, einfügen, fertig.',
   eb='Für Website-Betreiber', h1='Finanzrechner kostenlos auf deiner Website einbinden',
   lead='Für Blogs, Vereine, Schulen und Finanz-Seiten: Wähle einen Rechner, kopiere den Code und füge ihn in deine Seite ein. Der Rechner passt seine Höhe automatisch an, läuft komplett im Browser deiner Besucher und speichert nichts.',
   calc='Rechner', lang='Sprache', cur='Währung', copy='Code kopieren', copied='Kopiert ✓', code='Dein Einbettungscode', prev='Live-Vorschau',
   how='So funktioniert es', steps=['Rechner, Sprache und Währung wählen.', 'Code kopieren und an der gewünschten Stelle in deine Seite einfügen (WordPress: Block „Individuelles HTML“).', 'Fertig. Die Höhe passt sich automatisch an, auch auf dem Handy.'],
   faq=[('Kostet das etwas?', 'Nein. Die Rechner sind kostenlos. Unter jedem Rechner steht ein dezenter Hinweis „Bereitgestellt von Geld-Kompass Pro“, der bleiben muss.'),
        ('Werden Daten meiner Besucher gespeichert?', 'Nein. Alle Rechnungen laufen im Browser. Es gibt keine Cookies, kein Tracking und keine Anmeldung im Rechner.'),
        ('Kann ich den Rechner ohne Hinweis oder in meinen Farben haben?', 'Ja, als Lizenz-Version für Unternehmen, Banken-Blogs und Berater. Schreib an <a href="mailto:kontakt@geld-kompass.com?subject=Rechner-Lizenz">kontakt@geld-kompass.com</a>.'),
        ('Ist das Anlageberatung?', 'Nein. Die Rechner sind Modellrechnungen zur Finanzbildung und keine Anlage-, Steuer- oder Rechtsberatung.')],
   faqh='Häufige Fragen', home='/', app='Zum Geld-Kompass Pro', appurl='/app/', sw='English', swurl='/en/embed/?lang=en', all='Alle Rechner', allurl='/rechner/',
   logo='Geld-<span>Kompass</span> <span class="pro">Pro</span>',
   foot='<a href="/impressum/">Impressum</a> · <a href="/datenschutz/">Datenschutz</a> · Geld-Kompass Pro · © FreedomByDan · Allgemeine Finanzbildung, keine Anlage-, Steuer- oder Rechtsberatung.'),
 'en': dict(title='Embed free money calculators on your website | Money Compass Pro',
   desc='Embed savings plan, debt, emergency fund and other money calculators on your blog or website for free. Copy the code, paste it, done.',
   eb='For website owners', h1='Embed free money calculators on your website',
   lead='For blogs, clubs, schools and finance sites: pick a calculator, copy the code and paste it into your page. The calculator adjusts its height automatically, runs entirely in your visitors’ browser and stores nothing.',
   calc='Calculator', lang='Language', cur='Currency', copy='Copy code', copied='Copied ✓', code='Your embed code', prev='Live preview',
   how='How it works', steps=['Choose calculator, language and currency.', 'Copy the code and paste it where you want it on your page (WordPress: “Custom HTML” block).', 'Done. The height adjusts automatically, on phones too.'],
   faq=[('Does it cost anything?', 'No. The calculators are free. Each one shows a small “Powered by Geld-Kompass Pro” note, which must stay in place.'),
        ('Is my visitors’ data stored?', 'No. All calculations run in the browser. There are no cookies, no tracking and no sign-up inside the calculator.'),
        ('Can I get it without the note or in my own colours?', 'Yes, as a licensed version for companies, bank blogs and advisers. Write to <a href="mailto:kontakt@geld-kompass.com?subject=Calculator%20licence">kontakt@geld-kompass.com</a>.'),
        ('Is this investment advice?', 'No. The calculators are model calculations for financial education, not investment, tax or legal advice.')],
   faqh='Frequently asked questions', home='/?lang=en', app='Open the Money Compass Pro', appurl='/app/?lang=en', sw='Deutsch', swurl='/einbinden/?lang=de', all='All calculators', allurl='/en/calculators/',
   logo='Money <span>Compass</span> <span class="pro">Pro</span>',
   foot='<a href="/impressum/?lang=en">Legal notice</a> · <a href="/datenschutz/?lang=en">Privacy</a> · Money Compass Pro · © FreedomByDan · General financial education, not investment, tax or legal advice.'),
}
CSS = """.eb-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.4fr);gap:18px;align-items:start}
@media(max-width:820px){.eb-grid{grid-template-columns:1fr}}
.eb-form label{display:block;margin:0 0 12px;font-weight:600}
.eb-form select{display:block;width:100%;margin-top:6px;padding:10px 12px;border-radius:10px;border:1px solid rgba(14,23,48,.18);background:#fff;color:inherit;font:inherit}
.eb-form select option{color:#0E1730}
.eb-code{width:100%;min-height:150px;font:12.5px/1.5 ui-monospace,Menlo,Consolas,monospace;padding:12px;border-radius:10px;border:1px solid rgba(227,181,90,.4);background:#fffaf0;color:#0E1730;resize:vertical;box-sizing:border-box}
.eb-btn{margin-top:10px;width:100%;padding:12px 16px;border:0;border-radius:12px;background:linear-gradient(135deg,#f0c56a,#c99227);color:#1a1405;font-weight:800;font-size:1rem;cursor:pointer}
.eb-prev{border:1px dashed rgba(14,23,48,.2);border-radius:14px;padding:10px;background:rgba(255,255,255,.03)}
.eb-prev iframe{display:block;width:100%;border:0;min-height:400px;border-radius:10px}
.eb-steps{counter-reset:s;list-style:none;padding:0}.eb-steps li{counter-increment:s;padding:6px 0 6px 38px;position:relative}
.eb-steps li:before{content:counter(s);position:absolute;left:0;top:4px;width:26px;height:26px;border-radius:50%;background:#c99227;color:#1a1405;font-weight:800;display:grid;place-items:center;font-size:.85rem}
.eb-lic{margin-top:14px;padding:14px 16px;border-radius:14px;border:1px solid rgba(227,181,90,.45);background:linear-gradient(135deg,rgba(227,181,90,.12),rgba(227,181,90,.03))}"""

def page(lang):
    t = T[lang]; en = lang == 'en'
    url = BASE + ('en/embed/' if en else 'einbinden/')
    opts = ''.join('<option value="%d">%s</option>' % (i, c[3] if en else c[1]) for i, c in enumerate(CALC))
    data = json.dumps([[c[0], c[1], c[2], c[3], c[4]] for c in CALC], ensure_ascii=False)
    lic = ('<div class="eb-lic"><b>Licensed version for companies</b><br>Without the note, in your colours, with your own calculators or your logo. Write to <a href="mailto:kontakt@geld-kompass.com?subject=Calculator%20licence">kontakt@geld-kompass.com</a>.</div>' if en else
           '<div class="eb-lic"><b>Lizenz-Version für Unternehmen</b><br>Ohne Hinweis, in deinen Farben, mit eigenen Rechnern oder deinem Logo. Schreib an <a href="mailto:kontakt@geld-kompass.com?subject=Rechner-Lizenz">kontakt@geld-kompass.com</a>.</div>')
    faq = ''.join('<details><summary>%s</summary><p>%s</p></details>' % q for q in t['faq'])
    ld = json.dumps({"@context": "https://schema.org", "@type": "WebPage", "name": t['h1'], "url": url, "inLanguage": lang, "description": t['desc']}, ensure_ascii=False)
    js = """(function(){var C=%s,L='%s';var $=function(i){return document.getElementById(i);};
 function code(){var c=C[+$('ebCalc').value],l=$('ebLang').value,cur=$('ebCur').value,path=l==='en'?'/en/calculators/'+c[2]+'/':'/rechner/'+c[0]+'/',name=l==='en'?c[3]:c[1];
  var src='https://geld-kompass.com'+path+'?embed=1'+(cur?'&cur='+cur:'');
  $('ebCode').value='<iframe data-gk src="'+src+'" title="'+name+' · Geld-Kompass Pro" loading="lazy" style="width:100%%;max-width:760px;height:'+c[4]+'px;border:0;border-radius:12px"></iframe>\\n<script src="https://geld-kompass.com/embed.js" async></'+'script>';
  var f=$('ebFrame'),p=path+'?embed=1'+(cur?'&cur='+cur:'');if(f.getAttribute('src')!==p){f.style.height=c[4]+'px';f.setAttribute('src',p);}}
 ['ebCalc','ebLang','ebCur'].forEach(function(i){$(i).addEventListener('change',code);});
 $('ebCopy').addEventListener('click',function(){var t=$('ebCode'),b=this,done=function(){b.textContent='%s';setTimeout(function(){b.textContent='%s';},1800);};
  if(navigator.clipboard)navigator.clipboard.writeText(t.value).then(done,function(){t.select();document.execCommand('copy');done();});else{t.select();document.execCommand('copy');done();}});
 $('ebCode').addEventListener('focus',function(){this.select();});code();})();""" % (data, lang, t['copied'], t['copy'])
    return f"""<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<script>(function(){{var K='geld-kompass-lang',q=new URLSearchParams(location.search).get('lang'),w=q;if(q==='de'||q==='en'){{try{{localStorage.setItem(K,q);}}catch(e){{}}}}else{{try{{w=localStorage.getItem(K);}}catch(e){{}}}}if((w==='de'||w==='en')&&w!=='{lang}')location.replace('{'/einbinden/' if en else '/en/embed/'}'+location.search+location.hash);}})();</script>
<title>{t['title']}</title><meta name="description" content="{t['desc']}">
<link rel="canonical" href="{url}"><link rel="alternate" hreflang="de" href="{BASE}einbinden/"><link rel="alternate" hreflang="en" href="{BASE}en/embed/"><link rel="alternate" hreflang="x-default" href="{BASE}einbinden/">
<meta name="theme-color" content="#0E1730"><meta property="og:type" content="website"><meta property="og:title" content="{t['title']}"><meta property="og:description" content="{t['desc']}"><meta property="og:url" content="{url}">
<link rel="stylesheet" href="/rechner/rechner.css"><link rel="manifest" href="/manifest.webmanifest">
<link rel="icon" type="image/png" sizes="32x32" href="/icons/favicon-32.png?v=3"><link rel="apple-touch-icon" href="/icons/apple-touch-icon.png?v=3">
<script type="application/ld+json">{ld}</script>
<style>{CSS}</style>
</head><body data-page-lang="{lang}">
<header class="top"><div class="wrap"><a class="logo" href="{t['home']}">{LOGO}<b>{t['logo']}</b></a><nav><a href="{t['allurl']}">{t['all']}</a> · <a class="langsw" href="{t['swurl']}">{t['sw']}</a></nav></div></header>
<main class="wrap">
<div class="eyebrow">{t['eb']}</div>
<h1>{t['h1']}</h1>
<p class="lead">{t['lead']}</p>
<section class="card"><div class="eb-grid"><div class="eb-form">
<label>{t['calc']}<select id="ebCalc">{opts}</select></label>
<label>{t['lang']}<select id="ebLang"><option value="de"{'' if en else ' selected'}>Deutsch</option><option value="en"{' selected' if en else ''}>English</option></select></label>
<label>{t['cur']}<select id="ebCur"><option value="">{'Automatic' if en else 'Automatisch'}</option><option value="EUR"{'' if en else ' selected'}>EUR €</option><option value="USD"{' selected' if en else ''}>USD $</option><option value="GBP">GBP £</option><option value="CHF">CHF</option><option value="CAD">CAD</option><option value="AUD">AUD</option></select></label>
<label>{t['code']}<textarea id="ebCode" class="eb-code" readonly spellcheck="false"></textarea></label>
<button type="button" class="eb-btn" id="ebCopy">{t['copy']}</button>
{lic}
</div><div><h2 style="margin-top:0">{t['prev']}</h2><div class="eb-prev"><iframe data-gk id="ebFrame" title="{t['prev']}"></iframe></div></div></div></section>
<h2>{t['how']}</h2><ol class="eb-steps">{''.join('<li>%s</li>' % s for s in t['steps'])}</ol>
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
