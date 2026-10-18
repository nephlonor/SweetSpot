import json, sys, math
from PIL import Image, ImageDraw, ImageEnhance
F=json.load(open('feat.json')); G=json.load(open('greens_manual.json')); B=json.load(open('bunkers.json')); E0,N1,RES=-650,750,0.5
src=sys.argv[1]; out=sys.argv[2]; refs=sys.argv[3].split(',')
im=Image.open(src).convert('RGB'); H={h['tags']['ref']:h for h in F['holes']}; tiles=[]
for ref in refs:
    P=H[ref]['pts']; xs=[p[0] for p in P]; ys=[p[1] for p in P]; m=45
    e0,e1,n0,n1=min(xs)-m,max(xs)+m,min(ys)-m,max(ys)+m
    c=im.crop((int((e0-E0)/RES),int((N1-n1)/RES),int((e1-E0)/RES),int((N1-n0)/RES))); k=700/max(c.size); c=c.resize((int(c.width*k),int(c.height*k))); c=ImageEnhance.Contrast(c).enhance(1.2)
    d=ImageDraw.Draw(c); s=k/RES; f=lambda q:((q[0]-e0)*s,(n1-q[1])*s)
    for i,b in enumerate(B):
        bc=(sum(q[0] for q in b)/len(b),sum(q[1] for q in b)/len(b))
        if e0<bc[0]<e1 and n0<bc[1]<n1: d.polygon([f(q) for q in b],outline=(255,0,0)); x,y=f(bc); d.text((x+8,y-6),str(i),fill=(255,255,0))
    for g in G.values(): d.polygon([f(q) for q in g],outline=(255,0,255))
    d.line([f(q) for q in P],fill=(0,200,255))
    # 10 m scale ticks in the corner, labelled corner coords
    d.text((4,4),f'{ref}  e{e0:.0f}..{e1:.0f} n{n0:.0f}..{n1:.0f}  {s:.2f}px/m',fill=(255,255,0))
    tiles.append(c)
W=sum(t.width for t in tiles); Hh=max(t.height for t in tiles); o=Image.new('RGB',(W,Hh)); x=0
for t in tiles: o.paste(t,(x,0)); x+=t.width
o.save(out,quality=88); print(out,o.size)
