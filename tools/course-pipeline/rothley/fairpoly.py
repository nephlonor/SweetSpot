import json, math, numpy as np
from scipy import ndimage as ndi
from PIL import Image, ImageDraw
R=json.load(open('fair_prof.json')); G=json.load(open('greens_auto.json'))
PAR={1:4,2:4,3:4,4:3,5:4,6:4,7:3,8:4,9:4,10:4,11:4,12:3,13:4,14:4,15:5,16:4,17:4,18:5}
START={}   # manual start distances along the line (m) where the image shows the fairway beginning
def nanfill(a):
    a=np.array(a,float); i=np.arange(len(a)); ok=~np.isnan(a)
    return np.interp(i,i[ok],a[ok]) if ok.any() else np.zeros_like(a)
polys={}
for ref_s,p in R.items():
    ref=int(ref_s); par=PAR[ref]
    if par==3: continue
    st=np.array(p['st']); C=np.array(p['C']); N=np.array(p['N'])
    l=nanfill(p['l']); r=nanfill(p['r'])
    l=ndi.median_filter(l,7); r=ndi.median_filter(r,7)
    w=r-l; c=(r+l)/2
    w=np.clip(ndi.gaussian_filter1d(w,2.5),16,40); c=np.clip(ndi.gaussian_filter1d(c,3),-9,9)
    s0=START.get(ref, min(90, 0.22*p['L']) if par>3 else 0); s1=p['L']-12
    k=(st>=s0)&(st<=s1)
    # taper both ends
    t=np.clip((st-s0)/25,0,1)*np.clip((s1-st)/10+.5,0,1); w=w*(.55+.45*t)
    Lp=C+N*(c-w/2)[:,None]; Rp=C+N*(c+w/2)[:,None]
    poly=np.r_[Lp[k],Rp[k][::-1]]
    polys[ref]=poly.tolist()
json.dump(polys,open('fair_polys.json','w'))
E0,N1,RES=-650,750,0.5
im=Image.open('course.jpg').convert('RGB'); d=ImageDraw.Draw(im)
for ref,poly in polys.items(): d.polygon([((x-E0)/RES,(N1-y)/RES) for x,y in poly],outline=(255,0,255))
for ref,g in G.items(): d.polygon([((x-E0)/RES,(N1-y)/RES) for x,y in g['hull']],outline=(0,255,255))
im.save('fp.jpg',quality=88)
for nm,(e0,n0,e1,n1) in {'A':(-540,-120,-260,600),'B':(-420,-130,100,260),'C':(-430,-500,80,-40),'D':(-20,-160,480,170),'E':(280,40,700,400),'F':(580,-180,790,400)}.items():
    im.crop((int((e0-E0)/RES),int((N1-n1)/RES),int((e1-E0)/RES),int((N1-n0)/RES))).save('fp_'+nm+'.jpg',quality=85)
