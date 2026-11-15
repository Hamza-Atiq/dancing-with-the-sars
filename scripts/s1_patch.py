"""Measure the Langtang patch in Sentinel-1 burst interferograms (HyP3 INSAR_ISCE_BURST, 20 m).

Rules were written before any Sentinel-1 data was opened and copy the NISAR method (pipeline/series.py):
  * patch = the NISAR-selected patch pixels (box + 20 m coherence >= 0.45 in the 14-26 Jul NISAR pair),
    mapped to the Sentinel-1 grid by nearest neighbour
  * reference = the same west block
  * phase = complex mean of unit phasors, patch minus reference
  * "resolved" = patch consistency >= 0.6 and reference consistency >= 0.6
  * controls = the same control boxes as pipeline/series.py, measured the same way in each pair
No Sentinel-1 quantity is used to choose pixels, except validity (finite, non-zero).

Run: C:/Users/HP/anaconda3/python.exe scripts/s1_patch.py     -> data/s1/s1_patch.json
"""
import io
import json
import re
import sys
import zipfile
from pathlib import Path
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'pipeline'))
import series as se  # noqa: E402

RAD_TO_CM = 299792458 / 5.405e9 * 100 / (4 * np.pi)   # C-band, cm of line of sight per radian
TRACK = {'039570': '019 D', '258660': '121 D', '180590': '085 A'}


def read_tif(zf, name):
    im = Image.open(io.BytesIO(zf.read(name)))
    a = np.asarray(im)
    sx, sy = im.tag_v2[33550][:2]
    tp = im.tag_v2[33922]
    gk = im.tag_v2[34735]
    epsg = next((gk[i + 3] for i in range(4, len(gk), 4) if gk[i] == 3072), None)
    area = next((gk[i + 3] for i in range(4, len(gk), 4) if gk[i] == 1025), 1)
    off = 0.5 if area == 1 else 0.0                     # pixel-is-area -> centre coordinates
    x = tp[3] + (np.arange(a.shape[1]) + off) * sx
    y = tp[4] - (np.arange(a.shape[0]) + off) * sy
    return a, x, y, epsg


def nearest(src, sx, sy, X, Y, fill=False):
    """Sample boolean/float grid src (axes sy descending or ascending, sx) at points X, Y."""
    dx, dy = sx[1] - sx[0], sy[1] - sy[0]
    j = np.rint((X - sx[0]) / dx).astype(int)
    i = np.rint((Y - sy[0]) / dy).astype(int)
    ok = (i >= 0) & (i < src.shape[0]) & (j >= 0) & (j < src.shape[1])
    out = np.full(X.shape, fill, dtype=src.dtype)
    out[ok] = src[i[ok], j[ok]]
    return out


def main():
    pairs = se.load_all()
    sel = pairs[se.SELECT_PAIR]
    patch_n, refs_n, Xn, Yn = se.regions(pairs)
    selcoh = sel['coh']
    x0w, x1w, y0w, y1w = sel['x'].min(), sel['x'].max(), sel['y'].min(), sel['y'].max()
    rows = []
    for z in sorted((ROOT / 'data/s1').glob('*.zip')):
        zf = zipfile.ZipFile(z)
        names = zf.namelist()
        wp = next(n for n in names if n.endswith('_wrapped_phase.tif'))
        cc = next(n for n in names if n.endswith('_corr.tif'))
        ph, x, y, epsg = read_tif(zf, wp)
        coh, _, _, _ = read_tif(zf, cc)
        m = re.search(r'S1_(\d{6})_IW\d_(\d{8})_(\d{8})', z.name)
        burst, d0, d1 = m.groups()
        if epsg != 32645:
            rows.append({'file': z.name, 'error': f'epsg {epsg}'})
            continue
        jx = (x >= x0w) & (x <= x1w)
        iy = (y >= y0w) & (y <= y1w)
        ph, coh, x, y = ph[np.ix_(iy, jx)], coh[np.ix_(iy, jx)], x[jx], y[iy]
        X, Y = np.meshgrid(x, y)
        v = np.isfinite(ph) & (ph != 0) & np.isfinite(coh) & (coh > 0)
        u = np.where(v, np.exp(1j * np.nan_to_num(ph)), 0)
        patch = nearest(patch_n, sel['x'], sel['y'], X, Y)
        west = nearest(refs_n['west block'], sel['x'], sel['y'], X, Y)
        sc = nearest(selcoh, sel['x'], sel['y'], X, Y, fill=0.0)
        mres = se.measure(u, v, patch, west)
        row = {'track': TRACK.get(burst, burst), 'start': d0, 'end': d1, 'days': se.days(f'{d0}_{d1}'),
               'patch_pixels_on_grid': int(patch.sum()), 'patch_valid': int((patch & v).sum()),
               'patch_median_coherence': float(np.median(coh[patch & v])) if (patch & v).any() else None,
               'west_median_coherence': float(np.median(coh[west & v])) if (west & v).any() else None,
               'window_median_coherence': float(np.median(coh[v])) if v.any() else None}
        if mres:
            row.update(phase_rad=mres['phase_rad'], consistency=mres['consistency'],
                       reference_consistency=mres['reference_consistency'],
                       los_cm=mres['phase_rad'] * RAD_TO_CM,
                       resolved=bool(mres['consistency'] >= se.RESOLVED_CONSISTENCY
                                     and mres['reference_consistency'] >= se.RESOLVED_CONSISTENCY))
        else:
            row.update(resolved=False)
        # controls: same construction as pipeline/series.py, on this grid
        n0 = int(patch.sum())
        w, h = se.PATCH[1] - se.PATCH[0], se.PATCH[3] - se.PATCH[2]
        vals, cohs = [], []
        for cx in np.arange(x0w + 1500, x1w - 1500, 1000):
            for cy in np.arange(y0w + 1500, y1w - 1500, 1000):
                if abs(cx - se.PATCH[0]) < 2000 and abs(cy - se.PATCH[2]) < 2000:
                    continue
                bx = (X >= cx - 700) & (X <= cx + w + 100) & (Y >= cy - 100) & (Y <= cy + h + 400)
                if not bx.any():
                    continue
                ii, jj = np.nonzero(bx)
                sl = (slice(ii.min(), ii.max() + 1), slice(jj.min(), jj.max() + 1))
                Xs, Ys = X[sl], Y[sl]
                pm = se.box(Xs, Ys, (cx, cx + w, cy, cy + h)) & (sc[sl] >= se.PATCH_COH)
                if pm.sum() < n0:
                    continue
                rm = se.box(Xs, Ys, (cx + se.WEST_BLOCK[0] - se.PATCH[0], cx + se.WEST_BLOCK[1] - se.PATCH[0],
                                     cy + se.WEST_BLOCK[2] - se.PATCH[2], cy + se.WEST_BLOCK[3] - se.PATCH[2]))
                if (pm & v[sl]).any():
                    cohs.append(float(np.median(coh[sl][pm & v[sl]])))
                c = se.measure(u[sl], v[sl], pm, rm)
                if c and c['consistency'] >= se.RESOLVED_CONSISTENCY and c['reference_consistency'] >= se.RESOLVED_CONSISTENCY:
                    vals.append(abs(c['phase_rad']))
        vals, cohs = np.array(vals), np.array(cohs)
        row['controls_resolved'] = int(vals.size)
        row['controls_with_coherence'] = int(cohs.size)
        if vals.size:
            row.update(control_median_rad=float(np.median(vals)), control_p95_rad=float(np.percentile(vals, 95)),
                       control_max_rad=float(vals.max()))
            if row.get('resolved'):
                row['controls_at_or_above'] = int((vals >= abs(row['phase_rad'])).sum())
        if cohs.size and row['patch_median_coherence'] is not None:
            row['control_median_coherence'] = float(np.median(cohs))
            row['patch_coherence_percentile'] = float(100 * (cohs < row['patch_median_coherence']).mean())
        rows.append(row)
    rows.sort(key=lambda r: (r.get('track', ''), r.get('start', '')))
    (ROOT / 'data/s1/s1_patch.json').write_text(json.dumps(rows, indent=1))
    f = lambda v, n=2: '   -' if v is None else f'{v:.{n}f}'
    print('track  pair               valid coh_p coh_w coh_ctl pct | consist ref_c  rad    cm   res | ctl_n ctl_p95 ctl_max >=')
    for r in rows:
        if 'error' in r:
            print(r)
            continue
        print(f"{r['track']} {r['start']}-{r['end'][4:]} {r['days']:>2}d {r['patch_valid']:>4}/{r['patch_pixels_on_grid']:<4}"
              f" {f(r['patch_median_coherence'])} {f(r['west_median_coherence'])} {f(r.get('control_median_coherence'))}"
              f" {f(r.get('patch_coherence_percentile'), 0):>4} | {f(r.get('consistency'))} {f(r.get('reference_consistency'))}"
              f" {f(r.get('phase_rad')):>6} {f(r.get('los_cm')):>6} {'YES' if r.get('resolved') else 'no ':>3} |"
              f" {r['controls_resolved']:>4} {f(r.get('control_p95_rad'))} {f(r.get('control_max_rad'))} {r.get('controls_at_or_above', '')}")


if __name__ == '__main__':
    main()
