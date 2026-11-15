"""Independent checks of how scripts/s1_patch.py reads the Sentinel-1 files. Reads only; changes nothing.

Run: C:/Users/HP/anaconda3/python.exe scripts/s1_readcheck.py
"""
import io, sys, zipfile, re
from pathlib import Path
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'pipeline'))
sys.path.insert(0, str(ROOT / 'scripts'))
import series as se
import s1_patch as sp

pairs = se.load_all()
sel = pairs[se.SELECT_PAIR]
patch_n, refs_n, Xn, Yn = se.regions(pairs)
print('NISAR grid: dx', sel['x'][1] - sel['x'][0], 'dy', sel['y'][1] - sel['y'][0],
      'shape', sel['coh'].shape, 'patch px', int(patch_n.sum()), 'west px', int(refs_n['west block'].sum()))
print('NISAR window x', sel['x'].min(), sel['x'].max(), 'y', sel['y'].min(), sel['y'].max())

try:
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 32645, always_xy=True)
    summit = tr.transform(85.5169, 28.2556)
    print('Langtang Lirung summit (85.5169E 28.2556N, 7227 m) in UTM45N:', [round(c) for c in summit])
except Exception as e:
    summit = None
    print('pyproj not available:', e)

for tag in ('039570', '258660', '180590'):
    z = sorted((ROOT / 'data/s1').glob(f'S1_{tag}_*.zip'))[4]
    zf = zipfile.ZipFile(z)
    names = zf.namelist()
    print('\n==', z.name)
    grids = {}
    for suf in ('_wrapped_phase.tif', '_corr.tif', '_dem.tif'):
        n = next(n for n in names if n.endswith(suf))
        im = Image.open(io.BytesIO(zf.read(n)))
        t = im.tag_v2
        gk = t[34735]
        keys = {gk[i]: gk[i + 3] for i in range(4, len(gk), 4)}
        print(f' {suf:20s} size {im.size} mode {im.mode} scale {t[33550][:2]} tiepoint {t[33922]} '
              f'epsg {keys.get(3072)} rastertype {keys.get(1025)} nodata {t.get(42113)}')
        grids[suf] = sp.read_tif(zf, n)
    ph, x, y, _ = grids['_wrapped_phase.tif']
    coh, xc, yc, _ = grids['_corr.tif']
    dem, xd, yd, _ = grids['_dem.tif']
    print(' same grid phase/corr/dem:', ph.shape == coh.shape == dem.shape and np.allclose(x, xc) and np.allclose(y, yc)
          and np.allclose(x, xd) and np.allclose(y, yd))
    print(' phase range', float(np.nanmin(ph)), float(np.nanmax(ph)), 'dtype', ph.dtype,
          '| corr range', float(np.nanmin(coh)), float(np.nanmax(coh)))
    # DEM test of georeferencing
    jx = (x >= sel['x'].min()) & (x <= sel['x'].max()); iy = (y >= sel['y'].min()) & (y <= sel['y'].max())
    d = dem[np.ix_(iy, jx)].astype(float); xs, ys = x[jx], y[iy]
    X, Y = np.meshgrid(xs, ys)
    pm = sp.nearest(patch_n, sel['x'], sel['y'], X, Y)
    print(' DEM on patch: median %.0f m, min %.0f, max %.0f' % (np.median(d[pm]), d[pm].min(), d[pm].max()))
    if summit:
        r = np.hypot(X - summit[0], Y - summit[1])
        if r.min() < 100:
            near = r < 600
            k = np.argmax(np.where(near, d, -1)); i, j = np.unravel_index(k, d.shape)
            print(' DEM highest point within 600 m of summit: %.0f m, %.0f m from the catalogue position'
                  % (d[i, j], r[i, j]))
        else:
            print(' summit outside window')
    # alignment against NISAR coherence: shift test
    c = coh[np.ix_(iy, jx)].astype(float)
    v = np.isfinite(c) & (c > 0)
    best = []
    for di in range(-6, 7):
        for dj in range(-6, 7):
            sc = sp.nearest(sel['coh'], sel['x'], sel['y'], X + dj * 20, Y + di * 20, fill=np.nan)
            ok = v & np.isfinite(sc)
            best.append((np.corrcoef(c[ok], sc[ok])[0, 1], di, dj))
    best.sort(reverse=True)
    zero = [b for b in best if b[1] == 0 and b[2] == 0][0]
    print(' S1 corr vs NISAR coh: r at zero shift %.3f | best r %.3f at shift (rows %d, cols %d) x20 m'
          % (zero[0], best[0][0], best[0][1], best[0][2]))
    rd = next(n for n in names if n.endswith('README.md.txt'))
    txt = zf.read(rd).decode('utf8', 'replace')
    for m in re.finditer(r'[^\n]*(toward|away|positive|negative|reference minus|sign)[^\n]*', txt, re.I):
        if tag == '039570':
            print(' README:', m.group(0).strip()[:300])
