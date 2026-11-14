import json, urllib.request, os, numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
d=json.load(open("glac_goff.json")); os.makedirs("goff",exist_ok=True)
want={"Baltoro (Karakoram, PK)":(76.40,35.74,"055_A_020",0.45),"Hubbard (Alaska)":(-139.45,60.05,"063_A_032",0.5),"Hispar (PK)":(75.30,36.10,"055_A_020",0.45)}
for name,(lon,lat,tf,half) in want.items():
    us=[u for u in d[name] if '_'.join(u['GranuleUR'].split('_')[5:8])==tf]
    us=sorted(us,key=lambda u:u['GranuleUR'].split('_')[11])
    u=us[len(us)//2]
    pngs=[r['URL'] for r in u['RelatedUrls'] if r['URL'].startswith('https') and r['URL'].endswith('.png') and 'thumbnail' not in r['URL']]
    print(name,u['GranuleUR'][:70],[p.split('J_001')[-1] for p in pngs])
    pts=u['SpatialExtent']['HorizontalSpatialDomain']['Geometry']['GPolygons'][0]['Boundary']['Points']
    lo=[p['Longitude'] for p in pts]; la=[p['Latitude'] for p in pts]
    for p in pngs:
        if 'LATLON' not in p: continue
        fn="goff/"+name.split()[0]+p.split('J_001')[-1]
        urllib.request.urlretrieve(p,fn)
        im=Image.open(fn).convert("RGBA"); a=np.array(im)
        ys,xs=np.where(a[...,3]>0); x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max()
        x=x0+(lon-min(lo))/(max(lo)-min(lo))*(x1-x0); y=y0+(max(la)-lat)/(max(la)-min(la))*(y1-y0)
        ppd=(x1-x0)/(max(lo)-min(lo)); r=int(half*ppd)
        im.convert("RGB").crop((int(x-r),int(y-r),int(x+r),int(y+r))).resize((700,700),Image.LANCZOS).save(fn.replace(".png","_crop.png"))
        print("  saved",fn.replace(".png","_crop.png"),"px/deg",round(ppd))
