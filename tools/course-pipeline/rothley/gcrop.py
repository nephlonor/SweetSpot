import json, sys, math
from PIL import Image, ImageDraw, ImageEnhance
F=json.load(open('feat.json')); E0,N1,RES=-650,750,0.5
src=sys.argv[1]; out=sys.argv[2]; refs=sys.argv[3].split(','); half=float(sys.argv[4]) if len(sys.argv)>4 else 40
im=Image.open(src).convert('RGB')
H={h['tags']['ref']:h for h in F['holes']}
K=6  # px per metre
tiles=[]
for ref in refs:
    if ',' in ref: pass
    e,n=H[ref]['pts'][-1] if ref in H else map(float,ref.split(':'))
    e=round(e/5)*5; n=round(n/5)*5
    c=im.crop((int((e-half-E0)/RES),int((N1-n-half)/RES),int((e+half-E0)/RES),int((N1-n+half)/RES))).resize((int(2*half*K),int(2*half*K)),Image.BICUBIC)
    c=ImageEnhance.Contrast(c).enhance(1.25); d=ImageDraw.Draw(c)
    for v in range(int(-half),int(half)+1,5):
        x=(v+half)*K; col=(255,255,255) if v%10==0 else (170,170,170)
        d.line([(x,0),(x,c.height)],fill=col,width=1); d.line([(0,x),(c.width,x)],fill=col,width=1)
        if v%10==0:
            d.text((x+2,2),str(int(e+v)),fill=(255,255,0)); d.text((2,(half-v)*K+2),str(int(n+v)),fill=(255,255,0))
    d.text((c.width-40,c.height-14),ref,fill=(255,0,255))
    tiles.append(c)
W=sum(t.width for t in tiles); o=Image.new('RGB',(W,tiles[0].height)); x=0
for t in tiles: o.paste(t,(x,0)); x+=t.width
o.save(out,quality=90)
