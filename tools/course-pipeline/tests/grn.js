const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => loadData('stpatricks').then(() => setCourse('stpatricks')));
  for (let h = 0; h < 18; h++) {
    await p.evaluate(h => { $('title').classList.remove('on'); startHole(h); beginHole(); }, h);
    await p.waitForFunction(() => G.state === 'address', null, { timeout: 400000 });
    console.log(h + 1, await p.evaluate(() => { const C = G.C, g = C.green, pts = []; for (let x = -g.R * 1.3; x <= g.R * 1.3; x += 1) for (let z = -g.R * 1.3; z <= g.R * 1.3; z += 1) { const X = g.cx + x, Z = g.cz + z; if (C.surf(X, Z) === S.GREEN) pts.push([x, z, C.h(X, Z)]); }
      const n = pts.length; let sx = 0, sz = 0, sh = 0, sxx = 0, szz = 0, sxz = 0, sxh = 0, szh = 0; for (const [x, z, y] of pts) { sx += x; sz += z; sh += y; } const mx = sx / n, mz = sz / n, mh = sh / n;
      for (const [x, z, y] of pts) { const a = x - mx, c = z - mz, d = y - mh; sxx += a * a; szz += c * c; sxz += a * c; sxh += a * d; szh += c * d; } const det = sxx * szz - sxz * sxz, gx = (sxh * szz - szh * sxz) / det, gz = (szh * sxx - sxh * sxz) / det;
      let mn = 1e9, mxr = -1e9, ms = 0; const q = [0, 0]; for (const [x, z, y] of pts) { const r = y - mh - gx * (x - mx) - gz * (z - mz); mn = Math.min(mn, r); mxr = Math.max(mxr, r); C.grad(g.cx + x, g.cz + z, q); ms = Math.max(ms, Math.hypot(q[0], q[1])); }
      return JSON.stringify({ n, tilt: +Math.hypot(gx, gz).toFixed(3), crown: +(mxr - mn).toFixed(2), maxSlope: +ms.toFixed(3) }); }));
  }
  await b.close();
})();
