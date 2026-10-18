import xml.etree.ElementTree as ET, json, math, collections
LAT0, LON0 = 52.7000, -1.1500
KX = 111320*math.cos(math.radians(LAT0)); KY = 111132.0
def enu(lat, lon): return ((lon-LON0)*KX, (lat-LAT0)*KY)
r = ET.parse('r.osm').getroot()
nodes = {n.get('id'): (float(n.get('lat')), float(n.get('lon')), {k.get('k'): k.get('v') for k in n.findall('tag')}) for n in r.findall('node')}
ways = {}
for w in r.findall('way'):
    ways[w.get('id')] = ([x.get('ref') for x in w.findall('nd')], {k.get('k'): k.get('v') for k in w.findall('tag')})
def pts(wid): return [enu(*nodes[n][:2]) for n in ways[wid][0] if n in nodes]
out = collections.defaultdict(list); holes = []; pins = []
for wid, (nd, tg) in ways.items():
    p = pts(wid)
    if len(p) < 2: continue
    g = tg.get('golf'); closed = nd[0] == nd[-1] and len(p) >= 4
    rec = {'id': wid, 'pts': p, 'tags': tg}
    if g == 'hole':
        if tg.get('ref'): holes.append(rec)
        else: out['p3hole'].append(rec)
    elif g == 'fairway' and closed: out['fair'].append(rec)
    elif g == 'green' and closed: out['green'].append(rec)
    elif g == 'tee' and closed: out['tee'].append(rec)
    elif g == 'bunker' and closed: out['sand'].append(rec)
    elif (g in ('water_hazard','lateral_water_hazard') or tg.get('natural') == 'water') and closed: out['water'].append(rec)
    elif g == 'driving_range' and closed: out['range'].append(rec)
    elif g in ('cartpath','path') or tg.get('highway') in ('track', 'service', 'footway', 'path'): out['pathline'].append(rec)
    elif tg.get('leisure') == 'golf_course' and closed: out['boundary' if 'Rothley' in tg.get('name','') else 'other_course'].append(rec)
    elif g == 'pine straw' or tg.get('golf') == 'pine_straw': out['straw'].append(rec)
    elif tg.get('natural') in ('wood', 'scrub') or tg.get('landuse') == 'forest': out['forest_' + (tg.get('natural') or 'forest')].append(rec)
    elif tg.get('building') and closed: out['buildings'].append(rec)
    elif tg.get('waterway') in ('stream', 'river', 'ditch') : out['streams'].append(rec)
    elif g == 'clubhouse' and closed: out['buildings'].append(rec)
    elif g == 'rough' and closed: out['rough'].append(rec)
def join_rings(wids):
    segs = [[n for n in ways[w][0] if n in nodes] for w in wids if w in ways]
    segs = [x for x in segs if len(x) > 1]; rings = []
    while segs:
        cur = segs.pop(0)
        while cur[0] != cur[-1]:
            for i, sg in enumerate(segs):
                if sg[0] == cur[-1]: cur += sg[1:]; segs.pop(i); break
                if sg[-1] == cur[-1]: cur += sg[::-1][1:]; segs.pop(i); break
                if sg[-1] == cur[0]: cur = sg + cur[1:]; segs.pop(i); break
                if sg[0] == cur[0]: cur = sg[::-1] + cur[1:]; segs.pop(i); break
            else: break
        if cur[0] == cur[-1] and len(cur) >= 4: rings.append([enu(*nodes[n][:2]) for n in cur])
    return rings
for rel in r.findall('relation'):
    tg = {k.get('k'): k.get('v') for k in rel.findall('tag')}
    if tg.get('type') != 'multipolygon': continue
    mem = [(m.get('ref'), m.get('role')) for m in rel.findall('member') if m.get('type') == 'way']
    outer = join_rings([w for w, ro in mem if ro != 'inner']); inner = join_rings([w for w, ro in mem if ro == 'inner'])
    g = tg.get('golf'); key = {'fairway': 'fair', 'rough': 'rough', 'green': 'green', 'bunker': 'sand', 'tee': 'tee'}.get(g)
    if not key and (tg.get('natural') == 'wood' or tg.get('landuse') == 'forest'): key = 'forest_wood'
    if not key and tg.get('natural') == 'water': key = 'water'
    if not key: continue
    for o in outer: out[key].append({'id': 'r' + rel.get('id'), 'pts': o, 'inner': inner, 'tags': tg})
for nid, (la, lo, tg) in nodes.items():
    if tg.get('golf') == 'pin': pins.append({'ref': tg.get('ref'), 'p': enu(la, lo), 'tags': tg})
    if tg.get('golf') == 'tee': out['teenode'].append({'p': enu(la, lo), 'tags': tg})
json.dump({'out': out, 'holes': holes, 'pins': pins}, open('feat.json', 'w'))
print({k: len(v) for k, v in out.items()}, len(holes), len(pins))
for h in sorted(holes, key=lambda h: int(h['tags']['ref'])):
    p = h['pts']; L = sum(math.dist(p[i], p[i+1]) for i in range(len(p)-1)); print(h['tags']['ref'], h['tags'].get('par'), 'len %.0f' % L, 'tee %.0f,%.0f' % p[0], 'green %.0f,%.0f' % p[-1])
print('tee tags', collections.Counter(tuple(sorted(w['tags'].items())) for w in out['tee']).most_common(6))
print('pin tags', pins[:3])
for k in ('boundary',):
    for b in out[k]: xs=[q[0] for q in b['pts']]; ys=[q[1] for q in b['pts']]; print(k, len(b['pts']), min(xs), max(xs), min(ys), max(ys), b['tags'])
