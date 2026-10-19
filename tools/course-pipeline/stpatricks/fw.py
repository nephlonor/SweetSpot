import json,math,numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage as ndi
from skimage import measure
J=json.load(open('holes.json'))
E=np.asarray(Image.open('esri.jpg').convert('RGB'),float);Wb=np.asarray(Image.open('wb_64001.jpg').convert('RGB'),float)
def score(A):
    L=A.mean(-1);g=A[...,1]-A[...,0]
    m=ndi.uniform_filter(L,7);v=ndi.uniform_filter(L*L,7)-m*m;tex=ndi.gaussian_filter(np.sqrt(np.maximum(v,0)),3)
    return ndi.gaussian_filter(g,3),tex,ndi.gaussian_filter(L,3)
gE,tE,LE=score(E);gW,tW,LW=score(Wb)
cloud=ndi.binary_dilation(ndi.gaussian_filter(E.mean(-1),6)>150,iterations=30)
mE=(gE>11)&(tE<11)
mW=(gW>4)&(tW<9)
M=np.where(cloud,mW,mE)
# near the hole lines only (old-course remnants elsewhere are dropped)
Y,X=np.mgrid[0:3900,0:3000]
near=np.zeros(M.shape,bool)
img=Image.new('L',(3000,3900),0);d=ImageDraw.Draw(img)
P=lambda e,n:((e+750)*2,(980-n)*2)
for k,H in J['holes'].items():
    L=H['line']+[J['gc'][k]];d.line([P(*p) for p in L],fill=255,width=200)
near=np.array(img)>0
M=M&near
M=ndi.binary_opening(M,iterations=3);M=ndi.binary_closing(M,iterations=6);M=ndi.binary_fill_holes(M)
lab,n=ndi.label(M);sz=ndi.sum(M,lab,range(1,n+1))/4
M=np.isin(lab,[i+1 for i,s in enumerate(sz) if s>400])
np.save('mown_mask.npy',M)
Image.fromarray((M*255).astype(np.uint8)).resize((750,975)).save('mown_mask.png')
o=E*.6;o[M]=o[M]*.5+np.array([255,0,255])*.5
Image.fromarray(o.astype(np.uint8)).crop((200,200,2600,3300)).resize((1200,1550)).save('mown_ov.jpg',quality=85)
