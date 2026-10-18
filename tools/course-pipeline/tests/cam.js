const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  const course = process.argv[2] || 'rothley', hole = +(process.argv[3] || 8);
  await p.evaluate(c => loadData(c).then(() => setCourse(c)), course);
  await p.evaluate(() => { $('title').classList.remove('on'); const sty = document.createElement('style'); sty.textContent = '#hud,#pinTag,#ballTag,#aimHint,.hint{opacity:0!important}'; document.head.appendChild(sty); });
  for (const wx of ['fine', 'rain']) {
    await p.evaluate(([h, wx]) => { G.wxLeft = 9; G.wxK = 3; G.wxN = 8; G.weather = WEATHERS.find(w => w.id === wx); G.wxNext = G.weather; startHole(h); beginHole(); G.snapCam = true; }, [hole, wx]);
    await p.waitForFunction(() => G.state === 'address', null, { timeout: 400000 }); await p.waitForTimeout(1500);
    console.log(wx, await p.evaluate(() => JSON.stringify({ wx: G.weather.id, cam: W.cam.position.toArray().map(v => +v.toFixed(1)), ball: [G.ball.x, G.ball.z].map(v => +v.toFixed(1)), rot: W.cam.rotation.toArray().slice(0, 3).map(v => +(+v).toFixed(2)) })));
    await p.screenshot({ path: `/tmp/rothley/shots/cam_${wx}.png` });
  }
  await b.close();
})();
