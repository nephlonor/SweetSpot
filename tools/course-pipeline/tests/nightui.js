// GCC Basel night UI: all whites at half strength (--wk .5); the day UI is untouched (--wk 1). Screenshots go to /tmp/pbs
const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: process.env.THREE, contentType: 'application/javascript' })); await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => { settings.name = 'T'; settings.course = 'gccb'; $('title').classList.remove('on'); startHole(1); beginHole(); });
  await p.waitForFunction(() => G.state === 'address', null, { timeout: 300000 }); await p.waitForTimeout(1500);
  const read = () => p.evaluate(() => ({ wk: getComputedStyle(document.body).getPropertyValue('--wk').trim(), hudText: getComputedStyle(document.querySelector('#hud b, #hud span')).color, night: document.body.classList.contains('night') }));
  console.log('day  ', await read()); await p.screenshot({ path: '/tmp/pbs/ui-day.png' });
  await p.evaluate(() => { G.night = true; G.neon = 0x2ef2ff; setNeon(0x2ef2ff); $('neonAsk').classList.remove('on'); });
  await p.waitForFunction(() => G.nightU > .95, null, { timeout: 120000 }); await p.waitForTimeout(1500);
  console.log('night', await read()); await p.screenshot({ path: '/tmp/pbs/ui-night.png' });
  await p.evaluate(() => openSheet('menuSheet')); await p.waitForTimeout(1200); await p.screenshot({ path: '/tmp/pbs/ui-night-menu.png' });
  await b.close();
})();
