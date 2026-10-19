const { chromium } = require('/opt/node-tools/node_modules/playwright'); const fs = require('fs');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => loadData('stpatricks').then(() => setCourse('stpatricks')));
  const h = +(process.argv[2] || 14), name = process.argv[3] || 'drone';
  await p.evaluate(h => { $('title').classList.remove('on'); G.weather = WEATHERS[1]; G.wxNext = WEATHERS[1]; G.wxLeft = 9; startHole(h); beginHole(); }, h);
  await p.waitForFunction(() => G.state === 'address', null, { timeout: 400000 });
  await p.evaluate(([e, n]) => { const q = G.C.loc(e, n); placeBall(q[0], -q[1], false); }, [+process.argv[4], +process.argv[5]]);
  await p.waitForFunction(() => G.state === 'address', null, { timeout: 400000 }); await p.waitForTimeout(1500);
  const url = await p.evaluate(() => {
    // a drone view like the club's photographs: 45 m up, 40 m behind the ball, looking down the hole
    const C = G.C, bx = G.ball.x, bz = G.ball.z, dx = C.cup.x - bx, dz = C.cup.z - bz, L = Math.hypot(dx, dz), ux = dx / L, uz = dz / L;
    const w = 750, hh = 420, cam = new THREE.PerspectiveCamera(55, w / hh, 1, 3000);
    { const j = groundJob(W.life, bx, bz); let r; do { r = j.next(); } while (!r.done); } cam.position.set(bx - ux * 4, C.h(bx, bz) + 1.3, bz - uz * 4); cam.lookAt(bx + ux * 20, C.h(bx, bz), bz + uz * 20); cam.updateMatrixWorld();
    const rt = new THREE.WebGLRenderTarget(w, hh, { depthBuffer: true }); const hide = [W.ball, W.aim, W.ring, W.tracer]; hide.forEach(o => o && (o.visible = false));
    W.ren.setRenderTarget(rt); W.ren.render(W.scene, cam); const buf = new Uint8Array(w * hh * 4); W.ren.readRenderTargetPixels(rt, 0, 0, w, hh, buf); W.ren.setRenderTarget(null);
    const cv = document.createElement('canvas'); cv.width = w; cv.height = hh; const x = cv.getContext('2d'), img = x.createImageData(w, hh);
    for (let j = 0; j < hh; j++) img.data.set(buf.subarray((hh - 1 - j) * w * 4, (hh - j) * w * 4), j * w * 4); x.putImageData(img, 0, 0); return cv.toDataURL('image/png');
  });
  fs.writeFileSync(`/tmp/stpat/shots/${name}.png`, Buffer.from(url.split(',')[1], 'base64')); await b.close();
})();
