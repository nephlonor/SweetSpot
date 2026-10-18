import glob, math, numpy as np, laspy
LAT0, LON0 = 33.4995, -82.0225; KX = 111320*math.cos(math.radians(LAT0)); KY = 111132.0; R = 6378137.0
E0, N0, W, H = -900, -900, 1800, 2050
dsm = np.full((H, W), -1e9, np.float32); cnt = np.zeros((H, W), np.int32); gnd = np.full((H, W), np.nan, np.float32)
cls = np.zeros(20, np.int64)
for f in glob.glob('ept/*.laz'):
    L = laspy.read(f)
    x = np.asarray(L.x); y = np.asarray(L.y); z = np.asarray(L.z); c = np.asarray(L.classification)
    lon = np.degrees(x/R); lat = np.degrees(2*np.arctan(np.exp(y/R)) - math.pi/2)
    e = (lon-LON0)*KX; n = (lat-LAT0)*KY
    i = np.floor(e-E0).astype(int); j = np.floor(n-N0).astype(int)
    ok = (i >= 0) & (i < W) & (j >= 0) & (j < H) & (c != 7) & (c != 18)
    np.add.at(cls, np.clip(c[ok], 0, 19), 1)
    np.maximum.at(dsm, (j[ok], i[ok]), z[ok]); np.add.at(cnt, (j[ok], i[ok]), 1)
print('classes', {k: int(v) for k, v in enumerate(cls) if v})
print('density', cnt.mean(), (cnt == 0).mean())
np.save('dsm.npy', dsm); np.save('cnt.npy', cnt)
