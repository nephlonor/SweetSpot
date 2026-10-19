const { chromium } = require('/opt/node-tools/node_modules/playwright'); const fs = require('fs');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => loadData('rothley').then(() => setCourse('rothley')));
  const tag = process.argv[2] || 'a';
  const near = await p.evaluate(() => RDC.data.bridges.map(b => { let best = 0, bd = 1e9; RDC.data.holes.forEach((hd, i) => { const L = hd.line; for (let k = 0; k + 1 < L.length; k++) { const [x0, y0] = L[k], [x1, y1] = L[k + 1], dx = x1 - x0, dy = y1 - y0, t = Math.max(0, Math.min(1, ((b[0] - x0) * dx + (b[1] - y0) * dy) / (dx * dx + dy * dy))), d = Math.hypot(b[0] - x0 - t * dx, b[1] - y0 - t * dy); if (d < bd) { bd = d; best = i; } } }); return best; }));
  console.log('near', near); const holes = [...new Set(near)];
  const seen = new Set();
  for (const h of holes) {
    await p.evaluate(h => { $('title').classList.remove('on'); G.weather = WEATHERS[1]; G.wxNext = WEATHERS[1]; G.wxLeft = 9; startHole(h); beginHole(); }, h);
    await p.waitForFunction(() => G.state === 'address', null, { timeout: 400000 }); await p.waitForTimeout(1200);
    const res = await p.evaluate(near => {
      const C = G.C, out = [];
      for (const [k, b] of RDC.data.bridges.entries()) {
        const q0 = C.loc(b[0], b[1]), cx = q0[0], cz = -q0[1];
        if (near[k] !== G.hole) continue;
        const a = b[4] * Math.PI / 180, q1 = C.loc(b[0] + Math.cos(a), b[1] + Math.sin(a)), ax = q1[0] - q0[0], az = -(q1[1] - q0[1]), px = -az, pz = ax;
        let lv = null; for (const pd of C.ponds) { const inf = C.info ? null : null; } 
        let wl = -1e9; for (let t = -1; t <= 1; t += .25) for (let s2 = -1; s2 <= 1; s2 += .5) wl = Math.max(wl, C.wl(cx + px * t * b[3] / 2 + ax * s2 * b[2] / 2, cz + pz * t * b[3] / 2 + az * s2 * b[2] / 2)); let deck = null; W.scene.traverse(o => { if (o.isMesh && o.geometry.type === 'PlaneGeometry' && o.material.map && Math.hypot(o.position.x - cx, o.position.z - cz) < .1) deck = o.position.y; });
        const s = []; for (let t = -1; t <= 1; t += .25) s.push(+C.h(cx + px * t * b[3], cz + pz * t * b[3]).toFixed(2));
        const surf = C.surf(cx, cz);
        // render a close view
        const w = 500, hh = 300, cam = new THREE.PerspectiveCamera(50, w / hh, .5, 2000), yc = C.h(cx, cz);
        cam.position.set(cx + ax * 12 + px * 5, (deck || yc) + 3, cz + az * 12 + pz * 5); cam.lookAt(cx, yc, cz); cam.updateMatrixWorld();
        const rt = new THREE.WebGLRenderTarget(w, hh, { depthBuffer: true }); [W.ball, W.aim, W.ring, W.tracer].forEach(o => o && (o.visible = false));
        W.ren.setRenderTarget(rt); W.ren.render(W.scene, cam); const buf = new Uint8Array(w * hh * 4); W.ren.readRenderTargetPixels(rt, 0, 0, w, hh, buf); W.ren.setRenderTarget(null);
        const cv = document.createElement('canvas'); cv.width = w; cv.height = hh; const x = cv.getContext('2d'), img = x.createImageData(w, hh);
        for (let j = 0; j < hh; j++) img.data.set(buf.subarray((hh - 1 - j) * w * 4, (hh - j) * w * 4), j * w * 4); x.putImageData(img, 0, 0);
        out.push({ k, deck: deck && +deck.toFixed(2), yc: +yc.toFixed(2), wl: wl != null ? +wl.toFixed(2) : null, surf, prof: s, url: cv.toDataURL('image/png') });
      }
      return out;
    }, near);
    for (const r of res) { if (seen.has(r.k)) continue; seen.add(r.k); console.log(h + 1, JSON.stringify({ ...r, url: undefined })); fs.writeFileSync(`/tmp/stpat/shots/br_${tag}_${r.k}.png`, Buffer.from(r.url.split(',')[1], 'base64')); }
  }
  await b.close();
})();
