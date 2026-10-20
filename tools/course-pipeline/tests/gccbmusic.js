const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('http://localhost:8765/index.html'); await p.waitForTimeout(3000);
  await p.mouse.click(200, 400); // the first touch: audio unlock
  const st = () => p.evaluate(() => JSON.stringify({ course: COURSE.key, sound: settings.sound, music: settings.music, loaded: FM.loaded, paused: FM.el ? FM.el.paused : null, vol: FM.el ? +FM.el.volume.toFixed(2) : null, dur: FM.el ? +FM.el.duration.toFixed(1) : null, t: FM.el ? +FM.el.currentTime.toFixed(1) : null, ac: AC && AC.state, synth: !!MUS.ac }));
  await p.evaluate(() => { settings.sound = true; settings.music = true; loadData('gccb'); setCourse('gccb'); });
  await p.waitForTimeout(6000); console.log('gccb  ', await st());
  await p.waitForTimeout(3000); console.log('later ', await st());
  await p.evaluate(() => { settings.music = false; }); await p.waitForTimeout(6000); console.log('music off', await st());
  await p.evaluate(() => { settings.music = true; setCourse('augusta'); }); await p.waitForTimeout(6000); console.log('augusta', await st());
  await b.close();
})();
