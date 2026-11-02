"""Metropolis Links: where a fairway can go. A 1 m raster of the open ground of an area (no building standing on the ground, no water),
its clearance (metres to the nearest building or water), and a least-cost path through the streets between waypoints."""
import math, heapq
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
import geo

_R = {}
def raster(key, res=1.0):
    if key in _R: return _R[key]
    from areas import AREAS
    R = AREAS[key][2]; E = geo.area_enu(key); S = int(2 * R / res)
    tx = lambda p: ((p[0] + R) / res, (R - p[1]) / res)
    im = Image.new('L', (S, S), 255); d = ImageDraw.Draw(im)   # 255 open, 0 blocked, 128 water
    wim = Image.new('L', (S, S), 0); wd = ImageDraw.Draw(wim)
    def burn(g, dd, v):
        for poly in (g.geoms if g.geom_type == 'MultiPolygon' else [g]):
            dd.polygon([tx(p) for p in poly.exterior.coords], fill=v)
            for r in poly.interiors: dd.polygon([tx(p) for p in r.coords], fill=255 if v == 0 else 0)
    for g in E['water']: burn(g, wd, 255)
    if key in ('copa',):
        for g in E['beach']: burn(g, wd, 255)   # (Copacabana: the fairway keeps to the avenue, off the sand)
    for b in E['buildings']:
        if b['minh'] < 3: burn(b['g'], d, 0)
    A = np.array(im) > 0; Wt = np.array(wim) > 0
    free = A & ~Wt
    clr = ndimage.distance_transform_edt(free) * res
    out = dict(R=R, res=res, S=S, free=free, water=Wt, bld=~A, clr=clr)
    _R[key] = out; return out

def clearance(key, e, n):
    r = raster(key); i = int((r['R'] - n) / r['res']); j = int((e + r['R']) / r['res'])
    if 0 <= i < r['S'] and 0 <= j < r['S']: return float(r['clr'][i, j])
    return 0.0

def path(key, pts, minc=7.0, water_ok=False, step=2):
    """least-cost path through the waypoints; cost grows as the street narrows; nothing narrower than minc (m to a wall)"""
    r = raster(key); res = r['res'] * step; clr = r['clr'][::step, ::step]; wat = r['water'][::step, ::step]; S = clr.shape[0]; R = r['R']
    ij = lambda e, n: (int(round((R - n) / res)), int(round((e + R) / res)))
    en = lambda i, j: (j * res - R, R - i * res)
    def cost(i, j):
        c = clr[i, j]
        if wat[i, j]: return 1.5 if water_ok else None
        if c < minc: return None
        return 1 + 30.0 / c
    full = []
    for a, b in zip(pts[:-1], pts[1:]):
        s, g = ij(*a), ij(*b); D = {s: 0}; prev = {}; pq = [(0, s)]
        while pq:
            dcur, u = heapq.heappop(pq)
            if u == g: break
            if dcur > D.get(u, 1e18): continue
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    if not di and not dj: continue
                    v = (u[0] + di, u[1] + dj)
                    if not (0 <= v[0] < S and 0 <= v[1] < S): continue
                    c = cost(*v) if v != g else 1
                    if c is None: continue
                    nd = dcur + c * (1.4142 if di and dj else 1)
                    if nd < D.get(v, 1e18): D[v] = nd; prev[v] = u; heapq.heappush(pq, (nd, v))
        if g not in prev and g != s: raise SystemExit('no way from %s to %s' % (a, b))
        seg = [g]
        while seg[-1] != s: seg.append(prev[seg[-1]])
        seg = [en(*q) for q in seg[::-1]]
        full += seg if not full else seg[1:]
    return simplify(full, 3.0)

def simplify(P, tol):
    if len(P) < 3: return P
    a, b = np.array(P[0]), np.array(P[-1]); d = b - a; L = np.hypot(*d) or 1
    dist = [abs(d[0] * (p[1] - a[1]) - d[1] * (p[0] - a[0])) / L for p in P[1:-1]]
    k = int(np.argmax(dist))
    if dist[k] > tol: return simplify(P[:k + 2], tol)[:-1] + simplify(P[k + 1:], tol)
    return [P[0], P[-1]]

def snap(key, p, rad=40, want=16):
    """the open spot near p with the most room (up to want m to a wall), preferring nearer ones"""
    r = raster(key); R, res = r['R'], r['res']; i0, j0 = int((R - p[1]) / res), int((p[0] + R) / res); k = int(rad / res)
    sub = r['clr'][max(0, i0 - k):i0 + k + 1, max(0, j0 - k):j0 + k + 1]
    ii, jj = np.mgrid[max(0, i0 - k):i0 + k + 1, max(0, j0 - k):j0 + k + 1][:, :sub.shape[0], :sub.shape[1]]
    d = np.hypot(ii - i0, jj - j0) * res
    score = np.minimum(sub, want) - .08 * d - 1e3 * (d > rad)
    a = np.unravel_index(np.argmax(score), score.shape)
    return (float(jj[a] * res - R), float(R - ii[a] * res))
