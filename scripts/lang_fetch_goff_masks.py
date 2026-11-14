"""Add parent-grid GOFF masks, which are outside the per-layer groups."""
from pathlib import Path
import hashlib
import json
import numpy as np
from nisar_io import open_h5

ROOT=Path(__file__).resolve().parents[1]
for p in sorted((ROOT/'data/lang_review_goff').glob('*.npz')):
    sidecar=p.with_suffix('.json'); meta=json.loads(sidecar.read_text())
    with np.load(p) as source: arrays=dict(source)
    if 'mask' in arrays: continue
    with open_h5(meta['source_url']) as h:
        parent=h['science/LSAR/GOFF/grids/frequencyA/pixelOffsets']
        x=parent['xCoordinates'][:]; y=parent['yCoordinates'][:]
        ix=np.searchsorted(x,arrays['x']); iy=np.searchsorted(-y,-arrays['y'])
        assert np.array_equal(x[ix],arrays['x']) and np.array_equal(y[iy],arrays['y'])
        ds=parent['mask']; arrays['mask']=ds[iy[0]:iy[-1]+1,ix[0]:ix[-1]+1]
        meta['attributes']['mask']={k:str(ds.attrs[k]) for k in ['description','_FillValue'] if k in ds.attrs}
    np.savez_compressed(p,**arrays)
    meta['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
    sidecar.write_text(json.dumps(meta,indent=2),encoding='utf-8')
    print('mask saved',p.name,flush=True)
