import numpy as np
from PIL import Image
from scipy import ndimage as ndi
cx,cy,s=np.load('plan_xf.npy')
TH,SC,DE,DN=-2.0,1.03,50,0
def en2rect(E,N):
    e=np.asarray(E)-205-DE;n=np.asarray(N)-115-DN;t=np.radians(TH);ce,sn=np.cos(t),np.sin(t)
    er=ce*e-sn*n;nr=sn*e+ce*n;return cx+er*s*SC,cy-nr*s*SC
def rect2en(x,y):
    er=(np.asarray(x)-cx)/(s*SC);nr=-(np.asarray(y)-cy)/(s*SC);t=np.radians(-TH);ce,sn=np.cos(t),np.sin(t)
    return ce*er-sn*nr+205+DE, sn*er+ce*nr+115+DN
if __name__=='__main__':
    R=np.asarray(Image.open('plan_rect.jpg').convert('RGB'),float)
    Y,X=np.mgrid[0:3900,0:3000];E=X/2-750;N=980-Y/2
    x,y=en2rect(E,N)
    out=np.stack([ndi.map_coordinates(R[...,k],[y,x],order=1,cval=255) for k in range(3)],-1).astype(np.uint8)
    Image.fromarray(out).save('plan_geo_full.jpg',quality=90)
    A=Image.open('wb_64001.jpg').convert('RGB')
    Image.blend(A,Image.fromarray(out),0.5).resize((1500,1950)).save('ov_plan3.jpg',quality=85)
