# Pebble Beach: sea, beach, greens, fairways, bunkers, tees, paths, buildings and boundary (metres, local grid) -> features.json
import json, math, collections, xml.etree.ElementTree as ET
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from skimage import measure
LAT0, LON0 = 36.5645, -121.9410; KX = 111320*math.cos(math.radians(LAT0)); KY = 111132.0
E0, N0, W, H = -1000, -950, 2300, 1800
F = json.load(open('feat.json')); O = F['out']
def enu(la, lo): return ((lo-LON0)*KX, (la-LAT0)*KY)
def raster(polys, grow=0, holes=()):
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    for p in polys:
        if len(p) > 2: d.polygon([(x-E0, H-(y-N0)) for x, y in p], fill=255)
    for p in holes:
        if len(p) > 2: d.polygon([(x-E0, H-(y-N0)) for x, y in p], fill=0)
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
def pip(pt, poly):
    x, y = pt; ins = False
    for i in range(len(poly)):
        a = poly[i]; b = poly[(i+1) % len(poly)]
        if (a[1] > y) != (b[1] > y) and x < (b[0]-a[0])*(y-a[1])/(b[1]-a[1]) + a[0]: ins = not ins
    return ins
bnd = O['boundary'][0]['pts']
bmask = raster([bnd], 0)
near_b = ndi.distance_transform_edt(~bmask)          # metres from the boundary (0 inside)
def nb(p): 
    i, j = int(p[0]-E0), int(p[1]-N0)
    return near_b[j, i] if 0 <= i < W and 0 <= j < H else 1e9
# ---------------- sea from the OSM coastline (sea on the right of the line), closed round the grid's south-west
r = ET.parse('r.osm').getroot()
nodes = {n.get('id'): enu(float(n.get('lat')), float(n.get('lon'))) for n in r.findall('node')}
coast = {}
for w in r.findall('way'):
    tg = {k.get('k'): k.get('v') for k in w.findall('tag')}
    if tg.get('natural') == 'coastline': coast[w.get('id')] = [x.get('ref') for x in w.findall('nd')]
big = [v for v in coast.values() if v[0] != v[-1]]; rocks = [v for v in coast.values() if v[0] == v[-1]]
segs = [[nodes[n] for n in v] for v in big]; chain = []
cur = [s for s in segs if all(math.dist(s[0], t[-1]) > .5 for t in segs if t is not s)][0]; chain = list(cur); used = {id(cur)}
while True:
    nxt = [s for s in segs if id(s) not in used and math.dist(s[0], chain[-1]) < .5]
    if not nxt: break
    chain += nxt[0][1:]; used.add(id(nxt[0]))
print('coast chain', len(chain), [round(v) for v in chain[0]], [round(v) for v in chain[-1]])
sea_poly = chain + [(chain[-1][0]+40, -2400), (-3300, -2400), (-3300, chain[0][1]+1)]
SEAM = raster([sea_poly], 0)
# rocks and islets (closed coastline rings are land, in the sea)
ROCK = raster([[nodes[n] for n in v] for v in rocks], 1)
SEAM &= ~ROCK
# ---------------- beach and bare rock from the photo: bright, pale, low-saturation ground within 60 m of the sea
im = np.asarray(Image.open('course_esri.jpg').convert('RGB'), float)
im1 = np.asarray(Image.fromarray(im.astype(np.uint8)).resize((W, H), Image.BILINEAR), float)[::-1]
mx = im1.max(-1); mn = im1.min(-1); lum = im1.mean(-1)
sat = (mx-mn)/(mx+1)
dsea = ndi.distance_transform_edt(~SEAM)
beach = (lum > 150) & (sat < .33) & (im1[..., 0] >= im1[..., 2]) & (dsea < 55) & ~SEAM
beach = ndi.binary_opening(beach, iterations=1); beach = ndi.binary_closing(beach, iterations=2)
beach = ndi.binary_fill_holes(beach)
lab, n = ndi.label(beach); sz = ndi.sum(beach, lab, range(1, n+1))
beach = np.isin(lab, [i+1 for i, s in enumerate(sz) if s > 250])
# the playing ground is never beach: bunkers and greens are drawn from OSM, the beach is only what lies outside the mown polygons
mown = raster([w['pts'] for k in ('fair', 'green', 'tee') for w in O[k]], 2)
beach &= ~mown
BEACH = poly_of(beach, 1.2, 250)
# ---------------- greens: each hole's own
KT = {1: (-763, 543), 2: (-546, 650), 3: (-22, 520), 4: (-268, 322), 5: (35, 200), 6: (279, 174), 7: (45, -253), 8: (73, -357), 9: (374, -108), 10: (681, -314), 11: (884, -738), 12: (1073, -390), 13: (891, -385), 14: (511, -160), 15: (361, 289), 16: (98, 574), 17: (-277, 291), 18: (-375, 115)}
HL = {}
for h in F['holes']:
    for ref, t in KT.items():
        if math.dist(h['pts'][0], t) < 12: HL[ref] = [list(p) for p in h['pts']]
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
mine = {id(x) for x in GREEN.values()}
gids = {g['id'] for ref in HL for g in O['green'] if g['pts'] and math.dist(cen(g['pts']), HL[ref][-1]) < 12}
OTHERG = [chaikin(g['pts'], 1) for g in O['green'] if g['id'] not in gids and nb(cen(g['pts'])) < 20]
print('practice greens inside the boundary', len(OTHERG))
FAIR = [chaikin(w['pts'], 1) for w in O['fair'] if nb(cen(w['pts'])) < 20]
SAND = [chaikin(w['pts'], 1) if len(w['pts']) < 80 else w['pts'][:-1] for w in O['sand'] if nb(cen(w['pts'])) < 25]
TEES = [w['pts'][:-1] for w in O['tee'] if nb(cen(w['pts'])) < 25]
RANGE = [w['pts'][:-1] for w in O['range'] if nb(cen(w['pts'])) < 25]
PONDS = [w['pts'][:-1] for w in O['water'] if w['tags'].get('natural') == 'water' and nb(cen(w['pts'])) < 25]
print('fair', len(FAIR), 'sand', len(SAND), 'tees', len(TEES), 'range', len(RANGE), 'ponds', len(PONDS), [ (w['id'], [round(v) for v in cen(w['pts'])]) for w in O['water']])
json.dump({'boundary': bnd[:-1], 'sea': poly_of(SEAM, 1.5, 2000), 'beach': BEACH, 'greens': {str(k): v for k, v in GREEN.items()}, 'othergreens': OTHERG, 'fair': FAIR, 'sand': SAND, 'tees': TEES,
           'range': RANGE, 'ponds': PONDS, 'lines': {str(k): v for k, v in HL.items()}}, open('features.json', 'w'))
np.save('sea.npy', SEAM); np.save('rock.npy', ROCK)
print('sea polys', len(poly_of(SEAM, 1.5, 2000)), 'beach polys', len(BEACH), 'beach m2', int(beach.sum()))
# review image
o = im1[::-1].copy()*.7
for m, c in ((SEAM, (40, 90, 200)), (beach, (255, 230, 120)), (raster(FAIR), (60, 200, 60)), (raster(SAND), (255, 255, 255)), (raster(list(GREEN.values())+OTHERG), (255, 0, 255)), (raster(TEES), (0, 255, 255))):
    mm = m[::-1]; o[mm] = o[mm]*.35 + np.array(c)*.65
Image.fromarray(o.astype(np.uint8)).resize((1150, 900)).save('/tmp/pb/prep_rev.jpg', quality=88)
