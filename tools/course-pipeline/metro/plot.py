"""Metropolis Links: a top-down picture of a city block to lay a hole out on.
usage: python3 plot.py lat lon radius_m out.png [hole_index]
buildings shaded by height (labels: metres), water blue, parks green, trees dots; a 50 m grid in metres east / north of (lat, lon).
With a hole index the hole from cfg.py is drawn on top (tee, route, fairways, green) and its clashes with buildings are listed."""
import sys, math
from PIL import Image, ImageDraw, ImageFont
import osm, parse

def enu(lat0, lon0):
    k = 111320 * math.cos(math.radians(lat0))
    return lambda la, lo: ((lo - lon0) * k, (la - lat0) * 110574)

def area(lat, lon, R):
    import os, pickle
    fn = os.path.join(osm.CACHE, 'feat_%.5f_%.5f_%d.pkl' % (lat, lon, R))
    if os.path.exists(fn): return pickle.load(open(fn, 'rb'))
    dla, dlo = R / 110574, R / (111320 * math.cos(math.radians(lat)))
    F = parse.features(osm.tiles(lat - dla, lon - dlo, lat + dla, lon + dlo)); pickle.dump(F, open(fn, 'wb')); return F

def draw(lat, lon, R, out, hole=None, px=1.0, F=None):
    F = F or area(lat, lon, R); P = enu(lat, lon); S = int(2 * R / px)
    im = Image.new('RGB', (S, S), (70, 72, 76)); d = ImageDraw.Draw(im)
    tx = lambda e, n: ((e + R) / px, (R - n) / px)
    poly = lambda ring: [tx(*P(a, b)) for a, b in ring]
    for k, col in (('parks', (96, 150, 80)), ('woods', (60, 110, 60)), ('beach', (225, 210, 160)), ('paved', (150, 146, 138)), ('water', (90, 150, 200))):
        for f in F[k]:
            for r in f['outer']: d.polygon(poly(r), fill=col)
            for r in f['holes']: d.polygon(poly(r), fill=(70, 72, 76))
    for la, lo in F['trees']:
        x, y = tx(*P(la, lo)); d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(40, 120, 40))
    try: fnt = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 10)
    except Exception: fnt = None
    for b in sorted(F['buildings'], key=lambda b: b['h'] or 0):
        h = b['h'] or 0; c = int(150 + min(h, 200) / 200 * 100)
        col = (c, int(c * .8), int(c * .6)) if b['minh'] > 2 else (c, c, c - 20)
        for r in b['outer']: d.polygon(poly(r), fill=col, outline=(40, 40, 40))
    for b in F['buildings']:
        if not b['h'] or b['part']: continue
        r = b['outer'][0]; xs = [tx(*P(a, c)) for a, c in r]; cx = sum(p[0] for p in xs) / len(xs); cy = sum(p[1] for p in xs) / len(xs)
        if b['h'] > 0: d.text((cx - 6, cy - 5), str(round(b['h'])), fill=(20, 20, 20), font=fnt)
    for g in range(-int(R // 50) * 50, int(R) + 1, 50):
        a = tx(g, 0)[0]; d.line([(a, 0), (a, S)], fill=(255, 255, 255) if g == 0 else (120, 160, 220), width=1)
        b = tx(0, g)[1]; d.line([(0, b), (S, b)], fill=(255, 255, 255) if g == 0 else (120, 160, 220), width=1)
        d.text((a + 2, 2), str(g), fill=(255, 255, 0), font=fnt); d.text((2, b + 2), str(g), fill=(255, 255, 0), font=fnt)
    if hole is not None:
        import cfg, build
        hd = cfg.HOLES[hole]; geo = build.hole_geo(hd)
        for fw in geo['fairways_enu']: d.polygon([tx(*p) for p in fw], outline=(255, 255, 0), fill=None)
        d.polygon([tx(*p) for p in geo['green_enu']], outline=(255, 0, 255))
        d.line([tx(*p) for p in geo['route_enu']], fill=(255, 255, 255), width=2)
    im.save(out); return F

if __name__ == '__main__':
    if sys.argv[1] in __import__('areas').AREAS:
        la, lo, R = __import__('areas').AREAS[sys.argv[1]]; R2 = float(sys.argv[3]) if len(sys.argv) > 3 else R
        draw(la, lo, R2, sys.argv[2], int(sys.argv[4]) if len(sys.argv) > 4 else None, float(sys.argv[5]) if len(sys.argv) > 5 else 2.0, area(la, lo, R)); sys.exit()
    lat, lon, R = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])
    draw(lat, lon, R, sys.argv[4], int(sys.argv[5]) if len(sys.argv) > 5 else None, float(sys.argv[6]) if len(sys.argv) > 6 else 1.0)
