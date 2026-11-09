# every hole north up on the Esri photo, with the built trees (circles at crown size; red broadleaf, blue cedar, yellow creek elm, white shrub), the line of play and its numbered tree indices near the line
import json, re, base64, struct, math, sys
from PIL import Image, ImageDraw
from cfg import *
src = open('data-fieldsranch.js').read(); D = json.loads(src[src.index(',')+1:src.rindex(');RDS')])
b = base64.b64decode(D['trees']); a = struct.unpack('<%dh' % (len(b)//2), b)
T = [(a[i]/10, a[i+1]/10, a[i+2]/10, a[i+3]//1000, (a[i+3] % 1000)/10) for i in range(0, len(a), 4)]
json.dump(T, open('trees_dec.json', 'w'))
H_ = json.loads(open('rd_head.js').read().split('=', 1)[1].rstrip(';'))
im = Image.open('course_esri.jpg').convert('RGB'); col = {0: (255, 60, 60), 2: (60, 160, 255), 6: (255, 230, 0), 1: (255, 255, 255)}
for k, h in enumerate(H_['holes']):
    L = h['line']; xs = [p[0] for p in L]; ys = [p[1] for p in L]; x0, x1, y0, y1 = min(xs)-70, max(xs)+70, min(ys)-70, max(ys)+70
    S = 2
    c = im.crop((int((x0-E0)*2), int((N0+H-y1)*2), int((x1-E0)*2), int((N0+H-y0)*2))); d = ImageDraw.Draw(c)
    m = lambda p: ((p[0]-x0)*S, (y1-p[1])*S)
    for i, (e, n, dd, kd, hh) in enumerate(T):
        if not (x0 < e < x1 and y0 < n < y1): continue
        X, Y = m((e, n)); r = dd/2*S; d.ellipse([X-r, Y-r, X+r, Y+r], outline=col.get(kd, (255, 0, 255)))
    d.line([m(p) for p in L], fill=(0, 255, 255), width=2)
    sc = min(1, 900/max(c.size)); c = c.resize((int(c.width*sc), int(c.height*sc))); c.save(f'trees/h{k+1:02d}.jpg', quality=82)
