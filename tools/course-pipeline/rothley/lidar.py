import math, urllib.request, numpy as np, tifffile, io, pyproj, sys
from scipy import ndimage as ndi
LAT0, LON0 = 52.7000, -1.1500
KX = 111320*math.cos(math.radians(LAT0)); KY = 111132.0
E0, E1, N0, N1 = -800, 1000, -900, 850
t = pyproj.Transformer.from_crs(4326, 27700, always_xy=True)
cs = [t.transform(LON0+e/KX, LAT0+n/KY) for e in (E0, E1) for n in (N0, N1)]
X0 = math.floor(min(c[0] for c in cs))-20; X1 = math.ceil(max(c[0] for c in cs))+20
Y0 = math.floor(min(c[1] for c in cs))-20; Y1 = math.ceil(max(c[1] for c in cs))+20
print('bng', X0, X1, Y0, Y1)
def fetch(cov, svc):
    M = np.full((Y1-Y0, X1-X0), np.nan, np.float32); T = 600
    for y in range(Y0, Y1, T):
        for x in range(X0, X1, T):
            x1 = min(x+T, X1); y1 = min(y+T, Y1)
            u = f'https://environment.data.gov.uk/spatialdata/{svc}/wcs?service=WCS&version=2.0.1&request=GetCoverage&coverageId={cov}&format=image/tiff&subset=E({x},{x1})&subset=N({y},{y1})'
            for k in range(5):
                try: a = tifffile.imread(io.BytesIO(urllib.request.urlopen(u, timeout=180).read())); break
                except Exception as ex: print('retry', ex, flush=True)
            a = a.astype(np.float32); a[a < -1000] = np.nan
            M[Y1-y1 - (Y1-Y0) + (Y1-Y0) - (Y1 - y1) + (Y1-y1):, :][:0]  # noop
            r0 = Y1 - y1; M[r0:r0+a.shape[0], x-X0:x-X0+a.shape[1]] = a[:y1-y, :x1-x]
            print(svc[:30], x, y, a.shape, np.nanmin(a), np.nanmax(a), flush=True)
    return M   # row 0 = north (Y1)
def resample(M):
    inv = pyproj.Transformer.from_crs(4326, 27700, always_xy=True)
    ee, nn = np.meshgrid(np.arange(E0, E1)+.5, np.arange(N0, N1)+.5)
    X, Y = inv.transform(LON0+ee/KX, LAT0+nn/KY)
    r = (Y1 - Y) - .5; c = (X - X0) - .5
    return ndi.map_coordinates(np.nan_to_num(M, nan=np.nanmin(M)), [r, c], order=1).astype(np.float32)   # row 0 = south (N0)
dtm = fetch('13787b9a-26a4-4775-8523-806d13af58fc__Lidar_Composite_Elevation_DTM_1m', 'lidar-composite-digital-terrain-model-dtm-1m')
dsm = fetch('df4e3ec3-315e-48aa-aaaf-b5ae74d7b2bb__Lidar_Composite_Elevation_FZ_DSM_1m', 'lidar-composite-digital-surface-model-first-return-dsm-1m')
print('nan', np.isnan(dtm).mean(), np.isnan(dsm).mean())
G = resample(dtm); S = resample(dsm)
np.save('mnt.npy', G); np.save('mnh.npy', np.clip(S-G, 0, 60)); print('done', G.shape, G.min(), G.max())
