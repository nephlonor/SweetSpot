// keyboard: with --kb/--vvh set the sheet sits above it and the focused field stays inside the visible area
const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 780 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: process.env.THREE, contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => { settings.name = 'TEST'; saveSettings(); openSheet('menuSheet'); menuPage('feature'); }); await p.waitForTimeout(700);
  await p.evaluate(() => { document.documentElement.style.setProperty('--kb', '330px'); document.documentElement.style.setProperty('--vvh', '450px'); });
  await p.evaluate(() => { window.kbSync = () => {}; }); await p.focus('#frD'); await p.waitForTimeout(1200);
  console.log(await p.evaluate(() => { const r = $('frD').getBoundingClientRect(), s = $('menuSheet').getBoundingClientRect(); return { field: [r.top, r.bottom], sheet: [s.top, s.bottom], limit: 450 }; }));
  await p.screenshot({ path: '/tmp/pbs/kbd.png' }); await b.close();
})();
