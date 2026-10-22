const { boot, setup, swing } = require('./run'); const scenes = require('./scenes'); const fs = require('fs');
(async () => {
  const name = process.argv[2], sc = scenes[name], o = await boot({ dsf: 1 }), out = [];
  const seeds = (process.argv[3] || '1,2,3').split(',').map(Number);
  for (const v of sc.variants) for (const sd of seeds) {
    const info = await setup(o, Object.assign({}, sc.base, v.sc || {}));
    const r = await swing(o, Object.assign({}, sc.plan, v.plan), sd);
    const row = { v: v.name, sd, info, r }; out.push(row);
    console.log(v.name, 'seed', sd, '|', info.clubName, Math.round(info.d), 'm', '|', r.q, 'ratio', r.ratio && r.ratio.toFixed(2), 'path', r.path && r.path.toFixed(1), '| fin', r.surf, 'dpin', r.dpin && r.dpin.toFixed(1), 'holed', r.holed, 'water', r.water, 'trees', r.trees);
  }
  fs.writeFileSync(`/tmp/pbs/scout_${name}.json`, JSON.stringify(out)); await o.b.close();
})();
