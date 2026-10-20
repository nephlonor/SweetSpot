const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.stack.split('\n').slice(0, 3).join(' | ')));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => loadData('stpatricks').then(() => setCourse('stpatricks')));
  for (const h of [10, 11, 13, 0, 3]) {
    await p.evaluate(h => { $('title').classList.remove('on'); G.weather = WEATHERS[0]; G.wxNext = WEATHERS[0]; G.wxLeft = 9; startRound(); startHole(h); beginHole(); }, h);
    await p.waitForFunction(() => G.state === 'address', null, { timeout: 400000 }); await p.waitForTimeout(500);
    console.log(await p.evaluate(() => { const C = G.C, t = G.target; return JSON.stringify({ hole: G.hole + 1, club: CLUBS[G.club].name, carry: CLUBS[G.club].carry, pinD: Math.round(distToPin()), target: t ? t.map(v => +v.toFixed(0)) : null, toTarget: t ? Math.round(Math.hypot(t[0] - G.ball.x, t[1] - G.ball.z)) : null, targetToPin: t ? Math.round(Math.hypot(t[0] - C.cup.x, t[1] - C.cup.z)) : null, yaw: +(G.yaw / DEG).toFixed(1) }); }));
  }
  await b.close();
})();
