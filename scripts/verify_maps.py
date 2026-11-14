import numpy as np, json, glob, colorsys, sys
from PIL import Image, ImageDraw
import pathlib; R=str(pathlib.Path(__file__).resolve().parents[1]).replace("\\","/")+"/"
V=np.array(json.load(open(R+'data/lang_sources/detachment_utm.geojson'))['features'][0]['geometry']['coordinates'][0][0])
CX,CY=354900.,3130100.; H=2000.; S=600
def crop(x,y,a):
    ix=np.flatnonzero(abs(x-CX)<=H); iy=np.flatnonzero(abs(y-CY)<=H)
    return x[ix],y[iy],a[np.ix_(iy,ix)]
def finish(rgb,x,y,title):
    im=Image.fromarray(rgb.astype('uint8')).resize((S,S),Image.Resampling.NEAREST)
    d=ImageDraw.Draw(im)
    px=lambda X:(X-(x[0]-(x[1]-x[0])/2))/((x[-1]-x[0])+(x[1]-x[0]))*S
    py=lambda Y:((y[0]+(y[0]-y[1])/2)-Y)/((y[0]-y[-1])+(y[0]-y[1]))*S
    d.line([(px(a),py(b)) for a,b in V],fill=(0,0,0),width=2)
    d.line([(20,S-15),(20+500/(2*H)*S,S-15)],fill=(0,0,0),width=4)
    out=Image.new('RGB',(S,S+18),'white'); out.paste(im,(0,18)); ImageDraw.Draw(out).text((4,3),title,fill='black'); return out
def bwr(z,lim):
    z=np.clip(z/lim,-1,1); bad=~np.isfinite(z); z=np.nan_to_num(z)
    rgb=np.stack([255*(1+np.minimum(z,0)),255*(1-abs(z)),255*(1-np.maximum(z,0))],-1); rgb[bad]=110; return rgb
def cyc(ph,coh):
    h=(ph+np.pi)/(2*np.pi); out=np.zeros(ph.shape+(3,))
    lut=np.array([colorsys.hsv_to_rgb(i/256,1,1) for i in range(256)])*255
    out=lut[(h*255).astype(int)%256]; return out*np.clip(coh/0.5,0.25,1)[...,None]
def grey(a,lo,hi): g=np.clip((a-lo)/(hi-lo),0,1)*255; return np.stack([g]*3,-1)
def box(a,n):
    from scipy.ndimage import uniform_filter
    return uniform_filter(a,n)
def sheet(ims,name,cols):
    rows=(len(ims)+cols-1)//cols; W=Image.new('RGB',(cols*(S+6),rows*(S+24)),'white')
    for i,im in enumerate(ims): W.paste(im,((i%cols)*(S+6),(i//cols)*(S+24)))
    W.save(name)
# 1 backscatter
g={s:np.load(R+f'data/lang/098_A_016_{s}.npz') for s in ['20260714','20260726','20260819','20260831']}
ims=[]
for a,b in [('20260714','20260726'),('20260819','20260831')]:
    for pol in ['HHHH']:
        A=box(np.nan_to_num(g[a][pol]),5); B=box(np.nan_to_num(g[b][pol]),5)
        with np.errstate(all='ignore'): dB=10*np.log10(B/A)
        x,y,z=crop(g[a]['x'],g[a]['y'],dB); ims.append(finish(bwr(z,6),x,y,f'{a}->{b} {pol} dB change, 50 m box, +-6'))
x,y,z=crop(g['20260819']['x'],g['20260819']['y'],10*np.log10(box(np.nan_to_num(g['20260819']['HHHH']),3)+1e-9)); ims.append(finish(grey(z,-22,3),x,y,'HH 19 Aug (pre) dB'))
x,y,z=crop(g['20260831']['x'],g['20260831']['y'],10*np.log10(box(np.nan_to_num(g['20260831']['HHHH']),3)+1e-9)); ims.append(finish(grey(z,-22,3),x,y,'HH 31 Aug (post) dB'))
sheet(ims,'bs.png',2)
# 2 wrapped phase
ims=[];ims2=[]
for a,b in [('20260620','20260702'),('20260702','20260714'),('20260714','20260726'),('20260726','20260819')]:
    d=np.load(R+f'data/lang/GUNW_098_A_016_{a}_{b}.npz')
    x,y,w=crop(d['xw'],d['yw'],d['wrapped']); _,_,c=crop(d['xw'],d['yw'],d['wcoh'])
    ims.append(finish(cyc(np.angle(w),c),x,y,f'{a}-{b} wrapped phase 20 m (dimmed by coh)'))
    ims2.append(finish(grey(c,0,1),x,y,f'{a}-{b} coherence 20 m 0..1'))
sheet(ims+ims2,'ph.png',4)
# 3 GOFF
ims=[]
for a,b,days in [('20260702','20260714',12),('20260714','20260726',12),('20260726','20260819',24)]:
    d=np.load(R+f'data/lang/GOFF_098_A_016_{a}_{b}.npz')
    for L in ['layer1','layer3']:
        for ax in ['slantRangeOffset','alongTrackOffset']:
            o=d[f'{L}_{ax}'].astype(float); pk=d[f'{L}_correlationSurfacePeak']
            o[(abs(o)>30)|(pk<0.15)]=np.nan
            x,y,z=crop(d['x'],d['y'],o); z=z-np.nanmedian(z)
            ims.append(finish(bwr(z/days*12,3),x,y,f'{a}-{b} {L} {ax[:-6]} m per 12 d, +-3 m'))
sheet(ims,'goff.png',4)
