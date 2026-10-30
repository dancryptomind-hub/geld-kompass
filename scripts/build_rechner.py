"""Erzeugt die einzelnen Rechner-Seiten unter /rechner/ (statisches HTML für Google).
Aufruf im Repo-Hauptordner: python3 scripts/build_rechner.py"""
import json, os, html, datetime

BASE = 'https://geld-kompass.com/'
KANAL = 'https://whatsapp.com/channel/0029VbEHiDdLCoX7Bhggff2E'
BUCH = 'https://amzn.eu/d/01dK026o'
TODAY = datetime.date.today().isoformat()

LOGO = '<img class="gk-logo" src="/icons/logo-badge.webp" alt="" aria-hidden="true" width="34" height="34">'

PAGES = []
def page(**kw): PAGES.append(kw)

# ---------------------------------------------------------------- Sparplan
page(slug='sparplan-rechner', short='Sparplan-Rechner', teaser='Was aus einer monatlichen Sparrate werden kann',
 title='Sparplan-Rechner: Was werden 100 € im Monat? | Geld-Kompass',
 desc='Kostenloser Sparplan- und Zinseszinsrechner: Monatliche Rate, Laufzeit und angenommene Rendite eingeben und sofort sehen, was daraus rechnerisch werden kann.',
 eyebrow='Sparplan & Zinseszins', h1='Sparplan-Rechner: Was wird aus deiner monatlichen Rate?',
 lead='Gib ein, wie viel du monatlich zurücklegen möchtest. Der Rechner zeigt dir, wie viel du selbst einzahlst und welcher Teil rechnerisch durch Zinseszins entsteht.',
 calc='''
<div class="chips" id="pre"><button type="button" data-r="25">25 €</button><button type="button" data-r="50">50 €</button><button type="button" data-r="100">100 €</button><button type="button" data-r="250">250 €</button><button type="button" data-r="500">500 €</button></div>
<div class="grid">
<label>Monatliche Rate (€)<input id="rate" inputmode="decimal" value="100"></label>
<label>Laufzeit (Jahre)<input id="years" inputmode="numeric" value="20"></label>
<label>Angenommene Rendite pro Jahr (%)<input id="ret" inputmode="decimal" value="7"></label>
<label>Startbetrag (€)<input id="start" inputmode="decimal" value="0"></label>
</div>
<div class="big" id="big"></div><div id="bigsub" class="note" style="margin-top:0"></div>
<div class="res" id="res"></div>
<table id="tab"></table>
<p class="note">Modellrechnung mit gleichbleibender Rendite und monatlicher Verzinsung, ohne Kosten und Steuern. Echte Märkte schwanken, auch mit Verlustjahren. Keine Anlageberatung.</p>
<div class="share" id="share"></div>''',
 js='''
var G=GKR;document.querySelectorAll('#pre button').forEach(function(b){b.onclick=function(){G.$('rate').value=b.dataset.r;run();};});
function run(){var m=G.val('rate'),n=Math.max(1,Math.min(60,Math.round(G.val('years')))),r=G.val('ret')/100,s0=G.val('start');
 var rm=Math.pow(1+r,1/12)-1,v=s0,rows=[];for(var i=1;i<=n*12;i++){v=v*(1+rm)+m;if(i%60===0||i===n*12)rows.push([i/12,v,s0+m*i]);}
 var paid=s0+m*n*12,gain=v-paid;
 G.$('big').textContent=G.E(v);G.$('bigsub').textContent='nach '+n+' Jahren bei '+G.nf1.format(r*100)+' % pro Jahr (rechnerisch)';
 G.$('res').innerHTML='<div><span>Selbst eingezahlt</span><b>'+G.E(paid)+'</b></div><div><span>Zinseszins-Anteil</span><b class="pos">'+G.E(gain)+'</b></div><div><span>Anteil Zinseszins</span><b class="gold">'+G.nf0.format(v>0?gain/v*100:0)+' %</b></div>';
 G.$('tab').innerHTML='<thead><tr><th>Nach</th><th>Eingezahlt</th><th>Wert</th></tr></thead><tbody>'+rows.map(function(x){return '<tr><td>'+G.nf0.format(x[0])+' Jahren</td><td>'+G.E(x[2])+'</td><td>'+G.E(x[1])+'</td></tr>';}).join('')+'</tbody>';
 G.share(G.$('share'),G.E(m)+' im Monat über '+n+' Jahre: Bei '+G.nf1.format(r*100)+' % pro Jahr werden daraus rechnerisch '+G.E(v)+'. Selbst eingezahlt sind nur '+G.E(paid)+'.','rechner/sparplan-rechner/');}
G.bind(['rate','years','ret','start'],run);''',
 body='''
<h2>So rechnet der Sparplan-Rechner</h2>
<p>Jeden Monat kommt deine Rate dazu, und der bisherige Betrag wächst mit der angenommenen Rendite weiter. Genau das ist Zinseszins: Auch die Erträge der Vorjahre arbeiten mit. Am Anfang wirkt der Effekt klein, nach 15 bis 20 Jahren macht er oft einen großen Teil des Endwerts aus.</p>
<p>Der Rechner rechnet die Jahresrendite auf einen gleichwertigen Monatszins um und verzinst jeden Monat. Kosten, Steuern und Inflation sind nicht enthalten, damit die Mechanik klar sichtbar bleibt.</p>
<h2>Welche Rendite ist realistisch?</h2>
<p>Breit gestreute Aktien-ETFs auf den Weltmarkt haben über lange Zeiträume historisch im Schnitt etwa 6 bis 8 Prozent pro Jahr erzielt, mit starken Schwankungen und Jahren mit deutlichen Verlusten. Tagesgeld und Anleihen liegen meist darunter. Vergangene Renditen sind keine Garantie. Rechne deshalb ruhig mehrere Varianten durch, zum Beispiel mit 4, 6 und 8 Prozent.</p>
<h2>Der wichtigste Hebel ist die Zeit</h2>
<p>Wer 10 Jahre früher beginnt, braucht für dasselbe Ziel oft eine deutlich kleinere Rate. Darum lohnt es sich, mit einem kleinen Betrag anzufangen, statt auf den perfekten Zeitpunkt zu warten. Im Geld-Kompass siehst du, welche Rate dein Monat tatsächlich hergibt.</p>''',
 faqs=[('Was ist der Zinseszins-Effekt?','Erträge werden wieder angelegt und erzielen selbst Erträge. Dadurch wächst ein Betrag mit der Zeit nicht gleichmäßig, sondern immer schneller.'),
       ('Sind Steuern und Kosten berücksichtigt?','Nein. Der Rechner zeigt die reine Mechanik. In der Praxis mindern Fondskosten, Depotgebühren und Abgeltungsteuer das Ergebnis.'),
       ('Ist das eine Anlageempfehlung?','Nein. Es ist eine Modellrechnung zur Finanzbildung. Welche Anlage zu dir passt, hängt von deiner Lage, deinem Zeitraum und deiner Risikobereitschaft ab.')])

# ---------------------------------------------------------------- Inflation
page(slug='inflationsrechner', short='Inflationsrechner', teaser='Was dein Geld von damals heute noch wert ist',
 title='Inflationsrechner: Was sind 1.000 € von früher heute wert? | Geld-Kompass',
 desc='Inflationsrechner mit amtlichen Daten für Deutschland, Österreich, den Euroraum, die USA und Großbritannien: Kaufkraftverlust zwischen zwei Jahren kostenlos berechnen.',
 eyebrow='Kaufkraft & Inflation', h1='Inflationsrechner: Was ist dein Geld von damals heute noch wert?',
 lead='Wähle Betrag und Jahre. Der Rechner nutzt die amtlichen Jahresdurchschnitte des Harmonisierten Verbraucherpreisindex (HVPI) von Eurostat.',
 calc='''
<div class="grid">
<label><span id="amtL">Betrag (€)</span><input id="amt" inputmode="decimal" value="1000"></label>
<label>Land<select id="geo"><option value="DE">Deutschland</option><option value="AT">Österreich</option><option value="EA20">Euroraum</option><option value="US">USA</option><option value="UK">Großbritannien</option></select></label>
<label>Von Jahr<select id="y0"></select></label>
<label>Bis Jahr<select id="y1"></select></label>
</div>
<div class="big" id="big">…</div><div id="bigsub" class="note" style="margin-top:0"></div>
<div class="res" id="res"></div>
<p class="note" id="src">Amtliche Daten werden geladen.</p>
<div class="share" id="share"></div>''',
 js='''
var G=GKR,DATA=null,CURG={US:'USD',UK:'GBP'},SYMG={US:'$',UK:'£'};
function F(v){var c=CURG[G.$('geo').value]||'EUR';return new Intl.NumberFormat('de-DE',{style:'currency',currency:c,maximumFractionDigits:(Math.abs(v)>=1000||Math.abs(v-Math.round(v))<0.005)?0:2}).format(v);}
fetch('/data/hicp_annual.json',{cache:'no-cache'}).then(function(r){return r.json();}).then(function(d){DATA=d;fill();}).catch(function(){G.$('big').textContent='–';G.$('src').textContent='Die amtlichen Daten sind gerade nicht erreichbar. Bitte später erneut versuchen.';});
function years(){var g=DATA[G.$('geo').value]||DATA.DE;return Object.keys(g.index).sort();}
function fill(){var ys=years(),a=G.$('y0'),b=G.$('y1'),pa=a.value,pb=b.value;
 a.innerHTML=b.innerHTML=ys.map(function(y){return '<option>'+y+'</option>';}).join('');
 a.value=ys.indexOf(pa)>-1?pa:(ys.indexOf('2010')>-1?'2010':ys[0]);b.value=ys.indexOf(pb)>-1?pb:ys[ys.length-1];run();}
G.$('geo').addEventListener('change',function(){G.$('amtL').textContent='Betrag ('+(SYMG[G.$('geo').value]||'€')+')';fill();});
function run(){if(!DATA)return;var g=DATA[G.$('geo').value]||DATA.DE,ix=g.index,y0=G.$('y0').value,y1=G.$('y1').value,a=G.val('amt');
 if(!(y0 in ix)||!(y1 in ix))return;var f=ix[y1]/ix[y0],same=a*f,kauf=a/f,pct=(f-1)*100,n=Math.abs(+y1-+y0),pa=n?(Math.pow(f,1/n)-1)*100:0;
 var land=G.$('geo').selectedOptions[0].textContent;
 G.$('big').textContent=F(kauf);
 G.$('bigsub').textContent=+y1>=+y0?'Kaufkraft von '+F(a)+' aus '+y0+', gemessen in Preisen von '+y1:'Wert in Preisen von '+y1;
 G.$('res').innerHTML='<div><span>Für dasselbe brauchst du '+y1+'</span><b class="neg">'+F(same)+'</b></div><div><span>Preise insgesamt</span><b class="gold">'+(pct>=0?'+':'')+G.nf1.format(pct)+' %</b></div><div><span>Im Schnitt pro Jahr</span><b>'+G.nf1.format(pa)+' %</b></div>';
 G.$('src').innerHTML='Quelle: '+G.esc(g.source||'Eurostat, HVPI Jahresdurchschnitt')+' ('+G.esc(land)+', Jahresdurchschnitt, 2015 = 100). Stand der Abfrage: '+G.esc((DATA.checked||'').slice(0,10))+'. Das letzte Jahr ist der zuletzt vollständig veröffentlichte Jahresdurchschnitt.';
 G.share(G.$('share'),F(a)+' aus dem Jahr '+y0+' haben '+y1+' nur noch die Kaufkraft von '+F(kauf)+' ('+land+', amtliche Daten).','rechner/inflationsrechner/');}
G.bind(['amt','y0','y1'],run);''',
 body='''
<h2>Was der Inflationsrechner zeigt</h2>
<p>Inflation heißt: Mit demselben Geldbetrag kannst du später weniger kaufen. Der Rechner vergleicht den Preisindex zweier Jahre. Ist das allgemeine Preisniveau zum Beispiel um 40 Prozent gestiegen, brauchst du für denselben Einkauf 1.400 € statt 1.000 €. Umgekehrt haben 1.000 € von damals heute nur noch die Kaufkraft von rund 714 €.</p>
<h2>Woher die Zahlen kommen</h2>
<p>Verwendet wird der Harmonisierte Verbraucherpreisindex (HVPI) von Eurostat, also die amtliche, europaweit vergleichbare Messung der Verbraucherpreise. Für jedes Jahr gilt der Jahresdurchschnitt. Der deutsche Verbraucherpreisindex des Statistischen Bundesamts (VPI) weicht leicht davon ab, weil er anders gewichtet ist; die Größenordnung ist dieselbe.</p>
<h2>Was das für dein Geld bedeutet</h2>
<p>Geld, das jahrelang ohne Zinsen auf dem Girokonto liegt, verliert an Kaufkraft, auch wenn der Kontostand gleich bleibt. Einen Notgroschen brauchst du trotzdem sofort verfügbar. Für Geld, das du viele Jahre nicht brauchst, lohnt sich deshalb die Frage, wie es mindestens die Inflation ausgleichen kann. Im Geld-Kompass siehst du, wie viel davon bei dir betroffen ist.</p>''',
 faqs=[('Ist das die offizielle Inflationsrate?','Ja, die Werte stammen direkt aus der amtlichen Statistik von Eurostat (HVPI, Jahresdurchschnitt). Sie werden automatisch aktualisiert.'),
       ('Warum weicht meine gefühlte Inflation ab?','Der Index misst einen durchschnittlichen Warenkorb. Wer viel für Lebensmittel, Energie oder Miete ausgibt, spürt Preissteigerungen oft stärker.'),
       ('Warum fehlt das laufende Jahr?','Ein Jahresdurchschnitt steht erst fest, wenn das Jahr vorbei ist. Die aktuelle Monatsrate zeigt der Geld-Kompass im Kaufkraft-Check.')])

# ---------------------------------------------------------------- Abo als Aktie
page(slug='abo-als-aktie', short='Konsument oder Eigentümer?', teaser='Was dein Abo oder deine Gewohnheit angelegt wäre',
 title='Konsument oder Eigentümer? Was wäre dein Abo als Sparplan? | Geld-Kompass',
 desc='Netflix, Kaffee, Zigaretten oder Handyvertrag: Berechne kostenlos, was eine regelmäßige Ausgabe über Jahre gekostet hat und was sie angelegt rechnerisch geworden wäre.',
 eyebrow='Konsument oder Eigentümer?', h1='Was wäre aus deinem Abo geworden, wenn du es angelegt hättest?',
 lead='Jede regelmäßige Ausgabe macht ein Unternehmen reicher. Rechne nach, was dich eine Gewohnheit über die Jahre kostet und was derselbe Betrag angelegt rechnerisch hätte werden können.',
 calc='''
<div class="chips" id="pre"><button type="button" data-t="Streaming-Abo" data-a="13.99" data-p="m">Streaming 13,99 €/Monat</button><button type="button" data-t="Coffee to go" data-a="3.5" data-p="d">Kaffee 3,50 €/Tag</button><button type="button" data-t="Zigaretten" data-a="9" data-p="d">Zigaretten 9 €/Tag</button><button type="button" data-t="Lieferdienst" data-a="25" data-p="w">Lieferdienst 25 €/Woche</button><button type="button" data-t="Energy-Drink" data-a="2" data-p="d">Energy-Drink 2 €/Tag</button></div>
<div class="grid">
<label>Wofür?<input id="what" value="Streaming-Abo"></label>
<label>Betrag (€)<input id="amt" inputmode="decimal" value="13,99"></label>
<label>Wie oft?<select id="per"><option value="d">pro Tag</option><option value="w">pro Woche</option><option value="m" selected>pro Monat</option></select></label>
<label>Zeitraum (Jahre)<input id="years" inputmode="numeric" value="20"></label>
<label>Angenommene Rendite pro Jahr (%)<input id="ret" inputmode="decimal" value="7"></label>
</div>
<div class="res" id="res"></div>
<p class="note">Die Rendite ist eine Annahme, etwa für einen breit gestreuten Welt-ETF im langjährigen Mittel. Einzelne Aktien können stark schwanken und auch alles verlieren. Modellrechnung ohne Kosten und Steuern, keine Anlageberatung.</p>
<div class="share" id="share"></div>''',
 js='''
var G=GKR;document.querySelectorAll('#pre button').forEach(function(b){b.onclick=function(){G.$('what').value=b.dataset.t;G.$('amt').value=String(b.dataset.a).replace('.',',');G.$('per').value=b.dataset.p;run();};});
function run(){var a=G.val('amt'),p=G.$('per').value,m=a*(p==='d'?365/12:p==='w'?52/12:1),n=Math.max(1,Math.min(50,Math.round(G.val('years')))),r=G.val('ret')/100,rm=Math.pow(1+r,1/12)-1,v=0;
 for(var i=0;i<n*12;i++)v=v*(1+rm)+m;var spent=m*n*12,w=(G.$('what').value||'deine Ausgabe').trim();
 G.$('res').innerHTML='<div><span>Ausgegeben in '+n+' Jahren</span><b class="neg">'+G.E(spent)+'</b></div><div><span>Angelegt rechnerisch</span><b class="pos">'+G.E(v)+'</b></div><div><span>Unterschied</span><b class="gold">'+G.E(v-spent)+'</b></div><div><span>Pro Monat</span><b>'+G.E(m)+'</b></div>';
 G.share(G.$('share'),w+' für '+G.E(m)+' im Monat: In '+n+' Jahren sind das '+G.E(spent)+' ausgegeben. Angelegt wären es bei '+G.nf1.format(r*100)+' % pro Jahr rechnerisch '+G.E(v)+'.','rechner/abo-als-aktie/');}
G.bind(['what','amt','per','years','ret'],run);''',
 body='''
<h2>Konsument oder Eigentümer</h2>
<p>Wenn du jeden Tag einen Kaffee kaufst, verdienen daran die Kette, der Röster und viele andere. Als Kunde zahlst du; als Eigentümer, zum Beispiel über Aktien oder einen breit gestreuten Fonds, wärst du an solchen Gewinnen beteiligt. Diese Frage zieht sich durch das Buch „Der einfache Weg zur Finanziellen Freiheit“.</p>
<h2>Es geht nicht um Verzicht</h2>
<p>Niemand muss auf alles verzichten. Der Rechner macht nur sichtbar, was eine kleine, regelmäßige Ausgabe über lange Zeit bedeutet. Oft reicht es schon, eine von mehreren Gewohnheiten zu halbieren und die Differenz automatisch zurückzulegen.</p>
<h2>Mit echten Unternehmen rechnen</h2>
<p>Im kostenlosen Geld-Kompass erkennt der Bereich „Konsument oder Eigentümer?“ viele Marken automatisch und rechnet mit den durchschnittlichen Renditen der dazugehörigen Aktien der letzten Jahre, verglichen mit einem Welt-ETF.</p>''',
 faqs=[('Warum 7 Prozent?','Das ist eine Annahme für einen breit gestreuten Aktien-Weltindex über lange Zeiträume. Du kannst jeden anderen Wert eintragen.'),
       ('Rechnet der Rechner mit der echten Aktie von Netflix und Co.?','Diese Seite rechnet mit einer frei wählbaren Rendite. Im vollständigen Geld-Kompass werden Marken echten Unternehmen zugeordnet.'),
       ('Ist das eine Kaufempfehlung?','Nein. Es ist eine Modellrechnung zur Finanzbildung. Einzelaktien sind riskant und können ihren Wert vollständig verlieren.')])

# ---------------------------------------------------------------- Schuldenfrei
page(slug='schuldenfrei-rechner', short='Schuldenfrei-Rechner', teaser='Wann du schuldenfrei bist und was Extra-Raten bringen',
 title='Schuldenfrei-Rechner: Wann ist mein Kredit abbezahlt? | Geld-Kompass',
 desc='Tilgungsrechner für Ratenkredit, Dispo und Kreditkarte: Restschuld, Zins und Rate eingeben und sehen, in welchem Monat du schuldenfrei bist und wie viel Zinsen eine Extra-Rate spart.',
 eyebrow='Schulden & Tilgung', h1='Schuldenfrei-Rechner: Wann ist deine Schuld abbezahlt?',
 lead='Gib deine Restschuld, den Zinssatz und deine monatliche Rate ein. Du siehst das Datum, an dem du schuldenfrei bist, und wie viel Zinsen ein kleiner Extra-Betrag spart.',
 calc='''
<div class="grid">
<label>Restschuld (€)<input id="debt" inputmode="decimal" value="5000"></label>
<label>Zinssatz pro Jahr (%)<input id="rate" inputmode="decimal" value="12"></label>
<label>Monatliche Rate (€)<input id="pay" inputmode="decimal" value="150"></label>
<label>Extra pro Monat (€)<input id="extra" inputmode="decimal" value="50"></label>
</div>
<div class="big" id="big"></div><div id="bigsub" class="note" style="margin-top:0"></div>
<div class="res" id="res"></div>
<p class="note">Vereinfachte Rechnung mit festem Zins und gleichbleibender Rate, ohne Gebühren. Bei Problemen mit Raten helfen kostenlose Schuldnerberatungen, zum Beispiel der Verbraucherzentralen.</p>
<div class="share" id="share"></div>''',
 js='''
var G=GKR;
function plan(d,r,p){var rm=r/12,m=0,int=0;if(p<=d*rm+0.005)return null;while(d>0.005&&m<1200){var z=d*rm;int+=z;d=d+z-p;m++;}return {m:m,int:int};}
function run(){var d=G.val('debt'),r=G.val('rate')/100,p=G.val('pay'),x=G.val('extra'),a=plan(d,r,p),b=plan(d,r,p+x);
 if(!b){G.$('big').textContent='Rate zu niedrig';G.$('bigsub').textContent='Die Rate deckt nicht einmal die Zinsen von '+G.E(d*r/12)+' pro Monat. Die Schuld wächst. Hier lohnt sich ein Gespräch mit einer Schuldnerberatung.';G.$('res').innerHTML='';G.$('share').innerHTML='';return;}
 G.$('big').textContent=G.monthName(b.m);G.$('bigsub').textContent='schuldenfrei in '+b.m+' Monaten'+(b.m>=12?' (rund '+G.nf1.format(b.m/12)+' Jahre)':'')+(x>0?', mit '+G.E(x)+' extra pro Monat':'');
 var h='<div><span>Zinsen bis schuldenfrei</span><b class="neg">'+G.E(b.int)+'</b></div>';
 if(x>0&&a)h+='<div><span>Ohne Extra schuldenfrei</span><b>'+G.monthName(a.m)+'</b></div><div><span>Extra spart an Zinsen</span><b class="pos">'+G.E(a.int-b.int)+'</b></div><div><span>Früher fertig</span><b class="gold">'+(a.m-b.m)+' Monate</b></div>';
 else if(x>0&&!a)h+='<div><span>Ohne Extra</span><b class="neg">nie</b></div>';
 G.$('res').innerHTML=h;
 G.share(G.$('share'),x>0&&a?'Mit '+G.E(x)+' extra im Monat bin ich '+(a.m-b.m)+' Monate früher schuldenfrei und spare rechnerisch '+G.E(a.int-b.int)+' Zinsen.':'Mit meinem Plan bin ich in '+b.m+' Monaten schuldenfrei.','rechner/schuldenfrei-rechner/');}
G.bind(['debt','rate','pay','extra'],run);''',
 body='''
<h2>Warum schon kleine Extra-Beträge viel bewirken</h2>
<p>Bei jedem Kredit geht ein Teil der Rate an die Bank (Zinsen) und nur der Rest verringert die Schuld (Tilgung). Jeder zusätzliche Euro geht dagegen komplett in die Tilgung. Dadurch sinken die Zinsen im nächsten Monat, und mehr von deiner normalen Rate tilgt. Dieser Effekt verstärkt sich jeden Monat.</p>
<h2>Teure Schulden zuerst</h2>
<p>Dispo und Kreditkarte kosten oft 10 bis 20 Prozent Zinsen. Hast du mehrere Schulden, bringt ein Extra-Betrag bei der teuersten am meisten (Lawinen-Methode). Manche fangen lieber mit der kleinsten Schuld an, um schnell ein Erfolgserlebnis zu haben (Schneeball-Methode). Beides funktioniert, wenn du dranbleibst. Im Geld-Kompass vergleicht der Schulden-Plan beide Wege mit deinen echten Schulden.</p>
<h2>Wenn die Rate nicht reicht</h2>
<p>Deckt deine Rate kaum die Zinsen, wächst die Schuld trotz Zahlung. Dann ist das kein persönliches Versagen, sondern ein Zeichen, Hilfe zu holen. Kostenlose Schuldnerberatungen, etwa bei Verbraucherzentralen, Caritas oder Diakonie, verhandeln auch mit Gläubigern.</p>''',
 faqs=[('Darf ich einen Ratenkredit früher zurückzahlen?','Bei Verbraucherkrediten in Deutschland ist eine vorzeitige Rückzahlung grundsätzlich möglich; die Bank kann unter Umständen eine begrenzte Vorfälligkeitsentschädigung verlangen. Schau in deinen Vertrag.'),
       ('Wie genau ist die Rechnung?','Sie geht von festem Zins und gleicher Rate aus. Echte Verträge können Gebühren, Zinsbindungen oder Sondertilgungsregeln haben.'),
       ('Was ist besser: schneller tilgen oder sparen?','Bei teuren Schulden lohnt sich schnelles Tilgen meist mehr als Sparen. Ein kleiner Notgroschen sollte trotzdem da sein, damit keine neuen Schulden entstehen.')])

# ---------------------------------------------------------------- Notgroschen
page(slug='notgroschen-rechner', short='Notgroschen-Rechner', teaser='Wie groß deine Rücklage sein sollte',
 title='Notgroschen-Rechner: Wie viel Rücklage brauche ich? | Geld-Kompass',
 desc='Notgroschen berechnen: Aus deinen festen Monatskosten ergibt sich deine Ziel-Rücklage von 3 bis 6 Monaten, und du siehst, wann du sie mit deiner Sparrate erreichst.',
 eyebrow='Rücklage & Sicherheit', h1='Notgroschen-Rechner: Wie viel Rücklage brauchst du?',
 lead='Ein Notgroschen schützt dich davor, bei einer kaputten Waschmaschine oder einem Jobwechsel neue Schulden zu machen. Hier siehst du, wie groß er sein sollte und wann du ihn erreichst.',
 calc='''
<div class="grid">
<label>Feste Kosten pro Monat (€)<input id="cost" inputmode="decimal" value="1400"></label>
<label>Wie viele Monate absichern?<select id="mon"><option value="3">3 Monate</option><option value="4">4 Monate</option><option value="6" selected>6 Monate</option></select></label>
<label>Schon zurückgelegt (€)<input id="have" inputmode="decimal" value="1000"></label>
<label>Sparrate pro Monat (€)<input id="save" inputmode="decimal" value="150"></label>
</div>
<div class="big" id="big"></div><div id="bigsub" class="note" style="margin-top:0"></div>
<div class="res" id="res"></div>
<p class="note">Als feste Kosten zählen Miete, Nebenkosten, Versicherungen, Lebensmittel, Mobilität und Raten. Faustregel, keine Pflicht: Wer ein unsicheres Einkommen hat, plant eher mehr Monate ein.</p>
<div class="share" id="share"></div>''',
 js='''
var G=GKR;
function run(){var c=G.val('cost'),n=+G.$('mon').value,h=G.val('have'),s=G.val('save'),goal=c*n,miss=Math.max(0,goal-h),m=s>0?Math.ceil(miss/s):Infinity,cov=c>0?h/c:0;
 G.$('big').textContent=G.E(goal);G.$('bigsub').textContent='Ziel-Rücklage für '+n+' Monate';
 G.$('res').innerHTML='<div><span>Reicht heute für</span><b class="gold">'+G.nf1.format(cov)+' Monate</b></div><div><span>Fehlen noch</span><b class="'+(miss>0?'neg':'pos')+'">'+G.E(miss)+'</b></div><div><span>Ziel erreicht</span><b class="pos">'+(miss<=0?'schon jetzt ✓':isFinite(m)?G.monthName(m):'Sparrate eintragen')+'</b></div>';
 G.share(G.$('share'),miss<=0?'Mein Notgroschen steht: Er reicht für '+G.nf1.format(cov)+' Monate.':'Mein Notgroschen-Ziel: '+G.E(goal)+'. Mit '+G.E(s)+' im Monat erreiche ich es'+(isFinite(m)?' im '+G.monthName(m):'')+'.','rechner/notgroschen-rechner/');}
G.bind(['cost','mon','have','save'],run);''',
 body='''
<h2>Warum der Notgroschen zuerst kommt</h2>
<p>Ohne Rücklage wird jede unerwartete Rechnung zum Dispo oder zur Ratenzahlung, und die kosten Zinsen. Ein Notgroschen ist deshalb keine Geldanlage, sondern eine Versicherung gegen neue Schulden. Er gehört auf ein Konto, an das du schnell kommst, zum Beispiel ein Tagesgeldkonto.</p>
<h2>Wie groß sollte er sein?</h2>
<p>Häufig genannt werden drei bis sechs Monate deiner festen Kosten. Mit sicherem Job und ohne Kinder reichen oft drei Monate. Selbstständige, Alleinverdiener oder Menschen mit schwankendem Einkommen planen eher sechs Monate oder mehr.</p>
<h2>Klein anfangen</h2>
<p>Auch 500 € fangen schon viele kleine Notfälle ab. Richte am besten einen Dauerauftrag direkt nach dem Gehaltseingang ein. Im Geld-Kompass siehst du, wie viele Monate deine Rücklage bereits trägt.</p>''',
 faqs=[('Wo parke ich den Notgroschen am besten?','Auf einem sicheren, jederzeit verfügbaren Konto, zum Beispiel Tagesgeld mit Einlagensicherung. Nicht in Aktien, weil die genau im Notfall gefallen sein können.'),
       ('Soll ich erst Schulden tilgen oder sparen?','Meist zuerst einen kleinen Start-Notgroschen aufbauen, dann teure Schulden tilgen und danach die Rücklage vollständig auffüllen.'),
       ('Zählen Raten zu den festen Kosten?','Ja. Alles, was du jeden Monat sicher zahlen musst, gehört dazu.')])

# ---------------------------------------------------------------- Freiheitstage
page(slug='freiheitstage-rechner', short='Freiheitstage-Rechner', teaser='Wie viele Tage dein Vermögen dich trägt',
 title='Freiheitstage-Rechner: Wie lange reicht mein Geld ohne Einkommen? | Geld-Kompass',
 desc='Freiheitstage berechnen: Wie viele Tage könntest du von deinem Nettovermögen leben? Plus: Wie viele Tage Freiheit dir deine monatliche Sparrate jeden Monat dazugibt.',
 eyebrow='Freiheitstage', h1='Freiheitstage-Rechner: Wie viele Tage trägt dich dein Vermögen?',
 lead='Freiheitstage zeigen in einer einzigen Zahl, wie lange du rechnerisch von deinem Vermögen leben könntest. Diese Zahl wächst mit jedem Euro, den du sparst oder an Schulden tilgst.',
 calc='''
<div class="grid">
<label>Ersparnisse und Anlagen (€)<input id="assets" inputmode="decimal" value="8000"></label>
<label>Schulden (€)<input id="debts" inputmode="decimal" value="2000"></label>
<label>Ausgaben pro Monat (€)<input id="spend" inputmode="decimal" value="1800"></label>
<label>Sparrate pro Monat (€)<input id="save" inputmode="decimal" value="200"></label>
</div>
<div class="big" id="big"></div><div id="bigsub" class="note" style="margin-top:0"></div>
<div class="res" id="res"></div>
<p class="note">Rechnung: Nettovermögen geteilt durch Monatsausgaben, mal 30. Gebundenes Vermögen wie Immobilien oder Altersvorsorge ist nicht sofort verfügbar. Eine Orientierungszahl, keine Planung für den Ruhestand.</p>
<div class="share" id="share"></div>''',
 js='''
var G=GKR;
function run(){var a=G.val('assets'),d=G.val('debts'),s=G.val('spend'),sv=G.val('save'),nw=a-d,days=s>0?nw/s*30:0,gain=s>0?sv/s*30:0;
 G.$('big').textContent=s>0?(days>=0?G.nf0.format(days)+' Tage':'Noch im Minus'):'–';
 G.$('bigsub').textContent=days>=365?'das sind rund '+G.nf1.format(days/365)+' Jahre':days<0?'Dein Nettovermögen ist negativ. Jeder getilgte Euro bringt dich näher an Tag 1.':'rechnerisch von deinem Nettovermögen';
 G.$('res').innerHTML='<div><span>Nettovermögen</span><b class="'+(nw<0?'neg':'pos')+'">'+G.E(nw)+'</b></div><div><span>Jeden Monat dazu</span><b class="gold">+'+G.nf1.format(gain)+' Tage</b></div><div><span>Pro Jahr dazu</span><b>+'+G.nf0.format(gain*12)+' Tage</b></div>';
 G.share(G.$('share'),days>=0?'Ich habe '+G.nf0.format(days)+' Freiheitstage, und jeden Monat kommen '+G.nf1.format(gain)+' dazu. Wie viele hast du?':'Ich arbeite mich gerade zu meinem ersten Freiheitstag vor. Jeden Monat kommen '+G.nf1.format(gain)+' Tage dazu.','rechner/freiheitstage-rechner/');}
G.bind(['assets','debts','spend','save'],run);''',
 body='''
<h2>Was sind Freiheitstage?</h2>
<p>Stell dir vor, dein Einkommen fällt morgen weg. Wie viele Tage könntest du mit deinem heutigen Nettovermögen weiterleben, ohne etwas zu ändern? Das sind deine Freiheitstage. Die Zahl macht Fortschritt greifbar: Statt „2.000 € gespart“ heißt es „einen Monat mehr Freiheit“.</p>
<h2>Zwei Hebel</h2>
<p>Freiheitstage steigen, wenn dein Nettovermögen wächst, also durch Sparen, Anlegen und Tilgen. Sie steigen aber auch, wenn deine monatlichen Ausgaben sinken, denn dann reicht dasselbe Vermögen länger. Wer 100 € weniger pro Monat braucht, gewinnt doppelt: mehr Sparrate und mehr Tage pro Euro.</p>
<h2>Mit echten Zahlen verfolgen</h2>
<p>Im kostenlosen Geld-Kompass werden deine Freiheitstage automatisch aus deinen Buchungen, Schulden und deinem Depot berechnet und Monat für Monat sichtbar. Deine Daten bleiben dabei in deinem Browser.</p>''',
 faqs=[('Warum Nettovermögen und nicht nur Erspartes?','Schulden muss man von Ersparnissen abziehen, damit das Bild ehrlich ist. Wer 5.000 € gespart und 5.000 € Schulden hat, steht bei null.'),
       ('Gehört die Wohnung dazu?','Rechnerisch ja, praktisch kann man von einer selbst genutzten Wohnung nicht leben. Trag für eine ehrliche Zahl lieber nur verfügbares Vermögen ein.'),
       ('Woher kommt der Begriff?','Er stammt aus dem Buch „Der einfache Weg zur Finanziellen Freiheit“ und dem dazugehörigen Geld-Kompass.')])

# ================================================================= Ausgabe

# ---------------------------------------------------------------- Währungsrechner (Hauptseite + gefragte Währungspaare)

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rechner_en import EN as EN_TXT, EN_FX_SLUG, EN_FX_INTRO

# ---------------------------------------------------------------- Währungsrechner (Hauptseite + gefragte Währungspaare)
_CL = json.load(open('data/currencies.json', encoding='utf-8'))['currencies']
FXN = {x['c']: (x['de'], x.get('crypto', False)) for x in _CL}
FXN_EN = {x['c']: x['en'] for x in _CL}
FX_TOP = ['EUR','USD','GBP','CHF','TRY','THB','GEL','PLN','JPY','BTC']

def fx_opts(lang):
    nm = (lambda c: FXN_EN[c]) if lang == 'en' else (lambda c: FXN[c][0])
    o = lambda c: '<option value="%s">%s · %s</option>' % (c, c, nm(c))
    return ('<optgroup label="%s">' % ('Popular' if lang == 'en' else 'Häufig') + ''.join(o(c) for c in FX_TOP)
            + '</optgroup><optgroup label="%s">' % ('All currencies' if lang == 'en' else 'Alle Währungen')
            + ''.join(o(c) for c in sorted([c for c in FXN if not FXN[c][1]], key=nm)) + '</optgroup><optgroup label="%s">' % ('Crypto' if lang == 'en' else 'Krypto')
            + ''.join(o(c) for c in FXN if FXN[c][1]) + '</optgroup>')

def fx_calc(lang='de'):
    en = lang == 'en'
    return ('\n<div class="grid fxg">\n<label>%s<input id="amt" inputmode="decimal" value="100"></label>\n' % ('Amount' if en else 'Betrag')
            + '<label>%s<select id="from">' % ('From' if en else 'Von') + fx_opts(lang) + '</select></label>\n'
            + '<button type="button" id="swap" class="swapb" aria-label="%s">⇄</button>\n' % ('Swap currencies' if en else 'Währungen tauschen')
            + '<label>%s<select id="to">' % ('To' if en else 'Nach') + fx_opts(lang) + '</select></label>\n</div>\n'
            + '<div class="big" id="big">…</div><div id="bigsub" class="note" style="margin-top:0"></div>\n'
            + '<div class="res" id="res"></div>\n<table id="tab"></table>\n'
            + '<p class="note" id="src">%s</p>\n<div class="share" id="share"></div>' % ('Loading current exchange rates.' if en else 'Aktuelle Devisenkurse werden geladen.')
            + '<div class="fxchart"><p class="note" id="fxct" style="margin:0 0 6px"></p><div id="fxChart"></div></div>')

FX_JS = r'''
var G=GKR,FX=null,F0="__F__",T0="__T__",SLUG="__S__";
var N=__N__,CR=__CR__;
G.$('from').value=F0;G.$('to').value=T0;if(CR[F0])G.$('amt').value='1';
function fmt(v,c){if(CR[c]){var k=Math.abs(v)>=100?2:Math.abs(v)>=1?4:8;return new Intl.NumberFormat('de-DE',{maximumFractionDigits:k}).format(v)+' '+c;}var d=Math.abs(v)>=1000?0:(Math.abs(v)<1&&v!==0?4:2);try{return new Intl.NumberFormat('de-DE',{style:'currency',currency:c,minimumFractionDigits:d,maximumFractionDigits:d}).format(v);}catch(e){return G.nf1.format(v)+' '+c;}}
function nfx(v){return new Intl.NumberFormat('de-DE',{maximumSignificantDigits:6}).format(v);}
fetch('/data/markets.json',{cache:'no-cache'}).then(function(r){return r.json();}).then(function(d){FX=d.fx;run();}).catch(function(){G.$('big').textContent='–';G.$('src').textContent='Die Devisenkurse sind gerade nicht erreichbar. Bitte später erneut versuchen.';});
G.$('swap').onclick=function(){var a=G.$('from').value;G.$('from').value=G.$('to').value;G.$('to').value=a;run();};
function run(){if(!FX||!FX.rates)return;var R=FX.rates,f=G.$('from').value,to=G.$('to').value,a=G.val('amt');if(!R[f]||!R[to])return;
 var rate=R[to]/R[f],ch=FX.change||{},chg=((1+(ch[to]||0)/100)/(1+(ch[f]||0)/100)-1)*100;
 G.$('big').textContent=fmt(a*rate,to);
 G.$('bigsub').textContent=fmt(a,f)+' entsprechen aktuell '+fmt(a*rate,to)+' ('+N[f]+' in '+N[to]+')';
 G.$('res').innerHTML='<div><span>1 '+f+' =</span><b class="gold">'+nfx(rate)+' '+to+'</b></div><div><span>1 '+to+' =</span><b>'+nfx(1/rate)+' '+f+'</b></div><div><span>Zum Vortag</span><b class="'+(chg>=0?'pos':'neg')+'">'+(chg>=0?'+':'')+new Intl.NumberFormat('de-DE',{minimumFractionDigits:2,maximumFractionDigits:2}).format(chg)+' %</b></div>';
 var am=CR[f]?[0.001,0.005,0.01,0.05,0.1,0.25,0.5,1,2,5]:[1,5,10,20,50,100,200,500,1000,5000];
 G.$('tab').innerHTML='<tr><th>'+N[f]+'</th><th>'+N[to]+'</th></tr>'+am.map(function(x){return '<tr><td>'+fmt(x,f)+'</td><td>'+fmt(x*rate,to)+'</td></tr>';}).join('');
 var when=FX.updated?new Date(FX.updated).toLocaleString('de-DE',{day:'2-digit',month:'2-digit',year:'numeric',hour:'2-digit',minute:'2-digit'}):'';
 G.$('src').textContent='Mittelkurs von Yahoo Finance (Devisenmarkt), Stand '+when+' Uhr, wird automatisch alle zwei Stunden aktualisiert. Banken, Kartenanbieter und Wechselstuben rechnen mit Auf- und Abschlägen.';
 G.share(G.$('share'),fmt(a,f)+' sind gerade '+fmt(a*rate,to)+'. Live-Kurs, Chart und Umrechnungstabelle:','rechner/'+SLUG+'/');chart(f,to);}
var CK='',CT=null;
function sym(f,to){var BS={EUR:1,USD:1,GBP:1};if(CR[f]||CR[to]){var c=CR[f]?f:to,x=CR[f]?to:f;if(CR[x]||!(BS[x]||{TRY:1,BRL:1,PLN:1,JPY:1}[x]))x='USD';return [(BS[x]?'BITSTAMP:':'BINANCE:')+c+x,c+' in '+x];}
 if(f==='EUR'||f==='USD'||to==='EUR'||to==='USD')return ['FX_IDC:'+f+to,f+' in '+to];return ['FX_IDC:EUR'+to,'EUR in '+to];}
function chart(f,to){if(f===to)return;var s=sym(f,to);if(s[0]===CK)return;CK=s[0];clearTimeout(CT);CT=setTimeout(function(){
 G.$('fxct').textContent='Kursverlauf live: '+s[1]+' (TradingView)';var box=G.$('fxChart');
 box.innerHTML='<div class="tradingview-widget-container" style="height:100%"><div class="tradingview-widget-container__widget" style="height:100%"></div></div>';
 var sc=document.createElement('script');sc.src='https://s3.tradingview.com/external-embedding/embed-widget-symbol-overview.js';sc.async=true;
 var dk=window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches;sc.innerHTML=JSON.stringify({symbols:[[s[1],s[0]+'|12M']],chartOnly:false,width:'100%',height:'100%',locale:'de_DE',colorTheme:dk?'dark':'light',autosize:true,showVolume:false,hideDateRanges:false,hideMarketStatus:true,scalePosition:'right',scaleMode:'Normal',fontSize:'10',valuesTracking:'1',changeMode:'price-and-percent',chartType:'area',lineWidth:2,dateRanges:['1d|1','1m|30','3m|60','12m|1D','60m|1W','all|1M'],isTransparent:true,lineColor:'#b8862f',topColor:'rgba(227,181,90,0.35)',bottomColor:'rgba(227,181,90,0)'});
 box.firstChild.appendChild(sc);},300);}
G.bind(['amt','from','to'],run);'''

FX_JS_EN = [("'de-DE'", "'en-GB'"), ("' entsprechen aktuell '", "' is currently '"), ('Zum Vortag', 'vs. previous day'),
 ("'Die Devisenkurse sind gerade nicht erreichbar. Bitte später erneut versuchen.'", "'Exchange rates are not available right now. Please try again later.'"),
 ("'Mittelkurs von Yahoo Finance (Devisenmarkt), Stand '+when+' Uhr, wird automatisch alle zwei Stunden aktualisiert. Banken, Kartenanbieter und Wechselstuben rechnen mit Auf- und Abschlägen.'",
  "'Mid-market rate from Yahoo Finance, as of '+when+', updated automatically every two hours. Banks, card providers and exchange offices add a margin.'"),
 ("' sind gerade '", "' is currently '"), ("'. Live-Kurs, Chart und Umrechnungstabelle:'", "'. Live rate, chart and conversion table:'"),
 ("'rechner/'+SLUG+'/'", "'en/calculators/'+SLUG+'/'"), ("'Kursverlauf live: '", "'Live price chart: '"), ("locale:'de_DE'", "locale:'en'")]

def tr(s, pairs, where):
    for a, b in sorted(pairs, key=lambda x: -len(x[0])):
        if a not in s:
            raise SystemExit('Übersetzung nicht gefunden (%s): %s' % (where, a[:80]))
        s = s.replace(a, b)
    return s

def fx_js(f, to, slug, lang='de'):
    js = (FX_JS.replace('__F__', f).replace('__T__', to).replace('__S__', slug)
          .replace('__N__', json.dumps(FXN_EN if lang == 'en' else {c: n[0] for c, n in FXN.items()}, ensure_ascii=False))
          .replace('__CR__', json.dumps({c: 1 for c, n in FXN.items() if n[1]})))
    return tr(js, FX_JS_EN, 'fx_js') if lang == 'en' else js

BTC_TEXT = '''
<h2>Was du über den Bitcoin-Kurs wissen solltest</h2>
<p>Bitcoin hat keinen festen Wechselkurs wie eine Landeswährung. Der Preis entsteht an Kryptobörsen rund um die Uhr, auch am Wochenende, und kann innerhalb eines Tages um mehrere Prozent schwanken. Der Rechner nutzt den aktuellen Preis von Yahoo Finance; der Chart darunter zeigt den Verlauf an der Börse Bitstamp.</p>
<p>Beim Kauf über eine App oder Börse kommen Gebühren und ein Kursaufschlag dazu. Vergleiche deshalb den angebotenen Preis mit dem Kurs oben. Und die wichtigste Regel aus dem Buch gilt auch hier: Erst Notgroschen und teure Schulden, dann schwankende Anlagen, und nur mit Geld, das du lange nicht brauchst.</p>'''

BTC_TEXT_EN = """
<h2>What you should know about the bitcoin price</h2>
<p>Bitcoin has no fixed exchange rate like a national currency. Its price is set on crypto exchanges around the clock, including weekends, and can move several percent within a day. The calculator uses the current price from Yahoo Finance; the chart below shows the price history on the Bitstamp exchange.</p>
<p>When you buy through an app or exchange, fees and a price markup are added, so compare the offered price with the rate above. And the most important rule from the book applies here too: emergency fund and expensive debt first, then volatile investments, and only with money you will not need for a long time.</p>"""

FX_TIPS = '''
<h2>So zahlst du im Ausland nicht zu viel</h2>
<p>Der Kurs oben ist der Mittelkurs am Devisenmarkt. Den bekommst du als Privatperson fast nie ganz, denn Banken, Kartenanbieter und Wechselstuben verdienen an der Differenz. Drei Dinge machen in der Praxis den größten Unterschied:</p>
<ul><li><b>In Landeswährung zahlen.</b> Fragt dich ein Kartenterminal oder Geldautomat, ob in Euro abgerechnet werden soll, wähle die Landeswährung. Die angebotene Sofortumrechnung („Dynamic Currency Conversion“) ist meist deutlich teurer.</li>
<li><b>Gebühren deiner Karte prüfen.</b> Viele Karten berechnen für Zahlungen in Fremdwährung einen Aufschlag. Es gibt Karten ohne diese Gebühr; ein Blick ins Preisverzeichnis lohnt sich vor der Reise.</li>
<li><b>Bargeld nicht am Flughafen tauschen.</b> Wechselstuben an Flughäfen und Bahnhöfen haben oft schlechte Kurse. Vergleiche den angebotenen Kurs mit dem Mittelkurs oben: Je größer der Abstand, desto teurer.</li></ul>
<h2>Woher die Kurse kommen</h2>
<p>Die Wechselkurse stammen von Yahoo Finance und zeigen den aktuellen Mittelkurs am Devisenmarkt. Sie werden automatisch alle zwei Stunden aktualisiert. Die Veränderung zum Vortag zeigt, wie stark sich das Währungspaar zuletzt bewegt hat. Wechselkurse schwanken laufend; für Überweisungen und Kartenzahlungen gilt immer der Kurs deines Anbieters zum Zeitpunkt der Buchung.</p>'''

FX_TIPS_EN = """
<h2>How not to overpay abroad</h2>
<p>The rate above is the mid-market rate. As a private person you almost never get exactly that, because banks, card providers and exchange offices earn from the difference. Three things make the biggest difference in practice:</p>
<ul><li><b>Pay in the local currency.</b> If a card terminal or ATM asks whether to charge you in euros, choose the local currency. The instant conversion offered (“dynamic currency conversion”) is usually much more expensive.</li>
<li><b>Check your card's fees.</b> Many cards charge a surcharge for payments in foreign currencies. Some cards have no such fee; a look at the price list is worth it before you travel.</li>
<li><b>Do not exchange cash at the airport.</b> Exchange offices at airports and stations often have poor rates. Compare the offered rate with the mid-market rate above: the bigger the gap, the more expensive.</li></ul>
<h2>Where the rates come from</h2>
<p>The exchange rates come from Yahoo Finance and show the current mid-market rate. They are updated automatically every two hours. The change versus the previous day shows how much the currency pair moved recently. Exchange rates change constantly; for transfers and card payments your provider's rate at the time of booking always applies.</p>"""

def fx_faqs(f, to, lang='de'):
    if lang == 'en':
        nf, nt = FXN_EN[f], FXN_EN[to]
        return [('How much is 100 %s in %s?' % (nf, nt), 'That depends on the current exchange rate. The calculator above shows the amount live, the table the most common amounts.'),
                ('Why does my bank give me less %s?' % nt, 'The calculator shows the mid-market rate. Banks and exchange offices add a markup and sometimes fixed fees.'),
                ('How up to date is the rate?', 'The rates are updated automatically every two hours from Yahoo Finance. The date and time are shown right below the calculator.'),
                ('Does the calculator cost anything?', 'No. The currency converter is free, without sign-up and without ads. The calculation runs in your browser.')]
    nf, nt = FXN[f][0], FXN[to][0]
    return [('Wie viel sind 100 %s in %s?' % (nf, nt), 'Das hängt vom aktuellen Wechselkurs ab. Der Rechner oben zeigt den Betrag live, die Tabelle die gängigsten Beträge von 1 bis 5.000 %s.' % nf),
            ('Warum bekomme ich bei der Bank weniger %s?' % nt, 'Der Rechner zeigt den Mittelkurs am Devisenmarkt. Banken und Wechselstuben rechnen mit einem Aufschlag beziehungsweise Abschlag und teils mit festen Gebühren.'),
            ('Wie aktuell ist der Kurs?', 'Die Kurse werden automatisch alle zwei Stunden von Yahoo Finance aktualisiert. Datum und Uhrzeit des Stands stehen direkt unter dem Rechner.'),
            ('Kostet der Rechner etwas?', 'Nein. Der Währungsrechner ist kostenlos, ohne Anmeldung und ohne Werbung. Die Rechnung läuft in deinem Browser.')]

page(slug='waehrungsrechner', short='Währungsrechner', teaser='Live-Kurse für über 50 Währungen und Bitcoin', fx=('EUR', 'USD'),
 title='Währungsrechner mit Live-Kursen und Chart: über 50 Währungen und Bitcoin | Geld-Kompass',
 desc='Kostenloser Währungsrechner mit aktuellen Kursen für über 50 Währungen und Bitcoin: Euro, Dollar, Pfund, Franken, Lira, Lari, Baht, Dong und mehr. Mit Live-Chart und Umrechnungstabelle.',
 eyebrow='Währungen & Wechselkurse', h1='Währungsrechner: Beträge mit aktuellen Kursen umrechnen',
 lead='Betrag eingeben, Währungen wählen, fertig. Der Rechner nutzt aktuelle Mittelkurse vom Devisenmarkt und zeigt dir gleich eine Tabelle mit den gängigsten Beträgen.',
 calc=fx_calc(), js=fx_js('EUR', 'USD', 'waehrungsrechner'),
 body='\n<h2>Beliebte Umrechnungen</h2>\n<div class="more">%PAIRLINKS%</div>' + FX_TIPS,
 faqs=fx_faqs('EUR', 'USD'))

FX_PAIRS = [
 ('euro-in-dollar','EUR','USD','Euro in Dollar','Für Online-Shopping in den USA, Reisen nach Amerika oder den Blick aufs Depot: Der US-Dollar ist die wichtigste Währung der Welt. Viele Aktien, Rohstoffe und auch Gold werden in Dollar gehandelt.'),
 ('dollar-in-euro','USD','EUR','Dollar in Euro','Du hast Einnahmen, Preise oder Kontostände in US-Dollar und willst wissen, was das in Euro ist? Hier siehst du es mit aktuellem Kurs, inklusive Tabelle für typische Beträge.'),
 ('euro-in-pfund','EUR','GBP','Euro in Pfund','Für eine Reise nach London, Einkäufe bei britischen Shops oder eine Überweisung nach Großbritannien: So viel Pfund Sterling bekommst du aktuell für deine Euro.'),
 ('pfund-in-euro','GBP','EUR','Pfund in Euro','Preise, Gehalt oder Ersparnisse in Britischen Pfund? Der Rechner zeigt dir, wie viel das aktuell in Euro ist.'),
 ('euro-in-franken','EUR','CHF','Euro in Franken','Ob Urlaub in den Alpen, Pendeln in die Schweiz oder ein Einkauf in Zürich: Hier rechnest du Euro mit aktuellem Kurs in Schweizer Franken um.'),
 ('franken-in-euro','CHF','EUR','Franken in Euro','Lohn, Preise oder Erspartes in Schweizer Franken? Der Rechner zeigt dir den aktuellen Gegenwert in Euro.'),
 ('euro-in-tuerkische-lira','EUR','TRY','Euro in Türkische Lira','Für den Urlaub in der Türkei: Die Lira schwankt stark, deshalb lohnt sich vor jedem Umtausch ein Blick auf den aktuellen Kurs. Die Veränderung zum Vortag zeigt, wie stark sie sich zuletzt bewegt hat.'),
 ('euro-in-lari','EUR','GEL','Euro in Lari','Für Georgien-Reisen, ein Leben in Tiflis oder Überweisungen nach Georgien: So viel Georgische Lari bekommst du aktuell für deine Euro.'),
 ('euro-in-ringgit','EUR','MYR','Euro in Ringgit','Für Malaysia-Urlaub, Kuala Lumpur oder Penang: So viel Malaysische Ringgit bekommst du gerade für deine Euro.'),
 ('euro-in-dong','EUR','VND','Euro in Dong','Für Vietnam-Reisen: Beim Dong kommen schnell sehr große Zahlen zusammen. Der Rechner und die Tabelle zeigen dir auf einen Blick, wie viel deine Euro wert sind.'),
 ('euro-in-rubel','EUR','RUB','Euro in Rubel','Der aktuelle Kurs von Euro zu Russischem Rubel am Devisenmarkt. Beachte: Wegen Sanktionen und Kapitalverkehrsbeschränkungen weichen die tatsächlich erzielbaren Kurse oft deutlich ab.'),
 ('euro-in-zloty','EUR','PLN','Euro in Złoty','Für Einkäufe, Urlaub oder Arbeit in Polen: So viel Polnische Złoty bekommst du aktuell für deine Euro.'),
 ('bitcoin-in-euro','BTC','EUR','Bitcoin in Euro','Was ist ein Bitcoin gerade in Euro wert? Der Rechner zeigt den aktuellen Kurs, die Tabelle auch Bruchteile, denn du kannst Bitcoin in kleinen Stücken kaufen. Bitcoin schwankt stark; das ist eine Kursanzeige und keine Anlageberatung.'),
 ('euro-in-baht','EUR','THB','Euro in Baht','Für Thailand-Urlaub oder ein Leben als digitaler Nomade in Südostasien: So viel Thailändische Baht bekommst du aktuell für deine Euro.'),
]
for slug, f, to, name, intro in FX_PAIRS:
    page(slug=slug, short=name + ' umrechnen', teaser='%s live: 1 %s in %s' % (name, f, to), pair=True, fx=(f, to),
     title='%s umrechnen: aktueller Kurs und Tabelle | Geld-Kompass' % name,
     desc='%s umrechnen mit aktuellem Devisenkurs: Rechner, Umrechnungstabelle und Veränderung zum Vortag. Kostenlos und ohne Anmeldung.' % name,
     eyebrow='Währungsrechner', h1='%s umrechnen: Was ist dein Geld gerade wert?' % name, lead=intro,
     calc=fx_calc(), js=fx_js(f, to, slug), body=(BTC_TEXT if FXN[f][1] or FXN[to][1] else FX_TIPS) + '\n<h2>Weitere Währungen</h2>\n<div class="more">%PAIRLINKS%</div>', faqs=fx_faqs(f, to))

# ---------------------------------------------------------------- Englische Fassungen
def en_page(p):
    """Englische Seite zu einer deutschen Rechner-Seite."""
    if p.get('fx'):
        f, to = p['fx']; es = EN_FX_SLUG[p['slug']]; crypto = FXN[f][1] or FXN[to][1]
        if p['slug'] == 'waehrungsrechner':
            return dict(p, lang='en', slug=es, short='Currency converter', teaser='Live rates for 50+ currencies and bitcoin',
                title='Currency Converter with Live Rates and Chart: 50+ Currencies and Bitcoin | Money Compass',
                desc='Free currency converter with current rates for over 50 currencies and bitcoin: euro, dollar, pound, franc, lira, lari, baht, dong and more. With live chart and conversion table.',
                eyebrow='Currencies & exchange rates', h1='Currency converter: convert amounts at current rates',
                lead='Enter an amount, choose currencies, done. The converter uses current mid-market rates and shows a table of the most common amounts.',
                calc=fx_calc('en'), js=fx_js(f, to, es, 'en'), body='\n<h2>Popular conversions</h2>\n<div class="more">%PAIRLINKS%</div>' + FX_TIPS_EN, faqs=fx_faqs(f, to, 'en'))
        name = '%s to %s' % (FXN_EN[f], FXN_EN[to])
        return dict(p, lang='en', slug=es, short='Convert ' + name, teaser='%s live: 1 %s in %s' % (name, f, to),
            title='Convert %s: live rate and table | Money Compass' % name,
            desc='Convert %s at the current rate: calculator, conversion table and change versus the previous day. Free and without sign-up.' % name,
            eyebrow='Currency converter', h1='Convert %s: what is your money worth right now?' % name, lead=EN_FX_INTRO[es],
            calc=fx_calc('en'), js=fx_js(f, to, es, 'en'), body=(BTC_TEXT_EN if crypto else FX_TIPS_EN) + '\n<h2>More currencies</h2>\n<div class="more">%PAIRLINKS%</div>', faqs=fx_faqs(f, to, 'en'))
    e = EN_TXT[p['slug']]
    js = tr(p['js'], e['js'], p['slug'] + ' js').replace("'rechner/%s/'" % p['slug'], "'en/calculators/%s/'" % e['slug'])
    return dict(p, lang='en', slug=e['slug'], short=e['short'], teaser=e['teaser'], title=e['title'], desc=e['desc'], eyebrow=e['eyebrow'],
                h1=e['h1'], lead=e['lead'], calc=tr(p['calc'], e['calc'], p['slug'] + ' calc'), js=js, body=e['body'], faqs=e['faqs'])

PAGES_EN = [en_page(p) for p in PAGES]
for de, en in zip(PAGES, PAGES_EN):
    de['alt'] = BASE + 'en/calculators/' + en['slug'] + '/'
    en['alt'] = BASE + 'rechner/' + de['slug'] + '/'

def esc(s): return html.escape(s, quote=True)

def links(pages, cur, pair):
    return ''.join('<a href="../%s/">%s<small>%s</small></a>' % (p['slug'], esc(p['short']), esc(p['teaser'])) for p in pages if p['slug'] != cur and bool(p.get('pair')) == pair)

CTA = ('<div class="cta">'
 '<a href="/app/#overview"><i>'+LOGO+'</i><div><b>Mit deinen echten Zahlen weiterrechnen</b><span>Der kostenlose Geld-Kompass: Buchungen, Schulden-Plan, Depot und Freiheitstage. Ohne Anmeldung, deine Daten bleiben in deinem Browser.</span></div></a>'
 '<a href="' + KANAL + '" target="_blank" rel="noopener"><i><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="12" fill="#25d366"/><path d="M12 5.2a6.8 6.8 0 0 0-5.9 10.2l-.9 3.3 3.4-.9A6.8 6.8 0 1 0 12 5.2z" fill="none" stroke="#fff" stroke-width="1.5" stroke-linejoin="round"/><path d="M9.6 9.1c.2 2 1.8 3.7 3.9 4.2l.8-.9 1.4.7c-.2.8-.9 1.2-1.6 1.1-2.8-.3-5-2.5-5.3-5.3-.1-.8.4-1.4 1.1-1.6l.7 1.4z" fill="#fff"/></svg></i><div><b>Geld-Kompass auf WhatsApp</b><span>Jeden Sonntag ein kurzer Geld-Check und ein kleiner nächster Schritt. Kostenlos, deine Nummer bleibt privat.</span></div></a>'
 '<a href="' + BUCH + '" target="_blank" rel="noopener"><i><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5.5c2.5-1 5.2-1 8 .8 2.8-1.8 5.5-1.8 8-.8v13c-2.5-1-5.2-1-8 .8-2.8-1.8-5.5-1.8-8-.8z" fill="none" stroke="#e3b55a" stroke-width="1.6" stroke-linejoin="round"/><path d="M12 6.3v13" stroke="#e3b55a" stroke-width="1.6"/></svg></i><div><b>Das Buch dazu</b><span>„Der einfache Weg zur Finanziellen Freiheit“: Das Geldbaum-Prinzip in sieben Stufen.</span></div></a>'
 '</div>')

CTA_EN = ('<div class="cta">'
 '<a href="/app/?lang=en#overview"><i>'+LOGO+'</i><div><b>Continue with your real numbers</b><span>The free Money Compass: bookings, debt plan, portfolio and freedom days. No sign-up, your data stays in your browser.</span></div></a>'
 '<a href="/start/?lang=en"><i><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10" fill="none" stroke="#e3b55a" stroke-width="1.6"/><path d="M10 8l6 4-6 4z" fill="#e3b55a"/></svg></i><div><b>See how it works</b><span>A short animated tour: from a seed to your money tree, then one click on Start.</span></div></a>'
 '<a href="' + BUCH + '" target="_blank" rel="noopener"><i><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5.5c2.5-1 5.2-1 8 .8 2.8-1.8 5.5-1.8 8-.8v13c-2.5-1-5.2-1-8 .8-2.8-1.8-5.5-1.8-8-.8z" fill="none" stroke="#e3b55a" stroke-width="1.6" stroke-linejoin="round"/><path d="M12 6.3v13" stroke="#e3b55a" stroke-width="1.6"/></svg></i><div><b>The book behind it</b><span>“Der einfache Weg zur Finanziellen Freiheit”: the money tree principle in seven steps (German edition).</span></div></a>'
 '</div>')

WORKBOOK_NOTES = {'schulden': ('Aus der Übersicht wird dein Schuldenplan.', 'Im Arbeitsbuch sammelst du Forderungen, hältst tragbare Raten fest und vergleichst deine nächsten Schritte. So bleibt neben der Rechnung auch deine Entscheidung sichtbar.', 'Schulden-Übung ansehen'), 'ruecklagen': ('Gib deiner Rücklage einen festen Platz.', 'Halte Zweck, Zielbetrag und Termin im Arbeitsbuch fest. Die passende Übungsseite verbindet deinen Rücklagenplan mit den tatsächlich gespeicherten Monatsständen.', 'Rücklagen-Übung ansehen'), 'monatsabschluss': ('Was behältst du bei? Was änderst du?', 'Der Kompass zeigt deine Zahlen. Im Arbeitsbuch vergleichst du den letzten Monat, hältst Fortschritte fest und entscheidest, was du als Nächstes angehst.', 'Monatsauswertung ansehen')}
def workbook_note(slug):
    key = {'schuldenfrei-rechner':'schulden','notgroschen-rechner':'ruecklagen','freiheitstage-rechner':'monatsabschluss'}.get(slug)
    if not key: return ''
    title,text,label = WORKBOOK_NOTES[key]
    return '<aside class="workbook-note" aria-label="Passende Übung im Arbeitsbuch"><h2>'+esc(title)+'</h2><p>'+esc(text)+'</p><a href="/arbeitsbuch/#'+key+'">'+esc(label)+'</a></aside>'


def lang_js(me, other):
    """Sprache aus geteiltem Link (?lang=) oder gespeicherter Einstellung übernehmen und ggf. zur anderen Sprachfassung wechseln."""
    return ("<script>(function(){var K='geld-kompass-lang',q=new URLSearchParams(location.search).get('lang'),w=q;"
            "if(q==='de'||q==='en'){try{localStorage.setItem(K,q);}catch(e){}}else{try{w=localStorage.getItem(K);}catch(e){}}"
            "if((w==='de'||w==='en')&&w!=='%s')location.replace('%s'+location.search+location.hash);})();</script>" % (me, other.replace(BASE, '/')))

def render(p):
    en = p.get('lang') == 'en'
    url = BASE + ('en/calculators/' if en else 'rechner/') + p['slug'] + '/'
    de_url, en_url = (p['alt'], url) if en else (url, p['alt'])
    faq_ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in p['faqs']]}
    app_ld = {'@context': 'https://schema.org', '@type': 'WebApplication', 'name': p['short'] + (' · Money Compass' if en else ' · Geld-Kompass'),
              'url': url, 'applicationCategory': 'FinanceApplication', 'operatingSystem': 'Web', 'inLanguage': 'en' if en else 'de',
              'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'EUR'}, 'description': p['desc']}
    faqs = ''.join('<details><summary>%s</summary><p>%s</p></details>' % (esc(q), esc(a)) for q, a in p['faqs'])
    pages = PAGES_EN if en else PAGES
    body = p['body'].replace('%PAIRLINKS%', links(pages, p['slug'], True))
    T = (dict(all='All calculators', app=' · Open the Money Compass', appurl='/app/?lang=en', home='/?lang=en', faq='Frequently asked questions', more='More free calculators', sw='Deutsch', swurl=de_url,
              foot='Money Compass · companion to the book “Der einfache Weg zur Finanziellen Freiheit” · © FreedomByDan · General financial education, not investment, tax or legal advice. All calculations run in your browser; no data is sent.',
              logo='Money <span>Compass</span>', cta=CTA_EN, wb='')
         if en else
         dict(all='Alle Rechner', app=' · Zum Geld-Kompass', appurl='/app/', home='/', faq='Häufige Fragen', more='Weitere kostenlose Rechner', sw='English', swurl=en_url,
              foot='Geld-Kompass · Begleiter zum Buch „Der einfache Weg zur Finanziellen Freiheit“ · © FreedomByDan · Allgemeine Finanzbildung, keine Anlage-, Steuer- oder Rechtsberatung. Alle Berechnungen laufen in deinem Browser; es werden keine Daten übertragen.',
              logo='Geld-<span>Kompass</span>', cta=CTA, wb=workbook_note(p['slug'])))
    return f"""<!doctype html>
<html lang="{'en' if en else 'de'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
{lang_js('en' if en else 'de', de_url if en else en_url)}
<title>{esc(p['title'])}</title>
<meta name="description" content="{esc(p['desc'])}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="de" href="{de_url}">
<link rel="alternate" hreflang="en" href="{en_url}">
<link rel="alternate" hreflang="x-default" href="{de_url}">
<meta name="theme-color" content="#0E1730">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(p['title'])}">
<meta property="og:description" content="{esc(p['desc'])}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="{'en_GB' if en else 'de_DE'}">
<link rel="stylesheet" href="/rechner/rechner.css">
<link rel="stylesheet" href="/arbeitsbuch/hinweise.css">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="icon" type="image/png" sizes="32x32" href="/icons/favicon-32.png">
<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Geld-Kompass">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<script type="application/ld+json">{json.dumps(app_ld, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(faq_ld, ensure_ascii=False)}</script>
</head>
<body>
<header class="top"><div class="wrap"><a class="logo" href="{T['home']}">{LOGO}<b>{T['logo']}</b></a><nav><a href="../">{T['all']}</a><a class="hide-s" href="{T['appurl']}">{T['app']}</a> · <a class="langsw" href="{T['swurl'].replace(BASE, '/')}?lang={'de' if en else 'en'}" hreflang="{'de' if en else 'en'}">{T['sw']}</a></nav></div></header>
<main class="wrap">
<div class="eyebrow">{esc(p['eyebrow'])}</div>
<h1>{esc(p['h1'])}</h1>
<p class="lead">{esc(p['lead'])}</p>
<section class="card calc" aria-label="{'Calculator' if en else 'Rechner'}">{p['calc']}</section>
{T['wb']}
{T['cta']}
{body}
<h2>{T['faq']}</h2>
{faqs}
<h2>{T['more']}</h2>
<div class="more">{links(pages, p['slug'], False)}</div>
</main>
<footer><div class="wrap">{T['foot']}</div></footer>
<script src="/rechner/rechner.js"></script>
<script>{p['js']}</script>
</body>
</html>
"""

def hub(lang='de'):
    en = lang == 'en'
    pages = PAGES_EN if en else PAGES
    cards = ''.join('<a href="%s/">%s<small>%s</small></a>' % (p['slug'], esc(p['short']), esc(p['teaser'])) for p in pages if not p.get('pair'))
    pcards = ''.join('<a href="%s/">%s<small>%s</small></a>' % (p['slug'], esc(p['short']), esc(p['teaser'])) for p in pages if p.get('pair'))
    de_url, en_url = BASE + 'rechner/', BASE + 'en/calculators/'
    if en:
        t = 'Free Money Calculators: Savings, Inflation, Debt, Currency | Money Compass'
        d = 'Free money calculators without sign-up: savings plan, inflation, debt-free date, emergency fund, freedom days, subscription as investment and a currency converter with live rates.'
        txt = dict(eb='Free calculators', h1='Money calculators that bring clarity in a minute', lead='No sign-up, no ads. All calculations run in your browser. If you want to continue with your real numbers, use the full Money Compass.',
                   cur='Convert currencies', app='Open the Money Compass', appurl='/app/?lang=en', foot='Money Compass · © FreedomByDan · General financial education, not investment, tax or legal advice.', sw='Deutsch', swurl=de_url, logo='Money <span>Compass</span>', home='/?lang=en', cta=CTA_EN)
    else:
        t = 'Kostenlose Finanzrechner: Sparplan, Inflation, Schulden, Währung | Geld-Kompass'
        d = 'Kostenlose Finanzrechner ohne Anmeldung: Sparplan, Inflation, Schuldenfrei-Datum, Notgroschen, Freiheitstage, Abo als Aktie und Währungsrechner mit Live-Kursen.'
        txt = dict(eb='Kostenlose Rechner', h1='Finanzrechner, die in einer Minute Klarheit bringen', lead='Ohne Anmeldung, ohne Werbung. Alle Rechnungen laufen in deinem Browser. Wenn du mit deinen echten Zahlen weitermachen möchtest, nutze den vollständigen Geld-Kompass.',
                   cur='Währungen umrechnen', app='Zum Geld-Kompass', appurl='/app/', foot='Geld-Kompass · © FreedomByDan · Allgemeine Finanzbildung, keine Anlage-, Steuer- oder Rechtsberatung.', sw='English', swurl=en_url, logo='Geld-<span>Kompass</span>', home='/', cta=CTA)
    return f"""<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
{lang_js(lang, de_url if en else en_url)}
<title>{esc(t)}</title><meta name="description" content="{esc(d)}"><link rel="canonical" href="{en_url if en else de_url}">
<link rel="alternate" hreflang="de" href="{de_url}"><link rel="alternate" hreflang="en" href="{en_url}"><link rel="alternate" hreflang="x-default" href="{de_url}">
<meta name="theme-color" content="#0E1730">
<link rel="stylesheet" href="/rechner/rechner.css">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="icon" type="image/png" sizes="32x32" href="/icons/favicon-32.png">
<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">
<script src="/rechner/rechner.js"></script>
</head><body>
<header class="top"><div class="wrap"><a class="logo" href="{txt['home']}">{LOGO}<b>{txt['logo']}</b></a><nav><a href="{txt['appurl']}">{txt['app']}</a> · <a class="langsw" href="{txt['swurl'].replace(BASE, '/')}?lang={'de' if en else 'en'}">{txt['sw']}</a></nav></div></header>
<main class="wrap">
<div class="eyebrow">{txt['eb']}</div>
<h1>{txt['h1']}</h1>
<p class="lead">{txt['lead']}</p>
<div class="more">{cards}</div>
<h2>{txt['cur']}</h2>
<div class="more">{pcards}</div>
{txt['cta']}
</main>
<footer><div class="wrap">{txt['foot']}</div></footer>
</body></html>
"""

for lang, base, pages in (('de', 'rechner', PAGES), ('en', 'en/calculators', PAGES_EN)):
    os.makedirs(base, exist_ok=True)
    for p in pages:
        os.makedirs(base + '/' + p['slug'], exist_ok=True)
        open('%s/%s/index.html' % (base, p['slug']), 'w').write(render(p))
    open(base + '/index.html', 'w').write(hub(lang))
urls = [BASE, BASE + 'app/', BASE + 'start/', BASE + 'buchbegruessung/', BASE + 'arbeitsbuch/', BASE + 'rechner/', BASE + 'en/calculators/'] + \
       [BASE + 'rechner/' + p['slug'] + '/' for p in PAGES] + [BASE + 'en/calculators/' + p['slug'] + '/' for p in PAGES_EN]
open('sitemap.xml', 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    ''.join('<url><loc>%s</loc><lastmod>%s</lastmod></url>\n' % (u, TODAY) for u in urls) + '</urlset>\n')
print('ok', len(PAGES), 'Seiten je Sprache')
