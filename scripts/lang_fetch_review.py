"""Fetch small review windows with explicit source IDs and metadata.

Does not replace Claude's extracts. Uses existing Earthdata login via nisar_io.
"""
from pathlib import Path
import json
import hashlib
import time
import math
import numpy as np
import h5py
from nisar_io import open_h5
from utm import ll2xy

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/lang_review'
OUT.mkdir(exist_ok=True)
catalogue = json.loads((ROOT / 'data/lang_sources/cmr_candidates.json').read_text())
W,E,S,N = 85.48,85.56,28.26,28.32

def convert(v):
    if isinstance(v, h5py.Reference): return '<HDF5 object reference>'
    if isinstance(v, bytes): return v.decode(errors='replace')
    if isinstance(v, np.ndarray): return [convert(x) for x in v.tolist()] if v.ndim else convert(v.item())
    if isinstance(v, np.generic): return convert(v.item())
    if isinstance(v, (list,tuple)): return [convert(x) for x in v]
    if isinstance(v,float) and not math.isfinite(v): return str(v)
    return v

def window(g):
    epsg = int(g['projection'][()]); x=g['xCoordinates'][:]; y=g['yCoordinates'][:]
    pts = [ll2xy(lo,la,epsg) for lo in (W,E) for la in (S,N)]
    ix=np.flatnonzero((x>=min(p[0] for p in pts))&(x<=max(p[0] for p in pts)))
    iy=np.flatnonzero((y>=min(p[1] for p in pts))&(y<=max(p[1] for p in pts)))
    if not ix.size or not iy.size: raise ValueError('Window outside source')
    sl=(slice(iy[0],iy[-1]+1),slice(ix[0],ix[-1]+1))
    return x[sl[1]],y[sl[0]],epsg,sl

selected=[]
for item in catalogue['collections']['GUNW']['items']:
    g=item['umm']['GranuleUR']; p=g.split('_'); track='_'.join(p[5:8]); start=p[11][:8]
    if (track=='098_A_016' and start in ['20260702','20260714','20260726']) or (track=='048_D_074' and start in ['20260711','20260723','20260816']):
        selected.append(g)
for g in selected:
    output=OUT/(g+'.npz'); meta=OUT/(g+'.json')
    if output.exists() and meta.exists():
        print('have',g,flush=True); continue
    url=f'https://nisar.asf.earthdatacloud.nasa.gov/NISAR/NISAR_L2_GUNW_PROVISIONAL_V1/{g}/{g}.h5'
    t=time.time()
    print('fetch',g,flush=True)
    with open_h5(url) as h:
        root=h['science/LSAR/GUNW']
        u=root['grids/frequencyA/unwrappedInterferogram']
        x,y,epsg,sl=window(u)
        a={'x':x,'y':y,'epsg':epsg,'f0':float(root['grids/frequencyA/centerFrequency'][()])}
        attrs={}
        for k in ['unwrappedPhase','coherenceMagnitude','connectedComponents','ionospherePhaseScreen','ionospherePhaseScreenUncertainty']:
            ds=u['HH/'+k]; a[k]=ds[sl]; attrs[k]={key:convert(v) for key,v in ds.attrs.items()}
        if 'mask' in u: a['mask']=u['mask'][sl]; attrs['mask']={key:convert(v) for key,v in u['mask'].attrs.items()}
        w=root['grids/frequencyA/wrappedInterferogram']; xw,yw,_,sw=window(w)
        a.update(xw=xw,yw=yw,wrapped=w['HH/wrappedInterferogram'][sw],wcoh=w['HH/coherenceMagnitude'][sw])
        info={}
        for section in ['science/LSAR/identification','science/LSAR/GUNW/metadata/processingInformation/algorithms']:
            if section in h:
                def visit(name,obj):
                    if hasattr(obj,'shape') and obj.size<=100:
                        info[section+'/'+name]=convert(obj[()])
                h[section].visititems(visit)
        np.savez_compressed(output,**a)
        record={'source_granule':g,'source_url':url,'bbox': [W,S,E,N],
                'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'attributes':attrs,'metadata':info}
        meta.write_text(json.dumps(record,indent=2),encoding='utf-8')
    print('saved',g,round(time.time()-t),'seconds',flush=True)
