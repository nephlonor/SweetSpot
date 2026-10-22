// GCC Basel night, round two: fairway wash along the hole, black UI, trail that lasts until the ball has almost stopped, spookier waltz;
// the wildflowers are forced visible once, as a control for the colour-dot artefact
const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: process.env.THREE, contentType: 'application/javascript' })); await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => { settings.name = 'T'; settings.course = 'gccb'; $('title').classList.remove('on'); startHole(2); G.night = true; G.nightU = 1; G.neon = 0xffb020; setNeon(0xffb020); });
  await p.waitForTimeout(4000);
  console.log('wash', await p.evaluate(() => ({ lights: W.flood.length, discs: W.flood.filter(o => o.geometry && o.geometry.index).length })));
  await p.screenshot({ path: '/tmp/pbs/n2-intro.png' });
  await p.evaluate(() => { const o = nightTick; window.__orig = o; nightTick = dt => { o(dt); if (W.life && W.life.hMesh) W.life.hMesh.visible = W.life.sMesh.visible = true; }; }); await p.waitForTimeout(1500);
  await p.screenshot({ path: '/tmp/pbs/n2-flowers-forced.png' });
  await p.evaluate(() => { nightTick = window.__orig; beginHole(); }); await p.waitForFunction(() => G.state === 'address', null, { timeout: 300000 }); await p.waitForTimeout(1500);
  await p.screenshot({ path: '/tmp/pbs/n2-address.png' });
  console.log('trail', await p.evaluate(() => {
    const L = computeLaunch(G.club, { p: 1, Tb: .45, Td: .15 }, { h: 0, v: 0 }, G.surf, G.yaw, settings.hand, G.teed);
    const res = simulateShot(G.C, { x: G.ball.x, y: G.ball.y + .03, z: G.ball.z, v: L.v, w: L.w, wind: G.wind, putt: false, flag: true });
    const fr = res.frames, rest = trailRest(fr, res.n), out = { rest: +rest.toFixed(2), duration: +res.duration.toFixed(2) };
    for (const [nm, t] of [['air', rest * .4], ['preRest', rest - .2], ['rest+.5', rest + .5], ['rest+2', rest + 2]]) { trailFill(fr, res.n, Math.min(t, res.duration)); out[nm] = { n: W.trail.geometry.drawRange.count, fade: +W.trailFade.toFixed(3) }; }
    return out;
  }));
  console.log(await p.evaluate(async () => { const a = new AudioContext(); await a.resume().catch(() => { }); hwSetup(a); try { for (let i = 0; i < 400; i++) hwStep(a, i, a.currentTime + i * .01); } catch (e) { return 'ERR ' + e.message; } return 'waltz ok, stops ' + MUS.stops.length; }));
  await b.close();
})();
