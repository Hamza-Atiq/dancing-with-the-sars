import numpy as np, json, colorsys
from PIL import Image, ImageDraw
import pathlib; R=str(pathlib.Path(__file__).resolve().parents[1]).replace("\\","/")+"/"
V=np.array(json.load(open(R+'data/lang_sources/detachment_utm.geojson'))['features'][0]['geometry']['coordinates'][0][0])
X0,X1,Y0,Y1=354600,356200,3129300,3130700; K=8
lut=np.array([colorsys.hsv_to_rgb(i/256,1,1) for i in range(256)])*255
ims=[]
for a,b in [('20260620','20260702'),('20260702','20260714'),('20260714','20260726'),('20260726','20260819')]:
    d=np.load(R+f'data/lang/GUNW_098_A_016_{a}_{b}.npz'); x=d['xw'];y=d['yw']
    ix=np.flatnonzero((x>=X0)&(x<=X1)); iy=np.flatnonzero((y>=Y0)&(y<=Y1))
    w=d['wrapped'][np.ix_(iy,ix)]; c=d['wcoh'][np.ix_(iy,ix)]
    rgb=lut[((np.angle(w)+np.pi)/(2*np.pi)*255).astype(int)%256]*np.clip(c/0.5,0.2,1)[...,None]
    im=Image.fromarray(rgb.astype('uint8')).resize((len(ix)*K,len(iy)*K),Image.Resampling.NEAREST); dr=ImageDraw.Draw(im)
    px=lambda X:(X-x[ix[0]]+10)/20*K; py=lambda Y:(y[iy[0]]+10-Y)/20*K
    dr.line([(px(p),py(q)) for p,q in V],fill='white',width=2)
    for gx in range(354800,356200,200): dr.line([(px(gx),0),(px(gx),im.size[1])],fill=(255,255,255),width=1); dr.text((px(gx)+2,2),str(gx),fill='white')
    for gy in range(3129400,3130700,200): dr.line([(0,py(gy)),(im.size[0],py(gy))],fill=(255,255,255),width=1); dr.text((2,py(gy)+2),str(gy),fill='white')
    dr.text((5,im.size[1]-14),f'{a}-{b}',fill='white'); ims.append(im)
W=Image.new('RGB',(ims[0].size[0]*2+6,ims[0].size[1]*2+6))
for i,im in enumerate(ims): W.paste(im,((i%2)*(im.size[0]+6),(i//2)*(im.size[1]+6)))
W.save('zoom.png'); print(W.size)
