# St Patrick's Links: writes rd_head.js (the RD_STPATRICKS header for index.html) and data-stpatricks.js
import json, math, struct, base64
import numpy as np
from scipy import ndimage as ndi
from PIL import Image, ImageDraw
LAT0, LON0 = 55.1640, -7.8220
ME0, MN0 = -750, -970
GND = np.load('mnt.npy').astype(float); MH_, MW_ = GND.shape
FT = json.load(open('features.json')); HJ = json.load(open('holes.json'))
def i16(a):
    b = bytearray()
    for v in a:
        v = int(round(v)); assert -32768 <= v <= 32767, v; b += struct.pack('<h', v)
    return base64.b64encode(bytes(b)).decode()
def ring_pts(p):
    q = [tuple(x) for x in p]
    if len(q) > 1 and math.dist(q[0], q[-1]) < 0.01: q = q[:-1]
    return q
def enc_polys(polys):
    a = [len(polys)]
    for rings in polys:
        a.append(len(rings))
        for r in rings:
            r = ring_pts(r); a.append(len(r)); x = y = 0
            for (e, n) in r:
                dx = round(e*10) - x; dy = round(n*10) - y; x += dx; y += dy; a += [dx, dy]
    return i16(a)
def enc_lines(lines):
    a = [len(lines)]
    for r in lines:
        a.append(len(r)); x = y = 0
        for (e, n) in r:
            dx = round(e*10) - x; dy = round(n*10) - y; x += dx; y += dy; a += [dx, dy]
    return i16(a)
def centroid(p):
    q = ring_pts(p); A = Cx = Cy = 0
    for i in range(len(q)):
        x0, y0 = q[i]; x1, y1 = q[(i+1) % len(q)]; c = x0*y1 - x1*y0; A += c; Cx += (x0+x1)*c; Cy += (y0+y1)*c
    return (Cx/(3*A), Cy/(3*A))
def chaikin(p, k=2):
    p = [tuple(x) for x in ring_pts(p)]
    for _ in range(k):
        q = []
        for i in range(len(p)):
            a = p[i]; b = p[(i+1) % len(p)]; q += [(a[0]*.75+b[0]*.25, a[1]*.75+b[1]*.25), (a[0]*.25+b[0]*.75, a[1]*.25+b[1]*.75)]
        p = q
    return p
def raster(polys_, grow=0):
    m = Image.new('L', (MW_, MH_), 0); d = ImageDraw.Draw(m)
    for pts in polys_:
        if len(pts) > 2: d.polygon([(x-ME0, MH_-(y-MN0)) for x, y in pts], fill=255)
    a = np.array(m)[::-1, :] > 0
    return ndi.binary_dilation(a, iterations=grow) if grow else a
def gz(e, n):
    fx = e - ME0 - .5; fy = n - MN0 - .5; i = int(fx); j = int(fy); tx = fx-i; ty = fy-j
    return (GND[j, i]*(1-tx)+GND[j, i+1]*tx)*(1-ty) + (GND[j+1, i]*(1-tx)+GND[j+1, i+1]*tx)*ty
CARD = {int(k): v for k, v in HJ['card'].items()}   # par, stroke index, Sandstone, Slate, Granite, Claret (yards)
GREEN = {int(k): chaikin(v, 2) for k, v in FT['greens'].items()}
FAIR = [chaikin(p, 1) for p in FT['fair']]
# sandy tracks the bunker pass took for bunkers (checked on the photos): dropped by their centre
NOT_SAND = [(-156, -218), (-84, -320), (-94, -327)]
def _c(p): return (sum(x for x, _ in p)/len(p), sum(y for _, y in p)/len(p))
SAND = [chaikin(p, 1) for p in FT['sand'] if min(math.dist(_c(p), q) for q in NOT_SAND) > 6]
BEACH = FT['beach']; SEA = FT['sea']; PATHS = FT['path']; bnd = FT['boundary']
# the clubhouse (traced on the aerial photograph)
BUILD = [[(181.6, 104), (216.8, 137.6), (224.8, 124.8), (191.2, 92.8)]]


# ---------------- holes: tees set back along the opening line so each hole plays the Sandstone card (holes.py)
# tees where the club's plan puts them rather than at the card's length: the 14th starts from the tee beside the 13th green (the mown patch
# on the photos, where the plan's arrow starts) and plays round the dogleg along the west fairway, 318 m against 365 on the card
TEE_FWD = {}; TEE_PLAN = {14}
def _dpoly(p, poly):
    best = 1e9
    for i in range(len(poly)):
        a = poly[i]; c = poly[(i+1) % len(poly)]; dx, dy = c[0]-a[0], c[1]-a[1]; t = max(0, min(1, ((p[0]-a[0])*dx + (p[1]-a[1])*dy)/(dx*dx + dy*dy))); best = min(best, math.dist(p, (a[0]+t*dx, a[1]+t*dy)))
    return best
holes = []; alti = {}; tee_polys = []
for ref in range(1, 19):
    par, hcp, ys, ysl, ygr, ycl = CARD[ref]
    H = HJ['holes'][str(ref)]; g = GREEN[ref]; gc = centroid(g)
    line = [list(p) for p in H['line']] + [list(gc)]
    tee = line[0]; L = sum(math.dist(line[i], line[i+1]) for i in range(len(line)-1))
    ux, uy = line[1][0]-tee[0], line[1][1]-tee[1]; ul = math.hypot(ux, uy); ux /= ul; uy /= ul
    d0 = 0 if ref in TEE_PLAN else L - ys*.9144 + TEE_FWD.get(ref, 0); line[0] = tee = [tee[0]+ux*d0, tee[1]+uy*d0]   # to the card's length, along the opening line
    L = sum(math.dist(line[i], line[i+1]) for i in range(len(line)-1))
    ds = [(ys-y)*.9144 for y in (ysl, ygr, ycl)]
    cs = [(tee[0]+ux*d, tee[1]+uy*d) for d in ds]
    mk = {'w': [round(tee[0], 2), round(tee[1], 2)]}
    # (no markers for the forward tees: they have no boxes)
    lens = [round(L)] + [max(40, round(L - d)) for d in ds]
    for c in [tuple(tee)] + cs:
        # no forward tee box within 12 m of another hole's green (the 8th plays past the 7th green; its pad cut a step into the green)
        if c != tuple(tee): continue   # only the tee in play gets a box: the forward boxes broke the fairways' outlines (the cards' lengths stay in lens)
        hw, hl = 5.0, 6.0
        tee_polys.append([[(c[0]+ux*a-uy*b, c[1]+uy*a+ux*b) for a, b in ((-hl, -hw), (hl, -hw), (hl, hw), (-hl, hw))]])
    dz = gz(*gc) - gz(*tee)
    bits = []
    if abs(dz) >= 3: bits.append(f"plays {abs(round(dz))} m {'uphill' if dz > 0 else 'downhill'}")
    holes.append({'par': par, 'hcp': hcp, 'len': round(L), 'lens': lens, 'tee': [round(tee[0], 2), round(tee[1], 2)], 'green': [round(gc[0], 2), round(gc[1], 2)],
                  'line': [[round(p[0], 2), round(p[1], 2)] for p in line], 'mk': mk, 'desc': ' · '.join(bits)})
    xs = [p[0] for p in g]; ys_ = [p[1] for p in g]; a0 = min(xs)-7; b0_ = min(ys_)-7; s = 1.5
    gnx = int((max(xs)+7-a0)/s)+1; gny = int((max(ys_)+7-b0_)/s)+1
    alti[ref-1] = {'e0': round(a0, 2), 'n0': round(b0_, 2), 's': s, 'nx': gnx, 'ny': gny, 'z': [round(gz(a0+i*s, b0_+j*s)*100) for j in range(gny) for i in range(gnx)]}
    print(ref, par, 'len', round(L), 'card', round(ys*.9144), lens, holes[-1]['desc'])
# ---------------- terrain lattice (15 m) and relief (2 m): the dunes
de = 15.0; e0, n0 = ME0 + 30, MN0 + 30; nx = int((MW_-60)/de)+1; ny = int((MH_-60)/de)+1
Gs = ndi.gaussian_filter(GND, 6)
zdem = [float(Gs[int(n0 + j*de - MN0), int(e0 + i*de - ME0)]) for j in range(ny) for i in range(nx)]
Z = np.array(zdem).reshape(ny, nx)
FX, FY = np.meshgrid((np.arange(MW_)+ME0+.5-e0)/de, (np.arange(MH_)+MN0+.5-n0)/de)
def catrom(Z, FX, FY):
    ny_, nx_ = Z.shape; fx = np.clip(FX, 0, nx_-1.0001); fy = np.clip(FY, 0, ny_-1.0001); ix = fx.astype(int); iy = fy.astype(int); tx = fx-ix; ty = fy-iy
    def w(t): t2 = t*t; t3 = t2*t; return [(-t3+2*t2-t)*.5, (3*t3-5*t2+2)*.5, (-3*t3+4*t2+t)*.5, (t3-t2)*.5]
    wx = w(tx); wy = w(ty); out = 0
    for j in range(4):
        yy = np.clip(iy+j-1, 0, ny_-1); row = 0
        for i in range(4): row = row + wx[i]*Z[yy, np.clip(ix+i-1, 0, nx_-1)]
        out = out + wy[j]*row
    return out
rel = GND - catrom(Z, FX, FY)
rel = ndi.gaussian_filter(rel, 0.8)
# the dunes in more detail than the elevation model holds (Terrain 3D is smooth at the scale of a hummock):
# 1. the model's own small forms (under ~12 m) steepened: its high-pass added back, 1.4 times over
# 2. marram hummocks, the 3-12 m humps and hollows a marram dune is made of: ridged value noise at 13 m and 6 m, as high as the
#    marram is thick on the photos (image texture: dense tussocks throw speckled shadow), up to about 1.8 m
# neither on the fairways, greens, bunkers or the beach, eased in over 4-14 m from their edges
from scipy.ndimage import zoom as _zoom
_mown = raster(FAIR + list(GREEN.values()) + SAND + [t[0] for t in tee_polys], 0)
_wild = ndi.gaussian_filter(np.clip((ndi.distance_transform_edt(~_mown) - 4) / 10, 0, 1) * ~raster(BEACH + SEA, 3), 2)
# round the tees only the real ground: the added detail fades in from 15 to 40 m off each tee box, so no made-up hummock rises beside a
# tee or blocks the view off it (it did on the 4th and the 7th)
_wild *= np.clip((ndi.distance_transform_edt(~raster([t[0] for t in tee_polys], 0)) - 15) / 25, 0, 1)
_tex = np.load('tex.npy')[::-1][::2, ::2][:MH_, :MW_].astype(float)
_tex = np.clip((ndi.gaussian_filter(_tex, 3) - 5) / 10, 0, 1)
_rng = np.random.default_rng(11)
def _vnoise(wl):
    g = _rng.standard_normal((int(MH_/wl)+3, int(MW_/wl)+3))
    return _zoom(g, (MH_/(g.shape[0]-3), MW_/(g.shape[1]-3)), order=3)[:MH_, :MW_]
def _ridged(wl): n = _vnoise(wl); return 1 - np.abs(np.tanh(n))      # sharp crests, rounded hollows
hum = (.62 * (_ridged(13) - .45) + .38 * (_ridged(6) - .45)) * (.35 + .9 * _tex)
rel = rel + (1.4 * (GND - ndi.gaussian_filter(GND, 6)) + 2.2 * hum) * _wild
play = raster(list(GREEN.values()), 2) | raster([t[0] for t in tee_polys], 3) | raster(SEA, 3)   # no relief on the greens, tees or sea
wt = 1 - np.clip(ndi.gaussian_filter(play.astype(float), 1.5)*1.6, 0, 1)
# round the greens the relief fades in from 2 to 10 m off the edge: the green is shaped (and flattened) in the game, its 9 m apron blends it
# into the ground, and relief right at the edge would leave it sunk below a bank
wt *= np.clip((ndi.distance_transform_edt(~raster(list(GREEN.values()), 0)) - 2) / 8, 0, 1)
edge = np.ones(rel.shape); edge[:40] = edge[-40:] = 0; edge[:, :40] = edge[:, -40:] = 0; edge = ndi.gaussian_filter(edge, 10)
near = ndi.distance_transform_edt(~raster([bnd])) < 160   # the dunes within 160 m of the boundary; none under the sea
rel = np.clip(rel*wt*edge*ndi.gaussian_filter((near & ~raster(SEA, 2)).astype(float), 6), -6.3, 6.3)
rel[np.abs(rel) < 0.08] = 0
c2 = rel[:MH_//2*2, :MW_//2*2].reshape(MH_//2, 2, MW_//2, 2).mean(axis=(1, 3))
qq = np.clip(np.round(c2*20), -127, 127).astype(int)
out = []; zr = 0
for v in qq.ravel():
    if v == 0: zr += 1; continue
    while zr: n_ = min(zr, 255); out += [0, n_]; zr -= n_
    out.append(int(v) & 255)
while zr: n_ = min(zr, 255); out += [0, n_]; zr -= n_
D_RELIEF = {'e0': ME0, 'n0': MN0, 'res': 2, 'w': int(qq.shape[1]), 'h': int(qq.shape[0]), 'b8': 1, 'd': base64.b64encode(bytes(out)).decode()}
print('relief', c2.min(), c2.max())
# check: no hole's line passes within 25 m of another hole's green or tee (a line across a green means the routing is wrong)
def dseg(p, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]; t = max(0, min(1, ((p[0]-a[0])*dx + (p[1]-a[1])*dy)/(dx*dx + dy*dy))); return math.dist(p, (a[0]+t*dx, a[1]+t*dy))
for i, h_ in enumerate(holes):
    for j, o in enumerate(holes):
        if i != j:
            for nm in ('green', 'tee'):
                d = min(dseg(o[nm], h_['line'][k], h_['line'][k+1]) for k in range(len(h_['line'])-1))
                if d < 25: print(f'check: the line of {i+1} passes {round(d)} m from the {nm} of {j+1}')
feat = {'fair': enc_polys([[p] for p in FAIR]), 'green': enc_polys([[g] for g in GREEN.values()]), 'sand': enc_polys([[b] for b in SAND] + [[b] for b in BEACH]),
        'water': enc_polys([[w] for w in SEA]), 'creek': enc_polys([]), 'path': enc_polys([[p] for p in PATHS]), 'range': enc_polys([]), 'tee': enc_polys(tee_polys)}
zmin = math.floor(min(zdem))
GR = {'e0': e0 - 100, 'n0': n0 - 100, 'res': 2, 'W': math.ceil((nx*de + 200)/2), 'H': math.ceil((ny*de + 200)/2)}
HEAD = {'name': "St Patrick's Links", 'origin': [LAT0, LON0], 'mounds': [], 'bridges': [], 'holes': holes, 'ntrees': 0, 'z0': 0, 'gr': GR}
REST = {'relief': D_RELIEF, 'dem': {'e0': e0, 'n0': n0, 'de': de, 'dn': de, 'nx': nx, 'ny': ny, 'zb': float(zmin), 'data': i16([(z-zmin)*100 for z in zdem])},
  'feat': feat, 'trees': i16([]), 'forest': enc_polys([]), 'orchard': enc_polys([]), 'boundary': enc_polys([[bnd]]),
  'ditch': enc_lines([]), 'rail': enc_lines([]), 'buildings': enc_polys([[b] for b in BUILD]), 'cover': enc_polys([[[(ME0, MN0), (ME0+MW_, MN0), (ME0+MW_, MN0+MH_), (ME0, MN0+MH_)]]]),
  'streams': enc_lines([]), 'straw': i16([]), 'flowers': i16([]), 'alti': alti}
open('rd_head.js', 'w').write('const RD_STPATRICKS = ' + json.dumps(HEAD, separators=(',', ':')) + ';')
open('data-stpatricks.js', 'w').write('Object.assign(RD_STPATRICKS,' + json.dumps(REST, separators=(',', ':')) + ');RDS.stpatricks.alti=RD_STPATRICKS.alti;')
print({k:len(json.dumps(v)) for k,v in REST.items()}, {k:len(v) for k,v in feat.items()})
print('sizes', len(json.dumps(HEAD)), len(json.dumps(REST)), 'zmin', zmin, max(zdem))
