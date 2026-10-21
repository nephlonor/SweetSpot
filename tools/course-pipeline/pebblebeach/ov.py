import json, sys, math
from PIL import Image, ImageDraw
F = json.load(open('/tmp/pb/feat.json')); O = F['out']
E0, N1 = -1000, 850
im = Image.open(sys.argv[1] if len(sys.argv) > 1 else '/tmp/pb/course_esri.jpg').convert('RGB'); S = 1/0.5
def px(p): return ((p[0]-E0)*S, (N1-p[1])*S)
d = ImageDraw.Draw(im)
col = {'fair': (255, 255, 0), 'green': (255, 0, 255), 'tee': (0, 255, 255), 'sand': (255, 120, 0), 'water': (0, 120, 255), 'rough': (150, 255, 150), 'boundary': (255, 255, 255)}
for k, c in col.items():
    for w in O.get(k, []):
        pts = [px(p) for p in w['pts']]
        if len(pts) > 1: d.line(pts + [pts[0]], fill=c, width=2)
for h in F['holes']:
    pts = [px(p) for p in h['pts']]; d.line(pts, fill=(255, 0, 0), width=3)
    d.text((pts[0][0]+6, pts[0][1]-14), h['tags'].get('ref', '?') + 'p' + str(h['tags'].get('par')), fill=(255, 255, 255))

im.resize((1150,900)).save('/tmp/pb/ov_all.jpg',quality=88)
W,H=im.size
k=0
for (x0,y0) in [(0,0),(1700,0),(2900,0),(0,1500),(1700,1500),(2900,1500)]:
    im.crop((x0,y0,min(W,x0+1800),min(H,y0+2100))).save(f'/tmp/pb/q{k}.jpg',quality=85);k+=1
