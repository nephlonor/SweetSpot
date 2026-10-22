// plan: p power, tb back s, hold s, td down s, drift px, curve, rx/ry right thumb offset.  (tb 1.25 / td .33 is a 3:1 tempo)
const PURE = { tb: 1.25, hold: .08, td: .33 };
const ps = (list, extra) => list.map(p => ({ name: 'p' + p, plan: Object.assign({ p }, extra) }));
module.exports = {
  pebble7: { base: { course: 'pebblebeach', hole: 6, tod: 'dusk', wx: 0, wind: [1.5, 0] }, plan: PURE, variants: ps([.78, .82, .86, .9]) },
  augusta10: { base: { course: 'augusta', hole: 9, line: 175, tod: 'day', wx: 0, wind: [1, 1] }, plan: PURE, variants: ps([.86, .9, .94, .98, 1]) },
  trees: { base: { course: 'mountainvalley', hole: 2, tod: 'day', wx: 1, wind: [0, 1] }, plan: Object.assign({ p: .95 }, PURE),
    variants: [{ name: 'dR45', plan: { drift: 45, curve: 1 } }, { name: 'dL45', plan: { drift: -45, curve: -1 } }, { name: 'dR75', plan: { drift: 75, curve: 2 } }, { name: 'dL75', plan: { drift: -75, curve: -2 } }] },
  water: { base: { course: 'pebblebeach', hole: 11, tod: 'day', wx: 1, wind: [1, 0] }, plan: Object.assign({ p: .92 }, PURE),
    variants: [{ name: 'rushed', plan: { tb: .5, td: .3 } }, { name: 'slow', plan: { td: .62 } }, { name: 'crookR', plan: { drift: 70, curve: 2 } }, { name: 'crookL', plan: { drift: -70, curve: -2 } }] },
  bomb: { base: { course: 'stpatricks', hole: 3, tod: 'day', wx: 0, wind: [0, -1.5] }, plan: Object.assign({ p: 1 }, PURE, { td: .3 }), variants: [{ name: 'full' }, { name: 'p.97', plan: { p: .97 } }] },
  bunker: { base: { course: 'pebblebeach', hole: 16, at: [-4, -162], tod: 'day', wx: 0, wind: [.5, 0] }, plan: Object.assign({ p: .6 }, PURE, { tb: 1.0, td: .3 }), variants: ps([.5, .6, .7, .8]) },
  putt: { base: { course: 'augusta', hole: 0, putt: { d: 16, ang: 120 }, range: 30, yawOff: 15, tod: 'day', wx: 0, wind: [0, 0] }, plan: { p: .45, tb: .9, hold: .06, td: .33 }, variants: [{ name: 'a' }] },
};
