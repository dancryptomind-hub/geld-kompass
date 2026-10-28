"""Aktualisiert data/markets.json für den Geld Kompass.

Läuft täglich per GitHub Action. Quellen (alle kostenlos, ohne API-Schlüssel):
  - ETFs und Aktien: Yahoo Finance über yfinance
  - Krypto: CoinGecko (Fallback: Yahoo)
  - Inflation: Eurostat HVPI (prc_hicp_minr), Veränderung zum Vorjahresmonat

Neue Werte: in scripts/instruments.json ergänzen (s = Yahoo-Symbol, n = Name, t = Typ, i = ISIN, a = Suchbegriffe, cg = CoinGecko-ID bei Krypto).
Schlägt eine Quelle fehl, bleibt der letzte bekannte Wert erhalten.
"""
import json
import datetime as dt
from pathlib import Path

import requests
import yfinance as yf
from inflation_data import fetch_inflation, choose_observation

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "markets.json"
LIST = ROOT / "scripts" / "instruments.json"
INFL_GEO = ["DE", "AT", "EA"]
UA = {"User-Agent": "GeldKompass/1.0 (+github pages)"}


def load_old():
    try:
        return json.loads(OUT.read_text(encoding="utf-8"))
    except Exception:
        return {}


def fx_to_eur(cache, currency):
    """Kurs für 1 Einheit Fremdwährung in EUR."""
    if not currency or currency == "EUR":
        return 1.0
    if currency in cache:
        return cache[currency]
    rate = None
    try:
        hist = yf.Ticker(f"{currency}EUR=X").history(period="5d")
        if not hist.empty:
            rate = float(hist["Close"].dropna().iloc[-1])
    except Exception:
        pass
    cache[currency] = rate
    return rate


def yahoo_prices(symbols):
    prices, fx = {}, {}
    for sym in symbols:
        try:
            t = yf.Ticker(sym)
            hist = t.history(period="5d")
            if hist.empty:
                continue
            close = float(hist["Close"].dropna().iloc[-1])
            cur = None
            try:
                cur = t.fast_info.get("currency")
            except Exception:
                pass
            if cur == "GBp":  # London in Pence
                close, cur = close / 100, "GBP"
            rate = fx_to_eur(fx, cur or "EUR")
            if rate:
                prices[sym] = round(close * rate, 4)
        except Exception as e:
            print("yahoo fail", sym, e)
    return prices


def yearly_returns(symbols):
    """Durchschnittliche Jahresrendite der letzten (bis zu) 10 Jahre inkl. Dividenden, in Heimatwährung."""
    out = {}
    for sym in symbols:
        try:
            hist = yf.Ticker(sym).history(period="10y", interval="1mo", auto_adjust=True)
            closes = hist["Close"].dropna()
            if len(closes) < 36:
                continue
            years = (closes.index[-1] - closes.index[0]).days / 365.25
            first, last = float(closes.iloc[0]), float(closes.iloc[-1])
            if years >= 3 and first > 0:
                out[sym] = (round(((last / first) ** (1 / years) - 1) * 100, 1), round(years, 1))
        except Exception as e:
            print("history fail", sym, e)
    return out


def coingecko_prices(ids):
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": ",".join(ids.values()), "vs_currencies": "eur"},
            headers=UA, timeout=20,
        )
        r.raise_for_status()
        d = r.json()
        return {sym: d[cid]["eur"] for sym, cid in ids.items() if cid in d}
    except Exception as e:
        print("coingecko fail", e)
        return {}


def eurostat_inflation(geo):
    try:
        return fetch_inflation(geo)
    except Exception as e:
        print("eurostat fail", geo, e)
        return None


def main():
    old = load_old()
    old_prices = {x["s"]: x.get("p") for x in old.get("instruments", [])}
    instruments = json.loads(LIST.read_text(encoding="utf-8"))

    crypto_ids = {x["s"]: x["cg"] for x in instruments if x.get("cg")}
    prices = yahoo_prices([x["s"] for x in instruments if not x.get("cg")])
    prices.update(coingecko_prices(crypto_ids))
    prices.update(yahoo_prices([s for s in crypto_ids if s not in prices]))

    fresh = 0
    for x in instruments:
        p = prices.get(x["s"])
        if p:
            fresh += 1
        x["p"] = p if p else old_prices.get(x["s"])

    # Rendite der letzten 10 Jahre für den "Was wäre wenn"-Rechner (Marken-Aktien und ETFs)
    old_r = {x["s"]: (x.get("r"), x.get("ry")) for x in old.get("instruments", [])}
    rets = yearly_returns([x["s"] for x in instruments if x.get("r") is not None or x["t"] != "Krypto"])
    for x in instruments:
        if x["s"] in rets:
            x["r"], x["ry"] = rets[x["s"]]
            x.pop("rs", None)
        elif old_r.get(x["s"], (None,))[0] is not None and "rs" not in x:
            x["r"], x["ry"] = old_r[x["s"]]

    inflation = old.get("inflation", {})
    inflation_errors = []
    for geo in INFL_GEO:
        v = eurostat_inflation(geo)
        if v:
            inflation[geo] = choose_observation(inflation.get(geo), v)
        else:
            inflation_errors.append(geo)

    data = {
        "updated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "status": "live" if fresh >= len(instruments) * 0.6 else old.get("status", "start"),
        "currency": "EUR",
        "inflation": inflation,
        "instruments": instruments,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{fresh}/{len(instruments)} Kurse aktuell, Inflation: {list(inflation)}")
    if inflation_errors:
        raise RuntimeError("Inflationsaktualisierung fehlgeschlagen: " + ", ".join(inflation_errors))


if __name__ == "__main__":
    main()
