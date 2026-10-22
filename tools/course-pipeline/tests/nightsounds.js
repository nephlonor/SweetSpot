// GCC Basel night sounds: every owl call, the barn owl's screech and the howls schedule without errors (the sound itself is not heard here)
const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: process.env.THREE, contentType: 'application/javascript' })); await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  console.log(await p.evaluate(async () => {
    settings.sound = true; const a = audio(); if (a && a.resume) await a.resume().catch(() => { });
    const out = { calls: OWL_CALLS.length, notes: OWL_CALLS.map(c => c().length), state: a && a.state };
    try { for (let k = 0; k < 40; k++) owlHoot(); for (let k = 0; k < 12; k++) howl(); for (const c of OWL_CALLS) owlNotes(c(), .2, 1, 0); out.ok = true; } catch (e) { out.err = e.message; }
    return out;
  }));
  await b.close();
})();
