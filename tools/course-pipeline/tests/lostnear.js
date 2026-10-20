const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => loadData('stpatricks').then(() => setCourse('stpatricks')));
  await p.evaluate(() => { $('title').classList.remove('on'); G.weather = WEATHERS[0]; startRound(); startHole(1); beginHole(); });
  await p.waitForFunction(() => G.state === 'address', null, { timeout: 400000 });
  console.log(await p.evaluate(() => {
    const C = G.C; let n = 0, a = 0, b2 = 0, c2 = 0;
    for (let k = 0; k < 60000 && n < 200; k++) {
      const q = polyAt(C.center, Math.random() * C.center.L), t = Math.random() * 6.28, d = 1 + Math.random() * 40, x = q[0] + Math.cos(t) * d, z = q[1] + Math.sin(t) * d;
      if (!C.inBounds(x, z) || C.isOB(x, z) || C.surf(x, z) !== S.DEEP) continue; let nm = false; for (let dd = 1.5; dd <= 6 && !nm; dd += 1.5) for (let a2 = 0; a2 < 16 && !nm; a2++) { const sf = C.surf(x + Math.cos(a2 * .3927) * dd, z + Math.sin(a2 * .3927) * dd); if (sf === S.FAIR || sf === S.FIRST || sf === S.GREEN || sf === S.FRINGE) nm = true; } if (!nm) continue; n++;
      if (C.lost(x, z, 400)) a++; if (C.lost(x, z, 150)) b2++; if (C.lost(x, z, 200)) c2++;
    }
    return 'deep-rough points near the fairway: ' + n + '; lost when played from 400 m: ' + a + ', from 200 m: ' + c2 + ', from 150 m: ' + b2;
  }));
  await b.close();
})();
