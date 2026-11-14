import json, urllib.request, urllib.parse, os, sys
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
B="https://cmr.earthdata.nasa.gov/search/granules.umm_json"
def q(**p):
    with urllib.request.urlopen(B+"?"+urllib.parse.urlencode(p),timeout=120) as r: return json.load(r)['items']
sites={"manchar":(67.67,26.42,"164_D_075",0.35),"hunza_shishper":(74.60,36.38,"055_A_020",0.25),"lahore":(74.35,31.52,"084_A_017",0.30),"sukkur":(68.85,27.70,"164_D_075",0.35),"karachi":(67.05,24.85,"092_D_076",0.30)}
os.makedirs("gcov",exist_ok=True)
for name,(lon,lat,tf,half) in sites.items():
    it=q(short_name="NISAR_L2_GCOV_PROVISIONAL_V1",point=f"{lon},{lat}",page_size=200,sort_key="start_date")
    seen={}; 
    for i in it:
        u=i['umm']; p=u['GranuleUR'].split('_')
        if '_'.join(p[5:8])!=tf: continue
        seen.setdefault(p[11][:8],u)
    tiles=[]
    for date,u in sorted(seen.items()):
        png=[r['URL'] for r in u['RelatedUrls'] if r['URL'].startswith('https') and r['URL'].endswith('_LATLON.png')]
        pts=u['SpatialExtent']['HorizontalSpatialDomain']['Geometry']['GPolygons'][0]['Boundary']['Points']
        lo=[p['Longitude'] for p in pts]; la=[p['Latitude'] for p in pts]
        try:
            fn=f"gcov/{name}_{date}.png"
            if not os.path.exists(fn): urllib.request.urlretrieve(png[0],fn)
            im=Image.open(fn).convert("RGBA"); a=np.array(im)
            ys,xs=np.where(a[...,3]>0); x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max()
            x=x0+(lon-min(lo))/(max(lo)-min(lo))*(x1-x0); y=y0+(max(la)-lat)/(max(la)-min(la))*(y1-y0)
            ppd=(x1-x0)/(max(lo)-min(lo)); r=int(half*ppd)
            tiles.append((date,im.convert("RGB").crop((int(x-r),int(y-r),int(x+r),int(y+r))).resize((300,300),Image.LANCZOS)))
        except Exception as e: print(name,date,"ERR",str(e)[:60])
    if tiles:
        sh=Image.new("RGB",(300*len(tiles),300),"white")
        for k,(d,t) in enumerate(tiles): sh.paste(t,(300*k,0))
        sh.save(f"gcovsheet_{name}.png"); print(name,tf,[d for d,_ in tiles],"px/deg",round(ppd))
