import os
import json, math, struct, base64, collections
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree, ConvexHull
from PIL import Image, ImageDraw
F = json.load(open('feat.json')); O = F['out']
LAT0, LON0 = 33.4995, -82.0225
ME0, MN0 = -900, -900                       # 1 m LiDAR rasters (row 0 = south)
GND = np.load('mnt.npy').astype(float); CHM = np.load('mnh.npy').astype(float); MH_, MW_ = GND.shape
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
def gz(e, n):  # LiDAR ground, bilinear
    fx = e - ME0 - .5; fy = n - MN0 - .5; i = int(fx); j = int(fy); tx = fx-i; ty = fy-j
    return (GND[j, i]*(1-tx)+GND[j, i+1]*tx)*(1-ty) + (GND[j+1, i]*(1-tx)+GND[j+1, i+1]*tx)*ty

# ---------------- features
polys = lambda k: [[w['pts']] + [r for r in w.get('inner', [])] for w in O.get(k, []) if inside_box(w['pts'], 60)]
CREEK_POLY_IDS = {'855657877', '1381013284'}     # the creek on 13 and Rae's Creek past 11/12: long, falling water, cut into pieces
water = [w for w in O['water'] if w['id'] not in CREEK_POLY_IDS and inside_box(w['pts'])]
creek_polys = []
for w in O['water']:
    if w['id'] not in CREEK_POLY_IDS: continue
    # geodesic distance from the upstream (west) end inside the polygon, binned every 12 m; each bin's hull is one piece
    pts = w['pts']; xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; e0, n0 = math.floor(min(xs))-4, math.floor(min(ys))-4
    W_, H_ = math.ceil(max(xs)-e0)+5, math.ceil(max(ys)-n0)+5
    m = raster([pts], 0, W_, H_, e0, n0)
    m0 = m.copy()
    if w['id'] == '855657877': m = ndi.binary_dilation(m, iterations=1)   # the creek on 13 is drawn as a 2-3 m sliver in pieces: joined for the walk along it, but the water keeps its own narrow width (as in life)
    seed = min(zip(*np.nonzero(m)), key=lambda c: c[1])        # westmost cell
    dist = np.full(m.shape, -1); dist[seed] = 0; q = collections.deque([seed])
    while q:
        j, i = q.popleft()
        for dj, di in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            jj, ii = j+dj, i+di
            if 0 <= jj < H_ and 0 <= ii < W_ and m[jj, ii] and dist[jj, ii] < 0: dist[jj, ii] = dist[j, i]+1; q.append((jj, ii))
    for b in range(0, dist.max()+1, 12):
        js, is_ = np.nonzero((dist >= b) & (dist < b+13) & m0)
        if len(js) < 6: continue
        P = np.c_[e0 + is_ + .5, n0 + js + .5]
        try: h = P[ConvexHull(P).vertices]
        except Exception: continue
        c = h.mean(0); h = c + (h - c)*1.0 + (h - c)/np.maximum(1e-3, np.linalg.norm(h - c, axis=1))[:, None]*.6
        creek_polys.append([[tuple(x) for x in h]])
water_m = raster([w['pts'] for w in O['water'] if inside_box(w['pts'], 900)], 2)
for w in O['streams']:      # Rae's Creek beyond the mapped water: a 4 m channel cut into ~12 m pieces
    seg = [p for p in w['pts']]
    d = [seg[0]]
    for qq in seg[1:]:
        k = max(1, int(math.dist(d[-1], qq)//4)); a = d[-1]
        for t in range(1, k+1): d.append((a[0]+(qq[0]-a[0])*t/k, a[1]+(qq[1]-a[1])*t/k))
    cur = []
    def flush(c):
        if len(c) > 1 and inside_box(c): creek_polys.append([buffer_line(c, 4.5)])
    run = 0
    for p in d:
        i, j = int(p[0]-ME0), int(p[1]-MN0)
        wet = 0 <= i < MW_ and 0 <= j < MH_ and water_m[j, i]
        if wet: flush(cur); cur = []; run = 0; continue
        if cur: run += math.dist(cur[-1], p)
        cur.append(p)
        if run >= 12: flush(cur); cur = [p]; run = 0
    flush(cur)
print('creek pieces', len(creek_polys))

# the stone bridges (OSM man_made=bridge): centre, length along the deck, width, deck bearing (deg from east), name
BR = []
for b in json.load(open('bridges.json')):
    P = np.array(ring_pts(b['pts'])); best = None
    for a in np.arange(0, 180, 1.0):
        u = np.array([math.cos(math.radians(a)), math.sin(math.radians(a))]); v = np.array([-u[1], u[0]])
        pu = P @ u; pv = P @ v; ar = (pu.max()-pu.min())*(pv.max()-pv.min())
        if best is None or ar < best[0]: best = (ar, a, pu, pv, u, v)
    ar, a, pu, pv, u, v = best; L, Wd = pu.max()-pu.min(), pv.max()-pv.min()
    if Wd > L: L, Wd, a = Wd, L, a+90
    c = u*(pu.max()+pu.min())/2 + v*(pv.max()+pv.min())/2
    BR.append([round(float(c[0]), 1), round(float(c[1]), 1), round(float(L)+1.5, 1), round(max(2.6, float(Wd)), 1), round(float(a), 1), b['name'] or ''])
BR.append([193.0, -519.8, 15.5, 3.0, 75.3, ''])   # the cart bridge right of 11 (OSM path with bridge=yes, no outline)
print('bridges', BR)
paths = [[buffer_line(w['pts'], 3.0 if w['tags'].get('golf') == 'cartpath' else 2.2)] for w in O['pathline'] if len(w['pts']) > 1 and w['tags'].get('golf') in ('cartpath', 'path') and inside_box(w['pts'], 300)]
feat = {'fair': enc_polys(polys('fair')), 'green': enc_polys(polys('green')), 'sand': enc_polys(polys('sand')), 'water': enc_polys([[w['pts']] for w in water]),
        'creek': enc_polys(creek_polys), 'path': enc_polys(paths), 'range': enc_polys(polys('range'))}
bnd = O['boundary'][0]['pts']

# ---------------- coarse terrain lattice (15 m) and the relief on top of it (2 m)
de = 15.0; e0, n0 = ME0 + 30, MN0 + 30; nx = int((MW_-60)/de)+1; ny = int((MH_-60)/de)+1
Gs = ndi.gaussian_filter(GND, 6)
zdem = [float(Gs[int(n0 + j*de - MN0), int(e0 + i*de - ME0)]) for j in range(ny) for i in range(nx)]
def demz(e, n):
    fx = (e-e0)/de; fy = (n-n0)/de; fx = min(max(fx, 0), nx-1.001); fy = min(max(fy, 0), ny-1.001); ix, iy = int(fx), int(fy); tx, ty = fx-ix, fy-iy
    z = lambda i, j: zdem[j*nx+i]
    return (z(ix, iy)*(1-tx)+z(ix+1, iy)*tx)*(1-ty) + (z(ix, iy+1)*(1-tx)+z(ix+1, iy+1)*tx)*ty
Z = np.array(zdem).reshape(ny, nx)
FX, FY = np.meshgrid((np.arange(MW_)+ME0+.5-e0)/de, (np.arange(MH_)+MN0+.5-n0)/de)
# the game draws the lattice with Catmull-Rom; cubic spline order 3 is close; residual = what the lattice cannot hold
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
play = np.zeros(rel.shape, bool)
for k in ('green', 'tee', 'sand'): play |= raster([w['pts'] for w in O.get(k, []) if inside_box(w['pts'], 60)], 2)
play |= raster([w['pts'] for w in water], 3)
play |= raster([c[0] for c in creek_polys], 3)
wt = 1 - np.clip(ndi.gaussian_filter(play.astype(float), 1.5)*1.6, 0, 1)
edge = np.ones(rel.shape); edge[:40] = edge[-40:] = 0; edge[:, :40] = edge[:, -40:] = 0; edge = ndi.gaussian_filter(edge, 10)
rel = np.clip(rel*wt*edge*ndi.gaussian_filter(raster([bnd], 60).astype(float), 8), -6.3, 6.3)
rel[np.abs(rel) < 0.08] = 0
c2 = rel[:MH_//2*2, :MW_//2*2].reshape(MH_//2, 2, MW_//2, 2).mean(axis=(1, 3))
qq = np.clip(np.round(c2*20), -127, 127).astype(int)      # 5 cm steps, one signed byte per cell; zero runs as (0, count <= 255)
out = []; zr = 0
for v in qq.ravel():
    if v == 0: zr += 1; continue
    while zr: n_ = min(zr, 255); out += [0, n_]; zr -= n_
    out.append(int(v) & 255)
while zr: n_ = min(zr, 255); out += [0, n_]; zr -= n_
D_RELIEF = {'e0': ME0, 'n0': MN0, 'res': 2, 'w': int(qq.shape[1]), 'h': int(qq.shape[0]), 'b8': 1, 'd': base64.b64encode(bytes(out)).decode()}
print('relief', c2.min(), c2.max(), 'words', len(out))

# ---------------- holes: the Masters tees (2024 scorecard, yards -> m)
YARDS = {1: 445, 2: 585, 3: 350, 4: 240, 5: 495, 6: 180, 7: 450, 8: 570, 9: 460, 10: 495, 11: 520, 12: 155, 13: 545, 14: 440, 15: 550, 16: 170, 17: 440, 18: 465}
NAMES = {}
H = sorted(F['holes'], key=lambda h: int(h['tags']['ref']))
greens = [g for g in O['green'] if inside_box(g['pts'])]; tees = [t for t in O['tee'] if inside_box(t['pts'])]
holes = []; alti = {}
for idx, h in enumerate(H):
    ref = int(h['tags']['ref']); line = [list(p) for p in h['pts']]; end = line[-1]
    gi = min(range(len(greens)), key=lambda i: math.dist(centroid(greens[i]['pts']), end)); g = greens[gi]; gc = centroid(g['pts'])
    pin = [p for p in F['pins'] if p['ref'] == str(ref)]
    line[-1] = list(gc)
    tgt = YARDS[ref]*.9144
    nxp = line[1] if len(line) > 2 else gc
    def hlen(p_): return math.dist(p_, nxp) + sum(math.dist(line[k], line[k+1]) for k in range(1, len(line)-1)) if len(line) > 2 else math.dist(p_, gc)
    b0 = math.atan2(nxp[1]-line[0][1], nxp[0]-line[0][0])
    opts = [tuple(line[0])]
    for t in tees:
        p = centroid(t['pts'])
        if math.dist(p, line[0]) > 90: continue
        if ref == 9 and not t['tags'].get('tee'): continue  # the unlabelled box in the trees SW of the 9th tee sends the drive over the 8th green
        if abs((math.degrees(math.atan2(nxp[1]-p[1], nxp[0]-p[0]) - b0) + 180) % 360 - 180) > 25: continue
        ux, uy = p[0]-nxp[0], p[1]-nxp[1]; ul = math.hypot(ux, uy) or 1; ux /= ul; uy /= ul
        dd = [((q[0]-p[0])*ux + (q[1]-p[1])*uy, q) for q in t['pts']]; dm = max(d for d, _ in dd)
        ex = [q for d, q in dd if d >= dm-3]; back = (sum(q[0] for q in ex)/len(ex) - ux*2.5, sum(q[1] for q in ex)/len(ex) - uy*2.5)
        opts += [p, back]
    tee = min(opts, key=lambda p: abs(hlen(p)-tgt)); line[0] = list(tee)
    L = sum(math.dist(line[i], line[i+1]) for i in range(len(line)-1))
    b1 = math.atan2(line[1][1]-tee[1], line[1][0]-tee[0]); dw = math.dist(tee, gc); cs = []
    for t in tees:
        p = centroid(t['pts'])
        if math.dist(p, tee) < 8 or math.dist(p, tee) > 150 or math.dist(p, gc) > dw: continue
        if abs((math.degrees(math.atan2(line[1][1]-p[1], line[1][0]-p[0]) - b1) + 180) % 360 - 180) > 30: continue
        cs.append(p)
    cs = sorted(cs, key=lambda c: -math.dist(c, gc))[:3]
    ux, uy = (gc[0]-tee[0])/dw, (gc[1]-tee[1])/dw
    while len(cs) < 3: cs.append((tee[0]+ux*(10+10*len(cs)), tee[1]+uy*(10+10*len(cs))))
    mk = {'w': [round(tee[0], 2), round(tee[1], 2)]}
    for key, c in zip('ybr', cs): mk[key] = [round(c[0], 2), round(c[1], 2)]
    lens = [round(L)] + [max(40, round(L - math.dist(tee, c))) for c in cs]
    dz = gz(*gc) - gz(*tee); par = int(h['tags']['par'])
    bits = [h['tags']['name']]
    if abs(dz) >= 3: bits.append(f"plays {abs(round(dz))} m {'uphill' if dz > 0 else 'downhill'}")
    holes.append({'par': par, 'hcp': ref, 'len': round(L), 'lens': lens, 'tee': [round(tee[0], 2), round(tee[1], 2)], 'green': [round(gc[0], 2), round(gc[1], 2)], 'line': [[round(p[0], 2), round(p[1], 2)] for p in line], 'mk': mk, 'desc': ' · '.join(bits), 'nm': h['tags']['name']})
    xs = [p[0] for p in g['pts']]; ys = [p[1] for p in g['pts']]; a0 = min(xs)-7; b0_ = min(ys)-7; s = 1.5
    gnx = int((max(xs)+7-a0)/s)+1; gny = int((max(ys)+7-b0_)/s)+1
    alti[idx] = {'e0': round(a0, 2), 'n0': round(b0_, 2), 's': s, 'nx': gnx, 'ny': gny, 'z': [round((gz(a0+i*s, b0_+j*s)-0)*100) for j in range(gny) for i in range(gnx)]}
    print(ref, par, 'len', round(L), 'target', round(tgt), lens, holes[-1]['desc'])
# extra tee boxes where the back tee has no drawn box (the game adds a plain box itself)
feat['tee'] = enc_polys([[t['pts']] for t in tees])

# ---------------- trees from the canopy height model
MH = CHM.copy()
bm = raster([w['pts'] for w in O['buildings'] if inside_box(w['pts'], 900)], 3)
MH = np.where(bm, 0, np.clip(MH, 0, 45))
Hs = ndi.gaussian_filter(MH, 1.2)
mx = ndi.maximum_filter(Hs, size=5); mn = ndi.minimum_filter(Hs, size=9)
pk = (Hs == mx) & (Hs >= 3.0) & (Hs - mn > 1.2)
js, is_ = np.nonzero(pk); trees = []
for j, i in zip(js, is_):
    hgt = float(MH[max(0, j-1):j+2, max(0, i-1):i+2].max()); half = .55*hgt; rs = []
    for k in range(8):
        a_ = k*math.pi/4; r = 1
        while r < 9:
            jj = int(round(j+math.sin(a_)*r)); ii = int(round(i+math.cos(a_)*r))
            if jj < 0 or ii < 0 or jj >= MH_ or ii >= MW_ or Hs[jj, ii] < max(2.2, half): break
            r += 1
        rs.append(r)
    d = max(3.0, min(15.0, (2*float(np.mean(rs))+0.6)*1.15)); e = ME0 + i + .5; n = MN0 + j + .5
    kind = 1 if hgt < 5 else (4 if hgt >= 17 else 0)       # 4: a loblolly pine (Augusta's tall trees), 0: hardwood, 1: shrub
    trees.append((e, n, d, kind, hgt))
rng = np.random.default_rng(7); tk = cKDTree(np.array([(t[0], t[1]) for t in trees])); fill = []
for jn in np.arange(4, MH_-4, 7.0):
    for ie in np.arange(4, MW_-4, 7.0):
        j = int(jn + rng.uniform(-3, 3)); i = int(ie + rng.uniform(-3, 3)); hh = float(Hs[j, i])
        if hh < 7.0: continue
        e = ME0 + i + .5; n = MN0 + j + .5
        if tk.query((e, n))[0] < 4.0: continue
        fill.append((e, n, 6.5 + rng.uniform(0, 4), 4 if hh >= 17 else 0, min(38.0, hh)))
trees += fill
trees = [t for t in trees if ME0 + 30 < t[0] < ME0 + MW_ - 30 and MN0 + 30 < t[1] < MN0 + MH_ - 30]
# trees on mown ground or in the chute in front of a back tee are gone since the 2018 survey (13's and 11's tees were pushed back into the woods)
mown_t = raster([w['pts'] for k in ('fair', 'green', 'tee') for w in O.get(k, []) if inside_box(w['pts'], 60)], 0)
mown_t = ndi.binary_erosion(mown_t, iterations=1)
def chute(e, n):
    for h in holes:
        t = h['tee']; nx_ = h['line'][1]; dx, dy = nx_[0]-t[0], nx_[1]-t[1]; L_ = math.hypot(dx, dy) or 1; ux, uy = dx/L_, dy/L_
        a_ = (e-t[0])*ux + (n-t[1])*uy; b_ = abs(-(e-t[0])*uy + (n-t[1])*ux)
        if -12 < a_ < 75 and b_ < 9 + .1*max(0, a_): return True
    return False
n0_ = len(trees)
trees = [t for t in trees if not mown_t[int(t[1]-MN0), int(t[0]-ME0)] and not chute(t[0], t[1])]
print('trees cleared off mown ground and tee chutes', n0_ - len(trees))
# trees the 2018 survey still has but today's aerial photo shows as open, smooth grass (cleared since: e.g. the new back tees on 11 and 13)
_GI = np.array(Image.open('course.jpg').convert('RGB')).astype(float); _GE0, _GN1 = -700, 950
def _gone(e, n, r=3):
    x = int(e - _GE0); y = int(_GN1 - n)
    if not (r <= x < _GI.shape[1]-r and r <= y < _GI.shape[0]-r): return False
    p = _GI[y-r:y+r+1, x-r:x+r+1].reshape(-1, 3); L = p.mean(1)
    return L.std() < 3.6 and (p[:, 1] - p[:, 0]).mean() > 45 and L.mean() > 70
def _near_play(e, n):
    for h in holes:
        L_ = h['line']
        for k in range(len(L_)-1):
            ax, ay = L_[k]; bx, by = L_[k+1]; dx, dy = bx-ax, by-ay; l2 = dx*dx+dy*dy or 1; u = max(0, min(1, ((e-ax)*dx+(n-ay)*dy)/l2))
            if math.hypot(e-ax-dx*u, n-ay-dy*u) < 70: return True
    return False
n1_ = len(trees)
trees = [t for t in trees if not (_near_play(t[0], t[1]) and (_gone(t[0], t[1]) or _gone(t[0], t[1], 2)))]
print('trees gone on the current aerial photo', n1_ - len(trees))
print('trees', len(trees), 'kinds', collections.Counter(t[3] for t in trees))

# ---------------- pine straw: the ground under the stands (canopy over 4 m, grown a little), not on anything mown or wet
GR = {'e0': e0 - 100, 'n0': n0 - 100, 'res': 2, 'W': math.ceil((nx*de + 200)/2), 'H': math.ceil((ny*de + 200)/2)}
can = ndi.binary_opening(ndi.gaussian_filter(MH, 1.5) > 4.0, iterations=2)
can = ndi.binary_dilation(can, iterations=2)
mown = raster([w['pts'] for k in ('fair', 'green', 'tee', 'range') for w in O.get(k, []) if inside_box(w['pts'], 900)], 3)
mown |= raster([w['pts'] for w in O['water'] if inside_box(w['pts'], 900)], 1) | raster([c[0] for c in creek_polys], 1) | raster([p[0] for p in paths], 0) | bm
inb = raster([bnd], 0)
straw = can & ~mown & inb
straw |= raster([w['pts'] for w in O.get('straw', [])], 0)
straw = ndi.binary_closing(straw, iterations=2) & ~mown
# onto the GR grid (2 m)
gi_ = ((np.arange(GR['W'])*2 + GR['e0'] + 1) - ME0).astype(int); gj_ = ((np.arange(GR['H'])*2 + GR['n0'] + 1) - MN0).astype(int)
ok_i = (gi_ >= 0) & (gi_ < MW_); ok_j = (gj_ >= 0) & (gj_ < MH_)
S2 = np.zeros((GR['H'], GR['W']), bool)
S2[np.ix_(ok_j, ok_i)] = straw[np.ix_(gj_[ok_j], gi_[ok_i])]
runs = []; flat = S2.ravel(); cur = False; cnt = 0
for v in flat:
    if v == cur: cnt += 1
    else: runs.append(cnt); cur = v; cnt = 1
runs.append(cnt)
r2 = []
for rr in runs:
    while rr > 32767: r2 += [32767, 0]; rr -= 32767
    r2.append(rr)
print('straw cells', int(S2.sum()), 'runs', len(r2))

# ---------------- azaleas (and dogwoods): along the edges of the pine straw facing the grass; dense where Augusta is famous for them
edge = straw & ~ndi.binary_erosion(straw, iterations=3)
ZONES = [((-110, 10, -585, -535), 1.0),      # behind the 12th green, under the pines across Rae's Creek
         ((-300, -60, -470, -225), .9),       # the azalea bank left of 13, along the creek, and behind the 13th green
         ((-140, 70, -520, -455), .6),        # 11 green surrounds
         ((-420, -260, -160, 40), .6),        # 15 and 16
         ((100, 290, -200, 300), .45),        # 10 and 18
         ((-200, 280, 200, 620), .35)]        # 1, 9 and the clubhouse
ej, ei = np.nonzero(edge); flw = []; rr_ = np.random.default_rng(11); taken = []
order = rr_.permutation(len(ej))
for k in order:
    e = ME0 + ei[k] + .5; n = MN0 + ej[k] + .5
    w = .07
    for (a0, a1, b0, b1), wz in ZONES:
        if a0 < e < a1 and b0 < n < b1: w = max(w, wz)
    if rr_.random() > w*.16: continue
    flw.append((e, n))
fk = cKDTree(np.array(flw)); keep = []; dead = set()
for i, p in enumerate(flw):
    if i in dead: continue
    keep.append(p); dead.update(fk.query_ball_point(p, 2.6))
# flower beds (OSM landuse=flowerbed) by the clubhouse
fl_out = []
COLS = [0, 0, 1, 1, 2, 3, 4]   # 0 pink, 1 magenta, 2 coral red, 3 white, 4 pale pink
for (e, n) in keep:
    c = COLS[int(rr_.integers(len(COLS)))]
    fl_out += [e*10, n*10, (1.1 + rr_.random()*1.3)*10, c]
# dogwoods: small white-flowering trees standing just inside the stands
dog = []
for (e, n) in keep[::7]:
    dog.append((e + rr_.uniform(-3, 3), n + rr_.uniform(-3, 3), 4.5 + rr_.random()*2, 5, 6 + rr_.random()*3))
trees += dog
print('azaleas', len(keep), 'dogwoods', len(dog))
tarr = []
for e, n, d, kind, h_ in trees: tarr += [e*10, n*10, d*10, kind*1000 + min(99.9, h_)*10]

forest = [[w['pts']] for w in O.get('forest_wood', []) if len(w['pts']) > 3 and inside_box(w['pts'], 300)]
zmin = math.floor(min(zdem))
D = {
  'name': 'Augusta National Golf Club', 'origin': [LAT0, LON0], 'mounds': [], 'bridges': BR, 'relief': D_RELIEF,
  'dem': {'e0': e0, 'n0': n0, 'de': de, 'dn': de, 'nx': nx, 'ny': ny, 'zb': float(zmin), 'data': i16([(z-zmin)*100 for z in zdem])},
  'holes': holes, 'feat': feat, 'trees': i16(tarr), 'ntrees': len(trees), 'forest': enc_polys(forest), 'orchard': enc_polys([]), 'boundary': enc_polys([[bnd]]),
  'buildings': enc_polys([[w['pts']] for w in O['buildings'] if inside_box(w['pts'], -150) and len(w['pts']) > 3]), 'cover': enc_polys([[[(ME0, MN0), (ME0+MW_, MN0), (ME0+MW_, MN0+MH_), (ME0, MN0+MH_)]]]),
  'streams': enc_lines([]), 'straw': i16(r2), 'flowers': i16(fl_out),
  'z0': 0, 'alti': alti, 'gr': GR
}
s = json.dumps(D, separators=(',', ':'))
open('rd_augusta.js', 'w').write('const RD_AUGUSTA = ' + s + ';\n')
print('size', len(s), 'zmin', zmin, max(zdem), 'gr', GR)
