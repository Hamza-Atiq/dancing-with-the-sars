import math
def ll2utm(lon,lat,zone):
    a=6378137.0; f=1/298.257223563; k0=0.9996; e2=f*(2-f); ep2=e2/(1-e2)
    lon0=math.radians((zone-1)*6-180+3); la=math.radians(lat); lo=math.radians(lon)
    N=a/math.sqrt(1-e2*math.sin(la)**2); T=math.tan(la)**2; C=ep2*math.cos(la)**2; A=math.cos(la)*(lo-lon0)
    M=a*((1-e2/4-3*e2**2/64-5*e2**3/256)*la-(3*e2/8+3*e2**2/32+45*e2**3/1024)*math.sin(2*la)+(15*e2**2/256+45*e2**3/1024)*math.sin(4*la)-(35*e2**3/3072)*math.sin(6*la))
    x=k0*N*(A+(1-T+C)*A**3/6+(5-18*T+T*T+72*C-58*ep2)*A**5/120)+500000
    y=k0*(M+N*math.tan(la)*(A*A/2+(5-T+9*C+4*C*C)*A**4/24+(61-58*T+T*T+600*C-330*ep2)*A**6/720))
    return x,y
