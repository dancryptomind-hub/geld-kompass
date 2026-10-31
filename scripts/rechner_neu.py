"""Drei weitere Rechner (deutsch und englisch). Wird von build_rechner.py eingebunden.
JS ist sprachneutral (G.EN), englische Seiten brauchen nur die Beschriftungen."""

DEBTROWS = ''.join('''<div class="drow"><label>Schuld %d (€)<input id="b%d" inputmode="decimal" value="%s"></label><label>Zins %% p. a.<input id="r%d" inputmode="decimal" value="%s"></label><label>Mindestrate (€)<input id="m%d" inputmode="decimal" value="%s"></label></div>''' % (i, i, b, i, r, i, m)
                   for i, b, r, m in [(1, '3000', '19.9', '90'), (2, '1200', '12.9', '50'), (3, '8000', '6.2', '160'), (4, '', '', '')])

NEW = []
NEW.append(dict(slug='schneeball-lawine-rechner', short='Schneeball oder Lawine?', teaser='Welche Schuld du zuerst abzahlst',
 title='Schneeball- oder Lawinen-Methode: Rechner für mehrere Schulden | Geld-Kompass',
 desc='Schneeball oder Lawine? Gib bis zu vier Schulden und dein Monatsbudget ein und vergleiche, welche Methode schneller schuldenfrei macht und wie viel Zinsen du sparst.',
 eyebrow='Schulden & Tilgung', h1='Schneeball oder Lawine: Welche Schuld zahlst du zuerst ab?',
 lead='Trag deine Schulden und den Betrag ein, den du jeden Monat insgesamt zahlen kannst. Der Rechner vergleicht beide Methoden mit deinen Zahlen.',
 calc='<div class="dgrid">' + DEBTROWS + '</div><div class="grid"><label>Insgesamt pro Monat (€)<input id="budget" inputmode="decimal" value="450"></label></div>' + '''
<div class="big" id="big"></div><div id="bigsub" class="note" style="margin-top:0"></div>
<div class="res" id="res"></div><div id="order" class="note"></div>
<p class="note">Lawine: Extra-Geld geht an die Schuld mit dem höchsten Zins. Schneeball: an die kleinste Schuld. Beide zahlen alle Mindestraten weiter. Vereinfachte Rechnung mit festen Zinsen, ohne Gebühren.</p>
<div class="share" id="share"></div>''',
 js='''
var G=GKR,EN=G.EN;
function rows(){var a=[];for(var i=1;i<=4;i++){var b=G.val('b'+i);if(b>0)a.push({n:(EN?'Debt ':'Schuld ')+i,b:b,r:G.val('r'+i),m:G.val('m'+i)});}return a;}
function sim(ds,budget,key){var d=ds.map(function(x){return {n:x.n,b:x.b,r:x.r,m:x.m,done:0};}),mo=0,int=0,order=[];
 while(d.some(function(x){return x.b>0.005;})&&mo<1200){mo++;var av=budget;d.forEach(function(x){if(x.b>0){var z=x.b*x.r/1200;x.b+=z;int+=z;}});
  d.forEach(function(x){if(x.b>0){var p=Math.min(x.m,x.b);x.b-=p;av-=p;}});if(av<0)return null;
  d.filter(function(x){return x.b>0.005;}).sort(key).forEach(function(x){if(av<=0)return;var p=Math.min(av,x.b);x.b-=p;av-=p;});
  d.forEach(function(x){if(x.b<=0.005&&!x.done){x.done=mo;order.push(x.n);}});}
 return mo>=1200?null:{m:mo,int:int,order:order};}
function run(){var ds=rows(),bu=G.val('budget'),need=ds.reduce(function(s,x){return s+x.m;},0);
 if(!ds.length){G.$('big').textContent='–';G.$('res').innerHTML='';G.$('order').textContent='';G.$('share').innerHTML='';return;}
 var a=sim(ds,bu,function(x,y){return y.r-x.r;}),s=sim(ds,bu,function(x,y){return x.b-y.b;});
 if(!a||!s||bu<need){G.$('big').textContent=EN?'Budget too low':'Budget zu niedrig';G.$('bigsub').textContent=(EN?'Your minimum payments add up to ':'Deine Mindestraten ergeben zusammen ')+G.E(need)+(EN?' a month, or the interest grows faster than you pay.':' im Monat, oder die Zinsen wachsen schneller, als du zahlst.');G.$('res').innerHTML='';G.$('order').textContent='';G.$('share').innerHTML='';return;}
 var diff=s.int-a.int;G.$('big').textContent=G.monthName(a.m);G.$('bigsub').textContent=(EN?'debt-free with the avalanche, in ':'schuldenfrei mit der Lawine, in ')+a.m+(EN?' months':' Monaten');
 G.$('res').innerHTML='<div><span>'+(EN?'Avalanche: interest':'Lawine: Zinsen')+'</span><b class="pos">'+G.E(a.int)+'</b></div><div><span>'+(EN?'Snowball: interest':'Schneeball: Zinsen')+'</span><b>'+G.E(s.int)+'</b></div><div><span>'+(EN?'Avalanche saves':'Lawine spart')+'</span><b class="gold">'+G.E(Math.max(0,diff))+'</b></div><div><span>'+(EN?'Snowball: debt-free':'Schneeball: schuldenfrei')+'</span><b>'+G.monthName(s.m)+'</b></div>';
 G.$('order').textContent=(EN?'Order paid off. Avalanche: ':'Reihenfolge erledigt. Lawine: ')+a.order.join(' → ')+(EN?' · Snowball: ':' · Schneeball: ')+s.order.join(' → ');
 G.share(G.$('share'),EN?'Avalanche or snowball? With my debts the avalanche saves '+G.E(Math.max(0,diff))+' in interest. I am debt-free in '+G.monthName(a.m)+'.':'Schneeball oder Lawine? Bei meinen Schulden spart die Lawine '+G.E(Math.max(0,diff))+' Zinsen. Schuldenfrei bin ich im '+G.monthName(a.m)+'.','rechner/schneeball-lawine-rechner/');}
G.bind(['b1','r1','m1','b2','r2','m2','b3','r3','m3','b4','r4','m4','budget'],run);''',
 body='''
<h2>Die Lawinen-Methode</h2>
<p>Du zahlst überall die Mindestrate. Jeder zusätzliche Euro geht an die Schuld mit dem höchsten Zins. Ist sie weg, wandert ihre Rate zur nächstteuren. Rechnerisch ist das fast immer der günstigste Weg.</p>
<h2>Die Schneeball-Methode</h2>
<p>Hier geht das Extra-Geld an die kleinste Schuld. Du hast schneller ein Erfolgserlebnis, weil die erste Schuld bald verschwindet. Das kostet meist etwas mehr Zinsen, hilft aber vielen, dranzubleiben.</p>
<h2>Was zählt am meisten?</h2>
<p>Der Unterschied zwischen beiden Methoden ist oft kleiner als gedacht. Viel wichtiger ist, dass du überhaupt mehr als die Mindestrate zahlst und keine neuen Schulden dazukommen. Im Geld-Kompass rechnet der Schulden-Plan mit deinen echten Schulden weiter.</p>''',
 faqs=[('Welche Methode ist besser?','Die Lawine spart rechnerisch meist mehr Zinsen. Der Schneeball motiviert durch schnelle Erfolge. Die beste Methode ist die, bei der du durchhältst.'),
       ('Was ist, wenn mein Budget nicht für alle Mindestraten reicht?','Dann hilft keine Methode allein. Sprich mit deinen Gläubigern oder einer kostenlosen Schuldnerberatung, zum Beispiel bei einer Verbraucherzentrale.'),
       ('Sollte ich parallel sparen?','Ein kleiner Notgroschen verhindert, dass neue Schulden entstehen. Danach lohnt sich bei teuren Schulden meist das schnelle Tilgen.')]))

NEW.append(dict(slug='vier-prozent-regel-rechner', short='4-Prozent-Regel-Rechner', teaser='Wie viel Vermögen du für ein Leben vom Depot brauchst',
 title='4-Prozent-Regel-Rechner: Wie viel Vermögen brauche ich? | Geld-Kompass',
 desc='Mit der 4-Prozent-Regel berechnen, wie viel Vermögen du für deine monatlichen Ausgaben brauchst und wann du es mit deiner Sparrate erreichst. Kostenlos und ohne Anmeldung.',
 eyebrow='Finanzielle Freiheit', h1='4-Prozent-Regel: Wie viel Vermögen brauchst du?',
 lead='Gib ein, wie viel du im Monat ausgibst und was du schon hast. Der Rechner zeigt deine Freiheitszahl und wann du sie mit deiner Sparrate erreichen könntest.',
 calc='''
<div class="grid">
<label>Ausgaben pro Monat (€)<input id="spend" inputmode="decimal" value="2000"></label>
<label>Andere Einnahmen pro Monat, z. B. Rente (€)<input id="other" inputmode="decimal" value="0"></label>
<label>Entnahmerate<select id="swr"><option value="3">3 % (vorsichtig)</option><option value="3.5">3,5 %</option><option value="4" selected>4 %</option></select></label>
<label>Schon angelegt (€)<input id="have" inputmode="decimal" value="20000"></label>
<label>Sparrate pro Monat (€)<input id="save" inputmode="decimal" value="500"></label>
<label>Rendite pro Jahr (%)<input id="ret" inputmode="decimal" value="6"></label>
</div>
<div class="big" id="big"></div><div id="bigsub" class="note" style="margin-top:0"></div>
<div class="res" id="res"></div>
<p class="note">Modellrechnung ohne Inflation, Kosten und Steuern. Die 4-Prozent-Regel stammt aus US-Studien zu Aktien und Anleihen und ist keine Garantie. Keine Anlageberatung.</p>
<div class="share" id="share"></div>''',
 js='''
var G=GKR,EN=G.EN;
function run(){var sp=G.val('spend'),o=G.val('other'),w=(+G.$('swr').value)/100,h=G.val('have'),s=G.val('save'),r=G.val('ret')/100,need=Math.max(0,sp-o)*12,goal=w>0?need/w:0,i=r/12,m=0,v=h;
 while(v<goal&&m<1200){v=v*(1+i)+s;m++;}
 G.$('big').textContent=G.E(goal);G.$('bigsub').textContent=EN?'your freedom number ('+G.nf1.format(1/w)+' times your yearly spending)':'deine Freiheitszahl ('+G.nf1.format(1/w)+'-mal deine Jahresausgaben)';
 G.$('res').innerHTML='<div><span>'+(EN?'Already reached':'Schon erreicht')+'</span><b class="gold">'+G.nf0.format(goal>0?Math.min(100,h/goal*100):100)+' %</b></div><div><span>'+(EN?'Still missing':'Fehlen noch')+'</span><b>'+G.E(Math.max(0,goal-h))+'</b></div><div><span>'+(EN?'Reached in the model':'Im Modell erreicht')+'</span><b class="pos">'+(h>=goal?(EN?'already ✓':'schon jetzt ✓'):m<1200?G.monthName(m)+' ('+G.nf1.format(m/12)+(EN?' yrs':' J.')+')':(EN?'not with these numbers':'mit diesen Zahlen nicht'))+'</b></div>';
 G.share(G.$('share'),EN?'My freedom number by the 4 % rule: '+G.E(goal)+'. In the model I reach it in '+(m<1200?G.monthName(m):'–')+'.':'Meine Freiheitszahl nach der 4-%-Regel: '+G.E(goal)+'. Im Modell erreiche ich sie im '+(m<1200?G.monthName(m):'–')+'.','rechner/vier-prozent-regel-rechner/');}
G.bind(['spend','other','swr','have','save','ret'],run);''',
 body='''
<h2>Was die 4-Prozent-Regel sagt</h2>
<p>Studien aus den USA haben untersucht, wie viel man aus einem Depot aus Aktien und Anleihen jedes Jahr entnehmen kann, ohne dass es in 30 Jahren aufgebraucht ist. Ergebnis: Im ersten Jahr etwa 4 Prozent, danach an die Inflation angepasst. Umgekehrt heißt das: Du brauchst etwa das 25-Fache deiner Jahresausgaben.</p>
<h2>Warum vorsichtiger oft besser ist</h2>
<p>Wer früh aufhört zu arbeiten, braucht das Geld deutlich länger als 30 Jahre. Viele rechnen deshalb mit 3 bis 3,5 Prozent. Steuern, Kosten und schlechte Börsenjahre direkt zu Beginn können den Plan zusätzlich belasten.</p>
<h2>Der Hebel liegt bei den Ausgaben</h2>
<p>Jeder Euro, den du dauerhaft weniger ausgibst, senkt deine Freiheitszahl um das 25-Fache. 100 € weniger Ausgaben im Monat sind 30.000 € weniger nötiges Vermögen. Im Geld-Kompass siehst du, wo dein Geld hinfließt.</p>''',
 faqs=[('Ist die 4-Prozent-Regel sicher?','Nein, sie ist eine Faustregel aus historischen Daten. Zukünftige Renditen können niedriger ausfallen. Eine niedrigere Entnahmerate gibt mehr Sicherheit.'),
       ('Zählt die gesetzliche Rente mit?','Ja. Trag sie als andere Einnahme ein. Dann sinkt der Betrag, den dein Depot liefern muss.'),
       ('Gilt die Regel auch in Deutschland?','Das Prinzip ja. Beachte aber Abgeltungsteuer, Kosten und dass die Studien auf US-Märkten beruhen.')]))

NEW.append(dict(slug='kreditkarten-rechner', short='Kreditkarten-Rechner', teaser='Was dich die Mindestrate wirklich kostet',
 title='Kreditkarten-Rechner: Was kostet die Mindestrate wirklich? | Geld-Kompass',
 desc='Kreditkarten-Teilzahlung berechnen: Wie lange dauert die Rückzahlung, wenn du nur die Mindestrate zahlst, und wie viel sparst du mit einem festen Betrag? Kostenlos.',
 eyebrow='Schulden & Tilgung', h1='Kreditkarten-Rechner: Die Mindestraten-Falle',
 lead='Bei der Teilzahlung sinkt die Mindestrate mit der Schuld. Dadurch dauert die Rückzahlung oft viele Jahre. Vergleiche das mit einem festen Monatsbetrag.',
 calc='''
<div class="grid">
<label>Offener Betrag (€)<input id="bal" inputmode="decimal" value="3000"></label>
<label>Zins pro Jahr (%)<input id="apr" inputmode="decimal" value="19.9"></label>
<label>Mindestrate (% vom Saldo)<input id="minp" inputmode="decimal" value="3"></label>
<label>Mindestens (€)<input id="minf" inputmode="decimal" value="25"></label>
<label>Fester Betrag pro Monat (€)<input id="fix" inputmode="decimal" value="150"></label>
</div>
<div class="big" id="big"></div><div id="bigsub" class="note" style="margin-top:0"></div>
<div class="res" id="res"></div>
<p class="note">Vereinfachte Rechnung ohne neue Käufe und Gebühren. Die genauen Bedingungen stehen in deinem Kartenvertrag.</p>
<div class="share" id="share"></div>''',
 js='''
var G=GKR,EN=G.EN;
function sim(b,r,f){var m=0,int=0;while(b>0.005&&m<1200){var z=b*r/1200;int+=z;b+=z;var p=f(b);if(p<=z+0.005&&p<b)return null;b-=Math.min(p,b);m++;}return m>=1200?null:{m:m,int:int};}
function run(){var b=G.val('bal'),r=G.val('apr'),mp=G.val('minp')/100,mf=G.val('minf'),fx=G.val('fix');
 var a=sim(b,r,function(x){return Math.max(mf,x*mp);}),c=fx>0?sim(b,r,function(){return fx;}):null;
 G.$('big').textContent=a?(a.m>=24?G.nf1.format(a.m/12)+(EN?' years':' Jahre'):a.m+(EN?' months':' Monate')):(EN?'never':'nie');G.$('bigsub').textContent=EN?'with minimum payments only':'nur mit der Mindestrate';
 G.$('res').innerHTML='<div><span>'+(EN?'Interest with minimum':'Zinsen mit Mindestrate')+'</span><b class="neg">'+(a?G.E(a.int):'–')+'</b></div><div><span>'+(EN?'With fixed amount':'Mit festem Betrag')+'</span><b class="pos">'+(c?c.m+(EN?' months':' Monate'):(EN?'amount too low':'Betrag zu niedrig'))+'</b></div><div><span>'+(EN?'Interest with fixed amount':'Zinsen mit festem Betrag')+'</span><b>'+(c?G.E(c.int):'–')+'</b></div><div><span>'+(EN?'You save':'Du sparst')+'</span><b class="gold">'+(a&&c?G.E(Math.max(0,a.int-c.int)):'–')+'</b></div>';
 G.share(G.$('share'),a&&c?(EN?'Only the minimum payment on my card would take '+G.nf1.format(a.m/12)+' years. With '+G.E(fx)+' a month it is '+c.m+' months and I save '+G.E(a.int-c.int)+' in interest.':'Nur mit der Mindestrate bräuchte ich '+G.nf1.format(a.m/12)+' Jahre. Mit '+G.E(fx)+' im Monat sind es '+c.m+' Monate und ich spare '+G.E(a.int-c.int)+' Zinsen.'):(EN?'Credit card calculator':'Kreditkarten-Rechner'),'rechner/kreditkarten-rechner/');}
G.bind(['bal','apr','minp','minf','fix'],run);''',
 body='''
<h2>Warum die Mindestrate so teuer ist</h2>
<p>Die Mindestrate ist meist ein kleiner Prozentsatz des offenen Betrags. Sinkt die Schuld, sinkt auch die Rate. Der größte Teil geht anfangs an Zinsen, und die Rückzahlung zieht sich über viele Jahre. Für die Bank ist das ein gutes Geschäft.</p>
<h2>Der Ausweg: ein fester Betrag</h2>
<p>Zahlst du jeden Monat denselben festen Betrag, sinkt die Schuld immer schneller, weil der Zinsanteil kleiner wird. Stell die Teilzahlung wenn möglich auf einen festen Betrag um und nutze die Karte nicht weiter, bis sie abbezahlt ist.</p>
<h2>Umschulden prüfen</h2>
<p>Ein Ratenkredit kostet oft deutlich weniger Zinsen als die Kreditkarte. Das lohnt sich aber nur, wenn die Karte danach nicht wieder belastet wird. Im Geld-Kompass zeigt der Schulden-Plan, was eine Umschuldung bringen könnte.</p>''',
 faqs=[('Wie hoch sind Kreditkartenzinsen in Deutschland?','Für die Teilzahlung oft 14 bis 25 Prozent pro Jahr. Den genauen Satz findest du in deiner Abrechnung oder im Vertrag.'),
       ('Kann ich die Mindestrate ändern?','Bei vielen Banken lässt sich der monatliche Betrag in der App oder telefonisch erhöhen oder auf vollständige Zahlung umstellen.'),
       ('Was mache ich, wenn ich nicht mehr zahlen kann?','Sprich frühzeitig mit der Bank und hol dir Hilfe bei einer kostenlosen Schuldnerberatung.')]))

EN_NEW = {
'schneeball-lawine-rechner': dict(slug='debt-snowball-avalanche-calculator', short='Snowball or avalanche?', teaser='Which debt to pay off first',
 title='Debt Snowball vs. Avalanche Calculator | Money Compass',
 desc='Snowball or avalanche? Enter up to four debts and your monthly budget and compare which method gets you debt-free faster and how much interest you save.',
 eyebrow='Debt & repayment', h1='Snowball or avalanche: which debt should you pay off first?',
 lead='Enter your debts and the total amount you can pay each month. The calculator compares both methods with your numbers.',
 calc=[('Schuld 1 (€)','Debt 1 (€)'),('Schuld 2 (€)','Debt 2 (€)'),('Schuld 3 (€)','Debt 3 (€)'),('Schuld 4 (€)','Debt 4 (€)'),('Zins % p. a.','Rate % APR'),('Mindestrate (€)','Minimum (€)'),('Insgesamt pro Monat (€)','Total per month (€)'),
       ('Lawine: Extra-Geld geht an die Schuld mit dem höchsten Zins. Schneeball: an die kleinste Schuld. Beide zahlen alle Mindestraten weiter. Vereinfachte Rechnung mit festen Zinsen, ohne Gebühren.','Avalanche: extra money goes to the debt with the highest rate. Snowball: to the smallest balance. Both keep paying every minimum. Simplified, fixed rates, no fees.')],
 body='''
<h2>The avalanche method</h2>
<p>You pay the minimum everywhere. Every extra dollar or euro goes to the debt with the highest interest rate. Once it is gone, its payment moves to the next most expensive one. Mathematically this is almost always the cheapest way.</p>
<h2>The snowball method</h2>
<p>Here the extra money goes to the smallest balance. You get a quick win because the first debt disappears soon. It usually costs a little more interest, but helps many people stay on track.</p>
<h2>What matters most</h2>
<p>The difference between the two is often smaller than expected. Far more important is paying more than the minimum at all and not adding new debt. The Money Compass debt plan keeps calculating with your real debts.</p>''',
 faqs=[('Which method is better?','The avalanche usually saves more interest. The snowball motivates with quick wins. The best method is the one you stick with.'),
       ('What if my budget does not cover all minimum payments?','Then no method alone will help. Talk to your creditors or a free debt counselling service.'),
       ('Should I save at the same time?','A small emergency fund prevents new debt. After that, paying off expensive debt quickly usually pays off.')]),
'vier-prozent-regel-rechner': dict(slug='4-percent-rule-calculator', short='4 % rule calculator', teaser='How much you need to live off your portfolio',
 title='4 Percent Rule Calculator: How much do I need to retire? | Money Compass',
 desc='Use the 4 % rule to calculate how much wealth you need for your monthly spending and when you could reach it with your savings rate. Free, no sign-up.',
 eyebrow='Financial freedom', h1='The 4 % rule: how much do you need?',
 lead='Enter how much you spend each month and what you already have. The calculator shows your freedom number and when your savings could get you there.',
 calc=[('Ausgaben pro Monat (€)','Spending per month (€)'),('Andere Einnahmen pro Monat, z. B. Rente (€)','Other income per month, e.g. pension (€)'),('Entnahmerate','Withdrawal rate'),('3 % (vorsichtig)','3 % (cautious)'),('3,5 %','3.5 %'),
       ('Schon angelegt (€)','Already invested (€)'),('Sparrate pro Monat (€)','Savings per month (€)'),('Rendite pro Jahr (%)','Return per year (%)'),
       ('Modellrechnung ohne Inflation, Kosten und Steuern. Die 4-Prozent-Regel stammt aus US-Studien zu Aktien und Anleihen und ist keine Garantie. Keine Anlageberatung.','Model calculation without inflation, costs or taxes. The 4 % rule comes from US studies on stocks and bonds and is no guarantee. Not investment advice.')],
 body='''
<h2>What the 4 % rule says</h2>
<p>US studies looked at how much you can withdraw each year from a portfolio of stocks and bonds without running out within 30 years. The answer: about 4 % in the first year, then adjusted for inflation. Put the other way round, you need about 25 times your yearly spending.</p>
<h2>Why more caution often makes sense</h2>
<p>If you stop working early, the money has to last much longer than 30 years. Many therefore plan with 3 to 3.5 %. Taxes, costs and bad market years right at the start can put extra strain on the plan.</p>
<h2>The lever is your spending</h2>
<p>Every dollar or euro you spend less each month lowers your freedom number by 25 times as much per year. Spending 100 less a month means 30,000 less you need. The Money Compass shows where your money goes.</p>''',
 faqs=[('Is the 4 % rule safe?','No, it is a rule of thumb based on history. Future returns may be lower. A lower withdrawal rate gives more safety.'),
       ('Does a pension count?','Yes. Enter it as other income, so your portfolio needs to deliver less.'),
       ('Does it apply outside the US?','The principle does. Consider local taxes, costs and that the studies are based on US markets.')]),
'kreditkarten-rechner': dict(slug='credit-card-payoff-calculator', short='Credit card payoff calculator', teaser='What the minimum payment really costs you',
 title='Credit Card Minimum Payment Calculator | Money Compass',
 desc='Credit card payoff calculator: how long repayment takes with minimum payments only and how much a fixed monthly amount saves. Free, no sign-up.',
 eyebrow='Debt & repayment', h1='Credit card calculator: the minimum payment trap',
 lead='With minimum payments the payment shrinks along with the balance, so paying off often takes many years. Compare that with a fixed monthly amount.',
 calc=[('Offener Betrag (€)','Balance (€)'),('Zins pro Jahr (%)','APR (%)'),('Mindestrate (% vom Saldo)','Minimum payment (% of balance)'),('Mindestens (€)','At least (€)'),('Fester Betrag pro Monat (€)','Fixed amount per month (€)'),
       ('Vereinfachte Rechnung ohne neue Käufe und Gebühren. Die genauen Bedingungen stehen in deinem Kartenvertrag.','Simplified, without new purchases or fees. Your card agreement has the exact terms.')],
 body='''
<h2>Why the minimum payment is so expensive</h2>
<p>The minimum payment is usually a small percentage of the balance. As the debt shrinks, so does the payment. At first most of it goes to interest, and repayment drags on for years. For the card issuer, that is good business.</p>
<h2>The way out: a fixed amount</h2>
<p>If you pay the same fixed amount every month, the balance falls faster and faster because the interest part shrinks. Set up a fixed payment if you can and stop using the card until it is paid off.</p>
<h2>Consider consolidating</h2>
<p>A personal loan often costs much less interest than a credit card. It only pays off if you don't run the card up again. The Money Compass debt plan shows what refinancing could bring.</p>''',
 faqs=[('How high is credit card interest?','In the US often 20 % APR or more, in Germany 14 to 25 % for revolving credit. Your statement shows your exact rate.'),
       ('Can I change my minimum payment?','Many issuers let you pay more or set up autopay for a fixed amount or the full balance in the app.'),
       ('What if I can no longer pay?','Talk to your card issuer early and get help from a free, nonprofit credit counselling service.')]),
}
