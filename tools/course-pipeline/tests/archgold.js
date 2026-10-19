const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(3500);
  console.log(await p.evaluate(() => {
    settings.name = 'Mia'; DL.index = [{ d: '2026-10-18', c: 'augusta', n: 3, w: 'Mia', wb: dlMe(), t: 6 }, { d: '2026-10-17', c: 'alsace', n: 6, w: 'ADAM', wb: 'zz', t: -2 }, { d: '2026-10-16', c: 'gccb', n: 2, w: 'mia', t: 1 }, { d: '2026-10-15', c: 'gccb', n: 2, w: 'Bo', wb: 'qq', t: 1 }];
    DL.tab = 'archive'; DL.indexAt = Date.now() + 1e9; fillDaily($('dailyBody')); openSheet('dailySheet');
    return [...document.querySelectorAll('#dailyBody .lb .row')].map(r => r.querySelector('.st').textContent + ':' + getComputedStyle(r.querySelector('.st')).color).join(' | ');
  }));
  await b.close();
})();
