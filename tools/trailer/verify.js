// usage: node verify.js scene variantsJSON seeds   - runs real gestures; prints best outcomes
const { boot, setup, swing } = require('./run'); const scenes = require('./scenes'); const fs = require('fs');
(async () => {
  const name = process.argv[2], sc = scenes[name], vars = JSON.parse(process.argv[3] || '[{}]'), seeds = (process.argv[4] || '1,2,3').split(',').map(Number);
  const o = await boot({ dsf: +(process.env.DSF || 1) }), rows = [];
  for (const v of vars) for (const sd of seeds) {
    const info = await setup(o, Object.assign({}, sc.base, v.sc || {})), r = await swing(o, Object.assign({}, sc.plan, v.plan || {}), sd);
    rows.push({ v, sd, r, info }); console.log(JSON.stringify(v), 'sd', sd, '|', r.q, 'ratio', r.ratio && r.ratio.toFixed(2), 'h/v', r.h && r.h.toFixed(2), '/', r.v && typeof r.v === 'number' ? r.v.toFixed(2) : '', 'path', r.path && r.path.toFixed(1), '| surf', r.surf, 'dpin', r.dpin && r.dpin.toFixed(2), 'holed', r.holed, 'water', r.water, 'trees', r.trees, 'ev', (r.ev || '').slice(0, 60));
  }
  fs.writeFileSync(`/tmp/pbs/ver_${name}.json`, JSON.stringify(rows)); await o.b.close();
})();
