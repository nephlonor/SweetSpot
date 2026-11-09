# no LiDAR canopy here: a canopy height model from the Esri photograph (winter, leaf-off hardwoods read dark grey-brown and textured, cedars dark green):
# dark, textured pixels off the water -> tree cover; heights from the distance into the cover (6-15 m, the cross timbers' post oak, cedar elm and red cedar) -> mnh.npy
import json, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from cfg import *
im = np.asarray(Image.open('course_esri.jpg').convert('RGB'), float)
v = im.mean(2); g = im[..., 1] - (im[..., 0] + im[..., 2])/2
mu = ndi.uniform_filter(v, 13); sd = np.sqrt(np.clip(ndi.uniform_filter(v*v, 13) - mu*mu, 0, None))
tree = (mu < 78) & (sd > 12) & (ndi.maximum_filter(ndi.uniform_filter(v, 3), 11) < 135)   # (not the edge of a bright road, roof or sand)
F = json.load(open('features.json'))
m = Image.new('L', (im.shape[1], im.shape[0]), 0); d = ImageDraw.Draw(m)
for p in F['ponds'] + F['fair'] + list(F['greens'].values()) + F['tees'] + F['sand'] + F['buildings']:
    d.polygon([((x-E0)*2, (N0+H-y)*2) for x, y in p], fill=255)
tree &= ~ndi.binary_dilation(np.array(m) > 0, iterations=4)
# not in the housing and along the streets outside the course: the lawns and the young street trees read like canopy (OSM roads and buildings, 22 m either side, outside the course's own outline)
import math, xml.etree.ElementTree as ET
KX = 111320*math.cos(math.radians(LAT0)); KY = 111132.0
R_ = ET.parse('r.osm').getroot(); nd = {n.get('id'): ((float(n.get('lon'))-LON0)*KX, (float(n.get('lat'))-LAT0)*KY) for n in R_.findall('node')}
rd = Image.new('L', (im.shape[1], im.shape[0]), 0); dr = ImageDraw.Draw(rd)
for w in R_.findall('way'):
    tg = {k.get('k'): k.get('v') for k in w.findall('tag')}
    if tg.get('highway') in ('residential', 'living_street', 'tertiary', 'secondary', 'primary', 'unclassified', 'service') or tg.get('building'):
        p = [nd[x.get('ref')] for x in w.findall('nd') if x.get('ref') in nd]
        if len(p) > 1: dr.line([((x-E0)*2, (N0+H-y)*2) for x, y in p], fill=255, width=88)
own = Image.new('L', (im.shape[1], im.shape[0]), 0); ImageDraw.Draw(own).polygon([((x-E0)*2, (N0+H-y)*2) for x, y in json.load(open('feat.json'))['out']['boundary'][0]['pts']], fill=255)
ImageDraw.Draw(rd).polygon([((x-E0)*2, (N0+H-y)*2) for x, y in RESIDENTIAL], fill=255)
tree &= ~((np.array(rd) > 0) & ~ndi.binary_dilation(np.array(own) > 0, iterations=10))
tree = ndi.binary_opening(ndi.binary_closing(ndi.median_filter(tree, 5), iterations=3), iterations=5)
lab, n = ndi.label(tree); sz = np.bincount(lab.ravel()); tree &= sz[lab] >= 40   # (>= 10 m2)
tree = tree.reshape(H, 2, W, 2).mean(axis=(1, 3)) > .5   # to the 1 m grid, north up
tree = ndi.binary_opening(tree, structure=np.ones((3, 3)), iterations=2)   # (drops thin lines: path and kerb edges)
dist = ndi.distance_transform_edt(tree)
rng = np.random.default_rng(3); jitter = ndi.gaussian_filter(rng.standard_normal(tree.shape), 3); jitter /= jitter.std()
h = np.where(tree, np.clip(5 + 1.6*dist + 1.5*jitter, 3, 15), 0)
h = ndi.gaussian_filter(h, 1.0)*(tree | ndi.binary_dilation(tree, iterations=1))
mnh = h[::-1].astype(np.float32)   # row 0 = south, like mnt.npy
mnh[mnh < .3] = 0
np.save('mnh.npy', mnh); print('tree cover', tree.mean(), 'cells > 5 m', int((mnh > 5).sum()))
Image.fromarray((np.clip(h/15, 0, 1)*255).astype(np.uint8)).resize((1150, 950)).save('chm.png')
