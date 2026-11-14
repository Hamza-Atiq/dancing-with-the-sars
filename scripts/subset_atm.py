"""Cut the troposphere, solid-earth-tide and geometry cubes around Quetta from each GUNW pair."""
import sys, json, os, numpy as np, time
sys.path.insert(0,'.')
from nisar_io import *; from utm import ll2utm
track=sys.argv[1]
W,E,S,N=66.40,67.60,29.60,30.80
d=json.load(open("quetta_meta.json"))["NISAR_L2_GUNW_PROVISIONAL_V1"]
gs=sorted({u['GranuleUR'] for u in d if '_'.join(u['GranuleUR'].split('_')[5:8])==track}, key=lambda s:s.split('_')[11])
os.makedirs("atm",exist_ok=True)
keys=['hydrostaticTroposphericPhaseScreen','wetTroposphericPhaseScreen','slantRangeSolidEarthTidesPhase','incidenceAngle','losUnitVectorX','losUnitVectorY']
for g in gs:
    p=g.split('_'); out=f"atm/{track}_{p[11][:8]}_{p[13][:8]}.npz"
    if os.path.exists(out): print("have",out); continue
    t0=time.time()
    for attempt in range(3):
        try:
            h=open_h5(gunw_url(g)); R=h['science/LSAR/GUNW/metadata/radarGrid']
            zone=int(R['projection'][()])-32600
            x=R['xCoordinates'][:]; y=R['yCoordinates'][:]
            xs=[ll2utm(lo,la,zone)[0] for lo in(W,E) for la in(S,N)]; ys=[ll2utm(lo,la,zone)[1] for lo in(W,E) for la in(S,N)]
            ix=np.where((x>=min(xs))&(x<=max(xs)))[0]; iy=np.where((y>=min(ys))&(y<=max(ys)))[0]
            sl=(slice(None),slice(iy[0],iy[-1]+1),slice(ix[0],ix[-1]+1))
            arr={k:R[k][sl].astype('f4') for k in keys}
            np.savez_compressed(out,x=x[sl[2]],y=y[sl[1]],h=R['heightAboveEllipsoid'][:],**arr)
            print(out,arr[keys[0]].shape,f"{time.time()-t0:.0f}s",flush=True); h.close(); break
        except Exception as e:
            print("retry",attempt,str(e)[:120],flush=True); time.sleep(5)
