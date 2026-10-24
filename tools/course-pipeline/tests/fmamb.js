// Four Mile Ranch's soundscape: set up the bus and run 1500 steps (more than eleven cycles) through ambStep; any exception fails
const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.stack.split('\n').slice(0, 3).join(' | ')));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: '/tmp/claude-0/-home-user-SweetSpot/42254a9d-b7ad-52d7-9d2e-d0f8e3c6d97d/scratchpad/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => loadData('fourmile').then(() => setCourse('fourmile')));
  const r = await p.evaluate(async () => {
    const a = new AudioContext(); await a.resume(); AC = a; musSetup(a);
    let err = null, n = 0;
    try { for (let st = 0; st < 1500; st++) { ambStep(a, 'fourmile', st, a.currentTime + st * .02); n++; } } catch (e) { err = String(e.stack || e).slice(0, 300); }
    return { kind: MUS.kind, state: a.state, n, err, musicWanted: musicWanted() };
  });
  console.log(JSON.stringify(r)); await b.close();
})();
