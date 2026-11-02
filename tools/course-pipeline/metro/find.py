import sys, geo
E = geo.area_enu(sys.argv[1]); q = [a.lower() for a in sys.argv[2:]]
for b in E['buildings']:
    n = ' '.join(str(b['tags'].get(k, '')) for k in ('name', 'name:en', 'tourism', 'man_made', 'historic'))
    if any(x in n.lower() for x in q):
        c = b['g'].centroid; print(round(c.x), round(c.y), round(b['h']), round(b['minh']), b['id'], n.strip()[:70], round(b['g'].area))
