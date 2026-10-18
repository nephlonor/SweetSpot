const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => loadData('rothley').then(() => setCourse('rothley')));
  await p.evaluate(() => { $('title').classList.remove('on'); startHole(6); beginHole(); G.snapCam = true; });
  await p.waitForFunction(() => G.state === 'address', null, { timeout: 400000 });
  console.log(await p.evaluate(() => {
    const C = G.C, bx = G.ball.x, bz = G.ball.z, dx = C.cup.x - bx, dz = C.cup.z - bz, L = Math.hypot(dx, dz), ux = dx / L, uz = dz / L, out = [];
    GC.trees.forEach((t, i) => { const q = C.loc(t.e, t.n), x = q[0], z = -q[1], a = (x - bx) * ux + (z - bz) * uz, c = (x - bx) * -uz + (z - bz) * ux; if (a > 5 && a < 130 && Math.abs(c) < 16) out.push([i, Math.round(a), +c.toFixed(1), t.d, t.kind, t.H]); });
    return JSON.stringify(out.sort((p, q) => p[1] - q[1]));
  }));
  await b.close();
})();
