"""Dividenden je Wertpapier für den Dividenden- und Cashflow-Kalender.
Für jede Aktie/jeden ETF aus scripts/instruments.json: Ausschüttungen der letzten 12 Monate je Anteil (in EUR),
Zahlungsmonate und Häufigkeit. Ergebnis: data/dividends.json. Läuft wöchentlich per GitHub Action („Dividenden“)."""
import json, sys, datetime as dt
from pathlib import Path
import yfinance as yf

ROOT = Path(__file__).resolve().parent.parent
items = json.loads((ROOT / "scripts" / "instruments.json").read_text(encoding="utf-8"))
try:
    fx = json.loads((ROOT / "data" / "markets.json").read_text(encoding="utf-8")).get("fx", {}).get("rates", {})
except Exception:
    fx = {}
out = {}
cut = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=372)
for x in items:
    if x["t"] not in ("Aktie", "ETF") or x.get("cg"):
        continue
    try:
        t = yf.Ticker(x["s"])
        d = t.dividends
        if d is None or d.empty:
            continue
        d = d[d.index >= cut]
        if d.empty:
            continue
        cur = (t.history_metadata or {}).get("currency") or "EUR"
        amt = float(d.sum())
        if cur == "GBp":  # Pence
            amt, cur = amt / 100, "GBP"
        rate = 1.0 if cur == "EUR" else fx.get(cur)
        if not rate:
            continue
        months = sorted({int(i.month) for i in d.index})
        out[x["s"]] = {"dv": round(amt / rate, 4), "m": months, "n": int(len(d)), "c": cur, "last": d.index[-1].strftime("%Y-%m-%d")}
    except Exception as e:
        print("fail", x["s"], e, file=sys.stderr)
(ROOT / "data" / "dividends.json").write_text(json.dumps({"updated": dt.date.today().isoformat(), "d": out}, ensure_ascii=False, indent=0), encoding="utf-8")
print(len(out), "Werte mit Dividende")
