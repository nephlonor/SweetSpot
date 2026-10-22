// the home course on a player's card opened from the leaderboard (others via homecourses.json, own from settings)
const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.route('**/leaderboard/homecourses.json*', r => r.fulfill({ contentType: 'application/json', body: JSON.stringify({ abc: { c: 'Pine <b>Hollow</b> GC', r: 'Ohio, USA', at: 1 } }) }));
  await p.route('**/leaderboard/players.json*', r => r.fulfill({ contentType: 'application/json', body: '{}' }));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: process.env.THREE, contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  const rows = () => p.evaluate(() => [...document.querySelectorAll('#playerBody .stRow')].map(e => e.textContent).filter(t => /Home course/.test(t)));
  await p.evaluate(() => openPlayer({ name: 'Bob', id: 'abc' })); await p.waitForTimeout(1500); console.log('other:', await rows());
  await p.evaluate(() => openPlayer({ name: 'Zed', id: 'zzz' })); await p.waitForTimeout(1500); console.log('none:', await rows());
  await p.evaluate(() => { settings.homeC = 'Mountain Valley'; settings.homeR = 'Pennsylvania'; openPlayer({ name: 'Me', me: true }); }); await p.waitForTimeout(500); console.log('me:', await rows());
  await b.close();
})();
