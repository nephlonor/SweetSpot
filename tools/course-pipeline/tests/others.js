const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  for (const c of ['gccb', 'alsace', 'augusta', 'rothley', 'stpatricks']) for (const h of [0, 8, 17]) {
    await p.evaluate(c => loadData(c).then(() => setCourse(c)), c); await p.evaluate(h => { $('title').classList.remove('on'); startHole(h); beginHole(); G.snapCam = true; }, h);
    await p.waitForFunction(() => G.state === 'address', null, { timeout: 400000 });
    console.log(c, h + 1, await p.evaluate(() => JSON.stringify({ surf: G.surf, cup: G.C.surf(G.C.cup.x, G.C.cup.z), trees: W.trees.length })));
  }
  console.log(await p.evaluate(() => ['2026-10-17', '2026-10-18', '2026-10-19', '2026-10-20', '2026-10-21', '2026-10-24', '2026-10-25'].map(d => d + ' ' + dailyCourse(d)).join(' | ')));
  console.log(await p.evaluate(() => { const r = mulberry32(5), n = { fine: 0, damp: 0, rain: 0, dry: 0 }; let w = drawWeather(r, 'stpatricks'); for (let i = 0; i < 200000; i++) { n[w.id]++; w = nextWeather(w.id, r, 'stpatricks'); } return JSON.stringify(n); }));
  await b.close();
})();
