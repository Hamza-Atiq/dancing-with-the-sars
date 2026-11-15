"""Render the images and the data file used by the story page (docs/index.html).

Everything is drawn from the project's own extracts and result files:
  data/lang/098_A_016_<date>.npz      NISAR GCOV backscatter, 10 m
  data/series/098_A_016_<pair>.npz    NISAR GUNW wrapped phase and coherence, 20 m
  data/site/optical_*.npz             HLS Sentinel-2 true colour, 30 m (scripts/site_optical.py)
  docs/data/*.json                    results written by pipeline/build.py
  data/s1/s1_patch.json               Sentinel-1 patch measurements (optional; scripts/s1_patch.py)
Output: docs/story/*.webp and docs/story/story.json

Run: C:/Users/HP/anaconda3/python.exe scripts/site_assets.py
"""
import json
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import zoom, uniform_filter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'pipeline'))
import geo      # noqa: E402
import series as se  # noqa: E402

OUT = ROOT / 'docs/story'
OUT.mkdir(parents=True, exist_ok=True)

SITE = (351000, 360000, 3126500, 3133000)     # before/after views, UTM 45N
ZOOM = (354300, 356700, 3128900, 3131200)     # phase panels
PHASE_PAIRS = ['20260620_20260702', '20260702_20260714', '20260714_20260726', '20260726_20260819']


def lerp_colors(stops, t):
    """stops: list of (position 0..1, (r,g,b)); t array 0..1 -> rgb float array."""
    pos = np.array([s[0] for s in stops])
    col = np.array([s[1] for s in stops], float)
    return np.stack([np.interp(t, pos, col[:, i]) for i in range(3)], -1)


def save(rgb, name, quality=82):
    Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).save(OUT / name, quality=quality, method=6)
    return name


def crop(a, x, y, box):
    jx = (x >= box[0]) & (x <= box[1])
    iy = (y >= box[2]) & (y <= box[3])
    out = a[np.ix_(iy, jx)]
    if y[0] < y[-1]:
        out = out[::-1]                      # north up
    return out


def frac(xu, yu, box):
    """UTM point -> fraction (left, top) inside a north-up box."""
    return [round(float((xu - box[0]) / (box[1] - box[0])), 4), round(float((box[3] - yu) / (box[3] - box[2])), 4)]


# ---------- radar backscatter ----------
RADAR_STOPS = [(0.0, (6, 10, 16)), (0.35, (24, 44, 62)), (0.7, (118, 150, 168)), (1.0, (240, 246, 247))]


def radar_rgb(power, lo=-17.0, hi=5.0):
    db = 10 * np.log10(np.maximum(power, 1e-6))
    t = np.clip((db - lo) / (hi - lo), 0, 1) ** 0.9
    return lerp_colors(RADAR_STOPS, t)


def radar():
    meta = {}
    d = np.load(ROOT / 'data/lang/098_A_016_20260819.npz')
    x, y = d['x'], d['y']
    full = (float(x.min()), float(x.max()), float(y.min()), float(y.max()))
    hh = d['HHHH'] if y[0] > y[-1] else d['HHHH'][::-1]
    hh = uniform_filter(np.nan_to_num(hh), 2)
    save(radar_rgb(hh), 'radar_wide.webp', 80)
    meta['wide'] = {'file': 'radar_wide.webp', 'box_utm': full, 'w': int(hh.shape[1]), 'h': int(hh.shape[0]),
                    'date': '2026-08-19'}
    for date, tag in (('20260819', 'before'), ('20260831', 'after')):
        d = np.load(ROOT / f'data/lang/098_A_016_{date}.npz')
        a = crop(uniform_filter(np.nan_to_num(d['HHHH']), 2), d['x'], d['y'], SITE)
        rgb = radar_rgb(a)
        rgb = np.stack([zoom(rgb[..., i], 1.6, order=3) for i in range(3)], -1)
        save(rgb, f'radar_{tag}.webp', 84)
    meta['site_box_utm'] = SITE
    return meta


# ---------- optical ----------
def optical():
    out = {}
    for tag in ('before', 'after'):
        f = ROOT / f'data/site/optical_{tag}.npz'
        if not f.exists():
            continue
        d = np.load(f)
        rgb = np.stack([crop(d[b], d['x'], d['y'], SITE) for b in ('B04', 'B03', 'B02')], -1) * 1e-4
        rgb = np.clip(rgb, 0, None)
        rgb = 1.18 * rgb / (rgb + 0.22)                     # soft shoulder so snow keeps detail
        rgb = np.clip(rgb, 0, 1) ** 0.85 * 255
        rgb = np.stack([zoom(rgb[..., i], 4, order=3) for i in range(3)], -1)
        save(rgb, f'optical_{tag}.webp', 84)
        out[tag] = {'file': f'optical_{tag}.webp', 'date': str(d['date']), 'cloud_pct': float(d['cloud']),
                    'granule': str(d['title'])}
    return out


# ---------- phase ----------
PHASE_STOPS = [(0.0, (240, 166, 58)), (0.25, (27, 39, 64)), (0.5, (74, 126, 150)), (0.75, (232, 238, 240)),
               (1.0, (240, 166, 58))]                       # -pi .. +pi, cyclic; 0 = glacier blue, +-pi = ember


def phase_rgb(u, coh):
    """u: complex unit phasors (referenced), coh 0..1 -> rgb; low coherence goes dark."""
    t = (np.angle(u) + np.pi) / (2 * np.pi)
    rgb = lerp_colors(PHASE_STOPS, t)
    w = np.clip((coh - 0.15) / 0.45, 0, 1)[..., None]
    return rgb * (0.12 + 0.88 * w)


def phase_panel(p, scale):
    X, Y = np.meshgrid(p['x'], p['y'])
    u, v = se.unit(p)
    west = se.box(X, Y, se.WEST_BLOCK) & v
    ref = u[west].mean()
    ref = ref / max(abs(ref), 1e-9)
    w = np.where(v, p['coh'], 0) * u * np.conj(ref)          # coherence-weighted phasor
    wc = crop(w, p['x'], p['y'], ZOOM)
    cc = crop(np.where(v, p['coh'], 0), p['x'], p['y'], ZOOM)
    if scale != 1:
        wc = zoom(wc.real, scale, order=1) + 1j * zoom(wc.imag, scale, order=1)
        cc = zoom(cc, scale, order=1)
    return phase_rgb(wc, cc)


def phases():
    pairs = se.load_all()
    out = {'zoom_box_utm': ZOOM, 'panels': [], 'frames': []}
    for name in PHASE_PAIRS:
        out['panels'].append({'pair': name, 'file': save(phase_panel(pairs[name], 6), f'phase_{name}.webp', 86)})
    for name, p in pairs.items():
        out['frames'].append({'pair': name, 'file': save(phase_panel(p, 2), f'frame_{name}.webp', 78)})
    px, py = se.PATCH[:2], se.PATCH[2:]
    out['patch_frac'] = [frac(px[0], py[1], ZOOM), frac(px[1], py[0], ZOOM)]       # top-left, bottom-right
    wb = se.WEST_BLOCK
    out['west_frac'] = [frac(wb[0], wb[3], ZOOM), frac(wb[1], wb[2], ZOOM)]
    out['width_m'] = ZOOM[1] - ZOOM[0]
    return out


def control_steps(pair):
    """Step (rad, absolute) on every control slope resolved in this pair: same construction as
    pipeline/series.py control_ranks, returning the individual values for the dot plot."""
    pairs = se.load_all()
    sel = pairs[se.SELECT_PAIR]
    X, Y = np.meshgrid(sel['x'], sel['y'])
    n0 = int((se.box(X, Y, se.PATCH) & (sel['coh'] >= se.PATCH_COH)).sum())
    w, h = se.PATCH[1] - se.PATCH[0], se.PATCH[3] - se.PATCH[2]
    u, v = se.unit(pairs[pair])
    vals = []
    for x0 in np.arange(sel['x'].min() + 1500, sel['x'].max() - 1500, 1000):
        for y0 in np.arange(sel['y'].min() + 1500, sel['y'].max() - 1500, 1000):
            if abs(x0 - se.PATCH[0]) < 2000 and abs(y0 - se.PATCH[2]) < 2000:
                continue
            pm = se.box(X, Y, (x0, x0 + w, y0, y0 + h)) & (sel['coh'] >= se.PATCH_COH)
            if pm.sum() < n0:
                continue
            rm = se.box(X, Y, (x0 + se.WEST_BLOCK[0] - se.PATCH[0], x0 + se.WEST_BLOCK[1] - se.PATCH[0],
                               y0 + se.WEST_BLOCK[2] - se.PATCH[2], y0 + se.WEST_BLOCK[3] - se.PATCH[2]))
            m = se.measure(u, v, pm, rm)
            if m and m['consistency'] >= se.RESOLVED_CONSISTENCY and m['reference_consistency'] >= se.RESOLVED_CONSISTENCY:
                vals.append(abs(m['phase_rad']))
    return vals


# ---------- data ----------
def story(meta):
    s = json.loads((ROOT / 'docs/data/series.json').read_text())
    e = json.loads((ROOT / 'docs/data/evaluation.json').read_text())
    c = json.loads((ROOT / 'docs/data/collapse.json').read_text())
    fl = json.loads((ROOT / 'docs/data/flags.json').read_text())
    rows = []
    for r in s['rows']:
        w = r['refs']['west block']
        others = [v['los_cm'] for k, v in r['refs'].items() if v]
        rows.append({'pair': r['pair'], 'start': r['start'], 'end': r['end'], 'days': r['days'],
                     'resolved': r['resolved'], 'coh': round(r['patch_median_coherence'], 3),
                     'cm': round(w['los_cm'], 2) if w else None,
                     'cm_min': round(min(others), 2) if others else None,
                     'cm_max': round(max(others), 2) if others else None,
                     'rank': s['control_ranks'].get(r['pair'])})
    key = s['control_ranks']['20260714_20260726']
    steps = control_steps('20260714_20260726')
    assert len(steps) == key['n_controls'] and abs(max(steps) - key['control_max']) < 1e-6, (len(steps), max(steps))
    ctrl = [round(v * s['rad_to_cm'], 3) for v in steps]
    box = meta['radar']['wide']['box_utm']
    flags = []
    for pair, items in fl.items():
        for f in items if isinstance(items, list) else items.get('flags', []):
            xu, yu = f['utm']
            flags.append({'pair': pair, 'p': frac(xu, yu, box), 'lang': bool(f.get('at_langtang', f.get('langtang', False)))})
    passes = {'NISAR 098 ascending': sorted({r['start'] for r in rows} | {r['end'] for r in rows})}
    bf = ROOT / 'data/s1_bursts_at_source.json'
    if bf.exists():
        names = {'019_039570_IW1': 'Sentinel-1 019 descending', '121_258660_IW3': 'Sentinel-1 121 descending',
                 '085_180590_IW2': 'Sentinel-1 085 ascending'}
        for k, v in json.loads(bf.read_text()).items():
            passes[names.get(k.split('|')[1], k)] = sorted(x[0].replace('-', '') for x in v)
    desc = [d for d in s.get('descending', [])]
    s1f = ROOT / 'data/s1/s1_patch.json'
    out = {
        'generated_from': 'docs/data (pipeline/build.py), data/s1 (scripts/s1_patch.py)',
        'collapse_utc': s['collapse_utc'],
        'patch': {'area_km2': s['patch_area_km2'], 'pixels': s['patch_pixels'],
                  'center_lonlat': [85.52675, 28.28826]},
        'rows': rows,
        'key_pair': {'pair': '20260714_20260726', 'cm_refs': [rows[19]['cm_min'], rows[19]['cm_max']],
                     'controls_n': key['n_controls'], 'controls_at_or_above': key['controls_at_or_above_langtang'],
                     'control_max_cm': round(key['control_max'] * s['rad_to_cm'], 2),
                     'control_p95_cm': round(key['control_p95'] * s['rad_to_cm'], 2),
                     'langtang_cm': round(key['langtang_abs_rad'] * s['rad_to_cm'], 2)},
        'controls_cm': ctrl,
        'detector': {'summary': e['summary'], 'window_km2': e['window_km2'],
                     'rows': [{'pair': r['pair'], 'flags': r['flags'], 'lang': r['flags_at_langtang'],
                               'has_history': r['has_history']} for r in e['rows']]},
        'flags': flags,
        'collapse': {k: {'quiet_pct': round(v['quiet_pct'], 1), 'event_pct': round(v['event_pct'], 1),
                         'control_max_rise': round(v['control_event_minus_quiet_max'], 1),
                         'controls_n': v['controls_n']} for k, v in c['channels'].items()},
        'passes': passes,
        'descending_pairs': len(desc),
        'sentinel1': json.loads(s1f.read_text()) if s1f.exists() else None,
        'images': meta,
    }
    (OUT / 'story.json').write_text(json.dumps(out, separators=(',', ':')))
    print('flags placed:', len(flags), '| sentinel1:', 'yes' if out['sentinel1'] else 'placeholder')


def main():
    meta = {'radar': radar(), 'optical': optical(), 'phase': phases()}
    c = (355525, 3130015)
    meta['source_frac_site'] = frac(*c, SITE)
    meta['source_frac_wide'] = frac(*c, meta['radar']['wide']['box_utm'])
    story(meta)
    tot = sum(f.stat().st_size for f in OUT.iterdir())
    print('docs/story:', len(list(OUT.iterdir())), 'files,', round(tot / 1e6, 2), 'MB')


if __name__ == '__main__':
    main()
