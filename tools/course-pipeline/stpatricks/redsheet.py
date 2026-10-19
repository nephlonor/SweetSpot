import numpy as np,json,sys
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as ndi
sk=np.load('plan_red_m.npy');A=Image.open('wb_64001.jpg').convert('RGB');Pl=Image.open('plan_geo2.jpg').convert('RGB')
B=Image.blend(A,Pl,.45)
h=open(sys.argv[1]).read();H=json.loads(h[h.index('{'):h.rindex('}')+1])['holes']
f=ImageFont.load_default(size=20)
def tile(i,px=500):
    L=H[i]['line'];xs=[p[0] for p in L];ys=[p[1] for p in L];cx=(min(xs)+max(xs))/2;cy=(min(ys)+max(ys))/2;size=int(max(max(xs)-min(xs),max(ys)-min(ys))+100)
    e0=cx-size/2;n0=cy-size/2;x0=int((e0+750)*2);y0=int((980-(n0+size))*2)
    c=np.asarray(B.crop((x0,y0,x0+2*size,y0+2*size)),float);s=ndi.binary_dilation(sk[max(0,y0):y0+2*size,max(0,x0):x0+2*size],iterations=3)
    c[:s.shape[0],:s.shape[1]][s]=[255,0,0]
    im=Image.fromarray(c.astype(np.uint8)).resize((px,px));d=ImageDraw.Draw(im);k=px/size
    d.line([((e-e0)*k,(n0+size-n)*k) for e,n in L],fill=(0,255,255),width=3)
    t=L[0];d.ellipse([(t[0]-e0)*k-6,(n0+size-t[1])*k-6,(t[0]-e0)*k+6,(n0+size-t[1])*k+6],outline=(0,255,255),width=3)
    d.text((8,8),f'{i+1}  {size} m',fill=(255,255,255),font=f,stroke_width=2,stroke_fill=(0,0,0));return im
for sh in range(3):
    o=Image.new('RGB',(1520,1010))
    for k in range(6): o.paste(tile(sh*6+k),((k%3)*510,(k//3)*510))
    o.save(f'rs{sh}.jpg',quality=86)
