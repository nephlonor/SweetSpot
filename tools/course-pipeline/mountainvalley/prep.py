# Mountain Valley, The Mountain course: greens, fairways, bunkers, tees, ponds, paths, buildings and the boundary -> features.json (metres, local grid)
# OSM maps both courses; everything is assigned to the hole line nearest to it and kept if that hole is a Mountain hole.
import json, math, collections
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from skimage import measure
E0, N0, W, H = -1400, -800, 3450, 1200
F = json.load(open('feat.json')); O = F['out']
def raster(polys, grow=0):
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    for p in polys:
        if len(p) > 2: d.polygon([(x-E0, H-(y-N0)) for x, y in p], fill=255)
    a = np.array(m)[::-1, :] > 0
    return ndi.binary_dilation(a, iterations=grow) if grow else a
def poly_of(mask, tol=1.0, minA=20):
    out = []; lab, n = ndi.label(mask)
    for i in range(1, n+1):
        m = lab == i
        if m.sum() < minA: continue
        cs = measure.find_contours(np.pad(m, 1).astype(float), .5)
        c = measure.approximate_polygon(max(cs, key=len), tol)
        out.append([(round(x-1+E0, 1), round(y-1+N0, 1)) for y, x in c[:-1]])
    return out
def cen(p): return (sum(x for x, _ in p)/len(p), sum(y for _, y in p)/len(p))
def dseg(p, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]; t = max(0, min(1, ((p[0]-a[0])*dx + (p[1]-a[1])*dy)/(dx*dx + dy*dy))); return math.dist(p, (a[0]+t*dx, a[1]+t*dy))
MH = [h for h in F['holes'] if h['tags'].get('golf:course:name') == 'Mountain Course']; VH = [h for h in F['holes'] if h['tags'].get('golf:course:name') != 'Mountain Course']
def dh(p, hs): return min(dseg(p, h['pts'][i], h['pts'][i+1]) for h in hs for i in range(len(h['pts'])-1))
def mine(p): c = cen(p); return dh(c, MH) < dh(c, VH)
HL = {int(h['tags']['ref']): [list(p) for p in h['pts']] for h in MH}
def chaikin(p, k=1):
    p = [tuple(x) for x in p]
    if math.dist(p[0], p[-1]) < .01: p = p[:-1]
    for _ in range(k):
        q = []
        for i in range(len(p)):
            a = p[i]; b = p[(i+1) % len(p)]; q += [(a[0]*.75+b[0]*.25, a[1]*.75+b[1]*.25), (a[0]*.25+b[0]*.75, a[1]*.25+b[1]*.75)]
        p = q
    return p
GREEN = {}
for ref, L in HL.items():
    g = min(O['green'], key=lambda g: math.dist(cen(g['pts']), L[-1])); GREEN[ref] = chaikin(g['pts'], 1)
    print(ref, 'green', g['id'], round(math.dist(cen(g['pts']), L[-1]), 1))
gids = {id(g) for g in O['green']}
OTHERG = [chaikin(g['pts'], 1) for g in O['green'] if mine(g['pts']) and all(math.dist(cen(g['pts']), cen(v)) > 3 for v in GREEN.values())]
FAIR = [chaikin(w['pts'], 1) for w in O['fair'] if mine(w['pts'])]
SAND = [chaikin(w['pts'], 1) if len(w['pts']) < 80 else w['pts'][:-1] for w in O['sand'] if mine(w['pts'])]
TEES = [w['pts'][:-1] for w in O['tee'] if mine(w['pts'])]
PONDS = [w['pts'][:-1] for w in O['water'] if w['tags'].get('natural') == 'water' and dh(cen(w['pts']), MH) < 60 and dh(cen(w['pts']), MH) < dh(cen(w['pts']), VH)]
BLD = [w['pts'][:-1] for w in O['buildings'] if dh(cen(w['pts']), MH) < 300]
# ---------------- tees: play the card's Gold (back) tees. Each hole starts at the OSM tee box whose length is nearest the card; a hole still short is lengthened
# backward along its opening leg (a tee further back in the trees), to the card's length
GOLD = {1: 314, 2: 182, 3: 414, 4: 394, 5: 521, 6: 451, 7: 509, 8: 367, 9: 175, 10: 358, 11: 365, 12: 600, 13: 253, 14: 388, 15: 405, 16: 172, 17: 512, 18: 359}
def plen(L): return sum(math.dist(L[i], L[i+1]) for i in range(len(L)-1))
for ref, L in HL.items():
    tgt = GOLD[ref]*.9144; nxp = L[1]; b0 = math.atan2(nxp[1]-L[0][1], nxp[0]-L[0][0]); opts = [tuple(L[0])]
    for t in TEES:
        p = cen(t)
        if math.dist(p, L[0]) > 110: continue
        if abs((math.degrees(math.atan2(nxp[1]-p[1], nxp[0]-p[0]) - b0) + 180) % 360 - 180) > 30: continue
        ux, uy = p[0]-nxp[0], p[1]-nxp[1]; ul = math.hypot(ux, uy) or 1; ux /= ul; uy /= ul
        dd = [((q[0]-p[0])*ux + (q[1]-p[1])*uy, q) for q in t]; dm = max(d for d, _ in dd)
        ex = [q for d, q in dd if d >= dm-3]; opts += [p, (sum(q[0] for q in ex)/len(ex) - ux*2.5, sum(q[1] for q in ex)/len(ex) - uy*2.5)]
    def hl(p_): return math.dist(p_, nxp) + plen(L[1:])
    tee = min(opts, key=lambda p_: abs(hl(p_) - tgt)); short = tgt - hl(tee)
    if short > 1.5:
        ux, uy = tee[0]-nxp[0], tee[1]-nxp[1]; ul = math.hypot(ux, uy); ux /= ul; uy /= ul; tee = (tee[0] + ux*short, tee[1] + uy*short)
    # the tee stands on a real box when one lies within 25 m and plays within 10 m of the card (hole 12's OSM line starts at a box's edge: the tee goes to the centre of the box that plays 554 m of 549)
    best = None
    for t in TEES:
        c = cen(t)
        if math.dist(c, tee) < 25 and abs(hl(c) - tgt) <= 10 and (best is None or abs(hl(c) - tgt) < abs(hl(best) - tgt)): best = c
    if best is not None: tee = best
    L[0] = [tee[0], tee[1]]
    print(ref, 'tee', [round(v) for v in tee], 'length', round(plen(L)), 'card', round(tgt), 'extended' if short > 1.5 else '', round(max(0, short)))
# the boundary: the playing corridor, 55 m round the Mountain's holes and features, smoothed (the OSM outline holds both courses)
m = raster(FAIR + list(GREEN.values()) + OTHERG + SAND + TEES + PONDS, 0)
im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im)
for L in HL.values(): d.line([(x-E0, H-(y-N0)) for x, y in L], fill=255, width=2*55)
base = (np.array(im)[::-1] > 0) | ndi.binary_dilation(m, iterations=40)
R = 150   # the Mountain's holes lie in three groups across the property: a closing by distance joins them into one outline
dil = ndi.distance_transform_edt(~base) <= R
corr = ndi.distance_transform_edt(dil) > R - 0
corr = ndi.binary_fill_holes(corr | base)
lab, n = ndi.label(corr); corr = lab == (np.argmax(np.bincount(lab.ravel())[1:]) + 1)
BND = poly_of(ndi.binary_opening(corr, iterations=6), 3.0, 10000)[0]
json.dump({'boundary': BND, 'greens': {str(k): v for k, v in GREEN.items()}, 'othergreens': OTHERG, 'fair': FAIR, 'sand': SAND, 'tees': TEES, 'ponds': PONDS, 'lines': {str(k): v for k, v in HL.items()}, 'buildings': BLD}, open('features.json', 'w'))
print('fair', len(FAIR), 'sand', len(SAND), 'tees', len(TEES), 'ponds', len(PONDS), 'other greens', len(OTHERG), 'bnd pts', len(BND))
im0 = Image.open('course_esri.jpg').convert('RGB'); o = np.asarray(im0.resize((W, H), Image.BILINEAR), float)[::-1].copy()*.7
for mm, c in ((raster(FAIR), (60, 200, 60)), (raster(SAND), (255, 255, 255)), (raster(list(GREEN.values())+OTHERG), (255, 0, 255)), (raster(TEES), (0, 255, 255)), (raster(PONDS), (40, 90, 200))):
    q = mm[::-1]; o[q] = o[q]*.35 + np.array(c)*.65
img = Image.fromarray(o.astype(np.uint8)); dr = ImageDraw.Draw(img)
dr.line([(x-E0, H-(y-N0)) for x, y in BND + [BND[0]]], fill=(255, 255, 0), width=3)
for L in HL.values(): dr.line([(x-E0, H-(y-N0)) for x, y in L], fill=(255, 0, 0), width=3)
img.resize((W//2, H//2)).save('prep_rev.jpg', quality=88)
