// the finale: no strike-dial ball or result chip drawn on the fx canvas, and a glass "Play again" button
const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: process.env.THREE, contentType: 'application/javascript' })); await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => { settings.name = 'T'; $('title').classList.remove('on'); startHole(0); beginHole(); });
  await p.waitForFunction(() => G.state === 'address', null, { timeout: 300000 }); await p.waitForTimeout(800);
  const op = () => p.evaluate(() => ({ fx: getComputedStyle($('fx')).opacity, bg: getComputedStyle($('finaleBtn')).backgroundColor, img: getComputedStyle($('finaleBtn')).backgroundImage.slice(0, 40) }));
  console.log('address', await op());
  await p.evaluate(() => { SW.mark = { x: UI.faceCX, y: UI.faceCY }; SW.last = { loc: 'Centre', shape: 'Straight', qualityLevel: 2 }; document.body.classList.add('flight'); }); await p.waitForTimeout(700); console.log('flight', await op());
  await p.evaluate(() => { document.body.classList.remove('flight'); G.state = 'holed'; startFinale(); }); await p.waitForTimeout(1500); console.log('finale', await op()); await p.screenshot({ path: '/tmp/pbs/finalefx.png' });
  await b.close();
})();
