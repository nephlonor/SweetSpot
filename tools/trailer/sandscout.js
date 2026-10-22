const { boot, setup } = require('./run');
(async () => {
  const o = await boot({ dsf: 1 }), p = o.p;
  for (const [course, hole] of [['augusta', 7], ['augusta', 3], ['augusta', 13], ['pebblebeach', 5], ['pebblebeach', 16], ['stpatricks', 2], ['rothley', 3]]) {
    await setup(o, { course, hole, tod: 'day', wx: 0, settle: 2 });
    console.log(course, hole, JSON.stringify(await p.evaluate(() => { const C = G.C, out = []; for (let r = 6; r <= 40; r += 1) for (let a = 0; a < 360; a += 4) { const x = C.cup.x + Math.sin(a * DEG) * r, z = C.cup.z + Math.cos(a * DEG) * r; if (C.surf(x, z) === S.SAND) { out.push([Math.round(x), Math.round(z), r]); } } const best = out.sort((a, b) => a[2] - b[2]).slice(0, 3); return { n: out.length, best }; })));
  }
  await o.b.close();
})();
