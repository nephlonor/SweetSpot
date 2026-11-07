# ground (class 2 cell means, gaps filled from the nearest ground cell and smoothed) and canopy height (surface - ground) -> mnt.npy, mnh.npy
import numpy as np
from scipy import ndimage as ndi
g = np.load('gnd_raw.npy'); dsm = np.load('dsm.npy'); cnt = np.load('cnt.npy')
m = ~np.isnan(g)
idx = ndi.distance_transform_edt(~m, return_distances=False, return_indices=True)
f = ndi.gaussian_filter(g[tuple(idx)], 2.0)
mnt = np.where(m, ndi.gaussian_filter(np.where(m, g, f), 0.7), f).astype(np.float32)
d = dsm - mnt
mnh = np.where(cnt > 0, np.clip(d, 0, 60), 0).astype(np.float32); mnh[mnh < 0.3] = 0
print('ground', np.percentile(mnt, [1, 50, 99]), 'canopy >5 m cells', int((mnh > 5).sum()), 'ground cells measured', float(m.mean()))
np.save('mnt.npy', mnt); np.save('mnh.npy', mnh)
