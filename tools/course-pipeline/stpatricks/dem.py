# ground model: Esri World Elevation (Terrain3D) LERC tiles at z16 (~1.37 m here), resampled to the local 1 m grid (row 0 = south)
import math,urllib.request,lerc,numpy as np
from concurrent.futures import ThreadPoolExecutor
from scipy import ndimage as ndi
LAT0,LON0=55.1640,-7.8220;kx=111320*math.cos(math.radians(LAT0));ky=111132.0
ME0,MN0,W,H=-750,-970,1500,1950
B="https://elevation3d.arcgis.com/arcgis/rest/services/WorldElevation3D/Terrain3D/ImageServer/tile"
z=16;N=2**z
def txy(lat,lon): return (lon+180)/360*N,(1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*N
x0,y0=txy(LAT0+(MN0+H)/ky,LON0+ME0/kx);x1,y1=txy(LAT0+MN0/ky,LON0+(ME0+W)/kx)
ix0,iy0,ix1,iy1=int(x0),int(y0),int(x1),int(y1)
def get(a):
    i,j=a
    for t in range(4):
        try: return lerc.decode(urllib.request.urlopen(f"{B}/{z}/{j}/{i}",timeout=30).read())[1][:256,:256]
        except Exception as e: err=e
    raise err
jobs=[(i,j) for j in range(iy0,iy1+1) for i in range(ix0,ix1+1)]
tiles=dict(zip(jobs,ThreadPoolExecutor(12).map(get,jobs)))
M=np.vstack([np.hstack([tiles[(i,j)] for i in range(ix0,ix1+1)]) for j in range(iy0,iy1+1)]).astype(float)
E,Nn=np.meshgrid(np.arange(W)+ME0+.5,np.arange(H)+MN0+.5)
lat=LAT0+Nn/ky;lon=LON0+E/kx
tx=(lon+180)/360*N;ty=(1-np.arcsinh(np.tan(np.radians(lat)))/np.pi)/2*N
px=(tx-ix0)*256-.5;py=(ty-iy0)*256-.5
G=ndi.map_coordinates(M,[py,px],order=3)
np.save('mnt.npy',G.astype(np.float32))
print(G.shape,G.min(),G.max(),np.isnan(G).sum())
