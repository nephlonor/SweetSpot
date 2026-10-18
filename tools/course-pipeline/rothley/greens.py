import json, math, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from scipy.spatial import ConvexHull
F=json.load(open('feat.json')); E0,N1,RES=-650,750,0.5
I=np.array(Image.open('course.jpg').convert('RGB')).astype(float)
L=I.mean(2); Ls=ndi.gaussian_filter(L,1.5)
var=np.sqrt(ndi.gaussian_filter((L-ndi.gaussian_filter(L,1.5))**2,2.5))
gx=I[...,1]-(I[...,0]+I[...,2])/2
pins={}
for h in F['holes']: pins[h['tags']['ref']]=h['pts'][-1]
out={}
for ref,(e,n) in pins.items():
    cx,cy=int((e-E0)/RES),int((N1-n)/RES); r=int(26/RES)
    sub=lambda a:a[cy-r:cy+r,cx-r:cx+r]
    Lw,Vw,Gw=sub(Ls),sub(var),sub(gx)
    yy,xx=np.mgrid[-r:r,-r:r]; disk=xx**2+yy**2<r*r
    # seed stats: the smoothest bright pixels within 6 m of the end
    near=(xx**2+yy**2<(8/RES)**2)
    cand=near&(Vw<np.percentile(Vw[near],40))
    Lm=np.median(Lw[cand]); Gm=np.median(Gw[cand]); Vt=max(4.5,np.percentile(Vw[near],50)*1.5)
    m=disk&(Vw<Vt)&(abs(Lw-Lm)<16)&(abs(Gw-Gm)<14)
    m=ndi.binary_opening(m,iterations=3)
    lab,k=ndi.label(m)
    # the component holding most of the seed pixels
    ids,cnt=np.unique(lab[cand&m],return_counts=True); cnt=cnt[ids>0]; ids=ids[ids>0]
    if not len(ids): print(ref,'no green'); continue
    g=lab==ids[np.argmax(cnt)]
    g=ndi.binary_closing(g,iterations=5); g=ndi.binary_fill_holes(g); g=ndi.binary_opening(g,iterations=4)
    js,is_=np.nonzero(g); P=np.c_[E0+(cx-r+is_+.5)*RES, N1-(cy-r+js+.5)*RES]
    A=len(js)*RES*RES
    hull=P[ConvexHull(P).vertices]
    out[ref]={'area':A,'hull':hull.tolist(),'c':P.mean(0).tolist()}
    print(ref,'area %.0f'%A,'c %.1f %.1f'%tuple(P.mean(0)),'end %.1f %.1f'%(e,n),'Lm %.0f Vt %.1f'%(Lm,Vt))
json.dump(out,open('greens_auto.json','w'))
