import math
def ll2utm(lon,lat,zone):
    a=6378137.0; f=1/298.257223563; k0=0.9996; e2=f*(2-f); ep2=e2/(1-e2)
    lon0=math.radians((zone-1)*6-180+3); la=math.radians(lat); lo=math.radians(lon)
    N=a/math.sqrt(1-e2*math.sin(la)**2); T=math.tan(la)**2; C=ep2*math.cos(la)**2; A=math.cos(la)*(lo-lon0)
    M=a*((1-e2/4-3*e2**2/64-5*e2**3/256)*la-(3*e2/8+3*e2**2/32+45*e2**3/1024)*math.sin(2*la)+(15*e2**2/256+45*e2**3/1024)*math.sin(4*la)-(35*e2**3/3072)*math.sin(6*la))
    x=k0*N*(A+(1-T+C)*A**3/6+(5-18*T+T*T+72*C-58*ep2)*A**5/120)+500000
    y=k0*(M+N*math.tan(la)*(A*A/2+(5-T+9*C+4*C*C)*A**4/24+(61-58*T+T*T+600*C-330*ep2)*A**6/720))
    return x,y

def ll2ps(lon,lat,epsg):
    """Polar stereographic forward: EPSG 3413 (north, lat_ts 70, lon0 -45) or 3031 (south, lat_ts -71, lon0 0)."""
    a=6378137.0; f=1/298.257223563; e=math.sqrt(f*(2-f))
    if epsg==3413: sgn,lat_ts,lon0=1,70.0,-45.0
    elif epsg==3031: sgn,lat_ts,lon0=-1,71.0,0.0
    else: raise ValueError(epsg)
    phi=math.radians(sgn*lat); lam=math.radians(sgn*(lon-lon0)); pts=math.radians(lat_ts)
    t=lambda p: math.tan(math.pi/4-p/2)/((1-e*math.sin(p))/(1+e*math.sin(p)))**(e/2)
    mc=math.cos(pts)/math.sqrt(1-e*e*math.sin(pts)**2)
    rho=a*mc*t(phi)/t(pts)
    return sgn*rho*math.sin(lam), -sgn*rho*math.cos(lam)
def ll2xy(lon,lat,epsg):
    if epsg in (3413,3031): return ll2ps(lon,lat,epsg)
    if 32600<epsg<32661: return ll2utm(lon,lat,epsg-32600)
    if 32700<epsg<32761:
        x,y=ll2utm(lon,lat,epsg-32700); return x,y+10000000.0
    raise ValueError(epsg)
