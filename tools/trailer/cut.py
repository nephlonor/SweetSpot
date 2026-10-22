# The cut: a list of segments on a beat grid, sfx and music plan are produced alongside the video frames
import json, math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import edit as E
from edit import W, H, FPS, YEL, WHT, GRN
BPM = 116.; BEAT = 60 / BPM; BF = BEAT * FPS      # frames per beat (14.516)
CL = '/tmp/pbs/clips'
class Clip:
    def __init__(self, name):
        self.name = name; self.dir = f'{CL}/{name}'; self.meta = json.load(open(self.dir + '/meta.json')); self.n = self.meta['n']
        fr = self.meta.get('frames'); self.f2n = {x['f']: x['n'] for x in fr} if fr else None
    def N(self, f):
        """clip frame number for swing frame f (the first captured one at or after f)"""
        if self.f2n is None: return f
        ks = sorted(self.f2n); import bisect; i = bisect.bisect_left(ks, f); return self.f2n[ks[min(i, len(ks) - 1)]]
    def ev(self, kind, k=0):
        l = [e['f'] for e in self.meta['evF'] if e['type'] == kind]; return l[k] if len(l) > k else None
_clips = {}
def clip(n): _clips[n] = _clips.get(n) or Clip(n); return _clips[n]
def src(c, x, blend=True):
    """frame x (float, clip frame numbers) with a blend between neighbours for slow motion"""
    x = min(max(x, 0), c.n - 1); a = int(math.floor(x)); u = x - a
    im = E.clip_frame({'dir': c.dir, 'n': c.n}, a)
    if blend and u > .08 and a + 1 < c.n: im = Image.blend(im, E.clip_frame({'dir': c.dir, 'n': c.n}, a + 1), u)
    return im
class Seg:
    """clip, runs: [(x0, x1, nOutFrames)] source clip-frame ranges played over nOutFrames output frames each; fx at output-frame offsets"""
    def __init__(self, c, runs, **kw):
        self.c = c; self.runs = runs; self.kw = kw; self.len = sum(r[2] for r in runs); self.start = 0
        self.zoom = kw.get('zoom', lambda t: 1.); self.pan = kw.get('pan', lambda t: (.5, .5)); self.punch = [(a, b * .55, c) for a, b, c in kw.get('punch', [])]; self.shake = [(a, b * .45, c) for a, b, c in kw.get('shake', [])]; self.flash = [(a, b * .5, c * 1.4) for a, b, c in kw.get('flash', [])]; self.rot = kw.get('rot', lambda t: 0.)
        self.speedramp = kw.get('ramp', None)
    def at(self, i):
        for (x0, x1, n) in self.runs:
            if i < n:
                u = i / max(1, n); return x0 + (x1 - x0) * (u if not self.speedramp else u)
            i -= n
        return self.runs[-1][1]
    def out_of(self, x):
        """output-frame offset (within the segment) at which clip frame x is shown"""
        o = 0
        for (x0, x1, n) in self.runs:
            lo, hi = min(x0, x1), max(x0, x1)
            if lo <= x <= hi: return o + (x - x0) / ((x1 - x0) or 1) * n
            o += n
        return o
    def frame(self, i):
        c = self.c; x = self.at(i); im = src(c, x)
        z = self.zoom(i / FPS); cx, cy = self.pan(i / FPS)
        for (t0, amp, dec) in self.punch:
            dt = i / FPS - t0
            if dt >= 0: z *= 1 + amp * math.exp(-dt / dec)
        ox = oy = 0
        for (t0, amp, dec) in self.shake:
            dt = i / FPS - t0
            if dt >= 0: a = amp * math.exp(-dt / dec); ox += a * math.sin(dt * 71); oy += a * math.cos(dt * 83)
        rot = self.rot(i / FPS)
        out = E.cover(im, z, cx, cy, rot)
        if ox or oy: out = out.transform(out.size, Image.AFFINE, (1, 0, -ox, 0, 1, -oy), resample=Image.BILINEAR)
        for (t0, a0, dec) in self.flash:
            dt = i / FPS - t0
            if dt >= 0:
                a = a0 * math.exp(-dt / dec)
                if a > .01: out = Image.blend(out, Image.new('RGB', out.size, (255, 255, 255)), min(1, a))
        return out
