const { chromium } = require('/opt/node-tools/node_modules/playwright'); const fs = require('fs');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: process.env.THREE || (__dirname + '/three.min.js'), contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(c => loadData(c).then(() => setCourse(c)), process.env.COURSE || 'stpatricks');
  for (const h of [0, 5, 13, 17]) {
    await p.evaluate(h => { $('title').classList.remove('on'); startHole(h); beginHole(); }, h);
    await p.waitForFunction(() => G.state === 'address', null, { timeout: 400000 }); await p.waitForTimeout(500);
    await p.evaluate(() => $('mapBtn').click()); await p.waitForTimeout(2500);
    await p.screenshot({ path: `${process.env.SHOTS || '/tmp/stpat/shots'}/map${h + 1}.png` }); await p.evaluate(() => closeSheets());
  }
  await b.close();
})();
