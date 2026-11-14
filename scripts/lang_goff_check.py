"""Quality-screened offset diagnostics; thresholds are sensitivity tests."""
from pathlib import Path
from datetime import datetime
import hashlib
import json
import numpy as np
from lang_sensitivity import inside, vertices
from lang_quality import goff_valid_land

ROOT=Path(__file__).resolve().parents[1]
paths=sorted((ROOT/'data/lang_review_goff').glob('*.npz'))
paths=[p for p in paths if p.with_suffix('.json').exists()]
if len(paths)!=3:
    raise SystemExit(f'Need three complete versioned pairs; have {len(paths)}')
ds=[dict(np.load(p)) for p in paths]
report={'note':'Exploratory offset/reference sensitivity, no ground-truth calibration. Native radar axes; not 3D displacement. Variance is not total uncertainty. No independent terrain or stable-ground validation.', 'provenance':{},'layers':{},'mask_available':all('mask' in d for d in ds)}
for p,d in zip(paths,ds):
    meta=json.loads(p.with_suffix('.json').read_text())
    assert hashlib.sha256(p.read_bytes()).hexdigest()==meta['sha256']
    for k in ['x','y','epsg']: assert np.array_equal(ds[0][k],d[k])
    parts=p.stem.split('_'); start,end=parts[11][:8],parts[13][:8]
    original=np.load(ROOT/'data/lang'/f'GOFF_098_A_016_{start}_{end}.npz')
    ix=np.searchsorted(original['x'],d['x']); iy=np.searchsorted(-original['y'],-d['y'])
    assert np.array_equal(original['x'][ix],d['x']) and np.array_equal(original['y'][iy],d['y'])
    matches={k:bool(np.array_equal(original[k][np.ix_(iy,ix)],d[k],equal_nan=True)) for k in original.files if k.startswith('layer')}
    report['provenance'][p.name]={'sha256_verified':True,'old_extract_matches':matches}
aoi=inside(ds[0]); X,Y=np.meshgrid(ds[0]['x'],ds[0]['y']); cx,cy=vertices[:-1].mean(axis=0)
r=np.hypot(X-cx,Y-cy); ring=(r>=1500)&(r<=3000)&~aoi
refs={'all':ring,'west':ring&(X<cx),'east':ring&(X>=cx),'north':ring&(Y>=cy),'south':ring&(Y<cy)}
for layer in ['layer1','layer2','layer3']:
    result={}
    for peak in [.3,.5,.7]:
        common=np.ones(aoi.shape,bool)
        for d in ds:
            if 'mask' in d: common&=goff_valid_land(d['mask'])
            va=d[layer+'_alongTrackOffsetVariance']; vr=d[layer+'_slantRangeOffsetVariance']; cov=d[layer+'_crossOffsetVariance']
            common&=np.isfinite(va)&np.isfinite(vr)&np.isfinite(cov)&(va>0)&(vr>0)&(cov*cov<=va*vr+1e-6)
            common&=np.isfinite(d[layer+'_alongTrackOffset'])&np.isfinite(d[layer+'_slantRangeOffset'])
            common&=(d[layer+'_snr']>=5)&np.isfinite(d[layer+'_snr'])&(d[layer+'_correlationSurfacePeak']>=peak)&(d[layer+'_correlationSurfacePeak']<=1)
        source=common&aoi
        entry={'source_n':int(source.sum()),'pairs':[]}
        for p,d in zip(paths,ds):
            parts=p.stem.split('_'); start,end=parts[11][:8],parts[13][:8]
            days=(datetime.strptime(end,'%Y%m%d')-datetime.strptime(start,'%Y%m%d')).days
            row={'start':start,'days':days,'axes':{}}
            for axis in ['alongTrack','slantRange']:
                values=d[layer+'_'+axis+'Offset']; variance=d[layer+'_'+axis+'OffsetVariance']
                rates={}; source_value=float(np.median(values[source])) if source.any() else None
                for name,selection in refs.items():
                    control=common&selection
                    rates[name]={'reference_n':int(control.sum()),'relative_cm_day':float((source_value-np.median(values[control]))*100/days) if source_value is not None and control.any() else None}
                row['axes'][axis]={'native_source_median_m':source_value,
                                  'median_formal_sigma_m':float(np.median(np.sqrt(variance[source]))) if source.any() else None,
                                  'rates':rates}
            entry['pairs'].append(row)
        result[str(peak)]=entry
    report['layers'][layer]=result
(ROOT/'data/lang_check/goff_checks.json').write_text(json.dumps(report,indent=2,allow_nan=False),encoding='utf-8')
print(json.dumps({layer:{t:v['source_n'] for t,v in values.items()} for layer,values in report['layers'].items()},indent=2))
