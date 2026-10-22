// node capture.js scene '{"variant":...}' seed outdir [dsf]  -> frames f0000.jpg.. and meta.json
const { boot, setup, swing, FPS } = require('./run'); const scenes = require('./scenes'); const fs = require('fs');
(async () => {
  const name = process.argv[2], v = JSON.parse(process.argv[3] || '{}'), seed = +process.argv[4], dir = process.argv[5], dsf = +(process.argv[6] || 2);
  const sc = scenes[name], base = Object.assign({}, sc.base, v.sc || {}), plan = Object.assign({}, sc.plan, v.plan || {}); fs.mkdirSync(dir, { recursive: true });
  const o = await boot({ dsf }), p = o.p;
  // pass 1: no rendering, the timeline of the shot
  await setup(o, base);
  const tl = [];
  await p.evaluate(() => { window.__log = []; const f = window.__frame; window.__frame = (d, e) => { const r = f(d, e); const sh = G.shot; window.__log.push([G.state, sh ? +G.playT.toFixed(3) : -1]); return r; }; });
  const r1 = await swing(o, plan, seed, null);
  const log = await p.evaluate(() => window.__log), shot = await p.evaluate(() => { const r = G.shot.res; return { dur: r.duration, land: r.land && r.land.t, events: r.events.map(e => ({ type: e.type, t: e.t })), holed: r.holed, putt: !!G.shot.L.putt }; });
  console.log('pass1', JSON.stringify(r1).slice(0, 300), JSON.stringify(shot).slice(0, 400));
  let impactF = log.findIndex(x => x[0] === 'flight'); if (impactF < 0) impactF = 0;
  const fr = log.map((x, i) => ({ i, st: x[0], pt: x[1] }));
  // windows (frame indices): swing .. impact+.8 s, then the last 1.1 s before the landing .. rest+1.4 s
  let landF = fr.findIndex(x => x.st === 'flight' && x.pt >= (shot.land || shot.dur) - 1.1); { const evs = shot.events.filter(e => e.type === 'tree' || e.type === 'splash' || e.type === 'pin' || e.type === 'cup'); if (evs.length) { const f0 = fr.findIndex(x => x.st !== 'address' && x.pt >= Math.min(...evs.map(e => e.t)) - 1e-6); if (f0 > 0) landF = Math.min(landF, f0 - 20); } }
  const endF = Math.min(log.length - 1, (fr.findIndex(x => x.pt >= shot.dur) < 0 ? log.length : fr.findIndex(x => x.pt >= shot.dur)) + Math.round(1.4 * FPS));
  const wins = shot.putt ? [[Math.max(0, impactF - Math.round(2.6 * FPS)), endF]] : [[Math.max(0, impactF - Math.round(2.6 * FPS)), impactF + Math.round(.9 * FPS)], [Math.max(landF, impactF + Math.round(.9 * FPS) + 1), endF]];
  console.log('impactF', impactF, 'landF', landF, 'endF', endF, 'wins', JSON.stringify(wins));
  // pass 2: the same swing, rendered
  await setup(o, base);
  const evF = shot.events.map(e => ({ type: e.type, f: Math.max(0, fr.findIndex(x => x.st !== 'address' && x.pt >= e.t - 1e-6)) })), endPlayF = fr.findIndex(x => x.pt >= shot.dur - 1e-6);
  const meta = { name, seed, fps: FPS, impactF, shot, wins, evF, endPlayF, frames: [] };
  const cap = { dir, n: 0, on: false, from: 0, wins, meta, cineF: impactF + 14 };
  await p.evaluate(() => { window.__log = []; const f = window.__frame; window.__frame = (d, e) => { const r = f(d, e); const sh = G.shot; window.__log.push([G.state, sh ? +G.playT.toFixed(3) : -1]); return r; }; });
  const r2 = await swing(o, plan, seed, cap);
  console.log('pass2', JSON.stringify(r2).slice(0, 200), 'frames', cap.n); meta.n = cap.n; meta.r = r2;
  fs.writeFileSync(`${dir}/meta.json`, JSON.stringify(meta)); await o.b.close();
})();
