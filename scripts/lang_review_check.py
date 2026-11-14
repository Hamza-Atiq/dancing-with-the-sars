"""Validate versioned extracts, masks and equality against original extracts."""
from pathlib import Path
import hashlib
import json
import numpy as np
from lang_quality import gunw_quality
from lang_sensitivity import inside, run

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/lang_check'
result={'files':{},'version_sensitivity':{}}
for p in sorted((ROOT/'data/lang_review').glob('*.npz')):
    sidecar=p.with_suffix('.json')
    if not sidecar.exists(): continue
    metadata=json.loads(sidecar.read_text())
    assert hashlib.sha256(p.read_bytes()).hexdigest()==metadata['sha256']
    d=dict(np.load(p)); aoi=inside(d); q=gunw_quality(d['mask']); good=q['valid_land']&aoi
    old_parts=p.stem.split('_'); track='_'.join(old_parts[5:8]); start=old_parts[11][:8]; end=old_parts[13][:8]
    row={'source':metadata['source_granule'],'sha256_verified':True,
         'polygon_pixels':int(aoi.sum()),'valid_land_pixels':int(good.sum()),
         'phase_zero_pixels':int((aoi&(d['unwrappedPhase']==0)).sum()),
         'coherent_valid_component1_pixels':int((good&(d['coherenceMagnitude']>=.6)&(d['connectedComponents']==1)).sum()),
         'ionosphere_interpolated_valid_land_pixels':int((good&q['ionosphere_interpolated']).sum()),
         'polygon_mask_counts':{str(int(k)):int(v) for k,v in zip(*np.unique(d['mask'][aoi],return_counts=True))}}
    old=ROOT/'data/lang'/f'GUNW_{track}_{start}_{end}.npz'
    if old.exists():
        with np.load(old) as original:
            ix=np.searchsorted(original['x'],d['x']); iy=np.searchsorted(-original['y'],-d['y'])
            assert np.array_equal(original['x'][ix],d['x']) and np.array_equal(original['y'][iy],d['y'])
            assert np.array_equal(original['epsg'],d['epsg'])
            row['exact_match_old_extract']={k:bool(np.array_equal(original[k][np.ix_(iy,ix)],d[k],equal_nan=True)) for k in ['unwrappedPhase','coherenceMagnitude','connectedComponents','ionospherePhaseScreen']}
    result['files'][p.name]=row
for version in ['P05023','X05026']:
    paths=sorted((ROOT/'data/lang_review').glob(f'*098_A_016*{version}*.npz'))
    result['version_sensitivity'][version]=run(paths,version) if len(paths)==3 else {'status':'incomplete','available':len(paths),'required':3}
desc=sorted((ROOT/'data/lang_review').glob('*048_D_074*.npz'))
desc=[p for p in desc if p.stem.split('_')[11][:8] in ['20260711','20260723']]
result['version_sensitivity']['descending']=run(desc,'descending') if len(desc)==2 else {'status':'incomplete'}
(OUT/'review_checks.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
print(json.dumps({k:{a:v[a] for a in ['valid_land_pixels','coherent_valid_component1_pixels']} for k,v in result['files'].items()},indent=2))
