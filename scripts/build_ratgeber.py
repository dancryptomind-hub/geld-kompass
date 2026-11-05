#!/usr/bin/env python3
"""Ratgeber „Sparen in Freiheitstagen“: Handy & Internet, Strom & Gas, Versicherungen.
Jede Seite: Erklärtext, Mini-Rechner (Jahreskosten, Arbeitszeit, Ersparnis in Freiheitstagen), Partner-Platz (partner.js, nur sichtbar mit bestätigtem Link), FAQ.
Erzeugt /ratgeber/<slug>/index.html und /ratgeber/index.html."""
import json, os, html
BASE = 'https://geld-kompass.com/'
LOGO = '<img class="gk-logo" src="/icons/logo-badge.webp?v=3" alt="" aria-hidden="true" width="34" height="34">'
VIS = '<link rel=stylesheet href=/visuals.css?v20261104a><script src=/visuals.js?v20261104a></script>'
esc = html.escape

PAGES = [
 dict(slug='handy-internet-sparen', partner='mobilfunk', short='Handy & Internet günstiger', teaser='Was dich dein Tarif in Arbeitszeit kostet und wie du wechselst',
  title='Handy und Internet günstiger: so viel Lebenszeit kostet dein Tarif', h1='Handy und Internet: Was kostet dich dein Tarif wirklich?',
  desc='Handy- und Internettarif in Arbeitsstunden und Freiheitstage umrechnen, Sparpotenzial sehen und Schritt für Schritt wechseln. Kostenlos, ohne Anmeldung.',
  eb='Ratgeber · Laufende Kosten', amount=85, label='Handy und Internet zusammen pro Monat (€)',
  lead='Handy und Internet laufen jeden Monat still mit. Rechne hier aus, wie viele Arbeitsstunden dein Tarif im Jahr frisst und was ein günstigerer Vertrag dir an Freiheit zurückgibt.',
  body=[('Warum sich ein Blick lohnt', 'Viele Verträge laufen nach der Mindestlaufzeit einfach weiter, oft zu einem Preis, der für Neukunden längst günstiger ist. Datenvolumen und Leistungen passen häufig nicht mehr zum echten Verbrauch.'),
        ('So wechselst du in vier Schritten', '1. Prüfe auf deiner letzten Rechnung, wie viel Datenvolumen du wirklich nutzt. 2. Vergleiche Tarife mit genau diesem Bedarf. 3. Achte auf den Preis nach Aktionsende und die Laufzeit. 4. Kündige den alten Vertrag fristgerecht, die Rufnummer kannst du mitnehmen.'),
        ('Gut zu wissen', 'In Deutschland lassen sich Laufzeitverträge für Handy und Internet nach Ablauf der Mindestlaufzeit mit einer Frist von einem Monat kündigen. Online abgeschlossene Verträge müssen sich über einen Kündigungsbutton auf der Website des Anbieters kündigen lassen.')],
  faq=[('Verliere ich meine Rufnummer?', 'Nein. Die Rufnummer kannst du zum neuen Anbieter mitnehmen. Den Wechsel stößt in der Regel der neue Anbieter an.'),
       ('Ist der günstigste Tarif immer der beste?', 'Nicht unbedingt. Entscheidend sind Netzabdeckung an deinen Orten, Datenvolumen und der Preis nach Aktionsende, nicht nur der Einstiegspreis.'),
       ('Wie oft sollte ich vergleichen?', 'Spätestens zum Ende der Mindestlaufzeit und danach etwa einmal im Jahr.')]),
 dict(slug='strom-gas-wechseln', partner='energie', short='Strom & Gas wechseln', teaser='Grundversorgung, Bonusfallen und dein Sparpotenzial in Freiheitstagen',
  title='Strom und Gas wechseln: so viel Freiheit steckt in deinem Abschlag', h1='Strom und Gas: Wie viel Freiheit steckt in deinem Abschlag?',
  desc='Strom- und Gasabschlag in Arbeitszeit und Freiheitstage umrechnen, Grundversorgung erkennen und sicher wechseln. Kostenloser Rechner ohne Anmeldung.',
  eb='Ratgeber · Laufende Kosten', amount=95, label='Abschlag für Strom und Gas pro Monat (€)',
  lead='Der monatliche Abschlag wirkt klein, im Jahr ist er oft einer der größten festen Posten. Hier siehst du, was er dich an Arbeitszeit kostet und was ein günstigerer Tarif bringt.',
  body=[('Grundversorgung erkennen', 'Wer nie gewechselt hat oder nach dem Umzug nichts unternommen hat, ist oft in der Grundversorgung des örtlichen Anbieters. Sie ist sicher, aber häufig teurer als ein Sondervertrag. Ein Blick auf die Jahresabrechnung zeigt, welchen Tarif du hast.'),
        ('Bonusfallen vermeiden', 'Neukundenboni senken den Preis oft nur im ersten Jahr. Vergleiche deshalb auch den Preis ab dem zweiten Jahr und achte auf eine kurze Laufzeit und eine Preisgarantie.'),
        ('Sicher wechseln', 'Die Versorgung bricht beim Wechsel nicht ab. Der neue Anbieter übernimmt in der Regel die Kündigung beim alten. Bei einer Preiserhöhung hast du ein Sonderkündigungsrecht.')],
  faq=[('Kann mir beim Wechsel der Strom ausgehen?', 'Nein. Kommt ein Wechsel nicht zustande, versorgt dich weiterhin der Grundversorger.'),
       ('Wie lange dauert ein Wechsel?', 'Meist einige Wochen. Den Ablauf übernimmt in der Regel der neue Anbieter.'),
       ('Was brauche ich dafür?', 'Zählernummer, aktuellen Zählerstand und deinen ungefähren Jahresverbrauch aus der letzten Abrechnung.')]),
 dict(slug='versicherungen-pruefen', partner='versicherung', short='Versicherungen prüfen', teaser='Was du wirklich brauchst und was dich nur Lebenszeit kostet',
  title='Versicherungen prüfen: welche du brauchst und was sie dich an Lebenszeit kosten', h1='Versicherungen: Was brauchst du wirklich?',
  desc='Versicherungsbeiträge in Arbeitszeit und Freiheitstage umrechnen, wichtige von überflüssigen Policen unterscheiden und Doppelversicherungen finden.',
  eb='Ratgeber · Laufende Kosten', amount=70, label='Alle Versicherungsbeiträge pro Monat (€)',
  lead='Gute Versicherungen schützen deine Festung, überflüssige kosten nur Lebenszeit. Rechne aus, was deine Beiträge im Jahr an Arbeitszeit bedeuten und wo du sparen kannst, ohne Schutz zu verlieren.',
  body=[('Zuerst die großen Risiken', 'Wichtig sind Versicherungen gegen Risiken, die dich finanziell ruinieren könnten: vor allem eine private Haftpflichtversicherung und je nach Lebenslage eine Absicherung gegen Berufsunfähigkeit. Verbraucherschützer nennen diese Reihenfolge seit Jahren.'),
        ('Oft verzichtbar', 'Kleine Schäden, die du selbst bezahlen könntest, musst du meist nicht versichern, zum Beispiel Handy- oder Brillenversicherungen. Prüfe auch, ob du denselben Schutz doppelt hast, etwa über Kreditkarte oder Partnertarif.'),
        ('So sparst du ohne Schutzverlust', 'Selbstbeteiligung prüfen, jährliche statt monatliche Zahlung wählen, alte Verträge mit neuen Tarifen vergleichen und Kündigungsfristen notieren. Bei einer Beitragserhöhung hast du oft ein Sonderkündigungsrecht.')],
  faq=[('Welche Versicherung ist am wichtigsten?', 'Für fast alle die private Haftpflicht, weil Schäden an anderen schnell sehr teuer werden. Danach hängt es von deiner Lebenslage ab.'),
       ('Kann ich einfach kündigen?', 'Meist zum Ende der Vertragslaufzeit mit Frist, bei Beitragserhöhung oft auch außerordentlich. Kündige einen wichtigen Schutz erst, wenn der neue Vertrag steht.'),
       ('Ist das eine Versicherungsberatung?', 'Nein. Die Seite gibt allgemeine Orientierung. Welcher Schutz zu dir passt, hängt von deiner Situation ab.')]),
 dict(slug='internet-anschluss-guenstiger', partner='internet', short='Internetanschluss günstiger', teaser='DSL, Kabel oder Glasfaser: was du brauchst und was es dich kostet',
  title='Internetanschluss günstiger: DSL, Kabel, Glasfaser in Freiheitstagen gerechnet', h1='Internetanschluss: Zahlst du für Tempo, das du nicht nutzt?',
  desc='Internetanschluss in Arbeitszeit und Freiheitstage umrechnen, passende Geschwindigkeit wählen und nach der Mindestlaufzeit wechseln. Kostenloser Rechner.',
  eb='Ratgeber · Laufende Kosten', amount=45, label='Internetanschluss pro Monat (€)',
  lead='Der Internetanschluss läuft jahrelang mit, oft zu einem Preis, der nach dem ersten Jahr steigt. Rechne aus, was er dich an Arbeitszeit kostet und was ein Wechsel bringt.',
  body=[('Welches Tempo brauchst du wirklich?', 'Viele Haushalte buchen mehr Geschwindigkeit, als sie nutzen. Wie viel du brauchst, hängt davon ab, wie viele Personen gleichzeitig streamen, arbeiten oder spielen. Prüfe außerdem, was an deiner Adresse verfügbar ist: DSL, Kabel oder Glasfaser.'),
        ('Preis nach dem ersten Jahr', 'Lockangebote gelten oft nur für die ersten Monate. Vergleiche den Durchschnittspreis über die ganze Laufzeit und achte auf Einrichtungs- und Routerkosten.'),
        ('Zu langsam? Du hast Rechte', 'Liefert dein Anbieter dauerhaft deutlich weniger als vereinbart, kannst du das mit der Breitbandmessung der Bundesnetzagentur nachweisen und den Preis mindern oder kündigen. Nach der Mindestlaufzeit ist der Vertrag monatlich kündbar.')],
  faq=[('Bin ich nach dem Wechsel offline?', 'In der Regel kaum. Der neue Anbieter stimmt den Umschalttermin mit dem alten ab, die Versorgung darf dabei nicht länger als einen Arbeitstag unterbrochen sein.'),
       ('Lohnt sich Glasfaser?', 'Wenn sie verfügbar ist und der Preis passt, ist sie zukunftssicher. Entscheidend bleibt, was du wirklich brauchst und was du dafür im Monat zahlst.'),
       ('Kann ich meine Festnetznummer behalten?', 'Ja, die Rufnummer kannst du zum neuen Anbieter mitnehmen.')]),
 dict(slug='kfz-versicherung-wechseln', partner='kfz', short='Kfz-Versicherung wechseln', teaser='Stichtag 30. November: so viel kostet dich dein Auto an Lebenszeit',
  title='Kfz-Versicherung wechseln: Stichtag 30. November, gerechnet in Freiheitstagen', h1='Kfz-Versicherung: Wie viel Lebenszeit kostet dich dein Auto?',
  desc='Kfz-Versicherung in Arbeitszeit und Freiheitstage umrechnen, Stichtag 30. November beachten und mit wenigen Stellschrauben sparen. Kostenloser Rechner.',
  eb='Ratgeber · Laufende Kosten', amount=60, label='Kfz-Versicherung pro Monat (€)',
  lead='Die meisten Kfz-Versicherungen laufen bis zum Jahresende und lassen sich bis zum 30. November kündigen. Rechne aus, was dein Beitrag an Arbeitszeit kostet und was ein Wechsel bringt.',
  body=[('Der Stichtag', 'Bei den meisten Verträgen endet das Versicherungsjahr am 31. Dezember. Die ordentliche Kündigung muss dann in der Regel bis zum 30. November beim Versicherer sein. Prüfe das Datum in deinen Unterlagen.'),
        ('Sonderkündigung', 'Erhöht der Versicherer den Beitrag ohne bessere Leistung, kannst du meist innerhalb eines Monats nach der Mitteilung kündigen. Auch nach einem Schaden besteht oft ein Sonderkündigungsrecht.'),
        ('Stellschrauben', 'Realistische Kilometerleistung angeben, Fahrerkreis eingrenzen, Selbstbeteiligung prüfen, jährlich statt monatlich zahlen und prüfen, ob du Teilkasko oder Vollkasko für dein Auto wirklich brauchst.')],
  faq=[('Verliere ich meinen Schadenfreiheitsrabatt?', 'Nein. Deine Schadenfreiheitsklasse nimmst du zum neuen Versicherer mit.'),
       ('Muss ich die alte Versicherung selbst kündigen?', 'Ja, in der Regel kündigst du selbst. Viele Vergleichs- und Versicherungsportale bieten dafür einen Kündigungsservice an.'),
       ('Bin ich zwischendurch unversichert?', 'Nein, wenn der neue Vertrag nahtlos zum 1. Januar beginnt. Die elektronische Versicherungsbestätigung bekommst du vom neuen Versicherer.')]),
 dict(slug='girokonto-gebuehren-sparen', partner='girokonto', short='Kontogebühren sparen', teaser='Was dich dein Girokonto im Jahr kostet und wie der Wechsel leicht geht',
  title='Girokonto: Kontoführungsgebühren sparen und einfach wechseln', h1='Girokonto: Was kosten dich deine Kontogebühren an Lebenszeit?',
  desc='Kontoführungsgebühren in Arbeitszeit und Freiheitstage umrechnen, Bedingungen kostenloser Konten verstehen und mit Kontowechselhilfe wechseln.',
  eb='Ratgeber · Laufende Kosten', amount=8, label='Kontoführung und Kartengebühren pro Monat (€)',
  lead='Ein paar Euro im Monat wirken harmlos. Über Jahre werden daraus spürbare Beträge. Rechne aus, was dein Konto dich kostet und was ein Wechsel bringt.',
  body=[('Wo die Kosten stecken', 'Neben der monatlichen Kontoführung kosten oft auch die Girocard, die Kreditkarte, Überweisungen auf Papier oder Abhebungen an fremden Automaten Geld. Ein Blick in den Kontoauszug oder das Preisverzeichnis zeigt alles.'),
        ('Kostenlos mit Bedingungen', 'Viele Konten sind nur unter Bedingungen kostenlos, zum Beispiel mit einem regelmäßigen Geldeingang. Prüfe, ob du die Bedingungen dauerhaft erfüllst.'),
        ('Wechseln ist einfacher als gedacht', 'Banken müssen beim Kontowechsel helfen: Daueraufträge und Lastschriften können auf Wunsch übertragen und Zahlungspartner informiert werden. Plane trotzdem eine Übergangszeit mit beiden Konten ein.')],
  faq=[('Wie lange dauert ein Kontowechsel?', 'Mit der gesetzlichen Kontowechselhilfe in der Regel wenige Wochen.'),
       ('Was ist mit meinem Gehalt?', 'Gib die neue IBAN deinem Arbeitgeber oder lass die Kontowechselhilfe die Zahlungspartner informieren.'),
       ('Reicht ein Konto?', 'Für viele ja. Manche nutzen ein zweites Konto für Rücklagen oder Reisen, zum Beispiel mit Tagesgeld oder einer Karte ohne Auslandsgebühren.')]),
]

CSS = """.rg-calc .grid{grid-template-columns:1fr 1fr 1fr}@media(max-width:760px){.rg-calc .grid{grid-template-columns:1fr}}
.rg-body h2{margin-top:30px}.rg-steps{counter-reset:s}.calc label.rg-sl{display:flex!important;flex-direction:row;align-items:center;gap:12px;margin-top:14px;text-align:left}.calc .rg-sl input{flex:1;padding:0;border:0;background:none;accent-color:#c99227;min-height:28px}.rg-sl b{min-width:3em;text-align:right;color:var(--gold)}"""

def page(p):
    url = BASE + 'ratgeber/' + p['slug'] + '/'
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p['faq']]}
    body = ''.join('<h2>%s</h2><p>%s</p>' % (esc(h), esc(t)) for h, t in p['body'])
    faq = ''.join('<details><summary>%s</summary><p>%s</p></details>' % (esc(q), esc(a)) for q, a in p['faq'])
    more = ''.join('<a href="/ratgeber/%s/">%s<small>%s</small></a>' % (o['slug'], esc(o['short']), esc(o['teaser'])) for o in PAGES if o is not p)
    js = """(function(){var $=function(i){return document.getElementById(i);},f=new Intl.NumberFormat('de-DE',{style:'currency',currency:'EUR',maximumFractionDigits:0}),n1=new Intl.NumberFormat('de-DE',{maximumFractionDigits:1});
function v(i){var x=parseFloat(String($(i).value).replace(',','.'));return isFinite(x)&&x>0?x:0;}
function run(){var m=v('rgM'),inc=v('rgInc'),sp=v('rgSp'),pc=v('rgP')/100,y=m*12,hour=inc>0?inc/(40*52/12):0,day=sp>0?sp*12/365:0,sv=y*pc;$('rgPl').textContent=Math.round(pc*100)+' %';
 var h=hour>0?y/hour:0,wt=h<=0?'–':(h<12?n1.format(h)+' Std.':n1.format(h/8)+' Arbeitstage');
 $('rgBig').textContent=f.format(y)+' im Jahr';$('rgRes').innerHTML='<div><span>Dafür arbeitest du</span><b>'+wt+'</b></div><div><span>'+Math.round(pc*100)+' % günstiger</span><b class="pos">+'+f.format(sv)+' / Jahr</b></div><div><span>Das sind</span><b class="gold">'+(day>0?n1.format(sv/day)+' Freiheitstage':'–')+'</b></div><div><span>In 10 Jahren angelegt (5 %)</span><b class="pos">'+f.format(sv*((Math.pow(1.05,10)-1)/0.05))+'</b></div>';}
['rgM','rgInc','rgSp','rgP'].forEach(function(i){$(i).addEventListener('input',run);});run();})();"""
    return f"""<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(p['title'])} | Geld-Kompass Pro</title><meta name="description" content="{esc(p['desc'])}">
<link rel="canonical" href="{url}"><meta name="theme-color" content="#0E1730">
<meta property="og:type" content="article"><meta property="og:title" content="{esc(p['title'])}"><meta property="og:description" content="{esc(p['desc'])}"><meta property="og:url" content="{url}"><meta property="og:locale" content="de_DE">
<link rel="stylesheet" href="/rechner/rechner.css"><link rel="manifest" href="/manifest.webmanifest">
<link rel="icon" type="image/png" sizes="32x32" href="/icons/favicon-32.png?v=3"><link rel="apple-touch-icon" href="/icons/apple-touch-icon.png?v=3">
<script type="application/ld+json">{json.dumps(faq_ld, ensure_ascii=False)}</script>
<style>{CSS}</style>
{VIS}</head><body>
<header class="top"><div class="wrap"><a class="logo" href="/">{LOGO}<b>Geld-<span>Kompass</span> <span class="pro">Pro</span></b></a><nav><a href="/ratgeber/">Alle Ratgeber</a><a class="hide-s" href="/app/"> · Zum Geld-Kompass Pro</a></nav></div></header>
<main class="wrap">
<div class="eyebrow">{esc(p['eb'])}</div>
<h1>{esc(p['h1'])}</h1>
<p class="lead">{esc(p['lead'])}</p>
<section class="card calc rg-calc" aria-label="Rechner">
<div class="grid">
<label>{esc(p['label'])}<input id="rgM" inputmode="decimal" value="{p['amount']}"></label>
<label>Dein Nettoeinkommen pro Monat (€)<input id="rgInc" inputmode="decimal" value="2400"></label>
<label>Deine Ausgaben pro Monat (€)<input id="rgSp" inputmode="decimal" value="1800"></label>
</div>
<label class="rg-sl">Angenommene Ersparnis <input id="rgP" type="range" min="5" max="40" step="5" value="20"><b id="rgPl">20 %</b></label>
<div class="big" id="rgBig"></div>
<div class="res" id="rgRes"></div>
<p class="note">Rechenbeispiel ohne Gewähr. Arbeitszeit bei 40 Stunden pro Woche, ein Freiheitstag sind deine Ausgaben pro Tag. Die Ersparnis ist eine Annahme, keine Zusage.</p>
<div data-partner="{p['partner']}" hidden></div>
</section>
<div class="cta"><a href="/app/#recurring"><i>{LOGO}</i><div><b>Alle laufenden Kosten auf einmal prüfen</b><span>Der Spar-Check im Geld-Kompass Pro findet Abos und Fixkosten aus deinem Kontoauszug und zeigt deinen größten Hebel. Kostenlos, deine Daten bleiben auf deinem Gerät.</span></div></a></div>
<div class="rg-body">{body}</div>
<h2>Häufige Fragen</h2>{faq}
<h2>Weitere Ratgeber</h2><div class="more">{more}<a href="/rechner/">Alle Rechner<small>Sparplan, Schulden, Notgroschen und mehr</small></a></div>
<p class="note">Allgemeine Finanzbildung, keine Rechts-, Steuer-, Versicherungs- oder Anlageberatung. Partner-Links sind gekennzeichnet, mehr unter <a href="/werbung/">Werbung und Partner-Links</a>.</p>
</main>
<footer><div class="wrap"><a href="/impressum/">Impressum</a> · <a href="/datenschutz/">Datenschutz</a> · <a href="/werbung/">Werbung</a> · Geld-Kompass Pro · © FreedomByDan</div></footer>
<script src="/partner.js" defer></script>
<script>{js}</script>
<!-- Cloudflare Web Analytics (ohne Cookies, keine personenbezogenen Daten) --><script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token": "d5b51a031e8c4e26b08ad199a6bfd2da"}}'></script>
</body></html>
"""

def hub():
    cards = ''.join('<a href="%s/">%s<small>%s</small></a>' % (p['slug'], esc(p['short']), esc(p['teaser'])) for p in PAGES)
    return f"""<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ratgeber: laufende Kosten senken, gerechnet in Freiheitstagen | Geld-Kompass Pro</title>
<meta name="description" content="Kostenlose Ratgeber mit Rechner: Handy und Internet, Strom und Gas, Versicherungen. Sieh, was dich laufende Kosten an Lebenszeit kosten und wo du am leichtesten sparst.">
<link rel="canonical" href="{BASE}ratgeber/"><meta name="theme-color" content="#0E1730">
<link rel="stylesheet" href="/rechner/rechner.css"><link rel="icon" type="image/png" sizes="32x32" href="/icons/favicon-32.png?v=3">
{VIS}</head><body>
<header class="top"><div class="wrap"><a class="logo" href="/">{LOGO}<b>Geld-<span>Kompass</span> <span class="pro">Pro</span></b></a><nav><a href="/rechner/">Rechner</a> · <a href="/app/">Zum Geld-Kompass Pro</a></nav></div></header>
<main class="wrap"><div class="eyebrow">Ratgeber</div><h1>Laufende Kosten senken, gerechnet in Freiheitstagen</h1>
<p class="lead">Jeder Euro, den du jeden Monat weniger zahlst, kauft dir ein Stück Lebenszeit zurück. Diese Ratgeber zeigen dir mit einem kleinen Rechner, wo sich ein Blick am meisten lohnt.</p>
<div class="more">{cards}</div>
<p class="note">Allgemeine Finanzbildung, keine Beratung. Partner-Links sind gekennzeichnet: <a href="/werbung/">Werbung und Partner-Links</a>.</p></main>
<footer><div class="wrap"><a href="/impressum/">Impressum</a> · <a href="/datenschutz/">Datenschutz</a> · <a href="/werbung/">Werbung</a> · Geld-Kompass Pro · © FreedomByDan</div></footer>
<!-- Cloudflare Web Analytics (ohne Cookies, keine personenbezogenen Daten) --><script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token": "d5b51a031e8c4e26b08ad199a6bfd2da"}}'></script>
</body></html>
"""

os.makedirs('ratgeber', exist_ok=True)
for p in PAGES:
    os.makedirs('ratgeber/' + p['slug'], exist_ok=True)
    open('ratgeber/%s/index.html' % p['slug'], 'w').write(page(p))
open('ratgeber/index.html', 'w').write(hub())
print('ok', len(PAGES))

# Einheitlicher Rahmen (Kopfzeile, Fuß, ui.css) für alle öffentlichen Seiten
import importlib.util as _ilu, os as _os
_sp = _ilu.spec_from_file_location('unify_chrome', _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'unify_chrome.py')); _m = _ilu.module_from_spec(_sp); _sp.loader.exec_module(_m); _m.run()
