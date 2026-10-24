# bunkers: light, low-saturation blobs 8-450 m2, not too elongated, ringed by green grass, within 22 m of a fairway or green; run on both photos, kept where both agree
import json, math, sys, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
import skimage.measure as sm
E0, N1, RES = -1000, 1110, 0.5
F = json.load(open('feat.json')); FT = json.load(open('features.json'))
FP = FT['fair'] + list(FT['greens'].values())
def run(src, thr):
    I = np.array(Image.open(src).convert('RGB')).astype(float); Hh, Ww = I.shape[:2]
    R, G, B = I[..., 0], I[..., 1], I[..., 2]; L = I.mean(2)
    sand = (L > thr) & (B > 95) & (R > G - 28) & ((G - B) < 60) & (I.max(2) - I.min(2) < 80)
    sand = ndi.binary_opening(sand, iterations=1); sand = ndi.binary_closing(sand, iterations=2); sand = ndi.binary_fill_holes(sand)
    m = Image.new('L', (Ww, Hh), 0); d = ImageDraw.Draw(m)
    for p in FP: d.polygon([((x-E0)/RES, (N1-y)/RES) for x, y in p], fill=255)
    near = ndi.binary_dilation(np.array(m) > 0, iterations=int(22/RES))
    pm = Image.new('L', (Ww, Hh), 0); d = ImageDraw.Draw(pm)
    for w in F['out']['pathline']: d.line([((x-E0)/RES, (N1-y)/RES) for x, y in w['pts']], fill=255, width=10)
    for w in F['out']['buildings']: d.polygon([((x-E0)/RES, (N1-y)/RES) for x, y in w['pts']], fill=255)
    bad = ndi.binary_dilation(np.array(pm) > 0, iterations=4)
    lab, n = ndi.label(sand & near); out = []
    for k, sl in enumerate(ndi.find_objects(lab), 1):
        c = lab[sl] == k; A = c.sum()*RES*RES
        if A < 8 or A > 450: continue
        js, is_ = np.nonzero(c); js = js+sl[0].start; is_ = is_+sl[1].start
        if bad[js, is_].mean() > .3: continue
        P = np.c_[E0+(is_+.5)*RES, N1-(js+.5)*RES]; ev = np.linalg.eigvalsh(np.cov(P.T))
        if math.sqrt(ev[1]/max(ev[0], 1e-6)) > 3.2: continue
        y0, x0 = max(0, sl[0].start-8), max(0, sl[1].start-8); sub = I[y0:sl[0].stop+8, x0:sl[1].stop+8]
        cc = np.zeros(sub.shape[:2], bool); cc[sl[0].start-y0:sl[0].start-y0+c.shape[0], sl[1].start-x0:sl[1].start-x0+c.shape[1]] = c
        rg = ndi.binary_dilation(cc, iterations=6) & ~ndi.binary_dilation(cc, iterations=2); q = sub[rg]; gr = q[:, 1]-(q[:, 0]+q[:, 2])/2
        if np.mean(gr > 8) < .55: continue
        ring = max(sm.find_contours(np.pad(c, 2).astype(float), .5), key=len); ring = sm.approximate_polygon(ring, .8)
        out.append([[E0+(sl[1].start+x-2+.5)*RES, N1-(sl[0].start+y-2+.5)*RES] for y, x in ring])
    return out
A = run('course_esri.jpg', 150); Bg = run('course_google.jpg', 150)
cen = lambda p: (sum(q[0] for q in p)/len(p), sum(q[1] for q in p)/len(p))
both = [a for a in A if any(math.dist(cen(a), cen(b)) < 7 for b in Bg)]
print('esri', len(A), 'google', len(Bg), 'both', len(both))
json.dump(both, open('bunkers.json', 'w')); json.dump({'esri': A, 'google': Bg}, open('bunkers_all.json', 'w'))
