import json, sys, numpy as np
from PIL import Image, ImageDraw, ImageEnhance
F=json.load(open('feat.json')); E0,N1,RES=-650,750,0.5
src=sys.argv[6] if len(sys.argv)>6 else 'course.jpg'
im=Image.open(src).convert('RGB')
e0,n0,e1,n1=map(float,sys.argv[1:5]); name=sys.argv[5]
c=im.crop((int((e0-E0)/RES),int((N1-n1)/RES),int((e1-E0)/RES),int((N1-n0)/RES)))
c=ImageEnhance.Contrast(c).enhance(1.3)
k=1.6; c=c.resize((int(c.width*k),int(c.height*k)))
d=ImageDraw.Draw(c)
px=lambda e,n:((e-e0)/RES*k,(n1-n)/RES*k)
import math
for e in range(int(math.ceil(e0/10)*10),int(e1)+1,10):
    w=(255,255,255) if e%50==0 else (200,200,200); x=px(e,0)[0]
    if e%50==0: d.line([(x,0),(x,c.height)],fill=(255,255,255),width=1); d.text((x+2,2),str(e),fill=(255,255,0))
    else: d.line([(x,0),(x,c.height)],fill=(255,255,255,60),width=1) if False else None
for n in range(int(math.ceil(n0/10)*10),int(n1)+1,10):
    y=px(0,n)[1]
    if n%50==0: d.line([(0,y),(c.width,y)],fill=(255,255,255),width=1); d.text((2,y+2),str(n),fill=(255,255,0))
# 10 m ticks along grid lines
for e in range(int(math.ceil(e0/50)*50),int(e1)+1,50):
    for n in range(int(math.ceil(n0/10)*10),int(n1)+1,10):
        x,y=px(e,n); d.line([(x-3,y),(x+3,y)],fill=(255,255,255))
for n in range(int(math.ceil(n0/50)*50),int(n1)+1,50):
    for e in range(int(math.ceil(e0/10)*10),int(e1)+1,10):
        x,y=px(e,n); d.line([(x,y-3),(x,y+3)],fill=(255,255,255))
for h in F['holes']:
    P=[px(*p) for p in h['pts']]; d.line(P,fill=(255,0,0),width=1); d.text((P[0][0]+4,P[0][1]-12),'T'+h['tags']['ref'],fill=(255,80,80))
    d.text((P[-1][0]+4,P[-1][1]),'G'+h['tags']['ref'],fill=(255,80,80))
c.save(name,quality=90); print(c.size)
