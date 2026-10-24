# OSM features and hole lines over the aerial mosaic (0.5 m/px, north up, top row = N1)
import json, sys
from PIL import Image, ImageDraw
E0, N1, S = -1000, 1110, 2.0
F = json.load(open('feat.json')); O = F['out']
im = Image.open(sys.argv[1]).convert('RGB'); out = sys.argv[2]
def px(p): return ((p[0]-E0)*S, (N1-p[1])*S)
d = ImageDraw.Draw(im)
col = {'fair': (255, 255, 0), 'green': (255, 0, 255), 'tee': (0, 255, 255), 'sand': (255, 120, 0), 'water': (0, 120, 255), 'rough': (150, 255, 150), 'boundary': (255, 255, 255)}
for k, c in col.items():
    for w in O.get(k, []):
        pts = [px(p) for p in w['pts']]
        if len(pts) > 1: d.line(pts + [pts[0]], fill=c, width=2)
for h in F['holes']:
    pts = [px(p) for p in h['pts']]; d.line(pts, fill=(255, 0, 0), width=3)
    d.text((pts[0][0]+8, pts[0][1]-16), h['tags'].get('ref', '?') + ' p' + str(h['tags'].get('par')), fill=(255, 255, 255))
im.resize((1400, 1500)).save(out, quality=88)
