"""Explicit X05026 GOFF review subsets, including variance and validity masks."""
from pathlib import Path
import json
import hashlib
import numpy as np
from nisar_io import open_h5
from utm import ll2xy

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/lang_review_goff'; OUT.mkdir(exist_ok=True)
catalogue=json.loads((ROOT/'data/lang_sources/cmr_candidates.json').read_text())
for item in catalogue['collections']['GOFF']['items']:
    g=item['umm']['GranuleUR']; p=g.split('_')
    if '_'.join(p[5:8])!='098_A_016' or 'X05026' not in g or p[11][:8] not in ['20260702','20260714','20260726']: continue
    target=OUT/(g+'.npz'); sidecar=target.with_suffix('.json')
    if target.exists() and sidecar.exists(): continue
    print('fetch',g,flush=True)
    url=f'https://nisar.asf.earthdatacloud.nasa.gov/NISAR/NISAR_L2_GOFF_PROVISIONAL_V1/{g}/{g}.h5'
    with open_h5(url) as h:
        group=h['science/LSAR/GOFF/grids/frequencyA/pixelOffsets/HH']; arrays={}; attrs={}
        for layer in ['layer1','layer2','layer3']:
            L=group[layer]; x=L['xCoordinates'][:]; y=L['yCoordinates'][:]; epsg=int(L['projection'][()])
            pts=[ll2xy(lo,la,epsg) for lo in [85.48,85.56] for la in [28.26,28.32]]
            ix=np.flatnonzero((x>=min(a for a,b in pts))&(x<=max(a for a,b in pts)))
            iy=np.flatnonzero((y>=min(b for a,b in pts))&(y<=max(b for a,b in pts)))
            sl=(slice(iy[0],iy[-1]+1),slice(ix[0],ix[-1]+1))
            if arrays:
                assert np.array_equal(arrays['x'],x[sl[1]]) and np.array_equal(arrays['y'],y[sl[0]]) and int(arrays['epsg'])==epsg
            arrays.update(x=x[sl[1]],y=y[sl[0]],epsg=epsg)
            for key in L:
                ds=L[key]
                if not hasattr(ds,'ndim') or ds.ndim!=2 or ds.shape!=(len(y),len(x)): continue
                arrays[layer+'_'+key]=ds[sl]
                attrs[layer+'_'+key]={k:str(ds.attrs[k]) for k in ['description','units','_FillValue'] if k in ds.attrs}
        np.savez_compressed(target,**arrays)
        sidecar.write_text(json.dumps({'source_granule':g,'source_url':url,'attributes':attrs,
                                      'sha256':hashlib.sha256(target.read_bytes()).hexdigest()},indent=2),encoding='utf-8')
    print('saved',g,flush=True)
