import sys
from PIL import Image,ImageDraw,ImageFont
S=[Image.open(f) for f in ('wb_64001.jpg','bing.jpg','course.jpg','plan_geo_full.jpg')]
f=ImageFont.load_default(size=18)
def crop(src,e0,n0,size,px,step):
    x0=(e0+750)*2;y0=(980-(n0+size))*2
    c=src.crop((int(x0),int(y0),int(x0+size*2),int(y0+size*2))).resize((px,px))
    d=ImageDraw.Draw(c);s=px/size
    for k in range(0,size+1,step):
        w=2 if k%(step*2)==0 else 1
        d.line([(k*s,0),(k*s,px)],fill=(255,255,0),width=w);d.line([(0,k*s),(px,k*s)],fill=(255,255,0),width=w)
        if k%(step*2)==0:
            d.text((k*s+3,3),str(e0+k),fill=(255,255,0),font=f);d.text((3,px-k*s-20),str(n0+k),fill=(255,255,0),font=f)
    return c
if __name__=='__main__':
    e0,n0,size=map(int,sys.argv[1:4]);step=int(sys.argv[5]) if len(sys.argv)>5 else 25
    px=700;o=Image.new('RGB',(2*px+8,2*px+8))
    for i,s in enumerate(S): o.paste(crop(s,e0,n0,size,px,step),((i%2)*(px+8),(i//2)*(px+8)))
    o.save(sys.argv[4],quality=88)
