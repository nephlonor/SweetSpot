import json, math, urllib.request, os, sys, numpy as np, laspy
from concurrent.futures import ThreadPoolExecutor
B = 'https://s3-us-west-2.amazonaws.com/usgs-lidar-public/CA_FEMA_Z4_B1_2018/'
LAT0, LON0 = 36.5645, -121.9410; KX = 111320*math.cos(math.radians(LAT0)); KY = 111132.0
R = 6378137.0
def merc(e, n):
    lat = LAT0 + n/KY; lon = LON0 + e/KX
    return math.radians(lon)*R, R*math.log(math.tan(math.pi/4 + math.radians(lat)/2))
X0, Y0 = merc(-1000, -950); X1, Y1 = merc(1300, 850)
info = json.load(urllib.request.urlopen(B + 'ept.json')); bx = info['bounds']
MAXD = int(sys.argv[1]) if len(sys.argv) > 1 else 13
def get(u):
    for t in range(5):
        try: return urllib.request.urlopen(u, timeout=120).read()
        except Exception as ex: print('retry', u, ex, flush=True)
def hier(key):
    return json.loads(get(B + 'ept-hierarchy/' + key + '.json'))
H = hier('0-0-0-0'); nodes = []
def walk(d, x, y, z):
    key = f'{d}-{x}-{y}-{z}'; s = (bx[3]-bx[0])/2**d
    ax, ay = bx[0] + x*s, bx[1] + y*s
    if ax > X1 or ax + s < X0 or ay > Y1 or ay + s < Y0: return
    if key not in H: return
    if H[key] == -1: H.update(hier(key))
    if H[key] > 0: nodes.append(key)
    if d >= MAXD: return
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1): walk(d+1, 2*x+dx, 2*y+dy, 2*z+dz)
walk(0, 0, 0, 0)
print("nodes", len(nodes), "points", sum(H[k] for k in nodes), "maxdepth", max(int(k.split("-")[0]) for k in nodes), flush=True)
if len(sys.argv) > 2: sys.exit()
def fetch(k):
    fn = 'ept/' + k + '.laz'
    if not os.path.exists(fn): open(fn, 'wb').write(get(B + 'ept-data/' + k + '.laz'))
    return k
with ThreadPoolExecutor(12) as ex:
    for i, k in enumerate(ex.map(fetch, nodes)):
        if i % 50 == 0: print(i, len(nodes), flush=True)
print('fetched')
