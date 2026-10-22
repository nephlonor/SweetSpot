# Trailer soundtrack: a small numpy synth (drums, bass, arpeggio, pads) plus sound effects placed at the frame times of the edit
import numpy as np, wave
SR = 44100
def t_(d): return np.arange(int(d * SR)) / SR
def env(n, a=.005, d=.2, s=0., r=0.):
    t = np.arange(n) / SR; e = np.minimum(1, t / max(a, 1e-4)) * (s + (1 - s) * np.exp(-t / max(d, 1e-4)))
    if r: e *= np.clip((n / SR - t) / r, 0, 1)
    return e
def lp(x, fc, order=2):
    # one-pole low-pass applied in sequence
    a = np.exp(-2 * np.pi * fc / SR)
    for _ in range(order):
        y = np.zeros_like(x); s = 0.
        for i in range(len(x)): s = (1 - a) * x[i] + a * s; y[i] = s
        x = y
    return x
def lpf(x, fc, order=2):  # fast version via scipy
    from scipy.signal import butter, lfilter
    b, a = butter(order, min(fc, SR / 2 - 100) / (SR / 2), 'low'); return lfilter(b, a, x)
def hpf(x, fc, order=2):
    from scipy.signal import butter, lfilter
    b, a = butter(order, fc / (SR / 2), 'high'); return lfilter(b, a, x)
def bpf(x, lo, hi, order=2):
    from scipy.signal import butter, lfilter
    b, a = butter(order, [lo / (SR / 2), min(hi, SR / 2 - 100) / (SR / 2)], 'band'); return lfilter(b, a, x)
rng = np.random.default_rng(7)
def noise(n): return rng.standard_normal(n)
def saw(f, n, ph=0.):
    t = np.arange(n) / SR; return 2 * ((t * f + ph) % 1) - 1
def sq(f, n, w=.5):
    t = np.arange(n) / SR; return np.where((t * f) % 1 < w, 1., -1.)
def sine(f, n):
    t = np.arange(n) / SR; return np.sin(2 * np.pi * f * t)
def kick(v=1.):
    n = int(.42 * SR); t = np.arange(n) / SR; f = 46 + 130 * np.exp(-t / .035); ph = 2 * np.pi * np.cumsum(f) / SR
    return v * (np.sin(ph) * np.exp(-t / .16) + .35 * np.exp(-t / .004) * noise(n) * .3)
def clap(v=1.):
    n = int(.25 * SR); x = bpf(noise(n), 900, 3800); t = np.arange(n) / SR
    e = np.exp(-t / .07) + .8 * np.exp(-((t - .012) % .02) / .006) * (t < .05)
    return v * x * e * 1.4
def hat(v=1., o=False):
    n = int((.22 if o else .06) * SR); return v * hpf(noise(n), 7000) * np.exp(-np.arange(n) / SR / (.09 if o else .018)) * .5
def bass(f, d, v=1.):
    n = int(d * SR); x = lpf(saw(f, n) + .6 * sq(f / 2, n), 650); return v * x * env(n, .004, .3, .55, .03)
def pluck(f, d=.35, v=1.):
    n = int(d * SR); x = saw(f, n) + .5 * saw(f * 1.005, n) + .4 * sine(f * 2, n); x = lpf(x, 3200); return v * x * env(n, .002, .16, 0)
def pad(fs, d, v=1.):
    n = int(d * SR); x = sum(saw(f * (1 + dt), n, rng.random()) for f in fs for dt in (-.004, 0, .004)); x = lpf(x, 1800) / (len(fs) * 3); return v * x * env(n, .25, 5, 1, .4)
def riser(d, v=1.):
    n = int(d * SR); t = np.arange(n) / SR; x = noise(n); y = np.zeros(n); k = 40
    for i in range(0, n, 2048):
        fc = 300 + 9000 * (i / n) ** 2; seg = bpf(x[i:i + 2048], fc * .6, fc * 1.4, 1) if i + 2048 <= n else x[i:]; y[i:i + len(seg)] = seg[:len(y[i:i + len(seg)])]
    return v * y * (t / d) ** 1.8 * 1.2
def whoosh(d=.45, v=1., up=True):
    n = int(d * SR); t = np.arange(n) / SR; x = noise(n); y = np.zeros(n)
    for i in range(0, n, 1024):
        u = i / n; fc = 400 + 5000 * (u if up else 1 - u); seg = bpf(x[i:i + 1024], fc * .7, fc * 1.5, 1); y[i:i + len(seg)] = seg
    return v * y * np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.5 * 1.6
def thwack(v=1., q=1.):  # club on ball
    n = int(.4 * SR); t = np.arange(n) / SR
    x = bpf(noise(n), 1800, 6500) * np.exp(-t / .012) * 1.6 + np.sin(2 * np.pi * (180 * np.exp(-t / .03) + 90) * t) * np.exp(-t / .07) * .9 + sine(2400, n) * np.exp(-t / .006) * .4
    return v * x * q
def thud(v=1.):  # tree knock
    n = int(.5 * SR); t = np.arange(n) / SR
    return v * (lpf(noise(n), 700) * np.exp(-t / .05) * 3 + np.sin(2 * np.pi * (110 * np.exp(-t / .1) + 55) * t) * np.exp(-t / .12)) + v * bpf(noise(n), 2500, 5000) * np.exp(-t / .01) * .8
def leaves(v=1.):
    n = int(.6 * SR); t = np.arange(n) / SR; return v * bpf(noise(n), 2500, 9000) * np.exp(-t / .22) * (.6 + .4 * np.sin(t * 90)) * .8
def splash(v=1.):
    n = int(1.1 * SR); t = np.arange(n) / SR; x = lpf(noise(n), 2500) * np.exp(-t / .12) * 2.4 + hpf(noise(n), 3000) * np.exp(-t / .3) * .5
    x += sum(np.sin(2 * np.pi * (700 + 500 * k) * t * (1 + .3 * t)) * np.exp(-(t - .05 * k) ** 2 * 0 - np.clip(t - .05 * k, 0, 9) / .08) * (t > .05 * k) * .08 for k in range(1, 6)); return v * x
def bounce(v=1., f=300):
    n = int(.25 * SR); t = np.arange(n) / SR; return v * (np.sin(2 * np.pi * f * t) * np.exp(-t / .03) + lpf(noise(n), 1500) * np.exp(-t / .02) * .6)
def plink(f, v=1., d=.5):
    n = int(d * SR); t = np.arange(n) / SR; return v * (np.sin(2 * np.pi * f * t) + .4 * np.sin(2 * np.pi * f * 2.76 * t)) * np.exp(-t / .12)
def cuprattle():
    out = np.zeros(int(1.2 * SR)); 
    for k, (t0, f) in enumerate([(0, 3300), (.09, 2900), (.17, 3600), (.26, 2500)]): x = plink(f, .5 - .1 * k, .3); out[int(t0 * SR):int(t0 * SR) + len(x)] += x
    x = np.sin(2 * np.pi * (260 * np.exp(-np.arange(int(.35 * SR)) / SR / .08)) * np.arange(int(.35 * SR)) / SR) * np.exp(-np.arange(int(.35 * SR)) / SR / .12) * 1.1; out[int(.36 * SR):int(.36 * SR) + len(x)] += x; return out
def cheer(d=2.2, v=1.):
    n = int(d * SR); t = np.arange(n) / SR; x = bpf(noise(n), 500, 3200, 1) * 1.8; x += bpf(noise(n), 1500, 2600, 1) * (.5 + .5 * np.sin(t * 17 + np.sin(t * 5) * 3)) * 1.4
    e = np.clip(t / .25, 0, 1) * np.exp(-np.clip(t - .5, 0, 9) / (d * .38)); return v * x * e * .9
def groan(d=1.3, v=1.):
    n = int(d * SR); t = np.arange(n) / SR; f = 210 * np.exp(-t * .55); x = lpf(saw(1, n) * 0 + np.sin(2 * np.pi * np.cumsum(f) / SR) + .5 * np.sin(4 * np.pi * np.cumsum(f) / SR) + .3 * noise(n) * .2, 1400)
    return v * x * np.clip(t / .15, 0, 1) * np.exp(-t / .75) * .9
def trombone(v=1.):
    out = np.zeros(int(2.6 * SR))
    for k, (t0, f, d) in enumerate([(0, 233, .42), (.45, 220, .42), (.9, 207, .42), (1.35, 196, 1.0)]):
        n = int(d * SR); t = np.arange(n) / SR; fr = f * (1 - .02 * (k == 3) * np.sin(t * 28)) * (1 - .12 * (t / d) * (k == 3)); x = lpf(saw(1, n) * 0 + np.sin(2 * np.pi * np.cumsum(fr) / SR) + .6 * np.sin(4 * np.pi * np.cumsum(fr) / SR) + .4 * np.sin(6 * np.pi * np.cumsum(fr) / SR), 1800) * env(n, .03, 5, 1, .08); out[int(t0 * SR):int(t0 * SR) + n] += x * .6
    return v * out
def boom(v=1.):
    n = int(1.6 * SR); t = np.arange(n) / SR; return v * (np.sin(2 * np.pi * (38 + 90 * np.exp(-t / .1)) * t) * np.exp(-t / .55) * 1.2 + lpf(noise(n), 900) * np.exp(-t / .25) * .8)
def ding(v=1.):  # the sparkle of a clean strike
    n = int(1.0 * SR); t = np.arange(n) / SR; return v * sum(np.sin(2 * np.pi * f * t) * np.exp(-t / d) for f, d in [(1568, .5), (2349, .35), (3136, .25)]) * .25
class Mix:
    def __init__(self, dur): self.n = int((dur + 1) * SR); self.L = np.zeros(self.n); self.R = np.zeros(self.n)
    def add(self, t, x, v=1., pan=0.):
        i = int(t * SR); 
        if i < 0: x = x[-i:]; i = 0
        m = min(len(x), self.n - i); 
        if m <= 0: return
        self.L[i:i + m] += x[:m] * v * (1 - max(0, pan)); self.R[i:i + m] += x[:m] * v * (1 + min(0, pan))
    def duck(self, times, depth=.55, rel=.22):
        pass
    def save(self, path, gain=.9):
        y = np.stack([self.L, self.R], 1); pk = np.max(np.abs(y)) + 1e-9
        y = np.tanh(y / pk * 1.6) / np.tanh(1.6) * gain
        pcm = (y * 32767).astype(np.int16)
        with wave.open(path, 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
