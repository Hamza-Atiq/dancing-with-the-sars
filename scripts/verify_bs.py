import numpy as np, json
from PIL import Image, ImageDraw
import pathlib; R=str(pathlib.Path(__file__).resolve().parents[1]).replace("\\","/")+"/"
V=np.array(json.load(open(R+'data/lang_sources/detachment_utm.geojson'))['features'][0]['geometry']['coordinates'][0][0])
g={s:np.load(R+f'data/lang/098_A_016_{s}.npz') for s in ['20260714','20260726','20260819','20260831']}
x=g['20260714']['x'];y=g['20260714']['y']
def raster(dx=0,dy=0):
    im=Image.new('1',(len(x),len(y)));ImageDraw.Draw(im).polygon([((p+dx-x[0])/10,(y[0]-(q+dy))/10) for p,q in V],fill=1);return np.array(im,bool)
for pol in ['HHHH','HVHV']:
    ok=np.ones((len(y),len(x)),bool)
    for d in g.values(): ok&=np.isfinite(d[pol])&(d[pol]>0)&(d['mask']>=1)&(d['mask']<=5)
    with np.errstate(all='ignore'):
        q=np.abs(10*np.log10(g['20260726'][pol]/g['20260714'][pol]))>3; e=np.abs(10*np.log10(g['20260831'][pol]/g['20260819'][pol]))>3
    m=raster()&ok; print(pol,'polygon px',raster().sum(),'valid',m.sum(),'quiet %.2f event %.2f'%(100*q[m].mean(),100*e[m].mean()))
    ctl=[]
    for dx in range(-16000,8001,2000):
        for dy in range(-8000,8001,2000):
            if abs(dx)<3000 and abs(dy)<3000: continue
            if -9000<dx<-1000 and 0<dy<7000: continue  # skip debris path NW
            mm=raster(dx,dy)&ok
            if mm.sum()>0.7*raster().sum(): ctl.append((100*q[mm].mean(),100*e[mm].mean()))
    c=np.array(ctl); print('  controls n',len(c),'quiet min/med/max %.1f %.1f %.1f | event %.1f %.1f %.1f | event-quiet max %.1f'%(c[:,0].min(),np.median(c[:,0]),c[:,0].max(),c[:,1].min(),np.median(c[:,1]),c[:,1].max(),(c[:,1]-c[:,0]).max()))
