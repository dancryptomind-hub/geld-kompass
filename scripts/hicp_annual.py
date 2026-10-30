"""Jahresdurchschnitt des HVPI (Eurostat prc_hicp_aind) für Deutschland und den Euroraum.
Grundlage des Inflationsrechners unter /rechner/inflationsrechner/. Kostenlos, ohne API-Schlüssel."""
import datetime as dt, json, math, sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE = 'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/prc_hicp_aind'

def fetch(geo):
    last = None
    for ck, cv in (('coicop18', 'TOTAL'), ('coicop', 'CP00')):
        q = dict(lang='DE', unit='INX_A_AVG', geo=geo); q[ck] = cv
        url = BASE + '?' + urlencode(q)
        try:
            data = json.load(urlopen(Request(url, headers={'User-Agent': 'geld-kompass'}), timeout=40))
        except Exception as e:
            last = e; continue
        dims, sizes, dim = data['id'], data['size'], data['dimension']
        if 'time' not in dims or any(s > 1 for d, s in zip(dims, sizes) if d != 'time'):
            last = ValueError('mehrdeutig %s' % dict(zip(dims, sizes))); continue
        t = dim['time']['category']['index']
        inv = {v: k for k, v in t.items()} if isinstance(t, dict) else dict(enumerate(t))
        vals = data['value']
        it = vals.items() if isinstance(vals, dict) else enumerate(vals)
        out = {}
        for k, v in it:
            if isinstance(v, (int, float)) and math.isfinite(v):
                out[inv[int(k)]] = v
        if len(out) > 10:
            return dict(index=dict(sorted(out.items())), base='2015=100', url=url, updated=data.get('updated'))
        last = ValueError('zu wenige Werte')
    raise last

res = {'checked': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'),
       'source': 'Eurostat · HVPI Jahresdurchschnitt (prc_hicp_aind)'}
for geo in ('DE', 'EA20', 'AT'):
    try: res[geo] = fetch(geo)
    except Exception as e: print('Fehler', geo, e, file=sys.stderr)
if 'DE' not in res: sys.exit('Keine Daten für DE')
json.dump(res, open('data/hicp_annual.json', 'w'), ensure_ascii=False, indent=1)
print('ok', {k: len(v['index']) for k, v in res.items() if isinstance(v, dict)})
