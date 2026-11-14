"""Fixed patch / reference time series for the Langtang slope (spec 4.4)."""
import heapq
import json
from datetime import datetime
from pathlib import Path
import numpy as np
import anomaly as an

ROOT = Path(__file__).resolve().parents[1]
PATCH = (355250, 355800, 3129780, 3130250)          # xmin, xmax, ymin, ymax, UTM 45N
PATCH_COH = 0.45                                    # applied on the 14-26 Jul pair only
SELECT_PAIR = '20260714_20260726'
WEST_BLOCK = (354650, 354980, 3129900, 3130500)
RING = (700, 2500, 0.7)                             # inner m, outer m, coherence in both Jul pairs
RING_PAIRS = ('20260702_20260714', '20260714_20260726')
CENTER = (355500, 3130000)
RESOLVED_CONSISTENCY = 0.6


def days(name):
    a, b = name.split('_')
    return (datetime.strptime(b, '%Y%m%d') - datetime.strptime(a, '%Y%m%d')).days


def load_all(track='098_A_016'):
    """All pairs of a track from data/series; falls back to old extracts for ascending pairs not yet fetched."""
    out = {}
    for f in sorted((ROOT / 'data/series').glob(f'{track}_*.npz')):
        p = an.load_series_pair(f)
        p['source'] = json.loads(f.with_suffix('.json').read_text())['granule'] if f.with_suffix('.json').exists() else f.name
        out[f.stem[-17:]] = p
    if track == '098_A_016':
        for f in sorted((ROOT / 'data/lang').glob('GUNW_098_A_016_*.npz')):
            if f.stem[-17:] not in out:
                p = an.load_old_pair(f)
                p['source'] = 'old extract ' + f.name + ' (version not recorded, no mask)'
                out[f.stem[-17:]] = p
    return dict(sorted(out.items()))


def unit(p):
    v = an.valid_pixels(p['wrapped'], p['coh'], p['mask'])
    u = np.zeros(p['wrapped'].shape, complex)
    u[v] = p['wrapped'][v] / np.abs(p['wrapped'][v])
    return u, v


def box(X, Y, b):
    return (X >= b[0]) & (X <= b[1]) & (Y >= b[2]) & (Y <= b[3])


def regions(pairs):
    sel = pairs[SELECT_PAIR]
    X, Y = np.meshgrid(sel['x'], sel['y'])
    patch = box(X, Y, PATCH) & (sel['coh'] >= PATCH_COH)
    r = np.hypot(X - CENTER[0], Y - CENTER[1])
    both = np.ones(X.shape, bool)
    for n in RING_PAIRS:
        both &= pairs[n]['coh'] >= RING[2]
    ring = (r >= RING[0]) & (r <= RING[1]) & both
    dx, dy = X - CENTER[0], Y - CENTER[1]
    refs = {'west block': box(X, Y, WEST_BLOCK),
            'ring north': ring & (dy > 0) & (np.abs(dx) < np.abs(dy)),
            'ring south': ring & (dy < 0) & (np.abs(dx) < np.abs(dy)),
            'ring east': ring & (dx > 0) & (np.abs(dx) >= np.abs(dy)),
            'ring west': ring & (dx < 0) & (np.abs(dx) >= np.abs(dy))}
    return patch, refs, X, Y


def measure(u, v, patch, ref):
    pm, rm = patch & v, ref & v
    if pm.sum() < 20 or rm.sum() < 20:
        return None
    r = u[rm].mean()
    m = (u[pm] * np.conj(r) / max(abs(r), 1e-9)).mean()
    return {'phase_rad': float(np.angle(m)), 'consistency': float(abs(m)), 'reference_consistency': float(abs(r)),
            'los_cm': float(np.angle(m) * an.RAD_TO_CM), 'patch_n': int(pm.sum()), 'ref_n': int(rm.sum())}


def time_series(pairs):
    patch, refs, X, Y = regions(pairs)
    rows = []
    for name, p in pairs.items():
        u, v = unit(p)
        row = {'pair': name, 'start': name[:8], 'end': name[9:], 'days': days(name), 'source': p['source'],
               'patch_median_coherence': float(np.median(p['coh'][patch])), 'refs': {}}
        for rn, rm in refs.items():
            row['refs'][rn] = measure(u, v, patch, rm)
        w = row['refs']['west block']
        row['resolved'] = bool(w and w['consistency'] >= RESOLVED_CONSISTENCY and w['reference_consistency'] >= RESOLVED_CONSISTENCY)
        rows.append(row)
    return {'patch_pixels': int(patch.sum()), 'patch_area_km2': float(patch.sum() * 400 / 1e6), 'patch_box_utm': PATCH,
            'selection': f'pixels in box with 20 m coherence >= {PATCH_COH} in pair {SELECT_PAIR}',
            'reference_pixels': {k: int(v.sum()) for k, v in refs.items()},
            'resolved_rule': f'patch and west-block consistency >= {RESOLVED_CONSISTENCY}', 'rows': rows}


def controls(pairs, names=RING_PAIRS):
    """Negative controls: the same measurement on other coherent slopes in the window.
    A control is a box of the patch size on a 1 km grid with >= patch_pixels coherent pixels (same rule,
    same selection pair) and a reference block of the west-block size at the same offset to the west."""
    sel = pairs[SELECT_PAIR]
    X, Y = np.meshgrid(sel['x'], sel['y'])
    patch0 = box(X, Y, PATCH) & (sel['coh'] >= PATCH_COH)
    n0 = int(patch0.sum())
    us = {n: unit(pairs[n]) for n in names}
    out = []
    w, h = PATCH[1] - PATCH[0], PATCH[3] - PATCH[2]
    for x0 in np.arange(sel['x'].min() + 1500, sel['x'].max() - 1500, 1000):
        for y0 in np.arange(sel['y'].min() + 1500, sel['y'].max() - 1500, 1000):
            if abs(x0 - PATCH[0]) < 2000 and abs(y0 - PATCH[2]) < 2000:
                continue
            pb = (x0, x0 + w, y0, y0 + h)
            pm = box(X, Y, pb) & (sel['coh'] >= PATCH_COH)
            if pm.sum() < n0:
                continue
            rb = (x0 + WEST_BLOCK[0] - PATCH[0], x0 + WEST_BLOCK[1] - PATCH[0], y0 + WEST_BLOCK[2] - PATCH[2], y0 + WEST_BLOCK[3] - PATCH[2])
            rm = box(X, Y, rb)
            row = {'x': float(x0), 'y': float(y0)}
            ok = True
            for n in names:
                m = measure(us[n][0], us[n][1], pm, rm)
                if not m or m['consistency'] < RESOLVED_CONSISTENCY or m['reference_consistency'] < RESOLVED_CONSISTENCY:
                    ok = False
                    break
                row[n] = m['phase_rad']
            if ok:
                out.append(row)
    a = np.array([[abs(r[n]) for n in names] for r in out]) if out else np.zeros((0, len(names)))
    summary = {'n_controls': len(out), 'pairs': list(names)}
    if len(out):
        summary.update(abs_phase_median=[float(v) for v in np.median(a, axis=0)],
                       abs_phase_p95=[float(v) for v in np.percentile(a, 95, axis=0)],
                       abs_phase_max=[float(v) for v in a.max(axis=0)],
                       n_with_step_like_langtang=int(((a[:, 0] < 0.75) & (a[:, 1] >= 1.5)).sum()))
    return summary, out


def control_ranks(pairs, ts):
    """For every pair in which the Langtang patch is resolved: the same measurement on all control boxes
    (same construction as controls()) that are resolved in that pair, and where Langtang sits among them."""
    sel = pairs[SELECT_PAIR]
    X, Y = np.meshgrid(sel['x'], sel['y'])
    n0 = int((box(X, Y, PATCH) & (sel['coh'] >= PATCH_COH)).sum())
    w, h = PATCH[1] - PATCH[0], PATCH[3] - PATCH[2]
    masks = []
    for x0 in np.arange(sel['x'].min() + 1500, sel['x'].max() - 1500, 1000):
        for y0 in np.arange(sel['y'].min() + 1500, sel['y'].max() - 1500, 1000):
            if abs(x0 - PATCH[0]) < 2000 and abs(y0 - PATCH[2]) < 2000:
                continue
            pm = box(X, Y, (x0, x0 + w, y0, y0 + h)) & (sel['coh'] >= PATCH_COH)
            if pm.sum() < n0:
                continue
            rm = box(X, Y, (x0 + WEST_BLOCK[0] - PATCH[0], x0 + WEST_BLOCK[1] - PATCH[0],
                            y0 + WEST_BLOCK[2] - PATCH[2], y0 + WEST_BLOCK[3] - PATCH[2]))
            ys, xs = np.nonzero(pm | rm)
            sl = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
            masks.append((sl, pm[sl], rm[sl]))
    out = {}
    for row in ts['rows']:
        if not row['resolved']:
            continue
        u, v = unit(pairs[row['pair']])
        vals = []
        for sl, pm, rm in masks:
            m = measure(u[sl], v[sl], pm, rm)
            if m and m['consistency'] >= RESOLVED_CONSISTENCY and m['reference_consistency'] >= RESOLVED_CONSISTENCY:
                vals.append(abs(m['phase_rad']))
        lang = abs(row['refs']['west block']['phase_rad'])
        vals = np.array(vals)
        out[row['pair']] = {'n_controls': int(vals.size), 'langtang_abs_rad': float(lang),
                            'control_median': float(np.median(vals)) if vals.size else None,
                            'control_p95': float(np.percentile(vals, 95)) if vals.size else None,
                            'control_max': float(vals.max()) if vals.size else None,
                            'controls_at_or_above_langtang': int((vals >= lang).sum()),
                            'langtang_percentile': float(100 * (vals < lang).mean()) if vals.size else None}
    return out


def _unwrap_from(phase, quality, seed, region):
    """Quality-guided path-following unwrap inside region, starting at seed (row, col)."""
    out = np.full(phase.shape, np.nan)
    out[seed] = phase[seed]
    heap = [(-quality[seed], seed)]
    done = np.zeros(phase.shape, bool)
    done[seed] = True
    while heap:
        _, (r, c) = heapq.heappop(heap)
        for rr, cc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= rr < phase.shape[0] and 0 <= cc < phase.shape[1] and region[rr, cc] and not done[rr, cc]:
                d = phase[rr, cc] - phase[r, c]
                out[rr, cc] = out[r, c] + (d + np.pi) % (2 * np.pi) - np.pi
                done[rr, cc] = True
                heapq.heappush(heap, (-quality[rr, cc], (rr, cc)))
    return out


def unwrap_check(p, patch, ref, resolved):
    """Attempt to unwrap the pair between the reference block and the patch along two differently seeded
    quality-guided paths, on 60 m-smoothed phase. Returns agreement information; a number is reported
    only if both agree within a quarter cycle AND the pair is resolved by the consistency rule
    (spec 4.4, tightened: path-following cannot detect aliasing across an incoherent patch edge, and
    two thresholds are not independent paths)."""
    from scipy.ndimage import uniform_filter
    u, v = unit(p)
    c = np.where(v, p['coh'], 0.0)
    s = uniform_filter((c * u).real, 3) + 1j * uniform_filter((c * u).imag, 3)
    q = np.abs(s) / np.maximum(uniform_filter(c, 3), 1e-9)
    ph = np.angle(s)
    rows = np.flatnonzero((patch | ref).any(axis=1))
    cols = np.flatnonzero((patch | ref).any(axis=0))
    sl = (slice(rows[0] - 10, rows[-1] + 11), slice(cols[0] - 10, cols[-1] + 11))
    ph, q, pm, rm = ph[sl], q[sl], patch[sl], ref[sl]
    results = []
    for thr in (0.35, 0.5):
        region = q >= thr
        rr, cc = np.nonzero(rm & region)
        if not rr.size:
            results.append(None)
            continue
        k = np.argmax(q[rr, cc])
        un = _unwrap_from(ph, q, (int(rr[k]), int(cc[k])), region)
        got = pm & np.isfinite(un)
        if got.sum() < 0.3 * pm.sum():
            results.append(None)
            continue
        results.append({'quality_threshold': thr, 'patch_pixels_reached': int(got.sum()),
                        'patch_minus_ref_rad_median': float(np.nanmedian(un[got]) - np.nanmedian(un[rm & np.isfinite(un)])),
                        'patch_p10_p90_rad': [float(v) for v in np.nanpercentile(un[got] - np.nanmedian(un[rm & np.isfinite(un)]), [10, 90])]})
    ok = resolved and all(results) and abs(results[0]['patch_minus_ref_rad_median'] - results[1]['patch_minus_ref_rad_median']) < np.pi / 2
    return {'attempts': results, 'pair_resolved_by_consistency': bool(resolved), 'number_reported': bool(ok),
            'reported': ({'rad': results[0]['patch_minus_ref_rad_median'], 'los_cm': results[0]['patch_minus_ref_rad_median'] * an.RAD_TO_CM}
                         if ok else 'spatially mixed phase, magnitude unresolved')}


def descending():
    pairs = load_all('048_D_074')
    out = []
    for name, p in pairs.items():
        X, Y = np.meshgrid(p['x'], p['y'])
        u, v = unit(p)
        pb, rb = box(X, Y, PATCH), box(X, Y, WEST_BLOCK)
        pm = pb & v & (p['coh'] >= PATCH_COH)
        row = {'pair': name, 'days': days(name), 'box_pixels': int(pb.sum()), 'box_valid': int((pb & v).sum()),
               'box_coherent': int(pm.sum()), 'box_median_coherence': float(np.median(p['coh'][pb])) if pb.any() else None,
               'ref_valid': int((rb & v).sum())}
        m = measure(u, v, pm, rb)
        row['measurement'] = m if (m and m['consistency'] >= RESOLVED_CONSISTENCY and m['reference_consistency'] >= RESOLVED_CONSISTENCY) else None
        row['raw'] = m
        out.append(row)
    return out


if __name__ == '__main__':
    pairs = load_all()
    ts = time_series(pairs)
    print('patch px', ts['patch_pixels'], ts['reference_pixels'])
    for r in ts['rows']:
        w = r['refs']['west block']
        print(r['pair'], r['days'], 'coh %.2f' % r['patch_median_coherence'], 'resolved' if r['resolved'] else 'unresolved',
              ' | '.join(f"{k.split()[-1]} {v['los_cm']:+.1f}cm c{v['consistency']:.2f}" if v else f"{k.split()[-1]} -" for k, v in r['refs'].items()))
    patch, refs, X, Y = regions(pairs)
    for n in ('20260702_20260714', '20260714_20260726', '20260726_20260819'):
        res = {r['pair']: r['resolved'] for r in ts['rows']}[n]
        print('unwrap', n, json.dumps(unwrap_check(pairs[n], patch, refs['west block'], res)))
    s, _ = controls(pairs)
    print('controls', json.dumps(s))
    for r in descending():
        print('desc', json.dumps({k: r[k] for k in r if k != 'raw'}))
