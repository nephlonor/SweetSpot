# the USGS point-cloud tiles (CO_CONMGaps_D24) -> 1 m local grids: ground (class 2 cell mean), surface (highest non-noise return) and building cells (class 6)
import glob, math, sys, numpy as np, laspy
from pyproj import Transformer
LAT0, LON0 = 38.4675, -105.1655; KX = 111320*math.cos(math.radians(LAT0)); KY = 111132.0
E0, N0, W, H = -1000, -1140, 2100, 2250
gs = np.zeros(W*H); gn = np.zeros(W*H, np.int64); dsm = np.full(W*H, -1e9, np.float32); cnt = np.zeros(W*H, np.int64); bld = np.zeros(W*H, np.int64); veg = np.zeros(W*H, np.int64)
cls = np.zeros(32, np.int64); tr = None
for f in sorted(glob.glob('laz/*.laz')):
    with laspy.open(f) as rd:
        if tr is None:
            crs = rd.header.parse_crs(); print('crs', crs.to_epsg() if crs else None, flush=True); tr = Transformer.from_crs(crs if crs else 26913, 4326, always_xy=True)
        print(f, rd.header.point_count, flush=True)
        for pts in rd.chunk_iterator(4_000_000):
            lon, lat = tr.transform(np.asarray(pts.x), np.asarray(pts.y)); z = np.asarray(pts.z); c = np.asarray(pts.classification)
            e = (lon-LON0)*KX; n = (lat-LAT0)*KY; i = np.floor(e-E0).astype(np.int64); j = np.floor(n-N0).astype(np.int64)
            ok = (i >= 0) & (i < W) & (j >= 0) & (j < H); i, j, z, c = i[ok], j[ok], z[ok], c[ok]; k = j*W + i
            cls += np.bincount(np.clip(c, 0, 31), minlength=32)[:32]
            g = c == 2; gs += np.bincount(k[g], weights=z[g], minlength=W*H); gn += np.bincount(k[g], minlength=W*H)
            s = (c != 7) & (c != 18); np.maximum.at(dsm, k[s], z[s].astype(np.float32)); cnt += np.bincount(k[s], minlength=W*H)
            bld += np.bincount(k[c == 6], minlength=W*H); veg += np.bincount(k[(c >= 3) & (c <= 5)], minlength=W*H)
print('classes', {int(q): int(v) for q, v in enumerate(cls) if v})
g = np.where(gn > 0, gs/np.maximum(gn, 1), np.nan).astype(np.float32).reshape(H, W)
np.save('gnd_raw.npy', g); np.save('dsm.npy', dsm.reshape(H, W)); np.save('cnt.npy', cnt.reshape(H, W).astype(np.int32)); np.save('bld.npy', bld.reshape(H, W).astype(np.int32)); np.save('veg.npy', veg.reshape(H, W).astype(np.int32))
print('ground cells measured', float((gn > 0).mean()), 'density', cnt.mean())
