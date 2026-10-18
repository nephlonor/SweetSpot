const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.stack.split('\n').slice(0,3).join(' | ')));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: '/tmp/claude-0/-home-user-SweetSpot/42254a9d-b7ad-52d7-9d2e-d0f8e3c6d97d/scratchpad/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500); await p.evaluate(() => loadData('rothley').then(() => setCourse('rothley')));
  await p.evaluate(() => { $('title').classList.remove('on'); const sty = document.createElement('style'); sty.textContent = '#hud,#pinTag,#ballTag,#aimHint,.hint{opacity:0!important}'; document.head.appendChild(sty); });
  const from = +(process.argv[2] || 0), to = +(process.argv[3] || 17);
  for (let h = from; h <= to; h++) {
    const t0 = Date.now();
    await p.evaluate((h) => { startHole(h); beginHole(); G.snapCam = true; }, h);
    await p.waitForFunction(() => G.state === 'address', null, { timeout: 400000 });
    const inf = await p.evaluate(() => ({ n: G.C.def.name, club: CLUBS[G.club].name, yaw: +(G.yaw / DEG).toFixed(1), ntr: W.trees.length, ponds: G.C.ponds.length, surf: G.surf, cupSurf: G.C.surf(G.C.cup.x, G.C.cup.z) }));
    console.log(h + 1, Date.now() - t0, 'ms', JSON.stringify(inf), await p.evaluate(() => JSON.stringify({ wx: G.weather.id, st: G.state, cam: W.cam.position.toArray().map(v => +v.toFixed(1)), rot: W.cam.rotation.toArray().slice(0, 3).map(v => +(+v).toFixed(2)), intro: $('intro').classList.contains('on') })));
    await p.waitForTimeout(1200); await p.screenshot({ path: `/tmp/rothley/shots/h${h + 1}.png` });
  }
  await b.close();
})();
