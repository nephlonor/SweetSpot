const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('http://localhost:8765/index.html'); await p.waitForTimeout(3000);
  await p.mouse.click(200, 400);
  const st = () => p.evaluate(() => JSON.stringify({ hidden: document.hidden, paused: FM.el.paused, gain: +FM.gain.gain.value.toFixed(3), vol: +FM.vol.toFixed(3), t: +FM.el.currentTime.toFixed(1) }));
  await p.evaluate(() => { settings.sound = true; settings.music = true; loadData('gccb'); setCourse('gccb'); });
  await p.waitForTimeout(16000); console.log('playing     ', await st());
  // leave the app: the page is hidden and the timers are frozen (here: the interval is killed too)
  await p.evaluate(() => { window.__iv = window.setInterval; Object.defineProperty(document, 'hidden', { configurable: true, get: () => true }); document.dispatchEvent(new Event('visibilitychange')); });
  await p.waitForTimeout(150); console.log('just left   ', await st());
  await p.waitForTimeout(450); console.log('0.6 s later ', await st());
  await p.waitForTimeout(1500); console.log('2 s later   ', await st());
  await p.evaluate(() => { Object.defineProperty(document, 'hidden', { configurable: true, get: () => false }); document.dispatchEvent(new Event('visibilitychange')); });
  await p.waitForTimeout(500); await p.mouse.click(200, 400); await p.waitForTimeout(4000); console.log('back + touch', await st());
  await b.close();
})();
