// Pebble Beach: a ball that ends on the beach/cliffs outside the boundary is a penalty area (res.water + shore); a ball inland beyond the fence stays out of bounds
const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: process.env.THREE, contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => loadData('pebblebeach').then(() => setCourse('pebblebeach')));
  await p.evaluate(() => { $('title').classList.remove('on'); startHole(17); beginHole(); });
  await p.waitForFunction(() => G.state === 'address', null, { timeout: 400000 });
  console.log(await p.evaluate(() => {
    const C = G.C; let shore = 0, inland = 0, ex = null, exi = null;
    for (let k = 0; k < 40000 && (shore < 40 || inland < 40); k++) {
      const x = C.startPos.x + (Math.random() - .5) * 700, z = C.startPos.z + (Math.random() - .5) * 700;
      if (!C.inBounds(x, z) || !C.isOB(x, z) || C.surf(x, z) === S.WATER) continue;
      if (nearSea(C, x, z)) { shore++; ex = ex || [x, z]; } else { inland++; exi = exi || [x, z]; }
    }
    // real shots from the tee in every direction and at several powers: how they end
    const cnt = { sea: 0, shore: 0, ob: 0, ok: 0 }; let exS = null, exO = null;
    for (let k = 0; k < 400; k++) {
      const ang = Math.random() * 6.283, el = .25 + Math.random() * .5, v = 25 + Math.random() * 45, vh = v * Math.cos(el);
      const r = simulateShot(C, { x: G.ball.x, y: G.ball.y, z: G.ball.z, v: [Math.cos(ang) * vh, v * Math.sin(el), Math.sin(ang) * vh], w: [0, 0, 0], wind: null, putt: false, flag: true });
      if (r.shore) { cnt.shore++; exS = exS || ['final ' + [r.final.x, r.final.z].map(q => q.toFixed(0)), 'lastDry ' + r.lastDry.map(q => q.toFixed(0)), 'lastDry OB ' + C.isOB(r.lastDry[0], r.lastDry[1])].join(' '); }
      else if (r.water) cnt.sea++; else if (r.ob) { cnt.ob++; exO = exO || [r.final.x, r.final.z].map(q => q.toFixed(0)).join(','); } else cnt.ok++;
    }
    const out = ['outcomes ' + JSON.stringify(cnt), 'shore example: ' + exS, 'ob example final: ' + exO];
    return 'shore points ' + shore + ', inland OB points ' + inland + '\n' + out.join('\n');
  }));
  await b.close();
})();
