# Soundtrack for the trailer: 124 BPM, four-on-the-floor with a stripped breakdown for the putt, and sfx at the frame times from the edit
import json, sys
import numpy as np
import synth as s
BPM = 116.; BEAT = 60 / BPM
NOTE = lambda m: 440 * 2 ** ((m - 69) / 12)
CH = [(48, [60, 64, 67]), (43, [59, 62, 67]), (45, [57, 60, 64]), (41, [57, 60, 65])]   # C  G  Am  F  (bass root, chord)
def build(plan, out):
    """plan: { beats: total beats, sections: [[startBeat, name]], sfx: [{t, kind, v}] }"""
    nb = plan['beats']; dur = nb * BEAT + 3.2; M = s.Mix(dur); X = s.Mix(dur)
    sec = [(0, 'build')] + [tuple(x) for x in plan['sections']]
    def at(b):
        cur = 'build'
        for sb, nm in sec:
            if b >= sb - 1e-9: cur = nm
        return cur
    for b in range(0, nb):
        t = b * BEAT; sc = at(b); bar = b // 4; ch = CH[bar % 4]; step = b % 4
        full = sc in ('full', 'drop', 'hype'); brk = sc == 'break'
        if full or sc == 'end':
            if sc != 'end' or step == 0: M.add(t, s.kick(1.0 if full else .9), .95)
        if brk: M.add(t, s.kick(.55), .45)                         # a heartbeat under the putt
        if full and step in (1, 3): M.add(t, s.clap(1.), .55)
        if sc == 'build' and step in (1, 3): M.add(t, s.clap(.6), .3)
        if full or sc == 'build':
            for h in range(2):
                M.add(t + h * BEAT / 2, s.hat(.7 if h == 0 else 1., o=(h == 1 and full)), .26 if full else .18)
        # bass: off-beat eighths
        if full:
            M.add(t + BEAT / 2, s.bass(NOTE(ch[0]), BEAT * .42), .5)
            M.add(t, s.bass(NOTE(ch[0] - 12), BEAT * .36), .38)
        # arpeggio: sixteenth notes over the chord
        if full or brk or sc == 'end':
            for q in range(4):
                n = ch[1][(q + (1 if bar % 2 else 0)) % 3] + (12 if q % 2 else 24 if (b + q) % 3 == 0 else 12)
                v = .19 if full else .12
                if sc == 'hype': v = .24
                M.add(t + q * BEAT / 4, s.pluck(NOTE(n), .3, 1), v, pan=(-.35 if q % 2 else .35))
        if step == 0 and sc != 'build' or (sc == 'build' and b == 0):
            M.add(t, s.pad([NOTE(m) for m in ch[1]], BEAT * 4, 1), .22 if not brk else .3)
    # risers into each section change
    for sb, nm in sec:
        if sb >= 4 and nm in ('full', 'drop', 'hype', 'end'):
            M.add(max(0, sb * BEAT - 2 * BEAT), s.riser(2 * BEAT), .4)
            M.add(sb * BEAT, s.boom(1.), .5 if nm != 'end' else .8)
    M.add(0, s.riser(4 * BEAT), .5)
    # a sparkle outro
    for k, m in enumerate([72, 76, 79, 84]): M.add((nb - 4) * BEAT + k * BEAT / 4, s.pluck(NOTE(m + 12), .6), .3)
    for e in plan['sfx']:
        k, t, v = e['kind'], e['t'], e.get('v', 1.)
        f = {'whoosh': lambda: s.whoosh(e.get('d', .45), 1., e.get('up', True)), 'thwack': lambda: s.thwack(1., e.get('q', 1.)), 'ding': lambda: s.ding(), 'thud': lambda: s.thud(), 'leaves': lambda: s.leaves(),
             'splash': lambda: s.splash(), 'bounce': lambda: s.bounce(1., e.get('f', 300)), 'cup': lambda: s.cuprattle(), 'cheer': lambda: s.cheer(e.get('d', 2.2)), 'groan': lambda: s.groan(), 'trombone': lambda: s.trombone(),
             'boom': lambda: s.boom(), 'tick': lambda: s.plink(2200, 1., .08), 'riser': lambda: s.riser(e.get('d', 1.))}[k]()
        X.add(t, f, v, pan=e.get('pan', 0.))
    # the music ducks under the hits so the shots and the sfx stay clear
    env = np.ones(M.n)
    for e in plan['sfx']:
        if e['kind'] in ('thwack', 'thud', 'splash', 'cup', 'boom', 'cheer', 'trombone'):
            i = int(e['t'] * s.SR); L = int((.5 if e['kind'] in ('cheer', 'trombone') else .28) * s.SR); dip = .42 if e['kind'] in ('thwack', 'thud', 'cup') else .55
            ramp = 1 - (1 - dip) * np.exp(-np.arange(L) / (L / 3.)); env[i:i + L] = np.minimum(env[i:i + L], ramp[:len(env[i:i + L])])
    M.L *= env; M.R *= env
    pm = np.max(np.abs(np.stack([M.L, M.R]))) + 1e-9; M.L *= .62 / pm; M.R *= .62 / pm       # music peak at -4 dB, sfx on top
    px = np.max(np.abs(np.stack([X.L, X.R]))) + 1e-9; X.L *= .8 / px; X.R *= .8 / px
    M.L += X.L; M.R += X.R; M.save(out); return dur
if __name__ == '__main__':
    plan = json.load(open(sys.argv[1])); print(build(plan, sys.argv[2]))
