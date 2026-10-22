# node/python pipeline: python3 trailer.py [preview]   -> /tmp/pbs/trailer_silent.mp4, /tmp/pbs/plan.json; then music + mux
import json, math, sys, os
import numpy as np
from PIL import Image
import edit as E
from edit import W, H, FPS, YEL, WHT, GRN
from cut import *
PREVIEW = len(sys.argv) > 1 and sys.argv[1] == 'preview'
ORANGE = (255, 150, 60)
sfx = []
def EV(s, c, kind, k=0, off=0.): 
    f = c.ev(kind, k); return None if f is None else s.beat * BEAT + (s.out_of(c.N(f)) + off) / FPS
def S(t, kind, v=1., **kw): sfx.append(dict(t=round(t, 3), kind=kind, v=v, **kw))
segs = []   # (startBeat, Seg, captions)
def seg(beat, c, runs, caps=(), **kw):
    s = Seg(c, runs, **kw); s.caps = list(caps); s.beat = beat; segs.append(s); return s
def cap(t0, t1, lines, size=150, pos=(540, 470), color=WHT, rot=-4, it=True, outline=14): return dict(t0=t0, t1=t1, lines=lines, size=size, pos=pos, color=color, rot=rot, it=it, outline=outline)
def run_frames(beats): return int(round(beats * BF))
# ---------------------------------------------------------------- S0 hook
def build():
    global segs; segs = []
    fm = clip('fly_mv'); fa = clip('fly_aug')
    L = run_frames(4)
    seg(0, fm, [(0, 62, L)], caps=[cap(.12, 1.0, ['TWO', 'THUMBS.'], 210, (540, 640), YEL, -4), cap(1.0, 1.95, ['ONE', 'SWING.'], 230, (540, 1250), WHT, 3)], zoom=lambda t: 1 + .05 * t, flash=[(0, .9, .09)], punch=[(0, .06, .1), (.97, .08, .1)])
    # ------------------------------------------------------------ S1 hero swing
    h = clip('hero'); iF = h.meta['impactF']; lf = h.ev('land'); sf = h.ev('stop')
    L = run_frames(8); a = 34; b = 22
    seg(4, h, [(h.N(20), h.N(iF), a), (h.N(iF), h.N(iF + 25), b), (h.N(lf - 22), h.N(sf + 12), L - a - b)],
        caps=[cap(a / FPS + .05, a / FPS + 1.0, ['SWEET.'], 230, (540, 520), YEL, -5), cap((a + b) / FPS + 1.0, 4, ['TAP-IN', 'RANGE.'], 120, (540, 470), WHT, 3)],
        punch=[(0, .06, .1), (a / FPS, .1, .12)], shake=[(a / FPS, 12, .15)], flash=[(0, .6, .06), (a / FPS, .5, .07)])
    S(4 * BEAT + (a - 1) / FPS, 'thwack'); S(4 * BEAT + (a - 4) / FPS, 'whoosh', .6, d=.25)
    S(4 * BEAT + (a + b + 2) / FPS, 'whoosh', .5, d=.5, up=False)
    # ------------------------------------------------------------ S2 trees
    t = clip('trees'); iF = t.meta['impactF']; ft = t.ev('tree', 0); ft2 = t.ev('tree', 1)
    L = run_frames(7); a = 20; b = 18
    seg(12, t, [(t.N(30), t.N(iF), a), (t.N(iF), t.N(iF + 22), b), (t.N(ft - 20), t.N(ft + 34), L - a - b)],
        caps=[cap(.1, a / FPS + .5, ['CROOKED', 'THUMB...'], 140, (540, 470), WHT, -3), cap((a + b) / FPS + .55, 3.4, ['TIMBER.'], 210, (540, 520), ORANGE, 4)],
        punch=[(0, .06, .1), (a / FPS, .1, .12)], shake=[(a / FPS, 12, .15), ((a + b) / FPS + .62, 18, .2)], flash=[(0, .5, .06), (a / FPS, .4, .07)])
    S(12 * BEAT + (a - 1) / FPS, 'thwack', .9); S(12 * BEAT + (a - 4) / FPS, 'whoosh', .6, d=.25)
    s2 = segs[-1]; S(EV(s2, t, 'tree', 0), 'thud', 1.0); S(EV(s2, t, 'tree', 0), 'leaves', .8)
    if ft2 is not None: S(EV(s2, t, 'tree', 1), 'thud', .8)
    # ------------------------------------------------------------ S3 splash
    sp = clip('splash'); iF = sp.meta['impactF']; fs = sp.ev('splash'); fl = sp.ev('land')
    L = run_frames(6); a = 14; b = 20
    seg(19, sp, [(sp.N(38), sp.N(iF), a), (sp.N(iF), sp.N(iF + 26), b), (sp.N((fs or fl) - 30), sp.N((fs or fl) + 11), L - a - b)],
        caps=[cap(.05, a / FPS + .4, ['THUMB', 'SLIPS...'], 120, (540, 470), WHT, -3), cap((a + b) / FPS + .9, 2.9, ['SPLASH.'], 230, (540, 520), (120, 210, 255), 3)],
        punch=[(0, .06, .1), (a / FPS, .1, .12)], shake=[(a / FPS, 12, .15)], flash=[(0, .5, .06), (a / FPS, .4, .07)],
        zoom=lambda t: 1 + .7 * min(1, max(0, (t - (a + b) / FPS) / 1.1)), pan=lambda t: (.5 + .13 * min(1, max(0, (t - (a + b) / FPS) / 1.1)), .5 + .5 * min(1, max(0, (t - (a + b) / FPS) / 1.1))))
    S(19 * BEAT + (a - 1) / FPS, 'thwack', .8); S(19 * BEAT + (a - 4) / FPS, 'whoosh', .6, d=.25)
    s3 = segs[-1]; S(EV(s3, sp, 'splash'), 'splash', 1.0); S(EV(s3, sp, 'splash', 0, 10), 'trombone', .6)
    for k in range(4):
        e = EV(s3, sp, 'bounce', k)
        if e: S(e, 'bounce', .35, f=520)
    # ------------------------------------------------------------ S3b too slow
    sl = clip('slow'); iF = sl.meta['impactF']; lf = sl.ev('land')
    L = run_frames(4); a = 24; b = L - a
    seg(25, sl, [(sl.N(20), sl.N(iF), a), (sl.N(iF), sl.N(iF + 40), b)],
        caps=[cap(.1, a / FPS + .1, ['TOO', 'SLOW.'], 230, (540, 470), (255, 120, 90), -4), cap(a / FPS + .35, 1.9, ['POWER? GONE.'], 100, (540, 560), WHT, 3)],
        punch=[(0, .06, .1), (a / FPS, .08, .12)], shake=[(a / FPS, 8, .15)], flash=[(0, .5, .06), (a / FPS, .3, .07)])
    S(25 * BEAT + (a - 1) / FPS, 'thwack', .55, q=.5); S(25 * BEAT + (a + 8) / FPS, 'groan', .8)
    # ------------------------------------------------------------ S4 laser
    z = clip('laser'); iF = z.meta['impactF']; lf = z.ev('land'); sf = z.ev('stop')
    L = run_frames(8); a = 20; b = 22
    seg(29, z, [(z.N(24), z.N(iF), a), (z.N(iF), z.N(iF + 25), b), (z.N(lf - 16), z.N(sf + 10), L - a - b)],
        caps=[cap(.15, a / FPS + .6, ['169 METRES.'], 120, (540, 470), WHT, -3), cap((a + b) / FPS + .8, 3.9, ['LASER.'], 250, (540, 520), YEL, 4)],
        punch=[(0, .06, .1), (a / FPS, .1, .12)], shake=[(a / FPS, 12, .15)], flash=[(0, .5, .06), (a / FPS, .5, .07)])
    S(29 * BEAT + (a - 1) / FPS, 'thwack'); S(29 * BEAT + (a - 4) / FPS, 'whoosh', .6, d=.25)
    s4 = segs[-1]; S(EV(s4, z, 'land'), 'bounce', .6, f=230)
    for k in range(2): S(EV(s4, z, 'bounce', k), 'bounce', .4 / (k + 1), f=250)
    return segs
# ---------------------------------------------------------------- the rest of the cut
def build2():
    # ---- S5 putt (break: the music strips down)
    p = clip(os.environ.get('PUTT', 'putt')); iF = p.meta['impactF']; cf = p.ev('cup') or p.ev('stop'); end = p.meta['endPlayF']
    L = run_frames(10); a = 38
    roll = L - a
    seg(37, p, [(p.N(max(0, iF - 52)), p.N(iF), a), (p.N(iF), p.N(cf + 6), roll)],
        caps=[cap(.15, 1.2, ['16 METRES.'], 120, (540, 470), WHT, -3), cap(1.6, 3.1, ['BREAK?'], 200, (540, 470), WHT, -4), cap(3.5, 4.9, ['WHAT', 'BREAK.'], 230, (540, 560), YEL, 4)],
        punch=[(0, .05, .1)], flash=[(0, .5, .06), ((a + roll - 6) / FPS - 0.05, .6, .1)])
    S(37 * BEAT + (a - 1) / FPS, 'thwack', .45, q=.4); S(37 * BEAT + (a + roll - 8) / FPS, 'cup', .9); S(37 * BEAT + (a + roll - 4) / FPS, 'cheer', .9, d=2.4)
    # ---- S6 bunker hole-out
    b = clip('bunker'); iF = b.meta['impactF']; cf = b.ev('cup') or b.ev('stop'); lf = b.ev('land')
    L = run_frames(6); a = 16
    seg(47, b, [(b.N(iF - 30), b.N(iF), a), (b.N(iF), b.N(cf + 8), L - a)],
        caps=[cap(.1, 1.0, ['BUNKER?'], 190, (540, 470), WHT, -4), cap(1.35, 2.9, ['HOLED.'], 250, (540, 520), YEL, 4)],
        punch=[(0, .06, .1), (a / FPS, .12, .12)], shake=[(a / FPS, 16, .18)], flash=[(0, .5, .06), (a / FPS, .5, .07)])
    S(47 * BEAT + (a - 1) / FPS, 'thwack', .9); S(47 * BEAT + (L - 12) / FPS, 'cup', .8); S(47 * BEAT + (L - 10) / FPS, 'cheer', .7, d=1.5)
    # ---- S7 montage: four cuts, two beats each
    n2 = run_frames(2); bm = clip('bomb'); fa = clip('fly_aug'); fm = clip('fly_mv'); iF = bm.meta['impactF']
    seg(53, bm, [(bm.N(iF - 10), bm.N(iF + 30), n2)], caps=[cap(.05, .95, ['7 REAL', 'COURSES.'], 150, (540, 470), YEL, -4)], punch=[(0, .06, .1), (10 / FPS, .12, .12)], shake=[(10 / FPS, 14, .15)], flash=[(0, .6, .06), (10 / FPS, .5, .07)])
    S(53 * BEAT + 9 / FPS, 'thwack', .9)
    seg(55, fa, [(0, 60, n2)], caps=[cap(.05, .95, ['LIDAR', 'TERRAIN.'], 150, (540, 470), WHT, 4)], zoom=lambda t: 1 + .06 * t, punch=[(0, .08, .1)], flash=[(0, .6, .06)])
    seg(57, fm, [(30, 90, n2)], caps=[cap(.05, .95, ['DAILY', 'CHALLENGE.'], 140, (540, 470), YEL, -3)], zoom=lambda t: 1.08 - .06 * t, punch=[(0, .08, .1)], flash=[(0, .6, .06)])
    ti = clip('title'); seg(59, ti, [(0, ti.n - 1, n2)], punch=[(0, .08, .1)], flash=[(0, .6, .06)])
    for k in range(4): S((53 + 2 * k) * BEAT, 'whoosh', .6, d=.3, up=bool(k % 2))
    # ---- S8 end card (own frame function)
    L = run_frames(8); s = EndSeg(clip('fly_aug'), [(40, 89, L)]); s.caps = []; s.beat = 61; segs.append(s)
    S(61 * BEAT, 'boom', .9); S(61 * BEAT + .1, 'ding', .8)
class EndSeg(Seg):
    icon = None
    def frame(self, i):
        t = i / FPS; im = src(self.c, self.at(i)); out = E.cover(im, 1 + .03 * t); out = Image.blend(out, Image.new('RGB', out.size, (6, 28, 14)), .62)
        out = out.convert('RGBA')
        if EndSeg.icon is None: EndSeg.icon = Image.open('/home/user/SweetSpot/icon-512.png').convert('RGBA')
        sc = E.ease_out_back((t - .05) / .35) if t < .4 else 1.
        if sc > .02:
            sz = int(300 * sc); ic = EndSeg.icon.resize((sz, sz), Image.LANCZOS); m = Image.new('L', (sz, sz), 0); from PIL import ImageDraw as D; D.Draw(m).rounded_rectangle((0, 0, sz - 1, sz - 1), int(sz * .22), fill=255)
            ic.putalpha(m); out.paste(ic, (540 - sz // 2, 520 - sz // 2), ic)
        for (t0, lines, size, pos, col, rot, it) in [(.35, ['SWEET SPOT', 'GOLF'], 136, (540, 900), WHT, -2, True), (1.05, ['FREE. IN YOUR BROWSER.'], 70, (540, 1170), YEL, 0, True), (1.7, ['TWO THUMBS. ONE SWING.'], 66, (540, 1285), WHT, 0, True), (2.5, ['made by Nephlonor  ·  free forever'], 44, (540, 1700), (210, 230, 210), 0, False)]:
            if t >= t0:
                lay = E.text_layer(lines, size, pos, t - t0, col, it, 8 if size < 100 else 12, rot)
                if lay: E.paste_center(out, lay, lay[1])
        if t < .12: out = Image.blend(out.convert('RGB'), Image.new('RGB', out.size, (255, 255, 255)), .8 * (1 - t / .12)).convert('RGBA')
        return out.convert('RGB')
def finish(out_video, preview=False):
    import cut
    build(); build2()
    total_beats = 69; total = run_frames(total_beats)
    starts = [round(s.beat * BF) for s in segs]
    for i, s in enumerate(segs):
        s.start = starts[i]; s.end = starts[i + 1] if i + 1 < len(segs) else total
    wr = E.Writer(out_video) if not preview else None
    n = 0
    for fi in range(total):
        s = next(x for x in segs if x.start <= fi < x.end); i = fi - s.start
        # keep each segment exactly as long as its beat slot
        scale = (s.end - s.start) / max(1, s.len)
        im = s.frame(min(s.len - 1, int(i / scale)) if scale != 1 else min(i, s.len - 1))
        t = i / FPS
        for c in s.caps:
            if c['t0'] <= t < c['t1']:
                lay = E.text_layer(c['lines'], c['size'], c['pos'], t - c['t0'], c['color'], c['it'], c['outline'], c['rot'])
                if lay: im = im.convert('RGBA'); E.paste_center(im, lay, lay[1]); im = im.convert('RGB')
        arr = (np.asarray(im, dtype=np.float32) * E.VIG).clip(0, 255).astype(np.uint8)
        im = Image.fromarray(arr)
        if wr: wr.put(im)
        elif fi % 15 == 0: im.resize((270, 480)).save(f'/tmp/pbs/prev/p{fi:04d}.jpg', quality=80)
    if wr: wr.close()
    json.dump({'beats': total_beats, 'sections': [[4, 'full'], [37, 'break'], [45, 'drop'], [53, 'hype'], [61, 'end']], 'sfx': sfx}, open('/tmp/pbs/plan.json', 'w'), indent=1)
    print('frames', total, 'sfx', len(sfx))
if __name__ == '__main__':
    os.makedirs('/tmp/pbs/prev', exist_ok=True)
    finish('/tmp/pbs/trailer_silent.mp4', PREVIEW)
