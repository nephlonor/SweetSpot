# fairway, bunker, beach, sea, path and boundary polygons from the masks (metres, local grid)
import json,math,numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage as ndi
from skimage import measure
from skimage.morphology import skeletonize
def poly_of(mask,tol=1.0,minA=20):
    out=[]
    lab,n=ndi.label(mask)
    for i in range(1,n+1):
        m=lab==i
        if m.sum()/4<minA: continue
        cs=measure.find_contours(np.pad(m,1).astype(float),.5)
        c=max(cs,key=len);c=measure.approximate_polygon(c,tol*2)
        out.append([(round((x-1)/2-750,1),round(980-(y-1)/2,1)) for y,x in c[:-1]])
    return out
def raster(polys,grow=0):
    im=Image.new('L',(3000,3900),0);d=ImageDraw.Draw(im)
    for p in polys: d.polygon([((e+750)*2,(980-n)*2) for e,n in p],fill=255)
    a=np.array(im)>0
    return ndi.binary_dilation(a,iterations=grow) if grow else a
G=json.load(open('greens.json'))
def gpoly(g):
    if 'poly' in g: return [tuple(p) for p in g['poly']]
    cx,cy,a,b,ang=g['ell'];c,s=math.cos(math.radians(ang)),math.sin(math.radians(ang))
    return [(cx+a*math.cos(t)*c-b*math.sin(t)*s,cy+a*math.cos(t)*s+b*math.sin(t)*c) for t in [i*math.pi/14 for i in range(28)]]
GP={k:gpoly(v) for k,v in G.items()}
gm=raster(GP.values(),3)
mown=np.load('mown_mask.npy')
fair=mown&~gm
fair=ndi.binary_opening(fair,iterations=2)
FAIR=poly_of(fair,1.0,150)
# sand
B=json.load(open('sand_blobs.json'));lab=np.load('sand_lab.npy')
DROP={1,97,98,101,104,231,233,219,224,241,175,150,158}
sand=np.isin(lab,[b['lab'] for b in B if b['id'] not in DROP])&~gm
beach=lab==[b['lab'] for b in B if b['id']==1][0]
beach=ndi.binary_closing(beach,iterations=8);beach=ndi.binary_fill_holes(beach)
# beach: from the dune foot (the beach's east edge, smoothed) 105 m out to the water line; the sea beyond
E_=np.full(3900,np.nan)
for y in range(3900):
    xs=np.nonzero(beach[y])[0]
    if len(xs): E_[y]=xs.max()
ok=~np.isnan(E_);yy=np.arange(3900);E_=np.interp(yy,yy[ok],E_[ok]);E_=ndi.gaussian_filter1d(E_,25)
X_=np.arange(3000)[None,:]
bm=(X_<=E_[:,None])&(X_>E_[:,None]-210);sea=X_<=E_[:,None]-210
sand&=~ndi.binary_dilation(bm|sea,iterations=8)
SAND=poly_of(ndi.binary_dilation(sand,iterations=1),.6,6)
BEACH=poly_of(bm&~sea,2.0,1000);SEA=poly_of(sea,2.0,1000)
# paths: the sandy tracks (thin bright lines the bunker pass drops), skeleton buffered to 2.4 m
A=np.asarray(Image.open('wb_64001.jpg').convert('RGB'),float);L=ndi.gaussian_filter(A.mean(-1),1);mx=A.max(-1);mn=A.min(-1)
raw=(L>160)&((mx-mn)/(mx+1)<.3)
thin=raw&~ndi.binary_opening(raw,iterations=3)&~bm&~sea
thin=ndi.binary_closing(thin,iterations=2)
lt,nt=ndi.label(thin);sz=ndi.sum(thin,lt,range(1,nt+1))/4
thin=np.isin(lt,[i+1 for i,s in enumerate(sz) if s>25])
sk=skeletonize(thin);pth=ndi.binary_dilation(sk,iterations=2)&~gm&~mown
PATH=poly_of(pth,.8,15)
# boundary: everything within 130 m of the course's features, east of the dune foot
allf=raster(FAIR)|gm|raster([[(h[0]-1,h[1]-1),(h[0]+1,h[1]-1),(h[0]+1,h[1]+1),(h[0]-1,h[1]+1)] for h in json.load(open('holes.json'))['gc'].values()])
J=json.load(open('holes.json'))
for k,H in J['holes'].items():
    im=Image.new('L',(3000,3900),0);d=ImageDraw.Draw(im);d.line([((e+750)*2,(980-n)*2) for e,n in H['line']+[J['gc'][k]]],fill=255,width=60);allf|=np.array(im)>0
dist=ndi.distance_transform_edt(~allf)/2
bnd=(dist<110)&~ndi.binary_dilation(bm|sea,iterations=6)
bnd=ndi.binary_opening(bnd,iterations=10);lb,_=ndi.label(bnd);bnd=lb==np.argmax(np.bincount(lb.ravel())[1:])+1
BND=poly_of(bnd,3.0,10000)[0]
json.dump({'fair':FAIR,'sand':SAND,'beach':BEACH,'sea':SEA,'path':PATH,'boundary':BND,'greens':GP},open('features.json','w'))
print('fair',len(FAIR),'sand',len(SAND),'beach',len(BEACH),'sea',len(SEA),'path',len(PATH),'bnd pts',len(BND))
# review image
o=np.asarray(Image.open('esri.jpg').convert('RGB'),float)*.55
for m,c in ((raster(SEA),(40,90,200)),(raster(BEACH),(240,220,160)),(raster(FAIR),(60,200,60)),(raster(SAND),(255,255,255)),(raster(PATH),(200,120,60)),(gm,(120,255,120))):
    o[m]=o[m]*.3+np.array(c)*.7
im=Image.fromarray(o.astype(np.uint8));d=ImageDraw.Draw(im);d.line([((e+750)*2,(980-n)*2) for e,n in BND+[BND[0]]],fill=(255,0,0),width=4)
im.crop((0,100,3000,3500)).resize((1100,1250)).save('feat_rev.jpg',quality=85)
