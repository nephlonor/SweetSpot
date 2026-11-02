"""find tees for a green: one least-cost sweep out from the green through the streets; tees whose path is L0..L1 m long, through the widest streets
python3 search.py area ge gn L0 L1 [minc]"""
import sys, math, heapq, numpy as np, route
key = sys.argv[1]; G = (float(sys.argv[2]), float(sys.argv[3])); L0, L1 = float(sys.argv[4]), float(sys.argv[5]); minc = float(sys.argv[6]) if len(sys.argv) > 6 else 7
r = route.raster(key); step = 2; res = r['res'] * step; clr = r['clr'][::step, ::step]; S = clr.shape[0]; R = r['R']
ij = lambda e, n: (int(round((R - n) / res)), int(round((e + R) / res))); en = lambda i, j: (j * res - R, R - i * res)
s = ij(*route.snap(key, G, 30, 17)); D = {s: 0.0}; Lg = {s: 0.0}; prev = {}; pq = [(0.0, s)]
while pq:
    d, u = heapq.heappop(pq)
    if d > D[u]: continue
    if Lg[u] > L1 + 20: continue
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            if not di and not dj: continue
            v = (u[0] + di, u[1] + dj)
            if not (0 <= v[0] < S and 0 <= v[1] < S) or clr[v] < minc: continue
            st = res * (1.4142 if di and dj else 1); nd = d + st * (1 + 30 / clr[v])
            if nd < D.get(v, 1e18): D[v] = nd; Lg[v] = Lg[u] + st; prev[v] = u; heapq.heappush(pq, (nd, v))
cands = []
for v, L in Lg.items():
    if L0 <= L <= L1 and clr[v] >= 9: cands.append((L / D[v], v, L))
cands.sort(reverse=True); seen = []
for sc, v, L in cands:
    e, n = en(*v)
    if any(math.dist((e, n), q) < 80 for q in seen): continue
    seen.append((e, n)); p = [v]
    while p[-1] in prev: p.append(prev[p[-1]])
    P = route.simplify([en(*q) for q in p], 6)
    mc = min(clr[q] for q in p)
    print('tee (%d, %d) len %d score %.2f minclr %.1f turns %d  via %s' % (e, n, L, sc, mc, len(P) - 2, [(round(a), round(b)) for a, b in P[1:-1]][:6]))
    if len(seen) >= 8: break
