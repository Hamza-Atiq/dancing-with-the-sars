"""Save dated CMR candidates; do not silently choose among product versions."""
from pathlib import Path
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone

out = Path(__file__).resolve().parents[1] / 'data/lang_sources'
out.mkdir(exist_ok=True)
result = {'retrieved_utc': datetime.now(timezone.utc).isoformat(), 'collections': {}}
for product in ['GCOV', 'GUNW', 'GOFF']:
    short_name = f'NISAR_L2_{product}_PROVISIONAL_V1'
    query = dict(short_name=short_name, bounding_box='85.50,28.27,85.54,28.31',
                 temporal='2026-06-01T00:00:00Z,2026-09-02T00:00:00Z', page_size=2000)
    all_items = []
    for page in range(1, 20):
        url = 'https://cmr.earthdata.nasa.gov/search/granules.umm_json?' + urllib.parse.urlencode(dict(query, page_num=page))
        with urllib.request.urlopen(url, timeout=90) as response:
            items = json.load(response)['items']
        all_items.extend(items)
        if len(items) < 2000:
            break
    else:
        raise RuntimeError('Pagination safety limit reached')
    result['collections'][product] = {'query': query, 'items': all_items}
    (out / 'cmr_candidates.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    counts = {}
    for item in all_items:
        g = item['umm']['GranuleUR'].split('_')
        track = '_'.join(g[5:8])
        counts[track] = counts.get(track, 0) + 1
    print(product, counts, flush=True)
