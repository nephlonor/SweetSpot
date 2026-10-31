# Westminster National / Landmand (cfg.py says which): writes rd_head.js (the RD_<KEY> header for index.html) and data-<key>.js
import json, math, struct, base64, collections
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from PIL import Image, ImageDraw
from cfg import *
ME0, MN0 = E0, N0
F = json.load(open('feat.json')); O = F['out']; FT = json.load(open('features.json'))
GND = np.load('mnt.npy').astype(float); CHM = np.load('mnh.npy').astype(float); MH_, MW_ = GND.shape
SEAM = np.zeros(GND.shape, bool); ROCKM = np.zeros(GND.shape, bool)   # (no sea here)
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
def raster(polys_, grow=0):
    m = Image.new('L', (MW_, MH_), 0); d = ImageDraw.Draw(m)
    for pts in polys_:
        if len(pts) > 2: d.polygon([(x-ME0, MH_-(y-MN0)) for x, y in pts], fill=255)
    a = np.array(m)[::-1, :] > 0
    return ndi.binary_dilation(a, iterations=grow) if grow else a
Z0 = int(round(float(np.median(GND)) / 10) * 10)   # heights in the data are stored relative to this
def gz(e, n):
    fx = e - ME0 - .5; fy = n - MN0 - .5; i = int(fx); j = int(fy); tx = fx-i; ty = fy-j
    return (GND[j, i]*(1-tx)+GND[j, i+1]*tx)*(1-ty) + (GND[j+1, i]*(1-tx)+GND[j+1, i+1]*tx)*ty
bnd = FT['boundary']
GREEN = {int(k): v for k, v in FT['greens'].items()}; OTHERG = FT['othergreens']
FAIR = FT['fair']; SAND = FT['sand']; TEES = FT['tees']; BEACH = []; SEA = []; PONDS = FT['ponds']
# practice green and the like inside the boundary also drawn
ALLG = list(GREEN.values()) + OTHERG
_inb = raster([bnd], 0)
def _inside(p): return all(0 <= int(q[0]-ME0) < MW_ and 0 <= int(q[1]-MN0) < MH_ and _inb[int(q[1]-MN0), int(q[0]-ME0)] for q in p[::max(1, len(p)//6)])
paths = [buffer_line(w['pts'], 3.0 if w['tags'].get('highway') == 'service' else 2.0) for w in O['pathline'] if len(w['pts']) > 1 and (w['tags'].get('highway') in ('service', 'footway', 'track', 'path') or w['tags'].get('golf') in ('cartpath', 'path')) and inside_box(w['pts'], 0) and _inside(w['pts'])]
print('paths', len(paths))
# bunker rims on the cliffs: the waste areas are large; the sea wins where they meet
SANDP = [s for s in SAND]
creek_polys = []
_bm = raster([bnd], 0)
for s_ in FT.get('streams', []):
    cur = []; run = 0
    for k_, p in enumerate(s_):
        i_, j_ = int(p[0]-ME0), int(p[1]-MN0)
        ok = 0 <= i_ < MW_ and 0 <= j_ < MH_ and _bm[j_, i_]
        if not ok:
            if len(cur) > 1: creek_polys.append([buffer_line(cur, 4.0)])
            cur = []; run = 0; continue
        if cur: run += math.dist(cur[-1], p)
        cur.append(p)
        if run >= 12: creek_polys.append([buffer_line(cur, 4.0)]); cur = [p]; run = 0
    if len(cur) > 1: creek_polys.append([buffer_line(cur, 4.0)])
print('creek pieces', len(creek_polys))
feat = {'fair': enc_polys([[p] for p in FAIR]), 'green': enc_polys([[g] for g in ALLG]), 'sand': enc_polys([[b] for b in SANDP] + [[b] for b in BEACH]),
        'water': enc_polys([[w] for w in PONDS] + [[w] for w in SEA]), 'creek': enc_polys(creek_polys), 'path': enc_polys([[p] for p in paths]), 'range': enc_polys([])}
# ---------------- coarse terrain lattice (15 m) and relief (2 m)
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
play = raster(ALLG + TEES + SAND, 2) | raster(PONDS, 3) | raster(SEA, 2) | raster([c[0] for c in creek_polys], 3)
wt = 1 - np.clip(ndi.gaussian_filter(play.astype(float), 1.5)*1.6, 0, 1)
wt *= np.clip((ndi.distance_transform_edt(~raster(ALLG, 0)) - 2) / 8, 0, 1)
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
# ---------------- holes: the Blue tees (scorecard yards -> m); the line is OSM's own, ending at the traced green's centre
# the card (cfg.py): par, stroke index, then the yards from each tee, back to front. The game plays the back tees
HLINES = {int(k): v for k, v in FT['lines'].items()}
tee_polys = [t for t in TEES]
holes = []; alti = {}
for ref in range(1, 19):
    par, hcp, yb, *yfwd = CARD[ref]
    g = GREEN[ref]; gc = centroid(g); line = [list(p) for p in HLINES[ref]]; line[-1] = list(gc)
    tgt = yb*.9144
    nxp = line[1]
    def hlen(p_): return math.dist(p_, nxp) + sum(math.dist(line[k], line[k+1]) for k in range(1, len(line)-1))
    b0 = math.atan2(nxp[1]-line[0][1], nxp[0]-line[0][0])
    opts = [tuple(line[0])]
    for t in []:  # (the tee was placed by prep.py)
        p = centroid(t)
        if math.dist(p, line[0]) > 90: continue
        if abs((math.degrees(math.atan2(nxp[1]-p[1], nxp[0]-p[0]) - b0) + 180) % 360 - 180) > 25: continue
        ux, uy = p[0]-nxp[0], p[1]-nxp[1]; ul = math.hypot(ux, uy) or 1; ux /= ul; uy /= ul
        dd = [((q[0]-p[0])*ux + (q[1]-p[1])*uy, q) for q in t]; dm = max(d for d, _ in dd)
        ex = [q for d, q in dd if d >= dm-3]; back = (sum(q[0] for q in ex)/len(ex) - ux*2.5, sum(q[1] for q in ex)/len(ex) - uy*2.5)
        opts += [p, back]
    tee = min(opts, key=lambda p: abs(hlen(p)-tgt)); line[0] = list(tee)
    L = sum(math.dist(line[i], line[i+1]) for i in range(len(line)-1))
    ux, uy = line[1][0]-tee[0], line[1][1]-tee[1]; ul = math.hypot(ux, uy); ux /= ul; uy /= ul
    ds = [(yb-y)*.9144 for y in yfwd]
    cs = [(tee[0]+ux*d, tee[1]+uy*d) for d in ds]
    lens = [round(L)] + [max(40, round(L - d)) for d in ds]
    mk = {'w': [round(tee[0], 2), round(tee[1], 2)]}
    dz = gz(*gc) - gz(*tee); bits = []
    if abs(dz) >= 3: bits.append(f"plays {abs(round(dz))} m {'uphill' if dz > 0 else 'downhill'}")
    holes.append({'par': par, 'hcp': hcp, 'len': round(L), 'lens': lens, 'tee': [round(tee[0], 2), round(tee[1], 2)], 'green': [round(gc[0], 2), round(gc[1], 2)],
                  'line': [[round(p[0], 2), round(p[1], 2)] for p in line], 'mk': mk, 'desc': ' · '.join(bits)})
    xs = [p[0] for p in g]; ys_ = [p[1] for p in g]; a0 = min(xs)-7; b0_ = min(ys_)-7; s = 1.5
    gnx = int((max(xs)+7-a0)/s)+1; gny = int((max(ys_)+7-b0_)/s)+1
    alti[ref-1] = {'e0': round(a0, 2), 'n0': round(b0_, 2), 's': s, 'nx': gnx, 'ny': gny, 'z': [round((gz(a0+i*s, b0_+j*s) - Z0)*100) for j in range(gny) for i in range(gnx)]}
    print(ref, par, 'len', round(L), 'card', round(tgt), lens, holes[-1]['desc'])
print('total', sum(h['len'] for h in holes), 'card', round(sum(CARD[r][2] for r in CARD)*.9144))
feat['tee'] = enc_polys([[t] for t in tee_polys])
# ---------------- trees from the canopy height model: Monterey cypress (7), Monterey pine (8), coast live oak (0), scrub (1)
MH = CHM.copy()
BLD = [b for b in FT['buildings'] if len(b) > 3 and inside_box(b, -40)]
bm = raster(BLD, 3)
MH = np.where(bm, 0, np.clip(MH, 0, 45)); MH[SEAM | ROCKM] = 0
def _vn(wl, seed):
    r_ = np.random.default_rng(seed); g_ = r_.standard_normal((int(MH_/wl)+3, int(MW_/wl)+3))
    from scipy.ndimage import zoom as _z
    return _z(g_, (MH_/(g_.shape[0]-3), MW_/(g_.shape[1]-3)), order=3)[:MH_, :MW_]
_n = ndi.gaussian_filter(_vn(60, 5), 1.5); STAND = 1/(1+np.exp(-(_n/ _n.std() - .7)*4))   # conifer stands, patches 60-120 m across
Hs = ndi.gaussian_filter(MH, 1.2)
mx = ndi.maximum_filter(Hs, size=5); mn = ndi.minimum_filter(Hs, size=9)
pk = (Hs == mx) & (Hs >= 2.5) & (Hs - mn > 1.0)
js, is_ = np.nonzero(pk); trees = []
def kind_of(hgt, e_, n_, j, i):
    if KEY == 'westminster':
        # Maryland Piedmont: tulip poplar, red and white oak, red maple, sweetgum, black walnut (0); eastern red cedar and Virginia pine in the old fence rows (2); hedges (1)
        if hgt < 4.5: return 1
        if hgt < 16 and STAND[j, i] > .55: return 2
        return 0
    # the Loess Hills: eastern red cedar spreading over the bluffs (2, short and narrow), bur oak on the ridges and cottonwood by the water (0), sumac and dogwood thickets (1)
    if hgt < 3.5: return 1
    if hgt < 11 and (STAND[j, i] > .35 or hgt < 7): return 2
    return 0
for j, i in zip(js, is_):
    hgt = float(MH[max(0, j-1):j+2, max(0, i-1):i+2].max()); half = .55*hgt; rs = []
    for k in range(8):
        a_ = k*math.pi/4; r = 1
        while r < 10:
            jj = int(round(j+math.sin(a_)*r)); ii = int(round(i+math.cos(a_)*r))
            if jj < 0 or ii < 0 or jj >= MH_ or ii >= MW_ or Hs[jj, ii] < max(2.0, half): break
            r += 1
        rs.append(r)
    d = max(3.0, min(16.0, (2*float(np.mean(rs))+0.6)*1.15)); e = ME0 + i + .5; n = MN0 + j + .5
    trees.append((e, n, d, kind_of(hgt, e, n, j, i), hgt))
rng = np.random.default_rng(7); tk = cKDTree(np.array([(t[0], t[1]) for t in trees])); fill = []
for jn in np.arange(4, MH_-4, 7.0):
    for ie in np.arange(4, MW_-4, 7.0):
        j = int(jn + rng.uniform(-3, 3)); i = int(ie + rng.uniform(-3, 3)); hh = float(Hs[j, i])
        if hh < 7.0: continue
        e = ME0 + i + .5; n = MN0 + j + .5
        if tk.query((e, n))[0] < 4.0: continue
        fill.append((e, n, 6.5 + rng.uniform(0, 4), kind_of(hh, e, n, j, i), min(38.0, hh)))
trees += fill
trees = [t for t in trees if ME0 + 30 < t[0] < ME0 + MW_ - 30 and MN0 + 30 < t[1] < MN0 + MH_ - 30]
mown_t = ndi.binary_erosion(raster(FAIR + ALLG + TEES, 0), iterations=1)
def chute(e, n):
    for h in holes:
        t = h['tee']; nx_ = h['line'][1]; dx, dy = nx_[0]-t[0], nx_[1]-t[1]; L_ = math.hypot(dx, dy) or 1; ux, uy = dx/L_, dy/L_
        a_ = (e-t[0])*ux + (n-t[1])*uy; b_ = abs(-(e-t[0])*uy + (n-t[1])*ux)
        if -12 < a_ < 75 and b_ < 9 + .1*max(0, a_): return True
    return False
wet = raster(PONDS + [c[0] for c in creek_polys], 1) | ndi.binary_dilation(SEAM, iterations=2)
n0_ = len(trees)
trees = [t for t in trees if not mown_t[int(t[1]-MN0), int(t[0]-ME0)] and not chute(t[0], t[1]) and not wet[int(t[1]-MN0), int(t[0]-ME0)]]
print('trees cleared off mown ground, tee chutes and water', n0_ - len(trees))
print('trees', len(trees), 'kinds', collections.Counter(t[3] for t in trees))
# ---------------- wildflowers (goldenrod, asters, Queen Anne's lace) in the rough along the edges of the mown ground, and in the old fields
GR = {'e0': e0 - 100, 'n0': n0 - 100, 'res': 2, 'W': math.ceil((nx*de + 200)/2), 'H': math.ceil((ny*de + 200)/2)}
mown = raster(FAIR + ALLG + TEES + SAND + paths, 3) | wet
inb = raster([bnd], 0)
dmown = ndi.distance_transform_edt(~mown)
band = (dmown > 5) & (dmown < 26) & ~mown & (MH < 2.5) & inb
rr_ = np.random.default_rng(11); jj, ii = np.nonzero(band); keep = []
for k in rr_.permutation(len(jj))[:80000]:
    if rr_.random() > .05: continue
    keep.append((ME0 + ii[k] + .5, MN0 + jj[k] + .5))
fk = cKDTree(np.array(keep)); dead = set(); fl = []
for i, p in enumerate(keep):
    if i in dead: continue
    fl.append(p); dead.update(fk.query_ball_point(p, 2.6))
fl_out = []; COLS = [0, 0, 0, 1, 1, 2, 3]       # (index into the course's own late-flower table in index.html)
for (e, n) in fl: fl_out += [e*10, n*10, (.9 + rr_.random()*1.1)*10, COLS[int(rr_.integers(len(COLS)))]]
print('wildflower patches', len(fl))
tarr = []
for e, n, d, kind, h_ in trees: tarr += [e*10, n*10, d*10, kind*1000 + min(99.9, h_)*10]
forest = [[w['pts']] for w in O.get('forest_wood', []) if len(w['pts']) > 3 and inside_box(w['pts'], 300)]
zmin = math.floor(min(zdem))
HEAD = {'name': NAME, 'origin': [LAT0, LON0], 'mounds': [], 'bridges': [], 'holes': holes, 'ntrees': len(trees), 'z0': Z0, 'gr': GR}
REST = {'relief': D_RELIEF, 'dem': {'e0': e0, 'n0': n0, 'de': de, 'dn': de, 'nx': nx, 'ny': ny, 'zb': float(zmin), 'data': i16([(z-zmin)*100 for z in zdem])},
  'feat': feat, 'trees': i16(tarr), 'forest': enc_polys(forest), 'orchard': enc_polys([]), 'boundary': enc_polys([[bnd]]),
  'ditch': enc_lines([]), 'rail': enc_lines([]), 'buildings': enc_polys([[b] for b in BLD]), 'cover': enc_polys([[[(ME0, MN0), (ME0+MW_//2, MN0), (ME0+MW_, MN0), (ME0+MW_, MN0+MH_), (ME0+MW_//2, MN0+MH_), (ME0, MN0+MH_)]]]),
  'streams': enc_lines([]), 'straw': i16([]), 'flowers': i16(fl_out), 'alti': alti}
open('rd_head.js', 'w').write('const RD_' + KEY.upper() + ' = ' + json.dumps(HEAD, separators=(',', ':')) + ';')
open('data-' + KEY + '.js', 'w').write('Object.assign(RD_' + KEY.upper() + ',' + json.dumps(REST, separators=(',', ':')) + ');RDS.' + KEY + '.alti=RD_' + KEY.upper() + '.alti;')
print({k: len(json.dumps(v)) for k, v in REST.items()}, 'head', len(json.dumps(HEAD)), 'buildings', len(BLD), 'zmin', zmin, max(zdem))
