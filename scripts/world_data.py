"""Wechselkurse und Inflation USA / Großbritannien für den Geld-Kompass.

Läuft in der GitHub Action nach update_data.py und hicp_annual.py:
  - Wechselkurse (Basis EUR) über yfinance (Yahoo Finance, Forex-Paare EURxxx=X)
      -> data/markets.json  "fx"
  - USA: Verbraucherpreisindex CPI-U (BLS), abgerufen über FRED (Reihe CPIAUCNS, ohne Schlüssel),
         Ersatzweg: BLS-API v1 (Reihe CUUR0000SA0)
  - Großbritannien: CPI-Index (ONS, Reihe D7BT, 2015 = 100)
      -> data/markets.json  "inflation" US / UK  (Veränderung zum Vorjahresmonat)
      -> data/hicp_annual.json  US / UK  (Jahresdurchschnitte für den Inflationsrechner)
Schlägt eine Quelle fehl, bleibt der letzte bekannte Wert erhalten.
"""
import csv
import datetime as dt
import io
import json
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
MARKETS = ROOT / "data" / "markets.json"
ANNUAL = ROOT / "data" / "hicp_annual.json"
UA = {"User-Agent": "GeldKompass/2.0 (+https://geld-kompass.com)"}
NOW = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
CURRENCIES = ["USD", "GBP", "CHF", "JPY", "CAD", "AUD", "SEK", "NOK", "DKK", "PLN", "CZK", "HUF", "TRY", "THB", "CNY"]
MON = {m: i + 1 for i, m in enumerate(["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"])}


def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


# ---------- Wechselkurse ----------
def fx_rates(old):
    import yfinance as yf
    rates, change = {"EUR": 1.0}, {}
    for cur in CURRENCIES:
        try:
            hist = yf.Ticker(f"EUR{cur}=X").history(period="5d", interval="1d")
            closes = hist["Close"].dropna()
            if closes.empty:
                continue
            rates[cur] = round(float(closes.iloc[-1]), 6)
            if len(closes) > 1 and float(closes.iloc[-2]) > 0:
                change[cur] = round((float(closes.iloc[-1]) / float(closes.iloc[-2]) - 1) * 100, 2)
        except Exception as e:
            print("fx fail", cur, e, file=sys.stderr)
    oldr = (old or {}).get("rates", {})
    for cur in CURRENCIES:  # fehlende Kurse: letzten bekannten Wert behalten
        if cur not in rates and cur in oldr:
            rates[cur] = oldr[cur]
    fresh = len([c for c in CURRENCIES if c in rates and c not in (set(oldr) - set(rates))])
    if len(rates) < 4:
        raise RuntimeError("zu wenige Wechselkurse")
    return {"base": "EUR", "rates": rates, "change": change, "updated": NOW,
            "source": "Yahoo Finance (yfinance), Forex-Paare EURxxx=X", "fresh": fresh}


# ---------- Hilfsfunktionen Index ----------
def yoy(series):
    """series: dict 'YYYY-MM' -> Indexwert. Letzter Monat mit Vorjahreswert."""
    for period in sorted(series, reverse=True):
        y, m = period.split("-")
        prev = f"{int(y) - 1}-{m}"
        if prev in series and series[prev]:
            return period, round((series[period] / series[prev] - 1) * 100, 1)
    raise ValueError("kein Vorjahresvergleich")


def annual(series, rebase_year="2015"):
    by = {}
    for period, v in series.items():
        by.setdefault(period[:4], []).append(v)
    this = str(dt.date.today().year)
    # Ganze Jahre; ein fehlender Monat ist erlaubt (z. B. USA Oktober 2025: wegen Haushaltssperre nicht erhoben)
    full = {y: sum(v) / len(v) for y, v in by.items() if len(v) == 12 or (len(v) == 11 and y < this)}
    if rebase_year in full:
        b = full[rebase_year]
        full = {y: round(v / b * 100, 2) for y, v in full.items()}
    return dict(sorted(full.items()))


# ---------- USA ----------
def us_series():
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCNS"
    try:
        r = requests.get(url, headers=UA, timeout=40)
        r.raise_for_status()
        out = {}
        for row in csv.DictReader(io.StringIO(r.text)):
            date = row.get("observation_date") or row.get("DATE")
            val = row.get("CPIAUCNS")
            if date and val not in (None, "", "."):
                out[date[:7]] = float(val)
        if len(out) > 120:
            return out, "U.S. Bureau of Labor Statistics · CPI-U (über FRED, CPIAUCNS)", "https://fred.stlouisfed.org/series/CPIAUCNS"
    except Exception as e:
        print("fred fail", e, file=sys.stderr)
    # Ersatz: BLS API v1 (max. 10 Jahre je Abfrage)
    out, year = {}, dt.date.today().year
    for start in (year - 9, year - 19, year - 29):
        try:
            r = requests.post("https://api.bls.gov/publicAPI/v1/timeseries/data/",
                              json={"seriesid": ["CUUR0000SA0"], "startyear": str(start), "endyear": str(start + 9)},
                              headers=UA, timeout=40)
            for d in r.json()["Results"]["series"][0]["data"]:
                if d["period"].startswith("M") and d["period"] != "M13":
                    out[f"{d['year']}-{d['period'][1:]}"] = float(d["value"])
        except Exception as e:
            print("bls fail", start, e, file=sys.stderr)
    if len(out) < 24:
        raise RuntimeError("USA: keine Daten")
    return out, "U.S. Bureau of Labor Statistics · CPI-U (CUUR0000SA0)", "https://www.bls.gov/cpi/"


# ---------- Großbritannien ----------
def uk_series():
    url = "https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/d7bt/mm23/data"
    r = requests.get(url, headers=UA, timeout=40)
    r.raise_for_status()
    d = r.json()
    out = {}
    for m in d.get("months", []):
        parts = (m.get("date") or "").split()
        if len(parts) == 2 and parts[1][:3].upper() in MON and m.get("value") not in (None, ""):
            out[f"{parts[0]}-{MON[parts[1][:3].upper()]:02d}"] = float(m["value"])
    if len(out) < 24:
        raise RuntimeError("UK: zu wenige Werte")
    return out, "Office for National Statistics · CPI (D7BT, 2015 = 100)", "https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/d7bt/mm23"


def main():
    markets, ann = load(MARKETS), load(ANNUAL)
    if not markets:
        sys.exit("markets.json fehlt")
    errors = []
    try:
        markets["fx"] = fx_rates(markets.get("fx"))
    except Exception as e:
        errors.append(f"fx: {e}")
    infl = markets.setdefault("inflation", {})
    for geo, fn in (("US", us_series), ("UK", uk_series)):
        try:
            series, source, url = fn()
            period, rate = yoy(series)
            cand = dict(rate=rate, period=period, source=source, series=geo,
                        unit="Veränderung zum Vorjahresmonat in %", checked=NOW, url=url)
            cur = infl.get(geo)
            if not cur or cand["period"] >= cur.get("period", ""):
                infl[geo] = cand
            if ann:
                idx = annual(series)
                if len(idx) > 10:
                    ann[geo] = dict(index=idx, base="2015=100", url=url, source=source, updated=NOW)
        except Exception as e:
            errors.append(f"{geo}: {e}")
    MARKETS.write_text(json.dumps(markets, ensure_ascii=False, indent=1), encoding="utf-8")
    if ann:
        ANNUAL.write_text(json.dumps(ann, ensure_ascii=False, indent=1), encoding="utf-8")
    print("fx:", len(markets.get("fx", {}).get("rates", {})), "Kurse · Inflation:", {k: v.get("period") for k, v in infl.items()})
    if errors:
        print("Fehler:", "; ".join(errors), file=sys.stderr)


if __name__ == "__main__":
    main()
