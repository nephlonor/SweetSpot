// Pebble Beach: the lateral drop after the sea or the shore is always on the fairway; the stakes along the cliffs are red
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
  for (const hole of [6, 7, 9, 17]) {
    await p.evaluate(h => { $('title').classList.remove('on'); startHole(h); beginHole(); G.snapCam = true; }, hole);
    await p.waitForFunction(() => G.state === 'address', null, { timeout: 400000 });
    console.log('hole', hole + 1, await p.evaluate(() => {
      const C = G.C, cnt = { n: 0, fw: 0, none: 0 }, bad = [];
      for (let k = 0; k < 150; k++) {
        const ang = Math.random() * 6.283, el = .25 + Math.random() * .5, v = 25 + Math.random() * 45, vh = v * Math.cos(el);
        const r = simulateShot(C, { x: G.ball.x, y: G.ball.y, z: G.ball.z, v: [Math.cos(ang) * vh, v * Math.sin(el), Math.sin(ang) * vh], w: [0, 0, 0], wind: null, putt: false, flag: true });
        if (!r.water) continue; cnt.n++;
        const lat = waterOptions(r).find(o => o.k === 'lateral'); if (!lat) { cnt.none++; continue; }
        if (C.surf(lat.x, lat.z) === S.FAIR) cnt.fw++; else bad.push(SURF[C.surf(lat.x, lat.z)].name);
      }
      return JSON.stringify(cnt) + ' not fairway: ' + bad.slice(0, 5);
    }));
  }
  await b.close();
})();
