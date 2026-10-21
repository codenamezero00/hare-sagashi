# 使い方: CITIES に市町村を足して python3 build.py → index.html ができる
import json, os, urllib.request, urllib.parse
from datetime import date, timedelta

CITIES = [
    ("伊勢崎市", 36.3114, 139.1969),
    # ("前橋市", 36.3895, 139.0634),  # 足すときはこの形で
]
START, END = "2006-01-01", "2025-12-31"
HERE = os.path.dirname(os.path.abspath(__file__))

def fetch(name, lat, lon):
    path = os.path.join(HERE, "raw", name + ".json")
    if not os.path.exists(path):
        q = urllib.parse.urlencode(dict(latitude=lat, longitude=lon, start_date=START, end_date=END,
                                        hourly="precipitation", timezone="Asia/Tokyo"))
        urllib.request.urlretrieve("https://archive-api.open-meteo.com/v1/archive?" + q, path)
    return json.load(open(path))

def slot(d):  # 1/1=0 … 12/31=365（2/29は59番に固定）
    return (date(2000, d.month, d.day) - date(2000, 1, 1)).days

out = {}
for name, lat, lon in CITIES:
    h = fetch(name, lat, lon)["hourly"]
    years = {}
    for t, p in zip(h["time"], h["precipitation"]):
        d = date.fromisoformat(t[:10]); hr = int(t[11:13])
        y = years.setdefault(d.year, [[None] * 366, [None] * 366])
        s = slot(d)
        if y[0][s] is None: y[0][s] = 0; y[1][s] = 0
        v = round((p or 0) * 10)
        y[0][s] += v
        if 9 <= hr < 17: y[1][s] += v
    out[name] = {"lat": lat, "lon": lon, "years": {str(k): v for k, v in sorted(years.items())}}

tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
html = tpl.replace("/*DATA*/null", json.dumps(out, separators=(",", ":")))
open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(html)
print("ok", list(out), f"{len(html)//1024}KB")
