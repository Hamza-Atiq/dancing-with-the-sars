import json, urllib.request, os, glob
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
d=json.load(open("quetta_meta.json"))["NISAR_L2_GUNW_PROVISIONAL_V1"]
QL,QB=67.00,30.20
os.makedirs("crops",exist_ok=True)
sel={}
for u in d:
    p=u['GranuleUR'].split('_'); sel['_'.join(p[5:8])+"_"+p[11][:8]]=u
for key in sorted(sel):
    u=sel[key]
    png=[r['URL'] for r in u['RelatedUrls'] if r['URL'].startswith('https') and r['URL'].endswith('_LATLON.png')]
    pts=u['SpatialExtent']['HorizontalSpatialDomain']['Geometry']['GPolygons'][0]['Boundary']['Points']
    lo=[p['Longitude'] for p in pts]; la=[p['Latitude'] for p in pts]
    try:
        fn="browse/"+key+".png"
        if not os.path.exists(fn): urllib.request.urlretrieve(png[0],fn)
        im=Image.open(fn).convert("RGBA"); a=np.array(im)
        mask=(a[...,3]>0)&~((a[...,0]>250)&(a[...,1]>250)&(a[...,2]>250))
        ys,xs=np.where(mask); x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max()
        x=x0+(QL-min(lo))/(max(lo)-min(lo))*(x1-x0); y=y0+(max(la)-QB)/(max(la)-min(la))*(y1-y0)
        ppd=(x1-x0)/(max(lo)-min(lo)); r=int(0.5*ppd)
        c=im.convert("RGB").crop((int(x-r),int(y-r),int(x+r),int(y+r))).resize((330,330),Image.LANCZOS)
        c.save("crops/"+key+".png"); print(key,"ok",im.size,"px/deg",round(ppd))
    except Exception as e: print(key,"ERR",str(e)[:80])
for t in sorted(set(os.path.basename(f)[:9] for f in glob.glob("crops/*.png"))):
    fs=sorted(glob.glob("crops/"+t+"*.png"))
    sheet=Image.new("RGB",(330*len(fs),330),"white")
    for i,f in enumerate(fs): sheet.paste(Image.open(f),(330*i,0))
    sheet.save("sheet_"+t+".png"); print("sheet",t,[os.path.basename(f)[10:18] for f in fs])
