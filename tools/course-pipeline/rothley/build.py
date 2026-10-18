import json, math, struct, base64, collections
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from PIL import Image, ImageDraw
F = json.load(open('feat.json')); O = F['out']
LAT0, LON0 = 52.7000, -1.1500
ME0, MN0 = -800, -900
GND = np.load('mnt.npy').astype(float); CHM = np.load('mnh.npy').astype(float); MH_, MW_ = GND.shape
GM = json.load(open('greens_manual.json')); FP = {int(k): v for k, v in json.load(open('fair_polys.json')).items()}; BK = json.load(open('bunkers_final.json')); TB = {int(k): v for k, v in json.load(open('tee_back.json')).items()}
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
    if abs(A) < 1e-6: return (sum(x for x, _ in q)/len(q), sum(y for _, y in q)/len(q))
    return (Cx/(3*A), Cy/(3*A))
def area(p):
    q = ring_pts(p); return abs(sum(q[i][0]*q[(i+1) % len(q)][1] - q[(i+1) % len(q)][0]*q[i][1] for i in range(len(q))))/2
def buffer_line(p, w):
    L = []; R = []
    for i, (x, y) in enumerate(p):
        a = p[max(0, i-1)]; b = p[min(len(p)-1, i+1)]; dx = b[0]-a[0]; dy = b[1]-a[1]; l = math.hypot(dx, dy) or 1; nx, ny = -dy/l*w/2, dx/l*w/2
        L.append((x+nx, y+ny)); R.append((x-nx, y-ny))
    return L + R[::-1]
def inside_box(p, m=0): return all(ME0 + 20 - m < q[0] < ME0 + MW_ - 20 + m and MN0 + 20 - m < q[1] < MN0 + MH_ - 20 + m for q in p)
def raster(polys_, grow=0, W=MW_, H=MH_, e0=ME0, n0=MN0, res=1.0):
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    for pts in polys_:
        if len(pts) > 2: d.polygon([((x-e0)/res, (H-(y-n0)/res)) for x, y in pts], fill=255)
    a = np.array(m)[::-1, :] > 0
    return ndi.binary_dilation(a, iterations=grow) if grow else a
def gz(e, n):
    fx = e - ME0 - .5; fy = n - MN0 - .5; i = int(fx); j = int(fy); tx = fx-i; ty = fy-j
    return (GND[j, i]*(1-tx)+GND[j, i+1]*tx)*(1-ty) + (GND[j+1, i]*(1-tx)+GND[j+1, i+1]*tx)*ty
def chaikin(p, k=2):
    p = [tuple(x) for x in ring_pts(p)]
    for _ in range(k):
        q = []
        for i in range(len(p)):
            a = p[i]; b = p[(i+1) % len(p)]; q += [(a[0]*.75+b[0]*.25, a[1]*.75+b[1]*.25), (a[0]*.25+b[0]*.75, a[1]*.25+b[1]*.75)]
        p = q
    return p
def ellipse(cx, cy, a, b, ang, n=28):
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    return [(cx + a*math.cos(t)*c - b*math.sin(t)*s, cy + a*math.cos(t)*s + b*math.sin(t)*c) for t in np.linspace(0, 2*math.pi, n, endpoint=False)]
def scale_to(p, amin):
    A = area(p)
    if A >= amin: return p
    c = centroid(p); k = math.sqrt(amin/A); return [(c[0]+(x-c[0])*k, c[1]+(y-c[1])*k) for x, y in p]

# ---------------- scorecard (white / yellow / red, yards) and stroke index
CARD = {1: (4, 12, 393, 370, 367), 2: (4, 8, 341, 315, 283), 3: (4, 4, 427, 413, 367), 4: (3, 16, 163, 140, 124), 5: (4, 18, 251, 241, 232), 6: (4, 2, 447, 430, 418),
        7: (3, 14, 149, 136, 103), 8: (4, 10, 328, 321, 275), 9: (4, 6, 457, 434, 421), 10: (4, 11, 281, 280, 237), 11: (4, 3, 393, 377, 323), 12: (3, 17, 192, 182, 147),
        13: (4, 1, 423, 404, 368), 14: (4, 5, 450, 415, 370), 15: (5, 13, 521, 491, 442), 16: (4, 7, 391, 369, 320), 17: (4, 15, 368, 341, 331), 18: (5, 9, 515, 472, 441)}

# ---------------- greens: traced from the aerial photo (greens.py); the double green of 4 and 13 and the 11th by hand
# greens: every one traced by hand on the aerial photo (gman.py); 4 and 13 share a double green
GREEN = {int(ref): chaikin(g, 2) for ref, g in GM.items()}
for k in GREEN: GREEN[k] = scale_to(GREEN[k], 260)
# ---------------- creek: Rothley Brook, a 4 m channel cut into ~12 m pieces (open ground only; under the culvert it is skipped)
creek_polys = []
for w in O['streams']:
    if w['tags'].get('tunnel'): continue
    seg = [p for p in w['pts'] if -560 < p[0] < 60 and -100 < p[1] < 600]
    if len(seg) < 2: continue
    d = [seg[0]]
    for qq in seg[1:]:
        k = max(1, int(math.dist(d[-1], qq)//4)); a = d[-1]
        for t in range(1, k+1): d.append((a[0]+(qq[0]-a[0])*t/k, a[1]+(qq[1]-a[1])*t/k))
    cur = []; run = 0
    for p in d:
        if cur: run += math.dist(cur[-1], p)
        cur.append(p)
        if run >= 12: creek_polys.append([buffer_line(cur, 4.0)]); cur = [p]; run = 0
    if len(cur) > 1: creek_polys.append([buffer_line(cur, 4.0)])
print('creek pieces', len(creek_polys))
# field ditches across play, traced on the LiDAR ground model (ditch.py): a 2.6 m channel cut into ~10 m pieces, edged in stone in the game
DITCH = [[(480,378.3),(500,360),(516.7,346.7),(538.3,330),(560,315),(580,296.7),(587.3,288.3)],                                    # across the 6th, 50 m short of the green
         [(568.3,243.3),(580,230),(595,211.7),(610,196.7),(626.7,180),(646.7,166.7),(656.7,161.7)],                                # across the 10th
         [(271.7,230),(275,196.7),(279.3,170),(283.3,130),(286.7,115),(290,83.3),(301.7,53.3),(300,36.7),(286.7,26.7),(266.7,13.3)]]  # in front of the 13th tee, past the 5th green
for dl in DITCH:
    d = [dl[0]]
    for qq in dl[1:]:
        k = max(1, int(math.dist(d[-1], qq)//3)); a = d[-1]
        for t in range(1, k+1): d.append((a[0]+(qq[0]-a[0])*t/k, a[1]+(qq[1]-a[1])*t/k))
    cur = []; run = 0
    for p in d:
        if cur: run += math.dist(cur[-1], p)
        cur.append(p)
        if run >= 10: creek_polys.append([buffer_line(cur, 2.6)]); cur = [p]; run = 0
    if len(cur) > 1: creek_polys.append([buffer_line(cur, 2.6)])
# footbridges where the holes and the paths cross the brook and the ditches: [e, n, walkway width, span, bearing of the water]
BRIDGES = [[-440.8, 98.0, 2.2, 7.0, 33], [-268.1, 351.5, 2.4, 7.0, 35], [533.9, 443.4, 3.0, 7.0, 52],
           [581.7, 298.0, 1.8, 4.5, -42], [583.3, 231.7, 1.8, 4.5, -51], [514.0, 348.8, 2.0, 4.5, -39], [534.8, 332.7, 3.0, 4.5, -38],
           [301.1, 47.8, 3.0, 4.5, -96], [279.8, 164.8, 3.0, 4.5, -84]]
EX = json.load(open('extra.json'))
RAILS = []
for w in EX['rails']:
    if w['tags'].get('usage') != 'main': continue
    seg = [p for p in w['pts'] if ME0 + 40 < p[0] < ME0 + MW_ - 40 and MN0 + 40 < p[1] < MN0 + MH_ - 40]
    # densify the long straight runs so the clip keeps the course stretch
    if len(seg) > 1: RAILS.append(seg)
print('rails', [len(r) for r in RAILS])
water = [w for w in O['water'] if not w['tags'].get('intermittent') and inside_box(w['pts'])]
paths = [[buffer_line(w['pts'], 3.0 if w['tags'].get('highway') == 'service' else 2.2)] for w in O['pathline']
         if len(w['pts']) > 1 and w['tags'].get('highway') in ('track', 'service', 'footway', 'path') and w['tags'].get('name') is None and inside_box(w['pts'], 300)
         and all(-520 < p[0] < 800 and -520 < p[1] < 580 for p in w['pts'])]
bnd = O['boundary'][0]['pts']

# ---------------- terrain lattice (15 m) and relief (2 m), as for Augusta
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
play = raster(list(GREEN.values()), 2) | raster(BK, 2) | raster([w['pts'] for w in water], 3) | raster([c[0] for c in creek_polys], 3)
wt = 1 - np.clip(ndi.gaussian_filter(play.astype(float), 1.5)*1.6, 0, 1)
edge = np.ones(rel.shape); edge[:40] = edge[-40:] = 0; edge[:, :40] = edge[:, -40:] = 0; edge = ndi.gaussian_filter(edge, 10)
rel = np.clip(rel*wt*edge*ndi.gaussian_filter(raster([bnd], 60).astype(float), 8), -6.3, 6.3)
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
print('relief', c2.min(), c2.max(), 'words', len(out))

# ---------------- holes
H = sorted(F['holes'], key=lambda h: int(h['tags']['ref']))
holes = []; alti = {}; tee_polys = []
for idx, h in enumerate(H):
    ref = int(h['tags']['ref']); par, hcp, yw, yy_, yr = CARD[ref]
    line = [list(p) for p in h['pts']]; g = GREEN[ref]; gc = centroid(g); line[-1] = list(gc)
    # the back tee: as far back as the ground allows (tees.py: open ground, clear of other greens, bunkers, fairways, water and buildings)
    t0 = line[0]; ux0, uy0 = line[1][0]-t0[0], line[1][1]-t0[1]; ul0 = math.hypot(ux0, uy0); line[0] = [t0[0]-ux0/ul0*TB[ref], t0[1]-uy0/ul0*TB[ref]]
    tee = line[0]; L = sum(math.dist(line[i], line[i+1]) for i in range(len(line)-1))
    ux, uy = line[1][0]-tee[0], line[1][1]-tee[1]; ul = math.hypot(ux, uy); ux /= ul; uy /= ul
    # the forward tees along the opening leg, set by the scorecard's differences
    dy = (yw-yy_)*.9144; dr = (yw-yr)*.9144; db = (dy+dr)/2*.6
    cs = [(tee[0]+ux*d, tee[1]+uy*d) for d in (dy, db, dr)]
    mk = {'w': [round(tee[0], 2), round(tee[1], 2)]}
    for key, c in zip('ybr', cs): mk[key] = [round(c[0], 2), round(c[1], 2)]
    lens = [round(L)] + [max(40, round(L - math.dist(tee, c))) for c in cs]
    for c in [tuple(tee)] + cs:   # a mown box at each marker, set square to the line
        hw, hl = 5.0, 6.5
        tee_polys.append([[(c[0]+ux*a-uy*b, c[1]+uy*a+ux*b) for a, b in ((-hl, -hw), (hl, -hw), (hl, hw), (-hl, hw))]])
    dz = gz(*gc) - gz(*tee)
    bits = []
    if abs(dz) >= 3: bits.append(f"plays {abs(round(dz))} m {'uphill' if dz > 0 else 'downhill'}")
    holes.append({'par': par, 'hcp': hcp, 'len': round(L), 'lens': lens, 'tee': [round(tee[0], 2), round(tee[1], 2)], 'green': [round(gc[0], 2), round(gc[1], 2)],
                  'line': [[round(p[0], 2), round(p[1], 2)] for p in line], 'mk': mk, 'desc': ' · '.join(bits)})
    xs = [p[0] for p in g]; ys = [p[1] for p in g]; a0 = min(xs)-7; b0_ = min(ys)-7; s = 1.5
    gnx = int((max(xs)+7-a0)/s)+1; gny = int((max(ys)+7-b0_)/s)+1
    alti[idx] = {'e0': round(a0, 2), 'n0': round(b0_, 2), 's': s, 'nx': gnx, 'ny': gny, 'z': [round(gz(a0+i*s, b0_+j*s)*100) for j in range(gny) for i in range(gnx)]}
    print(ref, par, 'len', round(L), 'card', round(yw*.9144), lens, holes[-1]['desc'])
# merge tee boxes that overlap (forward tees a few metres apart)
from scipy.spatial import ConvexHull as _CH
_pp = np.array(GREEN[4] + GREEN[13]); DOUBLE = [tuple(x) for x in _pp[_CH(_pp).vertices]]   # 4 and 13: one double green
GFEAT = [g for k, g in GREEN.items() if k not in (4, 13)] + [chaikin(DOUBLE, 2)]
feat = {'fair': enc_polys([[chaikin(p, 1)] for p in FP.values()]), 'green': enc_polys([[g] for g in GFEAT]), 'sand': enc_polys([[chaikin(b, 1)] for b in BK]),
        'water': enc_polys([[w['pts']] for w in water]), 'creek': enc_polys(creek_polys), 'path': enc_polys(paths), 'range': enc_polys([]), 'tee': enc_polys(tee_polys)}

# ---------------- trees from the canopy height model (oaks, ash, the hedgerows between the fields)
MH = CHM.copy()
bm = raster([w['pts'] for w in O['buildings'] if inside_box(w['pts'], 900)], 3)
MH = np.where(bm, 0, np.clip(MH, 0, 40))
Hs = ndi.gaussian_filter(MH, 1.2)
mx = ndi.maximum_filter(Hs, size=5); mn = ndi.minimum_filter(Hs, size=9)
pk = (Hs == mx) & (Hs >= 2.5) & (Hs - mn > 1.0)
js, is_ = np.nonzero(pk); trees = []
for j, i in zip(js, is_):
    hgt = float(MH[max(0, j-1):j+2, max(0, i-1):i+2].max()); half = .55*hgt; rs = []
    for k in range(8):
        a_ = k*math.pi/4; r = 1
        while r < 10:
            jj = int(round(j+math.sin(a_)*r)); ii = int(round(i+math.cos(a_)*r))
            if jj < 0 or ii < 0 or jj >= MH_ or ii >= MW_ or Hs[jj, ii] < max(2.0, half): break
            r += 1
        rs.append(r)
    d = max(3.0, min(17.0, (2*float(np.mean(rs))+0.6)*1.15)); e = ME0 + i + .5; n = MN0 + j + .5
    sl = d/max(hgt, 1)
    hr = (i * 73856093 ^ j * 19349663) % 1000 / 1000
    # 1: hedge/shrub, 2: Scots pine (tall narrow crowns, and a few of the tall trees), 6: silver birch (slender, mid-height), 0: oak, ash, beech
    kind = 1 if hgt < 4.5 else 2 if (hgt > 14 and sl < .42) or (hgt > 13 and hr < .06) else 6 if (7 < hgt < 19 and sl < .62 and hr > .62) else 0
    trees.append((e, n, d, kind, hgt))
rng = np.random.default_rng(7); tk = cKDTree(np.array([(t[0], t[1]) for t in trees])); fill = []
for jn in np.arange(4, MH_-4, 7.0):
    for ie in np.arange(4, MW_-4, 7.0):
        j = int(jn + rng.uniform(-3, 3)); i = int(ie + rng.uniform(-3, 3)); hh = float(Hs[j, i])
        if hh < 7.0: continue
        e = ME0 + i + .5; n = MN0 + j + .5
        if tk.query((e, n))[0] < 4.0: continue
        fill.append((e, n, 7 + rng.uniform(0, 4), 0, min(30.0, hh)))
trees += fill
trees = [t for t in trees if ME0 + 30 < t[0] < ME0 + MW_ - 30 and MN0 + 30 < t[1] < MN0 + MH_ - 30]
mown_t = ndi.binary_erosion(raster(list(FP.values()) + list(GREEN.values()) + [p[0] for p in tee_polys], 0), iterations=1)
n0_ = len(trees); trees = [t for t in trees if not mown_t[int(t[1]-MN0), int(t[0]-ME0)]]
# nothing stands in the water: trees on the brook, the ditches and the ponds (and a metre of bank) are left out
wet = raster([c[0] for c in creek_polys] + [w['pts'] for w in water], 1)
n2_ = len(trees); trees = [t for t in trees if not wet[int(t[1]-MN0), int(t[0]-ME0)]]
print('trees out of the water', n2_ - len(trees))
print('trees off mown ground', n0_ - len(trees), 'trees', len(trees), collections.Counter(t[3] for t in trees))
tarr = []
for e, n, d, kind, h_ in trees: tarr += [e*10, n*10, d*10, kind*1000 + min(99.9, h_)*10]
GR = {'e0': e0 - 100, 'n0': n0 - 100, 'res': 2, 'W': math.ceil((nx*de + 200)/2), 'H': math.ceil((ny*de + 200)/2)}
forest = [[w['pts']] for k in ('forest_forest', 'forest_wood') for w in O.get(k, []) if len(w['pts']) > 3 and inside_box(w['pts'], 300)]
zmin = math.floor(min(zdem))
HEAD = {'name': 'Rothley Park Golf Club', 'origin': [LAT0, LON0], 'mounds': [], 'bridges': BRIDGES, 'holes': holes, 'ntrees': len(trees), 'z0': 0, 'gr': GR}
REST = {'relief': D_RELIEF, 'dem': {'e0': e0, 'n0': n0, 'de': de, 'dn': de, 'nx': nx, 'ny': ny, 'zb': float(zmin), 'data': i16([(z-zmin)*100 for z in zdem])},
  'feat': feat, 'trees': i16(tarr), 'forest': enc_polys(forest), 'orchard': enc_polys([]), 'boundary': enc_polys([[bnd]]),
  'ditch': enc_lines(DITCH), 'rail': enc_lines(RAILS), 'buildings': enc_polys([[w['pts']] for w in O['buildings'] if inside_box(w['pts'], -150) and len(w['pts']) > 3]), 'cover': enc_polys([[[(ME0, MN0), (ME0+MW_, MN0), (ME0+MW_, MN0+MH_), (ME0, MN0+MH_)]]]),
  'streams': enc_lines([]), 'straw': i16([]), 'flowers': i16([]), 'alti': alti}
open('rd_head.js', 'w').write('const RD_ROTHLEY = ' + json.dumps(HEAD, separators=(',', ':')) + ';')
open('data-rothley.js', 'w').write('Object.assign(RD_ROTHLEY,' + json.dumps(REST, separators=(',', ':')) + ');RDS.rothley.alti=RD_ROTHLEY.alti;')
print('sizes', len(json.dumps(HEAD)), len(json.dumps(REST)), 'zmin', zmin, max(zdem))
