const { chromium } = require('/opt/node-tools/node_modules/playwright'); const fs = require('fs');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader'] });
  const p = await b.newPage(); p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  const pcm = await p.evaluate(async () => {
    const SEC = 80, a = new OfflineAudioContext(2, 44100 * SEC, 44100), bus = a.createGain(), out = a.createGain(); bus.connect(out); out.connect(a.destination);
    MUS.bus = bus; MUS.out = out; MUS.stops = []; MUS.breath = null; COURSE = COURSES.rothley; ambSetup(a, bus, out);
    const per = AMB.rothley.per; for (let st = 0; st * per < SEC - 4; st++) ambStep(a, 'rothley', st + 96 * 0, st * per + .2);
    const buf = await a.startRendering(); const L = buf.getChannelData(0), R = buf.getChannelData(1); let pk = 0;
    for (let i = 0; i < L.length; i++) pk = Math.max(pk, Math.abs(L[i]), Math.abs(R[i]));
    const g = .89 / pk, o = new Int16Array(L.length * 2); for (let i = 0; i < L.length; i++) { o[2 * i] = L[i] * g * 32767; o[2 * i + 1] = R[i] * g * 32767; }
    return { pk, d: Array.from(new Uint8Array(o.buffer)) };
  });
  console.log('peak', pcm.pk); fs.writeFileSync('/tmp/rothley/amb.raw', Buffer.from(pcm.d)); await b.close();
})();
