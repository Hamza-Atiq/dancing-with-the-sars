"""Backscatter change across the collapse, with shifted-polygon controls (spec 4.5)."""
from pathlib import Path
import json
import numpy as np
from scipy.ndimage import uniform_filter
import geo

ROOT = Path(__file__).resolve().parents[1]
DATES = {'quiet': ('20260714', '20260726'), 'event': ('20260819', '20260831')}
THRESH_DB = 3.0


def polygon():
    f = json.loads((ROOT / 'data/lang_sources/detachment_utm.geojson').read_text())
    return np.array(f['features'][0]['geometry']['coordinates'][0][0])


def load():
    need = sorted({d for p in DATES.values() for d in p})
    g = {s: np.load(ROOT / f'data/lang/098_A_016_{s}.npz') for s in need}
    base = g[need[0]]
    for d in g.values():
        assert np.array_equal(d['x'], base['x']) and np.array_equal(d['y'], base['y']) and int(d['epsg']) == int(base['epsg'])
    return g, base['x'], base['y'], int(base['epsg'])


def stats():
    g, x, y, epsg = load()
    V = polygon()
    out = {'threshold_db': THRESH_DB, 'intervals': DATES, 'channels': {}}
    for pol in ['HHHH', 'HVHV']:
        ok = np.ones((len(y), len(x)), bool)
        for d in g.values():
            ok &= np.isfinite(d[pol]) & (d[pol] > 0) & (d['mask'] >= 1) & (d['mask'] <= 5)
        big = {}
        with np.errstate(all='ignore'):
            for k, (a, b) in DATES.items():
                big[k] = np.abs(10 * np.log10(g[b][pol] / g[a][pol])) > THRESH_DB
        m0 = geo.inside(x, y, V); m = m0 & ok
        row = {'polygon_pixels': int(m0.sum()), 'valid_pixels': int(m.sum()),
               'quiet_pct': float(100 * big['quiet'][m].mean()), 'event_pct': float(100 * big['event'][m].mean())}
        ctl = []
        for dx in range(-16000, 8001, 2000):
            for dy in range(-8000, 8001, 2000):
                if abs(dx) < 3000 and abs(dy) < 3000: continue          # the collapse itself
                if -9000 < dx < -1000 and 0 < dy < 7000: continue       # debris path to the north-west
                mm = geo.inside(x, y, V + [dx, dy]) & ok
                if mm.sum() > 0.7 * m0.sum():
                    ctl.append((100 * big['quiet'][mm].mean(), 100 * big['event'][mm].mean()))
        c = np.array(ctl)
        row.update(controls_n=len(c), control_event_minus_quiet_max=float((c[:, 1] - c[:, 0]).max()),
                   control_event_minus_quiet_median=float(np.median(c[:, 1] - c[:, 0])),
                   event_minus_quiet=row['event_pct'] - row['quiet_pct'])
        out['channels'][pol] = row
    return out


def change_maps(box=5):
    """Smoothed dB change maps (power averaged in a box before the ratio)."""
    g, x, y, epsg = load()
    maps = {}
    for k, (a, b) in DATES.items():
        A = uniform_filter(np.nan_to_num(g[a]['HHHH']).astype(float), box)
        B = uniform_filter(np.nan_to_num(g[b]['HHHH']).astype(float), box)
        ok = uniform_filter(((g[a]['mask'] >= 1) & (g[a]['mask'] <= 5) & (g[b]['mask'] >= 1) & (g[b]['mask'] <= 5)).astype(float), box) > 0.99
        with np.errstate(all='ignore'):
            z = 10 * np.log10(B / A)
        z[~ok | ~np.isfinite(z)] = np.nan
        maps[k] = z
    return maps, x, y, epsg


if __name__ == '__main__':
    print(json.dumps(stats(), indent=1))
