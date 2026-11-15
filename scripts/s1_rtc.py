"""Brightness (backscatter) of the Langtang patch in ready-made Sentinel-1 products (OPERA RTC-S1, 30 m, VV).

Question: did the radar brightness of the patch change in the last passes before the collapse
(track 19: 12 Aug -> 24 Aug, 50 h before) more than it does on comparable slopes?

Rules, written before any RTC file was opened:
  * patch = the 141 NISAR-selected patch pixels (pipeline/series.py); the RTC image is sampled at their
    centres by nearest neighbour
  * a pixel is used only if the product's own mask says valid (0 = valid; 1 shadow, 2 layover, 3 both, 255 none)
    in BOTH dates of a pair, and the value is finite and > 0
  * a box is measured in a pair only if at least half of its pixels are usable
  * value = median VV backscatter in dB over the usable pixels; change = later date minus earlier date, same track
  * controls = the same control boxes as scripts/s1_patch.py, measured the same way in the same pair
  * the patch "stands out" in a pair if its absolute change is at or above the 95th percentile of the controls
  * every consecutive pair on every track from 1 May to 11 Nov 2026 is reported, not only the last ones
  * where a date has two product versions, the later-produced one is used
Nothing in the RTC data is used to choose pixels.

Follow-up added AFTER the 2026 table was seen (the patch brightened by about 9 dB from June to the end of July):
the same measurement, unchanged, on the same months of 2025 (add "2025" as a second argument). Stated before the
2025 files were opened: if the patch shows a June-July rise in 2025 of at least half the 2026 size, the 2026 rise
is treated as seasonal (snow melting off the slope) and not as a sign of the coming collapse.

Run: C:/Users/HP/anaconda3/python.exe scripts/s1_rtc.py fetch     (downloads VV and mask, about 100 files)
     C:/Users/HP/anaconda3/python.exe scripts/s1_rtc.py measure   -> data/rtc/rtc_patch.json, rtc_patch_table.txt
"""
import io
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
import requests
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

ROOT = Path(__file__).resolve().parents[1]
YEAR = sys.argv[2] if len(sys.argv) > 2 else '2026'
OUT = ROOT / ('data/rtc' if YEAR == '2026' else f'data/rtc_{YEAR}')
CMR = 'https://cmr.earthdata.nasa.gov/search/granules.json'
POINT = '85.52701,28.28858'
TRACK = {'T019-039570-IW1': '019 D', 'T121-258660-IW3': '121 D', 'T085-180590-IW2': '085 A'}


def granules():
    r = requests.get(CMR, params={'short_name': 'OPERA_L2_RTC-S1_V1', 'point': POINT,
                                  'temporal': f'{YEAR}-05-01T00:00:00Z,{YEAR}-11-16T00:00:00Z',
                                  'page_size': 500, 'sort_key': 'start_date'}, timeout=120)
    r.raise_for_status()
    best = {}
    for g in r.json()['feed']['entry']:
        t = g['title'].split('_')            # OPERA L2 RTC-S1 burst acquired produced sat 30 v
        key = (t[3], t[4][:8])
        urls = {u['href'].rsplit('_', 1)[-1]: u['href'] for u in g['links']
                if u['href'].startswith('https') and u['href'].endswith(('_VV.tif', '_mask.tif'))}
        if key not in best or t[5] > best[key][0]:
            best[key] = (t[5], urls)
    return {k: v[1] for k, v in best.items()}


def fetch():
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = []
    for (burst, date), urls in sorted(granules().items()):
        for kind in ('VV.tif', 'mask.tif'):
            jobs.append((urls[kind], OUT / f'{burst}_{date}_{kind}'))

    def get(job):
        url, path = job
        if path.exists():
            return 'have ' + path.name
        with requests.Session() as s:
            r = s.get(url, timeout=600)
            r.raise_for_status()
            tmp = path.with_suffix('.part')
            tmp.write_bytes(r.content)
            tmp.replace(path)
        return f'got {path.name} {len(r.content) / 1e6:.1f} MB'

    with ThreadPoolExecutor(4) as ex:
        for msg in ex.map(get, jobs):
            print(msg, flush=True)


def read(path):
    im = Image.open(io.BytesIO(path.read_bytes()))
    a = np.asarray(im)
    sx, sy = im.tag_v2[33550][:2]
    tp = im.tag_v2[33922]
    gk = im.tag_v2[34735]
    keys = {gk[i]: gk[i + 3] for i in range(4, len(gk), 4)}
    off = 0.5 if keys.get(1025, 1) == 1 else 0.0
    x = tp[3] + (np.arange(a.shape[1]) + off - tp[0]) * sx
    y = tp[4] - (np.arange(a.shape[0]) + off - tp[1]) * sy
    return a, x, y, keys.get(3072)


def on_grid(a, x, y, X, Y, fill):
    j = np.rint((X - x[0]) / (x[1] - x[0])).astype(int)
    i = np.rint((Y - y[0]) / (y[1] - y[0])).astype(int)
    ok = (i >= 0) & (i < a.shape[0]) & (j >= 0) & (j < a.shape[1])
    out = np.full(X.shape, fill, dtype=a.dtype)
    out[ok] = a[i[ok], j[ok]]
    return out


def measure():
    sys.path.insert(0, str(ROOT / 'pipeline'))
    import series as se
    pairs = se.load_all()
    sel = pairs[se.SELECT_PAIR]
    patch, refs, X, Y = se.regions(pairs)
    selcoh = sel['coh']
    n0 = int(patch.sum())
    x0w, x1w, y0w, y1w = sel['x'].min(), sel['x'].max(), sel['y'].min(), sel['y'].max()
    w, h = se.PATCH[1] - se.PATCH[0], se.PATCH[3] - se.PATCH[2]
    boxes = []
    for cx in np.arange(x0w + 1500, x1w - 1500, 1000):
        for cy in np.arange(y0w + 1500, y1w - 1500, 1000):
            if abs(cx - se.PATCH[0]) < 2000 and abs(cy - se.PATCH[2]) < 2000:
                continue
            pm = se.box(X, Y, (cx, cx + w, cy, cy + h)) & (selcoh >= se.PATCH_COH)
            if pm.sum() >= n0:
                boxes.append(np.flatnonzero(pm))
    pidx = np.flatnonzero(patch)

    data = {}
    for f in sorted(OUT.glob('*_VV.tif')):
        burst, date, _ = f.name.split('_')
        vv, x, y, epsg = read(f)
        mk, xm, ym, _ = read(OUT / f'{burst}_{date}_mask.tif')
        if epsg != 32645:
            print('skip', f.name, 'epsg', epsg)
            continue
        g = on_grid(vv.astype('float32'), x, y, X, Y, np.nan)
        m = on_grid(mk, xm, ym, X, Y, 255)
        ok = (m == 0) & np.isfinite(g) & (g > 0)
        db = np.where(ok, 10 * np.log10(np.where(ok, g, 1)), np.nan).ravel()
        data.setdefault(burst, {})[date] = (db, ok.ravel(), m.ravel())

    def med(db, use, idx):
        u = use[idx]
        return float(np.median(db[idx][u])) if u.sum() * 2 >= idx.size else None

    rows = []
    for burst, byd in data.items():
        dates = sorted(byd)
        mfirst = byd[dates[0]][2][pidx]
        geom = {'track': TRACK[burst], 'patch_valid_pct': float(100 * (mfirst == 0).mean()),
                'patch_shadow_pct': float(100 * np.isin(mfirst, (1, 3)).mean()),
                'patch_layover_pct': float(100 * np.isin(mfirst, (2, 3)).mean())}
        rows.append({'geometry': geom})
        for d0, d1 in zip(dates[:-1], dates[1:]):
            a, b = byd[d0], byd[d1]
            use = a[1] & b[1]
            p0, p1 = med(a[0], use, pidx), med(b[0], use, pidx)
            row = {'track': TRACK[burst], 'start': d0, 'end': d1, 'patch_usable': int(use[pidx].sum()),
                   'patch_db_start': p0, 'patch_db_end': p1}
            ch = []
            for idx in boxes:
                c0, c1 = med(a[0], use, idx), med(b[0], use, idx)
                if c0 is not None:
                    ch.append(abs(c1 - c0))
            ch = np.array(ch)
            row['controls'] = int(ch.size)
            if ch.size:
                row.update(control_median_db=float(np.median(ch)), control_p95_db=float(np.percentile(ch, 95)),
                           control_max_db=float(ch.max()))
            if p0 is not None:
                row['change_db'] = p1 - p0
                if ch.size:
                    row['controls_at_or_above'] = int((ch >= abs(p1 - p0)).sum())
                    row['stands_out'] = bool(abs(p1 - p0) >= np.percentile(ch, 95))
            rows.append(row)
    (OUT / 'rtc_patch.json').write_text(json.dumps(rows, indent=1))
    f = lambda v, n=2: '    -' if v is None else f'{v:+.{n}f}'
    lines = []
    for r in rows:
        if 'geometry' in r:
            q = r['geometry']
            lines.append(f"-- {q['track']}: patch valid {q['patch_valid_pct']:.0f}%  shadow {q['patch_shadow_pct']:.0f}%  layover {q['patch_layover_pct']:.0f}%")
            lines.append('track  pair            usable  dB_start dB_end  change | ctl_n ctl_med ctl_p95 ctl_max  >=  out')
            continue
        lines.append(f"{r['track']} {r['start']}-{r['end'][4:]}  {r['patch_usable']:>3}/{n0}  {f(r['patch_db_start'])} {f(r['patch_db_end'])}"
                     f"  {f(r.get('change_db'))} | {r['controls']:>4}  {f(r.get('control_median_db'))}  {f(r.get('control_p95_db'))}"
                     f"  {f(r.get('control_max_db'))} {r.get('controls_at_or_above', ''):>4} {'YES' if r.get('stands_out') else ''}")
    (OUT / 'rtc_patch_table.txt').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    {'fetch': fetch, 'measure': measure}[sys.argv[1]]()
