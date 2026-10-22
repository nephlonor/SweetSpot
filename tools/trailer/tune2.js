// where does a shot end for path angles and powers (direct simulation): node tune2.js scene
const { boot, setup } = require('./run'); const scenes = require('./scenes');
(async () => {
  const name = process.argv[2], sc = scenes[name], o = await boot({ dsf: 1 }), p = o.p;
  await setup(o, Object.assign({}, sc.base, sc.sc || {}));
  const rows = await p.evaluate(() => {
    const C = G.C, out = [];
    for (const pd of [-9, -6, -3, 0, 3, 6, 9]) for (const pw of [.6, .75, .87, .95, 1]) for (const h of [0, .5, -.5]) {
      const L = computeLaunch(G.club, { p: pw, Tb: .95, Td: .33, range: G.puttRange, pathDeg: pd }, { h, v: 0 }, G.surf, G.yaw, settings.hand, G.teed, .5);
      const r = simulateShot(C, { x: G.ball.x, y: G.ball.y + (G.teed ? .03 : 0), z: G.ball.z, v: L.v, w: L.w, wind: G.wind, putt: false, flag: true });
      out.push({ pd, pw, h, d: Math.round(Math.hypot(C.cup.x - r.final.x, C.cup.z - r.final.z)), s: r.finalSurf, w: r.water ? 1 : 0, ob: r.ob ? 1 : 0, t: r.events.filter(e => e.type === 'tree').length });
    }
    return { club: CLUBS[G.club].id, out };
  });
  console.log(name, rows.club); for (const r of rows.out) if (r.w || r.ob) console.log(JSON.stringify(r)); await o.b.close();
})();
