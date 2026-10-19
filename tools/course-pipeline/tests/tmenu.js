const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 }, hasTouch: false })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(3000);
  const vis = () => p.evaluate(() => { const b = $('titleMenu'), r = b.getBoundingClientRect(); return { hidden: b.hidden, w: Math.round(r.width) }; });
  console.log('start', JSON.stringify(await vis()), await p.evaluate(() => settings.name));
  await p.fill('#nameIn', 'Tom'); console.log('typed', JSON.stringify(await vis()));
  await p.screenshot({ path: '/tmp/stpat/shots/tmenu.png' });
  await p.click('#titleMenu'); await p.waitForTimeout(700); console.log('menu', await p.evaluate(() => $('menuSheet').classList.contains('on')));
  await p.screenshot({ path: '/tmp/stpat/shots/tmenu2.png' });
  await p.evaluate(() => closeSheets()); await p.fill('#nameIn', ''); console.log('cleared', JSON.stringify(await vis()));
  await b.close();
})();
