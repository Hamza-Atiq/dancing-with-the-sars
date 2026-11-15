"""Catalogue only (no data opened): NISAR GUNW pairs covering a point.
Run: python scripts/indep_catalogue.py LON LAT
Prints track, frame, start, end, version for every granule over the point."""
import json, sys, urllib.parse, urllib.request
from collections import defaultdict

SN = 'NISAR_L2_GUNW_PROVISIONAL_V1'
lon, lat = float(sys.argv[1]), float(sys.argv[2])
items = []
for page in range(1, 20):
    q = dict(short_name=SN, point=f'{lon},{lat}', page_size=2000, page_num=page)
    with urllib.request.urlopen('https://cmr.earthdata.nasa.gov/search/granules.umm_json?' + urllib.parse.urlencode(q), timeout=120) as r:
        got = json.load(r)['items']
    items += got
    if len(got) < 2000:
        break
pairs = defaultdict(list)
for i in items:
    g = i['umm']['GranuleUR']; p = g.split('_')
    pairs[('_'.join(p[5:8]), p[11][:8], p[13][:8])].append(p[15])
for k in sorted(pairs):
    print(*k, ','.join(sorted(pairs[k])))
print(len(items), 'granules', len(pairs), 'pairs')
