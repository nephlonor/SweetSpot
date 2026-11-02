"""Metropolis Links: lay each hole of cfg.HOLES into its real city block and write the course data.
python3 build.py check [i ...]   the clash report (fairway, green, tee against the buildings standing on the ground)
python3 build.py plot i out.png  the hole drawn over the city
python3 build.py write           data-metro.js (the engine, metro-engine.js, followed by the data)"""
import sys, math, json, base64, struct, os
import numpy as np
from shapely.geometry import Polygon, Point, LineString, box
from shapely.ops import unary_union
import geo, route
from areas import AREAS

def along(P, s):
    for a, b in zip(P[:-1], P[1:]):
        L = math.dist(a, b)
        if s <= L: t = s / L if L else 0; return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t), ((b[0] - a[0]) / (L or 1), (b[1] - a[1]) / (L or 1))
        s -= L
    a, b = P[-2], P[-1]; L = math.dist(a, b) or 1
    return b, ((b[0] - a[0]) / L, (b[1] - a[1]) / L)
def plen(P): return sum(math.dist(a, b) for a, b in zip(P[:-1], P[1:]))

_G = {}
def hole_geo(hd):
    k = id(hd)
    if k in _G: return _G[k]
    key = hd['area']; E = geo.area_enu(key)
    tee, grn = tuple(hd['tee']), tuple(hd['green'])
    if not hd.get('roof') and not hd.get('nosnap'):
        tee = route.snap(key, tee, hd.get('snapt', 25), 10); grn = route.snap(key, grn, hd.get('snapg', 35), hd.get('gr', 14) + 3)
    if hd.get('route'): P = [tee] + [tuple(p) for p in hd['route']] + [grn]
    elif hd.get('direct') or hd['par'] == 3: P = [tee] + [tuple(p) for p in hd.get('via', [])] + [grn]
    else: P = route.path(key, [tee] + [tuple(p) for p in hd.get('via', [])] + [grn], minc=hd.get('minc', 8), water_ok=hd.get('water_ok', False))
    P[0] = tee; P[-1] = grn
    L = plen(P); gR = hd.get('gr', 14)
    # fairways: from fw0 m to just short of the green, as wide as the street allows
    roofs = None
    if hd.get('roof'):
        corr = LineString(P).buffer(hd.get('roofw', 26))
        roofs = [b for b in E['buildings'] if b['minh'] < 3 and b['h'] > 8 and b['g'].intersects(corr)]
        roofU = unary_union([b['g'] for b in roofs])
    fws, cur = [], None
    s0 = hd.get('fw0', 40 if hd['par'] > 3 else L - gR - 30); s1 = L - gR * .6
    s = s0
    while s <= s1:
        p, d = along(P, s); c = route.clearance(key, *p)
        w = min(hd.get('wmax', 28), 2 * (c - hd.get('margin', 4)))
        if roofs is not None:
            ok = roofU.contains(Point(p).buffer(4)); w = hd.get('wmax', 20) if ok else 0
        cut = any(a <= s <= b for a, b in hd.get('gaps', []))
        if w >= hd.get('wmin', 9) and not cut:
            if cur is None: cur = {'pts': [], 'w': []}; fws.append(cur)
            cur['pts'].append(p); cur['w'].append(round(w, 1))
        else: cur = None
        s += 8
    fws = [f for f in fws if len(f['pts']) >= 2]
    # the green, the tee
    _, dg = along(P, L - 1)
    gr = route.clearance(key, *grn) if roofs is None else 99
    rx = min(gR, max(8, gr - 3)) * hd.get('gs', 1)
    G = dict(c=grn, rx=rx * 1.08, rz=rx * .86, ang=math.atan2(dg[0], dg[1]))
    gpoly = Polygon([(grn[0] + math.cos(t) * G['rx'] * math.cos(G['ang']) + math.sin(t) * G['rz'] * math.sin(G['ang']), grn[1] - math.cos(t) * G['rx'] * math.sin(G['ang']) + math.sin(t) * G['rz'] * math.cos(G['ang'])) for t in np.linspace(0, 2 * math.pi, 40)])
    p50, _ = along(P, min(50, L * .4)); u = ((p50[0] - tee[0]), (p50[1] - tee[1])); ul = math.hypot(*u); u = (u[0] / ul, u[1] / ul)
    fwpolys = [LineString(f['pts']).buffer(min(f['w']) / 2, cap_style=2) if len(f['pts']) > 1 else None for f in fws]
    fwpolys = [unary_union([Point(p).buffer(w / 2) for p, w in zip(f['pts'], f['w'])] + [LineString(f['pts']).buffer(min(f['w']) / 2)]) for f in fws]
    tc = route.clearance(key, *tee) if roofs is None else 30
    tw, tl = min(5, max(2.2, tc * .66)), min(7, max(3, tc * .66))
    from shapely import affinity
    teep = affinity.rotate(box(tee[0] - tw, tee[1] - tl, tee[0] + tw, tee[1] + tl), -math.degrees(math.atan2(u[0], u[1])), origin=tee)
    out = dict(key=key, P=P, L=L, fws=fws, G=G, u=u, tw=tw, tl=tl, gpoly=gpoly, fwpolys=fwpolys, teep=teep, roofs=roofs,
               route_enu=P, fairways_enu=[list(f.exterior.coords) if f.geom_type == 'Polygon' else list(max(f.geoms, key=lambda g: g.area).exterior.coords) for f in fwpolys], green_enu=list(gpoly.exterior.coords))
    _G[k] = out; return out

def clashes(hd):
    g = hole_geo(hd); E = geo.area_enu(hd['area']); out = []
    if hd.get('roof'): return out
    turf = unary_union(g['fwpolys'] + [g['gpoly'], g['teep']])
    for b in E['buildings']:
        if b['minh'] >= 3: continue
        a = b['g'].intersection(turf).area
        if a > .5: out.append((round(a, 1), b['name'] or b['id'], round(b['h'])))
    for w in E['water']:
        a = w.intersection(unary_union([g['gpoly'], g['teep']])).area
        if a > .5 and not hd.get('island'): out.append((round(a, 1), 'WATER under green/tee', 0))
    return out

if __name__ == '__main__':
    import cfg
    cmd = sys.argv[1]
    if cmd == 'check':
        ids = [int(x) for x in sys.argv[2:]] or range(len(cfg.HOLES))
        for i in ids:
            hd = cfg.HOLES[i]; g = hole_geo(hd); c = clashes(hd)
            print('%2d %-18s par %d  %4d m  fairways %s  green r %.1f  clashes %s' % (i + 1, hd['name'], hd['par'], g['L'], [len(f['pts']) for f in g['fws']], g['G']['rx'], c[:6] or 'none'))
    elif cmd == 'plot':
        import plot
        i = int(sys.argv[2]); hd = cfg.HOLES[i]; g = hole_geo(hd); la, lo, R = AREAS[hd['area']]
        xs = [p[0] for p in g['P']]; ys = [p[1] for p in g['P']]; cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        rr = max(max(xs) - min(xs), max(ys) - min(ys)) / 2 + 90
        k = 111320 * math.cos(math.radians(la))
        from PIL import Image, ImageDraw
        F = plot.area(la, lo, R); out = sys.argv[3]
        plot.draw(la, lo, R, out, None, rr / 350, F)
        im = Image.open(out); d = ImageDraw.Draw(im); px = rr / 350
        # crop to the hole
        tx = lambda e, n: ((e + R) / px, (R - n) / px)
        for fw in g['fairways_enu']: d.polygon([tx(*p) for p in fw], outline=(255, 255, 0))
        d.polygon([tx(*p) for p in g['green_enu']], outline=(255, 0, 255))
        d.line([tx(*p) for p in g['P']], fill=(255, 255, 255), width=1)
        if g['roofs']:
            for b in g['roofs']: d.polygon([tx(*p) for p in b['g'].exterior.coords], outline=(0, 255, 255))
        a = tx(cx - rr, cy + rr); b = tx(cx + rr, cy - rr)
        im.crop((int(a[0]), int(a[1]), int(b[0]), int(b[1]))).save(out)

# ---------------- the course data ----------------
DEM_AREAS = {'mont': 'N48E002', 'urca': 'S23W044', 'jockey': 'S23W044', 'copa': 'S23W044'}
def dem_sampler(tile):
    a = np.fromfile('/tmp/metro-dem/%s.hgt' % tile, dtype='>i2').reshape(3601, 3601).astype(np.float32)
    a[a < -500] = 0
    lat0 = (-1 if tile[0] == 'S' else 1) * int(tile[1:3]) + 1; lon0 = (-1 if tile[3] == 'W' else 1) * int(tile[4:7])
    def at(la, lo):
        r = min(3598.99, max(0, (lat0 - la) * 3600)); c = min(3598.99, max(0, (lo - lon0) * 3600)); i, j = int(r), int(c); fr, fc = r - i, c - j
        return float(a[i, j] * (1 - fr) * (1 - fc) + a[i, j + 1] * (1 - fr) * fc + a[i + 1, j] * fr * (1 - fc) + a[i + 1, j + 1] * fr * fc)
    return at
# the landmarks drawn as models (their OpenStreetMap outline is left out; the model stands where it stands): area -> [(names, kind, extra)]
MODELS = {
    'eiffel': [(('Tour Eiffel', 'Eiffel Tower'), 'eiffel')],
    'champs': [(("Arc de Triomphe", "Arc de Triomphe de l'Étoile"), 'arc')],
    'ttower': [(('東京タワー', 'Tokyo Tower'), 'tokyotower')],
    'emb': [(('Elizabeth Tower', 'Big Ben', 'Clock Tower'), 'bigben')],
}
# landmarks that are not buildings in OpenStreetMap: placed at their real position (lat, lon, kind, rotation deg)
EXTRA = {
    'emb': [(51.50330, -0.11960, 'eye', 22)],
    'jockey': [(-22.95194, -43.21050, 'christ', 160)], 'copa': [(-22.95194, -43.21050, 'christ', 160)], 'urca': [(-22.95194, -43.21050, 'christ', 160)],
}
def enc(vals):
    v = np.clip(np.round(np.array(vals, dtype=np.float64)), -32768, 32767).astype('<i2'); return base64.b64encode(v.tobytes()).decode()
def ringpts(g, tol):
    g = g.simplify(tol, preserve_topology=True)
    return list(g.exterior.coords)[:-1] if g.geom_type == 'Polygon' else []

def write(out_js):
    import cfg
    from areas import AREAS
    from shapely import affinity
    HC = ['ny', 'ny', 'ny', 'london', 'london', 'london', 'paris', 'paris', 'paris', 'tokyo', 'tokyo', 'tokyo', 'ams', 'ams', 'ams', 'rio', 'rio', 'rio']
    hcp = [15, 3, 7, 5, 13, 1, 9, 11, 17, 2, 16, 8, 6, 4, 18, 10, 14, 12]
    defs = []; dems = {}
    for i, hd in enumerate(cfg.HOLES):
        g = hole_geo(hd); key = hd['area']; E = geo.area_enu(key); la0, lo0, Ra = AREAS[key]
        T = g['P'][0]; u = g['u']
        X = lambda e, n: ((e - T[0]) * u[1] - (n - T[1]) * u[0], (e - T[0]) * u[0] + (n - T[1]) * u[1])
        ang = lambda a: math.degrees(a - math.atan2(u[0], u[1]))  # a bearing (rad, from north) -> degrees from the hole's forward
        route_ln = LineString(g['P']); near = route_ln.buffer(hd.get('keep', 430))
        # landmarks replaced by models
        mons, skip = [], set()
        for names, kind in MODELS.get(key, []):
            for b in E['buildings']:
                nm = ' '.join(str(b['tags'].get(k, '')) for k in ('name', 'name:en', 'name:fr', 'name:ja'))
                if any(n.lower() in nm.lower() for n in names):
                    skip.add(id(b))
            hits = [b for b in E['buildings'] if id(b) in skip]
            if hits:
                big = max(hits, key=lambda b: b['g'].area); hits = [b for b in hits if b['g'].distance(big['g']) < 5]  # (the landmark itself, not a shop of the same name down the road)
                skip -= set(id(b) for b in E['buildings'] if id(b) in skip and b not in hits)
                U = unary_union([b['g'] for b in hits]); c = U.centroid; r = U.minimum_rotated_rectangle; cc = list(r.exterior.coords)
                br = math.atan2(cc[1][0] - cc[0][0], cc[1][1] - cc[0][1])
                x, f = X(c.x, c.y); mons.append(dict(kind=kind, x=round(x, 1), f=round(f, 1), rot=round(-ang(br), 1)))
        P = plot.enu(la0, lo0) if False else None
        import plot as _pl
        Pj = _pl.enu(la0, lo0)
        for la, lo, kind, rot in EXTRA.get(key, []):
            e, n = Pj(la, lo); x, f = X(e, n)
            mons.append(dict(kind=kind, x=round(x, 1), f=round(f, 1), rot=round(rot - math.degrees(math.atan2(u[0], u[1])), 1), far=math.hypot(x, f) > 900))
        # buildings
        roofids = set(id(b) for b in (g['roofs'] or []))
        Bv = [0]; nb = 0
        for b in E['buildings']:
            if id(b) in skip or not b['g'].intersects(near): continue
            d = b['g'].distance(route_ln); pts = ringpts(b['g'], .4 if d < 120 else 1.2 if d < 300 else 2.5)
            if len(pts) < 3: continue
            h = b['h'] or hd.get('hdef', {'ny': 18, 'london': 14, 'paris': 18, 'tokyo': 12, 'ams': 12, 'rio': 10}[HC[i]])
            if b['minh'] >= h: continue
            col = b['tags'].get('building:colour') or b['tags'].get('colour') or ''
            ci = 0
            if col.startswith('#') and len(col) in (4, 7):
                c7 = col if len(col) == 7 else '#' + ''.join(ch * 2 for ch in col[1:])
                try: r_, g_, b_ = int(c7[1:3], 16), int(c7[3:5], 16), int(c7[5:7], 16); ci = 1 + (r_ >> 4) * 256 + (g_ >> 4) * 16 + (b_ >> 4)
                except ValueError: ci = 0
            Bv += [len(pts), h * 10, b['minh'] * 10, (1 if id(b) in roofids else 0), ci - 32768 if ci else -32768]
            for p in pts: x, f = X(*p); Bv += [x * 10, f * 10]
            nb += 1
        Bv[0] = nb
        def polys(lst, tol=1.0):
            V = [0]; n = 0
            for gg in lst:
                gg = gg.intersection(near)
                for pg in (gg.geoms if gg.geom_type in ('MultiPolygon', 'GeometryCollection') else [gg]):
                    if pg.geom_type != 'Polygon' or pg.area < 20: continue
                    pg = pg.simplify(tol, preserve_topology=True); rings = [list(pg.exterior.coords)[:-1]] + [list(r.coords)[:-1] for r in pg.interiors]
                    rings = [r for r in rings if len(r) >= 3]
                    V += [len(rings)]
                    for r in rings:
                        V += [len(r)]
                        for p in r: x, f = X(*p); V += [x * 10, f * 10]
                    n += 1
            V[0] = n; return V
        trees = []
        for (e, n) in E['trees']:
            if route_ln.distance(Point(e, n)) < 260: x, f = X(e, n); trees.append((round(x, 1), round(f, 1)))
        trees = trees[:700]
        # the ground's height (SRTM), relative to the tee
        dem = None
        if key in DEM_AREAS:
            at = dem_sampler(DEM_AREAS[key]); k_ = 111320 * math.cos(math.radians(la0))
            ll = lambda e, n: (la0 + n / 110574, lo0 + e / k_)
            # back from the hole frame to east / north
            inv = lambda x, f: (T[0] + x * u[1] + f * u[0], T[1] - x * u[0] + f * u[1])
            z0 = at(*ll(*T)); res, ext = (25, 7000) if DEM_AREAS[key] == 'S23W044' else (10, 2600); N = ext // res
            vals = [round((at(*ll(*inv((j - N // 2) * res, (i - N // 2) * res))) - z0) * 10) for i in range(N) for j in range(N)]
            dem = dict(res=res, n=N, z0=round(z0, 1), d=enc(vals))
        gC = g['G']; gx, gf = X(*gC['c']); _, dg = along(g['P'], g['L'] - 1)
        ga = math.atan2(dg[0], dg[1]); grot = ang(ga)
        rr = random_pin = (i * 7919) % 360
        pin = (gx + 3 * math.sin(math.radians(rr)), gf + 3 * math.cos(math.radians(rr)))
        # greenside bunkers where the ground is open
        bunk = []
        for side, back in ((-1, -.3), (1, .2), (0, 1)):
            a = ga + side * math.pi / 2 if side else ga
            k = gC['rx'] + 4.5 if side else gC['rz'] + 4
            e = gC['c'][0] + math.sin(a) * k + (math.sin(ga) * back * gC['rz'] if side else 0); n = gC['c'][1] + math.cos(a) * k + (math.cos(ga) * back * gC['rz'] if side else 0)
            if hd.get('roof') or route.clearance(key, e, n) > 5:
                x, f = X(e, n); bunk.append(dict(x=round(x, 1), f=round(f, 1), rx=4.5 if side else 6, rz=3 if side else 2.6, rot=round(ang(a) + 90 if side else ang(ga) + 90, 1), depth=1))
        par = hd['par']
        dd = dict(name=hd['name'], city=HC[i], par=par, hcp=hcp[i], seed=4100 + i * 7, inspo=hd.get('inspo', ''),
                  tee=dict(x=0, f=0, w=round(2 * g['tw'], 1), l=round(2 * g['tl'], 1), elev=.3), start=dict(x=0, f=0 if par == 3 else -min(3, g['tl'] - 1)),
                  route=[[round(a, 1) for a in X(*p)] for p in g['P']],
                  fairways=[dict(pts=[[round(a, 1) for a in X(*p)] for p in fw['pts']], w=fw['w']) for fw in g['fws']],
                  green=dict(x=round(gx, 1), f=round(gf, 1), rx=round(gC['rx'], 1), rz=round(gC['rz'], 1), rot=round(grot, 1), elev=.4, sx=.004, sf=.009, und=.06, blend=4),
                  pin=dict(x=round(pin[0], 1), f=round(pin[1], 1)), bunkers=bunk,
                  hw=hd.get('hw', 75), turf=hd.get('turf', 6), margin=hd.get('mg', 110), windMax=hd.get('wind', 6),
                  mons=mons, roofHole=bool(hd.get('roof')), neon=hd.get('neon', 0), data=i)
        if hd.get('island'):
            dd['island'] = dict(x=round(gx, 1), f=round(gf, 1), rx=round(gC['rx'] + 7, 1), rz=round(gC['rz'] + 6, 1), rot=round(grot, 1), wob=.04)
        defs.append(dict(def_=dd, B=enc(Bv), W=enc(polys([unary_union([w.buffer(0) for w in E['water']])], .8)), P=enc(polys([unary_union([w.buffer(0) for w in E['parks'] + E['woods']])] if E['parks'] + E['woods'] else [], 1.5)), S=enc(polys([unary_union([w.buffer(0) for w in E['beach']])] if E['beach'] else [], 1.5)), T=trees, D=dem, area=key))
        print(i + 1, dd['name'], 'buildings', nb, 'trees', len(trees), 'mons', [m['kind'] for m in mons], 'B kb', len(defs[-1]['B']) // 1024, flush=True)
    eng = open(os.path.join(os.path.dirname(__file__), 'metro-engine.js')).read()
    data = 'const METRO_DATA = ' + json.dumps([dict(d['def_'] and {'def': d['def_'], 'B': d['B'], 'W': d['W'], 'P': d['P'], 'S': d['S'], 'T': d['T'], 'D': d['D']}) for d in defs], separators=(',', ':'), ensure_ascii=False) + ';\n'
    open(out_js, 'w').write('// Metropolis Links (generated by tools/course-pipeline/metro/build.py from OpenStreetMap and SRTM: do not edit; the engine is metro-engine.js)\n' + eng + '\n' + data)
    print('wrote', out_js, os.path.getsize(out_js) // 1024, 'kB')

if __name__ == '__main__' and sys.argv[1] == 'write':
    write(sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), '../../../data-metro.js'))
