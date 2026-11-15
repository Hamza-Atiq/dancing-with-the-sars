"""26 Jul - 19 Aug at 5 m from NISAR GSLC: phase at finer pixels and offset tracking (project/gap_check.md).
Run: C:/Users/HP/anaconda3/python.exe scripts/gap_check.py
Reads a 6 x 6 km crop of five GSLC files remotely (Earthdata ~/.netrc), caches them in data/gap/,
writes data/gap/gap_check.json and data/gap/gap_check_table.txt.
"""
import json, sys
from pathlib import Path
import numpy as np
from scipy.ndimage import uniform_filter
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'pipeline'), str(ROOT / 'scripts')]
import series as se                 # noqa: E402
import anomaly as an                # noqa: E402
from nisar_io import open_h5        # noqa: E402

OUT = ROOT / 'data/gap'; OUT.mkdir(exist_ok=True)
X0, X1, Y0, Y1 = 352525, 358525, 3127015, 3133015
GR = {'20260702': 'NISAR_L2_PR_GSLC_024_098_A_016_4005_DHDH_A_20260702T233920_20260702T233955_P05023_N_F_J_001',
      '20260714': 'NISAR_L2_PR_GSLC_025_098_A_016_4005_DHDH_A_20260714T233920_20260714T233954_P05023_F_F_J_001',
      '20260726': 'NISAR_L2_PR_GSLC_026_098_A_016_4005_DHDH_A_20260726T233919_20260726T233954_P05023_N_F_J_001',
      '20260819': 'NISAR_L2_PR_GSLC_028_098_A_016_4005_DHDH_A_20260819T233918_20260819T233953_P05023_N_F_J_001',
      '20260831': 'NISAR_L2_PR_GSLC_029_098_A_016_4005_DHDH_A_20260831T233918_20260831T233952_P05023_N_F_J_001'}
PAIRS = [('20260702', '20260714'), ('20260714', '20260726'), ('20260726', '20260819'), ('20260819', '20260831')]
TARGET = ('20260726', '20260819')
WIN, STEP, SEARCH, MINPEAK = 48, 10, 16, 0.2


def crop(d):
    f = OUT / f'gslc_{d}.npz'
    if not f.exists():
        g = GR[d]
        for attempt in range(4):
            try:
                h = open_h5(f'https://nisar.asf.earthdatacloud.nasa.gov/NISAR/NISAR_L2_GSLC_PROVISIONAL_V1/{g}/{g}.h5')
                G = h['science/LSAR/GSLC/grids/frequencyA']
                x, y = G['xCoordinates'][:], G['yCoordinates'][:]
                ix = np.flatnonzero((x >= X0) & (x < X1)); iy = np.flatnonzero((y > Y0) & (y <= Y1))
                sl = (slice(iy[0], iy[-1] + 1), slice(ix[0], ix[-1] + 1))
                np.savez_compressed(f, s=G['HH'][sl], mask=G['mask'][sl], x=x[sl[1]], y=y[sl[0]], granule=g)
                h.close(); print('saved', d, flush=True); break
            except Exception as e:
                print('retry', d, attempt, str(e)[:120], flush=True)
    z = np.load(f)
    return z['s'], z['x'], z['y']


def masks_5m(x5, y5):
    pairs = se.load_all()
    patch20, refs, X, Y = se.regions(pairs)
    x20, y20 = X[0], Y[:, 0]
    c = np.clip(np.round((x5 - x20[0]) / (x20[1] - x20[0])).astype(int), 0, len(x20) - 1)
    r = np.clip(np.round((y5 - y20[0]) / (y20[1] - y20[0])).astype(int), 0, len(y20) - 1)
    ok = (np.abs(x20[c] - x5) <= 10)[None, :] & (np.abs(y20[r] - y5) <= 10)[:, None]
    return patch20[np.ix_(r, c)] & ok, refs['west block'][np.ix_(r, c)] & ok


def look(a, L):
    n0, n1 = a.shape[0] // L * L, a.shape[1] // L * L
    return a[:n0, :n1].reshape(n0 // L, L, n1 // L, L).mean(axis=(1, 3))


def method1(s1, s2, P, R):
    I = s1 * np.conj(s2); I[~np.isfinite(I)] = 0
    out = {}
    for L in (2, 4):
        IL = look(I, L)
        u = np.zeros(IL.shape, complex); v = np.abs(IL) > 0
        u[v] = IL[v] / np.abs(IL[v])
        PL, RL = look(P.astype(float), L) > 0.5, look(R.astype(float), L) > 0.5
        m = se.measure(u, v, PL, RL)
        out[f'L{L}'] = m and {**m, 'readable': bool(m['consistency'] >= 0.6 and m['reference_consistency'] >= 0.6)}
    # description at 10 m: local coherence (3 x 3 of 10 m cells) and neighbour phase change inside the patch
    I2 = look(I, 2); p1 = look(np.abs(s1) ** 2, 2); p2 = look(np.abs(s2) ** 2, 2)
    num = uniform_filter(I2.real, 3) + 1j * uniform_filter(I2.imag, 3)
    with np.errstate(all='ignore'):
        coh = np.abs(num) / np.sqrt(uniform_filter(p1, 3) * uniform_filter(p2, 3))
    P2 = look(P.astype(float), 2) > 0.5
    u = np.exp(1j * np.angle(I2))
    dx = np.abs(np.angle(u[:, 1:] * np.conj(u[:, :-1])))[P2[:, 1:] & P2[:, :-1]]
    dy = np.abs(np.angle(u[1:] * np.conj(u[:-1])))[P2[1:] & P2[:-1]]
    out['patch_frac_coh10m_ge_0.5'] = float((coh[P2] >= 0.5).mean())
    out['patch_median_coh10m'] = float(np.nanmedian(coh[P2]))
    out['patch_median_neighbour_phase_change_rad'] = float(np.median(np.r_[dx, dy]))
    return out


def ncc_offsets(a1, a2):
    """Offsets (rows, cols in pixels) of WIN windows of a1 found in a2, on a STEP grid."""
    h, w = a1.shape; S = WIN + 2 * SEARCH
    pts = []
    for r in range(SEARCH, h - WIN - SEARCH, STEP):
        for c in range(SEARCH, w - WIN - SEARCH, STEP):
            t = a1[r:r + WIN, c:c + WIN]; s = a2[r - SEARCH:r - SEARCH + S, c - SEARCH:c - SEARCH + S]
            if not (np.isfinite(t).all() and np.isfinite(s).all()):
                continue
            t = t - t.mean(); tn = np.sqrt((t ** 2).sum())
            if tn == 0:
                continue
            F = np.fft.rfft2(s, (S, S)); T = np.fft.rfft2(t[::-1, ::-1], (S, S))
            num = np.fft.irfft2(F * T, (S, S))[WIN - 1:S, WIN - 1:S]
            cs = np.cumsum(np.cumsum(np.pad(s, ((1, 0), (1, 0))), 0), 1)
            cs2 = np.cumsum(np.cumsum(np.pad(s ** 2, ((1, 0), (1, 0))), 0), 1)
            box = lambda C: C[WIN:, WIN:] - C[:-WIN, WIN:] - C[WIN:, :-WIN] + C[:-WIN, :-WIN]
            var = box(cs2) - box(cs) ** 2 / WIN ** 2
            with np.errstate(all='ignore'):
                cc = num / (tn * np.sqrt(np.maximum(var, 1e-12)))
            i, j = np.unravel_index(np.nanargmax(cc), cc.shape)
            pk = cc[i, j]
            if 0 < i < cc.shape[0] - 1 and 0 < j < cc.shape[1] - 1:
                di = 0.5 * (cc[i - 1, j] - cc[i + 1, j]) / (cc[i - 1, j] - 2 * pk + cc[i + 1, j])
                dj = 0.5 * (cc[i, j - 1] - cc[i, j + 1]) / (cc[i, j - 1] - 2 * pk + cc[i, j + 1])
            else:
                di = dj = 0.0
            pts.append((r + WIN / 2, c + WIN / 2, i + di - SEARCH, j + dj - SEARCH, pk))
    return np.array(pts)


def method2(s1, s2, x, y, prev_patch_mag=None):
    a1, a2 = np.abs(s1).astype(float), np.abs(s2).astype(float)
    P = ncc_offsets(a1, a2)
    P = P[P[:, 4] >= MINPEAK]
    cx = np.interp(P[:, 1], np.arange(len(x)), x); cy = np.interp(P[:, 0], np.arange(len(y)), y)
    east, north = P[:, 3] * 5.0, -P[:, 2] * 5.0
    pc = ((se.PATCH[0] + se.PATCH[1]) / 2, (se.PATCH[2] + se.PATCH[3]) / 2)
    far = np.hypot(cx - pc[0], cy - pc[1]) > 1000
    inp = (cx >= se.PATCH[0]) & (cx <= se.PATCH[1]) & (cy >= se.PATCH[2]) & (cy <= se.PATCH[3])
    be, bn = np.median(east[far]), np.median(north[far])
    east, north = east - be, north - bn
    mag_c = np.hypot(east[far], north[far])
    res = {'points': int(len(P)), 'controls': int(far.sum()), 'patch_points': int(inp.sum()),
           'bulk_shift_m': [float(be), float(bn)], 'control_p95_m': float(np.percentile(mag_c, 95)),
           'control_median_m': float(np.median(mag_c))}
    if inp.sum() >= 5:
        e, n = float(np.median(east[inp])), float(np.median(north[inp]))
        k = 1.4826 / np.sqrt(inp.sum())
        ue = k * np.median(np.abs(east[inp] - e)); un = k * np.median(np.abs(north[inp] - n))
        mag = float(np.hypot(e, n))
        res.update(patch_east_m=e, patch_north_m=n, patch_mag_m=mag, patch_unc_m=float(np.hypot(ue, un)),
                   patch_peak_median=float(np.median(P[inp, 4])),
                   patch_percentile=float(100 * (mag_c < mag).mean()))
    return res


def main():
    S = {d: crop(d) for d in GR}
    x, y = S['20260726'][1], S['20260726'][2]
    assert all(np.allclose(S[d][1], x) and np.allclose(S[d][2], y) for d in S), 'grids differ'
    P5, R5 = masks_5m(x, y)
    print('patch 5 m pixels', int(P5.sum()), 'reference', int(R5.sum()), flush=True)
    out = {'patch_5m_pixels': int(P5.sum()), 'ref_5m_pixels': int(R5.sum()), 'pairs': {}}
    for a, b in PAIRS:
        k = f'{a}_{b}'
        m1 = method1(S[a][0], S[b][0], P5, R5)
        m2 = method2(S[a][0], S[b][0], x, y)
        out['pairs'][k] = {'method1': m1, 'method2': m2}
        print(k, json.dumps(out['pairs'][k]), flush=True)
    # outcomes
    chk = out['pairs']['20260714_20260726']['method1']['L4']
    m1_works = bool(chk and abs(np.angle(np.exp(1j * (chk['phase_rad'] - (-2.91))))) <= 1.0)
    t = out['pairs']['_'.join(TARGET)]
    t1 = t['method1']
    m1_value = None
    if m1_works:
        for L in ('L2', 'L4'):
            if t1[L] and t1[L]['readable']:
                m1_value = {'L': L, 'phase_rad': t1[L]['phase_rad'], 'los_cm': t1[L]['los_cm']}; break
    t2 = t['method2']; jul = out['pairs']['20260714_20260726']['method2']
    if t2['patch_points'] < 5:
        m2_out = 'not trackable'
    elif t2['patch_mag_m'] >= t2['control_p95_m'] and t2['patch_mag_m'] >= 3 * jul.get('patch_mag_m', np.inf):
        m2_out = 'measured'
    else:
        m2_out = 'not distinguishable'
    out['outcome'] = {'method1_check_14_26_jul_works': m1_works, 'method1_target_value': m1_value,
                      'method2': m2_out,
                      'method2_upper_bound_m': (t2['patch_mag_m'] + 2 * t2['patch_unc_m']) if t2['patch_points'] >= 5 else None}
    (OUT / 'gap_check.json').write_text(json.dumps(out, indent=1))
    L = [f"patch {out['patch_5m_pixels']} px at 5 m, reference {out['ref_5m_pixels']} px", '',
         'pair                M1 L2: phase cons refcons  | M1 L4: phase cons refcons | coh10m>=.5  nbr dphi | M2: patch pts  east  north   mag  unc  pctl  ctrl p95  peak']
    for k, v in out['pairs'].items():
        f = lambda m: '   -' if not m else f"{m['phase_rad']:+.2f} {m['consistency']:.2f} {m['reference_consistency']:.2f}"
        m2 = v['method2']
        s2 = (f"{m2['patch_points']:4d} {m2['patch_east_m']:+5.2f} {m2['patch_north_m']:+5.2f} {m2['patch_mag_m']:5.2f} {m2['patch_unc_m']:4.2f} {m2['patch_percentile']:5.1f}"
              if m2['patch_points'] >= 5 else f"{m2['patch_points']:4d}  (too few)")
        L.append(f"{k}  {f(v['method1']['L2'])}  | {f(v['method1']['L4'])} | {v['method1']['patch_frac_coh10m_ge_0.5']:.2f}  {v['method1']['patch_median_neighbour_phase_change_rad']:.2f} | {s2}  {m2['control_p95_m']:.2f}  {m2.get('patch_peak_median', float('nan')):.2f}")
    L += ['', 'outcome: ' + json.dumps(out['outcome'])]
    (OUT / 'gap_check_table.txt').write_text('\n'.join(L))
    print('\n'.join(L))


if __name__ == '__main__':
    main()
