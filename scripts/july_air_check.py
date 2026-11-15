"""Post-hoc check (added after the winter results, project/winter_check.md): how much of the
14-26 Jul step could height-linked air delay explain? Same tests A and D as scripts/winter_check.py,
on the 14-26 Jul pair. Also: height difference of the controls vs the patch (do the controls cover 775 m?).
Run: C:/Users/HP/anaconda3/python.exe scripts/july_air_check.py
"""
import json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'pipeline'), str(ROOT / 'scripts')]
import series as se                    # noqa: E402
import anomaly as an                   # noqa: E402
import winter_check as wc              # noqa: E402
from nisar_io import open_h5, gunw_url  # noqa: E402

pairs = se.load_all()
ts = se.time_series(pairs)
patch, refs, X, Y = se.regions(pairs); west = refs['west block']
H, _ = wc.dem_on(X, Y)
hp, hw = float(np.median(H[patch])), float(np.median(H[west])); dhp = hp - hw
cms = wc.control_masks(pairs)
dh_c = np.array([np.median(H[pm]) - np.median(H[rm]) for pm, rm in cms])
cp = (float(X[patch].mean()), float(Y[patch].mean())); cw = (float(X[west].mean()), float(Y[west].mean()))
out = {'patch_minus_west_m': dhp, 'controls_dh_m': {'p5': float(np.percentile(dh_c, 5)), 'median': float(np.median(dh_c)),
       'p95': float(np.percentile(dh_c, 95)), 'n_ge_patch': int((np.abs(dh_c) >= abs(dhp)).sum()), 'n': int(len(dh_c))}}
rng = np.random.default_rng(0)
for name in ('20260702_20260714', '20260714_20260726'):
    r = next(q for q in ts['rows'] if q['pair'] == name)
    p = pairs[name]; u, v = se.unit(p)
    obs = r['refs']['west block']['phase_rad']
    ph, dh = [], []
    for (pm, rm), d in zip(cms, dh_c):
        m = se.measure(u, v, pm, rm)
        if m and m['consistency'] >= 0.6 and m['reference_consistency'] >= 0.6:
            ph.append(m['phase_rad']); dh.append(d / 1000)
    ph, dh = np.array(ph), np.array(dh)
    A = np.c_[np.ones_like(dh), dh]; a, k = np.linalg.lstsq(A, ph, rcond=None)[0]
    bs = [np.linalg.lstsq(A[i], ph[i], rcond=None)[0][1] for i in (rng.integers(0, len(ph), len(ph)) for _ in range(2000))]
    h5 = open_h5(gunw_url(p['source'])); c1, c2 = wc.cube_at(h5, [(cp[0], cp[1], hp), (cw[0], cw[1], hw)]); h5.close()
    model = (c1['hydrostaticTroposphericPhaseScreen'] + c1['wetTroposphericPhaseScreen']) - (c2['hydrostaticTroposphericPhaseScreen'] + c2['wetTroposphericPhaseScreen'])
    predA = a + k * dhp / 1000
    # controls with a large height difference: is any of them as far out as the patch after the fit?
    big = np.abs(dh) * 1000 >= 500
    out[name] = {'obs_rad': obs, 'obs_cm': obs * an.RAD_TO_CM, 'n_controls': int(len(ph)), 'k_rad_per_km': float(k),
                 'k_ci': [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                 'predA_rad': float(predA), 'predA_cm': float(predA * an.RAD_TO_CM),
                 'model_D_rad': float(model), 'model_D_cm': float(model * an.RAD_TO_CM),
                 'after_A_cm': float((obs - predA) * an.RAD_TO_CM), 'after_D_cm': float((obs - model) * an.RAD_TO_CM),
                 'controls_with_dh_ge_500m': int(big.sum()),
                 'their_abs_phase_max_rad': float(np.abs(ph[big]).max()) if big.any() else None}
(ROOT / 'data/winter/july_air_check.json').write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
