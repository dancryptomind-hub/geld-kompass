#!/usr/bin/env python3
"""Steuern nach Wohnsitz: kostenloser Vergleich (DE /rechner/steuern-nach-wohnsitz/, EN /en/calculators/taxes-by-residence/)
und je Land eine eigene Seite (für Suchanfragen wie „Steuern Thailand Auswanderer“).
Daten: data/tax-residence.json (Länderreferenzen mit Quellen). Danach build_rechner.py (Sitemap, Rahmen) und csp.py laufen lassen.
Aufruf im Repo-Hauptordner: python3 scripts/build_steuern.py"""
import json, os, html, re, unicodedata
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://geld-kompass.com/'
esc = lambda s: html.escape(str(s), quote=True)
LOGO = '<img class="gk-logo" src="/icons/logo-badge.webp?v=3" alt="" aria-hidden="true" width="34" height="34">'
DE_DIR, EN_DIR = 'rechner/steuern-nach-wohnsitz', 'en/calculators/taxes-by-residence'
NAME_FIX = {'HK': ('Hongkong', 'Hong Kong'), 'US': ('USA', 'United States'), 'GB': ('Großbritannien', 'United Kingdom'), 'MD': ('Moldau', 'Moldova'), 'AE': ('Vereinigte Arabische Emirate (Dubai)', 'United Arab Emirates (Dubai)')}
REGION = {
 'EU': 'AT BE BG CH CZ DE DK EE ES FI FR GR HR HU IS IT LI LT LU LV MT NL NO PL PT RO SE SI SK CY IE GB AL ME RS BA MK MD UA',
 'AS': 'TH VN ID MY PH KH LA SG JP KR TW CN HK IN LK NP MV KZ UZ KG',
 'ME': 'AE QA OM BH SA JO IL TR GE AM AZ',
 'AM': 'US CA MX CO BR AR CL PE EC UY PA CR DO',
 'AF': 'ZA MA EG KE TZ MU AU NZ'}
REG_OF = {c: r for r, cs in REGION.items() for c in cs.split()}
REG_NAME = {'EU': ('Europa', 'Europe'), 'AS': ('Asien', 'Asia'), 'ME': ('Naher Osten und Kaukasus', 'Middle East and Caucasus'), 'AM': ('Amerika', 'Americas'), 'AF': ('Afrika und Ozeanien', 'Africa and Oceania')}

def slugify(s):
    s = s.replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('Ä', 'ae').replace('Ö', 'oe').replace('Ü', 'ue').replace('ß', 'ss')
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', re.sub(r'\(.*?\)', '', s)).strip('-')

def load():
    d = json.load(open(os.path.join(ROOT, 'data/tax-residence.json')))
    for c, fix in NAME_FIX.items():
        if c in d['countries']: d['countries'][c]['name'] = list(fix)
    for x in d['countries'].values():
        for f in ('incomeDisplay', 'capitalDisplay', 'note'):
            x[f] = [v.replace(' %', '\u00a0%') for v in x[f]]
    d['slugs'] = {c: slugify(x['name'][0]) for c, x in d['countries'].items()}
    d['slugs_en'] = {c: slugify(x['name'][1]) for c, x in d['countries'].items()}
    return d

def urls():
    d = load()
    return ([BASE + DE_DIR + '/', BASE + EN_DIR + '/'] + [BASE + DE_DIR + '/' + s + '/' for s in d['slugs'].values()] + [BASE + EN_DIR + '/' + s + '/' for s in d['slugs_en'].values()])

SRC_EN = [('Einkommensteuergesetz', 'Income Tax Act'), ('Einkommensteuer', 'Income tax'), ('Private Kapitalgewinne', 'Private capital gains'), ('Kapitalgewinne', 'Capital gains'), ('Veräußerungsgewinne', 'Capital gains'), ('Finanzministerium', 'Ministry of Finance'), ('Tarife', 'Rates')]
def src_label(s, en):
    if en:
        for a, b in SRC_EN: s = s.replace(a, b)
    return s

def calc_html(en, c='', cmp=''):
    L = (('Wohnsitz-Land', 'Vergleichen mit', 'Einkommen pro Jahr aus Arbeit', 'Kapitalerträge pro Jahr') if not en else
         ('Country of residence', 'Compare with', 'Income per year from work', 'Capital income per year'))
    return ('<div id="tx" data-c="%s" data-cmp="%s"><div class="grid">'
            '<label>%s<select id="txA"></select></label><label>%s<select id="txB"></select></label>'
            '<label>%s<input id="txInc" inputmode="decimal" value="48000"></label><label>%s<input id="txCap" inputmode="decimal" value="6000"></label>'
            '</div><div id="res"><div id="txOut"><p class="note">%s</p></div></div><p class="note">%s</p><div class="share" id="share"></div></div>') % (
        c, cmp, L[0], L[1], L[2], L[3], 'Länderdaten werden geladen …' if not en else 'Loading country data …',
        ('Länderwerte zur Orientierung: Spitzensatz der Einkommensteuer und Referenzsatz für Kapitalerträge. Persönliche Lage, Freibeträge, Abkommen und Sonderregeln entscheiden. Keine Steuerberatung.' if not en else
         'Country figures for orientation: top income tax rate and reference rate for capital income. Your personal situation, allowances, treaties and special rules decide. Not tax advice.'))

CSS = ('<style>.txgrid{display:grid;gap:14px;margin-top:14px}.txgrid.two{grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}.txc{border:1px solid var(--line);border-radius:14px;padding:14px;background:var(--card2,rgba(255,255,255,.03))}.txc h3{margin:0 0 8px}'
       '.txc .res{margin:8px 0}.txtab{width:100%;border-collapse:collapse;font-size:.92rem}.txtab th,.txtab td{text-align:left;padding:8px 6px;border-bottom:1px solid var(--line)}.txtab td.n{white-space:nowrap}.txreg{margin-top:22px}</style>')

def table(d, en, codes, base):
    L = 1 if en else 0
    rows = ''.join('<tr><td><a href="%s/%s/">%s</a></td><td class="n">%s</td><td class="n">%s</td></tr>' % (base, (d['slugs_en'] if en else d['slugs'])[c], esc(d['countries'][c]['name'][L]), esc(d['countries'][c]['incomeDisplay'][L]), esc(d['countries'][c]['capitalDisplay'][L]))
                   for c in sorted(codes, key=lambda c: d['countries'][c]['name'][L]))
    h = ('Land', 'Einkommensteuer (Spitzensatz)', 'Kapitalerträge') if not en else ('Country', 'Income tax (top rate)', 'Capital income')
    return '<table class="txtab"><thead><tr><th>%s</th><th>%s</th><th>%s</th></tr></thead><tbody>%s</tbody></table>' % (h + (rows,))

def shell(en, url, alt, title, desc, eyebrow, h1, lead, calc, body, faqs, crumbs):
    L = 1 if en else 0
    de_url, en_url = (alt, url) if en else (url, alt)
    faq_ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faqs]}
    app_ld = {'@context': 'https://schema.org', '@type': 'WebApplication', 'name': h1, 'url': url, 'applicationCategory': 'FinanceApplication', 'operatingSystem': 'Web', 'inLanguage': 'en' if en else 'de',
              'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'EUR'}, 'description': desc}
    bc_ld = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(crumbs)]}
    other = en_url if not en else de_url
    langjs = ("<script>(function(){var K='geld-kompass-lang',q=new URLSearchParams(location.search).get('lang'),w=q;if(new URLSearchParams(location.search).get('embed')==='1')return;"
              "if(q==='de'||q==='en'){try{localStorage.setItem(K,q);}catch(e){}}else{try{w=localStorage.getItem(K);}catch(e){}}"
              "if((w==='de'||w==='en')&&w!=='%s')location.replace('%s'+location.search+location.hash);})();</script>" % ('en' if en else 'de', other.replace(BASE, '/')))
    faqh = 'Frequently asked questions' if en else 'Häufige Fragen'
    cta = ('<div class="cta"><a href="/app/?tour=plus%s"><i>%s</i><div><b>%s</b><span>%s</span></div></a><a href="%s"><i>%s</i><div><b>%s</b><span>%s</span></div></a></div>' % (
        '&lang=en' if en else '', LOGO,
        'Count your days per country automatically' if en else 'Tage je Land automatisch zählen',
        'The nomad mode in Money Compass Plus counts your days per country, Schengen 90/180 and your costs per country. See an example.' if en else 'Der Nomaden-Modus in Geld-Kompass Plus zählt deine Tage je Land, Schengen 90/180 und deine Kosten pro Land. Beispiel ansehen.',
        '/en/expat-money-app/' if en else '/auswandern-finanzen/', LOGO,
        'Money app for expats and nomads' if en else 'Finanz-App für Auswanderer und Nomaden',
        'Budget in 50+ currencies, freedom days and debt plan. Free, no bank account needed.' if en else 'Budget in über 50 Währungen, Freiheitstage und Schulden-Plan. Kostenlos, ohne Bankkonto.'))
    nav = ('<nav class="crumbs" aria-label="Breadcrumb">' + ' › '.join('<a href="%s">%s</a>' % (u.replace(BASE, '/'), esc(n)) for n, u in crumbs[:-1]) + '</nav>')
    return f"""<!doctype html>
<html lang="{'en' if en else 'de'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
{langjs}
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="de" href="{de_url}">
<link rel="alternate" hreflang="en" href="{en_url}">
<link rel="alternate" hreflang="x-default" href="{de_url}">
<meta name="theme-color" content="#0E1730">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="{'en_GB' if en else 'de_DE'}">
<link rel="stylesheet" href="/rechner/rechner.css">
<link rel="stylesheet" href="/arbeitsbuch/hinweise.css">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="icon" type="image/png" sizes="32x32" href="/icons/favicon-32.png?v=3">
<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png?v=3">
<script type="application/ld+json">{json.dumps(app_ld, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(faq_ld, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(bc_ld, ensure_ascii=False)}</script>
{CSS}
<link rel=stylesheet href=/visuals.css?v20261104a><script src=/visuals.js?v20261104a></script></head>
<body>
<header class="top"><div class="wrap"><a class="logo" href="{'/?lang=en' if en else '/'}">{LOGO}<b>{'Money <span>Compass</span>' if en else 'Geld-<span>Kompass</span> <span class="pro">Pro</span>'}</b></a></div></header>
<main class="wrap">
{nav}
<div class="eyebrow">{esc(eyebrow)}</div>
<h1>{esc(h1)}</h1>
<p class="lead">{esc(lead)}</p>
<section class="card calc" aria-label="{'Calculator' if en else 'Rechner'}">{calc}</section>
{cta}
{body}
<h2>{faqh}</h2>
{''.join('<details><summary>%s</summary><p>%s</p></details>' % (esc(q), esc(a)) for q, a in faqs)}
<div data-partner="newsletter" hidden></div>
</main>
<footer><div class="wrap"></div></footer>
<script src="/share-state.js"></script>
<script src="/rechner/rechner.js"></script>
<script src="/rechner/steuern-nach-wohnsitz/steuern.js?v=1"></script>
<script src="/partner.js" defer></script>
<!-- Cloudflare Web Analytics (ohne Cookies, keine personenbezogenen Daten) --><script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token": "d5b51a031e8c4e26b08ad199a6bfd2da"}}'></script>
</body>
</html>
"""

def hub(d, en):
    L = 1 if en else 0
    n = len(d['countries'])
    url = BASE + (EN_DIR if en else DE_DIR) + '/'
    alt = BASE + (DE_DIR if en else EN_DIR) + '/'
    base = '/' + (EN_DIR if en else DE_DIR)
    regs = ''.join('<div class="txreg"><h3>%s</h3>%s</div>' % (REG_NAME[r][L], table(d, en, [c for c in d['countries'] if REG_OF.get(c) == r], base)) for r in REGION)
    chk = d['checked']
    if en:
        title = 'Taxes by Residence: Compare Income and Capital Gains Tax in %d Countries | Money Compass Pro' % n
        desc = 'Free tax comparison for expats and digital nomads: top income tax rate and capital gains tax in %d countries, with sources (checked %s). Thailand, Portugal, Dubai, Georgia and more.' % (n, chk)
        body = ('<h2>How to read the figures</h2><p>For every country you see two reference values: the top rate of income tax and a reference rate for capital income such as gains, dividends or interest. The calculator multiplies your amounts by these rates. That gives an upper estimate, not your actual tax: allowances, progressive brackets, social security, tax treaties and special regimes can change the result a lot.</p>'
                '<h2>Residence, 183 days and double taxation</h2><p>Where you pay tax usually depends on your tax residence, not your passport. Many countries look at a permanent home, your centre of vital interests or around 183 days of presence, but the rules differ from country to country. Leaving one country does not automatically end your tax liability there. Double tax treaties decide which country may tax which income.</p>'
                '<h2>For digital nomads</h2><p>If you move often, write down your days per country. Many tax questions start with: where did you spend how many days, and where is your home? Some countries only tax foreign income when it is brought into the country, others tax worldwide income from the first day of residence.</p>'
                '<h2>All %d countries at a glance</h2>%s<p class="note">Data: public country summaries, mainly PwC Worldwide Tax Summaries and official tax authorities, checked %s. Orientation only, not tax advice.</p>') % (n, regs, chk)
        faqs = [('Where do I have to pay tax as a digital nomad?', 'Usually where you are tax resident. Many countries use criteria such as a permanent home, centre of vital interests or around 183 days of presence. Without a clear residence, several countries may claim taxes. Get advice for your situation.'),
                ('Is the figure shown my actual tax?', 'No. The calculator uses the top income tax rate and a reference rate for capital income. Your actual tax is usually lower because of allowances and progressive brackets.'),
                ('Which countries have low taxes on capital gains?', 'Several countries, for example some in the Gulf region or in Asia, tax private capital gains low or not at all. Use the table and the sources linked for each country, and check the rules for your income type.'),
                ('How current is the data?', 'Each country shows its check date and sources. The current data was checked on %s.' % chk)]
        return shell(True, url, alt, title, desc, 'Expats & taxes', 'Taxes by residence: compare income and capital gains tax in %d countries' % n,
                     'Choose your country of residence and a second country. You see the top income tax rate, the rate for capital income and a rough upper estimate for your own amounts, with sources for every country.',
                     calc_html(True), body, faqs, [('Money Compass Pro', BASE + '?lang=en'), ('Calculators', BASE + 'en/calculators/'), ('Taxes by residence', url)])
    title = 'Steuern nach Wohnsitz: Einkommensteuer und Kapitalerträge in %d Ländern vergleichen | Geld-Kompass Pro' % n
    desc = 'Kostenloser Steuervergleich für Auswanderer und digitale Nomaden: Spitzensteuersatz und Steuer auf Kapitalerträge in %d Ländern, mit Quellen (geprüft %s). Thailand, Portugal, Dubai, Georgien und mehr.' % (n, chk)
    body = ('<h2>So liest du die Werte</h2><p>Für jedes Land siehst du zwei Referenzwerte: den Spitzensatz der Einkommensteuer und einen Referenzsatz für Kapitalerträge wie Kursgewinne, Dividenden oder Zinsen. Der Rechner multipliziert deine Beträge mit diesen Sätzen. Das ergibt eine Obergrenze, nicht deine tatsächliche Steuer: Freibeträge, Stufentarif, Sozialabgaben, Doppelbesteuerungsabkommen und Sonderregeln können das Ergebnis stark verändern.</p>'
            '<h2>Wohnsitz, 183 Tage und Doppelbesteuerung</h2><p>Wo du Steuern zahlst, hängt meist von deinem steuerlichen Wohnsitz ab, nicht von deinem Pass. Viele Länder schauen auf eine ständige Wohnung, den Mittelpunkt deiner Lebensinteressen oder rund 183 Tage Aufenthalt, die Regeln unterscheiden sich aber von Land zu Land. Wer Deutschland verlässt, ist nicht automatisch dort steuerfrei. Doppelbesteuerungsabkommen regeln, welches Land welche Einkünfte besteuern darf.</p>'
            '<h2>Für digitale Nomaden</h2><p>Wer oft das Land wechselt, sollte seine Tage je Land festhalten. Viele Steuerfragen beginnen mit: Wo warst du wie viele Tage, und wo ist dein Zuhause? Manche Länder besteuern ausländische Einkünfte nur, wenn sie ins Land gebracht werden, andere ab dem ersten Tag des Wohnsitzes weltweit.</p>'
            '<h2>Alle %d Länder im Überblick</h2>%s<p class="note">Daten: öffentliche Länderübersichten, vor allem PwC Worldwide Tax Summaries und offizielle Steuerbehörden, geprüft am %s. Orientierung, keine Steuerberatung.</p>') % (n, regs, chk)
    faqs = [('Wo muss ich als digitaler Nomade Steuern zahlen?', 'In der Regel dort, wo du steuerlich ansässig bist. Viele Länder nutzen Merkmale wie eine ständige Wohnung, den Lebensmittelpunkt oder rund 183 Tage Aufenthalt. Ohne klaren Wohnsitz können mehrere Länder Steuern verlangen. Lass dich für deine Lage beraten.'),
            ('Ist der angezeigte Betrag meine tatsächliche Steuer?', 'Nein. Der Rechner nutzt den Spitzensatz der Einkommensteuer und einen Referenzsatz für Kapitalerträge. Deine tatsächliche Steuer ist wegen Freibeträgen und Stufentarif meist niedriger.'),
            ('Welche Länder besteuern Kapitalerträge niedrig?', 'Mehrere Länder, etwa am Golf oder in Asien, besteuern private Kursgewinne niedrig oder gar nicht. Nutze die Tabelle und die verlinkten Quellen je Land und prüfe die Regeln für deine Ertragsart.'),
            ('Wie aktuell sind die Daten?', 'Jedes Land zeigt sein Prüfdatum und die Quellen. Der aktuelle Datenstand wurde am %s geprüft.' % chk),
            ('Bin ich nach dem Wegzug aus Deutschland automatisch steuerfrei?', 'Nicht automatisch. Behältst du zum Beispiel eine Wohnung in Deutschland, kann die unbeschränkte Steuerpflicht weiter bestehen. Auch Einkünfte aus Deutschland, etwa Mieten, können dort steuerpflichtig bleiben.')]
    return shell(False, url, alt, title, desc, 'Auswandern & Steuern', 'Steuern nach Wohnsitz: Einkommensteuer und Kapitalerträge in %d Ländern vergleichen' % n,
                 'Wähle dein Wohnsitz-Land und ein Vergleichsland. Du siehst den Spitzensatz der Einkommensteuer, den Satz für Kapitalerträge und eine grobe Obergrenze für deine eigenen Beträge, mit Quellen für jedes Land.',
                 calc_html(False), body, faqs, [('Geld-Kompass Pro', BASE), ('Rechner', BASE + 'rechner/'), ('Steuern nach Wohnsitz', url)])

def country(d, c, en):
    L = 1 if en else 0
    x = d['countries'][c]; name = x['name'][L]
    sl, sl_en = d['slugs'][c], d['slugs_en'][c]
    url = BASE + (EN_DIR + '/' + sl_en if en else DE_DIR + '/' + sl) + '/'
    alt = BASE + (DE_DIR + '/' + sl if en else EN_DIR + '/' + sl_en) + '/'
    base = '/' + (EN_DIR if en else DE_DIR)
    lf = lambda v: v if re.search(r'\d', v) else v[:1].lower() + v[1:]
    inc, cap, note, chk = lf(x['incomeDisplay'][L]), lf(x['capitalDisplay'][L]), x['note'][L], x['checked']
    near = [k for k in d['countries'] if REG_OF.get(k) == REG_OF.get(c) and k != c][:9]
    home = ['DE', 'AT', 'CH'] if not en else ['GB', 'US', 'DE']
    cmp_codes = [c] + [k for k in home if k != c] + [k for k in near if k not in home][:5]
    srcs = ''.join('<li><a href="%s" target="_blank" rel="noopener nofollow">%s</a></li>' % (esc(s['url']), esc(src_label(s['label'], en))) for s in x['sources'])
    cmp_default = '' if en else ('AT' if c == 'DE' else 'DE')
    if en:
        title = 'Taxes in %s for Expats and Digital Nomads (%s) | Money Compass Pro' % (name, chk[:4])
        desc = '%s: income tax %s, capital income %s. Country figures with sources (checked %s), calculator for your own amounts and comparison with other countries.' % (name, inc, cap, chk)
        body = ('<h2>Taxes in %s at a glance</h2><div class="res"><div><span>Income tax (top rate)</span><b class="gold">%s</b></div><div><span>Capital income (reference)</span><b class="gold">%s</b></div><div><span>Checked</span><b>%s</b></div></div>'
                '<p>%s</p><h3>Sources</h3><ul>%s</ul>'
                '<h2>%s compared</h2>%s'
                '<h2>Before you move to %s</h2><ul><li>Clarify where you will be tax resident and whether your previous country still treats you as resident.</li><li>Check how %s taxes foreign income, and whether only money brought into the country is taxed.</li><li>Look for a double tax treaty between %s and the countries your income comes from.</li><li>Keep a record of your days per country, flights and rental contracts.</li><li>Get tax advice for your situation before you decide.</li></ul>'
                '<p><a href="%s/">All %d countries: taxes by residence</a></p>') % (name, esc(inc), esc(cap), esc(chk), esc(note), srcs, name, table(d, True, cmp_codes, base), name, name, name, base, len(d['countries']))
        faqs = [('How high is income tax in %s?' % name, 'The top income tax rate in %s is %s. %s' % (name, inc, note)),
                ('How is capital income taxed in %s?' % name, 'The reference value for capital income in %s is %s. Allowances and the type of income (gains, dividends, interest) matter.' % (name, cap)),
                ('When do I become tax resident in %s?' % name, 'That depends on the rules of %s, often on a permanent home, the centre of vital interests or around 183 days of presence. Check the official sources and get advice for your situation.' % name)]
        return shell(True, url, alt, title, desc, 'Taxes by residence · ' + name, 'Taxes in %s: income tax %s, capital income %s' % (name, inc, cap),
                     'Country figures for %s with sources, a calculator for your own amounts and a comparison with other countries. Orientation for expats and digital nomads, not tax advice.' % name,
                     calc_html(True, c, cmp_default), body, faqs, [('Money Compass Pro', BASE + '?lang=en'), ('Taxes by residence', BASE + EN_DIR + '/'), (name, url)])
    title = 'Steuern in %s für Auswanderer und Nomaden (%s) | Geld-Kompass Pro' % (name, chk[:4])
    desc = '%s: Einkommensteuer %s, Kapitalerträge %s. Länderwerte mit Quellen (geprüft %s), Rechner für deine Beträge und Vergleich mit Deutschland, Österreich und der Schweiz.' % (name, inc, cap, chk)
    body = ('<h2>Steuern in %s auf einen Blick</h2><div class="res"><div><span>Einkommensteuer (Spitzensatz)</span><b class="gold">%s</b></div><div><span>Kapitalerträge (Referenz)</span><b class="gold">%s</b></div><div><span>Geprüft</span><b>%s</b></div></div>'
            '<p>%s</p><h3>Quellen</h3><ul>%s</ul>'
            '<h2>%s im Vergleich</h2>%s'
            '<h2>Bevor du nach %s ziehst</h2><ul><li>Kläre, wo du steuerlich ansässig wirst und ob dein bisheriges Land dich weiter als ansässig sieht.</li><li>Prüfe, wie %s ausländische Einkünfte besteuert und ob nur ins Land gebrachtes Geld zählt.</li><li>Schau, ob es ein Doppelbesteuerungsabkommen zwischen %s und den Ländern gibt, aus denen dein Einkommen kommt.</li><li>Halte deine Tage je Land, Flüge und Mietverträge fest.</li><li>Lass dich vor der Entscheidung steuerlich beraten.</li></ul>'
            '<p><a href="%s/">Alle %d Länder: Steuern nach Wohnsitz</a></p>') % (name, esc(inc), esc(cap), esc(chk), esc(note), srcs, name, table(d, False, cmp_codes, base), name, name, name, base, len(d['countries']))
    faqs = [('Wie hoch ist die Einkommensteuer in %s?' % name, 'Der Spitzensatz der Einkommensteuer in %s liegt bei %s. %s' % (name, inc, note)),
            ('Wie werden Kapitalerträge in %s besteuert?' % name, 'Der Referenzwert für Kapitalerträge in %s liegt bei %s. Freibeträge und die Ertragsart (Kursgewinne, Dividenden, Zinsen) spielen eine Rolle.' % (name, cap)),
            ('Ab wann bin ich in %s steuerpflichtig?' % name, 'Das hängt von den Regeln in %s ab, oft von einer ständigen Wohnung, dem Lebensmittelpunkt oder rund 183 Tagen Aufenthalt. Prüfe die offiziellen Quellen und lass dich für deine Lage beraten.' % name)]
    return shell(False, url, alt, title, desc, 'Steuern nach Wohnsitz · ' + name, 'Steuern in %s: Einkommensteuer %s, Kapitalerträge %s' % (name, inc, cap),
                 'Länderwerte für %s mit Quellen, ein Rechner für deine eigenen Beträge und der Vergleich mit anderen Ländern. Orientierung für Auswanderer und digitale Nomaden, keine Steuerberatung.' % name,
                 calc_html(False, c, cmp_default), body, faqs, [('Geld-Kompass Pro', BASE), ('Steuern nach Wohnsitz', BASE + DE_DIR + '/'), (name, url)])

def main():
    d = load()
    pub = dict(d); json.dump(pub, open(os.path.join(ROOT, 'data/tax-residence.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    n = 0
    for en, base, slugs in ((False, DE_DIR, d['slugs']), (True, EN_DIR, d['slugs_en'])):
        os.makedirs(os.path.join(ROOT, base), exist_ok=True)
        open(os.path.join(ROOT, base, 'index.html'), 'w').write(hub(d, en)); n += 1
        for c, s in slugs.items():
            os.makedirs(os.path.join(ROOT, base, s), exist_ok=True)
            open(os.path.join(ROOT, base, s, 'index.html'), 'w').write(country(d, c, en)); n += 1
    print('ok', n, 'Seiten')

if __name__ == '__main__':
    main()
