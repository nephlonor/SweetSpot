# per hole: the tee end, rotated so the hole plays up, both photos side by side; OSM line (red) and tee boxes (cyan), the current tee (yellow) and the OSM line start (white), 10 m ticks back from the first line point
import json, math, sys
import numpy as np
from PIL import Image, ImageDraw
from cfg import *
F = json.load(open('feat.json')); FT = json.load(open('features.json'))
osm = {int(h['tags']['ref']): h['pts'] for h in F['holes']}
ims = [Image.open('course_esri.jpg').convert('RGB'), Image.open('course_g.jpg').convert('RGB')]
def px(p): return ((p[0]-E0)*2, (N0+H-p[1])*2)
S = 3  # px per metre in the crop
for ref in range(1, 19):
    L = FT['lines'][str(ref)]; t = L[0]; nx = L[1]; a = math.atan2(nx[1]-t[1], nx[0]-t[0])
    ux, uy = math.cos(a), math.sin(a); vx, vy = -uy, ux   # up = along the hole, right = (uy,-ux)
    back, fwd, half = 140, 70, 60
    w, h = int(2*half*S), int((back+fwd)*S)
    def m2c(p):   # metres -> crop pixel
        dx, dy = p[0]-t[0], p[1]-t[1]; along = dx*ux + dy*uy; side = dx*uy - dy*ux
        return ((side+half)*S, (fwd-along)*S)
    outs = []
    for im in ims:
        # sample: for every crop pixel the photo pixel
        jj, ii = np.mgrid[0:h, 0:w]; side = ii/S - half; along = fwd - jj/S
        X = t[0] + along*ux + side*uy; Y = t[1] + along*uy - side*ux
        a_ = np.asarray(im); pxi = np.clip(((X-E0)*2).astype(int), 0, a_.shape[1]-1); pyi = np.clip(((N0+H-Y)*2).astype(int), 0, a_.shape[0]-1)
        c = Image.fromarray(a_[pyi, pxi]); d = ImageDraw.Draw(c)
        for tb in FT['tees']: d.line([m2c(q) for q in tb + [tb[0]]], fill=(0, 255, 255), width=1)
        d.line([m2c(q) for q in L[:3]], fill=(255, 0, 0), width=1)
        o0 = osm[ref][0]; x, y = m2c(o0); d.ellipse([x-4, y-4, x+4, y+4], outline=(255, 255, 255), width=2)
        x, y = m2c(t); d.ellipse([x-5, y-5, x+5, y+5], outline=(255, 255, 0), width=2)
        for k in range(0, back+1, 10):
            yy = (fwd + k)*S; d.line([(0, yy), (12 if k % 50 else 30, yy)], fill=(255, 255, 255), width=1)
            if k % 50 == 0: d.text((32, yy-6), f'-{k}', fill=(255, 255, 255))
        outs.append(c)
    W2 = Image.new('RGB', (w*2+6, h), 'black'); W2.paste(outs[0], (0, 0)); W2.paste(outs[1], (w+6, 0))
    ImageDraw.Draw(W2).text((4, 4), f'{ref}', fill=(255, 255, 0))
    W2.save(f'tee/t{ref:02d}.jpg', quality=85)
