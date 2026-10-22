// direct-simulation search for the power that leaves a pure shot closest to the flag (then the gestures are verified with real runs)
const { boot, setup } = require('./run'); const scenes = require('./scenes');
(async () => {
  const name = process.argv[2], sc = scenes[name], o = await boot({ dsf: 1 }), p = o.p;
  await setup(o, Object.assign({}, sc.base, sc.sc || {}));
  const rows = await p.evaluate(() => {
    const C = G.C, out = [];
    for (let pw = .5; pw <= 1.04; pw += .004) {
      const L = computeLaunch(G.club, { p: pw, Tb: .95, Td: .33, range: G.puttRange, pathDeg: 0 }, { h: 0, v: 0 }, G.surf, G.yaw, settings.hand, G.teed, .5);
      const r = simulateShot(C, { x: G.ball.x, y: G.ball.y + (G.teed ? .03 : 0), z: G.ball.z, v: L.v, w: L.w, wind: L.putt ? null : G.wind, putt: !!L.putt, flag: !L.putt });
      out.push([+pw.toFixed(3), +Math.hypot(C.cup.x - r.final.x, C.cup.z - r.final.z).toFixed(2), r.finalSurf, r.holed ? 1 : 0, r.water ? 1 : 0, r.events.filter(e => e.type === 'tree').length]);
    }
    return { club: CLUBS[G.club].id, d: distToPin(), out };
  });
  console.log(name, rows.club, Math.round(rows.d), 'm');
  console.log(rows.out.sort((a, b) => a[1] - b[1]).slice(0, 8).map(r => r.join(' ')).join('\n'));
  await o.b.close();
})();
