// Pebble Beach: a gull comes to look at the ball after it comes to rest, and leaves when the camera comes in
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
  await p.evaluate(() => { $('title').classList.remove('on'); startRound(); G.gullHole = 0; });
  await p.waitForFunction(() => G.state === 'address' || G.state === 'intro', null, { timeout: 400000 });
  await p.evaluate(() => { $('intro').classList.remove('on'); beginHole(); G.snapCam = true; });
  await p.waitForFunction(() => G.state === 'address', null, { timeout: 400000 }); await p.waitForTimeout(1500);
  console.log('deer/rabbits', await p.evaluate(() => W.life.ents.filter(e => e.kind === 'deer' || e.kind === 'rabbit').length), 'gull state', await p.evaluate(() => W.life.vis.st));
  // the ball comes to rest 150 m down the fairway; the camera is still far back. Time is stepped by hand (headless frames are slow).
  const log = await p.evaluate(() => {
    const C = G.C, q = polyAt(C.center, 150), out = []; placeBall(q[0], q[1], false); G.state = 'settle'; G.settleT = -1e3; W.cam.position.set(q[0] - 40, G.ball.y + 12, q[1] - 40);
    const L = W.life; L.pst = 'address'; let t = 0; const step = n => { for (let i = 0; i < n; i++) { updateLife(.05, t); t += .05; } };
    const st = () => { const g = L.vis, bp = W.ball.position; return g.st + ' d_ball ' + Math.hypot(g.x - bp.x, g.z - bp.z).toFixed(1) + ' done ' + G.gullDone; };
    for (let k = 0; k < 8; k++) { step(30); out.push((k * 1.5 + 1.5).toFixed(1) + 's ' + st()); }
    window.__q = q; return out;
  });
  console.log(log.join('\n'));
  await p.evaluate(() => { const bp = W.ball.position, L = W.life; L.pst = 'settle'; W.cam.position.set(bp.x - 14, bp.y + 3.2, bp.z - 10); G.camLook.set(bp.x, bp.y, bp.z); W.cam.lookAt(bp.x, bp.y + .3, bp.z); });
  await p.waitForTimeout(500); await p.screenshot({ path: '/tmp/pbs/gull.png' });
  console.log('camera in close:', await p.evaluate(() => { const L = W.life, bp = W.ball.position; W.cam.position.set(bp.x - 8, bp.y + 2.5, bp.z - 8); for (let i = 0; i < 10; i++) updateLife(.05, 100 + i); return L.vis.st; }));
  console.log('deer/rabbits', await p.evaluate(() => W.life.ents.filter(e => e.kind === 'deer' || e.kind === 'rabbit').length));
  await b.close();
})();
