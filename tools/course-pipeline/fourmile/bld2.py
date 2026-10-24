# buildings from the LiDAR height model (the point cloud has no building class): blobs of canopy >2.5 m that are flat-roofed/planar and compact, as minimum-rotated rectangles
import numpy as np, json
from scipy import ndimage as ndi
from scipy.spatial import ConvexHull
def mrr(pts):
    h=pts[ConvexHull(pts).vertices]; best=None
    for i in range(len(h)):
        e=h[(i+1)%len(h)]-h[i]; t=np.arctan2(e[1],e[0]); R=np.array([[np.cos(-t),-np.sin(-t)],[np.sin(-t),np.cos(-t)]])
        q=h@R.T; lo=q.min(0); hi=q.max(0); ar=(hi-lo).prod()
        if best is None or ar<best[0]:
            box=np.array([[lo[0],lo[1]],[hi[0],lo[1]],[hi[0],hi[1]],[lo[0],hi[1]]]); best=(ar,box@R)
    return best
ME0,MN0=-1000,-1140
c=np.load('mnh.npy').astype(float); d=np.load('dsm.npy').astype(float)
m=ndi.binary_opening(c>2.4,iterations=1)
lab,n=ndi.label(m)
out=[]
sl=ndi.find_objects(lab)
for k,s in enumerate(sl,1):
    mk=lab[s]==k; a=mk.sum()
    if a<70 or a>2500: continue
    h=c[s][mk]
    if h.max()>14 or np.median(h)<2.6: continue
    # roof flatness: std of the DSM gradient magnitude inside the eroded blob
    er=ndi.binary_erosion(mk,iterations=2)
    if er.sum()<10: continue
    ds=d[s]; gy,gx=np.gradient(np.where(np.isfinite(ds),ds,0))
    g=np.hypot(gx,gy)[er]
    ys,xs=np.nonzero(mk)
    pts=np.c_[xs+s[1].start+ME0+.5, ys+s[0].start+MN0+.5]
    if len(pts)<5: continue
    harea=ConvexHull(pts).volume
    if a/harea<.8: continue
    rarea,box=mrr(pts)
    if a/rarea<.75: continue
    if np.median(g)>.9: continue   # trees have a rough surface
    out.append([[round(float(x),1),round(float(y),1)] for x,y in box])
print(len(out))
json.dump(out,open('bld_lidar.json','w'))
