import json, sys
from PIL import Image, ImageDraw
G=json.load(open('greens_manual.json')); B=json.load(open('bunkers.json')); E0,N1,RES=-650,750,0.5
im=Image.open(sys.argv[1]).convert('RGB'); out=sys.argv[2]; refs=sys.argv[3].split(','); half=float(sys.argv[4]) if len(sys.argv)>4 else 40
S=360; tiles=[]
for ref in refs:
    p=G[ref]; e=sum(q[0] for q in p)/len(p); n=sum(q[1] for q in p)/len(p)
    c=im.crop((int((e-half-E0)/RES),int((N1-n-half)/RES),int((e+half-E0)/RES),int((N1-n+half)/RES))).resize((S,S)); d=ImageDraw.Draw(c); s=S/(2*half)
    f=lambda q:((q[0]-e+half)*s,(n+half-q[1])*s)
    for k,g in G.items(): d.polygon([f(q) for q in g],outline=(255,0,255))
    for b in B: d.polygon([f(q) for q in b],outline=(255,40,0))
    d.text((4,4),ref,fill=(255,255,0)); tiles.append(c)
o=Image.new('RGB',(S*len(tiles),S))
for i,t in enumerate(tiles): o.paste(t,(i*S,0))
o.save(out,quality=88)
