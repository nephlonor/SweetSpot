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
  for (const h of [3, 4, 13, 14]) {
    await p.evaluate(h => { $('title').classList.remove('on'); startHole(h); beginHole(); }, h);
    await p.waitForFunction(() => G.state === 'address', null, { timeout: 400000 });
    console.log(h + 1, await p.evaluate(() => { const C = G.C, out = [];
      for (let e = -700; e <= -300; e += 20) { const n = C.enu(0, 0)[1] + 60; const q = C.loc(e, n), x = q[0], z = -q[1]; const s = C.surf(x, z); out.push(e + ':' + s + (C.isOB(x, z) ? 'ob' : '') + '@' + C.h(x, z).toFixed(1)); }
      return out.join(' '); }));
  }
  await b.close();
})();
