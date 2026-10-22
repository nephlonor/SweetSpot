// find long putts with a lot of break: straight at the hole they miss widely, yet some aimed line holes out
const { boot, setup } = require('./run'); const fs = require('fs');
(async () => {
  const o = await boot({ dsf: 1 }), p = o.p, out = [];
  const spots = [['augusta', 0], ['augusta', 1], ['augusta', 8], ['augusta', 9], ['augusta', 17], ['augusta', 11], ['pebblebeach', 17], ['pebblebeach', 6], ['rothley', 0], ['stpatricks', 4]];
  for (const [course, hole] of spots) {
    await setup(o, { course, hole, tod: 'day', wx: 0 });
    const res = await p.evaluate(() => {
      const C = G.C, rows = [];
      for (const d of [10, 12, 14, 16]) for (let a = 0; a < 360; a += 30) {
        const x = C.cup.x + Math.sin(a * DEG) * d, z = C.cup.z + Math.cos(a * DEG) * d;
        if (C.surf(x, z) !== S.GREEN) continue;
        const y0 = Math.atan2(C.cup.x - x, -(C.cup.z - z)), hit = (yo, pw) => { const L = computeLaunch(PUTTER, { p: pw, Tb: 1.2, Td: .6, range: 30, pathDeg: 0 }, { h: 0, v: 0 }, S.GREEN, y0 + yo * DEG, settings.hand, false, .5); return simulateShot(C, { x, y: C.h(x, z), z, v: L.v, w: L.w, wind: null, putt: true, flag: true }); };
        let best = null, straight = null;
        for (let pw = .3; pw <= 1.05; pw += .015) { const r = hit(0, pw); const m = Math.hypot(C.cup.x - r.final.x, C.cup.z - r.final.z); if (!straight || m < straight.m) straight = { m, pw }; }
        for (let yo = -30; yo <= 30; yo += .5) for (let pw = .3; pw <= 1.05; pw += .01) { const r = hit(yo, pw); if (r.holed && (!best || Math.abs(yo) > Math.abs(best.yo))) best = { yo, pw }; }
        if (best) rows.push({ d, a, yo: best.yo, pw: +best.pw.toFixed(2), x, z, missStraight: +straight.m.toFixed(1) });
      }
      return rows.sort((a, b) => Math.abs(b.yo) - Math.abs(a.yo)).slice(0, 4);
    });
    console.log(course, hole, JSON.stringify(res)); out.push({ course, hole, res });
  }
  fs.writeFileSync('/tmp/pbs/puttscout.json', JSON.stringify(out)); await o.b.close();
})();
