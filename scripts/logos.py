"""Lädt die Logos der Wertpapiere und Kryptowährungen aus scripts/instruments.json herunter
und legt sie unter /logos/ ab (64 × 64 PNG). Die App lädt sie von geld-kompass.com selbst,
Nutzer stellen also keine Anfragen an fremde Logo-Dienste.
Quellen: Kryptowährungen über CoinGecko (offizielle Coin-Bilder), Aktien über die Website des
Unternehmens laut Yahoo Finance (Symbol der Website), ETFs über die Website des Anbieters.
Läuft in der GitHub Action „Logos aktualisieren“ (monatlich und von Hand)."""
import io, json, re, sys, time
from pathlib import Path
import requests
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "logos"
OUT.mkdir(exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (GeldKompass logo fetcher; +https://geld-kompass.com)"}
DOMAIN = {"GOOGL": "google.com", "BRK-B": "berkshirehathaway.com", "TSM": "tsmc.com", "AMD": "amd.com", "COST": "costco.com", "OR.PA": "loreal.com",
          "2914.T": "jt.com", "HEIA.AS": "heineken.com", "CARL-B.CO": "carlsberg.com", "MNST": "monsterbevcorp.com", "PDD": "temu.com",
          "TTE.PA": "totalenergies.com", "XOM": "exxonmobil.com", "VOD": "vodafone.com", "NEM": "newmont.com", "AEM": "agnicoeagle.com",
          "FNV": "franco-nevada.com", "KGC": "kinross.com", "FCX": "fcx.com", "ENB.TO": "enbridge.com", "AAL.L": "angloamerican.com",
          "FRES.L": "fresnilloplc.com", "NWG.L": "natwestgroup.com", "TSCO.L": "tesco.com", "NG.L": "nationalgrid.com", "UNH": "unitedhealthgroup.com",
          "CSCO": "cisco.com", "BA": "boeing.com", "NEE": "nexteraenergy.com", "BABA": "alibaba.com", "9988.HK": "alibaba.com", "1211.HK": "byd.com",
          "1299.HK": "aia.com", "000660.KS": "skhynix.com", "9984.T": "softbank.jp", "8306.T": "mufg.jp", "HDB": "hdfcbank.com",
          "RELIANCE.NS": "ril.com", "URNM": "sprott.com", "4GLD.DE": "xetra-gold.com", "SLV": "ishares.com", "CPER": "uscfinvestments.com"}
ISSUER = {"ishares": "ishares.com", "vanguard": "vanguard.com", "xtrackers": "etf.dws.com", "spdr": "ssga.com", "vaneck": "vaneck.com",
          "global x": "globalxetfs.com", "amundi": "amundi.com", "invesco": "invesco.com", "kraneshares": "kraneshares.com",
          "sprott": "sprott.com", "united states": "uscfinvestments.com", "wisdomtree": "wisdomtree.com", "xetra-gold": "xetra-gold.com",
          "franklin": "franklintempleton.com", "fidelity": "fidelity.com", "jpmorgan": "jpmorgan.com", "ubs": "ubs.com", "hanetf": "hanetf.com"}


def key(sym):
    return re.sub(r"[^A-Za-z0-9]+", "_", sym).strip("_").upper()


def save(img_bytes, sym):
    im = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    if im.width < 32 or im.height < 32:  # Platzhalter oder zu klein: lieber Buchstaben-Symbol in der App
        return False
    im.thumbnail((64, 64), Image.LANCZOS)
    canvas = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    canvas.paste(im, ((64 - im.width) // 2, (64 - im.height) // 2), im)
    canvas.save(OUT / (key(sym) + ".png"), optimize=True)
    return True


ALT = {"etf.dws.com": ["dws.com", "xtrackers.com"], "ssga.com": ["spdrs.com", "statestreet.com"], "vaneck.com": ["vaneck.de"], "xetra-gold.com": ["deutsche-boerse-commodities.com"]}


def favicon(domain):
    for d in [domain] + ALT.get(domain, []):
        b = favicon1(d)
        if b:
            return b
    return None


def favicon1(domain):
    for url in (f"https://www.google.com/s2/favicons?domain={domain}&sz=128", f"https://icons.duckduckgo.com/ip3/{domain}.ico"):
        try:
            r = requests.get(url, headers=UA, timeout=20)
            if r.ok and len(r.content) > 300:
                im = Image.open(io.BytesIO(r.content))
                if im.width >= 32:
                    return r.content
        except Exception:
            pass
    return None


def domain_of(url):
    m = re.match(r"https?://(?:www\.)?([^/]+)", url or "")
    return m.group(1) if m else None


def main():
    items = json.loads((ROOT / "scripts" / "instruments.json").read_text(encoding="utf-8"))
    done = {}
    # Kryptowährungen: CoinGecko-Bilder
    cg = [x for x in items if x.get("cg")]
    if cg:
        try:
            r = requests.get("https://api.coingecko.com/api/v3/coins/markets", params={"vs_currency": "eur", "ids": ",".join(x["cg"] for x in cg)}, headers=UA, timeout=30).json()
            img = {c["id"]: c.get("image") for c in r}
            for x in cg:
                u = img.get(x["cg"])
                if u:
                    b = requests.get(u, headers=UA, timeout=20).content
                    if save(b, x["s"]):
                        done[x["s"]] = "logos/" + key(x["s"]) + ".png"
        except Exception as e:
            print("coingecko fail", e, file=sys.stderr)
    import yfinance as yf
    for x in items:
        if x["s"] in done or x.get("cg"):
            continue
        dom = DOMAIN.get(x["s"])
        name = x["n"].lower()
        if not dom and x["t"] in ("ETF", "Rohstoff"):
            dom = next((d for k, d in ISSUER.items() if name.startswith(k) or k in name), None)
        if not dom:
            try:
                info = yf.Ticker(x["s"]).info
                dom = domain_of(info.get("website"))
                if not dom and info.get("fundFamily"):
                    ff = info["fundFamily"].lower()
                    dom = next((d for k, d in ISSUER.items() if k in ff), None)
            except Exception as e:
                print("yf fail", x["s"], e, file=sys.stderr)
            time.sleep(0.3)
        if dom:
            b = favicon(dom)
            if b and save(b, x["s"]):
                done[x["s"]] = "logos/" + key(x["s"]) + ".png"
                continue
        print("kein Logo:", x["s"], dom, file=sys.stderr)
    (ROOT / "data" / "logos.json").write_text(json.dumps(done, ensure_ascii=False, indent=0, sort_keys=True), encoding="utf-8")
    print(len(done), "Logos von", len(items))


if __name__ == "__main__":
    main()
