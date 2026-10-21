import glob, math, numpy as np, laspy
LAT0, LON0 = 36.5645, -121.9410; KX = 111320*math.cos(math.radians(LAT0)); KY = 111132.0; R = 6378137.0
E0, N0, W, H = -1000, -950, 2300, 1800
s = np.zeros((H, W), np.float64); n_ = np.zeros((H, W), np.int32)
for f in glob.glob('ept/*.laz'):
    L = laspy.read(f)
    x = np.asarray(L.x); y = np.asarray(L.y); z = np.asarray(L.z); c = np.asarray(L.classification)
    lon = np.degrees(x/R); lat = np.degrees(2*np.arctan(np.exp(y/R)) - math.pi/2)
    e = (lon-LON0)*KX; n = (lat-LAT0)*KY
    i = np.floor(e-E0).astype(int); j = np.floor(n-N0).astype(int)
    ok = (i >= 0) & (i < W) & (j >= 0) & (j < H) & (c == 2)
    np.add.at(s, (j[ok], i[ok]), z[ok]); np.add.at(n_, (j[ok], i[ok]), 1)
g = np.where(n_ > 0, s/np.maximum(n_, 1), np.nan).astype(np.float32)
np.save('gnd_raw.npy', g); np.save('gnd_n.npy', n_)
print('ground cells', (n_ > 0).mean())
