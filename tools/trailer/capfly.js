// node capfly.js course hole tod seconds outdir [dsf] - the hole's flyover (before the first swing)
const { boot } = require('./run'); const fs = require('fs');
(async () => {
  const [course, hole, tod, secs, dir, dsf] = process.argv.slice(2), o = await boot({ dsf: +(dsf || 2) }), p = o.p; fs.mkdirSync(dir, { recursive: true });
  await p.evaluate(c => loadData(c).then(() => setCourse(c)), course);
  await p.evaluate(([h, tod]) => { G.weather = WEATHERS[0]; G.wxNext = G.weather; G.wxLeft = 9; startHole(+h); G.tod = tod; }, [hole, tod]);
  let n = 0; for (let i = 0; i < 40; i++) await o.step();
  const st = await p.evaluate(() => G.state); console.log('state', st);
  for (let i = 0; i < +secs * 30; i++) { await p.evaluate(() => { window.__nr = false; document.body.classList.add('cine'); }); await o.step(); await p.screenshot({ path: `${dir}/f${String(n++).padStart(4, '0')}.jpg`, type: 'jpeg', quality: 90 }); }
  fs.writeFileSync(`${dir}/meta.json`, JSON.stringify({ n, fps: 30, kind: 'fly' })); await o.b.close();
})();
