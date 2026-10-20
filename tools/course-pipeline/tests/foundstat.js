const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(3000);
  console.log(await p.evaluate(() => {
    ST.found = 3; ST.lost = 2; openStats(); const own = [...document.querySelectorAll('#statsBody .stRow, .sheet.on .stRow')].filter(r => r.textContent.includes('Balls found')).map(r => r.textContent.replace(/\s+/g, ' ')).join(' | ');
    const fun = [...document.querySelectorAll('.stFun div')].map(d => d.textContent).filter(t => t.includes('found after')).join(' | ');
    closeSheets(); DL.players = { z: { n: 'Zoe', pf: { xp: 100, r: 1, h: 18, fd: 4, lo: 1 } } }; DL.playersAt = Date.now() + 1e9; openPlayer({ name: 'Zoe', id: 'z' });
    return JSON.stringify({ own, fun, compact: [profileCompact().fd, profileCompact().lo] });
  }));
  await p.waitForTimeout(800);
  console.log(await p.evaluate(() => [...$('playerBody').querySelectorAll('.stRow')].filter(r => r.textContent.includes('Balls found')).map(r => r.textContent.replace(/\s+/g, ' ')).join(' | ')));
  await b.close();
})();
