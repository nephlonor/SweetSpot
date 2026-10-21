import math, urllib.request, urllib.parse, numpy as np, tifffile, io, sys, os, time
LAT0, LON0 = 36.5645, -121.9410
KX = 111320*math.cos(math.radians(LAT0)); KY = 111132.0
E0, E1, N0, N1 = -1000, 1300, -950, 850   # 1 m cells
T = 4000
H = N1-N0; W = E1-E0; M = np.full((H, W), np.nan, np.float32)
for j0 in range(0, H, T):
    for i0 in range(0, W, T):
        w = min(T, W-i0); h = min(T, H-j0)
        e_a, e_b = E0+i0, E0+i0+w; n_b, n_a = N1-j0, N1-j0-h
        bbox = f"{LON0+e_a/KX},{LAT0+n_a/KY},{LON0+e_b/KX},{LAT0+n_b/KY}"
        q = urllib.parse.urlencode({'bbox': bbox, 'bboxSR': 4326, 'imageSR': 4326, 'size': f'{w},{h}', 'format': 'tiff', 'pixelType': 'F32', 'interpolation': 'RSP_BilinearInterpolation', 'f': 'image'})
        for t in range(5):
            try:
                d = urllib.request.urlopen('https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/exportImage?' + q, timeout=120).read()
                a = tifffile.imread(io.BytesIO(d)); break
            except Exception as ex: print('retry', ex, flush=True); time.sleep(2)
        M[j0:j0+h, i0:i0+w] = a[:h, :w]
        print(j0, i0, a.shape, float(np.nanmin(a)), float(np.nanmax(a)), flush=True)
M = M[::-1]   # row 0 = N0 (south), like mnt.npy
np.save('mnt.npy', M); print('done', M.shape, np.nanmin(M), np.nanmax(M))
