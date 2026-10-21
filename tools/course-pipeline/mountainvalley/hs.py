import json, sys, math
from PIL import Image, ImageDraw
F=json.load(open('feat.json'));O=F['out']
im0=Image.open('course_esri.jpg').convert('RGB')
KT={1:(-763,543),2:(-546,650),3:(-22,520),4:(-268,322),5:(35,200),6:(279,174),7:(45,-253),8:(73,-357),9:(374,-108),10:(681,-314),11:(884,-738),12:(1073,-390),13:(891,-385),14:(511,-160),15:(361,289),16:(98,574),17:(-277,291),18:(-375,115)}
H={}
for h in F['holes']:
    for r,t in KT.items():
        if math.dist(h['pts'][0],t)<12: H[r]=h
col={'fair':(255,255,0),'green':(255,0,255),'tee':(0,255,255),'sand':(255,120,0),'water':(0,120,255),'rough':(150,255,150)}
def px(p): return ((p[0]+1000)*2,(850-p[1])*2)
d=ImageDraw.Draw(im0)
for k,c in col.items():
    for w in O.get(k,[]):
        pts=[px(p) for p in w['pts']]
        if len(pts)>1: d.line(pts+[pts[0]],fill=c,width=1)
for r,h in H.items():
    pts=[px(p) for p in h['pts']];d.line(pts,fill=(255,0,0),width=2)
for r in (int(a) for a in sys.argv[1:]):
    h=H[r];xs=[px(p)[0] for p in h['pts']];ys=[px(p)[1] for p in h['pts']]
    cx,cy=(min(xs)+max(xs))/2,(min(ys)+max(ys))/2;s=max(max(xs)-min(xs),max(ys)-min(ys))/2+140
    s=max(s,260)
    c=im0.crop((int(cx-s),int(cy-s),int(cx+s),int(cy+s))).resize((900,900))
    c.save(f'h{r}.jpg',quality=88)
