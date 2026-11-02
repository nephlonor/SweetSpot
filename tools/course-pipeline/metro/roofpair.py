import math, geo
from shapely.geometry import LineString
E = geo.area_enu('ttower'); B = [b for b in E['buildings'] if b['minh'] < 3 and b['h'] > 20]
def dims(g):
    r = g.minimum_rotated_rectangle; c = list(r.exterior.coords); a = math.dist(c[0], c[1]); b = math.dist(c[1], c[2]); return min(a, b), max(a, b)
tees = [b for b in B if 50 <= b['h'] <= 140 and dims(b['g'])[0] >= 14 and math.hypot(b['g'].centroid.x, b['g'].centroid.y) < 450]
grs = [b for b in B if 25 <= b['h'] <= 90 and dims(b['g'])[0] >= 30 and math.hypot(b['g'].centroid.x, b['g'].centroid.y) < 450]
out = []
for t in tees:
    for g in grs:
        if g is t: continue
        a, c = t['g'].centroid, g['g'].centroid; d = math.dist((a.x, a.y), (c.x, c.y))
        if not (130 <= d <= 200): continue
        dh = t['h'] - g['h']
        if not (8 <= dh <= 50): continue
        ln = LineString([(a.x, a.y), (c.x, c.y)]); block = max([b['h'] for b in B if b is not t and b is not g and b['g'].intersects(ln)] + [0])
        if block > g['h'] + 5: continue
        tw = min(math.hypot(a.x, a.y), math.hypot(c.x, c.y))
        out.append((tw, round(a.x), round(a.y), round(t['h']), round(c.x), round(c.y), round(g['h']), round(d), dims(g['g'])))
out.sort()
for o in out[:10]: print(o)
