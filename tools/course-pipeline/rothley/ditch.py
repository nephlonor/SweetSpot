import numpy as np, json, math
from scipy import ndimage as ndi
from skimage.morphology import skeletonize
from PIL import Image, ImageDraw
G=np.load('mnt.npy'); CHM=np.load('mnh.npy'); ME0,MN0=-800,-900; F=json.load(open('feat.json')); O=F['out']
d=G-ndi.median_filter(G,size=11)
m=(d<-.3)
m=ndi.binary_closing(m,iterations=2)
# open ground (no canopy over it), inside the course, within 70 m of a hole line, not the brook or the railway cutting
H=G.shape[0]; W=G.shape[1]
def raster(polys):
    im=Image.new('L',(W,H),0); dr=ImageDraw.Draw(im)
    for p in polys: dr.polygon([(x-ME0,H-(y-MN0)) for x,y in p],fill=255)
    return np.array(im)[::-1]>0
def lines(ls,w):
    im=Image.new('L',(W,H),0); dr=ImageDraw.Draw(im)
    for p in ls: dr.line([(x-ME0,H-(y-MN0)) for x,y in p],fill=255,width=w)
    return np.array(im)[::-1]>0
inb=raster([O['boundary'][0]['pts']])
near=lines([h['pts'] for h in F['holes']],140)
brook=lines([w['pts'] for w in O['streams']],14)
greens=raster(json.load(open('greens_manual.json')).values())
bunk=ndi.binary_dilation(raster(json.load(open('bunkers_final.json'))),iterations=3)
open_=ndi.gaussian_filter((CHM<2.5).astype(float),1.5)>.5
m=m&inb&near&~brook&~bunk&~ndi.binary_dilation(greens,iterations=2)
sk=skeletonize(m)
lab,n=ndi.label(sk,structure=np.ones((3,3)))
out=[]
for k,sl in enumerate(ndi.find_objects(lab),1):
    c=lab[sl]==k; js,is_=np.nonzero(c)
    if len(js)<20: continue
    P=np.c_[ME0+is_+sl[1].start+.5, MN0+js+sl[0].start+.5]
    # straight-ish and thin: principal axis length vs spread
    ev,vec=np.linalg.eigh(np.cov(P.T)); 
    if math.sqrt(ev[0])>3.5: continue
    u=vec[:,1]; t=(P-P.mean(0))@u; order=np.argsort(t); Q=P[order]
    # thin to points every ~4 m along the axis
    pts=[Q[0]]; 
    for q in Q[1:]:
        if math.dist(q,pts[-1])>=4: pts.append(q)
    if len(pts)<5: continue
    op=np.mean([open_[int(p[1]-MN0),int(p[0]-ME0)] for p in pts])
    out.append({'pts':[[round(float(a),1),round(float(b),1)] for a,b in pts],'open':round(float(op),2),'len':round(float(t.max()-t.min()))})
print(len(out),[ (o['len'],o['open']) for o in out])
json.dump(out,open('ditches.json','w'))
im=Image.open('course.jpg').convert('RGB'); dr=ImageDraw.Draw(im); E0,N1,RES=-650,750,0.5
for i,o in enumerate(out):
    dr.line([((x-E0)/RES,(N1-y)/RES) for x,y in o['pts']],fill=(0,255,255) if o['open']>.5 else (255,0,0),width=5); x,y=o['pts'][0]; dr.text(((x-E0)/RES+6,(N1-y)/RES),str(i),fill=(255,255,0))
im.resize((1550,1550)).save('ditches.jpg',quality=85)
