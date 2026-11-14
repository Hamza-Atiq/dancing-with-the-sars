"""Predeclared coherence/reference sweeps; no selection by expected signal."""
from pathlib import Path
import json
from datetime import datetime
import numpy as np
from utm import ll2xy
from lang_quality import gunw_quality

ROOT=Path(__file__).resolve().parents[1]
geo=json.loads((ROOT/'data/lang_sources/detachment_utm.geojson').read_text())
ll=json.loads((ROOT/'data/lang_sources/detachment.geojson').read_text())
vertices=np.array(geo['features'][0]['geometry']['coordinates'][0][0])
ll_vertices=ll['features'][0]['geometry']['coordinates'][0][0]
transformed=np.array([ll2xy(x,y,32645) for x,y in ll_vertices])
assert np.max(np.abs(vertices-transformed))<.01,'Coordinate transform differs from GDAL by >1 cm'

def inside(d):
    assert int(d['epsg'])==32645
    X,Y=np.meshgrid(d['x'],d['y']); result=np.zeros(X.shape,bool)
    for (x1,y1),(x2,y2) in zip(vertices[:-1],vertices[1:]):
        if y1!=y2: result^=((y1>Y)!=(y2>Y)) & (X<(x2-x1)*(Y-y1)/(y2-y1)+x1)
    return result

def run(paths, name):
    ds=[dict(np.load(p)) for p in paths]
    if not ds: return {'status':'no files'}
    for d in ds[1:]:
        for k in ['x','y','epsg']: assert np.array_equal(ds[0][k],d[k]), f'{name} mismatch {k}'
    base=ds[0]; aoi=inside(base); cx,cy=vertices[:-1].mean(axis=0)
    X,Y=np.meshgrid(base['x'],base['y']); r=np.hypot(X-cx,Y-cy)
    annulus=(r>=1500)&(r<=3000)&~aoi
    sectors={'all':annulus,'west':annulus&(X<cx),'east':annulus&(X>=cx),
             'north':annulus&(Y>=cy),'south':annulus&(Y<cy)}
    results={'aoi_n':int(aoi.sum()),'files':[p.name for p in paths],'mask_available':all('mask' in d for d in ds),'sweeps':{}}
    for threshold in [.3,.4,.5,.6,.7]:
        common=np.ones(aoi.shape,bool)
        for d in ds:
            common&=(d['coherenceMagnitude']>=threshold)&(d['coherenceMagnitude']<=1)&(d['connectedComponents']==1)
            common&=np.isfinite(d['unwrappedPhase'])&np.isfinite(d['ionospherePhaseScreen'])
            if 'mask' in d: common&=gunw_quality(d['mask'])['valid_land']
        selected=common&aoi
        row={'common_aoi_n':int(selected.sum()),'pairs':[]}
        for p,d in zip(paths,ds):
            # Review granule names carry timestamps; old names carry only dates.
            parts=p.stem.split('_')
            start,end=(parts[11][:8],parts[13][:8]) if parts[0]=='NISAR' else parts[-2:]
            days=(datetime.strptime(end,'%Y%m%d')-datetime.strptime(start,'%Y%m%d')).days
            factor=299792458/float(d['f0'])/(4*np.pi)*100/days
            item={'start':start,'end':end,'days':days,'reference':{},
                  'source_zero_phase_fraction':float(np.mean(d['unwrappedPhase'][aoi]==0)),
                  'source_valid_land_pixels':int((aoi&gunw_quality(d['mask'])['valid_land']).sum()) if 'mask' in d else None}
            for label,sel in sectors.items():
                ref=common&sel
                v={'reference_n':int(ref.sum())}
                for correction in ['raw','minus_ionosphere']:
                    phase=d['unwrappedPhase']-(d['ionospherePhaseScreen'] if correction=='minus_ionosphere' else 0)
                    v[correction+'_phase_equivalent_cm_day']=float((np.median(phase[selected])-np.median(phase[ref]))*factor) if selected.any() and ref.any() else None
                item['reference'][label]=v
            row['pairs'].append(item)
        results['sweeps'][str(threshold)]=row
    return results

def main():
    paths=[ROOT/'data/lang'/f'GUNW_098_A_016_{a}_{b}.npz' for a,b in [('20260702','20260714'),('20260714','20260726'),('20260726','20260819')]]
    result={'note':'Diagnostic phase-equivalent rates, no verified physical direction or stable ground. Spatially correlated pixels are not independent samples.',
        'transform_max_difference_m':float(np.max(abs(vertices-transformed))),
        'polygon_area_m2':float(abs(np.sum(vertices[:-1,0]*vertices[1:,1]-vertices[1:,0]*vertices[:-1,1]))/2),
        'ascending':run(paths,'ascending')}
    desc=sorted((ROOT/'data/lang_review').glob('*GUNW*048_D_074*202607*P05023*.npz'))
# Only the two pre-failure pairs, not the Aug16-Aug28 event pair.
    desc=[p for p in desc if p.stem.split('_')[11][:8] in ['20260711','20260723']]
    result['descending']=run(desc,'descending')
    (ROOT/'data/lang_check/sensitivity.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
    print(json.dumps({k:{t:v['common_aoi_n'] for t,v in result[k].get('sweeps',{}).items()} for k in ['ascending','descending']},indent=2))

if __name__=='__main__': main()
