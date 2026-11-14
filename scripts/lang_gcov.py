"""Cut a full-resolution GCOV window around Langtang Lirung / Lhende Khola for dates around 26 Aug 2026."""
import sys, json, os, time, urllib.request, urllib.parse, numpy as np
sys.path.insert(0,'.')
from nisar_io import *; from utm import ll2xy
W,E,S,N=85.33,85.62,28.20,28.37
track="098_A_016"; want=["20260714","20260726","20260819","20260831","20260912","20260924"]
B="https://cmr.earthdata.nasa.gov/search/granules.umm_json"
with urllib.request.urlopen(B+"?"+urllib.parse.urlencode(dict(short_name="NISAR_L2_GCOV_PROVISIONAL_V1",point="85.52,28.25",page_size=2000)),timeout=120) as r: items=json.load(r)['items']
gs={}
for i in items:
    g=i['umm']['GranuleUR']; p=g.split('_')
    if '_'.join(p[5:8])==track and p[11][:8] in want: gs[p[11][:8]]=g
os.makedirs("lang",exist_ok=True)
for date in want:
    g=gs.get(date); out=f"lang/{track}_{date}.npz"
    if not g: print("missing",date); continue
    if os.path.exists(out): print("have",out); continue
    t0=time.time()
    for attempt in range(3):
        try:
            h=open_h5(f"https://nisar.asf.earthdatacloud.nasa.gov/NISAR/NISAR_L2_GCOV_PROVISIONAL_V1/{g}/{g}.h5")
            G=h['science/LSAR/GCOV/grids/frequencyA']; epsg=int(G['projection'][()])
            x=G['xCoordinates'][:]; y=G['yCoordinates'][:]
            c=[ll2xy(lo,la,epsg) for lo in(W,E) for la in(S,N)]
            ix=np.where((x>=min(a for a,_ in c))&(x<=max(a for a,_ in c)))[0]; iy=np.where((y>=min(b for _,b in c))&(y<=max(b for _,b in c)))[0]
            sl=(slice(iy[0],iy[-1]+1),slice(ix[0],ix[-1]+1))
            arr={k:G[k][sl] for k in ('HHHH','HVHV','mask','numberOfLooks') if k in G}
            np.savez_compressed(out,x=x[sl[1]],y=y[sl[0]],epsg=epsg,**arr)
            print(out,arr['HHHH'].shape,"epsg",epsg,"spacing",abs(x[1]-x[0]),"keys",list(G.keys())[:14],f"{time.time()-t0:.0f}s",flush=True); h.close(); break
        except Exception as e:
            print("retry",attempt,str(e)[:140],flush=True); time.sleep(5)
