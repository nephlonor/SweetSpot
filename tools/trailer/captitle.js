// node captitle.js course tod seconds outdir [dsf] - the start screen with the course turning behind the logo
const { boot } = require('./run'); const fs = require('fs');
(async () => {
  const [course, tod, secs, dir, dsf] = process.argv.slice(2), o = await boot({ dsf: +(dsf || 2) }), p = o.p; fs.mkdirSync(dir, { recursive: true });
  await p.evaluate(c => loadData(c).then(() => setCourse(c)), course);
  await p.evaluate(tod => { settings.course = COURSE.key; G.tod = tod; showTitleHole(); $('title').classList.add('on'); }, tod);
  for (let i = 0; i < 45; i++) await o.step();
  let n = 0; for (let i = 0; i < +secs * 30; i++) { await p.evaluate(() => { window.__nr = false; }); await o.step(); await p.screenshot({ path: `${dir}/f${String(n++).padStart(4, '0')}.jpg`, type: 'jpeg', quality: 90 }); }
  fs.writeFileSync(`${dir}/meta.json`, JSON.stringify({ n, fps: 30, kind: 'title' })); await o.b.close();
})();
