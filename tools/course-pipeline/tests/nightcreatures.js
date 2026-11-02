// GCC Basel night: floodlight masts light the hole, an owl hoots, a birdie rains sparkles that pop (no confetti); screenshots go to /tmp/pbs
const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: process.env.THREE, contentType: 'application/javascript' })); await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => { settings.name = 'T'; settings.course = 'gccb'; $('title').classList.remove('on'); startHole(1); beginHole(); });
  await p.waitForFunction(() => G.state === 'address', null, { timeout: 300000 }); await p.waitForTimeout(500);
  await p.evaluate(() => { G.night = true; G.neon = 0x2ef2ff; setNeon(0x2ef2ff); $('neonAsk').classList.remove('on'); });
  await p.waitForFunction(() => G.nightU > .95, null, { timeout: 120000 }); await p.waitForTimeout(2500);
  console.log('flood', await p.evaluate(() => ({ masts: W.flood.n, lit: W.flood.lights.filter(l => l.intensity > 0).length })));
  await p.screenshot({ path: '/tmp/pbs/night-flood.png' });
  console.log('owl', await p.evaluate(() => { try { owlHoot(); return 'ok'; } catch (e) { return 'ERR ' + e.message; } }));
  await p.evaluate(() => burstSparkles()); await p.waitForTimeout(1200);
  console.log('sparkles', await p.evaluate(() => { const cv = $('sparkles'); if (!cv) return 'none'; const d = cv.getContext('2d').getImageData(0, 0, cv.width, cv.height).data; let n = 0; for (let i = 3; i < d.length; i += 4) if (d[i] > 20) n++; return { canvas: true, litPixels: n, confettiDom: $('confetti').children.length }; }));
  await p.screenshot({ path: '/tmp/pbs/night-sparkles.png' });
  await p.waitForTimeout(6500); console.log('sparkles gone', await p.evaluate(() => !$('sparkles')));
  await b.close();
})();
