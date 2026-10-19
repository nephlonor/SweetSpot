const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => loadData('stpatricks').then(() => setCourse('stpatricks')));
  for (let h = 0; h < 18; h++) {
    await p.evaluate(h => { $('title').classList.remove('on'); startHole(h); beginHole(); G.snapCam = true; }, h);
    await p.waitForFunction(() => G.state === 'address', null, { timeout: 400000 }); await p.waitForTimeout(800);
    console.log(h + 1, await p.evaluate(() => {
      const C = G.C, bx = G.ball.x, bz = G.ball.z, y0 = C.h(bx, bz); let mn = 1e9, mx = -1e9;
      for (let x = -4; x <= 4; x += .5) for (let z = -5; z <= 5; z += .5) { const y = C.h(bx + x, bz + z); mn = Math.min(mn, y); mx = Math.max(mx, y); }
      const r = C.center, eye = y0 + 1.6; let worst = -9, at = 0; const ux = Math.sin(G.yaw), uz = -Math.cos(G.yaw);
      for (let d = 6; d <= 200; d += 2) { const a = (C.h(bx + ux * d, bz + uz * d) - eye) / d; if (a > worst) { worst = a; at = d; } }
      // can the eye see the ground where a drive lands (200-250 m)?
      let vis = 0; for (let d = 200; d <= 250; d += 10) { const yt = C.h(bx + ux * d, bz + uz * d), sl = (yt - eye) / d; let ok = true; for (let e = 4; e < d; e += 2) if (C.h(bx + ux * e, bz + uz * e) > eye + sl * e + .3) { ok = false; break; } vis += ok; }
      return JSON.stringify({ teeRange: +(mx - mn).toFixed(2), rise: +worst.toFixed(3), at, landVis: vis + '/6' });
    }));
  }
  await b.close();
})();
