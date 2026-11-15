"""Independent test of the frozen rule at Budhi Gandaki (project/independent_test.md).
Run after scripts/indep_fetch.py:  C:/Users/HP/anaconda3/python.exe scripts/indep_run.py
Writes data/indep_bg/indep_result.json and data/indep_bg/indep_result.txt.
"""
import json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'pipeline'), str(ROOT / 'scripts')]
import anomaly as an   # noqa: E402
import detect as dt    # noqa: E402
from utm import ll2xy  # noqa: E402

D = ROOT / 'data/indep_bg'
TRACKS = ['098_A_016', '149_D_074', '048_D_074']
SCAR = (84.9345, 28.5336); RADIUS = 600.0
CUTOFF = '20261010T2215'                     # flood at Chumchet, 04:00 NPT 11 Oct = 22:15 UTC 10 Oct
END_TIME = {'098_A_016': 'T2339', '149_D_074': 'T1306', '048_D_074': 'T1258'}   # pass time (UTC) from the catalogue


def run(track):
    files = sorted(D.glob(f'{track}_*.npz'))
    names = [f.stem[-17:] for f in files]
    P = [an.load_series_pair(f) for f in files]
    x, y, epsg = P[0]['x'], P[0]['y'], P[0]['epsg']
    for p in P:
        assert np.array_equal(p['x'], x) and np.array_equal(p['y'], y) and p['epsg'] == epsg, 'grid mismatch'
    spacing = float(abs(x[1] - x[0])), float(abs(y[1] - y[0]))
    gaps = [(a, b) for a, b in zip(names[:-1], names[1:]) if a[9:] != b[:8]]
    out = {'track': track, 'pairs': len(names), 'spacing_m': spacing, 'gaps': gaps,
           'granules': [json.loads(f.with_suffix('.json').read_text())['granule'] for f in files]}
    if spacing != (20.0, 20.0):
        out['outcome'] = 'NOT TESTED (grid spacing is not 20 m)'
        return out
    sx, sy = ll2xy(SCAR[0], SCAR[1], epsg)
    X, Y = np.meshgrid(x, y)
    zone = np.hypot(X - sx, Y - sy) <= RADIUS
    R = [an.anomaly(p['wrapped'], p['coh'], p['mask']) for p in P]
    A, M = [r['a'] for r in R], [r['measurable'] for r in R]
    res = dt.detect(A, M, x, y)
    rows = []
    for k, (name, r) in enumerate(zip(names, res)):
        fl, el = dt.flag_pixels(A, M, k)
        lab = r['labels']
        hit_labels = set(np.unique(lab[zone & (lab > 0)]).tolist())
        zf = [f for f in r['flags'] if f['label'] in hit_labels]
        ends = name[9:] + END_TIME[track]
        rows.append({'pair': name, 'has_history': r['has_history'], 'flags': len(r['flags']),
                     'flags_in_zone': len(zf), 'zone_flags': [{k2: f[k2] for k2 in ('pixels', 'mean_abs_rad', 'x', 'y')} for f in zf],
                     'zone_pixels': int(zone.sum()), 'zone_valid': int((zone & R[k]['valid']).sum()),
                     'zone_measurable': int((zone & M[k]).sum()), 'zone_eligible': int((zone & el).sum()),
                     'zone_median_coh': float(np.median(P[k]['coh'][zone])),
                     'measurable_km2': r['measurable_pixels'] * 400 / 1e6, 'eligible_km2': r['eligible_pixels'] * 400 / 1e6,
                     'pre_event': ends < CUTOFF})
    # rule 5: a pre-event pair whose zone coherence has collapsed may already contain the failure
    for i, row in enumerate(rows):
        prev = [q['zone_median_coh'] for q in rows[max(0, i - 4):i]]
        row['coherence_collapsed'] = bool(prev and row['zone_median_coh'] < 0.5 * np.median(prev))
        row['counted'] = bool(row['pre_event'] and not row['coherence_collapsed'] and row['has_history'])
    cnt = [q for q in rows if q['counted']]
    if any(q['flags_in_zone'] for q in cnt):
        oc = 'HIT'
    elif any(q['zone_eligible'] for q in cnt):
        oc = 'MISS'
    else:
        oc = 'NOT TESTABLE'
    h = [q for q in rows if q['has_history']]
    out.update(rows=rows, outcome=oc, flags_total=sum(q['flags'] for q in h), pairs_with_history=len(h),
               median_flags=float(np.median([q['flags'] for q in h])) if h else None,
               event_pairs=[q['pair'] for q in rows if not q['pre_event']][:1],
               zone_flag_pairs=[q['pair'] for q in rows if q['flags_in_zone']])
    return out


def main():
    out = {t: run(t) for t in TRACKS if list(D.glob(f'{t}_*.npz'))}
    oc = [o['outcome'] for o in out.values()]
    overall = 'HIT' if 'HIT' in oc else 'MISS' if 'MISS' in oc else 'NOT TESTABLE'
    (D / 'indep_result.json').write_text(json.dumps({'overall': overall, 'tracks': out}, indent=1))
    L = []
    for t, o in out.items():
        L.append(f"== {t}: {o['pairs']} pairs, spacing {o['spacing_m']}, gaps {o['gaps']}, outcome {o['outcome']}")
        if 'rows' not in o:
            continue
        L.append(f"   flags in pairs with history: {o['flags_total']} over {o['pairs_with_history']} pairs (median {o['median_flags']})")
        L.append('   pair               hist  flags  zone: valid meas elig flags  coh   pre-event coh-collapse counted')
        for q in o['rows']:
            L.append(f"   {q['pair']}  {'y' if q['has_history'] else '-'}  {q['flags']:5d}  {q['zone_valid']:10d} {q['zone_measurable']:4d} {q['zone_eligible']:4d} {q['flags_in_zone']:5d}  {q['zone_median_coh']:.2f}  {str(q['pre_event']):5s}     {str(q['coherence_collapsed']):5s}        {q['counted']}")
    L.append(f'OVERALL: {overall}')
    (D / 'indep_result.txt').write_text('\n'.join(L))
    print('\n'.join(L))


if __name__ == '__main__':
    main()
