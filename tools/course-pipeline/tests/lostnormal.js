const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.stack.split('\n').slice(0, 4).join(' | ')));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  for (const [course, hole] of [['stpatricks', 2], ['gccb', 3], ['augusta', 4], ['rothley', 5]]) {
    await p.evaluate(c => loadData(c).then(() => setCourse(c)), course);
    await p.evaluate(h => { $('title').classList.remove('on'); G.weather = WEATHERS[0]; G.wxNext = WEATHERS[0]; G.wxLeft = 9; startRound(); startHole(h); beginHole(); }, hole);
    await p.waitForFunction(() => G.state === 'address', null, { timeout: 400000 }); await p.waitForTimeout(500);
    const lostFn = await p.evaluate(() => typeof G.C.lost);
    await p.evaluate(() => { G.club = 0; const now = performance.now(); Object.assign(SW, { phase: 'swing', t0: now - 900, tTop: now - 450, pMax: .85 }); impact(now); document.getElementById('skipBtn'); G.playT = 2.2; });
    await p.evaluate(() => skipShot());
    let s = ''; for (let i = 0; i < 60; i++) { await p.waitForTimeout(700); s = await p.evaluate(() => G.state); if (s === 'address' || s === 'search') break; }
    console.log(course, 'hole', hole, 'C.lost:', lostFn, '->', s, await p.evaluate(() => JSON.stringify({ lost: G.shot.res.lost, surf: SURF[G.surf].name, strokes: G.strokes })));
  }
  await b.close();
})();
