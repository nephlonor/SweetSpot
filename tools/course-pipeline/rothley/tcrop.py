import json, sys, math
from PIL import Image, ImageDraw, ImageEnhance
F=json.load(open('feat.json')); E0,N1,RES=-650,750,0.5
im=Image.open(sys.argv[1]).convert('RGB'); out=sys.argv[2]; refs=sys.argv[3].split(','); half=40; K=4
H={h['tags']['ref']:h for h in F['holes']}; tiles=[]
for ref in refs:
    P=H[ref]['pts']; t=P[0]; nx=P[1]; L=math.dist(t,nx); ux,uy=(nx[0]-t[0])/L,(nx[1]-t[1])/L
    ec,nc=round(t[0]-ux*25),round(t[1]-uy*25)
    c=im.crop((int((ec-half-E0)/RES),int((N1-nc-half)/RES),int((ec+half-E0)/RES),int((N1-nc+half)/RES))).resize((2*half*K,2*half*K)); c=ImageEnhance.Contrast(c).enhance(1.25)
    d=ImageDraw.Draw(c); f=lambda e,n:((e-ec+half)*K,(nc+half-n)*K)
    for v in range(-half,half+1,10):
        x=(v+half)*K; d.line([(x,0),(x,c.height)],fill=(200,200,200)); d.line([(0,x),(c.width,x)],fill=(200,200,200))
    # the line from the OSM tee, and extended backwards with 10 m marks
    d.line([f(*t),f(*nx)],fill=(0,220,255),width=2)
    for k in range(0,71,10):
        x,y=f(t[0]-ux*k,t[1]-uy*k); d.ellipse((x-3,y-3,x+3,y+3),outline=(255,0,0) if k else (255,255,0)); d.text((x+5,y-5),str(k),fill=(255,80,80))
    d.text((4,4),f'{ref} c({ec},{nc})',fill=(255,255,0)); tiles.append(c)
o=Image.new('RGB',(320*len(tiles),320))
for i,tl in enumerate(tiles): o.paste(tl,(i*320,0))
o.save(out,quality=90)
