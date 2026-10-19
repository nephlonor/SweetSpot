import sys
from PIL import Image,ImageDraw,ImageFont
A=Image.open('wb_64001.jpg');P=Image.open('plan_geo_full.jpg')
f=ImageFont.load_default(size=20)
def crop(src,e0,n0,size,px=900,step=25):
    x0=(e0+750)*2;y0=(980-(n0+size))*2
    c=src.crop((int(x0),int(y0),int(x0+size*2),int(y0+size*2))).resize((px,px))
    d=ImageDraw.Draw(c);s=px/size
    for k in range(0,size+1,step):
        w=2 if k%(step*2)==0 else 1
        d.line([(k*s,0),(k*s,px)],fill=(255,255,0),width=w);d.line([(0,k*s),(px,k*s)],fill=(255,255,0),width=w)
        if k%(step*2)==0:
            d.text((k*s+3,3),str(e0+k),fill=(255,255,0),font=f);d.text((3,px-k*s-22),str(n0+k),fill=(255,255,0),font=f)
    return c
def sbs(e0,n0,size,name,step=25):
    o=Image.new('RGB',(1810,900),(0,0,0));o.paste(crop(A,e0,n0,size,step=step),(0,0));o.paste(crop(P,e0,n0,size,step=step),(910,0));o.save(name,quality=88)
if __name__=='__main__':
    e0,n0,size=map(int,sys.argv[1:4]);sbs(e0,n0,size,sys.argv[4],int(sys.argv[5]) if len(sys.argv)>5 else 25)
