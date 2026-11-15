"""Post-hoc (added after seeing the HIT, project/independent_test.md): how often does a zone of the same size,
placed at random on the same window, collect at least one flag in the same pre-event pairs by chance?
Track 098 A only. Zones are placed on ground that was eligible in at least one counted pair, at least 2 km from the scar.
Run: C:/Users/HP/anaconda3/python.exe scripts/indep_chance.py
"""
import json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'pipeline'), str(ROOT / 'scripts')]
import anomaly as an   # noqa: E402
import detect as dt    # noqa: E402
from utm import ll2xy  # noqa: E402
import indep_run as ir  # noqa: E402

files = sorted(ir.D.glob('098_A_016_*.npz'))
P = [an.load_series_pair(f) for f in files]; names = [f.stem[-17:] for f in files]
x, y, epsg = P[0]['x'], P[0]['y'], P[0]['epsg']
R = [an.anomaly(p['wrapped'], p['coh'], p['mask']) for p in P]
A, M = [r['a'] for r in R], [r['measurable'] for r in R]
res = dt.detect(A, M, x, y)
counted = [k for k, n in enumerate(names) if res[k]['has_history'] and n[9:] + 'T2339' < ir.CUTOFF]
flagged_any = np.zeros(A[0].shape, bool); elig_any = np.zeros(A[0].shape, bool)
last4 = counted[-4:]; flagged_last4 = np.zeros(A[0].shape, bool)
for k in counted:
    fl, el = dt.flag_pixels(A, M, k)
    lab = res[k]['labels'] > 0
    flagged_any |= lab; elig_any |= el
    if k in last4:
        flagged_last4 |= lab
X, Y = np.meshgrid(x, y)
sx, sy = ll2xy(ir.SCAR[0], ir.SCAR[1], epsg)
rng = np.random.default_rng(0)
cand = np.flatnonzero(elig_any.ravel() & (np.hypot(X - sx, Y - sy).ravel() > 2000))
hits = hits4 = 0; N = 2000
step = 4   # evaluate the zone on a 4-pixel lattice for speed (80 m)
for c in rng.choice(cand, N, replace=False):
    cx, cy = X.ravel()[c], Y.ravel()[c]
    j0, j1 = np.searchsorted(x, cx - 620), np.searchsorted(x, cx + 620)
    i = np.argsort(y); ys = y[i]
    rows = i[np.searchsorted(ys, cy - 620):np.searchsorted(ys, cy + 620)]
    sub = np.hypot(X[np.ix_(rows, range(j0, j1))] - cx, Y[np.ix_(rows, range(j0, j1))] - cy) <= ir.RADIUS
    hits += bool((flagged_any[np.ix_(rows, range(j0, j1))] & sub).any())
    hits4 += bool((flagged_last4[np.ix_(rows, range(j0, j1))] & sub).any())
out = {'track': '098_A_016', 'counted_pairs': len(counted), 'random_zones': N,
       'share_with_flag_in_any_counted_pair': hits / N, 'share_with_flag_in_last_4_pre_event_pairs': hits4 / N,
       'last4': [names[k] for k in last4]}
(ir.D / 'indep_chance.json').write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
z = json.loads((ir.D / 'indep_result.json').read_text())['tracks']['098_A_016']
print([q for q in z['rows'] if q['flags_in_zone']])
