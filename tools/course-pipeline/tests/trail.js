// GCC Basel at night: a drive trails small glowing neon particles off the ball (a putt trails none); screenshots at two points in the flight
const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: process.env.THREE, contentType: 'application/javascript' })); await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => { settings.name = 'T'; settings.course = 'gccb'; $('title').classList.remove('on'); startHole(0); beginHole(); });
  await p.waitForFunction(() => G.state === 'address', null, { timeout: 300000 }); await p.waitForTimeout(800);
  await p.evaluate(() => { G.night = true; G.nightU = 1; setNeon(0xff2fa0); $('neonAsk').classList.remove('on'); G.yaw = 0.05; });
  await p.waitForTimeout(800);
  for (const [name, f] of [['early', .08], ['mid', .3]]) {
    const tt = await p.evaluate(f => {
      const L = computeLaunch(G.club, { p: 1, Tb: .45, Td: .15 }, { h: 0, v: 0 }, G.surf, G.yaw, settings.hand, G.teed);
      const res = simulateShot(G.C, { x: G.ball.x, y: G.ball.y + .03, z: G.ball.z, v: L.v, w: L.w, wind: G.wind, putt: false, flag: true });
      const tt = res.frames[Math.floor(res.n * f) * 5]; window.__res = res;
      W.tracerT0 = performance.now(); W.tracer.visible = true; W.tracer.material.opacity = .8;
      trailFill(res.frames, res.n, tt); W.aim.visible = false; W.ring.visible = false;
      return tt;
    }, f);
    await p.waitForTimeout(700); console.log(name, 'tt', +tt.toFixed(2), await p.evaluate(() => ({ trail: W.trail.visible, n: W.trail.geometry.drawRange.count, glow: W.ballGlow.visible, glowScale: +W.ballGlow.scale.x.toFixed(3), night: document.body.classList.contains('night') })));
    await p.screenshot({ path: `/tmp/pbs/trail-${name}.png` });
    await p.evaluate(() => { W.ball.visible = true; W.aim.visible = true; W.ring.visible = true; });
  }
  await b.close();
})();
