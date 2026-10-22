// GCC Basel night: a putt leaves the glowing trail too, until the ball has almost stopped; the Replay button is black; glow worms drift;
// the dark course screenshot goes to /tmp/pbs
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
  await p.waitForFunction(() => G.nightU > .95, null, { timeout: 120000 }); await p.waitForTimeout(2500);
  console.log('putt', await p.evaluate(() => {
    const c = G.C.cup, bx = c.x + 4, bz = c.z, y = G.C.h(bx, bz), d = Math.hypot(c.x - bx, c.z - bz), sp = 2.4;
    const res = simulateShot(G.C, { x: bx, y: y + .03, z: bz, v: [(c.x - bx) / d * sp, 0, (c.z - bz) / d * sp], w: [0, 0, 0], wind: null, putt: true, flag: false });
    const fr = res.frames, rest = trailRest(fr, res.n), out = { n: res.n, duration: +res.duration.toFixed(2), rest: +rest.toFixed(2) };
    for (const [nm, t] of [['rolling', rest * .5], ['atRest', rest], ['rest+1', rest + 1], ['rest+2.5', rest + 2.5]]) { trailFill(fr, res.n, Math.min(t, res.duration)); out[nm] = { n: W.trail.geometry.drawRange.count, fade: +W.trailFade.toFixed(3) }; }
    return out;
  }));
  console.log('worms', await p.evaluate(() => ({ shown: W.worms.pts.visible, n: W.worms.pts.geometry.attributes.position.count, y0: +W.worms.pts.geometry.attributes.position.array[1].toFixed(2) })));
  await p.screenshot({ path: '/tmp/pbs/night-dark.png' });
  await p.evaluate(() => { $('d1').textContent = 'Birdie'; $('done').classList.add('on'); }); await p.waitForTimeout(900);
  console.log('replay btn', await p.evaluate(() => getComputedStyle($('dReplay')).backgroundImage.slice(0, 60)));
  await p.screenshot({ path: '/tmp/pbs/night-done.png' });
  await b.close();
})();
