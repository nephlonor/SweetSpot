"""Metropolis Links: download OpenStreetMap data (api.openstreetmap.org, map call) in tiles and cache it.
usage: python3 osm.py south west north east   (degrees)"""
import os, sys, time, subprocess, hashlib
CACHE = os.environ.get('MT_CACHE', '/tmp/metro-osm')
os.makedirs(CACHE, exist_ok=True)
def get(s, w, n, e):
    fn = os.path.join(CACHE, '%.5f_%.5f_%.5f_%.5f.osm' % (s, w, n, e))
    if os.path.exists(fn) and os.path.getsize(fn) > 0: return [fn]
    url = 'https://api.openstreetmap.org/api/0.6/map?bbox=%.5f,%.5f,%.5f,%.5f' % (w, s, e, n)
    for k in range(4):
        r = subprocess.run(['curl', '-sS', '-m', '120', '-w', '%{http_code}', '-o', fn + '.part', url], capture_output=True, text=True)
        code = r.stdout.strip()
        if code == '200': os.rename(fn + '.part', fn); return [fn]
        if code in ('400', '509'):  # too many nodes: split in four
            if os.path.exists(fn + '.part'): os.remove(fn + '.part')
            ms, mw = (s + n) / 2, (w + e) / 2
            return get(s, w, ms, mw) + get(s, mw, ms, e) + get(ms, w, n, mw) + get(ms, mw, n, e)
        time.sleep(2 ** k * 2)
    raise SystemExit('failed ' + url + ' ' + code)
def relation_full(rid):
    fn = os.path.join(CACHE, 'rel_%s.osm' % rid)
    if os.path.exists(fn) and os.path.getsize(fn) > 0: return fn
    url = 'https://api.openstreetmap.org/api/0.6/relation/%s/full' % rid
    for k in range(4):
        r = subprocess.run(['curl', '-sS', '-m', '180', '-w', '%{http_code}', '-o', fn + '.part', url], capture_output=True, text=True)
        if r.stdout.strip() == '200': os.rename(fn + '.part', fn); return fn
        time.sleep(2 ** k * 2)
    raise SystemExit('failed ' + url)
def tiles(s, w, n, e, step=.006):
    out = []; y = s
    while y < n - 1e-9:
        x = w
        while x < e - 1e-9:
            out += get(y, x, min(n, y + step), min(e, x + step)); x += step
        y += step
    return out
if __name__ == '__main__':
    s, w, n, e = map(float, sys.argv[1:5]); fs = tiles(s, w, n, e); print(len(fs), 'tiles')
