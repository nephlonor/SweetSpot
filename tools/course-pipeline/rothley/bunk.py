import json, math, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from scipy.spatial import ConvexHull
F=json.load(open('feat.json')); FP=list(json.load(open('fair_polys.json')).values())+[g['hull'] for g in json.load(open('greens_auto.json')).values()]; E0,N1,RES=-650,750,0.5
I=np.array(Image.open('course.jpg').convert('RGB')).astype(float); Hh,Ww=I.shape[:2]
R,G,B=I[...,0],I[...,1],I[...,2]; L=I.mean(2)
sand=(L>150)&(B>105)&(R>G-28)&((G-B)<55)&(np.max(I,2)-np.min(I,2)<75)
sand=ndi.binary_opening(sand,iterations=1); sand=ndi.binary_closing(sand,iterations=2); sand=ndi.binary_fill_holes(sand)
# near the holes only
m=Image.new('L',(Ww,Hh),0); d=ImageDraw.Draw(m)
for h in F['holes']:
    d.line([((x-E0)/RES,(N1-y)/RES) for x,y in h['pts']],fill=255,width=int(2*45/RES))
    x,y=h['pts'][-1]; d.ellipse(((x-E0)/RES-90,(N1-y)/RES-90,(x-E0)/RES+90,(N1-y)/RES+90),fill=255)
near=np.array(m)>0
# not on paths or buildings
pm=Image.new('L',(Ww,Hh),0); d=ImageDraw.Draw(pm)
for w in F['out']['pathline']: d.line([((x-E0)/RES,(N1-y)/RES) for x,y in w['pts']],fill=255,width=10)
for w in F['out']['buildings']: d.polygon([((x-E0)/RES,(N1-y)/RES) for x,y in w['pts']],fill=255)
bad=ndi.binary_dilation(np.array(pm)>0,iterations=4)
lab,n=ndi.label(sand&near); out=[]
for k,sl in enumerate(ndi.find_objects(lab),1):
    c=lab[sl]==k; A=c.sum()*RES*RES
    if A<12 or A>450: continue
    js,is_=np.nonzero(c); js=js+sl[0].start; is_=is_+sl[1].start
    if bad[js,is_].mean()>.3: continue
    P=np.c_[E0+(is_+.5)*RES,N1-(js+.5)*RES]
    ev=np.linalg.eigvalsh(np.cov(P.T)); el=math.sqrt(ev[1]/max(ev[0],1e-6))
    if el>3.2: continue
    ring_=ndi.binary_dilation(c,iterations=6)&~ndi.binary_dilation(c,iterations=2)
    rj,ri=np.nonzero(ring_); rj=np.clip(rj+sl[0].start-0,0,Hh-1); ri=np.clip(ri+sl[1].start,0,Ww-1)
    # (dilation inside the slice is clipped at its edge; good enough with the pad below)
    sub=I[max(0,sl[0].start-8):sl[0].stop+8,max(0,sl[1].start-8):sl[1].stop+8]
    cc=np.zeros(sub.shape[:2],bool); cc[sl[0].start-max(0,sl[0].start-8):sl[0].start-max(0,sl[0].start-8)+c.shape[0],sl[1].start-max(0,sl[1].start-8):sl[1].start-max(0,sl[1].start-8)+c.shape[1]]=c
    rg=ndi.binary_dilation(cc,iterations=6)&~ndi.binary_dilation(cc,iterations=2)
    q=sub[rg]; gr=(q[:,1]-(q[:,0]+q[:,2])/2)
    if np.mean(gr>12)<.7: continue
    cxy=P.mean(0)
    if min(np.min(np.hypot(*(np.array(p)-cxy).T)) for p in FP)>22: continue
    # outline: contour of the blob (via hull of boundary is fine for bunkers but keep concavity: use a traced ring)
    import skimage.measure as sm
    pad=np.pad(c,2); cs=sm.find_contours(pad.astype(float),.5)
    ring=max(cs,key=len); ring=sm.approximate_polygon(ring,.8)
    pts=[[E0+(sl[1].start+x-2+.5)*RES, N1-(sl[0].start+y-2+.5)*RES] for y,x in ring]
    out.append(pts)
print('bunkers',len(out))
json.dump(out,open('bunkers.json','w'))
o=Image.open('course.jpg').convert('RGB'); d=ImageDraw.Draw(o)
for p in out: d.polygon([((x-E0)/RES,(N1-y)/RES) for x,y in p],outline=(255,0,0))
o.crop((1100,1000,2300,1800)).save('bk.jpg',quality=85)
