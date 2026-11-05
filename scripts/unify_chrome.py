#!/usr/bin/env python3
"""Einheitlicher Rahmen für ALLE öffentlichen Seiten: gleiche Kopfzeile, gleicher Fuß, gemeinsames /ui.css.
Idempotent: kann nach jedem Generator erneut laufen (build_rechner, build_embed, build_ratgeber, build_nomad, dividend_pages).
Nicht angefasst: /app/ (eigene App-Oberfläche), /konto/ (Codex), Weiterleitungen /go/, /start/ und /buchbegruessung/ (Intro-Seiten)."""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://geld-kompass.com'
LOGO = '<img class="gk-logo" src="/icons/logo-badge.webp?v=3" alt="" aria-hidden="true" width="34" height="34">'
SKIP = ('app/', 'konto/', 'go/', 'en/go/', 'start/', 'buchbegruessung/', 'en/advertising/', 'node_modules/', 'tests/', '_')
UI = '<link rel="stylesheet" href="/ui.css?v=1">'

def chrome(lang, other, bilingual):
    en = lang == 'en'
    if en:
        logo = 'Money <span>Compass</span> <span class="pro">Pro</span>'
        nav = [('/en/calculators/', 'Calculators'), ('/en/expat-money-app/', 'Expats & nomads')]
        app, appt, sw = '/app/?lang=en', 'Open app', 'Deutsch'
        foot = [('/en/calculators/', 'Calculators'), ('/en/embed/', 'Embed'), ('/en/expat-money-app/', 'Expats & nomads'), ('/en/workbook/', 'Workbook'), ('/impressum/?lang=en', 'Legal notice'), ('/datenschutz/?lang=en', 'Privacy'), ('/werbung/?lang=en', 'Advertising')]
        note = 'Money Compass Pro · © FreedomByDan · General financial education, not investment, tax or legal advice. All calculations are model calculations.'
        home = '/?lang=en'
    else:
        logo = 'Geld-<span>Kompass</span> <span class="pro">Pro</span>'
        nav = [('/rechner/', 'Rechner'), ('/ratgeber/', 'Ratgeber')]
        app, appt, sw = '/app/', 'App öffnen', 'English'
        foot = [('/rechner/', 'Rechner'), ('/ratgeber/', 'Ratgeber'), ('/einbinden/', 'Einbinden'), ('/auswandern-finanzen/', 'Auswandern'), ('/arbeitsbuch/', 'Arbeitsbuch'), ('/impressum/', 'Impressum'), ('/datenschutz/', 'Datenschutz'), ('/werbung/', 'Werbung')]
        note = 'Geld-Kompass Pro · © FreedomByDan · Begleiter zum Buch „Der einfache Weg zur Finanziellen Freiheit“ · Allgemeine Finanzbildung, keine Anlage-, Steuer- oder Rechtsberatung. Alle Berechnungen sind Modellrechnungen.'
        home = '/'
    if bilingual:
        swurl = '?lang=' + ('de' if en else 'en')
    elif other:
        swurl = other.replace(BASE, '') + ('?lang=' + ('de' if en else 'en'))
    else:
        swurl = None
    links = ''.join('<a href="%s">%s</a>' % x for x in nav)
    lsw = '<a class="langsw" href="%s" hreflang="%s">%s</a>' % (swurl, 'de' if en else 'en', sw) if swurl else ''
    if bilingual:  # eine Datei für beide Sprachen: Umschalter passt sich der angezeigten Sprache an
        lsw = '<a class="langsw" data-bi href="?lang=en" hreflang="en">English</a><script>(function(){var a=document.currentScript.previousElementSibling;if(document.documentElement.lang==="en"){a.href="?lang=de";a.hreflang="de";a.textContent="Deutsch";a.setAttribute("data-i18n-skip","")}})();</script>'
    header = ('<header class="top gk-chrome"><div class="wrap"><a class="logo" href="%s">%s<b>%s</b></a><nav>%s%s<a class="navapp" href="%s"><span class="l">%s</span><span class="s">App</span></a></nav></div></header>'
              % (home, LOGO, logo, links, lsw, app, appt))
    footer = ('<footer class="gk-foot"><div class="wrap"><nav>%s<a href="https://geld-kompass.com/go/whatsapp/" target="_blank" rel="noopener">WhatsApp</a></nav><p>%s</p></div></footer>'
              % (''.join('<a href="%s">%s</a>' % x for x in foot), note))
    return header, footer

def process(path):
    rel = os.path.relpath(path, ROOT).replace(os.sep, '/')
    if rel.startswith(SKIP) or '/_' in rel:
        return False
    s = open(path, encoding='utf-8').read()
    if 'http-equiv="refresh"' in s:
        return False
    m = re.search(r'<html lang="(de|en)"', s)
    lang = m.group(1) if m else 'de'
    other = None
    for hl, href in re.findall(r'<link rel="alternate" hreflang="(de|en)" href="([^"]+)"', s):
        if hl != lang:
            other = href
    bilingual = 'href="/site.css"' in s and not other  # Startseite, Impressum, Datenschutz, Werbung: eine Datei, Sprache per DICT
    header, footer = chrome(lang, other, bilingual)
    o = s
    if UI not in s:
        s = re.sub(r'<link rel="stylesheet" href="/ui\.css[^"]*">', '', s)
        s = s.replace('</head>', UI + '</head>', 1)
    # Kopfzeile ersetzen oder einfügen
    if re.search(r'<header class="top[^"]*">.*?</header>', s, flags=re.S):
        s = re.sub(r'<header class="top[^"]*">.*?</header>', header, s, count=1, flags=re.S)
    else:
        s = re.sub(r'(<body[^>]*>)', r'\1' + '\n' + header.replace('\\', '\\\\'), s, count=1)
        # eigene Logo-Zeile in main entfernen (Startseite, Rechtstexte)
        s = re.sub(r'(<main[^>]*>)\s*<a class="logo" href="/">.*?</a>\s*', r'\1\n', s, count=1, flags=re.S)
    # Fuß ersetzen oder einfügen
    if re.search(r'<footer[^>]*>.*?</footer>', s, flags=re.S):
        s = re.sub(r'<footer[^>]*>.*?</footer>', footer.replace('\\', '\\\\'), s, count=1, flags=re.S)
    else:
        s = re.sub(r'<nav class="links">.*?</nav>\s*(<small>[^<]*</small>)?', '', s, count=1, flags=re.S)
        s = s.replace('</main>', '</main>\n' + footer, 1)
    if 'href="/site.css"' in s and 'class="gk-u"' not in s:
        s = re.sub(r'<body(?![^>]*gk-u)([^>]*)>', lambda mm: '<body' + (mm.group(1).replace('class="', 'class="gk-u ') if 'class="' in mm.group(1) else mm.group(1) + ' class="gk-u"') + '>', s, count=1)
    if s != o:
        open(path, 'w', encoding='utf-8').write(s)
        return True
    return False

def run():
    n = 0
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if not d.startswith('.') and d != 'node_modules']
        if 'index.html' in fn and process(os.path.join(dp, 'index.html')):
            n += 1
    return n

if __name__ == '__main__':
    print('vereinheitlicht:', run())
