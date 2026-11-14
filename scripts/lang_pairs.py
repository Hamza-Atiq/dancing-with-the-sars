"""Cut GUNW (phase, coherence) and GOFF (offsets) windows around Langtang Lirung for pairs leading up to and across 26 Aug 2026."""
import sys, json, os, time, urllib.request, urllib.parse, numpy as np
sys.path.insert(0,'.')
from nisar_io import *; from utm import ll2xy
W,E,S,N=85.33,85.62,28.20,28.37
track="098_A_016"; want=["20260819","20260726","20260714","20260702","20260620","20260608"]   # pair start dates, most important first
B="https://cmr.earthdata.nasa.gov/search/granules.umm_json"
def find(sn):
    with urllib.request.urlopen(B+"?"+urllib.parse.urlencode(dict(short_name=sn,point="85.52,28.25",page_size=2000)),timeout=120) as r: items=json.load(r)['items']
    out={}
    for i in items:
        g=i['umm']['GranuleUR']; p=g.split('_')
        if '_'.join(p[5:8])==track: out[p[11][:8]]=g
    return out
os.makedirs("lang",exist_ok=True)
def window(G,epsg):
    x=G['xCoordinates'][:]; y=G['yCoordinates'][:]
    c=[ll2xy(lo,la,epsg) for lo in(W,E) for la in(S,N)]
    ix=np.where((x>=min(a for a,_ in c))&(x<=max(a for a,_ in c)))[0]; iy=np.where((y>=min(b for _,b in c))&(y<=max(b for _,b in c)))[0]
    return x,y,(slice(iy[0],iy[-1]+1),slice(ix[0],ix[-1]+1))
for prod,sn in (("GUNW","NISAR_L2_GUNW_PROVISIONAL_V1"),("GOFF","NISAR_L2_GOFF_PROVISIONAL_V1")):
    gs=find(sn)
    for d0 in want:
        g=gs.get(d0); 
        if not g: print("missing",prod,d0); continue
        p=g.split('_'); out=f"lang/{prod}_{track}_{p[11][:8]}_{p[13][:8]}.npz"
        if os.path.exists(out): print("have",out); continue
        t0=time.time()
        for attempt in range(3):
            try:
                h=open_h5(f"https://nisar.asf.earthdatacloud.nasa.gov/NISAR/{sn}/{g}/{g}.h5"); arr={}
                if prod=="GUNW":
                    U=h['science/LSAR/GUNW/grids/frequencyA/unwrappedInterferogram']; epsg=int(U['projection'][()])
                    x,y,sl=window(U,epsg)
                    for k in('unwrappedPhase','coherenceMagnitude','connectedComponents','ionospherePhaseScreen'): arr[k]=U['HH/'+k][sl]
                    Wg=h['science/LSAR/GUNW/grids/frequencyA/wrappedInterferogram']; xw,yw,slw=window(Wg,epsg)
                    arr['wrapped']=Wg['HH/wrappedInterferogram'][slw]; arr['wcoh']=Wg['HH/coherenceMagnitude'][slw]; arr['xw']=xw[slw[1]]; arr['yw']=yw[slw[0]]
                    arr['f0']=float(h['science/LSAR/GUNW/grids/frequencyA/centerFrequency'][()])
                else:
                    P=h['science/LSAR/GOFF/grids/frequencyA/pixelOffsets/HH']; L=P['layer3']; epsg=int(L['projection'][()])
                    x,y,sl=window(L,epsg)
                    for ln in('layer1','layer2','layer3'):
                        for k in('alongTrackOffset','slantRangeOffset','snr','correlationSurfacePeak'): arr[ln+'_'+k]=P[ln][k][sl]
                np.savez_compressed(out,x=x[sl[1]],y=y[sl[0]],epsg=epsg,**arr)
                print(out,"epsg",epsg,[v.shape for k,v in arr.items() if hasattr(v,'shape') and v.ndim==2][:2],f"{time.time()-t0:.0f}s",flush=True); h.close(); break
            except Exception as e:
                print("retry",attempt,str(e)[:140],flush=True); time.sleep(5)
