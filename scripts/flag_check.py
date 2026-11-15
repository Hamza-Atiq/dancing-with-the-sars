"""Classify the detector's flags against NASA HLS Fmask (cloud and snow/ice), rules in project/flag_check.md.

Step 1 (automatic classes):  python scripts/flag_check.py classes
Step 2 (eye-check chips):    python scripts/flag_check.py chips
Downloads Fmask layers (small) to data/flagcheck/fmask, writes data/flagcheck/flag_check.json and
data/flagcheck/flag_check_table.txt. Step 2 writes true-colour chips for the random sample to
data/flagcheck/chips/. Needs Earthdata Login in ~/.netrc.
"""
import io, json, sys, random
from datetime import date, timedelta
from pathlib import Path
import numpy as np
import requests
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
sys.path.insert(0, str(Path(__file__).parent))
from utm import ll2xy

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/flagcheck'; FM = OUT / 'fmask'; FM.mkdir(parents=True, exist_ok=True)
BBOX = '85.33,28.20,85.62,28.37'
WIDEN, DAYS, MIN_CLEAR = 60.0, 5, 0.70
AUTUMN = ('2025-10-01T00:00:00Z', '2025-12-15T23:59:59Z')
S = requests.Session()                      # downloads: reads ~/.netrc
C = requests.Session(); C.trust_env = False  # catalogue: no proxy/netrc (as scripts/site_optical.py)


def retry(f, *a, **k):
    import time
    for n in range(5):
        try:
            r = f(*a, **k); r.raise_for_status(); return r
        except Exception as e:
            print('retry', n, str(e)[:120], flush=True); time.sleep(5 * (n + 1))
    raise RuntimeError('gave up')


def cmr(temporal):
    out = []
    for sn in ('HLSS30', 'HLSL30'):
        r = retry(C.get, 'https://cmr.earthdata.nasa.gov/search/granules.json', params={
            'short_name': sn, 'bounding_box': BBOX, 'temporal': ','.join(temporal), 'page_size': 500}, timeout=120)
        out += r.json()['feed']['entry']
    return out


def tif(url):
    r = retry(S.get, url, timeout=600)
    im = Image.open(io.BytesIO(r.content))
    a = np.asarray(im)
    sx, sy = im.tag_v2[33550][:2]; tp = im.tag_v2[33922]
    epsg = None
    k = im.tag_v2.get(34735)
    if k:                                       # GeoKey 3072 = projected CRS code
        k = list(k)
        for i in range(4, len(k), 4):
            if k[i] == 3072: epsg = k[i + 3]
    return a, tp[3] + (np.arange(a.shape[1]) + .5) * sx, tp[4] - (np.arange(a.shape[0]) + .5) * sy, epsg


def fmask(entry):
    """Fmask of one granule, cached as npz. Returns dict or None if not UTM 45N."""
    f = FM / (entry['title'] + '.npz')
    if not f.exists():
        url = next(l['href'] for l in entry['links'] if l['href'].startswith('https') and l['href'].endswith('.Fmask.tif'))
        a, xs, ys, epsg = tif(url)
        np.savez_compressed(f, a=a, x=xs, y=ys, epsg=epsg or 0, time=entry['time_start'])
    d = np.load(f)
    if int(d['epsg']) != 32645:
        return None
    return {'a': d['a'], 'x': d['x'], 'y': d['y'], 'time': str(d['time']), 'title': entry['title']}


def box_of(fl):
    lo0, la0, lo1, la1 = fl['bbox']
    xs, ys = zip(*[ll2xy(lo, la, 32645) for lo in (lo0, lo1) for la in (la0, la1)])
    return min(xs) - WIDEN, max(xs) + WIDEN, min(ys) - WIDEN, max(ys) + WIDEN


def measure(F, b):
    jx = (F['x'] >= b[0]) & (F['x'] <= b[1]); iy = (F['y'] >= b[2]) & (F['y'] <= b[3])
    m = F['a'][np.ix_(iy, jx)].astype(np.uint16)
    if m.size == 0:
        return None
    nod = m == 255
    cloud = ((m >> 1) & 1) | ((m >> 2) & 1) | ((m >> 3) & 1)
    clear = (~nod) & (cloud == 0)
    if nod.mean() > 0.5:
        return None
    n = int(clear.sum())
    return {'clear': float(clear.sum() / m.size), 'snow': float((((m >> 4) & 1) == 1)[clear].mean()) if n else None,
            'scene': F['title'], 'time': F['time'][:10]}


def best(scenes, b):
    got = [r for r in (measure(F, b) for F in scenes) if r]
    got = [r for r in got if r['clear'] >= MIN_CLEAR]
    return max(got, key=lambda r: r['clear']) if got else None


def d8(s):
    return date(int(s[:4]), int(s[4:6]), int(s[6:8]))


def classify(a, b):
    if a is None and b is None: return 'no image'
    if a is None or b is None: return 'one date'
    sa, sb = a['snow'], b['snow']
    if abs(sb - sa) >= 0.3: return 'snow change'
    if sa >= 0.5 and sb >= 0.5: return 'snow both'
    if sa < 0.2 and sb < 0.2: return 'snow-free both'
    return 'mixed'


def classes():
    F = json.loads((ROOT / 'docs/data/flags.json').read_text())
    flags = [(p, i, fl) for p, v in F.items() for i, fl in enumerate(v)]
    dates = sorted({d for p, _, fl in flags for d in p.split('_')})
    scenes = {}
    for d in dates:
        t = d8(d)
        es = cmr(((t - timedelta(DAYS)).isoformat() + 'T00:00:00Z', (t + timedelta(DAYS)).isoformat() + 'T23:59:59Z'))
        scenes[d] = [x for x in (fmask(e) for e in es) if x]
        print(d, len(es), 'granules', len(scenes[d]), 'in UTM 45N', flush=True)
    aut = [x for x in (fmask(e) for e in cmr(AUTUMN)) if x]
    print('autumn 2025', len(aut), 'scenes', flush=True)
    rows = []
    for p, i, fl in flags:
        b = box_of(fl); d0, d1 = p.split('_')
        a, e = best(scenes[d0], b), best(scenes[d1], b)
        au = best(aut, b)
        rows.append({'pair': p, 'index': i, 'at_langtang': fl['at_langtang'], 'lonlat': fl['lonlat'], 'pixels': fl['pixels'],
                     'start': a, 'end': e, 'class': classify(a, e),
                     'lasting_ice': None if au is None else au['snow'] >= 0.5, 'autumn': au})
    (OUT / 'flag_check.json').write_text(json.dumps(rows, indent=1))
    others = [r for r in rows if not r['at_langtang']]
    order = ['snow change', 'snow both', 'mixed', 'snow-free both', 'one date', 'no image']
    lines = [f'{len(others)} flags not on Langtang (of {len(rows)})', '']
    lines.append(f"{'class':16s} {'all':>4s} {'lasting ice':>12s} {'not lasting':>12s} {'no autumn img':>14s}")
    for c in order:
        g = [r for r in others if r['class'] == c]
        lines.append(f"{c:16s} {len(g):4d} {sum(r['lasting_ice'] is True for r in g):12d} {sum(r['lasting_ice'] is False for r in g):12d} {sum(r['lasting_ice'] is None for r in g):14d}")
    lines += ['', 'by pair: ' + 'pair, flags, ' + ', '.join(order)]
    for p in F:
        g = [r for r in others if r['pair'] == p]
        if g:
            lines.append(p + '  ' + str(len(g)) + '  ' + '  '.join(str(sum(r['class'] == c for r in g)) for c in order))
    lines += ['', 'Langtang flags:'] + [f"  {r['pair']} {r['class']} start {r['start'] and round(r['start']['snow'], 2)} end {r['end'] and round(r['end']['snow'], 2)}" for r in rows if r['at_langtang']]
    (OUT / 'flag_check_table.txt').write_text('\n'.join(lines))
    print('\n'.join(lines))


def chips():
    rows = json.loads((OUT / 'flag_check.json').read_text())
    others = [r for r in rows if not r['at_langtang']]
    sample = random.Random(2026).sample(others, 20)
    CH = OUT / 'chips'; CH.mkdir(exist_ok=True)
    rgb = {}
    for name, temporal in (('2025', AUTUMN), ('2026', ('2026-10-15T00:00:00Z', '2026-11-12T23:59:59Z'))):
        es = [e for e in cmr(temporal) if e['id'] and e.get('cloud_cover') not in (None, '')]
        es = [e for e in es if '.T45RUL.' in e['title'] or '.T45R' in e['title']]
        es.sort(key=lambda e: float(e['cloud_cover']))
        e = es[0]
        bands = []
        for bn in (('B04', 'B03', 'B02') if 'HLS.S30' in e['title'] else ('B04', 'B03', 'B02')):
            url = next(l['href'] for l in e['links'] if l['href'].startswith('https') and l['href'].endswith(f'.{bn}.tif'))
            a, xs, ys, epsg = tif(url); bands.append(a.astype(np.float32))
        rgb[name] = {'a': np.dstack(bands), 'x': xs, 'y': ys, 'title': e['title'], 'epsg': epsg}
        print(name, e['title'], e['cloud_cover'], 'epsg', epsg, flush=True)
    meta = []
    for k, r in enumerate(sample):
        cx, cy = ll2xy(r['lonlat'][0], r['lonlat'][1], 32645)
        tiles = []
        for name in ('2025', '2026'):
            R = rgb[name]
            jx = np.flatnonzero(np.abs(R['x'] - cx) <= 1500); iy = np.flatnonzero(np.abs(R['y'] - cy) <= 1500)
            c = R['a'][np.ix_(iy, jx)]
            c = np.clip(np.where(c < 0, 0, c) / 3000.0, 0, 1) ** (1 / 1.6)
            im = Image.fromarray((c * 255).astype(np.uint8)).resize((300, 300), Image.NEAREST)
            px_per_m = 300 / (c.shape[1] * 30)
            arr = np.asarray(im).copy()
            m = int(150 - 150 * px_per_m); M = int(150 + 150 * px_per_m)   # 300 m square around the flag centre (chip is 3 km)
            arr[m:M, [m, M - 1]] = [255, 60, 60]; arr[[m, M - 1], m:M] = [255, 60, 60]
            tiles.append(arr)
        Image.fromarray(np.hstack([tiles[0], np.full((300, 6, 3), 255, np.uint8), tiles[1]])).save(CH / f'{k:02d}_{r["pair"]}_{r["index"]}.png')
        meta.append({'k': k, 'pair': r['pair'], 'index': r['index'], 'lonlat': r['lonlat'], 'class': r['class'], 'lasting_ice': r['lasting_ice']})
    (CH / 'sample.json').write_text(json.dumps({'scenes': {n: rgb[n]['title'] for n in rgb}, 'sample': meta}, indent=1))
    print('chips written', len(meta))


if __name__ == '__main__':
    {'classes': classes, 'chips': chips}[sys.argv[1]]()
