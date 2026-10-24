// a lateral drop lands more than 3 m from the water (checked at several waterlines on the first holes with water), and a swipe across the
// leaderboard moves to the next / previous course
const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 }, hasTouch: true })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: process.env.THREE, contentType: 'application/javascript' })); await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  console.log('swipe', await p.evaluate(async () => {
    settings.name = 'T'; openBoard(); const bb = $('boardBody'), out = [Board.view];
    const touch = (type, x, y) => { const t = new Touch({ identifier: 1, target: bb, clientX: x, clientY: y }); bb.dispatchEvent(new TouchEvent(type, { touches: type === 'touchend' ? [] : [t], changedTouches: [t], bubbles: true })); };
    const swipe = (x0, x1) => { touch('touchstart', x0, 400); touch('touchend', x1, 410); };
    swipe(300, 120); out.push(Board.view); swipe(300, 120); out.push(Board.view); swipe(120, 300); out.push(Board.view); swipe(200, 230); out.push(Board.view + ' (a short drag: unchanged)');
    return out;
  }));
  const res = await p.evaluate(() => {
    settings.course = 'gccb'; $('title').classList.remove('on'); closeSheets(); const out = [];
    for (let h = 0; h < 18 && out.length < 6; h++) {
      startHole(h); const C = G.C, I = C.inner;
      for (let x = I.minX; x < I.maxX && out.length < 6; x += 6) for (let z = I.minZ; z < I.maxZ && out.length < 6; z += 6) {
        if (C.surf(x, z) !== S.WATER) continue;
        let E = null; for (let a = 0; a < 12 && !E; a++) { const ex = x + Math.cos(a * TAU / 12) * 2.5, ez = z + Math.sin(a * TAU / 12) * 2.5; if (dryGround(ex, ez)) E = [ex, ez]; }
        if (!E || Math.random() < .6) continue;
        const o = waterOptions({ lastDry: E, final: { x, z } }).find(q => q.k === 'lateral'); if (!o) { out.push({ h, lateral: 'none' }); continue; }
        let near = 99; for (let rr = .5; rr <= 3.2; rr += .5) for (let a = 0; a < 24; a++) if (C.surf(o.x + Math.cos(a * TAU / 24) * rr, o.z + Math.sin(a * TAU / 24) * rr) === S.WATER) near = Math.min(near, rr);
        out.push({ h, fromEntry: +Math.hypot(o.x - E[0], o.z - E[1]).toFixed(1), waterWithin3m: near < 3.01, nearestWaterRing: near === 99 ? '>3.2' : near });
      }
    }
    return out;
  });
  console.log('drops', JSON.stringify(res));
  await b.close();
})();
