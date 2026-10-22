// GCC Basel night: aiming away from the clubhouse on the first tee does nothing; holding the aim on it starts the night, shows the
// neon colour pop-up, and a picked colour lights the ball. Screenshots of the day, the night and the pop-up go to /tmp/pbs.
const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: process.env.THREE, contentType: 'application/javascript' })); await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => { settings.name = 'T'; settings.course = 'gccb'; $('title').classList.remove('on'); startHole(0); beginHole(); });
  await p.waitForFunction(() => G.state === 'address', null, { timeout: 300000 }); await p.waitForTimeout(1500);
  const st = () => p.evaluate(() => ({ night: !!G.night, nightU: +(G.nightU || 0).toFixed(2), look: +(G.nightLook || 0).toFixed(2), popup: $('neonAsk').classList.contains('on'), neon: G.neon, glow: W.ballGlow.visible }));
  // 1. the fairway: no trigger
  await p.evaluate(() => { G.yaw = 0; }); await p.waitForTimeout(2500); console.log('fairway', await st());
  // 2. the clubhouse on the first tee: the look has to hold
  await p.evaluate(() => { G.yaw = clubhouseOf(G.C).yaw; }); await p.waitForTimeout(400); console.log('brief look', await st());
  await p.evaluate(() => { G.yaw = clubhouseOf(G.C).yaw; }); await p.waitForFunction(() => G.night, null, { timeout: 120000 });
  await p.waitForFunction(() => G.nightU > .98, null, { timeout: 120000 });
  console.log('turned to clubhouse', await st()); await p.waitForTimeout(600);
  await p.evaluate(() => { $('neonAsk').classList.remove('on'); }); await p.waitForTimeout(400); await p.screenshot({ path: '/tmp/pbs/night-clubhouse.png' });
  await p.evaluate(() => { $('neonAsk').classList.add('on'); }); await p.waitForTimeout(700); await p.screenshot({ path: '/tmp/pbs/night-popup.png' });
  await p.click('.neonO[data-i="2"]'); await p.waitForTimeout(300); console.log('picked cyan', await st(), await p.evaluate(() => W.ball.material.emissive.getHex().toString(16)));
  // 3. the fairway at night, with the floodlights
  await p.evaluate(() => { G.yaw = 0; }); await p.waitForTimeout(1200); await p.screenshot({ path: '/tmp/pbs/night-fairway.png' });
  await b.close();
})();
