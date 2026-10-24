import math,urllib.request,io,sys
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
LAT0,LON0=38.4675,-105.1655;kx=111320*math.cos(math.radians(LAT0));ky=111132.0
def tile(e_,n_,z):
    N=2**z; lat=LAT0+n_/ky;lon=LON0+e_/kx;return (lon+180)/360*N,(1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*N
def get(i,j,z):
    u=f"https://mt1.google.com/vt/lyrs=s&x={i}&y={j}&z={z}"
    for t in range(4):
        try: return Image.open(io.BytesIO(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read())).convert('RGB')
        except Exception: pass
    return Image.new('RGB',(256,256))
def mosaic(e0,n0,e1,n1,z=19,res=0.5):
    """an image of the box [e0,e1]x[n0,n1] resampled to res m/px, north up"""
    x0,y0=tile(e0,n1,z);x1,y1=tile(e1,n0,z)
    ix0,iy0,ix1,iy1=int(x0),int(y0),int(x1),int(y1)
    W=Image.new('RGB',((ix1-ix0+1)*256,(iy1-iy0+1)*256))
    jobs=[(i,j) for i in range(ix0,ix1+1) for j in range(iy0,iy1+1)]
    with ThreadPoolExecutor(16) as ex:
        for (i,j),im in zip(jobs,ex.map(lambda a:get(a[0],a[1],z),jobs)): W.paste(im,((i-ix0)*256,(j-iy0)*256))
    # resample to the local metric grid (mercator is locally linear but y scale varies slightly: map each output row)
    w=int((e1-e0)/res); h=int((n1-n0)/res); out=Image.new('RGB',(w,h))
    # affine approx using the corners (fine at this scale)
    ax=(x1-x0)*256/w; ay=(y1-y0)*256/h
    out=W.transform((w,h),Image.AFFINE,(ax,0,(x0-ix0)*256,0,ay,(y0-iy0)*256),Image.BILINEAR)
    return out
if __name__=='__main__':
    e0,n0,e1,n1,z,res,name=sys.argv[1:8]
    mosaic(float(e0),float(n0),float(e1),float(n1),int(z),float(res)).save(name,quality=88)
