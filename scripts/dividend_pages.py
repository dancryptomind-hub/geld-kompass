# Erzeugt die Google-Seiten „Dividenden-Kalender: Wer zahlt wann?“ (DE) und „Dividend calendar“ (EN)
# aus data/dividends.json (Ausschüttungen der letzten 12 Monate, wöchentlich), data/markets.json (Kurse in EUR),
# scripts/instruments.json (Namen, Typ) und data/dividend_meta.json (Abzeichen, Kurzinfo). Läuft im Workflow „Dividenden“.
import json, html, os, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: json.load(open(os.path.join(ROOT, p), encoding="utf-8"))
DIV = J("data/dividends.json")
INS = {x["s"]: x for x in J("scripts/instruments.json")}
for x in J("data/markets.json").get("instruments", []):
    if x.get("p"):
        INS.setdefault(x["s"], x)["p"] = x["p"]
META = J("data/dividend_meta.json")
try:
    LOGOS = J("data/logos.json")
except Exception:
    LOGOS = {}

MS = {"de": ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"],
      "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]}
ML = {"de": ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"],
      "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]}
TYPE = {"de": {"Aktie": "Aktie", "ETF": "ETF"}, "en": {"Aktie": "Stock", "ETF": "ETF"}}
BADGE = {"de": {"king": "👑 Dividenden-König", "arist": "🏅 Dividenden-Aristokrat", "cont": "Dividenden-Herausforderer"},
         "en": {"king": "👑 Dividend King", "arist": "🏅 Dividend Aristocrat", "cont": "Dividend Contender"}}


def esc(s):
    return html.escape(str(s), quote=True)


def num(v, lang, d=2):
    s = f"{v:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".") if lang == "de" else s


def freq(n, lang):
    de = {12: "monatlich", 4: "quartalsweise", 2: "halbjährlich", 1: "jährlich"}
    en = {12: "monthly", 4: "quarterly", 2: "semi-annual", 1: "annual"}
    k = 12 if n >= 12 else 4 if n >= 4 else 2 if n >= 2 else 1
    return (de if lang == "de" else en)[k]


def rows():
    out = []
    for s, x in DIV.get("d", {}).items():
        i = INS.get(s)
        if not i or not x.get("dv"):
            continue
        p = i.get("p")
        y = x["dv"] / p if p else None
        out.append({"s": s, "n": i["n"], "t": i.get("t", "Aktie"), "dv": x["dv"], "m": sorted(set(x["m"])), "y": y,
                    "b": META["badge"].get(s), "info": META["info"].get(s)})
    out.sort(key=lambda r: ({"king": 0, "arist": 1, "cont": 2}.get(r["b"], 3), -(r["y"] or 0)))
    return out


def page(lang):
    R = rows()
    de = lang == "de"
    upd = DIV.get("updated", datetime.date.today().isoformat())
    kings = [r for r in R if r["b"] == "king"]
    monthly = [r for r in R if len(r["m"]) >= 12]
    t = {
        "title": "Dividenden-Kalender: Wer zahlt wann? Monate, Rendite, Dividenden-Könige | Geld-Kompass" if de else "Dividend calendar: who pays when? Months, yield, Dividend Kings | Geld-Kompass",
        "desc": f"Kostenloser Dividenden-Kalender für {len(R)} Aktien und ETFs: in welchem Monat gezahlt wird, Dividendenrendite, Monatszahler, Dividenden-Könige und Aristokraten. Wöchentlich aktualisiert." if de else f"Free dividend calendar for {len(R)} stocks and ETFs: which month they pay, dividend yield, monthly payers, Dividend Kings and Aristocrats. Updated weekly.",
        "eyebrow": "Kostenloser Dividenden-Kalender" if de else "Free dividend calendar",
        "h1": "Dividenden-Kalender: Wer zahlt wann?" if de else "Dividend calendar: who pays when?",
        "lead": (f"{len(R)} Aktien und ETFs mit ihren Zahlungsmonaten, der Dividende der letzten 12 Monate und der Rendite zum aktuellen Kurs. Tippe auf einen Monat, um nur die Zahler dieses Monats zu sehen. Stand: {upd}." if de else
                 f"{len(R)} stocks and ETFs with their payment months, the dividend of the last 12 months and the yield at the current price. Tap a month to see only that month’s payers. Updated: {upd}."),
        "all": "Alle" if de else "All", "q": "Name oder Kürzel suchen" if de else "Search name or ticker",
        "th": ["Wertpapier", "Zahlungsmonate", "Dividende / Jahr", "Rendite"] if de else ["Security", "Payment months", "Dividend / year", "Yield"],
        "per": "je Anteil, in Euro" if de else "per share, in euro",
        "cta_b": "Deinen eigenen Dividenden-Kalender planen" if de else "Plan your own dividend calendar",
        "cta_s": "Trag deine Aktien im kostenlosen Geld-Kompass ein: Du siehst Monat für Monat, wie viel passives Einkommen kommt. Ohne Anmeldung." if de else "Add your stocks to the free Geld-Kompass and see month by month how much passive income arrives. No sign-up.",
        "foot": "Impressum · Datenschutz · Geld-Kompass · © FreedomByDan · Allgemeine Finanzbildung, keine Anlage-, Steuer- oder Rechtsberatung." if de else "Legal notice · Privacy · Geld-Kompass · © FreedomByDan · General financial education, not investment, tax or legal advice.",
    }
    faq = ([("Was ist ein Dividenden-König?", f"Ein Unternehmen, das seine Dividende mindestens 50 Jahre in Folge erhöht hat. In dieser Liste: {', '.join(r['n'] for r in kings)}. Das zeigt ein sehr stabiles Geschäft, garantiert aber keine künftigen Erhöhungen."),
            ("Was ist ein Dividenden-Aristokrat?", "Ein Unternehmen aus dem US-Index S&P 500 mit mindestens 25 Jahren ununterbrochener Dividendenerhöhung, zum Beispiel Realty Income, McDonald’s oder ExxonMobil."),
            ("Welche Aktien zahlen monatlich?", (", ".join(r["n"] for r in monthly) or "In dieser Liste keine") + ". Mit drei Quartalszahlern, die in unterschiedlichen Monaten zahlen, kommt ebenfalls jeden Monat Geld."),
            ("Wie wird die Rendite berechnet?", "Summe der Ausschüttungen der letzten 12 Monate je Anteil, umgerechnet in Euro, geteilt durch den aktuellen Kurs. Künftige Dividenden können sinken oder ausfallen."),
            ("Wie plane ich jeden Monat Dividenden?", "Kombiniere Werte mit unterschiedlichen Zahlungsmonaten, zum Beispiel Quartalszahler aus Januar/April/Juli/Oktober, Februar/Mai/August/November und März/Juni/September/Dezember. Im Geld-Kompass siehst du das Ergebnis für dein Depot.")] if de else
           [("What is a Dividend King?", f"A company that has raised its dividend for at least 50 consecutive years. In this list: {', '.join(r['n'] for r in kings)}. It shows a very stable business but does not guarantee future increases."),
            ("What is a Dividend Aristocrat?", "A company in the US S&P 500 index with at least 25 consecutive years of dividend increases, for example Realty Income, McDonald’s or ExxonMobil."),
            ("Which stocks pay monthly?", (", ".join(r["n"] for r in monthly) or "None in this list") + ". Three quarterly payers paying in different months also give you money every month."),
            ("How is the yield calculated?", "Sum of the last 12 months of payouts per share, converted to euro, divided by the current price. Future dividends may fall or be cancelled."),
            ("How do I get dividends every month?", "Combine holdings with different payment months, e.g. quarterly payers in Jan/Apr/Jul/Oct, Feb/May/Aug/Nov and Mar/Jun/Sep/Dec. The Geld-Kompass shows the result for your portfolio.")])
    trs = []
    for r in R:
        cal = "".join(f'<i class="{"on" if (k + 1) in r["m"] else ""}" title="{ML[lang][k]}">{MS[lang][k][0]}</i>' for k in range(12))
        bd = f'<span class="bdg {r["b"]}">{BADGE[lang][r["b"]]}</span>' if r["b"] else ""
        info = f'<small class="inf">{esc(r["info"][0 if de else 1])}</small>' if r["info"] else ""
        logo = f'<img src="/{esc(LOGOS[r["s"]])}" alt="" width="28" height="28" loading="lazy">' if r["s"] in LOGOS else f'<span class="lg">{esc(r["n"][:1])}</span>'
        trs.append(f'<tr data-m="{" ".join(str(m) for m in r["m"])}" data-q="{esc((r["n"] + " " + r["s"]).lower())}"><td><div class="ent">{logo}<div><b>{esc(r["n"])}</b><small>{esc(r["s"])} · {TYPE[lang].get(r["t"], r["t"])} · {freq(len(r["m"]), lang)}</small>{bd}{info}</div></div></td>'
                   f'<td><div class="cal">{cal}</div></td><td class="n">{num(r["dv"], lang)} €</td><td class="n"><b>{(num(r["y"] * 100, lang, 1) + " %") if r["y"] else "–"}</b></td></tr>')
    months = "".join(f'<button type="button" data-f="{k + 1}">{MS[lang][k]}</button>' for k in range(12))
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    url_de, url_en = "https://geld-kompass.com/dividenden-kalender/", "https://geld-kompass.com/en/dividend-calendar/"
    other = '<a class="langsw" href="/en/dividend-calendar/?lang=en">English</a>' if de else '<a class="langsw" href="/dividenden-kalender/?lang=de">Deutsch</a>'
    app = "/app/#assets" if de else "/app/?lang=en#assets"
    return f'''<!doctype html><html lang="{lang}" data-page-lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(t["title"])}</title><meta name="description" content="{esc(t["desc"])}">
<link rel="canonical" href="{url_de if de else url_en}"><link rel="alternate" hreflang="de" href="{url_de}"><link rel="alternate" hreflang="en" href="{url_en}"><link rel="alternate" hreflang="x-default" href="{url_de}">
<meta name="theme-color" content="#0E1730"><link rel="stylesheet" href="/rechner/rechner.css"><link rel="icon" type="image/png" sizes="32x32" href="/icons/favicon-32.png"><link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">
<meta property="og:title" content="{esc(t["h1"])}"><meta property="og:description" content="{esc(t["desc"])}"><meta property="og:image" content="https://geld-kompass.com/pins/{"pin" if de else "en"}-div-king.jpg">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>.mf{{display:flex;flex-wrap:wrap;gap:6px;margin:16px 0 10px}}.mf button{{all:unset;cursor:pointer;padding:6px 11px;border-radius:999px;border:1px solid rgba(219,227,250,.18);font-size:.85rem}}.mf button.on{{background:#e3b55a;color:#0e1730;border-color:#e3b55a;font-weight:700}}
#dq{{width:100%;padding:10px 12px;border-radius:10px;border:1px solid rgba(219,227,250,.18);background:rgba(255,255,255,.04);color:inherit;font:inherit;margin-bottom:8px}}
.dt{{width:100%;border-collapse:collapse}}.dt td,.dt th{{padding:10px 6px;border-bottom:1px solid rgba(219,227,250,.1);vertical-align:top;text-align:left}}.dt .n{{text-align:right;white-space:nowrap}}.dt th{{font-size:.75rem;text-transform:uppercase;letter-spacing:.04em;opacity:.7}}
.ent{{display:flex;gap:10px;align-items:flex-start}}.ent img{{border-radius:7px;background:#fff;flex:none}}.ent .lg{{width:28px;height:28px;border-radius:7px;background:rgba(227,181,90,.2);display:grid;place-items:center;font-weight:800;flex:none}}.ent small{{display:block;opacity:.7;font-size:.78rem}}.ent .inf{{opacity:.8;margin-top:4px;max-width:46ch}}
.bdg{{display:inline-block;margin-top:4px;font-size:.72rem;font-weight:700;padding:2px 8px;border-radius:999px;background:rgba(227,181,90,.16);color:#f5d58f}}.bdg.cont{{background:rgba(123,152,242,.16);color:#b8c8ff}}
.cal{{display:grid;grid-template-columns:repeat(12,16px);gap:2px}}.cal i{{font-style:normal;font-size:.6rem;text-align:center;line-height:16px;border-radius:4px;background:rgba(255,255,255,.05);opacity:.5}}.cal i.on{{background:#6fcf97;color:#0e1730;opacity:1;font-weight:700}}
@media(max-width:640px){{.dt td:nth-child(2),.dt th:nth-child(2){{display:none}}.ent .inf{{display:none}}}}
.faq details{{border-bottom:1px solid rgba(219,227,250,.1);padding:10px 0}}.faq summary{{cursor:pointer;font-weight:700}}</style>
<script src="/i18n.js"></script></head><body>
<header class="top"><div class="wrap"><a class="logo" href="/"><img class="gk-logo" src="/icons/logo-badge.webp" alt="" aria-hidden="true" width="34" height="34"><b>Geld-<span>Kompass</span></b></a><nav><a href="{app}">{"Zum Geld-Kompass" if de else "Open the Geld-Kompass"}</a> · {other}</nav></div></header>
<main class="wrap"><div class="eyebrow">{t["eyebrow"]}</div><h1>{t["h1"]}</h1><p class="lead">{t["lead"]}</p>
<div class="mf" id="mf"><button type="button" data-f="0" class="on">{t["all"]}</button>{months}</div>
<input id="dq" type="search" placeholder="{t["q"]}" aria-label="{t["q"]}">
<div style="overflow-x:auto"><table class="dt"><thead><tr><th>{t["th"][0]}</th><th>{t["th"][1]}</th><th class="n">{t["th"][2]}<br><small>{t["per"]}</small></th><th class="n">{t["th"][3]}</th></tr></thead><tbody id="dtb">{"".join(trs)}</tbody></table></div>
<div data-partner="broker" hidden></div>
<div class="cta"><a href="{app}"><i><img class="gk-logo" src="/icons/logo-badge.webp" alt="" aria-hidden="true" width="34" height="34"></i><div><b>{t["cta_b"]}</b><span>{t["cta_s"]}</span></div></a></div>
<h2>{"Häufige Fragen" if de else "FAQ"}</h2><div class="faq">{"".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in faq)}</div>
<p class="lead" style="font-size:.85rem;opacity:.75">{"Daten: Ausschüttungen der letzten 12 Monate laut Yahoo Finance, wöchentlich aktualisiert. Die Monate richten sich nach dem Ex-Tag, die Zahlung kommt meist 2 bis 4 Wochen später. Abzeichen nach Jahren ununterbrochener Dividendenerhöhung, Stand 2026. Keine Anlageberatung." if de else "Data: last 12 months of payouts from Yahoo Finance, updated weekly. Months follow the ex-dividend date; the payment usually arrives 2 to 4 weeks later. Badges based on consecutive years of dividend increases, as of 2026. Not investment advice."}</p>
</main><footer><div class="wrap"><a href="/impressum/">{"Impressum" if de else "Legal notice"}</a> · <a href="/datenschutz/">{"Datenschutz" if de else "Privacy"}</a> · Geld-Kompass · © FreedomByDan · {"Allgemeine Finanzbildung, keine Anlage-, Steuer- oder Rechtsberatung." if de else "General financial education, not investment, tax or legal advice."}</div></footer>
<script>(function(){{var f=0,q="",rows=[].slice.call(document.querySelectorAll("#dtb tr"));function run(){{rows.forEach(function(r){{var ok=(!f||(" "+r.getAttribute("data-m")+" ").indexOf(" "+f+" ")>-1)&&(!q||r.getAttribute("data-q").indexOf(q)>-1);r.style.display=ok?"":"none";}});}}
document.getElementById("mf").addEventListener("click",function(e){{var b=e.target.closest("button");if(!b)return;f=+b.getAttribute("data-f");[].forEach.call(this.children,function(x){{x.classList.toggle("on",x===b);}});run();}});
document.getElementById("dq").addEventListener("input",function(e){{q=e.target.value.toLowerCase().trim();run();}});var m=(location.hash.match(/m=(\\d+)/)||[])[1];if(m){{var b=document.querySelector('#mf [data-f="'+m+'"]');if(b)b.click();}}}})();</script>
<script src="/partner.js"></script>
<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token": "d5b51a031e8c4e26b08ad199a6bfd2da"}}'></script>
</body></html>'''


for lang, path in (("de", "dividenden-kalender"), ("en", "en/dividend-calendar")):
    d = os.path.join(ROOT, path)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(page(lang))
print("Dividenden-Seiten:", len(rows()), "Werte")
