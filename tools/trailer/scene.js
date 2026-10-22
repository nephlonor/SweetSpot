// Scripted human thumbs and the scene loop (see lib.js)
const { open } = require('./lib'); const fs = require('fs');
const FPS = 30, DT = 1000 / FPS;
// deterministic noise for the thumbs
function rng(seed) { let s = seed >>> 0; return () => { s = (s + 0x6D2B79F5) >>> 0; let t = Math.imul(s ^ s >>> 15, 1 | s); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const sm = u => u * u * (3 - 2 * u);
// plan: { p: power 0..1, tb: backswing s, hold: pause at the top s, td: downswing s, drift: sideways px during the upstroke (+ right),
//         curve: crookedness of the downward drag, rx,ry: where the right thumb rests relative to the sweet spot (px), seed, lead: s before the touch }
function planEvents(g, plan) {
  const R = rng(plan.seed || 1), lead = plan.lead == null ? .5 : plan.lead, pre = plan.pre == null ? .16 : plan.pre;
  const hold = plan.hold == null ? .08 : plan.hold, T0 = lead, tTop = T0 + pre + plan.tb, tHold = tTop + hold, tEnd = tHold + plan.td, total = tEnd + .25;
  const drop = (plan.p) * g.px, wob = (t, f, a) => Math.sin(t * f + (plan.seed || 1)) * a;
  const left = t => {
    if (t < T0 || t > tEnd) return null;
    let y, x = g.x + wob(t, 3.1, 1.6);
    if (t < T0 + pre) { y = g.y0 + 0; } // finger down on the top of the track
    else if (t < tTop) { const u = (t - T0 - pre) / plan.tb; y = g.y0 + drop * sm(u); x += (plan.curve || 0) * Math.sin(u * Math.PI) * 6; }
    else if (t < tHold) { y = g.y0 + drop; }
    else { const u = (t - tHold) / plan.td; y = g.y0 + drop * (1 - Math.pow(u, 1.5)) - 14 * u; x += (plan.drift || 0) * Math.pow(u, 1.15) + wob(t, 9, 1.2); }
    return [x, y];
  };
  const right = t => { if (t < .1) return null; const k = Math.min(1, (t - .1) / .3); return [g.rx + (plan.rx || 0) * (1 - 0) + wob(t, 2.3, 2.5) * k, g.ry + (plan.ry || 0) + wob(t, 3.7, 2.5) * k]; };
  return { total, left, right, tEnd, T0, tTop, tHold };
}
async function geo(p) { return p.evaluate(() => { const rt = $('tempoCv').getBoundingClientRect(); return { x: rt.left + rt.width * .55, y0: rt.top + 16, px: UI.trackPx, rx: UI.faceCX + 44, ry: UI.faceCY + 62 }; }); }
// events for one frame (4 sub-steps) from the plan at frame index f
function frameEvents(pl, f, st) {
  const out = [[], [], [], []];
  for (let i = 0; i < 4; i++) {
    const t = (f * 4 + i + 1) / (4 * FPS), L = pl.left(t), Rr = pl.right(t);
    if (Rr) { if (!st.r) { out[i].push(['pointerdown', Rr[0], Rr[1], 2]); st.r = true; } else out[i].push(['pointermove', Rr[0], Rr[1], 2]); out[i].push(['pad', 'R', Rr[0], Rr[1], 1, 0]); }
    if (L) { if (!st.l) { out[i].push(['pointerdown', L[0], L[1], 1]); st.l = true; } else out[i].push(['pointermove', L[0], L[1], 1]); out[i].push(['pad', 'L', L[0], L[1], 1, 0]); }
    else if (st.l && !st.lu) { out[i].push(['pointerup', st.lx, st.ly, 1]); out[i].push(['pad', 'L', 0, 0, 0, 0]); st.lu = true; }
    if (L) { st.lx = L[0]; st.ly = L[1]; }
    if (!Rr && st.r && !st.ru) { out[i].push(['pointerup', 0, 0, 2]); out[i].push(['pad', 'R', 0, 0, 0, 0]); st.ru = true; }
    if (t > pl.tEnd + .12 && st.r && !st.ru) { out[i].push(['pointerup', 0, 0, 2]); out[i].push(['pad', 'R', 0, 0, 0, 0]); st.ru = true; }
  }
  return out;
}
module.exports = { open, FPS, DT, planEvents, geo, frameEvents, rng };
