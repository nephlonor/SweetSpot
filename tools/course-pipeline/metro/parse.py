"""Metropolis Links: read cached OpenStreetMap tiles (osm.py) into features in lat/lon.
buildings: [{id, h, minh, outer: [(lat, lon)...], holes: [...], part, name, tags}]; water / parks: polygons; trees: points."""
import xml.etree.ElementTree as ET
import re

def num(v):
    if v is None: return None
    m = re.match(r'\s*([0-9]+(?:[.,][0-9]+)?)\s*(m|ft|\')?', v)
    if not m: return None
    x = float(m.group(1).replace(',', '.'))
    return x * .3048 if m.group(2) in ('ft', "'") else x

def join_rings(ways):
    """ways: lists of node ids -> closed rings"""
    ways = [list(w) for w in ways if len(w) > 1]; rings = []
    while ways:
        cur = ways.pop(0)
        while cur[0] != cur[-1]:
            for i, w in enumerate(ways):
                if w[0] == cur[-1]: cur += w[1:]
                elif w[-1] == cur[-1]: cur += w[::-1][1:]
                elif w[-1] == cur[0]: cur = w[:-1] + cur
                elif w[0] == cur[0]: cur = w[::-1][:-1] + cur
                else: continue
                ways.pop(i); break
            else: break
        if cur[0] == cur[-1] and len(cur) > 3: rings.append(cur)
    return rings

def WATER(t):
    if t.get('natural') in ('water', 'bay', 'strait'): return True
    if t.get('waterway') in ('riverbank', 'dock', 'canal') and t.get('type') == 'multipolygon' or t.get('waterway') in ('riverbank', 'dock'): return True
    return t.get('landuse') in ('basin', 'reservoir')
PARK = lambda t: t.get('leisure') in ('park', 'garden', 'pitch', 'playground') or t.get('landuse') in ('grass', 'recreation_ground', 'village_green', 'meadow', 'forest') or t.get('natural') in ('wood', 'scrub', 'grassland')
WOOD = lambda t: t.get('natural') == 'wood' or t.get('landuse') == 'forest'
BEACH = lambda t: t.get('natural') in ('beach', 'sand')
PAVED = lambda t: t.get('highway') == 'pedestrian' and t.get('area') == 'yes' or t.get('place') == 'square' or t.get('amenity') == 'parking' and False

def load(files):
    N, Wy, R = {}, {}, {}
    for fn in files:
        root = ET.parse(fn).getroot()
        for el in root:
            if el.tag == 'node':
                N[el.get('id')] = (float(el.get('lat')), float(el.get('lon')), {t.get('k'): t.get('v') for t in el.findall('tag')})
            elif el.tag == 'way':
                Wy[el.get('id')] = ([n.get('ref') for n in el.findall('nd')], {t.get('k'): t.get('v') for t in el.findall('tag')})
            elif el.tag == 'relation':
                R[el.get('id')] = ([(m.get('type'), m.get('ref'), m.get('role')) for m in el.findall('member')], {t.get('k'): t.get('v') for t in el.findall('tag')})
    return N, Wy, R

def features(files, lvl=3.3, deflt=10):
    N, Wy, R = load(files)
    pts = lambda ids: [(N[i][0], N[i][1]) for i in ids if i in N] if all(i in N for i in ids) else None
    out = {'buildings': [], 'water': [], 'parks': [], 'woods': [], 'beach': [], 'trees': [], 'paved': [], 'coast': []}
    def height(t):
        h = num(t.get('height')); mh = num(t.get('min_height'))
        lv = num(t.get('building:levels')); ml = num(t.get('building:min_level'))
        if h is None and lv is not None: h = lv * lvl + (1.5 if t.get('roof:shape') not in (None, 'flat') else .6)
        if mh is None and ml is not None: mh = ml * lvl
        return h, mh or 0
    def add(kind, rings_outer, rings_inner, t, oid):
        if kind == 'b':
            h, mh = height(t)
            out['buildings'].append({'id': oid, 'h': h, 'minh': mh, 'outer': rings_outer, 'holes': rings_inner, 'part': 'building:part' in t and 'building' not in t, 'name': t.get('name'), 'tags': t})
        else: out[kind].append({'id': oid, 'outer': rings_outer, 'holes': rings_inner, 'tags': t})
    def kind_of(t):
        if ('building' in t and t.get('building') != 'no') or 'building:part' in t:
            if t.get('building') in ('roof',) and num(t.get('min_height')) is None and 'building:min_level' not in t: return 'b'
            return 'b'
        if WATER(t): return 'water'
        if WOOD(t): return 'woods'
        if PARK(t): return 'parks'
        if BEACH(t): return 'beach'
        if PAVED(t): return 'paved'
        return None
    for wid, (ids, t) in Wy.items():
        if t.get('natural') == 'coastline':
            p = [(N[i][0], N[i][1]) for i in ids if i in N]
            if len(p) > 1: out['coast'].append(p)
            continue
        k = kind_of(t)
        if not k or len(ids) < 4 or ids[0] != ids[-1]: continue
        p = pts(ids)
        if p: add(k, [p], [], t, 'w' + wid)
    for rid, (mem, t) in R.items():
        if t.get('type') not in ('multipolygon', 'building'): continue
        k = kind_of(t)
        if not k: continue
        if t.get('type') == 'building': continue  # (its parts are ways of their own)
        if any(ty == 'way' and r not in Wy for (ty, r, ro) in mem) and k in ('water', 'parks', 'woods', 'beach', 'b'):
            import osm
            try:
                n2, w2, _ = load([osm.relation_full(rid)])
                for i, v in n2.items(): N.setdefault(i, v)
                for i, v in w2.items(): Wy.setdefault(i, v)
            except SystemExit: pass
        outer = [Wy[r][0] for (ty, r, ro) in mem if ty == 'way' and ro in ('outer', '') and r in Wy]
        inner = [Wy[r][0] for (ty, r, ro) in mem if ty == 'way' and ro == 'inner' and r in Wy]
        ro = [pts(r) for r in join_rings(outer)]; ri = [pts(r) for r in join_rings(inner)]
        ro = [r for r in ro if r]; ri = [r for r in ri if r]
        if ro: add(k, ro, ri, t, 'r' + rid)
    for nid, (la, lo, t) in N.items():
        if t.get('natural') == 'tree': out['trees'].append((la, lo))
    return out
