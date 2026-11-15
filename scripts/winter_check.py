"""Winter steps on the Langtang patch: tests A-D of project/winter_check.md.
Run: C:/Users/HP/anaconda3/python.exe scripts/winter_check.py
Needs data/series (NISAR windows), data/dem/cop_N28_E085.tif (Copernicus GLO-30, AWS open data),
Earthdata ~/.netrc (GUNW metadata cube, HLS Fmask). Writes data/winter/winter_check.json and _table.txt.
"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'pipeline'), str(ROOT / 'scripts')]
import series as se                      # noqa: E402
import anomaly as an                     # noqa: E402
from utm import ll2xy                    # noqa: E402
from nisar_io import open_h5, gunw_url   # noqa: E402
import flag_check as fc                  # noqa: E402

OUT = ROOT / 'data/winter'; OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(0)


def dem_on(X, Y):
    """Copernicus heights at radar pixels: invert UTM with a 3rd-order fit over the window."""
    im = Image.open(ROOT / 'data/dem/cop_N28_E085.tif'); D = np.asarray(im, dtype=np.float32)
    lo0, la0 = im.tag_v2[33922][3], im.tag_v2[33922][4]; d = im.tag_v2[33550][0]
    lo, la = np.meshgrid(np.linspace(85.25, 85.70, 40), np.linspace(28.15, 28.42, 40))
    xy = np.array([ll2xy(a, b, 32645) for a, b in zip(lo.ravel(), la.ravel())])
    def terms(x, y):
        x = (x - 355000) / 1e4; y = (y - 3130000) / 1e4
        return np.stack([x ** i * y ** j for i in range(4) for j in range(4 - i)], -1)
    T = terms(xy[:, 0], xy[:, 1])
    clo = np.linalg.lstsq(T, lo.ravel(), rcond=None)[0]; cla = np.linalg.lstsq(T, la.ravel(), rcond=None)[0]
    err = max(np.abs(T @ clo - lo.ravel()).max(), np.abs(T @ cla - la.ravel()).max()) * 111e3
    TT = terms(X.ravel(), Y.ravel())
    LO = (TT @ clo).reshape(X.shape); LA = (TT @ cla).reshape(X.shape)
    c = np.clip(np.round((LO - lo0) / d - 0.5).astype(int), 0, D.shape[1] - 1)   # pixel-is-area centres
    r = np.clip(np.round((la0 - LA) / d - 0.5).astype(int), 0, D.shape[0] - 1)
    return D[r, c], float(err)


def control_masks(pairs):
    sel = pairs[se.SELECT_PAIR]
    X, Y = np.meshgrid(sel['x'], sel['y'])
    n0 = int((se.box(X, Y, se.PATCH) & (sel['coh'] >= se.PATCH_COH)).sum())
    w, h = se.PATCH[1] - se.PATCH[0], se.PATCH[3] - se.PATCH[2]
    out = []
    for x0 in np.arange(sel['x'].min() + 1500, sel['x'].max() - 1500, 1000):
        for y0 in np.arange(sel['y'].min() + 1500, sel['y'].max() - 1500, 1000):
            if abs(x0 - se.PATCH[0]) < 2000 and abs(y0 - se.PATCH[2]) < 2000:
                continue
            pm = se.box(X, Y, (x0, x0 + w, y0, y0 + h)) & (sel['coh'] >= se.PATCH_COH)
            if pm.sum() < n0:
                continue
            rm = se.box(X, Y, (x0 + se.WEST_BLOCK[0] - se.PATCH[0], x0 + se.WEST_BLOCK[1] - se.PATCH[0],
                               y0 + se.WEST_BLOCK[2] - se.PATCH[2], y0 + se.WEST_BLOCK[3] - se.PATCH[2]))
            out.append((pm, rm))
    return out


def cube_at(h5, pts):
    """Baseline, incidence, range and tropo screens from the metadata cube at (x, y, height) points."""
    R = h5['science/LSAR/GUNW/metadata/radarGrid']
    xs, ys, hs = R['xCoordinates'][:], R['yCoordinates'][:], R['heightAboveEllipsoid'][:]
    names = ['perpendicularBaseline', 'incidenceAngle', 'referenceSlantRange',
             'hydrostaticTroposphericPhaseScreen', 'wetTroposphericPhaseScreen']
    out = []
    for x, y, z in pts:
        i, j = int(np.argmin(np.abs(ys - y))), int(np.argmin(np.abs(xs - x)))
        k = int(np.clip(np.searchsorted(hs, z) - 1, 0, len(hs) - 2)); t = (z - hs[k]) / (hs[k + 1] - hs[k])
        out.append({n: float((1 - t) * R[n][k, i, j] + t * R[n][k + 1, i, j]) for n in names})
    return out


def main():
    pairs = se.load_all()
    ts = se.time_series(pairs)
    rows = [r for r in ts['rows'] if r['resolved'] and r['pair'] != se.SELECT_PAIR]
    patch, refs, X, Y = se.regions(pairs); west = refs['west block']
    H, inv_err = dem_on(X, Y)
    hp, hw = float(np.median(H[patch])), float(np.median(H[west])); dhp = hp - hw
    cms = control_masks(pairs)
    dh_c = np.array([np.median(H[pm]) - np.median(H[rm]) for pm, rm in cms])
    print(f'DEM inverse error {inv_err:.2f} m; patch {hp:.0f} m, west block {hw:.0f} m, difference {dhp:+.0f} m; {len(cms)} control boxes', flush=True)
    cp = (float(X[patch].mean()), float(Y[patch].mean())); cw = (float(X[west].mean()), float(Y[west].mean()))
    res = []
    for r in rows:
        p = pairs[r['pair']]; u, v = se.unit(p)
        obs = r['refs']['west block']['phase_rad']
        ph, dh = [], []
        for (pm, rm), d in zip(cms, dh_c):
            m = se.measure(u, v, pm, rm)
            if m and m['consistency'] >= se.RESOLVED_CONSISTENCY and m['reference_consistency'] >= se.RESOLVED_CONSISTENCY:
                ph.append(m['phase_rad']); dh.append(d)
        ph, dh = np.array(ph), np.array(dh) / 1000.0          # rad, km
        A = np.c_[np.ones_like(dh), dh]
        a, k = np.linalg.lstsq(A, ph, rcond=None)[0]
        boots = []
        for _ in range(2000):
            i = rng.integers(0, len(ph), len(ph))
            boots.append(np.linalg.lstsq(A[i], ph[i], rcond=None)[0][1])
        lo, hi = np.percentile(boots, [2.5, 97.5])
        pred = a + k * dhp / 1000.0
        rc = float(np.corrcoef(dh, ph)[0, 1])
        A_ok = bool((lo > 0 or hi < 0) and abs(obs - pred) < 0.5 * abs(obs))
        src = p['source']
        if src.startswith('NISAR'):
            h5 = open_h5(gunw_url(src)); c1, c2 = cube_at(h5, [(cp[0], cp[1], hp), (cw[0], cw[1], hw)]); h5.close()
            bperp, inc, rng_m = c1['perpendicularBaseline'], c1['incidenceAngle'], c1['referenceSlantRange']
            model = (c1['hydrostaticTroposphericPhaseScreen'] + c1['wetTroposphericPhaseScreen']) - \
                    (c2['hydrostaticTroposphericPhaseScreen'] + c2['wetTroposphericPhaseScreen'])
        else:
            bperp = inc = rng_m = model = None
        D_ok = None if model is None else bool(abs(obs - model) < 0.5 * abs(obs))
        snow = {}
        for nm, b in (('patch', se.PATCH), ('west', se.WEST_BLOCK)):
            for when, dd in (('start', r['start']), ('end', r['end'])):
                t = fc.d8(dd)
                es = fc.cmr(((t - fc.timedelta(fc.DAYS)).isoformat() + 'T00:00:00Z', (t + fc.timedelta(fc.DAYS)).isoformat() + 'T23:59:59Z'))
                sc = [x for x in (fc.fmask(e) for e in es) if x]
                bb = fc.best(sc, b)
                snow[f'{nm}_{when}'] = None if bb is None else round(bb['snow'], 2)
        ch = [abs(snow[f'{n}_end'] - snow[f'{n}_start']) for n in ('patch', 'west')
              if snow[f'{n}_end'] is not None and snow[f'{n}_start'] is not None]
        res.append({'pair': r['pair'], 'winter': r['end'] < '20260401', 'obs_rad': obs, 'obs_cm': obs * an.RAD_TO_CM,
                    'n_controls': int(len(ph)), 'k_rad_per_km': float(k), 'k_ci': [float(lo), float(hi)], 'a_rad': float(a),
                    'r_height': rc, 'pred_height_rad': float(pred), 'A_explains': A_ok,
                    'bperp_m': bperp, 'incidence_deg': inc, 'slant_range_m': rng_m,
                    'model_rad': model, 'D_explains': D_ok, 'snow': snow,
                    'snow_change': (max(ch) >= 0.3) if ch else None})
        print(json.dumps(res[-1]), flush=True)
    # test B: patch step vs perpendicular baseline (ten readable pairs)
    B = [(x['bperp_m'], x['obs_rad'], x['incidence_deg'], x['slant_range_m']) for x in res if x['bperp_m'] is not None]
    b, o = np.array([q[0] for q in B]), np.array([q[1] for q in B])
    m, c = np.polyfit(b, o, 1); rB = float(np.corrcoef(b, o)[0, 1])
    perm = np.array([abs(np.corrcoef(rng.permutation(b), o)[0, 1]) for _ in range(10000)])
    pB = float((perm >= abs(rB)).mean())
    resid = o - (c + m * b)
    rms_o, rms_r = float(np.sqrt(np.mean((o - o.mean()) ** 2))), float(np.sqrt(np.mean(resid ** 2)))
    inc = np.radians(np.mean([q[2] for q in B])); R0 = float(np.mean([q[3] for q in B]))
    lam = an.WAVELENGTH_CM / 100
    dz = float(m * lam * R0 * np.sin(inc) / (4 * np.pi))     # phase = 4 pi Bperp dZ / (lam R sin inc)
    testB = {'n': len(B), 'slope_rad_per_m': float(m), 'r': rB, 'p_perm': pB, 'rms_steps_rad': rms_o, 'rms_resid_rad': rms_r,
             'implied_height_error_m': dz, 'consistent': bool(pB < 0.05 and rms_r < 0.5 * rms_o)}
    win = [x for x in res if x['winter']]
    nA = sum(x['A_explains'] for x in win); nD = sum(bool(x['D_explains']) for x in win)
    verdict = lambda n: 'yes' if n >= 5 else 'partly' if n >= 2 else 'no'
    out = {'dem_inverse_error_m': inv_err, 'patch_height_m': hp, 'west_height_m': hw, 'n_control_boxes': len(cms),
           'pairs': res, 'testA': {'explains_in': nA, 'of': len(win), 'verdict': verdict(nA)},
           'testB': testB, 'testD': {'explains_in': nD, 'of': len(win), 'verdict': verdict(nD)}}
    (OUT / 'winter_check.json').write_text(json.dumps(out, indent=1))
    L = [f"patch {hp:.0f} m, west block {hw:.0f} m (difference {dhp:+.0f} m), DEM grid error {inv_err:.1f} m", '',
         'pair               obs cm  ctrl  k rad/km [95%]        r     pred(A) cm  A   Bperp m  model(D) cm  D   snow p s>e   w s>e   change']
    for x in res:
        sn = x['snow']; f = lambda v: '  -' if v is None else f'{v:.1f}'
        L.append(f"{x['pair']}  {x['obs_cm']:+6.2f}  {x['n_controls']:4d}  {x['k_rad_per_km']:+6.2f} [{x['k_ci'][0]:+.2f},{x['k_ci'][1]:+.2f}]  {x['r_height']:+.2f}  "
                 f"{x['pred_height_rad'] * an.RAD_TO_CM:+6.2f}  {'Y' if x['A_explains'] else 'n'}  "
                 f"{'' if x['bperp_m'] is None else format(x['bperp_m'], '+8.1f')}  "
                 f"{'' if x['model_rad'] is None else format(x['model_rad'] * an.RAD_TO_CM, '+6.2f')}  {'Y' if x['D_explains'] else 'n'}  "
                 f"{f(sn['patch_start'])}>{f(sn['patch_end'])}  {f(sn['west_start'])}>{f(sn['west_end'])}  {x['snow_change']}")
    L += ['', f"Test A (height-linked air delay): explains {nA} of {len(win)} winter pairs -> {verdict(nA)}",
          f"Test B (height-model error): r = {rB:+.2f}, permutation p = {pB:.3f}, residual RMS {rms_r:.2f} vs {rms_o:.2f} rad, implied height error {dz:+.1f} m -> {'consistent' if testB['consistent'] else 'not explained'}",
          f"Test D (weather model): explains {nD} of {len(win)} winter pairs -> {verdict(nD)}"]
    (OUT / 'winter_check_table.txt').write_text('\n'.join(L))
    print('\n'.join(L))


if __name__ == '__main__':
    main()
