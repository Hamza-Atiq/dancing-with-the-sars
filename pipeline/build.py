"""Regenerates everything in docs/data from data/ (spec section 7).

Usage: python pipeline/build.py [--no-images] [--no-sensitivity]
"""
import copy
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import anomaly as an
import collapse
import detect as dt
import geo
import render
import series

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/data'
IMG = OUT / 'img'
EPSG = 32645
NEAR = 300          # m: a flag whose centroid is within this margin of the patch box counts as "at Langtang"
COLLAPSE_UTC = '2026-08-26T02:52:00Z'


def dump(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=1, allow_nan=False), encoding='utf-8')


def ll(x, y):
    lon, lat = geo.xy2ll(x, y, EPSG)
    return [round(float(lon), 6), round(float(lat), 6)]


def at_langtang(f):
    b = series.PATCH
    return b[0] - NEAR <= f['x'] <= b[1] + NEAR and b[2] - NEAR <= f['y'] <= b[3] + NEAR


def box_ring(b):
    return [ll(b[0], b[2]), ll(b[1], b[2]), ll(b[1], b[3]), ll(b[0], b[3]), ll(b[0], b[2])]


def run_detector(names, A, M, x, y, params):
    res = dt.detect(A, M, x, y, params)
    rows = []
    cell_km2 = 400 / 1e6
    for name, r in zip(names, res):
        flags = sorted(r['flags'], key=lambda f: -f['pixels'])
        near = [f for f in flags if at_langtang(f)]
        by_anom = sorted(flags, key=lambda f: -f['mean_abs_rad'])
        rows.append({'pair': name, 'days': series.days(name), 'has_history': r['has_history'],
                     'measurable_km2': r['measurable_pixels'] * cell_km2, 'eligible_km2': r['eligible_pixels'] * cell_km2,
                     'flags': len(flags), 'flags_at_langtang': len(near),
                     'langtang_rank_by_area': (flags.index(near[0]) + 1) if near else None,
                     'langtang_rank_by_anomaly': (by_anom.index(max(near, key=lambda f: f['mean_abs_rad'])) + 1) if near else None,
                     'flags_per_100km2_eligible': (len(flags) / (r['eligible_pixels'] * cell_km2) * 100) if r['eligible_pixels'] else None})
    return res, rows


def summary(rows):
    h = [r for r in rows if r['has_history']]
    pre = [r for r in h if r['pair'][9:] <= '20260819']
    return {'pairs_with_history': len(h), 'total_flags': sum(r['flags'] for r in h),
            'flags_at_langtang_total': sum(r['flags_at_langtang'] for r in h),
            'pairs_with_langtang_flag': [r['pair'] for r in h if r['flags_at_langtang']],
            'median_flags_per_pair': float(np.median([r['flags'] for r in h])) if h else None,
            'max_flags_per_pair': max((r['flags'] for r in h), default=None),
            'pre_collapse_pairs_with_history': len(pre),
            'pre_collapse_flags_not_at_langtang': sum(r['flags'] - r['flags_at_langtang'] for r in pre),
            'mean_unverified_flags_per_100km2_eligible_per_pass': float(np.mean([(r['flags'] - r['flags_at_langtang']) / r['eligible_km2'] * 100 for r in h if r['eligible_km2']])) if h else None}


def main():
    images = '--no-images' not in sys.argv
    sens = '--no-sensitivity' not in sys.argv
    IMG.mkdir(parents=True, exist_ok=True)
    pairs = series.load_all()
    names = list(pairs)
    x, y = pairs[names[0]]['x'], pairs[names[0]]['y']
    for p in pairs.values():
        assert np.array_equal(p['x'], x) and np.array_equal(p['y'], y) and p['epsg'] == EPSG, 'grid mismatch'
    # consecutive-pair check: each pair must start where the previous ended
    gaps = [(a, b) for a, b in zip(names[:-1], names[1:]) if a[9:] != b[:8]]

    print('anomaly maps for', len(names), 'pairs', flush=True)
    R = [an.anomaly(p['wrapped'], p['coh'], p['mask']) for p in pairs.values()]
    A = [r['a'] for r in R]
    M = [r['measurable'] for r in R]
    res, rows = run_detector(names, A, M, x, y, an.PARAMS)

    # ---- flags
    flags = {}
    for name, r in zip(names, res):
        out = []
        for f in sorted(r['flags'], key=lambda f: -f['pixels']):
            rr, cc = np.nonzero(r['labels'] == f['label'])
            w, s = ll(x[cc.min()] - 10, y[rr.max()] - 10)
            e, n = ll(x[cc.max()] + 10, y[rr.min()] + 10)
            out.append({'lonlat': ll(f['x'], f['y']), 'utm': [round(f['x']), round(f['y'])], 'bbox': [w, s, e, n],
                        'pixels': f['pixels'], 'area_km2': round(f['area_km2'], 4), 'mean_abs_rad': round(f['mean_abs_rad'], 2),
                        'mean_abs_cm': round(f['mean_abs_rad'] * an.RAD_TO_CM, 1), 'continuing': f['continuing'],
                        'at_langtang': at_langtang(f)})
        flags[name] = out
    dump('flags.json', flags)
    dump('evaluation.json', {'params': an.PARAMS, 'rows': rows, 'summary': summary(rows), 'non_consecutive_pairs': gaps,
                             'window_km2': len(x) * len(y) * 400 / 1e6,
                             'note': 'Flags other than Langtang are unverified, not false alarms. Rule calibrated on Langtang (project/results.md).'})

    # ---- sensitivity (one parameter at a time)
    if sens:
        table = []
        for key, values in [('flag_abs_anomaly_rad', [1.0, 2.0]), ('quiet_abs_anomaly_rad', [0.5, 1.0]),
                            ('min_blob_pixels', [20, 80]), ('min_history_measurable', [2]), ('history_pairs', [3, 6])]:
            for v in values:
                p = copy.deepcopy(an.PARAMS)
                p[key] = v
                _, rws = run_detector(names, A, M, x, y, p)
                table.append({'parameter': key, 'value': v, **summary(rws)})
        for v in [51, 125]:
            p = copy.deepcopy(an.PARAMS)
            p['background_box'] = v
            R2 = [an.anomaly(q['wrapped'], q['coh'], q['mask'], p) for q in pairs.values()]
            _, rws = run_detector(names, [r['a'] for r in R2], [r['measurable'] for r in R2], x, y, p)
            table.append({'parameter': 'background_box', 'value': v, **summary(rws)})
        dump('sensitivity.json', {'base': summary(rows), 'variants': table})

    # ---- Langtang series, controls, unwrap, descending
    ts = series.time_series(pairs)
    patch, refs, X, Y = series.regions(pairs)
    resolved = {r['pair']: r['resolved'] for r in ts['rows']}
    ts['unwrap'] = {n: series.unwrap_check(pairs[n], patch, refs['west block'], resolved[n])
                    for n in ('20260702_20260714', '20260714_20260726', '20260726_20260819') if n in pairs}
    csum, clist = series.controls(pairs)
    ts['controls'] = csum
    ts['control_values'] = [[round(c[n], 3) for n in csum['pairs']] for c in clist]
    ts['control_ranks'] = series.control_ranks(pairs, ts)
    ts['descending'] = [{k: v for k, v in r.items() if k != 'raw'} for r in series.descending()]
    ts['collapse_utc'] = COLLAPSE_UTC
    ts['rad_to_cm'] = an.RAD_TO_CM
    dump('series.json', ts)

    # ---- collapse
    cs = collapse.stats()
    dump('collapse.json', cs)

    # ---- outlines
    poly = collapse.polygon()
    feats = [{'type': 'Feature', 'properties': {'name': 'UNOSAT detachment zone (preliminary, not field validated)', 'kind': 'unosat'},
              'geometry': {'type': 'Polygon', 'coordinates': [[ll(a, b) for a, b in poly]]}},
             {'type': 'Feature', 'properties': {'name': 'Measured patch box', 'kind': 'patch'},
              'geometry': {'type': 'Polygon', 'coordinates': [box_ring(series.PATCH)]}},
             {'type': 'Feature', 'properties': {'name': 'Reference block (west)', 'kind': 'reference'},
              'geometry': {'type': 'Polygon', 'coordinates': [box_ring(series.WEST_BLOCK)]}}]
    dump('outlines.geojson', {'type': 'FeatureCollection', 'features': feats})

    # ---- images + manifest
    man = {'generated_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'bounds': render.BOUNDS,
           'collapse_utc': COLLAPSE_UTC, 'track': '098 A 016 (ascending)', 'pairs': [], 'image_bytes': 0,
           'patch_center': ll(series.CENTER[0], series.CENTER[1])}
    for name, p, r, d, row in zip(names, pairs.values(), R, res, rows):
        src = p['source']
        version = src.split('_')[15] if src.startswith('NISAR') else 'unknown'
        entry = {'id': name, 'start': name[:8], 'end': name[9:], 'days': row['days'], 'version': version,
                 'forward_processed': version.startswith('P'), 'has_mask': p['mask'] is not None,
                 'measurable_fraction': round(float(r['measurable'].mean()), 3), 'has_history': row['has_history'],
                 'flags': row['flags'], 'flags_at_langtang': row['flags_at_langtang']}
        if images:
            n = 0
            n += render.anomaly_image(r['a'], r['measurable'], x, y, EPSG, IMG / f'{name}_anom.webp')
            n += render.phase_image(p['wrapped'], p['coh'], r['valid'], x, y, EPSG, IMG / f'{name}_phase.webp')
            n += render.coherence_image(p['coh'], r['valid'], x, y, EPSG, IMG / f'{name}_coh.webp')
            n += render.flag_image(d['labels'], x, y, EPSG, IMG / f'{name}_flag.webp')
            man['image_bytes'] += n
            print(name, f'{n/1e6:.2f} MB', flush=True)
        man['pairs'].append(entry)
    if images:
        maps, gx, gy, gepsg = collapse.change_maps()
        for k, z in maps.items():
            man['image_bytes'] += render.change_image(z, gx, gy, gepsg, IMG / f'collapse_{k}.webp')
    dump('manifest.json', man)
    print('done; images', round(man['image_bytes'] / 1e6, 1), 'MB;', json.dumps(summary(rows)))


if __name__ == '__main__':
    main()
