const { chromium } = require('/opt/node-tools/node_modules/playwright'); const fs = require('fs');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(3000);
  const old = JSON.parse(fs.readFileSync('/tmp/ov_old.json')), oldIdx = JSON.parse(fs.readFileSync('/tmp/idx_old.json')), day = JSON.parse(fs.readFileSync('/home/user/SweetSpot/leaderboard/daily-2026-10-20.json')), want = JSON.parse(fs.readFileSync('/home/user/SweetSpot/leaderboard/daily-overall.json'));
  const out = await p.evaluate(([old, oldIdx, day, want]) => {
    // pretend it is 2026-10-21 and the workflow has not rebuilt the standings yet
    const real = dayId; window.dayId = () => '2026-10-21';
    DL.index = oldIdx; DL.overall = old; DL.metaAt = Date.now() + 1e9;
    DL.files['2026-10-20'] = day.map(x => ({ id: x.by, n: x.name, c: x.c, h: x.h, th: 18, done: true, at: x.at }));
    const m = dlMetaLive(); const key = o => o.n + ':' + o.p + ':' + o.d + ':' + o.w + ':' + o.pod + ':' + o.best;
    return { idxDays: m.idx.map(x => x.d), idxFirst: m.idx[0], same: JSON.stringify(m.ov.map(key).sort()) === JSON.stringify(want.map(key).sort()), sameOrder: JSON.stringify(m.ov.map(key)) === JSON.stringify(want.map(key)), n: m.ov.length, live: m.ov.slice(0, 4).map(key), server: want.slice(0, 4).map(key) };
  }, [old, oldIdx, day, want]);
  console.log(JSON.stringify(out));
  await b.close();
})();
