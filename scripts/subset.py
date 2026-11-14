import sys, json, os, numpy as np, time
sys.path.insert(0,'.')
from nisar_io import *; from utm import ll2utm
track=sys.argv[1]
W,E,S,N=66.45,67.55,29.65,30.75
d=json.load(open("quetta_meta.json"))["NISAR_L2_GUNW_PROVISIONAL_V1"]
gs=sorted({u['GranuleUR'] for u in d if '_'.join(u['GranuleUR'].split('_')[5:8])==track}, key=lambda s:s.split('_')[11])
os.makedirs("sub",exist_ok=True)
for g in gs:
    p=g.split('_'); out=f"sub/{track}_{p[11][:8]}_{p[13][:8]}.npz"
    if os.path.exists(out): print("have",out); continue
    t0=time.time()
    for attempt in range(3):
        try:
            h=open_h5(gunw_url(g)); G=h['science/LSAR/GUNW/grids/frequencyA/unwrappedInterferogram']
            epsg=int(G['projection'][()]); zone=epsg-32600
            x=G['xCoordinates'][:]; y=G['yCoordinates'][:]
            xs=[ll2utm(lo,la,zone)[0] for lo in(W,E) for la in(S,N)]; ys=[ll2utm(lo,la,zone)[1] for lo in(W,E) for la in(S,N)]
            ix=np.where((x>=min(xs))&(x<=max(xs)))[0]; iy=np.where((y>=min(ys))&(y<=max(ys)))[0]
            if len(ix)<50 or len(iy)<50: print("no overlap",g); break
            sl=(slice(iy[0],iy[-1]+1),slice(ix[0],ix[-1]+1))
            arr={k:G['HH/'+k][sl] for k in('unwrappedPhase','coherenceMagnitude','ionospherePhaseScreen','ionospherePhaseScreenUncertainty','connectedComponents')}
            arr['mask']=G['mask'][sl]
            f0=float(h['science/LSAR/GUNW/grids/frequencyA/centerFrequency'][()])
            np.savez_compressed(out,x=x[sl[1]],y=y[sl[0]],epsg=epsg,f0=f0,**arr)
            v=np.isfinite(arr['unwrappedPhase']).mean()
            print(f"{out} shape {arr['unwrappedPhase'].shape} epsg {epsg} f0 {f0/1e9:.4f}GHz valid {v:.2f} meancoh {np.nanmean(arr['coherenceMagnitude']):.2f} {time.time()-t0:.0f}s",flush=True)
            h.close(); break
        except Exception as e:
            print("retry",attempt,str(e)[:100],flush=True); time.sleep(5)
