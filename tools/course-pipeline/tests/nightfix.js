// GCC Basel night: flowers hidden, black buttons, every green lit, and the Halloween waltz schedules without errors
const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: process.env.THREE, contentType: 'application/javascript' })); await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => { settings.name = 'T'; settings.course = 'gccb'; $('title').classList.remove('on'); startHole(1); G.night = true; G.nightU = 1; G.neon = 0x2ef2ff; setNeon(0x2ef2ff); });
  await p.waitForTimeout(4000);
  console.log(await p.evaluate(() => ({ state: G.state, night: document.body.classList.contains('night'), flowers: W.life && W.life.hMesh ? W.life.hMesh.visible : 'n/a', btn: getComputedStyle(document.querySelector('#intro .btn')).backgroundImage.slice(0, 60), lights: W.flood.length, discs: W.flood.filter(o => o.geometry && o.geometry.index).length })));
  await p.screenshot({ path: '/tmp/pbs/nightfix-intro.png' });
  // the waltz: schedule 200 steps on a real audio context
  console.log(await p.evaluate(async () => { const a = new AudioContext(); await a.resume().catch(() => { }); hwSetup(a); try { for (let i = 0; i < 200; i++) hwStep(a, i, a.currentTime + i * .01); } catch (e) { return 'ERR ' + e.message; } return 'waltz ok, kind ' + MUS.kind + ' state ' + a.state; }));
  await b.close();
})();
