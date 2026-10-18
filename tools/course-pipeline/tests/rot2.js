const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(3000);
  await p.selectOption('#segCourse', 'rothley'); await p.waitForTimeout(6000);
  console.log(await p.evaluate(() => [COURSE.key, $('segCourse').value, dailyCourse('2026-10-18'), dailyCourse('2026-10-19'), dailyCourse('2026-10-20'), dailyCourse('2026-10-17')]));
  await p.screenshot({ path: '/tmp/rothley/shots/title.png' });
  await p.evaluate(() => { $('title').classList.remove('on'); startHole(1); beginHole(); G.snapCam = true; });
  await p.waitForFunction(() => G.state === 'address', null, { timeout: 400000 }); await p.waitForTimeout(1000);
  await p.evaluate(() => openMap()); await p.waitForTimeout(4000);
  await p.screenshot({ path: '/tmp/rothley/shots/map2.png' });
  await b.close();
})();
