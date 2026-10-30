"""Erzeugt die einzelnen Rechner-Seiten unter /rechner/ (statisches HTML für Google).
Aufruf im Repo-Hauptordner: python3 scripts/build_rechner.py"""
import json, os, html, datetime

BASE = 'https://geld-kompass.com/'
KANAL = 'https://whatsapp.com/channel/0029VbEHiDdLCoX7Bhggff2E'
BUCH = 'https://amzn.eu/d/01dK026o'
TODAY = datetime.date.today().isoformat()

LOGO = ('<svg viewBox="0 0 52 52" aria-hidden="true"><circle cx="26" cy="26" r="23" fill="none" stroke="#e3b55a" stroke-width="2"/>'
        '<circle cx="26" cy="26" r="17" fill="none" stroke="#e3b55a" stroke-width="1" opacity=".45"/>'
        '<path d="M26 7 L30 26 L26 45 L22 26 Z" fill="#e3b55a"/><path d="M26 7 L30 26 L22 26 Z" fill="#f3f1ea"/>'
        '<circle cx="26" cy="26" r="2.5" fill="#162447"/></svg>')

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
 desc='Inflationsrechner mit amtlichen Eurostat-Daten (HVPI) für Deutschland, Österreich und den Euroraum: Kaufkraftverlust zwischen zwei Jahren kostenlos berechnen.',
 eyebrow='Kaufkraft & Inflation', h1='Inflationsrechner: Was ist dein Geld von damals heute noch wert?',
 lead='Wähle Betrag und Jahre. Der Rechner nutzt die amtlichen Jahresdurchschnitte des Harmonisierten Verbraucherpreisindex (HVPI) von Eurostat.',
 calc='''
<div class="grid">
<label>Betrag (€)<input id="amt" inputmode="decimal" value="1000"></label>
<label>Land<select id="geo"><option value="DE">Deutschland</option><option value="AT">Österreich</option><option value="EA20">Euroraum</option></select></label>
<label>Von Jahr<select id="y0"></select></label>
<label>Bis Jahr<select id="y1"></select></label>
</div>
<div class="big" id="big">…</div><div id="bigsub" class="note" style="margin-top:0"></div>
<div class="res" id="res"></div>
<p class="note" id="src">Amtliche Daten werden geladen.</p>
<div class="share" id="share"></div>''',
 js='''
var G=GKR,DATA=null;
fetch('../../data/hicp_annual.json',{cache:'no-cache'}).then(function(r){return r.json();}).then(function(d){DATA=d;fill();}).catch(function(){G.$('big').textContent='–';G.$('src').textContent='Die amtlichen Daten sind gerade nicht erreichbar. Bitte später erneut versuchen.';});
function years(){var g=DATA[G.$('geo').value]||DATA.DE;return Object.keys(g.index).sort();}
function fill(){var ys=years(),a=G.$('y0'),b=G.$('y1'),pa=a.value,pb=b.value;
 a.innerHTML=b.innerHTML=ys.map(function(y){return '<option>'+y+'</option>';}).join('');
 a.value=ys.indexOf(pa)>-1?pa:(ys.indexOf('2010')>-1?'2010':ys[0]);b.value=ys.indexOf(pb)>-1?pb:ys[ys.length-1];run();}
G.$('geo').addEventListener('change',fill);
function run(){if(!DATA)return;var g=DATA[G.$('geo').value]||DATA.DE,ix=g.index,y0=G.$('y0').value,y1=G.$('y1').value,a=G.val('amt');
 if(!(y0 in ix)||!(y1 in ix))return;var f=ix[y1]/ix[y0],same=a*f,kauf=a/f,pct=(f-1)*100,n=Math.abs(+y1-+y0),pa=n?(Math.pow(f,1/n)-1)*100:0;
 var land=G.$('geo').selectedOptions[0].textContent;
 G.$('big').textContent=G.E(kauf);
 G.$('bigsub').textContent=+y1>=+y0?'Kaufkraft von '+G.E(a)+' aus '+y0+', gemessen in Preisen von '+y1:'Wert in Preisen von '+y1;
 G.$('res').innerHTML='<div><span>Für dasselbe brauchst du '+y1+'</span><b class="neg">'+G.E(same)+'</b></div><div><span>Preise insgesamt</span><b class="gold">'+(pct>=0?'+':'')+G.nf1.format(pct)+' %</b></div><div><span>Im Schnitt pro Jahr</span><b>'+G.nf1.format(pa)+' %</b></div>';
 G.$('src').innerHTML='Quelle: Eurostat, HVPI Jahresdurchschnitt ('+G.esc(land)+', 2015 = 100). Stand der Abfrage: '+G.esc((DATA.checked||'').slice(0,10))+'. Das letzte Jahr ist der zuletzt vollständig veröffentlichte Jahresdurchschnitt.';
 G.share(G.$('share'),G.E(a)+' aus dem Jahr '+y0+' haben '+y1+' nur noch die Kaufkraft von '+G.E(kauf)+' ('+land+', amtliche Eurostat-Daten).','rechner/inflationsrechner/');}
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
def esc(s): return html.escape(s, quote=True)

def other_links(cur):
    return ''.join('<a href="../%s/">%s<small>%s</small></a>' % (p['slug'], esc(p['short']), esc(p['teaser'])) for p in PAGES if p['slug'] != cur)

CTA = ('<div class="cta">'
 '<a href="../../#overview"><i>🧭</i><div><b>Mit deinen echten Zahlen weiterrechnen</b><span>Der kostenlose Geld-Kompass: Buchungen, Schulden-Plan, Depot und Freiheitstage. Ohne Anmeldung, deine Daten bleiben in deinem Browser.</span></div></a>'
 '<a href="' + KANAL + '" target="_blank" rel="noopener"><i>🌱</i><div><b>Geld-Kompass auf WhatsApp</b><span>Jeden Sonntag ein kurzer Geld-Check und ein kleiner nächster Schritt. Kostenlos, deine Nummer bleibt privat.</span></div></a>'
 '<a href="' + BUCH + '" target="_blank" rel="noopener"><i>📖</i><div><b>Das Buch dazu</b><span>„Der einfache Weg zur Finanziellen Freiheit“: Das Geldbaum-Prinzip in sieben Stufen.</span></div></a>'
 '</div>')

def render(p):
    url = BASE + 'rechner/' + p['slug'] + '/'
    faq_ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in p['faqs']]}
    app_ld = {'@context': 'https://schema.org', '@type': 'WebApplication', 'name': p['short'] + ' · Geld-Kompass',
              'url': url, 'applicationCategory': 'FinanceApplication', 'operatingSystem': 'Web', 'inLanguage': 'de',
              'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'EUR'}, 'description': p['desc']}
    faqs = ''.join('<details><summary>%s</summary><p>%s</p></details>' % (esc(q), esc(a)) for q, a in p['faqs'])
    return f'''<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(p['title'])}</title>
<meta name="description" content="{esc(p['desc'])}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#0E1730">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(p['title'])}">
<meta property="og:description" content="{esc(p['desc'])}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="de_DE">
<link rel="stylesheet" href="../rechner.css">
<script type="application/ld+json">{json.dumps(app_ld, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(faq_ld, ensure_ascii=False)}</script>
</head>
<body>
<header class="top"><div class="wrap"><a class="logo" href="../../">{LOGO}<b>Geld-<span>Kompass</span></b></a><nav><a href="../">Alle Rechner</a><a class="hide-s" href="../../"> · Zum Geld-Kompass</a></nav></div></header>
<main class="wrap">
<div class="eyebrow">{esc(p['eyebrow'])}</div>
<h1>{esc(p['h1'])}</h1>
<p class="lead">{esc(p['lead'])}</p>
<section class="card calc" aria-label="Rechner">{p['calc']}</section>
{CTA}
{p['body']}
<h2>Häufige Fragen</h2>
{faqs}
<h2>Weitere kostenlose Rechner</h2>
<div class="more">{other_links(p['slug'])}</div>
</main>
<footer><div class="wrap">Geld-Kompass · Begleiter zum Buch „Der einfache Weg zur Finanziellen Freiheit“ · © FreedomByDan · Allgemeine Finanzbildung, keine Anlage-, Steuer- oder Rechtsberatung. Alle Berechnungen laufen in deinem Browser; es werden keine Eingaben gespeichert oder übertragen.</div></footer>
<script src="../rechner.js"></script>
<script>{p['js']}</script>
</body>
</html>
'''

def hub():
    cards = ''.join('<a href="%s/">%s<small>%s</small></a>' % (p['slug'], esc(p['short']), esc(p['teaser'])) for p in PAGES)
    t = 'Kostenlose Finanzrechner: Sparplan, Inflation, Schulden, Notgroschen | Geld-Kompass'
    d = 'Sechs kostenlose Finanzrechner ohne Anmeldung: Sparplan, Inflation, Schuldenfrei-Datum, Notgroschen, Freiheitstage und was dein Abo angelegt wäre.'
    return f'''<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(t)}</title><meta name="description" content="{esc(d)}"><link rel="canonical" href="{BASE}rechner/">
<meta name="theme-color" content="#0E1730">
<link rel="stylesheet" href="rechner.css">
</head><body>
<header class="top"><div class="wrap"><a class="logo" href="../">{LOGO}<b>Geld-<span>Kompass</span></b></a><nav><a href="../">Zum Geld-Kompass</a></nav></div></header>
<main class="wrap">
<div class="eyebrow">Kostenlose Rechner</div>
<h1>Finanzrechner, die in einer Minute Klarheit bringen</h1>
<p class="lead">Ohne Anmeldung, ohne Werbung. Alle Rechnungen laufen in deinem Browser. Wenn du mit deinen echten Zahlen weitermachen möchtest, nutze den vollständigen Geld-Kompass.</p>
<div class="more">{cards}</div>
{CTA.replace('../../#overview', '../#overview')}
</main>
<footer><div class="wrap">Geld-Kompass · © FreedomByDan · Allgemeine Finanzbildung, keine Anlage-, Steuer- oder Rechtsberatung.</div></footer>
</body></html>
'''

os.makedirs('rechner', exist_ok=True)
for p in PAGES:
    os.makedirs('rechner/' + p['slug'], exist_ok=True)
    open('rechner/%s/index.html' % p['slug'], 'w').write(render(p))
open('rechner/index.html', 'w').write(hub())
urls = [BASE, BASE + 'start/', BASE + 'rechner/'] + [BASE + 'rechner/' + p['slug'] + '/' for p in PAGES]
open('sitemap.xml', 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    ''.join('<url><loc>%s</loc><lastmod>%s</lastmod></url>\n' % (u, TODAY) for u in urls) + '</urlset>\n')
print('ok', len(PAGES), 'Seiten')
