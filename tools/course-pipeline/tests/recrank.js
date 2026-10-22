// stats page: rank of each record among the published players
const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 780 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: process.env.THREE, contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.route('**/leaderboard/players.json*', r => r.fulfill({ contentType: 'application/json', body: JSON.stringify({
    a: { n: 'ANNA', pf: { r: 3, h: 40, dr: 310, ho: 40, pt: 12, br: -2, gs: 5, fs: 6, bk: 2 } },
    b: { n: 'BEN', pf: { r: 3, h: 40, dr: 250, ho: 60, pt: 20, br: 3, gs: 3, fs: 9 } },
    b2: { n: 'ben', pf: { r: 1, h: 10, dr: 270, br: 1 } },
    me: { n: 'TEST', pf: { r: 1, h: 1, dr: 999 } } }) }));
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => { settings.name = 'TEST'; saveSettings(); const R = ST.rec; R.drive.v = 280; R.drive.at = 1; R.holed.v = 50; R.holed.at = 1; R.round.v = 0; R.round.at = 1; R.girStreak.v = 9; R.girStreak.at = 1; openStats(); });
  await p.waitForTimeout(1500);
  console.log(await p.evaluate(() => [...document.querySelectorAll('#statsBody .stCard.rec')].map(e => e.querySelector('.k').textContent + ': ' + (e.querySelector('.rk') || {}).textContent)));
  console.log('classes:', await p.evaluate(() => [...document.querySelectorAll('#statsBody .rk')].map(e => e.className)));
  await p.evaluate(() => openPlayer({ name: 'ANNA', id: 'a' })); await p.waitForTimeout(1800);
  console.log('anna:', await p.evaluate(() => [...document.querySelectorAll('#playerBody .stCard')].map(e => e.querySelector('.k').textContent + ': ' + ((e.querySelector('.rk') || {}).textContent || '') + ' ' + ((e.querySelector('.rk') || {}).className || ''))));
  await p.screenshot({ path: '/tmp/pbs/recrank_pl.png' });
  await p.evaluate(() => { closeSheets(); openStats(); }); await p.waitForTimeout(800);
  await p.evaluate(() => document.querySelector('#statsSheet').scrollTop = 500); await p.screenshot({ path: '/tmp/pbs/recrank.png' }); await b.close();
})();
