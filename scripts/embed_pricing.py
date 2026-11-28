"""EUR B2B pricing; licence scope comes from the confirmed DE/EN copy."""
from html import escape
from urllib.parse import quote
LINKS = {
 'offer': ('cIxQo-Xjki8teco', 'eBtVofz-S2LN06I'),
 'professional': ('9X8ex7Pmhl3odzA', '0-8F2xEeYpop_j4'),
 'business': ('PzKOsnQNGVKkWWM', 'ZI40RxbNtwrhNXs'),
 'agency': ('55fP7X4zWIbfSAg', 'n_WNk78aPCp8nM4'),
}

def actions(lang, key, amount):
 en = lang == 'en'
 mo,yr = LINKS[key]
 monthly = f'Pay {amount} EUR with Wise' if en else f'{amount} EUR mit Wise zahlen'
 yearly = f'Pay {amount*12} EUR with Wise' if en else f'{amount*12} EUR mit Wise zahlen'
 note = ('Only pay after your licence scope and invoice details have been confirmed. Use the invoice or quote number as payment reference.' if en else 'Erst zahlen, wenn Lizenzumfang und Rechnungsangaben bestätigt sind. Angebots- oder Rechnungsnummer als Zahlungsreferenz angeben.')
 gate = ('Confirm the agreed Agency base licence before paying. Reseller rights, client domains and extras require a separate agreement.' if en else 'Vor Zahlung die vereinbarte Agency-Basislizenz bestätigen. Reseller-Rechte, Kundendomains und Zusatzleistungen separat vereinbaren.')
 mail='mailto:kontakt@geld-kompass.com?subject='+quote('White-Label '+key)+'&amp;body='+quote('Company / Unternehmen:\nDomains:\nInvoice details / Rechnungsangaben:\n')
 return f'''<div class="eb-pay-actions"><p>{gate if key=='agency' else note}</p><a href="{mail}">{'Confirm licence &amp; invoice details' if en else 'Lizenz &amp; Rechnungsangaben klären'}</a>{'<label><input type="checkbox" id="ebAgencyConsent"> '+('My Agency base licence and price have been expressly agreed.' if en else 'Meine Agency-Basislizenz und der Preis sind ausdrücklich vereinbart.')+'</label>' if key=='agency' else ''}<a class="eb-cta" data-wise="{key}" data-link-mo="https://wise.com/pay/r/{mo}" data-link-yr="https://wise.com/pay/r/{yr}" data-label-mo="{monthly}" data-label-yr="{yearly}" {'aria-disabled="true"' if key=='agency' else 'href="https://wise.com/pay/r/'+yr+'"'} target="_blank" rel="noopener noreferrer">{yearly}</a></div>'''

def pricing(lang, cards):
 en=lang=='en'
 out='<h2 id="ebPricing">'+('B2B licences &amp; EUR payments' if en else 'B2B-Lizenzen &amp; EUR-Zahlungen')+'</h2>'
 out+='<p>'+('All payments below are in EUR. Licence scope, applicable taxes, term and cancellation are confirmed in your quote before purchase. Existing contracts remain unchanged.' if en else 'Alle folgenden Zahlungen erfolgen in EUR. Lizenzumfang, anwendbare Steuern, Laufzeit und Kündigung werden vor dem Kauf im Angebot bestätigt. Bestehende Verträge bleiben unverändert.')+'</p>'
 out+='''<div class="eb-bill" role="group" aria-label="'''+('Payment interval' if en else 'Zahlungszeitraum')+'''"><button type="button" data-ebbill="mo" aria-pressed="false">'''+('Monthly' if en else 'Monatlich')+'''</button><button type="button" data-ebbill="yr" aria-pressed="true">'''+('12 months upfront' if en else '12 Monate vorauszahlen')+'''</button></div>'''
 out+='<p id="ebPaymentTerms">'+('Monthly: manually pay each month; no automatic debit. Annual: a single payment for 12 months; no automatic debit or automatic renewal through Wise.' if en else 'Monatlich: jeden Monat selbst zahlen; kein automatischer Einzug. Jährlich: einmalige Zahlung für 12 Monate; kein automatischer Einzug und keine automatische Verlängerung durch Wise.')+'</p>'
 out+='<div id="gk-seasonal-offer" class="eb-risk" hidden><h3 id="ebOfferTitle"></h3><p id="ebOfferTerms"></p><p>'+('Professional scope: up to 3 own company domains; no client websites or reseller rights.' if en else 'Professional-Umfang: bis zu 3 eigene Unternehmensdomains; keine Kunden-Websites oder Reseller-Rechte.')+'</p>'+actions(lang,'offer',39)+'</div>'
 out+='<div class="eb-tiers">'
 assert len(cards)==4, cards
 for i,(title,features) in enumerate(cards):
  key=['free','professional','business','agency'][i]; amount=[0,79,199,399][i]
  price='0 EUR' if not i else ('From ' if en else 'Ab ') * (i==3)+f'{amount} EUR'
  yearly=('From ' if en else 'Ab ') * (i==3)+f'{amount*12} EUR'
  out+=f'<div'+(' class="eb-tier-pro"' if i==1 else '')+f'><h3>{title}</h3><div class="eb-price"'+(f' data-price-mo="{price}" data-price-yr="{yearly}"' if i else '')+f'>{yearly if i else price}</div><p class="eb-subprice"'+(' data-period' if i else '')+'>'+ (('One payment for 12 months' if en else 'Einmalig für 12 Monate') if i else ('With provider attribution' if en else 'Mit Anbieterhinweis'))+f'</p><ul>{features}</ul>'
  out+=actions(lang,key,amount) if i else '<a class="eb-cta" href="#ebCode">'+('Copy code' if en else 'Code kopieren')+'</a>'
  out+='</div>'
 out+='</div><div class="eb-risk"><b>'+('Payment &amp; activation' if en else 'Zahlung &amp; Freischaltung')+'</b><p>'+('Include your company, domains, billing address and quote/invoice number when arranging your licence at kontakt@geld-kompass.com. Payment reconciliation, invoicing and activation are handled manually. Opening a Wise link or returning to this website does not activate a licence. Activation follows verification of funds received and the agreed licence scope. Request your branded preview before buying.' if en else 'Kläre deine Lizenz mit Unternehmen, Domains, Rechnungsanschrift und Angebots-/Rechnungsnummer unter kontakt@geld-kompass.com. Zahlungsabgleich, Rechnung und Freischaltung erfolgen manuell. Ein geöffneter Wise-Link oder die Rückkehr zur Website aktiviert keine Lizenz. Die Freischaltung erfolgt nach Prüfung des Zahlungseingangs und des vereinbarten Lizenzumfangs. Fordere vor dem Kauf eine Vorschau in deinem Design an.')+'</p></div>'
 return out
