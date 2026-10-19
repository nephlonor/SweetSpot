import json,sys,math
from PIL import Image,ImageDraw,ImageFont
J=json.load(open('holes.json'));src=sys.argv[1];out=sys.argv[2];hs=[int(x) for x in sys.argv[3].split(',')];half=int(sys.argv[4]) if len(sys.argv)>4 else 40
A=Image.open(src);f=ImageFont.load_default(size=15);fb=ImageFont.load_default(size=28);px=500
o=Image.new('RGB',(3*px+20,2*px+10))
for i,h in enumerate(hs):
    H=J['holes'][str(h)];e,n=H['tee'];e0=round(e)-half;n0=round(n)-half;size=2*half
    x0=(e0+750)*2;y0=(980-(n0+size))*2
    c=A.crop((x0,y0,x0+size*2,y0+size*2)).resize((px,px),Image.LANCZOS);d=ImageDraw.Draw(c);s=px/size
    for k in range(0,size+1,10):
        d.line([(k*s,0),(k*s,px)],fill=(255,255,0),width=1);d.line([(0,k*s),(px,k*s)],fill=(255,255,0),width=1)
        d.text((k*s+2,2),str(e0+k),fill=(255,255,0),font=f);d.text((2,px-k*s-16),str(n0+k),fill=(255,255,0),font=f)
    P=lambda E,N:((E-e0)*s,(n0+size-N)*s)
    L=H['line'];d.line([P(*L[0]),P(*L[1])],fill=(255,60,60),width=2)
    x,y=P(*L[0]);d.ellipse([x-6,y-6,x+6,y+6],outline=(0,220,255),width=3)
    d.text((px-60,px-40),str(h),fill=(255,255,255),font=fb,stroke_width=2,stroke_fill=(0,0,0))
    o.paste(c,((i%3)*(px+10),(i//3)*(px+10)))
o.save(out,quality=90)
