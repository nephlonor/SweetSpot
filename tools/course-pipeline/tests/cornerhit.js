const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: process.env.THREE, contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => loadData('pebblebeach').then(() => setCourse('pebblebeach')));
  await p.evaluate(() => { $('title').classList.remove('on'); startHole(13); beginHole(); G.snapCam = true; });
  await p.waitForFunction(() => G.state === 'address', null, { timeout: 400000 });
  console.log(await p.evaluate(() => {
    const C = G.C, st = C.startPos, out = [], H = C.def.rh, l0 = H.line[0], l1 = H.line[1];
    const q0 = C.loc(l0[0], l0[1]), q1 = C.loc(l1[0], l1[1]); const base = Math.atan2(-q1[1] + q0[1], q1[0] - q0[0]);
    for (let da = -50; da <= 50; da += 5) {
      const ang = base + da * Math.PI / 180, v = 62, el = .2, vh = v * Math.cos(el);
      const r = simulateShot(C, { x: G.ball.x, y: G.ball.y + .03, z: G.ball.z, v: [Math.cos(ang) * vh, v * Math.sin(el), Math.sin(ang) * vh], w: [0, 0, 0], wind: null, putt: false, flag: true });
      const tr = r.events.filter(e => e.type === 'tree').slice(0, 2).map(e => 'id ' + e.id + (e.trunk ? ' trunk' : '') + ' at ' + (e.x - G.ball.x).toFixed(1) + ',' + (e.z - G.ball.z).toFixed(1) + ' h ' + (e.y - G.ball.y).toFixed(1) + ' t ' + e.t.toFixed(2));
      out.push(da + ' deg: ' + (tr.length ? tr.join(' | ') : 'clear') + ' total ' + r.total.toFixed(0));
    }
    return out.join('\n');
  }));
  await b.close();
})();
