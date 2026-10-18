import json, math, numpy as np
from scipy import ndimage as ndi
from PIL import Image, ImageDraw
F=json.load(open('feat.json')); O=F['out']
G=json.load(open('greens_manual.json')); B=json.load(open('bunkers_final.json')); FP={int(k):v for k,v in json.load(open('fair_polys.json')).items()}
CHM=np.load('mnh.npy'); ME0,MN0=-800,-900
CARD={1:393,2:341,3:427,4:163,5:251,6:447,7:149,8:328,9:457,10:281,11:393,12:192,13:423,14:450,15:521,16:391,17:368,18:515}
def pip(p,poly):
    x,y=p; c=False
    for i in range(len(poly)):
        x0,y0=poly[i]; x1,y1=poly[(i+1)%len(poly)]
        if (y0>y)!=(y1>y) and x<(x1-x0)*(y-y0)/(y1-y0)+x0: c=not c
    return c
def dpoly(p,poly): 
    if pip(p,poly): return -1
    best=1e9
    for i in range(len(poly)):
        a=poly[i]; b=poly[(i+1)%len(poly)]; dx,dy=b[0]-a[0],b[1]-a[1]; l2=dx*dx+dy*dy or 1; t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/l2))
        best=min(best,math.hypot(p[0]-a[0]-dx*t,p[1]-a[1]-dy*t))
    return best
can=ndi.median_filter(CHM,size=3)   # canopy right over the box
water=[w['pts'] for w in O['water']]; streams=[p for w in O['streams'] for p in w['pts']]
blds=[w['pts'] for w in O['buildings']]
res={}
for h in sorted(F['holes'],key=lambda h:int(h['tags']['ref'])):
    ref=int(h['tags']['ref']); P=h['pts']; t=P[0]; nx=P[1]; L0=sum(math.dist(P[i],P[i+1]) for i in range(len(P)-1))
    # length to the traced green centre
    gc=np.mean(G[str(ref)],axis=0); L0=L0-math.dist(P[-1],P[-2])+math.dist(P[-2],gc) if len(P)>2 else math.dist(t,gc)
    ux,uy=(nx[0]-t[0])/math.dist(t,nx),(nx[1]-t[1])/math.dist(t,nx)
    want=max(0,CARD[ref]*.9144-L0); ok=0; why=''   # play to the card (white tees) exactly, if the ground allows
    for k in np.arange(.5,want+.01,.5):
        c=(t[0]-ux*k,t[1]-uy*k); bad=''
        for s in (-2,0,2):
            for a in (-3,0,3,-6,-9):   # the box and the camera's spot behind it (about 9 m back)
                q=(c[0]-uy*s+ux*a,c[1]+ux*s+uy*a)
                pass   # (trees no longer stop a tee: build.py clears a chute behind and in front of the moved tee, as the club would)
        if not bad:
            for g,poly in G.items():
                if dpoly(c,poly)<(8 if int(g)!=ref else -2): bad='green '+g
            for b in B:
                if dpoly(c,b)<6: bad='bunker'
            for r,fp in FP.items():
                if r!=ref and pip(c,fp): bad='fairway %d'%r
            for w in water:
                if dpoly(c,w)<6: bad='water'
            if any(math.dist(c,s)<7 for s in streams): bad='brook'
            if not pip(c,O['boundary'][0]['pts']): bad='outside'
            for bl in blds:
                if dpoly(c,bl)<8: bad='building'
        if bad: why=bad+' at %d'%k; break
        ok=k
    ok=ok
    res[ref]=ok
    print(ref,'L %.0f card %.0f want %.0f -> back %d m  (%s)  new %.0f'%(L0,CARD[ref]*.9144,want,ok,why,L0+ok))
json.dump(res,open('tee_back.json','w'))
