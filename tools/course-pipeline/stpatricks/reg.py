import numpy as np
from PIL import Image
from scipy import ndimage as ndi
cx,cy,s=np.load('plan_xf.npy')
R=np.asarray(Image.open('plan_rect.jpg').convert('L'),float)
A=np.asarray(Image.open('wb_64001.jpg').convert('L').resize((375,488)),float)  # 4 m/px
def norm(a,sig,bg):
    a=a-ndi.gaussian_filter(a,bg);a=ndi.gaussian_filter(a,sig);return (a-a.mean())/a.std()
An=norm(A,1,12)
Rn=norm(R,1.27*4,12*4*1.27)
Y,X=np.mgrid[0:488,0:375];E=X*4-750+2;N=980-Y*4-2
m=(E>-450)&(E<650)&(N>-650)&(N<850);E=E[m];N=N[m];Am=An[m]
def score(th,sc,dE,dN):
    e=E-205-dE;n=N-115-dN;t=np.radians(th);ce,sn=np.cos(t),np.sin(t)
    er=ce*e-sn*n;nr=sn*e+ce*n
    v=ndi.map_coordinates(Rn,[cy-nr*s*sc,cx+er*s*sc],order=1,cval=0)
    return np.mean(v*Am)
best=max(((score(th,sc,dE,dN),th,sc,dE,dN) for th in range(-10,11,2) for sc in (0.92,0.96,1.0,1.04,1.08) for dE in range(-80,81,20) for dN in range(-80,81,20)))
print('coarse',best,flush=True)
_,th0,sc0,dE0,dN0=best
best=max(((score(th,sc,dE,dN),th,sc,dE,dN) for th in np.arange(th0-1.5,th0+1.6,0.5) for sc in np.arange(sc0-0.03,sc0+0.031,0.01) for dE in range(dE0-15,dE0+16,5) for dN in range(dN0-15,dN0+16,5)))
print('fine',best)
