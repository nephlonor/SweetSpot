const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: process.env.THREE, contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => openBoard()); await p.waitForTimeout(1000);
  await p.evaluate(() => { const o = fillBoard; window.fillBoard = function (el, l, k, pk) { console.log('FILL', k, new Error().stack.split('\n').slice(2, 5).join(' < ')); return o.apply(this, arguments); }; });
  p.on('console', m => { if (m.text().startsWith('FILL')) console.log(m.text().slice(0, 300)); });
  // let go between two names (browser snapping off, as on a browser that ignores it): the wheel must ease to the nearest name and select it
  await p.evaluate(() => { const w = document.querySelector('.cwheel'); w.style.scrollSnapType = 'none'; w.scrollTop = 44 * 3 + 13; });
  for (let i = 0; i < 6; i++) { await p.waitForTimeout(500); console.log(await p.evaluate(() => JSON.stringify({ top: Math.round(document.querySelector('.cwheel').scrollTop), name: $('boardName').textContent }))); }
  await b.close();
})();
