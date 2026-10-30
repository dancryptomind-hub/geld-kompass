"""Englische Fassungen der Rechner-Seiten (/en/calculators/...).
Je Rechner: englische Adresse, Texte, FAQ und Ersetzungen für Rechner-HTML (calc) und Skript (js).
Wird von build_rechner.py eingebunden. Deutsche Texte ändern -> hier die englische Entsprechung prüfen."""

EN = {}

EN['sparplan-rechner'] = dict(
 slug='savings-plan-calculator', short='Savings plan calculator', teaser='What a monthly savings amount can grow into',
 title='Savings Plan Calculator: What does €100 a month become? | Money Compass',
 desc='Free savings plan and compound interest calculator: enter your monthly amount, time frame and assumed return and instantly see what it could grow into.',
 eyebrow='Savings plan & compound interest', h1='Savings plan calculator: what will your monthly amount become?',
 lead='Enter how much you want to put aside each month. The calculator shows how much you pay in yourself and how much comes from compound interest.',
 calc=[('Monatliche Rate (€)','Monthly amount (€)'),('Laufzeit (Jahre)','Time frame (years)'),('Angenommene Rendite pro Jahr (%)','Assumed annual return (%)'),('Startbetrag (€)','Starting amount (€)'),
       ('Modellrechnung mit gleichbleibender Rendite und monatlicher Verzinsung, ohne Kosten und Steuern. Echte Märkte schwanken, auch mit Verlustjahren. Keine Anlageberatung.','Model calculation with a constant return and monthly compounding, without costs or taxes. Real markets fluctuate, including years with losses. Not investment advice.')],
 js=[("'nach '+n+' Jahren bei '+G.nf1.format(r*100)+' % pro Jahr (rechnerisch)'","'after '+n+' years at '+G.nf1.format(r*100)+' % per year (model)'"),
     ('Selbst eingezahlt','Paid in yourself'),('Zinseszins-Anteil','From compound interest'),('Anteil Zinseszins','Share of compound interest'),
     ("<th>Nach</th><th>Eingezahlt</th><th>Wert</th>","<th>After</th><th>Paid in</th><th>Value</th>"),("' Jahren</td>","' years</td>"),
     ("G.E(m)+' im Monat über '+n+' Jahre: Bei '+G.nf1.format(r*100)+' % pro Jahr werden daraus rechnerisch '+G.E(v)+'. Selbst eingezahlt sind nur '+G.E(paid)+'.'",
      "G.E(m)+' a month for '+n+' years: at '+G.nf1.format(r*100)+' % per year that could grow to '+G.E(v)+'. Only '+G.E(paid)+' of it is paid in by me.'")],
 body='''
<h2>How the savings plan calculator works</h2>
<p>Every month your amount is added, and the existing balance keeps growing at the assumed return. That is compound interest: the returns of previous years work for you too. At first the effect looks small; after 15 to 20 years it often makes up a large part of the final value.</p>
<p>The calculator converts the annual return into an equivalent monthly rate and compounds every month. Costs, taxes and inflation are left out so the mechanics stay clearly visible.</p>
<h2>What return is realistic?</h2>
<p>Broadly diversified global equity ETFs have historically returned roughly 6 to 8 percent per year over long periods, with strong swings and years of clear losses. Savings accounts and bonds usually return less. Past returns are no guarantee, so try several scenarios, for example 4, 6 and 8 percent.</p>
<h2>Time is the biggest lever</h2>
<p>Starting 10 years earlier often means you need a much smaller monthly amount for the same goal. That is why it pays to start with a small amount instead of waiting for the perfect moment. The Money Compass shows you what monthly amount your budget really allows.</p>''',
 faqs=[('What is the compound interest effect?','Returns are reinvested and earn returns themselves. That is why an amount does not grow evenly over time but faster and faster.'),
       ('Are taxes and costs included?','No. The calculator shows the pure mechanics. In practice, fund costs, account fees and taxes reduce the result.'),
       ('Is this investment advice?','No. It is a model calculation for financial education. Which investment suits you depends on your situation, time frame and risk tolerance.')])

EN['inflationsrechner'] = dict(
 slug='inflation-calculator', short='Inflation calculator', teaser='What your money from back then is worth today',
 title='Inflation Calculator: What is €1,000 from back then worth today? | Money Compass',
 desc='Inflation calculator with official data for Germany, Austria, the euro area, the USA and the UK: calculate the loss of purchasing power between two years for free.',
 eyebrow='Purchasing power & inflation', h1='Inflation calculator: what is your money from back then worth today?',
 lead='Choose an amount and two years. The calculator uses official annual averages from Eurostat (HICP), the U.S. Bureau of Labor Statistics and the UK Office for National Statistics.',
 calc=[('<span id="amtL">Betrag (€)</span>','<span id="amtL">Amount (€)</span>'),('>Land<','>Country<'),('>Deutschland<','>Germany<'),('>Österreich<','>Austria<'),('>Euroraum<','>Euro area<'),('>Großbritannien<','>United Kingdom<'),
       ('Von Jahr','From year'),('Bis Jahr','To year'),('Amtliche Daten werden geladen.','Loading official data.')],
 js=[("'Die amtlichen Daten sind gerade nicht erreichbar. Bitte später erneut versuchen.'","'The official data is not available right now. Please try again later.'"),
     ("'Betrag ('","'Amount ('"),
     ("'Kaufkraft von '+F(a)+' aus '+y0+', gemessen in Preisen von '+y1:'Wert in Preisen von '+y1","'Purchasing power of '+F(a)+' from '+y0+', measured in '+y1+' prices':'Value in '+y1+' prices'"),
     ("'<div><span>Für dasselbe brauchst du '+y1+'</span>","'<div><span>For the same you need in '+y1+'</span>"),('Preise insgesamt','Prices overall'),('Im Schnitt pro Jahr','Average per year'),
     ("'Quelle: '+G.esc(g.source||'Eurostat, HVPI Jahresdurchschnitt')+' ('+G.esc(land)+', Jahresdurchschnitt, 2015 = 100). Stand der Abfrage: '+G.esc((DATA.checked||'').slice(0,10))+'. Das letzte Jahr ist der zuletzt vollständig veröffentlichte Jahresdurchschnitt.'",
      "'Source: '+G.esc(g.source||'Eurostat, HICP annual average')+' ('+G.esc(land)+', annual average, 2015 = 100). Retrieved: '+G.esc((DATA.checked||'').slice(0,10))+'. The latest year is the most recent fully published annual average.'"),
     ("F(a)+' aus dem Jahr '+y0+' haben '+y1+' nur noch die Kaufkraft von '+F(kauf)+' ('+land+', amtliche Daten).'","F(a)+' from '+y0+' only had the purchasing power of '+F(kauf)+' in '+y1+' ('+land+', official data).'"),
     ("new Intl.NumberFormat('de-DE'","new Intl.NumberFormat('en-GB'")],
 body='''
<h2>What the inflation calculator shows</h2>
<p>Inflation means that the same amount of money buys less later on. The calculator compares the price index of two years. If the general price level has risen by 40 percent, for example, you need €1,400 instead of €1,000 for the same shopping. Put the other way round, €1,000 from back then only has the purchasing power of about €714 today.</p>
<h2>Where the figures come from</h2>
<p>For Europe the calculator uses the Harmonised Index of Consumer Prices (HICP) from Eurostat, the official measure that is comparable across Europe. For the USA it uses the consumer price index CPI-U of the U.S. Bureau of Labor Statistics, for the UK the CPI of the Office for National Statistics. Each year is the annual average.</p>
<h2>What this means for your money</h2>
<p>Money that sits in a current account for years without interest loses purchasing power, even if the balance stays the same. You still need an emergency fund that is available immediately. For money you will not need for many years, it is worth asking how it can at least keep up with inflation. The Money Compass shows you how much of your money is affected.</p>''',
 faqs=[('Is this the official inflation rate?','Yes. The values come directly from official statistics (Eurostat, BLS, ONS) as annual averages and are updated automatically.'),
       ('Why does my perceived inflation differ?','The index measures an average basket of goods. If you spend a lot on food, energy or rent, you often feel price increases more strongly.'),
       ('Why is the current year missing?','An annual average is only final once the year is over. The Money Compass shows the current monthly rate in its purchasing power check.')])

EN['abo-als-aktie'] = dict(
 slug='subscription-as-investment', short='Consumer or owner?', teaser='What your subscription or habit would be worth invested',
 title='Consumer or owner? What would your subscription be as an investment? | Money Compass',
 desc='Netflix, coffee, cigarettes or phone contract: calculate for free what a regular expense has cost you over the years and what it could have become if invested.',
 eyebrow='Consumer or owner?', h1='What would your subscription have become if you had invested it?',
 lead='Every regular expense makes a company richer. Calculate what a habit costs you over the years and what the same amount could have become if invested.',
 calc=[('data-t="Streaming-Abo" data-a="13.99" data-p="m">Streaming 13,99 €/Monat','data-t="Streaming subscription" data-a="13.99" data-p="m">Streaming €13.99/month'),
       ('data-t="Coffee to go" data-a="3.5" data-p="d">Kaffee 3,50 €/Tag','data-t="Coffee to go" data-a="3.5" data-p="d">Coffee €3.50/day'),
       ('data-t="Zigaretten" data-a="9" data-p="d">Zigaretten 9 €/Tag','data-t="Cigarettes" data-a="9" data-p="d">Cigarettes €9/day'),
       ('data-t="Lieferdienst" data-a="25" data-p="w">Lieferdienst 25 €/Woche','data-t="Food delivery" data-a="25" data-p="w">Food delivery €25/week'),
       ('Energy-Drink 2 €/Tag','Energy drink €2/day'),
       ('Wofür?<input id="what" value="Streaming-Abo">','What for?<input id="what" value="Streaming subscription">'),('Betrag (€)<input id="amt" inputmode="decimal" value="13,99">','Amount (€)<input id="amt" inputmode="decimal" value="13.99">'),
       ('Wie oft?','How often?'),('>pro Tag<','>per day<'),('>pro Woche<','>per week<'),('>pro Monat<','>per month<'),('Zeitraum (Jahre)','Time frame (years)'),('Angenommene Rendite pro Jahr (%)','Assumed annual return (%)'),
       ('Die Rendite ist eine Annahme, etwa für einen breit gestreuten Welt-ETF im langjährigen Mittel. Einzelne Aktien können stark schwanken und auch alles verlieren. Modellrechnung ohne Kosten und Steuern, keine Anlageberatung.',
        'The return is an assumption, roughly the long-term average of a broadly diversified global ETF. Individual shares can fluctuate strongly and even lose everything. Model calculation without costs or taxes, not investment advice.')],
 js=[(".replace('.',',')",""),("'deine Ausgabe'","'your expense'"),
     ("'<div><span>Ausgegeben in '+n+' Jahren</span>","'<div><span>Spent in '+n+' years</span>"),('Angelegt rechnerisch','If invested (model)'),('>Unterschied<','>Difference<'),('>Pro Monat<','>Per month<'),
     ("w+' für '+G.E(m)+' im Monat: In '+n+' Jahren sind das '+G.E(spent)+' ausgegeben. Angelegt wären es bei '+G.nf1.format(r*100)+' % pro Jahr rechnerisch '+G.E(v)+'.'",
      "w+' for '+G.E(m)+' a month: in '+n+' years that is '+G.E(spent)+' spent. Invested at '+G.nf1.format(r*100)+' % per year it could have become '+G.E(v)+'.'")],
 body='''
<h2>Consumer or owner</h2>
<p>When you buy a coffee every day, the chain, the roaster and many others earn from it. As a customer you pay; as an owner, for example through shares or a broadly diversified fund, you would share in such profits. This question runs through the book behind the Money Compass.</p>
<h2>It is not about giving things up</h2>
<p>Nobody has to give up everything. The calculator simply makes visible what a small, regular expense means over a long time. Often it is enough to halve one of several habits and put the difference aside automatically.</p>
<h2>Calculating with real companies</h2>
<p>In the free Money Compass, the section “Consumer or owner?” recognises many brands automatically and calculates with the average returns of the related shares over recent years, compared with a global ETF.</p>''',
 faqs=[('Why 7 percent?','It is an assumption for a broadly diversified global equity index over long periods. You can enter any other value.'),
       ('Does the calculator use the real Netflix share and others?','This page calculates with a return you choose. In the full Money Compass, brands are matched to real companies.'),
       ('Is this a recommendation to buy?','No. It is a model calculation for financial education. Individual shares are risky and can lose their entire value.')])

EN['schuldenfrei-rechner'] = dict(
 slug='debt-free-calculator', short='Debt-free calculator', teaser='When you will be debt-free and what extra payments do',
 title='Debt-Free Calculator: When will my loan be paid off? | Money Compass',
 desc='Repayment calculator for loans, overdrafts and credit cards: enter balance, interest rate and payment and see the month you will be debt-free and how much interest an extra payment saves.',
 eyebrow='Debt & repayment', h1='Debt-free calculator: when will your debt be paid off?',
 lead='Enter your remaining balance, interest rate and monthly payment. You will see the date you become debt-free and how much interest a small extra amount saves.',
 calc=[('Restschuld (€)','Remaining balance (€)'),('Zinssatz pro Jahr (%)','Interest rate per year (%)'),('Monatliche Rate (€)','Monthly payment (€)'),('Extra pro Monat (€)','Extra per month (€)'),
       ('Vereinfachte Rechnung mit festem Zins und gleichbleibender Rate, ohne Gebühren. Bei Problemen mit Raten helfen kostenlose Schuldnerberatungen, zum Beispiel der Verbraucherzentralen.',
        'Simplified calculation with a fixed rate and constant payment, without fees. If you struggle with payments, free debt advice services can help.')],
 js=[("'Rate zu niedrig'","'Payment too low'"),
     ("'Die Rate deckt nicht einmal die Zinsen von '+G.E(d*r/12)+' pro Monat. Die Schuld wächst. Hier lohnt sich ein Gespräch mit einer Schuldnerberatung.'","'The payment does not even cover the interest of '+G.E(d*r/12)+' per month. The debt is growing. A conversation with a free debt advice service is worth it.'"),
     ("'schuldenfrei in '+b.m+' Monaten'+(b.m>=12?' (rund '+G.nf1.format(b.m/12)+' Jahre)':'')+(x>0?', mit '+G.E(x)+' extra pro Monat':'')","'debt-free in '+b.m+' months'+(b.m>=12?' (about '+G.nf1.format(b.m/12)+' years)':'')+(x>0?', with '+G.E(x)+' extra per month':'')"),
     ('Zinsen bis schuldenfrei','Interest until debt-free'),('Ohne Extra schuldenfrei','Debt-free without extra'),('Extra spart an Zinsen','Extra saves in interest'),('Früher fertig','Done earlier'),("' Monate</b>","' months</b>"),
     ('<span>Ohne Extra</span><b class="neg">nie</b>','<span>Without extra</span><b class="neg">never</b>'),
     ("'Mit '+G.E(x)+' extra im Monat bin ich '+(a.m-b.m)+' Monate früher schuldenfrei und spare rechnerisch '+G.E(a.int-b.int)+' Zinsen.':'Mit meinem Plan bin ich in '+b.m+' Monaten schuldenfrei.'",
      "'With '+G.E(x)+' extra a month I will be debt-free '+(a.m-b.m)+' months earlier and save about '+G.E(a.int-b.int)+' in interest.':'With my plan I will be debt-free in '+b.m+' months.'")],
 body='''
<h2>Why small extra amounts make a big difference</h2>
<p>With every loan, part of the payment goes to the bank as interest and only the rest reduces the debt. Every extra euro, on the other hand, goes entirely into repayment. That lowers next month's interest, so more of your normal payment reduces the debt. This effect builds up every month.</p>
<h2>Expensive debt first</h2>
<p>Overdrafts and credit cards often cost 10 to 20 percent interest. If you have several debts, an extra amount does the most on the most expensive one (avalanche method). Some prefer to start with the smallest debt for a quick win (snowball method). Both work if you stick with it. In the Money Compass, the debt plan compares both approaches with your real debts.</p>
<h2>When the payment is not enough</h2>
<p>If your payment barely covers the interest, the debt grows despite paying. That is not a personal failure but a sign to get help. Free debt advice services can also negotiate with creditors.</p>''',
 faqs=[('Can I repay a loan early?','For consumer loans early repayment is usually possible; the lender may charge a limited early repayment fee. Check your contract.'),
       ('How accurate is the calculation?','It assumes a fixed interest rate and a constant payment. Real contracts can have fees, fixed-rate periods or special repayment rules.'),
       ('What is better: repay faster or save?','With expensive debt, faster repayment usually pays off more than saving. You should still keep a small emergency fund so no new debt arises.')])

EN['notgroschen-rechner'] = dict(
 slug='emergency-fund-calculator', short='Emergency fund calculator', teaser='How big your safety cushion should be',
 title='Emergency Fund Calculator: How much do I need? | Money Compass',
 desc='Calculate your emergency fund: your fixed monthly costs give your target reserve of 3 to 6 months, and you see when you will reach it with your savings rate.',
 eyebrow='Reserve & safety', h1='Emergency fund calculator: how big should your safety cushion be?',
 lead='An emergency fund keeps a broken washing machine or a job change from turning into new debt. Here you see how big it should be and when you will reach it.',
 calc=[('Feste Kosten pro Monat (€)','Fixed costs per month (€)'),('Wie viele Monate absichern?','How many months to cover?'),('>3 Monate<','>3 months<'),('>4 Monate<','>4 months<'),('>6 Monate<','>6 months<'),
       ('Schon zurückgelegt (€)','Already saved (€)'),('Sparrate pro Monat (€)','Savings per month (€)'),
       ('Als feste Kosten zählen Miete, Nebenkosten, Versicherungen, Lebensmittel, Mobilität und Raten. Faustregel, keine Pflicht: Wer ein unsicheres Einkommen hat, plant eher mehr Monate ein.',
        'Fixed costs include rent, utilities, insurance, food, transport and loan payments. Rule of thumb, not a must: with an uncertain income, plan for more months.')],
 js=[("'Ziel-Rücklage für '+n+' Monate'","'Target reserve for '+n+' months'"),('Reicht heute für','Lasts today for'),("' Monate</b>","' months</b>"),('Fehlen noch','Still missing'),('Ziel erreicht','Goal reached'),
     ("'schon jetzt ✓'","'already ✓'"),("'Sparrate eintragen'","'enter savings rate'"),
     ("'Mein Notgroschen steht: Er reicht für '+G.nf1.format(cov)+' Monate.':'Mein Notgroschen-Ziel: '+G.E(goal)+'. Mit '+G.E(s)+' im Monat erreiche ich es'+(isFinite(m)?' im '+G.monthName(m):'')+'.'",
      "'My emergency fund is in place: it lasts '+G.nf1.format(cov)+' months.':'My emergency fund goal: '+G.E(goal)+'. With '+G.E(s)+' a month I will reach it'+(isFinite(m)?' in '+G.monthName(m):'')+'.'")],
 body='''
<h2>Why the emergency fund comes first</h2>
<p>Without a reserve, every unexpected bill turns into an overdraft or an instalment plan, and those cost interest. An emergency fund is therefore not an investment but insurance against new debt. It belongs in an account you can access quickly, such as an instant-access savings account.</p>
<h2>How big should it be?</h2>
<p>Three to six months of your fixed costs is often recommended. With a secure job and no children, three months is often enough. Self-employed people, single earners or people with fluctuating income tend to plan for six months or more.</p>
<h2>Start small</h2>
<p>Even €500 covers many small emergencies. Ideally set up a standing order right after payday. The Money Compass shows you how many months your reserve already covers.</p>''',
 faqs=[('Where should I keep my emergency fund?','In a safe account you can access at any time, for example an instant-access savings account with deposit protection. Not in shares, because they may have fallen exactly when you need the money.'),
       ('Should I repay debt or save first?','Usually build a small starter emergency fund first, then repay expensive debt, and then fill up the reserve completely.'),
       ('Do loan payments count as fixed costs?','Yes. Everything you definitely have to pay every month counts.')])

EN['freiheitstage-rechner'] = dict(
 slug='freedom-days-calculator', short='Freedom days calculator', teaser='How many days your wealth carries you',
 title='Freedom Days Calculator: How long would my money last without income? | Money Compass',
 desc='Calculate your freedom days: how many days could you live on your net worth? Plus: how many days of freedom your monthly savings add every month.',
 eyebrow='Freedom days', h1='Freedom days calculator: how many days does your wealth carry you?',
 lead='Freedom days show in a single number how long you could live on your wealth. The number grows with every euro you save or every euro of debt you repay.',
 calc=[('Ersparnisse und Anlagen (€)','Savings and investments (€)'),('Schulden (€)','Debt (€)'),('Ausgaben pro Monat (€)','Spending per month (€)'),('Sparrate pro Monat (€)','Savings per month (€)'),
       ('Rechnung: Nettovermögen geteilt durch Monatsausgaben, mal 30. Gebundenes Vermögen wie Immobilien oder Altersvorsorge ist nicht sofort verfügbar. Eine Orientierungszahl, keine Planung für den Ruhestand.',
        'Calculation: net worth divided by monthly spending, times 30. Tied-up assets such as property or pension savings are not immediately available. A guide figure, not retirement planning.')],
 js=[("' Tage':'Noch im Minus'","' days':'Still negative'"),("'das sind rund '+G.nf1.format(days/365)+' Jahre'","'that is about '+G.nf1.format(days/365)+' years'"),
     ("'Dein Nettovermögen ist negativ. Jeder getilgte Euro bringt dich näher an Tag 1.':'rechnerisch von deinem Nettovermögen'","'Your net worth is negative. Every euro of debt repaid brings you closer to day 1.':'calculated from your net worth'"),
     ('>Nettovermögen<','>Net worth<'),('Jeden Monat dazu','Added every month'),("' Tage</b>","' days</b>"),('Pro Jahr dazu','Added per year'),
     ("'Ich habe '+G.nf0.format(days)+' Freiheitstage, und jeden Monat kommen '+G.nf1.format(gain)+' dazu. Wie viele hast du?':'Ich arbeite mich gerade zu meinem ersten Freiheitstag vor. Jeden Monat kommen '+G.nf1.format(gain)+' Tage dazu.'",
      "'I have '+G.nf0.format(days)+' freedom days, and every month '+G.nf1.format(gain)+' more are added. How many do you have?':'I am working my way to my first freedom day. Every month '+G.nf1.format(gain)+' days are added.'")],
 body='''
<h2>What are freedom days?</h2>
<p>Imagine your income stopped tomorrow. How many days could you keep living on your current net worth without changing anything? Those are your freedom days. The number makes progress tangible: instead of “saved €2,000” it says “one more month of freedom”.</p>
<h2>Two levers</h2>
<p>Freedom days rise when your net worth grows, through saving, investing and repaying debt. They also rise when your monthly spending falls, because the same wealth lasts longer. If you need €100 less per month, you win twice: a higher savings rate and more days per euro.</p>
<h2>Track it with real numbers</h2>
<p>In the free Money Compass, your freedom days are calculated automatically from your bookings, debts and portfolio and shown month by month. Your data stays in your browser.</p>''',
 faqs=[('Why net worth and not just savings?','Debt has to be subtracted from savings for an honest picture. Someone with €5,000 saved and €5,000 of debt is at zero.'),
       ('Does my home count?','In theory yes, in practice you cannot live off a home you live in. For an honest number, only enter wealth you can actually access.'),
       ('Where does the term come from?','It comes from the book behind the Money Compass, “Der einfache Weg zur Finanziellen Freiheit”.')])

# Währungsrechner: englische Adressen der Paarseiten
EN_FX_SLUG = {'waehrungsrechner':'currency-converter','euro-in-dollar':'eur-to-usd','dollar-in-euro':'usd-to-eur','euro-in-pfund':'eur-to-gbp','pfund-in-euro':'gbp-to-eur',
              'euro-in-franken':'eur-to-chf','franken-in-euro':'chf-to-eur','euro-in-tuerkische-lira':'eur-to-try','euro-in-lari':'eur-to-gel','euro-in-ringgit':'eur-to-myr',
              'euro-in-dong':'eur-to-vnd','euro-in-rubel':'eur-to-rub','euro-in-zloty':'eur-to-pln','bitcoin-in-euro':'btc-to-eur','euro-in-baht':'eur-to-thb'}
EN_FX_INTRO = {
 'eur-to-usd':'For online shopping in the US, trips to America or a look at your portfolio: the US dollar is the world\'s most important currency. Many shares, commodities and gold are traded in dollars.',
 'usd-to-eur':'Do you have income, prices or balances in US dollars and want to know what that is in euros? Here you see it at the current rate, with a table of typical amounts.',
 'eur-to-gbp':'For a trip to London, shopping at British stores or a transfer to the UK: this is how many pounds sterling you currently get for your euros.',
 'gbp-to-eur':'Prices, salary or savings in British pounds? The calculator shows what that is currently worth in euros.',
 'eur-to-chf':'Holidays in the Alps, commuting to Switzerland or shopping in Zurich: convert euros to Swiss francs at the current rate.',
 'chf-to-eur':'Salary, prices or savings in Swiss francs? The calculator shows the current value in euros.',
 'eur-to-try':'For a holiday in Turkey: the lira fluctuates strongly, so check the current rate before every exchange. The change versus the previous day shows how much it moved recently.',
 'eur-to-gel':'For trips to Georgia, living in Tbilisi or transfers to Georgia: this is how many Georgian lari you currently get for your euros.',
 'eur-to-myr':'For Malaysia, Kuala Lumpur or Penang: this is how many Malaysian ringgit you currently get for your euros.',
 'eur-to-vnd':'For trips to Vietnam: with the dong, numbers get big quickly. The calculator and table show at a glance what your euros are worth.',
 'eur-to-rub':'The current euro to Russian ruble rate on the currency market. Note: due to sanctions and capital controls, the rates you can actually get often differ significantly.',
 'eur-to-pln':'For shopping, holidays or work in Poland: this is how many Polish złoty you currently get for your euros.',
 'btc-to-eur':'What is one bitcoin worth in euros right now? The calculator shows the current price, the table also fractions, because you can buy bitcoin in small pieces. Bitcoin is very volatile; this is a price display, not investment advice.',
 'eur-to-thb':'For a holiday in Thailand or life as a digital nomad in Southeast Asia: this is how many Thai baht you currently get for your euros.',
}
