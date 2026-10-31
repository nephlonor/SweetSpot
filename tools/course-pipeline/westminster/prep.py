# OSM course features -> features.json (metres, local grid): greens, fairways, bunkers, tees, ponds, streams, buildings, the boundary,
# and each hole's line with its back tee set to the scorecard's length. Shared by Westminster National and Landmand (their cfg.py differs).
import json, math, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from skimage import measure
from cfg import *
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
    dx, dy = b[0]-a[0], b[1]-a[1]; t = max(0, min(1, ((p[0]-a[0])*dx + (p[1]-a[1])*dy)/(dx*dx + dy*dy or 1))); return math.dist(p, (a[0]+t*dx, a[1]+t*dy))
HL = {int(h['tags']['ref']): [list(p) for p in h['pts']] for h in F['holes']}
def dh(p): return min(dseg(p, L[i], L[i+1]) for L in HL.values() for i in range(len(L)-1))
def near(p, r): return dh(cen(p)) < r
def chaikin(p, k=1):
    p = [tuple(x) for x in p]
    if math.dist(p[0], p[-1]) < .01: p = p[:-1]
    for _ in range(k):
        q = []
        for i in range(len(p)):
            a = p[i]; b = p[(i+1) % len(p)]; q += [(a[0]*.75+b[0]*.25, a[1]*.75+b[1]*.25), (a[0]*.25+b[0]*.75, a[1]*.25+b[1]*.75)]
        p = q
    return p
GREEN = {}; gid = set()
for ref, L in HL.items():
    g = min(O['green'], key=lambda g: math.dist(cen(g['pts']), L[-1])); GREEN[ref] = chaikin(g['pts'], 1); gid.add(g['id'])
    print(ref, 'green', g['id'], 'off the line end', round(math.dist(cen(g['pts']), L[-1]), 1))
OTHERG = [chaikin(g['pts'], 1) for g in O['green'] if g['id'] not in gid and near(g['pts'], 120)]
FAIR = [chaikin(w['pts'], 1) for w in O['fair'] if near(w['pts'], 120)]
SAND = [chaikin(w['pts'], 1) if len(w['pts']) < 80 else w['pts'][:-1] for w in O['sand'] if near(w['pts'], 90)]
TEES = [w['pts'][:-1] for w in O['tee'] if near(w['pts'], 90)]
PONDS = [w['pts'][:-1] for w in O['water'] if w['tags'].get('natural') == 'water' and w['tags'].get('intermittent') != 'yes' and w['tags'].get('water') != 'stream' and near(w['pts'], 150)]
STREAMS = [w['pts'] for w in O['streams'] if w['tags'].get('tunnel') is None and len(w['pts']) > 1]
BLD = [w['pts'][:-1] for w in O['buildings'] if dh(cen(w['pts'])) < 300]
# ---------------- tees: play the card's back tees. The hole starts at the OSM tee box nearest the card's length; a hole still short goes back along its opening leg
def plen(L): return sum(math.dist(L[i], L[i+1]) for i in range(len(L)-1))
TEE_BOX = globals().get('TEE_BOX', {})
for ref, L in HL.items():
    tgt = CARD[ref][2]*.9144; nxp = L[1]; b0 = math.atan2(nxp[1]-L[0][1], nxp[0]-L[0][0]); opts = [tuple(L[0])]
    for t in TEES:
        p = cen(t)
        if math.dist(p, L[0]) > 110: continue
        if abs((math.degrees(math.atan2(nxp[1]-p[1], nxp[0]-p[0]) - b0) + 180) % 360 - 180) > 30: continue
        ux, uy = p[0]-nxp[0], p[1]-nxp[1]; ul = math.hypot(ux, uy) or 1; ux /= ul; uy /= ul
        dd = [((q[0]-p[0])*ux + (q[1]-p[1])*uy, q) for q in t]; dm = max(d for d, _ in dd)
        ex = [q for d, q in dd if d >= dm-3]; opts += [p, (sum(q[0] for q in ex)/len(ex) - ux*2.5, sum(q[1] for q in ex)/len(ex) - uy*2.5)]
    def hl(p_): return math.dist(p_, nxp) + plen(L[1:])
    tee = TEE_BOX.get(ref) or min(opts, key=lambda p_: abs(hl(p_) - tgt))
    if ref not in TEE_BOX and hl(tee) - tgt > 10:   # no box plays within 10 m of the card: from the longest box short of it, back along the opening leg
        sh = [p_ for p_ in opts if hl(p_) <= tgt]
        if sh: tee = max(sh, key=hl)
    short = tgt - hl(tee)
    if short > 1.5:
        ux, uy = tee[0]-nxp[0], tee[1]-nxp[1]; ul = math.hypot(ux, uy); ux /= ul; uy /= ul; tee = (tee[0] + ux*short, tee[1] + uy*short)
    L[0] = [tee[0], tee[1]]
    print(ref, 'par', CARD[ref][0], 'tee', [round(v) for v in tee], 'length', round(plen(L)), 'card', round(tgt), 'extended %d m' % round(short) if short > 1.5 else '')
# ---------------- the boundary: the club's OSM outline, cut down to the playing corridor (55 m round the holes and their features, joined across gaps up to 150 m)
m = raster(FAIR + list(GREEN.values()) + OTHERG + SAND + TEES + PONDS, 0)
im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im)
for L in HL.values(): d.line([(x-E0, H-(y-N0)) for x, y in L], fill=255, width=2*55)
base = (np.array(im)[::-1] > 0) | ndi.binary_dilation(m, iterations=40)
R = 150
dil = ndi.distance_transform_edt(~base) <= R
corr = ndi.binary_fill_holes((ndi.distance_transform_edt(dil) > R) | base)
osm_b = raster([O['boundary'][0]['pts']], 25) if O.get('boundary') else np.ones_like(corr)
corr &= osm_b
edge = np.zeros_like(corr); edge[30:-30, 30:-30] = True; corr &= edge
lab, n = ndi.label(corr); corr = lab == (np.argmax(np.bincount(lab.ravel())[1:]) + 1)
BND = poly_of(ndi.binary_opening(corr, iterations=6), 3.0, 10000)[0]
bm = raster([BND])
def inb(p): i, j = int(p[0]-E0), int(p[1]-N0); return 0 <= i < W and 0 <= j < H and bm[j, i]
for ref, L in HL.items():
    if not inb(L[0]): print('!! hole', ref, 'tee outside the boundary')
STREAMS = [[p for p in s if inb(p) or True] for s in STREAMS if any(inb(p) for p in s)]
json.dump({'boundary': BND, 'greens': {str(k): v for k, v in GREEN.items()}, 'othergreens': OTHERG, 'fair': FAIR, 'sand': SAND, 'tees': TEES, 'ponds': PONDS, 'streams': STREAMS,
           'lines': {str(k): v for k, v in HL.items()}, 'buildings': BLD}, open('features.json', 'w'))
print('fair', len(FAIR), 'sand', len(SAND), 'tees', len(TEES), 'ponds', len(PONDS), 'streams', len(STREAMS), 'other greens', len(OTHERG), 'buildings', len(BLD), 'bnd pts', len(BND))
print('total', round(sum(plen(L) for L in HL.values())), 'card', round(sum(v[2] for v in CARD.values())*.9144))
# ---------------- review image
im0 = Image.open('course_esri.jpg').convert('RGB'); o = np.asarray(im0.resize((W, H), Image.BILINEAR), float)[::-1].copy()*.7
for mm, c in ((raster(FAIR), (60, 200, 60)), (raster(SAND), (255, 255, 255)), (raster(list(GREEN.values())+OTHERG), (255, 0, 255)), (raster(TEES), (0, 255, 255)), (raster(PONDS), (40, 90, 200))):
    q = mm[::-1]; o[q] = o[q]*.35 + np.array(c)*.65
img = Image.fromarray(o.astype(np.uint8)); dr = ImageDraw.Draw(img)
dr.line([(x-E0, H-(y-N0)) for x, y in BND + [BND[0]]], fill=(255, 255, 0), width=3)
for s in STREAMS: dr.line([(x-E0, H-(y-N0)) for x, y in s], fill=(0, 120, 255), width=3)
for ref, L in HL.items():
    dr.line([(x-E0, H-(y-N0)) for x, y in L], fill=(255, 0, 0), width=3); dr.text((L[0][0]-E0+4, H-(L[0][1]-N0)), str(ref), fill=(255, 255, 0))
img.save('prep_rev.jpg', quality=85)
