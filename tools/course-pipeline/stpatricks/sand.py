import numpy as np,json
from PIL import Image
from scipy import ndimage as ndi
def sandmask(f,thr):
    A=np.asarray(Image.open(f).convert('RGB'),float);L=A.mean(-1);mx=A.max(-1);mn=A.min(-1);sat=(mx-mn)/(mx+1)
    return (ndi.gaussian_filter(L,1)>thr)&(sat<.28)
W=sandmask('wb_64001.jpg',170);Ee=sandmask('esri.jpg',175)
E=np.asarray(Image.open('esri.jpg').convert('RGB'),float);cloud=ndi.binary_dilation(ndi.gaussian_filter(E.mean(-1),6)>150,iterations=20)
M=W&(Ee|cloud)
M=ndi.binary_opening(M,iterations=3)   # thin tracks and paths drop out (under ~3 m wide)
M=ndi.binary_closing(M,iterations=2);M=ndi.binary_fill_holes(M)
Y,X=np.mgrid[0:3900,0:3000];Em=X/2-750;Nm=980-Y/2
beach=(Em<-300+ (Nm+0)*0)  # placeholder
lab,n=ndi.label(M);objs=ndi.find_objects(lab)
mown=np.load('mown_mask.npy');dm=ndi.distance_transform_edt(~mown)/2
out=[]
for i,sl in enumerate(objs):
    m=lab[sl]==i+1;a=m.sum()/4
    if a<6: continue
    ys,xs=np.nonzero(m);ys=ys+sl[0].start;xs=xs+sl[1].start
    e=xs/2-750;nn=980-ys/2
    d=float(dm[ys,xs].min())
    out.append({'id':len(out),'area':round(a,1),'e':round(float(e.mean()),1),'n':round(float(nn.mean()),1),'dmown':round(d,1),'lab':i+1})
np.save('sand_lab.npy',lab.astype(np.int32));json.dump(out,open('sand_blobs.json','w'))
print(len(out),sum(1 for o in out if o['dmown']<3),'touching mown')
