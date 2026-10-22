// GCC Basel night survives leaving the app: the round is saved with the night and the neon colour, and a resumed round (a fresh page)
// has the neon ball and its glow again; a new round after it is a plain ball again
const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const ctx = await b.newContext({ viewport: { width: 405, height: 720 } }), p = await ctx.newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: process.env.THREE, contentType: 'application/javascript' })); await p.route('**/fonts.googleapis.com/**', r => r.abort());
  const open = async () => { await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500); };
  const look = () => p.evaluate(() => ({ night: !!G.night, neon: G.neon && G.neon.toString(16), emissive: W.ball.material.emissive.getHex().toString(16), glow: W.ballGlow.visible, glowCol: W.ballGlow.material.color.getHex().toString(16), nightU: +(G.nightU || 0).toFixed(2) }));
  await open();
  await p.evaluate(() => { settings.name = 'T'; settings.course = 'gccb'; $('title').classList.remove('on'); startHole(0); beginHole(); });
  await p.waitForFunction(() => G.state === 'address', null, { timeout: 300000 }); await p.waitForTimeout(500);
  await p.evaluate(() => { nightStart(); }); await p.waitForFunction(() => $('neonAsk').classList.contains('on'), null, { timeout: 60000 });
  await p.click('.neonO[data-i="1"]'); await p.waitForTimeout(1200); console.log('picked   ', await look());
  console.log('saved    ', await p.evaluate(() => { const r = JSON.parse(localStorage.getItem(saveKey('gccb'))); return { night: r.night, neon: r.neon }; }));
  await open();            // the app comes back as a fresh page
  await p.evaluate(() => { settings.name = 'T'; $('title').classList.remove('on'); resumeRound('gccb'); });
  await p.waitForFunction(() => G.state === 'address' || G.state === 'intro', null, { timeout: 300000 }); await p.waitForTimeout(3500); console.log('resumed  ', await look());
  await p.evaluate(() => { startRound(); }); await p.waitForTimeout(5000); console.log('new round', await look());
  await b.close();
})();
