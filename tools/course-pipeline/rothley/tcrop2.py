import json, sys, math
from PIL import Image, ImageDraw, ImageEnhance
F=json.load(open('feat.json')); E0,N1,RES=-650,750,0.5
im=Image.open(sys.argv[1]).convert('RGB'); out=sys.argv[2]; refs=sys.argv[3].split(','); half=26; K=7
H={h['tags']['ref']:h for h in F['holes']}; tiles=[]
for ref in refs:
    P=H[ref]['pts']; t=P[0]; nx=P[1]; L=math.dist(t,nx); ux,uy=(nx[0]-t[0])/L,(nx[1]-t[1])/L
    # rotate so the hole plays up the tile: sample by hand
    S=2*half*K; tile=Image.new('RGB',(S,S)); px=tile.load(); src=im.load()
    for j in range(S):
        for i in range(S):
            a=(i-S/2)/K; b=(S*.72-j)/K        # a: across (right +), b: along the hole (forward +); the tee sits 72% down
            e=t[0]+ux*b+uy*a; n=t[1]+uy*b-ux*a
            x=(e-E0)/RES; y=(N1-n)/RES
            if 0<=x<im.width-1 and 0<=y<im.height-1: px[i,j]=src[int(x),int(y)]
    tile=ImageEnhance.Contrast(tile).enhance(1.3); d=ImageDraw.Draw(tile)
    cx=S/2; ty=S*.72
    for k in range(0,int(S*.28/K)+1,2):
        y=ty+k*K; d.line([(cx-6 if k%10 else cx-14,y),(cx+6 if k%10 else cx+14,y)],fill=(255,255,0) if k%10==0 else (255,120,120))
        if k%10==0: d.text((cx+16,y-6),str(k),fill=(255,255,0))
    for k in range(0,int(S*.72/K),10): y=ty-k*K; d.line([(cx-3,y),(cx+3,y)],fill=(0,220,255))
    d.text((4,4),ref,fill=(255,255,0)); tiles.append(tile)
o=Image.new('RGB',(S*len(tiles),S))
for i,t in enumerate(tiles): o.paste(t,(i*S,0))
o.save(out,quality=88); print(o.size)
