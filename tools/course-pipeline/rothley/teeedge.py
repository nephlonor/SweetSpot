import json, math, numpy as np
from PIL import Image
from scipy import ndimage as ndi
F=json.load(open('feat.json')); E0,N1,RES=-650,750,0.5
TB=json.load(open('tee_back.json'))
out={}
for src in ('course.jpg','esri.jpg'):
    I=np.array(Image.open(src).convert('RGB')).astype(float); L=I.mean(2); Ls=ndi.gaussian_filter(L,2)
    var=np.sqrt(ndi.gaussian_filter((L-ndi.gaussian_filter(L,1.5))**2,2)); gx=ndi.gaussian_filter(I[...,1]-(I[...,0]+I[...,2])/2,2)
    samp=lambda a,e,n: ndi.map_coordinates(a,[[(N1-n)/RES],[(e-E0)/RES]],order=1)[0]
    res={}
    for h in sorted(F['holes'],key=lambda h:int(h['tags']['ref'])):
        ref=h['tags']['ref']; P=h['pts']; t=P[0]; nx=P[1]; l=math.dist(t,nx); ux,uy=(nx[0]-t[0])/l,(nx[1]-t[1])/l
        # reference: the tee itself (the OSM tee point and 4 m in front)
        def sc(k, s=0):
            e=t[0]-ux*k-uy*s; n=t[1]-uy*k+ux*s; return samp(Ls,e,n), samp(var,e,n), samp(gx,e,n)
        ref0=[sc(k) for k in (-4,-2,0)]; L0=np.mean([r[0] for r in ref0]); V0=np.mean([r[1] for r in ref0])
        last=0; gap=0
        for k in np.arange(1,60,1.0):
            Lk,Vk,Gk=sc(k)
            mown = abs(Lk-L0) < 14 and Vk < max(V0*1.6, V0+3) and Gk > 0
            if mown: last=k; gap=0
            else:
                gap+=1
                if gap>3: break
        res[ref]=last
    out[src]=res
print(out)
fin={}
for ref in out['course.jpg']:
    edge=out['course.jpg'][ref] if int(ref) not in (1,2,17,18) else out['esri.jpg'][ref]   # the north-west lies in the darker photo
    fin[ref]=min(TB[ref], edge+4)
print(fin)
json.dump({'edge':out,'final':fin},open('tee_edge.json','w'))
