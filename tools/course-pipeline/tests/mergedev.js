const { chromium } = require('/opt/node-tools/node_modules/playwright'); const { execSync } = require('child_process'); const fs = require('fs');
(async () => {
  // the overall script on a temporary copy: two devices, one name
  const d = '/tmp/stpat/ov'; fs.rmSync(d, { recursive: true, force: true }); fs.mkdirSync(d + '/leaderboard', { recursive: true });
  const row = (name, by, toPar, at) => ({ name, strokes: 71 + toPar, toPar, at, by, c: 'gccb', h: [] });
  fs.writeFileSync(d + '/leaderboard/daily-2026-10-10.json', JSON.stringify([row('Zoe', 'a1', -3, 1), row('zoe', 'b2', 0, 2), row('Max', 'c3', 2, 3)]));
  fs.writeFileSync(d + '/leaderboard/daily-2026-10-11.json', JSON.stringify([row('Max', 'c3', -1, 1), row('ZOE', 'b2', 1, 2)]));
  execSync(`cd ${d} && node -e "require('/home/user/SweetSpot/.github/scripts/daily-overall.js')('2026-10-15')"`);
  console.log(fs.readFileSync(d + '/leaderboard/daily-overall.json', 'utf8').trim());
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(3500);
  console.log(await p.evaluate(() => {
    const pf = (r, h, di, dr, br, tw) => ({ xp: 100, r, h, st: 80, di, dr, br, tw });
    DL.players = { a1: { n: 'Zoe', pf: pf(2, 36, 1000, 250, -3, [20000]), bs: [{ p: 10 }] }, b2: { n: 'ZOE', pf: pf(1, 18, 500, 280, 2, [20001, 20000]), bs: [{ p: 30 }] } }; DL.playersAt = Date.now() + 1e9;
    openPlayer({ name: 'Zoe', id: 'a1' });
    return null;
  }));
  await p.waitForTimeout(900);
  console.log(await p.evaluate(() => [...$('playerBody').querySelectorAll('.stLvl span, .stRow')].map(x => x.textContent.replace(/\s+/g, ' ')).slice(0, 3).join(' | ')));
  await b.close();
})();
