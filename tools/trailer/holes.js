const { open, DT } = require('./scene');
(async () => {
  const { b, p } = await open({ dsf: 1 });
  for (let i = 0; i < 30; i++) await p.evaluate(d => __frame(d, []), DT);
  for (const c of ['augusta', 'mountainvalley', 'pebblebeach', 'rothley', 'stpatricks']) {
    await p.evaluate(c => loadData(c).then(() => setCourse(c)), c);
    console.log(c, await p.evaluate(() => HOLE_DEFS.map((d, i) => (i + 1) + ':p' + d.par + '/' + Math.round(HOLE_LEN[i] || 0)).join(' ')));
  }
  await b.close();
})();
