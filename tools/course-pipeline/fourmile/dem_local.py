# the 1 m USGS ground (UTM 13N) resampled onto the local grid: 1 m cells, row 0 = south (N0), column 0 = west (E0) -> mnt_dem.npy
import math, numpy as np, tifffile
from scipy.ndimage import map_coordinates
from pyproj import Transformer
LAT0, LON0 = 38.4675, -105.1655; KX = 111320*math.cos(math.radians(LAT0)); KY = 111132.0
E0, N0, W, H = -1000, -1140, 2100, 2250
A = tifffile.imread('dem1m.tif').astype(np.float32); A[A < -1000] = np.nan
X0, Y0 = 479993.99996, 4260006.0     # top-left corner of the tile (UTM 13N), 1 m cells
tr = Transformer.from_crs(4326, 26913, always_xy=True)
e = E0 + np.arange(W) + .5; n = N0 + np.arange(H) + .5
EE, NN = np.meshgrid(e, n)
x, y = tr.transform(LON0 + EE/KX, LAT0 + NN/KY)
col = x - X0 - .5; row = Y0 - y - .5
nanm = np.isnan(A); Af = np.where(nanm, np.nanmedian(A), A)
M = map_coordinates(Af, [row.ravel(), col.ravel()], order=1, mode='nearest').reshape(H, W).astype(np.float32)
bad = map_coordinates(nanm.astype(np.float32), [row.ravel(), col.ravel()], order=1, mode='nearest').reshape(H, W) > 0.01
print('ground', np.nanmin(M), np.nanmedian(M), np.nanmax(M), 'nodata cells', int(bad.sum()))
np.save('mnt_dem.npy', M)
