# fit the plan (rectified board photo) to the ground: projective + quadratic warp, metres -> plan px, by matching the plan's fairway/green
# shapes to the mown ground traced on the aerial (two-way chamfer distance)
import numpy as np,json
from PIL import Image
from scipy import ndimage as ndi, optimize
exec(open('geo.py').read().split("if __name__")[0])
PM=np.load('plan_fw.npy');M=np.load('mown_mask.npy')
dtP=ndi.distance_transform_edt(~PM)
ys,xs=np.nonzero(M[::4,::4]);E=xs*2-750.;N=980-ys*2.
dtM=ndi.distance_transform_edt(~M)/2  # metres
py,px=np.nonzero(PM[::3,::3]);px=px*3.;py=py*3.
E0,N0=E.mean(),N.mean();S=400.
def warp(p,e,n):
    u=(e-E0)/S;v=(n-N0)/S
    x0,y0=en2rect(e,n)
    X=x0+p[0]+p[1]*u+p[2]*v+p[3]*u*u+p[4]*u*v+p[5]*v*v
    Y=y0+p[6]+p[7]*u+p[8]*v+p[9]*u*u+p[10]*u*v+p[11]*v*v
    w=1+p[12]*u+p[13]*v
    return X/w+(x0*(1-1/w)) if False else (X,Y)
def cost(p,ret=False):
    X,Y=warp(p,E,N)
    a=ndi.map_coordinates(dtP,[Y,X],order=1,cval=60)
    a=np.minimum(a,60).mean()
    return a
p0=np.zeros(14)
best=optimize.minimize(cost,p0,method='Powell',options={'maxiter':20000,'xtol':1e-2,'ftol':1e-4})
print('cost before',cost(p0),'after',best.fun)
np.save('reg2_p.npy',best.x)
# per-hole check: where the plan's fairway sits against ours, as the mean chamfer distance (m) of each hole's mown pixels
