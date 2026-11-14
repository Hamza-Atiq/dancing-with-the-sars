"""Fetch the 20 m wrapped interferogram + coherence for every GUNW pair on tracks
098 A 016 and 048 D 074 over the Langtang window (85.33-85.62 E, 28.20-28.37 N).

Version rule (recorded per file): prefer forward-processed 'P' products, the ones
that existed operationally; fall back to reprocessed 'X'. Skips existing files.
Run: python scripts/series_fetch.py   (Anaconda Python, Earthdata .netrc)
"""
from pathlib import Path
import json, time, urllib.parse, urllib.request, hashlib
import numpy as np
from nisar_io import open_h5
from utm import ll2xy

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/series'; OUT.mkdir(parents=True, exist_ok=True)
W, E, S, N = 85.33, 85.62, 28.20, 28.37
SN = 'NISAR_L2_GUNW_PROVISIONAL_V1'
TRACKS = ['098_A_016', '048_D_074']

def catalogue():
    items = []
    for page in range(1, 20):
        q = dict(short_name=SN, bounding_box='85.50,28.27,85.54,28.31', page_size=2000, page_num=page)
        with urllib.request.urlopen('https://cmr.earthdata.nasa.gov/search/granules.umm_json?' + urllib.parse.urlencode(q), timeout=120) as r:
            got = json.load(r)['items']
        items += got
        if len(got) < 2000: break
    return [i['umm']['GranuleUR'] for i in items]

def choose(granules):
    pairs = {}
    for g in granules:
        p = g.split('_'); track = '_'.join(p[5:8])
        if track not in TRACKS: continue
        pairs.setdefault((track, p[11][:8], p[13][:8]), []).append(g)
    chosen = {}
    for key, gs in pairs.items():
        ranked = sorted(gs, key=lambda g: (0 if g.split('_')[15].startswith('P') else 1, g))
        chosen[key] = {'granule': ranked[0], 'alternatives': sorted(gs)}
    return chosen

def window(G, epsg):
    x = G['xCoordinates'][:]; y = G['yCoordinates'][:]
    c = [ll2xy(lo, la, epsg) for lo in (W, E) for la in (S, N)]
    ix = np.flatnonzero((x >= min(a for a, _ in c)) & (x <= max(a for a, _ in c)))
    iy = np.flatnonzero((y >= min(b for _, b in c)) & (y <= max(b for _, b in c)))
    return x, y, (slice(iy[0], iy[-1] + 1), slice(ix[0], ix[-1] + 1))

if __name__ == '__main__':
    chosen = choose(catalogue())
    (OUT / 'catalogue.json').write_text(json.dumps({f'{k[0]}_{k[1]}_{k[2]}': v for k, v in sorted(chosen.items())}, indent=1))
    print(len(chosen), 'pairs', flush=True)
    # ascending track first, newest first (most relevant first)
    order = sorted(chosen, key=lambda k: (TRACKS.index(k[0]), -int(k[1])))
    for key in order:
        g = chosen[key]['granule']; out = OUT / f'{key[0]}_{key[1]}_{key[2]}.npz'
        if out.exists(): print('have', out.name, flush=True); continue
        t0 = time.time()
        for attempt in range(4):
            try:
                h = open_h5(f'https://nisar.asf.earthdatacloud.nasa.gov/NISAR/{SN}/{g}/{g}.h5')
                Wg = h['science/LSAR/GUNW/grids/frequencyA/wrappedInterferogram']
                epsg = int(Wg['projection'][()]); x, y, sl = window(Wg, epsg)
                arr = dict(x=x[sl[1]], y=y[sl[0]], epsg=epsg, wrapped=Wg['HH/wrappedInterferogram'][sl],
                           wcoh=Wg['HH/coherenceMagnitude'][sl],
                           f0=float(h['science/LSAR/GUNW/grids/frequencyA/centerFrequency'][()]))
                if 'mask' in Wg: arr['mask'] = Wg['mask'][sl]
                h.close()
                np.savez_compressed(out, **arr)
                out.with_suffix('.json').write_text(json.dumps({'granule': g, 'alternatives': chosen[key]['alternatives'],
                    'sha256': hashlib.sha256(out.read_bytes()).hexdigest()}, indent=1))
                print('saved', out.name, arr['wrapped'].shape, f'{time.time()-t0:.0f}s', flush=True); break
            except Exception as e:
                print('retry', attempt, out.name, str(e)[:160], flush=True); time.sleep(10)
