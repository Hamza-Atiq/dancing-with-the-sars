import numpy as np
import pathlib; R=str(pathlib.Path(__file__).resolve().parents[1]).replace("\\","/")+"/"
lam=299792458/1.239e9*100
pairs=[('20260608','20260620',12),('20260620','20260702',12),('20260702','20260714',12),('20260714','20260726',12),('20260726','20260819',24),('20260819','20260831',12)]
D={p[0]:np.load(R+f'data/lang/GUNW_098_A_016_{p[0]}_{p[1]}.npz') for p in pairs}
d=D['20260714']; X,Y=np.meshgrid(d['xw'],d['yw'])
patch=(X>=355250)&(X<=355800)&(Y>=3129780)&(Y<=3130250)&(d['wcoh']>=0.45)
ref=(X>=354650)&(X<=354980)&(Y>=3129900)&(Y<=3130500)
print('patch px',patch.sum(),'area km2',patch.sum()*400/1e6,'ref px',ref.sum())
for a,b,days in pairs:
    d=D[a]; w=d['wrapped']; u=w/np.maximum(abs(w),1e-20)
    r=u[ref].mean(); rel=u[patch]*np.conj(r)/abs(r)
    ph=np.angle(rel); m=rel.mean()
    # 80 m product stats in same patch
    Xc,Yc=np.meshgrid(d['x'],d['y']); p80=(Xc>=355250)&(Xc<=355800)&(Yc>=3129780)&(Yc<=3130250)
    print(f"{a}-{b} {days}d ref|R|={abs(r):.2f} patch mean phase {np.angle(m):+.2f} rad resultant {abs(m):.2f} "
          f"=> {np.angle(m)*lam/(4*np.pi):+.1f} cm ({np.angle(m)*lam/(4*np.pi)/days:+.2f} cm/d, wrapped) "
          f"pcts {np.percentile(ph,[10,50,90]).round(2)} coh20 patch med {np.median(d['wcoh'][patch]):.2f} | 80m: coh med {np.median(d['coherenceMagnitude'][p80]):.2f} n>=0.6 {int((d['coherenceMagnitude'][p80]>=.6).sum())}/{p80.sum()} cc {np.unique(d['connectedComponents'][p80],return_counts=True)}")
