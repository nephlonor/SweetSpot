# Trailer editor: cuts, speed ramps, punch zooms, shake, flashes and kinetic captions over the captured game frames; frames go straight into ffmpeg
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H, FPS = 1080, 1920, 30
FONT = '/usr/share/fonts/opentype/inter/InterDisplay-Black.otf'
FONTI = '/usr/share/fonts/opentype/inter/InterDisplay-BlackItalic.otf'
YEL, WHT, GRN = (247, 220, 46), (255, 255, 255), (141, 206, 105)
_cache = {}
def font(sz, it=False): k = (sz, it); _cache[k] = _cache.get(k) or ImageFont.truetype(FONTI if it else FONT, sz); return _cache[k]
_img = {}
def load(path):
    if path not in _img:
        if len(_img) > 160: _img.clear()
        _img[path] = Image.open(path).convert('RGB')
    return _img[path]
def ease_out_back(u, s=1.9): u = min(1, max(0, u)); return 1 + (s + 1) * (u - 1) ** 3 + s * (u - 1) ** 2
def clip_frame(clip, i):
    n = clip['n']; i = int(round(min(max(i, 0), n - 1)))
    return load(f"{clip['dir']}/f{i:04d}.jpg")
def cover(img, zoom=1., cx=.5, cy=.5, rot=0.):
    w, h = img.size; s = max(W / w, H / h) * zoom
    if abs(rot) > 1e-3: img = img.rotate(rot, resample=Image.BICUBIC, expand=False)
    nw, nh = int(w * s), int(h * s); r = img.resize((nw, nh), Image.BICUBIC)
    x0 = int((nw - W) * cx); y0 = int((nh - H) * cy); return r.crop((x0, y0, x0 + W, y0 + H))
def text_layer(lines, size, pos, t, color=WHT, it=True, outline=14, rot=-4, anchor='c', pop=.22, align='c'):
    """kinetic caption: pops in with overshoot, rotated a few degrees, thick dark outline and a coloured drop shadow"""
    if t < 0: return None
    sc = ease_out_back(t / pop) if t < pop else 1.0
    if sc <= .02: return None
    f = font(int(size * sc), it); lay = Image.new('RGBA', (W * 2, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    y = 0; items = []
    for ln in lines:
        c = color; txt = ln
        if isinstance(ln, tuple): txt, c = ln
        bb = d.textbbox((0, 0), txt, font=f, stroke_width=outline); items.append((txt, c, bb)); y += bb[3] - bb[1] + int(size * sc * .06)
    tw = max(b[2] - b[0] for _, _, b in items); th = y; ox, oy = 40, 40
    box = Image.new('RGBA', (tw + 2 * ox + 40, th + 2 * oy + 40), (0, 0, 0, 0)); bd = ImageDraw.Draw(box); yy = oy
    for txt, c, bb in items:
        x = ox + ((tw - (bb[2] - bb[0])) / 2 if align == 'c' else 0) - bb[0]
        bd.text((x + 8, yy - bb[1] + 10), txt, font=f, fill=(0, 30, 10, 190), stroke_width=outline, stroke_fill=(0, 30, 10, 190))
        bd.text((x, yy - bb[1]), txt, font=f, fill=c + (255,), stroke_width=outline, stroke_fill=(10, 40, 18, 255))
        yy += bb[3] - bb[1] + int(size * sc * .06)
    if rot: box = box.rotate(rot, resample=Image.BICUBIC, expand=True)
    return box, pos
def paste_center(base, layer, pos):
    box, (cx, cy) = layer; base.paste(box, (int(cx - box.width / 2), int(cy - box.height / 2)), box)
def vignette():
    y, x = np.mgrid[0:H, 0:W]; r = np.sqrt(((x - W / 2) / (W * .75)) ** 2 + ((y - H / 2) / (H * .7)) ** 2); return np.clip(1 - .24 * np.clip(r - .55, 0, 1) ** 1.3 / .45, .7, 1)[..., None].astype(np.float32)
VIG = vignette()
class Writer:
    def __init__(self, out, audio=None):
        cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-']
        if audio: cmd += ['-i', audio]
        cmd += ['-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-movflags', '+faststart']
        if audio: cmd += ['-c:a', 'aac', '-b:a', '256k', '-shortest']
        self.p = subprocess.Popen(cmd + [out], stdin=subprocess.PIPE); self.n = 0
    def put(self, im): self.p.stdin.write(np.asarray(im.convert('RGB'), dtype=np.uint8).tobytes()); self.n += 1
    def close(self): self.p.stdin.close(); self.p.wait()
