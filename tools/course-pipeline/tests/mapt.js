const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message)); p.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') console.log('CON', m.text().slice(0, 160)); });
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  const c = process.argv[2] || 'rothley';
  await p.evaluate(c => loadData(c).then(() => setCourse(c)), c);
  await p.evaluate(() => { $('title').classList.remove('on'); });
  for (let h = 0; h < 18; h++) {
    await p.evaluate(h => { startHole(h); beginHole(); G.snapCam = true; }, h);
    await p.waitForFunction(() => G.state === 'address', null, { timeout: 400000 }); await p.waitForTimeout(600);
    const r = await p.evaluate(() => new Promise(res => { const t0 = performance.now(); $('mapBtn').click(); setTimeout(() => {
      const P = G.C.plan, cv = $('mapCv'), on = $('mapSheet').classList.contains('on');
      let uni = null; if (P && P.top) { const d = P.top.getContext('2d').getImageData(0, 0, P.top.width, P.top.height).data; let mn = 1e9, mx = -1; for (let i = 0; i < d.length; i += 4 * 97) { const v = d[i] + d[i + 1] + d[i + 2]; mn = Math.min(mn, v); mx = Math.max(mx, v); } uni = mx - mn; }
      const r = { on, top: !!(P && P.top), size: P && P.top ? [P.top.width, P.top.height] : null, contrast: uni, cv: [cv.width, cv.height], skyVis: W.sky ? W.sky.visible : null };
      closeSheets(); res(r); }, 1500); }));
    console.log(h + 1, JSON.stringify(r));
  }
  await b.close();
})();
