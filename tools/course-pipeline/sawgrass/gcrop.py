# per green: 120 m square, north up, both photos side by side; OSM green (magenta), bunkers (orange), fairways (green), 10 m grid labelled in metres
import json
from PIL import Image, ImageDraw
from cfg import *
FT = json.load(open('features.json'))
ims = [Image.open('course_esri.jpg').convert('RGB'), Image.open('course_g.jpg').convert('RGB')]
HALF, S = 60, 3
def cen(p): return (sum(x for x, _ in p)/len(p), sum(y for _, y in p)/len(p))
for ref in range(1, 19):
    g = FT['greens'][str(ref)]; cx, cy = cen(g); cx, cy = round(cx/10)*10, round(cy/10)*10
    outs = []
    for im in ims:
        box = ((cx-HALF-E0)*2, (N0+H-(cy+HALF))*2, (cx+HALF-E0)*2, (N0+H-(cy-HALF))*2)
        c = im.crop(tuple(int(v) for v in box)).resize((2*HALF*S, 2*HALF*S)); d = ImageDraw.Draw(c)
        m2c = lambda p: ((p[0]-cx+HALF)*S, (cy+HALF-p[1])*S)
        for k in range(-HALF, HALF+1, 10):
            d.line([((k+HALF)*S, 0), ((k+HALF)*S, 4)], fill=(255, 255, 255)); d.line([(0, (k+HALF)*S), (4, (k+HALF)*S)], fill=(255, 255, 255))
            d.text(((k+HALF)*S+1, 5), str(cx+k), fill=(255, 255, 255)); d.text((6, (HALF-k)*S-5), str(cy+k), fill=(255, 255, 255))
        for f in FT['fair']: d.line([m2c(q) for q in f + [f[0]]], fill=(80, 255, 80), width=1)
        for s in FT['sand']: d.line([m2c(q) for q in s + [s[0]]], fill=(255, 140, 0), width=2)
        for gg in list(FT['greens'].values()) + FT['othergreens']: d.line([m2c(q) for q in gg + [gg[0]]], fill=(255, 0, 255), width=2)
        outs.append(c)
    w = 2*HALF*S; W2 = Image.new('RGB', (2*w+6, w), 'black'); W2.paste(outs[0], (0, 0)); W2.paste(outs[1], (w+6, 0))
    ImageDraw.Draw(W2).text((w-20, w-14), str(ref), fill=(255, 255, 0)); W2.save(f'grn/g{ref:02d}.jpg', quality=85)
