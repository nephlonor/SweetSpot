// GCC Basel night tune: ten minutes, 22 sections; renders slices offline and measures the level (peak and average) per ten seconds, so the
// loud climax can be checked for clipping (the sound itself is not heard here)
const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: process.env.THREE, contentType: 'application/javascript' })); await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  console.log(await p.evaluate(() => { hwCompose(); let n = 0; for (const l of HW_EV.values()) n += l.length; const kinds = {}; for (const l of HW_EV.values()) for (const e of l) kinds[e.k] = (kinds[e.k] || 0) + 1; return { seconds: +(HW_TOTAL * HW_PER).toFixed(1), sections: HW_SECS.length, events: n, kinds }; }));
  for (const [name, sec0] of [['intro', 0], ['climax', 16]]) {
    console.log(name, await p.evaluate(async ([s0]) => {
      const secLen = 96 * HW_PER, dur = secLen * 2, a = new OfflineAudioContext(2, Math.ceil(44100 * dur), 44100);
      hwSetup(a); MUS.ac = null; for (let st = s0 * 96; st < s0 * 96 + 192; st++) hwStep(a, st, (st - s0 * 96) * HW_PER);
      const buf = await a.startRendering(), d = buf.getChannelData(0), out = [];
      for (let w = 0; w + 441000 <= d.length; w += 441000) { let pk = 0, sq = 0; for (let i = w; i < w + 441000; i++) { const x = Math.abs(d[i]); if (x > pk) pk = x; sq += x * x; } out.push({ peak: +pk.toFixed(2), rms: +Math.sqrt(sq / 441000).toFixed(3) }); }
      return out;
    }, [sec0]));
  }
  await b.close();
})();
