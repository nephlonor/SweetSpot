# a crop of whole holes from an aerial mosaic, the traced features drawn over it: python3 hsheet.py esri|google out.jpg 1,2,3 [bunkers.json]
import json, sys
from PIL import Image, ImageDraw, ImageEnhance
E0, N1, RES = -1000, 1110, 0.5
FT = json.load(open('features.json')); src = {'esri': 'course_esri.jpg', 'google': 'course_google.jpg'}[sys.argv[1]]; out = sys.argv[2]; refs = [int(r) for r in sys.argv[3].split(',')]
extra = json.load(open(sys.argv[4])) if len(sys.argv) > 4 else []
im = Image.open(src).convert('RGB'); tiles = []
for ref in refs:
    P = FT['lines'][str(ref)]; xs = [p[0] for p in P]; ys = [p[1] for p in P]; m = 45
    e0, e1, n0, n1 = min(xs)-m, max(xs)+m, min(ys)-m, max(ys)+m
    c = im.crop((int((e0-E0)/RES), int((N1-n1)/RES), int((e1-E0)/RES), int((N1-n0)/RES))); k = 760/max(c.size); c = c.resize((int(c.width*k), int(c.height*k))); c = ImageEnhance.Contrast(c).enhance(1.15)
    d = ImageDraw.Draw(c); s = k/RES; f = lambda q: ((q[0]-e0)*s, (n1-q[1])*s)
    def inb(p): cx = sum(q[0] for q in p)/len(p); cy = sum(q[1] for q in p)/len(p); return e0-20 < cx < e1+20 and n0-20 < cy < n1+20
    for key, col in (('fair', (255, 255, 0)), ('sand', (255, 60, 60)), ('tees', (0, 255, 255)), ('ponds', (0, 140, 255))):
        for p in FT[key]:
            if inb(p): d.polygon([f(q) for q in p], outline=col)
    for i, p in enumerate(extra):
        if inb(p): d.polygon([f(q) for q in p], outline=(255, 150, 0)); x, y = f(p[0]); d.text((x+6, y-4), str(i), fill=(255, 150, 0))
    for g in FT['greens'].values():
        if inb(g): d.polygon([f(q) for q in g], outline=(255, 0, 255))
    d.line([f(q) for q in P], fill=(255, 60, 60)); d.text((4, 4), f'{ref}  e{e0:.0f}..{e1:.0f} n{n0:.0f}..{n1:.0f}  {s:.2f}px/m', fill=(255, 255, 0))
    tiles.append(c)
W = sum(t.width for t in tiles); Hh = max(t.height for t in tiles); o = Image.new('RGB', (W, Hh)); x = 0
for t in tiles: o.paste(t, (x, 0)); x += t.width
o.save(out, quality=88); print(out, o.size)
