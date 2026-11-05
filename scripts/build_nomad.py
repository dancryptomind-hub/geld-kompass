#!/usr/bin/env python3
"""Landingpages der zweiten Säule „international und ortsunabhängig“:
/auswandern-finanzen/ (DE) und /en/expat-money-app/ (EN)."""
import json, os, html
BASE = 'https://geld-kompass.com/'
LOGO = '<img class="gk-logo" src="/icons/logo-badge.webp?v=3" alt="" aria-hidden="true" width="34" height="34">'
VIS = '<link rel=stylesheet href=/visuals.css?v20261104a><script src=/visuals.js?v20261104a></script>'
esc = html.escape
DE_URL, EN_URL = BASE + 'auswandern-finanzen/', BASE + 'en/expat-money-app/'
T = {
'de': dict(url=DE_URL, other=EN_URL, sw='English', swurl='/en/expat-money-app/?lang=en', home='/', app='/app/',
  title='Finanz-App für Auswanderer und digitale Nomaden: Tage je Land, Währungen, Freiheitstage',
  desc='Aufenthaltstage je Land und Schengen 90/180 zählen, in über 50 Währungen planen und sehen, wie viele Freiheitstage dein Vermögen kauft. Ohne Bankkonto, ohne Anmeldung.',
  eb='Für Auswanderer und Nomaden', h1='Die Finanz-App für ein Leben in mehr als einem Land',
  lead='Zähle deine Tage je Land und im Schengen-Raum, plane in jeder Währung und sieh, wie viele Freiheitstage dein Vermögen dir kauft. Ohne Bankkonto, ohne Anmeldung, deine Daten bleiben auf deinem Gerät.',
  cta1='Nomaden-Modus öffnen', plus='Nomaden-Modus ist Teil von Plus · bis zum Start kostenlos in der Vorschau', cta2='Meine Freiheitstage in 60 Sekunden', img='nomad-de', alt='Nomaden-Modus: Tage je Land und Schengen-Zähler',
  sec=[('Tage je Land und Schengen 90/180', 'Trag ein, wann du wo angekommen bist. Der Kompass zählt deine Tage je Land und Jahr, zeigt deinen Schengen-Stand über die letzten 180 Tage und warnt, wenn du dich der üblichen 183-Tage-Marke näherst. Als Orientierung, nicht als Steuerberatung.'),
       ('Jede Währung, eine Übersicht', 'Buche in Baht, Lari, Dong oder Dollar. Der Kompass rechnet mit Tageskursen in deine Hauptwährung um, damit Monatsbericht, Depot und Freiheitstage stimmen.'),
       ('Was ein Monat in welchem Land kostet', 'Pro Land siehst du deine durchschnittlichen Ausgaben im Monat. So erkennst du, wo dich das Leben wie viele Freiheitstage kostet, und kannst deine nächste Station bewusst wählen.'),
       ('Funktioniert ohne lokales Bankkonto', 'Kein Bankzugang nötig. Trag grob ein oder lies Kontoauszüge als Datei ein, zum Beispiel von Wise oder Revolut. Abos und Fixkosten erkennt der Kompass dann selbst.')],
  faq=[('Sagt mir die App, wo ich steuerpflichtig bin?', 'Nein. Sie zählt deine Tage als Orientierung. Die 183 Tage sind eine häufige, aber keine überall gültige Regel. Wo du steuerlich ansässig bist, klärst du mit einer Steuerberatung.'),
       ('Welche Währungen gehen?', 'Über 50 Währungen mit Tageskursen, dazu Bitcoin. Deine Hauptwährung wählst du selbst.'),
       ('Brauche ich ein Bankkonto oder eine Anmeldung?', 'Nein. Der Geld-Kompass Pro läuft im Browser und als App auf dem Handy, ohne Konto und ohne Bankzugang.'),
       ('Kostet das etwas?', 'Freiheitstage, Budget, Schulden-Plan und Währungsrechner sind kostenlos. Der Nomaden-Modus gehört zu Plus, dem kommenden Abo. Bis zum Start kannst du ihn in der Vorschau kostenlos testen.')],
  faqh='Häufige Fragen', fx='Geld zwischen Ländern senden? Rechne vorher im <a href="/rechner/waehrungsrechner/">Währungsrechner</a> mit Live-Kursen.',
  foot='<a href="/impressum/">Impressum</a> · <a href="/datenschutz/">Datenschutz</a> · <a href="/werbung/">Werbung</a> · Geld-Kompass Pro · © FreedomByDan · Allgemeine Finanzbildung, keine Steuer-, Rechts- oder Anlageberatung.',
  logo='Geld-<span>Kompass</span> <span class="pro">Pro</span>'),
'en': dict(url=EN_URL, other=DE_URL, sw='Deutsch', swurl='/auswandern-finanzen/?lang=de', home='/?lang=en', app='/app/?lang=en',
  title='Money app for expats and digital nomads: days per country, currencies, freedom days',
  desc='Count days per country and Schengen 90/180, plan in 50+ currencies and see how many freedom days your wealth buys. No bank account, no sign-up.',
  eb='For expats and nomads', h1='The money app for a life in more than one country',
  lead='Count your days per country and in the Schengen area, plan in any currency and see how many freedom days your wealth buys you. No bank account, no sign-up, your data stays on your device.',
  cta1='Open nomad mode', plus='Nomad mode is part of Plus · free in preview until launch', cta2='My freedom days in 60 seconds', img='nomad-en', alt='Nomad mode: days per country and Schengen counter',
  sec=[('Days per country and Schengen 90/180', 'Enter when you arrived where. The Compass counts your days per country and year, shows your Schengen status over the last 180 days and warns you when you approach the common 183-day mark. As guidance, not tax advice.'),
       ('Every currency, one overview', 'Book in baht, lari, dong or dollars. The Compass converts with daily rates into your main currency so your monthly report, portfolio and freedom days add up.'),
       ('What a month costs in which country', 'For each country you see your average monthly spending. So you know how many freedom days life costs you where, and can choose your next stop on purpose.'),
       ('Works without a local bank account', 'No bank access needed. Enter rough numbers or import statements as files, for example from Wise or Revolut. The Compass then spots subscriptions and fixed costs by itself.')],
  faq=[('Does the app tell me where I am tax resident?', 'No. It counts your days as guidance. 183 days is a common rule but not universal. Where you are tax resident is something to clarify with a tax adviser.'),
       ('Which currencies work?', '50+ currencies with daily rates, plus bitcoin. You choose your main currency.'),
       ('Do I need a bank account or an account?', 'No. Money Compass Pro runs in the browser and as an app on your phone, without an account and without bank access.'),
       ('Does it cost anything?', 'Freedom days, budget, debt plan and currency converter are free. Nomad mode is part of Plus, the upcoming subscription. Until launch you can try it for free in the preview.')],
  faqh='Frequently asked questions', fx='Sending money between countries? Check first in the <a href="/en/calculators/currency-converter/">currency converter</a> with live rates.',
  foot='<a href="/impressum/?lang=en">Legal notice</a> · <a href="/datenschutz/?lang=en">Privacy</a> · <a href="/werbung/?lang=en">Advertising</a> · Money Compass Pro · © FreedomByDan · General financial education, not tax, legal or investment advice.',
  logo='Money <span>Compass</span> <span class="pro">Pro</span>'),
}
CSS = """.nm-img{display:block;width:100%;height:auto;border-radius:16px;border:1px solid var(--line);margin:22px 0 6px;box-shadow:0 24px 60px -25px rgba(0,0,0,.6)}
.nm-cta{display:flex;flex-wrap:wrap;gap:10px;margin:6px 0 10px}.nm-cta a{display:inline-block;padding:13px 20px;border-radius:12px;font-weight:800;text-decoration:none}.nm-cta .p{background:linear-gradient(135deg,#f0c56a,#c99227);color:#1a1405}.nm-cta .s{border:1px solid var(--gold);color:var(--gold)}
.nm-plus{display:flex;align-items:center;gap:8px;color:var(--muted);font-size:14px;margin:4px 0 0}.nm-plus span{background:linear-gradient(135deg,#f0c56a,#c99227);color:#1a1405;font-weight:800;font-size:11px;letter-spacing:.06em;text-transform:uppercase;padding:3px 9px;border-radius:99px}
.nm-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-top:26px}@media(max-width:720px){.nm-grid{grid-template-columns:1fr}}.nm-grid section{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px}.nm-grid h2{margin:0 0 6px;font-size:19px}.nm-grid p{margin:0;color:var(--muted)}"""

def page(lang):
    t = T[lang]
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in t['faq']]}
    secs = ''.join('<section><h2>%s</h2><p>%s</p></section>' % (esc(h), esc(p)) for h, p in t['sec'])
    faq = ''.join('<details><summary>%s</summary><p>%s</p></details>' % (esc(q), esc(a)) for q, a in t['faq'])
    other_lang = 'de' if lang == 'en' else 'en'
    return f"""<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<script>(function(){{var K='geld-kompass-lang',q=new URLSearchParams(location.search).get('lang'),w=q;if(q==='de'||q==='en'){{try{{localStorage.setItem(K,q);}}catch(e){{}}}}else{{try{{w=localStorage.getItem(K);}}catch(e){{}}}}if((w==='de'||w==='en')&&w!=='{lang}')location.replace('{t['other'].replace(BASE, '/')}'+location.search+location.hash);}})();</script>
<title>{esc(t['title'])} | {'Money' if lang=='en' else 'Geld'}-{'Compass' if lang=='en' else 'Kompass'} Pro</title><meta name="description" content="{esc(t['desc'])}">
<link rel="canonical" href="{t['url']}"><link rel="alternate" hreflang="de" href="{DE_URL}"><link rel="alternate" hreflang="en" href="{EN_URL}"><link rel="alternate" hreflang="x-default" href="{EN_URL}">
<meta name="theme-color" content="#0E1730"><meta property="og:type" content="website"><meta property="og:title" content="{esc(t['title'])}"><meta property="og:description" content="{esc(t['desc'])}"><meta property="og:url" content="{t['url']}"><meta property="og:image" content="{BASE}screens/{t['img']}.webp">
<link rel="stylesheet" href="/rechner/rechner.css"><link rel="manifest" href="/manifest.webmanifest"><link rel="icon" type="image/png" sizes="32x32" href="/icons/favicon-32.png?v=3"><link rel="apple-touch-icon" href="/icons/apple-touch-icon.png?v=3">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>{CSS}</style>
{VIS}</head><body>
<header class="top"><div class="wrap"><a class="logo" href="{t['home']}">{LOGO}<b>{t['logo']}</b></a><nav><a href="{t['app']}">App</a> · <a class="langsw" href="{t['swurl']}" hreflang="{other_lang}">{t['sw']}</a></nav></div></header>
<main class="wrap">
<div class="eyebrow">{esc(t['eb'])}</div>
<h1>{esc(t['h1'])}</h1>
<p class="lead">{esc(t['lead'])}</p>
<div class="nm-cta"><a class="p" href="{t['app']}{'&' if '?' in t['app'] else '?'}start=1#overview">{esc(t['cta2'])}</a><a class="s" href="{t['app']}#nomad">{esc(t['cta1'])}</a></div>
<p class="nm-plus"><span>Plus</span>{esc(t['plus'])}</p>
<img class="nm-img" src="/screens/{t['img']}.webp" width="1100" height="805" alt="{esc(t['alt'])}">
<div class="nm-grid">{secs}</div>
<p class="note">{t['fx']}</p>
<div data-partner="fx" hidden></div>
<h2>{esc(t['faqh'])}</h2>{faq}
</main>
<footer><div class="wrap">{t['foot']}</div></footer>
<script src="/partner.js" defer></script>
<!-- Cloudflare Web Analytics (ohne Cookies, keine personenbezogenen Daten) --><script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token": "d5b51a031e8c4e26b08ad199a6bfd2da"}}'></script>
</body></html>
"""

for lang, d in (('de', 'auswandern-finanzen'), ('en', 'en/expat-money-app')):
    os.makedirs(d, exist_ok=True)
    open(d + '/index.html', 'w').write(page(lang))
print('ok')

# Einheitlicher Rahmen (Kopfzeile, Fuß, ui.css) für alle öffentlichen Seiten
import importlib.util as _ilu, os as _os
_sp = _ilu.spec_from_file_location('unify_chrome', _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'unify_chrome.py')); _m = _ilu.module_from_spec(_sp); _sp.loader.exec_module(_m); _m.run()
