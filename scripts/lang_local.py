"""Exploratory local checks. Circular AOIs are NOT a mapped collapse outline.

Run with Anaconda Python. Outputs are diagnostic, not hazard predictions.
"""
from pathlib import Path
from datetime import datetime
import json
import numpy as np
from PIL import Image, ImageDraw
from utm import ll2xy

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/lang'
OUT = ROOT / 'data/lang_check'
OUT.mkdir(exist_ok=True)
# Published reconnaissance location; rounded to avoid implying survey precision.
LON, LAT = 85.5252, 28.2853
report = {'aoi': {'lon': LON, 'lat': LAT, 'radii_m': [300, 500, 800],
                  'status': 'exploratory circles, not a validated scar polygon',
                  'source': 'https://www.antarcticglaciers.org/2026/08/august-2026-nepal-tibet-floods/'},
          'controls': 'annulus 1500-3000 m, candidate reference only; stability unverified',
          'gcov': {}, 'gunw': {}, 'goff': {}}
FEATURES = json.loads((ROOT / 'data/lang_sources/detachment.geojson').read_text())['features']
report['detachment'] = {'source': 'https://unosat.org/products/4260',
    'status': 'UNOSAT preliminary Landsat-9 detachment polygon, not field validated',
    'metadata_conflict': 'layer name says 20260826 but SensorDate attribute says 2026-09-26; preserved as received'}

def regions(d):
    r = radius(d)
    selections = {str(rad): r <= rad for rad in [300, 500, 800]}
    X, Y = d['x'][None, :], d['y'][:, None]
    union = np.zeros(r.shape, bool)
    for f in FEATURES:
        for polygon in f['geometry']['coordinates']:
            inside = np.zeros(r.shape, bool)
            for ring in polygon:
                points = [ll2xy(lon, lat, int(d['epsg'])) for lon, lat in ring]
                for (x1,y1),(x2,y2) in zip(points[:-1],points[1:]):
                    if y1 == y2: continue
                    inside ^= ((y1 > Y) != (y2 > Y)) & (X < (x2-x1)*(Y-y1)/(y2-y1)+x1)
            union |= inside
    selections['unosat_detachment'] = union
    return selections

def radius(d):
    cx, cy = ll2xy(LON, LAT, int(d['epsg']))
    return np.hypot(d['x'][None, :] - cx, d['y'][:, None] - cy)

def stats(a, valid):
    v = a[valid & np.isfinite(a)]
    return {'n': int(v.size), 'p10_p50_p90': np.percentile(v, [10, 50, 90]).tolist() if v.size else None}

def gridcheck(a, b):
    for k in ('x', 'y', 'epsg'):
        assert np.array_equal(a[k], b[k]), f'grid mismatch: {k}'

def panel(d, a, valid, title, limit):
    """Fixed physical 8-km crop, blue/white/red, grey excluded values."""
    cx, cy = ll2xy(LON, LAT, int(d['epsg']))
    ix = np.flatnonzero(abs(d['x'] - cx) < 4000)
    iy = np.flatnonzero(abs(d['y'] - cy) < 4000)
    z = a[np.ix_(iy, ix)] / limit
    good = valid[np.ix_(iy, ix)] & np.isfinite(z)
    z = np.nan_to_num(np.clip(z, -1, 1))
    rgb = np.stack([255 * (1 + np.minimum(z, 0)), 255 * (1 - abs(z)),
                    255 * (1 - np.maximum(z, 0))], axis=-1).astype('uint8')
    rgb[~good] = [110, 110, 110]
    im = Image.new('RGB', (420, 460), 'white')
    im.paste(Image.fromarray(rgb).resize((400, 400), Image.Resampling.NEAREST), (10, 35))
    draw = ImageDraw.Draw(im)
    draw.text((10, 8), title, fill='black')
    px = 10 + (cx - d['x'][ix[0]]) / (d['x'][ix[-1]] - d['x'][ix[0]]) * 400
    py = 35 + (cy - d['y'][iy[0]]) / (d['y'][iy[-1]] - d['y'][iy[0]]) * 400
    rr = 500 / abs(d['x'][ix[-1]] - d['x'][ix[0]]) * 400
    draw.ellipse((px-rr, py-rr, px+rr, py+rr), outline='black', width=2)
    for f in FEATURES:
        for polygon in f['geometry']['coordinates']:
            for ring in polygon:
                pts = [ll2xy(lon,lat,int(d['epsg'])) for lon,lat in ring]
                pts = [(10+(x-d['x'][ix[0]])/(d['x'][ix[-1]]-d['x'][ix[0]])*400,
                        35+(y-d['y'][iy[0]])/(d['y'][iy[-1]]-d['y'][iy[0]])*400) for x,y in pts]
                draw.line(pts, fill=(0,120,0), width=2)
    draw.text((10, 441), f'Blue -{limit}; white 0; red +{limit}; grey excluded', fill='black')
    return im

gcov = {s: dict(np.load(DATA / f'098_A_016_{s}.npz')) for s in ['20260714', '20260726', '20260819', '20260831']}
base = gcov['20260714']
for d in gcov.values(): gridcheck(base, d)
r = radius(base)
areas = regions(base)
panels = []
for pol in ['HHHH', 'HVHV']:
    common = np.ones(r.shape, bool)
    for d in gcov.values():
        common &= np.isfinite(d[pol]) & (d[pol] > 0) & (d['mask'] >= 1) & (d['mask'] <= 5)
    for label, a, b in [('quiet', '20260714', '20260726'), ('event', '20260819', '20260831')]:
        delta = np.full(r.shape, np.nan)
        delta[common] = 10 * np.log10(gcov[b][pol][common] / gcov[a][pol][common])
        rows = {}
        for name, sel in areas.items():
            valid = common & sel
            rows[name] = stats(delta, valid)
            rows[name]['fraction_abs_gt_3db'] = float(np.mean(abs(delta[valid]) > 3)) if valid.any() else None
            rows[name]['valid_fraction'] = float(valid.sum() / sel.sum())
        rows['annulus'] = stats(delta, common & (r >= 1500) & (r <= 3000))
        report['gcov'][label+'_'+pol] = rows
        panels.append(panel(base, delta, common, f'{label} {pol}: power change dB', 6))
sheet = Image.new('RGB', (840, 920), 'white')
for i, im in enumerate(panels): sheet.paste(im, ((i % 2)*420, (i // 2)*460))
sheet.save(OUT / 'local_backscatter.png')
del gcov

pairs = [(p, dict(np.load(p))) for p in sorted(DATA.glob('GUNW_*.npz'))]
base = pairs[0][1]
for _, d in pairs: gridcheck(base, d)
r = radius(base)
areas = regions(base)
common = np.ones(r.shape, bool)
for p, d in pairs:
    # Do not require a destroyed surface to remain coherent after collapse.
    if p.stem.split('_')[-2] not in ('20260702', '20260714', '20260726'):
        continue
    common &= (d['coherenceMagnitude'] >= .6) & (d['coherenceMagnitude'] <= 1) & (d['connectedComponents'] == 1)
    common &= np.isfinite(d['unwrappedPhase']) & np.isfinite(d['ionospherePhaseScreen'])
report['gunw_common_pixels'] = {name: int((common & sel).sum()) for name, sel in areas.items()}
report['gunw_common_definition'] = 'coherence >=0.6, component 1, finite phase and ionosphere across July 2-14, July 14-26, July 26-August 19 (published benchmark intervals); other dates independently screened'
panels = []
for p, d in pairs:
    start, end = p.stem.split('_')[-2:]
    days = (datetime.strptime(end, '%Y%m%d') - datetime.strptime(start, '%Y%m%d')).days
    rows = {'days': days, 'phase_direction': 'unverified; positive phase-equivalent only', 'radii': {}}
    per_pair = np.isfinite(d['unwrappedPhase']) & np.isfinite(d['ionospherePhaseScreen']) & (d['coherenceMagnitude'] >= .6) & (d['coherenceMagnitude'] <= 1) & (d['connectedComponents'] == 1)
    active = common & per_pair
    fine = {'x': d['xw'], 'y': d['yw'], 'epsg': d['epsg']}
    fine_areas = regions(fine)
    for name, sel in areas.items():
        rows['radii'][name] = {'coherence': stats(d['coherenceMagnitude'], sel),
            'fraction_coherence_ge_0_6': float(np.mean(d['coherenceMagnitude'][sel] >= .6)),
            'components': {str(int(k)): int(v) for k,v in zip(*np.unique(d['connectedComponents'][sel], return_counts=True))},
            'per_pair_usable_pixels': int((sel & per_pair).sum()),
            'wrapped_20m_coherence': stats(d['wcoh'], fine_areas[name]),
            'wrapped_20m_fraction_ge_0_6': float(np.mean(d['wcoh'][fine_areas[name]] >= .6))}
    ref = active & (r >= 1500) & (r <= 3000)
    assert ref.any(), 'No common reference pixels'
    factor = 299792458 / float(d['f0']) / (4*np.pi) * 100 / days
    for label, phase in [('raw', d['unwrappedPhase']), ('minus_ionosphere', d['unwrappedPhase']-d['ionospherePhaseScreen'])]:
        relative = phase - np.median(phase[ref])
        rows[label] = {name: stats(relative * factor, active & sel) for name, sel in areas.items()}
        rows[label]['reference_n'] = int(ref.sum())
        rows[label]['reference_p10_p50_p90_cm_day'] = stats(relative * factor, ref)
        if label == 'minus_ionosphere':
            panels.append(panel(d, relative * factor, active, f'{start}-{end}: phase-equiv cm/day', 1.2))
    report['gunw'][p.name] = rows
sheet = Image.new('RGB', (1260, 920), 'white')
for i, im in enumerate(panels): sheet.paste(im, ((i % 3)*420, (i // 3)*460))
sheet.save(OUT / 'local_phase_diagnostic.png')

for p in sorted(DATA.glob('GOFF_*.npz')):
    with np.load(p) as d:
        r = radius(d)
        areas = regions(d)
        start, end = p.stem.split('_')[-2:]
        days = (datetime.strptime(end, '%Y%m%d') - datetime.strptime(start, '%Y%m%d')).days
        rows = {'days': days, 'note': 'unreferenced native offsets; units/provenance and quality calibration pending'}
        for layer in ['layer1', 'layer2', 'layer3']:
            rows[layer] = {name: {k: stats(d[layer+'_'+k], sel) for k in ['alongTrackOffset', 'slantRangeOffset', 'snr', 'correlationSurfacePeak']} for name, sel in areas.items()}
        report['goff'][p.name] = rows
(OUT / 'local_checks.json').write_text(json.dumps(report, indent=2, allow_nan=False), encoding='utf-8')
print(json.dumps({'common_gunw_pixels': report['gunw_common_pixels'], 'output': str(OUT)}, indent=2))
