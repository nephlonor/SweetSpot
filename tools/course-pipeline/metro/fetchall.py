import sys, math, osm
from areas import AREAS
for k, (la, lo, R) in AREAS.items():
    if len(sys.argv) > 1 and k not in sys.argv[1:]: continue
    dla, dlo = R / 110574, R / (111320 * math.cos(math.radians(la)))
    fs = osm.tiles(la - dla, lo - dlo, la + dla, lo + dlo); print(k, len(fs), flush=True)
