"""shared geometry: features of an area in ENU metres (shapely), parts replace their outlines"""
import math, plot
from shapely.geometry import Polygon, Point, LineString
from shapely.strtree import STRtree
from shapely.validation import make_valid
from areas import AREAS
_C = {}
def area_enu(key):
    if key in _C: return _C[key]
    la, lo, R = AREAS[key]; F = plot.area(la, lo, R); P = plot.enu(la, lo)
    def pg(f):
        try:
            g = Polygon([P(*q) for q in f['outer'][0]], [[P(*q) for q in r] for r in f['holes'] if len(r) > 3] if len(f['outer']) == 1 else [])
            if not g.is_valid: g = make_valid(g)
            if g.geom_type == 'GeometryCollection': g = max([x for x in g.geoms if x.area > 0], key=lambda x: x.area, default=None)
            if g is not None and g.geom_type == 'MultiPolygon': g = max(g.geoms, key=lambda x: x.area)
            return g
        except Exception: return None
    B = []
    for f in F['buildings']:
        for k, ring in enumerate(f['outer']):
            g = pg(dict(f, outer=[ring], holes=f['holes'] if k == 0 else []))
            if g is None or g.area < 4: continue
            B.append(dict(id=f['id'], g=g, h=f['h'], minh=f['minh'], part=f['part'], name=f['name'], tags=f['tags']))
    # outlines that have parts inside them are drawn by their parts
    parts = [b for b in B if b['part']]; tp = STRtree([b['g'] for b in parts]) if parts else None
    out = []
    for b in B:
        if not b['part'] and tp is not None:
            ins = [parts[i] for i in tp.query(b['g']) if b['g'].contains(parts[i]['g'].representative_point())]
            if ins and sum(p['g'].area for p in ins) > .3 * b['g'].area: continue
        out.append(b)
    for b in out:
        if b['h'] is None: b['h'] = 0
    E = dict(buildings=out, tree=STRtree([b['g'] for b in out]))
    for k in ('water', 'parks', 'woods', 'beach', 'paved'):
        E[k] = [g for g in (pg(f) for f in F[k]) if g is not None]
    E['trees'] = [P(*t) for t in F['trees']]
    # the open sea: OpenStreetMap draws only the coastline (land on its left); the box of the area is cut along it and the pieces on its right are sea
    if F.get('coast'):
        from shapely.ops import split, linemerge, unary_union
        from shapely.geometry import box, MultiLineString
        Rr = AREAS[key][2]; bx = box(-Rr, -Rr, Rr, Rr)
        lines = linemerge(MultiLineString([[P(*q) for q in c] for c in F['coast']]))
        lines = [lines] if lines.geom_type == 'LineString' else list(lines.geoms)
        pieces = [bx]
        for ln in lines:
            ln2 = ln.intersection(bx.buffer(50))
            nxt = []
            for pc in pieces:
                try: nxt += list(split(pc, ln2).geoms)
                except Exception: nxt.append(pc)
            pieces = nxt
        def right(pc):
            q = pc.representative_point(); best = None
            for ln in lines:
                d = ln.project(q); a = ln.interpolate(max(0, d - 1)); b = ln.interpolate(min(ln.length, d + 1)); dist = ln.distance(q)
                if best is None or dist < best[0]: best = (dist, (b.x - a.x) * (q.y - a.y) - (b.y - a.y) * (q.x - a.x))
            return best and best[1] < 0
        sea = [pc for pc in pieces if right(pc)]
        E['water'] += [g for s in sea for g in (s.geoms if s.geom_type == 'MultiPolygon' else [s])]
    _C[key] = E; return E
def roof_at(E, x, y):
    p = Point(x, y); best = None
    for i in E['tree'].query(p):
        b = E['buildings'][i]
        if b['minh'] < 3 and b['g'].contains(p) and (best is None or b['h'] > best['h']): best = b
    return best
