// A scene: set the ball up on a course, let a scripted thumb swing, optionally capture every frame
const { open, planEvents, geo, frameEvents, DT, FPS } = require('./scene'); const fs = require('fs');
async function boot(opts = {}) {
  const o = await open(opts), p = o.p;
  o.step = evs => p.evaluate(([d, e]) => __frame(d, e), [DT, evs || []]);
  for (let i = 0; i < 30; i++) await o.step();
  await p.evaluate(() => { settings.name = 'TRAILER'; saveSettings(); $('title').classList.remove('on'); window.__nr = true; const r = W.ren.render; W.ren.render = function () { if (window.__nr) return; return r.apply(this, arguments); }; });
  // the swing draws its own random numbers (wobble phase, lie roll): reseed at those two points so the frame-level randomness of the scene cannot change the shot
  await p.evaluate(() => { window.__S = 1; const sb = swingBegin, im = impact; window.swingBegin = function (...a) { __seed(window.__S * 7919 + 1); return sb.apply(this, a); }; window.impact = function (...a) { __seed(window.__S * 7919 + 2); return im.apply(this, a); }; });
  await p.evaluate(() => { const st = document.createElement('style'); st.textContent = '.cine #tempo,.cine #strike,.cine #fx,.cine #readout,.cine #skipBtn,.cine #unplayBtn,.cine #done,.cine #intro,.cine #coach{opacity:0!important;transition:none!important}'; document.head.appendChild(st); });
  o.course = null; return o;
}
async function setup(o, sc) {
  const { p } = o;
  if (o.course !== sc.course) { await p.evaluate(c => loadData(c).then(() => setCourse(c)), sc.course); o.course = sc.course; }
  await p.evaluate(sc => { G.weather = WEATHERS[sc.wx == null ? 1 : sc.wx]; G.wxNext = G.weather; G.wxLeft = 9; startHole(sc.hole); beginHole(); }, sc);
  let n = 0; while (!(await p.evaluate(() => G.state === 'address')) && n++ < 700) await o.step();
  const info = await p.evaluate(sc => {
    const C = G.C; G.tod = sc.tod || 'day'; if (sc.wind) G.wind = sc.wind.slice(); G.swirl = null;
    let ok = true;
    if (sc.at || sc.line || sc.sand || sc.putt) {
      let x, z;
      if (sc.at) [x, z] = sc.at;
      else if (sc.line) { const q = polyAt(C.center, Math.max(0, C.center.L - sc.line)); x = q[0]; z = q[1]; }
      else if (sc.putt) { const a = (sc.putt.ang || 0) * Math.PI / 180; x = C.cup.x + Math.sin(a) * sc.putt.d; z = C.cup.z + Math.cos(a) * sc.putt.d; }
      else { ok = false; for (let r = sc.sand[0]; r <= sc.sand[1] && !ok; r += 1) for (let a = 0; a < 360 && !ok; a += 5) { const xx = C.cup.x + Math.sin(a * Math.PI / 180) * r, zz = C.cup.z + Math.cos(a * Math.PI / 180) * r; if (C.surf(xx, zz) === S.SAND) { x = xx; z = zz; ok = true; } } }
      if (ok) { placeBall(x, z, false); G.state = 'settle'; G.settleT = 0; G.camFrom = W.cam.position.clone(); G.lookFrom = G.camLook.clone(); }
    }
    autoClubAndAim();
    if (sc.club != null) { G.club = sc.club; if (isPutt()) pickPuttRange(); }
    if (sc.range && isPutt()) G.puttRange = sc.range;
    if (sc.yawOff) G.yaw += sc.yawOff * DEG; G.target = null; G.carryKey = ''; updateAim(true);
    return { ok, club: G.club, clubName: CLUBS[G.club].id, d: distToPin(), surf: G.surf, range: G.puttRange };
  }, sc);
  n = 0; while (!(await p.evaluate(() => G.state === 'address')) && n++ < 400) await o.step();
  for (let i = 0; i < (sc.settle || 40); i++) await o.step();
  return info;
}
// run the swing; shots: { dir, from, every } captures frames; returns the outcome
async function swing(o, plan, seed, cap) {
  const { p } = o;
  await p.evaluate(s => { window.__S = s; }, seed);
  const g = await geo(p), pl = planEvents(g, plan), st = {};
  let f = 0, endF = 0, i = 0;
  const grab = async () => { if (cap) { await p.evaluate(() => { window.__nr = false; }); } };
  const inWin = f => !cap || (cap.wins ? cap.wins.some(w => f >= w[0] && f <= w[1]) : f >= (cap.from || 0) * FPS);
  for (; f < 900; f++) {
    const s = await p.evaluate(() => G.state), t = f / FPS, on = inWin(f);
    await p.evaluate(([on, cine]) => { window.__nr = !on; document.body.classList.toggle('cine', cine); }, [!!(cap && on), !!(cap && cap.cineF != null && f >= cap.cineF)]);
    await o.step(frameEvents(pl, f, st));
    if (cap && on && (f % (cap.every || 1)) === 0) { await p.screenshot({ path: `${cap.dir}/f${String(cap.n).padStart(4, '0')}.jpg`, type: 'jpeg', quality: 90 }); if (cap.meta) cap.meta.frames.push({ n: cap.n, f }); cap.n++; }
    if (t > pl.total + .1 && s !== 'flight' && s !== 'address' && s !== 'settle' && s !== 'holed') { if (!endF) endF = f; if (f - endF > 12) break; }
    if (t > pl.total + .1 && (s === 'settle' || s === 'holed' || s === 'address')) { if (!endF) endF = f; if (f - endF > (cap && cap.tail != null ? cap.tail : 45)) break; }
  }
  await p.evaluate(() => { window.__nr = true; });
  return p.evaluate(() => { const r = G.shot && G.shot.res, L = G.shot && G.shot.L; return { state: G.state, strokes: G.strokes, q: L && L.quality, ratio: L && L.ratio, h: L && L.h, v: L && L.v, p: L && L.p, path: SW.pathDeg, fin: r && [r.final.x, r.final.z], surf: r && r.finalSurf, holed: r && r.holed, water: r && r.water, ob: r && r.ob, trees: r ? r.events.filter(e => e.type === 'tree').length : 0, ev: r && r.events.map(e => e.type).join(','), dpin: r && Math.hypot(G.C.cup.x - r.final.x, G.C.cup.z - r.final.z), carry: r && r.carry, n: r && r.n, ball: [G.ball.x, G.ball.z] }; });
}
module.exports = { boot, setup, swing, FPS };
