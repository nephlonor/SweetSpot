// GCC Basel night: the ball's point light lifts the ground and trees round it; the same view with the light on and off goes to /tmp/pbs
const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 }, deviceScaleFactor: 2 })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: process.env.THREE, contentType: 'application/javascript' })); await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => { settings.name = 'T'; settings.course = 'gccb'; $('title').classList.remove('on'); startHole(1); beginHole(); });
  await p.waitForFunction(() => G.state === 'address', null, { timeout: 300000 }); await p.waitForTimeout(500);
  await p.evaluate(() => { G.night = true; G.neon = 0x2ef2ff; setNeon(0x2ef2ff); $('neonAsk').classList.remove('on'); });
  await p.waitForFunction(() => G.nightU > .95, null, { timeout: 120000 });
  await p.evaluate(() => { const t = G.C.startPos, c = G.C.cup, u = .45; placeBall(t.x + (c.x - t.x) * u, t.z + (c.z - t.z) * u, false); G.prev = { x: G.ball.x, z: G.ball.z, teed: false }; autoClubAndAim(); camSnap(); });
  await p.waitForTimeout(3500);
  console.log(await p.evaluate(() => ({ k: +W.ballLight.userData.k.toFixed(2), intensity: +W.ballLight.intensity.toFixed(2), pos: W.ballLight.position.toArray().map(v => +v.toFixed(1)), ball: W.ball.position.toArray().map(v => +v.toFixed(1)) })));
  await p.screenshot({ path: '/tmp/pbs/light-on.png' });
  await p.evaluate(() => { W.ballLight.intensity = 0; W.ballLight.userData.k = 0; window.nightTick = () => { }; }); await p.waitForTimeout(2500); await p.screenshot({ path: '/tmp/pbs/light-off.png' });
  await b.close();
})();
