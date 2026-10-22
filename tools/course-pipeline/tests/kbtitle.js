// start screen: with a (faked) keyboard the name field is lifted above it, and released afterwards
const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 780 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => { localStorage.setItem('ssg-intro-seen', '1'); const vv = Object.assign(new EventTarget(), { height: 780, offsetTop: 0, offsetLeft: 0, width: 405, scale: 1 }); Object.defineProperty(window, 'visualViewport', { value: vv }); window.__vv = vv; });
  await p.route('**/three.min.js', r => r.fulfill({ path: process.env.THREE, contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  const pos = () => p.evaluate(() => $('nameIn').getBoundingClientRect().bottom);
  console.log('before', await pos());
  await p.focus('#nameIn'); await p.evaluate(() => { __vv.height = 450; __vv.dispatchEvent(new Event('resize')); }); await p.waitForTimeout(900);
  await p.waitForTimeout(1500); console.log('keyboard open (visible bottom 450):', await pos(), await p.evaluate(() => [$('title')._lift, $('title').style.transform])); await p.screenshot({ path: '/tmp/pbs/kbtitle.png' });
  await p.evaluate(() => { document.activeElement.blur(); __vv.height = 780; __vv.dispatchEvent(new Event('resize')); }); await p.waitForTimeout(900);
  await p.waitForTimeout(1500); console.log('closed:', await pos()); await b.close();
})();
