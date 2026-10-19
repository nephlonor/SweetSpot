import sys,json
from PIL import Image,ImageDraw,ImageFont
R=json.load(open(sys.argv[1]));src=sys.argv[2];out=sys.argv[3];holes=sys.argv[4].split(',')
half=int(sys.argv[5]) if len(sys.argv)>5 else 45
A=Image.open(src);f=ImageFont.load_default(size=16);fb=ImageFont.load_default(size=28)
px=500;o=Image.new('RGB',(3*px+20,2*px+10))
for i,h in enumerate(holes):
    e,n=R[h][1] if isinstance(R[h][1],list) else R[h]
    e0=round(e)-half;n0=round(n)-half;size=2*half
    x0=(e0+750)*2;y0=(980-(n0+size))*2
    c=A.crop((x0,y0,x0+size*2,y0+size*2)).resize((px,px),Image.LANCZOS)
    d=ImageDraw.Draw(c);s=px/size
    for k in range(0,size+1,10):
        d.line([(k*s,0),(k*s,px)],fill=(255,255,0),width=1);d.line([(0,k*s),(px,k*s)],fill=(255,255,0),width=1)
        d.text((k*s+2,2),str(e0+k),fill=(255,255,0),font=f);d.text((2,px-k*s-16),str(n0+k),fill=(255,255,0),font=f)
    d.text((px-60,px-40),h,fill=(255,255,255),font=fb,stroke_width=2,stroke_fill=(0,0,0))
    o.paste(c,((i%3)*(px+10),(i//3)*(px+10)))
o.save(out,quality=90)
