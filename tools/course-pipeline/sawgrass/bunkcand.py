# sand candidates missing from OSM: bright, low-saturation blobs in BOTH photos, 6-400 m2, compact, within 25 m of a fairway or green, not on an OSM bunker, path or building
import json, math
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from cfg import *
FT = json.load(open('features.json')); F = json.load(open('feat.json'))
def mask(polys, grow=0, sc=2):
    m = Image.new('L', (W*sc, H*sc), 0); d = ImageDraw.Draw(m)
    for p in polys:
        if len(p) > 2: d.polygon([((x-E0)*sc, (N0+H-y)*sc) for x, y in p], fill=255)
    a = np.array(m) > 0
    return ndi.binary_dilation(a, iterations=grow) if grow else a
def sandish(fn):
    a = np.asarray(Image.open(fn).convert('RGB'), float); r, g, b = a[..., 0], a[..., 1], a[..., 2]; mx = a.max(2); mn = a.min(2); v = a.mean(2)
    sat = (mx-mn)/np.maximum(mx, 1)
    return (v > 165) & (sat < .28) & (r >= b)
m = sandish('course_esri.jpg') & ndi.binary_dilation(sandish('course_g.jpg'), iterations=3)
m = ndi.binary_opening(m, iterations=1)
pathl = [w['pts'] for w in F['out']['pathline']]
pm = Image.new('L', (W*2, H*2), 0); d = ImageDraw.Draw(pm)
for p in pathl: d.line([((x-E0)*2, (N0+H-y)*2) for x, y in p], fill=255, width=14)
excl = mask(FT['sand'], 4) | (np.array(pm) > 0) | mask(FT['buildings'], 10) | mask(FT['ponds'], 2)
near = mask(FT['fair'] + list(FT['greens'].values()), 50)
lab, n = ndi.label(m); out = []
for i, sl in enumerate(ndi.find_objects(lab), 1):
    blob = lab[sl] == i; A = blob.sum()/4
    if not (6 <= A <= 400): continue
    hh, ww = blob.shape; el = max(hh, ww)**2/4/max(A, 1)
    if el > 4: continue
    if (excl[sl] & blob).mean() > .1 or not (near[sl] & blob).any(): continue
    jj, ii = np.nonzero(blob); cy = sl[0].start + jj.mean(); cx = sl[1].start + ii.mean()
    out.append((round(cx/2+E0, 1), round(N0+H-cy/2, 1), round(A)))
print(len(out)); json.dump(out, open('bunkcand.json', 'w'))
for o in out: print(o)
