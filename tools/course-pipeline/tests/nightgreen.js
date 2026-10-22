// GCC Basel night, by the green: glow worms live round the green, the ball lights a little of the ground, and the tempo and strike
// panels are almost black; screenshot goes to /tmp/pbs/night-green.png
const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: process.env.THREE, contentType: 'application/javascript' })); await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => { settings.name = 'T'; settings.course = 'gccb'; $('title').classList.remove('on'); startHole(1); beginHole(); });
  await p.waitForFunction(() => G.state === 'address', null, { timeout: 300000 }); await p.waitForTimeout(500);
  await p.evaluate(() => { G.night = true; G.neon = 0x2ef2ff; setNeon(0x2ef2ff); $('neonAsk').classList.remove('on'); });
  await p.waitForFunction(() => G.nightU > .95, null, { timeout: 120000 });
  await p.evaluate(() => { const c = G.C.cup; placeBall(c.x + 6, c.z + 30, false); G.prev = { x: G.ball.x, z: G.ball.z, teed: false }; autoClubAndAim(); camSnap(); });
  await p.waitForTimeout(3500);
  console.log(await p.evaluate(() => ({ worms: W.worms.d.length, nearGreen: W.worms.d.filter(w => Math.hypot(w.hx - G.C.cup.x, w.hz - G.C.cup.z) < 30).length, pool: W.ballPool.visible, poolOp: +W.ballPool.material.opacity.toFixed(2), state: G.state })));
  await p.screenshot({ path: '/tmp/pbs/night-green.png' });
  await b.close();
})();
