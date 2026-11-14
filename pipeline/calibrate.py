"""Calibration of the detector on the pairs 8 Jun - 31 Aug 2026 only (plan step 3b).

Usage:  python pipeline/calibrate.py [old|series]
  old    : six extracts in data/lang (no mask; only three pairs of history before 14-26 Jul)
  series : data/series files with start dates 20260503..20260819 (mask, four pairs of history)
Prints a report; nothing is frozen by this script.
"""
import sys
import json
import copy
from pathlib import Path
import numpy as np
import anomaly as an
import detect as dt

ROOT = Path(__file__).resolve().parents[1]
PATCH = (355250, 355800, 3129780, 3130250)       # xmin, xmax, ymin, ymax (UTM 45N), from the verification record


def load(mode):
    if mode == 'old':
        files = sorted((ROOT / 'data/lang').glob('GUNW_098_A_016_*.npz'))
        return [(f.stem[-17:], an.load_old_pair(f)) for f in files]
    files = sorted(f for f in (ROOT / 'data/series').glob('098_A_016_*.npz') if '20260503' <= f.stem.split('_')[3] <= '20260819')
    return [(f.stem[-17:], an.load_series_pair(f)) for f in files]


def run(pairs, params, verbose=True):
    x, y = pairs[0][1]['x'], pairs[0][1]['y']
    X, Y = np.meshgrid(x, y)
    box = (X >= PATCH[0]) & (X <= PATCH[1]) & (Y >= PATCH[2]) & (Y <= PATCH[3])
    A, M = [], []
    rows = []
    for name, p in pairs:
        assert np.array_equal(p['x'], x) and np.array_equal(p['y'], y)
        r = an.anomaly(p['wrapped'], p['coh'], p['mask'], params)
        A.append(r['a'])
        M.append(r['measurable'])
        m = box & r['measurable']
        absa = np.abs(r['a'][m])
        rows.append({'pair': name, 'window_measurable_frac': float(r['measurable'].mean()),
                     'patch_box_measurable': int(m.sum()), 'patch_box_pixels': int(box.sum()),
                     'patch_median_abs_a': float(np.median(absa)) if absa.size else None,
                     'patch_px_abs_ge_flag': int((absa >= params['flag_abs_anomaly_rad']).sum()),
                     'patch_px_abs_lt_quiet': int((absa < params['quiet_abs_anomaly_rad']).sum())})
    res = dt.detect(A, M, x, y, params)
    for row, r in zip(rows, res):
        fl = r['flags']
        near = [f for f in fl if PATCH[0] - 300 <= f['x'] <= PATCH[1] + 300 and PATCH[2] - 300 <= f['y'] <= PATCH[3] + 300]
        row.update(has_history=r['has_history'], eligible_px=r['eligible_pixels'], flags=len(fl),
                   flags_at_patch=[(f['pixels'], round(f['mean_abs_rad'], 2)) for f in near],
                   patch_box_flagged_px=int(((r['labels'] > 0) & box).sum()),
                   patch_box_eligible_px=None,
                   rank_by_pixels=(sorted([f['pixels'] for f in fl], reverse=True).index(max(f['pixels'] for f in near)) + 1) if near else None)
    if verbose:
        for row in rows:
            print(json.dumps(row))
    return rows, res


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'old'
    pairs = load(mode)
    base = copy.deepcopy(an.PARAMS)
    if mode == 'old':
        base['history_pairs'] = 3
        print('NOTE old mode: history_pairs=3 because only three pairs precede 14-26 Jul')
    print('== base parameters ==')
    run(pairs, base)
    for key, values in [('background_box', [51, 125]), ('flag_abs_anomaly_rad', [1.0, 2.0]),
                        ('quiet_abs_anomaly_rad', [0.5, 1.0]), ('min_blob_pixels', [20, 80]),
                        ('min_background_strength', [0.1, 0.5]), ('min_consistency', [0.5, 0.7])]:
        for v in values:
            p = copy.deepcopy(base)
            p[key] = v
            rows, _ = run(pairs, p, verbose=False)
            print(f'-- {key}={v}: ' + ' | '.join(
                f"{r['pair'][4:8]}: flags {r['flags']}, at patch {r['flags_at_patch']}" for r in rows if r['has_history']))
