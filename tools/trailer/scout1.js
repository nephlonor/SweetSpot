const { open, planEvents, geo, frameEvents, DT } = require('./scene');
(async () => {
  const { b, p } = await open({ dsf: 1 });
  const step = (evs) => p.evaluate(([d, e]) => __frame(d, e), [DT, evs || []]);
  for (let i = 0; i < 40; i++) await step();
  await p.evaluate(() => { settings.name = 'TRAILER'; saveSettings(); $('title').classList.remove('on'); window.__nr = false; const o = W.ren.render; W.ren.render = function () { if (window.__nr) return; return o.apply(this, arguments); }; });
  await p.evaluate(c => loadData(c).then(() => setCourse(c)), 'pebblebeach');
  await p.evaluate(() => { G.weather = WEATHERS[0]; startHole(6); beginHole(); });
  await p.evaluate(() => { window.__nr = true; });
  let t0 = Date.now(), n = 0; while (!(await p.evaluate(() => G.state === 'address')) && n < 600) { await step(); n++; } console.log('to address', n, Date.now() - t0, 'ms');
  const g = await geo(p); console.log(g);
  const plan = { p: .92, tb: .9, hold: .1, td: .30, seed: 3 }, pl = planEvents(g, plan), st = {};
  t0 = Date.now(); let f = 0;
  for (; f < 400; f++) { await step(frameEvents(pl, f, st)); const s = await p.evaluate(() => G.state); if (f > pl.total * 30 + 5 && s !== 'flight') break; }
  console.log('frames', f, Date.now() - t0, 'ms', await p.evaluate(() => ({ s: G.state, strokes: G.strokes, L: G.shot && G.shot.L && { q: G.shot.L.quality, ratio: G.shot.L.ratio, h: G.shot.L.h, v: G.shot.L.v, ps: G.shot.L.p }, res: G.shot && { fin: G.shot.res.final, surf: G.shot.res.finalSurf, holed: G.shot.res.holed, water: G.shot.res.water, n: G.shot.res.n }, ball: [G.ball.x, G.ball.z], cup: [G.C.cup.x, G.C.cup.z] })));
  await b.close();
})();
