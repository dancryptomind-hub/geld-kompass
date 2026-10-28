"""Amtlicher HVPI-Gesamtindex über Eurostat, kostenlos und ohne API-Schlüssel."""
import datetime as dt
import json
import math
import time
from urllib.parse import urlencode
from urllib.request import Request,urlopen

BASE='https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/prc_hicp_minr'
def api_url(geo):
 return BASE+'?'+urlencode(dict(lang='DE',freq='M',unit='RCH_A',coicop18='TOTAL',geo=geo,lastTimePeriod=12))

def parse_eurostat(data,geo,checked=None):
 dims=data['id'];sizes=data['size'];dimensions=data['dimension'];values=data['value']
 select=dict(freq='M',unit='RCH_A',coicop18='TOTAL',geo=geo)
 if not set(select).issubset(dims) or 'time' not in dims:raise ValueError('Falsche Datenreihe')
 def position(dim,key):
  idx=dimensions[dim]['category']['index']
  return idx.index(key) if isinstance(idx,list) else idx[key]
 for dim,key in select.items():position(dim,key)
 times=dimensions['time']['category']['index'];best=None
 now=checked or dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
 for period in sorted(times):
  if len(period)!=7 or period>now[:7]:continue
  offset=0
  for dim,size in zip(dims,sizes):
   if dim=='time':pos=position(dim,period)
   elif dim in select:pos=position(dim,select[dim])
   elif size==1:pos=0
   else:raise ValueError('Mehrdeutige Datenreihe '+dim)
   offset=offset*size+pos
  value=values[offset] if isinstance(values,list) and offset<len(values) else values.get(str(offset)) if isinstance(values,dict) else None
  if isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value):
   best=dict(rate=value,period=period,source='Eurostat · HVPI',series='prc_hicp_minr',unit='Veränderung zum Vorjahresmonat in %',checked=now,sourceUpdated=data.get('updated'),url=api_url(geo))
 if best is None:raise ValueError('Keine gültige Beobachtung')
 return best

def choose_observation(current,candidate):
 if candidate and (not current or candidate['period']>=current['period']):return candidate
 return current

def fetch_inflation(geo):
 error=None
 for attempt in range(3):
  try:
   request=Request(api_url(geo),headers={'User-Agent':'GeldKompass/2.0','Accept':'application/json'})
   with urlopen(request,timeout=25) as response:return parse_eurostat(json.load(response),geo)
  except Exception as exc:
   error=exc
   if attempt<2:time.sleep(2**attempt)
 raise RuntimeError(f'Eurostat {geo}: {error}')

if __name__=='__main__':
 for geo in ['DE','EA']:
  print(json.dumps(fetch_inflation(geo),ensure_ascii=False))
