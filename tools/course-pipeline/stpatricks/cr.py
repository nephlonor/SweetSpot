import sys
from PIL import Image,ImageDraw,ImageFont
def crop(e0,n0,size,name,src='wb_64001.jpg',px=1000,step=None):
    A=Image.open(src);f=ImageFont.load_default(size=22)
    step=step or (10 if size<=120 else 25 if size<=400 else 50)
    x0=(e0+750)*2;y0=(980-(n0+size))*2
    c=A.crop((int(x0),int(y0),int(x0+size*2),int(y0+size*2))).resize((px,px))
    d=ImageDraw.Draw(c);s=px/size
    for k in range(0,size+1,step):
        w=2 if k%(step*2)==0 else 1
        d.line([(k*s,0),(k*s,px)],fill=(255,255,0),width=w);d.line([(0,k*s),(px,k*s)],fill=(255,255,0),width=w)
        if k%(step*2)==0:
            d.text((k*s+3,3),str(e0+k),fill=(255,255,0),font=f);d.text((3,px-k*s-24),str(n0+k),fill=(255,255,0),font=f)
    c.save(name,quality=88)
if __name__=='__main__':
    a=sys.argv;crop(int(a[1]),int(a[2]),int(a[3]),a[4],a[5] if len(a)>5 else 'wb_64001.jpg')
