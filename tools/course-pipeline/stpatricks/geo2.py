import numpy as np,json
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as ndi
exec(open('reg2.py').read().split("p0=np.zeros")[0])
p=np.load('reg2_p.npy')
R=np.asarray(Image.open('plan_rect.jpg').convert('RGB'),float)
Y,X=np.mgrid[0:3900,0:3000];Ee=X/2-750;Nn=980-Y/2
x,y=warp(p,Ee,Nn)
out=np.stack([ndi.map_coordinates(R[...,k],[y,x],order=1,cval=255) for k in range(3)],-1).astype(np.uint8)
Image.fromarray(out).save('plan_geo2.jpg',quality=90)
A=Image.open('wb_64001.jpg').convert('RGB')
o=Image.blend(A,Image.fromarray(out),.55);d=ImageDraw.Draw(o);f=ImageFont.load_default(size=44)
h=open('rd_head.js').read();H=json.loads(h[h.index('{'):h.rindex('}')+1])['holes']
P=lambda e,n:((e+750)*2,(980-n)*2)
for i,hh in enumerate(H):
    d.line([P(*q) for q in hh['line']],fill=(0,255,255),width=4);x0,y0=P(*hh['tee']);d.text((x0+10,y0),str(i+1),fill=(0,255,255),font=f,stroke_width=3,stroke_fill=(0,0,0))
o.save('ov_plan4.jpg',quality=85)
o.crop((300,200,1700,1700)).save('op_NW.jpg',quality=85);o.crop((1300,200,2700,1700)).save('op_NE.jpg',quality=85)
o.crop((300,1600,1700,3300)).save('op_SW.jpg',quality=85);o.crop((1300,1600,2700,3300)).save('op_SE.jpg',quality=85)
