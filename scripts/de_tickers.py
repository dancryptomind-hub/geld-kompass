"""Ermittelt für internationale Aktien das deutsche Börsenkürzel (Xetra/Tradegate/Frankfurt),
z. B. Coca-Cola KO -> CCC3, Realty Income O -> RY6. Ergebnis: Feld "de" in scripts/instruments.json.
Quelle: Yahoo-Finance-Suche (nach ISIN, sonst nach Name). Läuft per GitHub Action („Deutsche Kürzel“)."""
import json, re, sys, time
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent.parent
F = ROOT / "scripts" / "instruments.json"
UA = {"User-Agent": "Mozilla/5.0"}
GER = ("GER", "FRA", "STU", "MUN", "BER", "DUS", "HAM", "HAN", "XETRA", "TRADEGATE")


def words(s):
    return set(w for w in re.findall(r"[a-z0-9]+", s.lower()) if len(w) > 2 and w not in ("inc", "corp", "the", "plc", "ltd", "group", "holding", "holdings", "company", "class", "co"))


def search(q):
    r = requests.get("https://query2.finance.yahoo.com/v1/finance/search", params={"q": q, "quotesCount": 25, "newsCount": 0}, headers=UA, timeout=20)
    return r.json().get("quotes", []) if r.ok else []


def main():
    items = json.loads(F.read_text(encoding="utf-8"))
    n = 0
    for x in items:
        if x["t"] != "Aktie" or x["s"].endswith((".DE", ".F")) or x.get("de"):
            continue
        found = None
        for q in [x.get("i"), x["s"], x["n"].split("(")[0].strip()]:
            if not q:
                continue
            try:
                qs = search(q)
            except Exception as e:
                print("fail", q, e, file=sys.stderr); qs = []
            nm = words(x["n"].split("(")[0])
            cands = [c for c in qs if (c.get("exchange") in GER or str(c.get("symbol", "")).endswith((".DE", ".F", ".SG", ".MU", ".BE", ".DU", ".HM")))
                     and c.get("quoteType") == "EQUITY" and (q == x.get("i") or nm & words(c.get("shortname", "") + " " + c.get("longname", "")))]
            if cands:
                cands.sort(key=lambda c: (not str(c["symbol"]).endswith(".DE"), not str(c["symbol"]).endswith(".F")))
                found = str(cands[0]["symbol"]).split(".")[0]
                break
            time.sleep(0.4)
        if found and found != x["s"]:
            x["de"] = found
            n += 1
            print(x["s"], "->", found)
    F.write_text(json.dumps(items, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    print(n, "deutsche Kürzel")


if __name__ == "__main__":
    main()
