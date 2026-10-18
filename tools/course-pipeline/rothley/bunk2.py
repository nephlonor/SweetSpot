import json, math, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
import skimage.measure as sm
E0,N1,RES=-650,750,0.5
F=json.load(open('feat.json'))
out=[]
for src,thr in (('course.jpg',38),('esri.jpg',30)):
    I=np.array(Image.open(src).convert('RGB')).astype(float); L=I.mean(2)
    loc=ndi.uniform_filter(L,41); sat=I.max(2)-I.min(2)
    m=(L-loc>thr)&(sat<70)&(I[...,0]>I[...,1]-20)
    # region of interest: the dark NW part of the course
    ee,nn=np.meshgrid(E0+(np.arange(I.shape[1])+.5)*RES,N1-(np.arange(I.shape[0])+.5)*RES)
    roi=(ee<-60)&(nn>40)&(ee>-560)&(nn<620)
    m=ndi.binary_opening(m&roi,iterations=1); m=ndi.binary_fill_holes(ndi.binary_closing(m,iterations=2))
    lab,n=ndi.label(m); res=[]
    for k,sl in enumerate(ndi.find_objects(lab),1):
        c=lab[sl]==k; A=c.sum()*RES*RES
        if A<12 or A>300: continue
        js,is_=np.nonzero(c); P=np.c_[E0+(is_+sl[1].start+.5)*RES,N1-(js+sl[0].start+.5)*RES]
        ev=np.linalg.eigvalsh(np.cov(P.T)); 
        if math.sqrt(ev[1]/max(ev[0],1e-6))>3.5: continue
        ring=max(sm.find_contours(np.pad(c,2).astype(float),.5),key=len); ring=sm.approximate_polygon(ring,.8)
        res.append([[E0+(sl[1].start+x-2+.5)*RES,N1-(sl[0].start+y-2+.5)*RES] for y,x in ring])
    print(src,len(res)); out.append(res)
json.dump(out,open('bunk_nw.json','w'))
im=Image.open('esri.jpg').convert('RGB'); d=ImageDraw.Draw(im)
f=lambda q:((q[0]-E0)/RES,(N1-q[1])/RES)
for col,res in zip(((255,0,0),(0,200,255)),out):
    for i,b in enumerate(res): d.polygon([f(q) for q in b],outline=col); x,y=f(b[0]); d.text((x+6,y),str(i),fill=col)
im.crop((int((-560-E0)/RES),int((N1-620)/RES),int((-260-E0)/RES),int((N1-90)/RES))).save('nw.jpg',quality=88)
