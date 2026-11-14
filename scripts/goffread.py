import sys, json, numpy as np, time
sys.path.insert(0,'.')
from nisar_io import *; from utm import ll2xy
from PIL import Image
d=json.load(open("glac_goff.json"))
want={"Hubbard (Alaska)":(-139.45,60.05,"063_A_032",25),"Baltoro (Karakoram, PK)":(76.40,35.74,"055_A_020",30)}
for name,(lon,lat,tf,half_km) in want.items():
    us=sorted([u for u in d[name] if '_'.join(u['GranuleUR'].split('_')[5:8])==tf],key=lambda u:u['GranuleUR'].split('_')[11])
    g=us[len(us)//2]['GranuleUR']; p=g.split('_'); t0=time.time()
    h=open_h5(f"https://nisar.asf.earthdatacloud.nasa.gov/NISAR/NISAR_L2_GOFF_PROVISIONAL_V1/{g}/{g}.h5")
    P=h['science/LSAR/GOFF/grids/frequencyA/pixelOffsets/HH']
    layers=[k for k in P.keys() if k.startswith('layer')]
    print(f"\n## {name}  {p[11][:8]}->{p[13][:8]}  layers {layers}")
    L=P[layers[0]]; print("   datasets:",list(L.keys()))
    for k in ('alongTrackOffset','slantRangeOffset'):
        print("   ",k,{a:(v.decode() if isinstance(v,bytes) else v) for a,v in L[k].attrs.items() if a in('units','description')})
    epsg=int(P['projection'][()]) if 'projection' in P else int(L['projection'][()])
    src=P if 'xCoordinates' in P else L
    x=src['xCoordinates'][:]; y=src['yCoordinates'][:]
    cx,cy=ll2xy(lon,lat,epsg)
    ix=np.where(np.abs(x-cx)<half_km*1000)[0]; iy=np.where(np.abs(y-cy)<half_km*1000)[0]
    print(f"   epsg {epsg} grid {len(x)}x{len(y)} spacing {abs(x[1]-x[0]):.0f} m window {len(ix)}x{len(iy)}")
    sl=(slice(iy[0],iy[-1]+1),slice(ix[0],ix[-1]+1))
    best=None
    for ln in layers:
        az=P[ln]['alongTrackOffset'][sl].astype('f8'); rg=P[ln]['slantRangeOffset'][sl].astype('f8')
        az-=np.nanmedian(az); rg-=np.nanmedian(rg)          # remove the scene-wide bulk shift
        sp=np.hypot(az,rg)/12.0                              # metres per day, slant-range plane
        v=np.isfinite(sp)
        print(f"   {ln}: valid {v.mean():.2f}  speed m/day  p50 {np.nanpercentile(sp,50):.2f}  p90 {np.nanpercentile(sp,90):.2f}  p99 {np.nanpercentile(sp,99):.2f}  max {np.nanmax(sp):.1f}")
        if best is None: best=sp
    lim=np.nanpercentile(best,99)
    t=np.clip(best/lim,0,1); img=np.stack([t*255,t*200,255*(1-t)*0.6+40],-1); img[~np.isfinite(best)]=90
    fn="goff/"+name.split()[0]+"_speed.png"; Image.fromarray(img.astype('u1')).resize((img.shape[1]*1,img.shape[0]*1)).save(fn)
    np.save("goff/"+name.split()[0]+"_speed.npy",best)
    print(f"   saved {fn} {img.shape[:2]}  colour max = {lim:.2f} m/day   {time.time()-t0:.0f}s",flush=True)
    h.close()
