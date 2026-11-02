import math, sys, geo
E = geo.area_enu('nyroof'); brg = math.radians(29); u = (math.sin(brg), math.cos(brg)); r = (u[1], -u[0])
best = []
for off in range(-600, 601, 6):
    for s0 in range(-600, 200, 20):
        prof = []
        for s in range(0, 500, 5):
            x = r[0] * off + u[0] * (s0 + s); y = r[1] * off + u[1] * (s0 + s)
            if abs(x) > 650 or abs(y) > 650: prof = None; break
            b = geo.roof_at(E, x, y); prof.append(b['h'] if b else 0)
        if not prof: continue
        on = [h for h in prof if h > 0]; cov = len(on) / len(prof)
        if cov < .7 or not on: continue
        hs = sorted(on); med = hs[len(hs) // 2]
        if med < 35: continue
        good = sum(1 for h in on if abs(h - med) < 10) / len(on)
        # start and end need big roofs of that height
        best.append((good * cov, off, s0, med, ''.join('#' if h > 0 and abs(h - med) < 10 else ('^' if h > med else ('.' if h == 0 else 'v')) for h in prof)))
best.sort(reverse=True)
for b in best[:12]: print('%.2f off %d s0 %d med %d %s' % b)
