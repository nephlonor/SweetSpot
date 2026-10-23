// GCC Basel night soundscape: renders a minute offline and measures the level per ten seconds, so it can be checked that it stays quiet and
// calm (the sound itself is not heard here)
const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: process.env.THREE, contentType: 'application/javascript' })); await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  console.log('cycle seconds', await p.evaluate(() => +(HW_TOTAL * HW_PER).toFixed(0)));
  for (const [name, s0] of [['scene 0', 0], ['scene 4', 96]]) {
    console.log(name, await p.evaluate(async ([st0]) => {
      const dur = 60, a = new OfflineAudioContext(2, 44100 * dur, 44100);
      hwSetup(a); MUS.ac = null; for (let st = st0; st < st0 + Math.ceil(dur / HW_PER); st++) hwStep(a, st, (st - st0) * HW_PER);
      const d = (await a.startRendering()).getChannelData(0), out = [];
      for (let w = 0; w + 441000 <= d.length; w += 441000) { let pk = 0, sq = 0; for (let i = w; i < w + 441000; i++) { const x = Math.abs(d[i]); if (x > pk) pk = x; sq += x * x; } out.push({ peak: +pk.toFixed(2), rms: +Math.sqrt(sq / 441000).toFixed(3) }); }
      return out;
    }, [s0]));
  }
  await b.close();
})();
