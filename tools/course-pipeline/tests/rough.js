const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => loadData('rothley').then(() => setCourse('rothley')));
  console.log(await p.evaluate(() => { let n = 0, N = 0; for (let s = 1; s < 400; s++) { const r = mulberry32(s); let w = drawWeather(r, 'rothley'); for (let k = 0; k < 6; k++) { const L = 6 + Math.floor(r() * 4); if (w.id === 'rain') n += L; N += L; w = nextWeather(w.id, r, 'rothley'); } } return 'rain share ' + (n / N).toFixed(3); }));
  await p.evaluate(() => { $('title').classList.remove('on'); const sty = document.createElement('style'); sty.textContent = '#hud,#pinTag,#ballTag,#aimHint,.hint{opacity:0!important}'; document.head.appendChild(sty); startHole(2); beginHole(); G.snapCam = true; });
  await p.waitForFunction(() => G.state === 'address', null, { timeout: 400000 });
  // into the rough: walk sideways off the fairway until the surface is deep rough
  const at = await p.evaluate(() => { const C = G.C; for (let s = 120; s < 260; s += 10) for (let o = 14; o < 40; o += 2) { const pt = polyAt(C.center, s), q = polyAt(C.center, s + 5), tx = q[0] - pt[0], tz = q[1] - pt[1], l = Math.hypot(tx, tz); const x = pt[0] - tz / l * o, z = pt[1] + tx / l * o; if (C.surf(x, z) === S.DEEP || C.surf(x, z) === S.ROUGH) { placeBall(x, z, false); G.prev = { x, z }; autoClubAndAim(); G.snapCam = true; return [s, o, C.surf(x, z)]; } } return null; });
  console.log('ball', at); await p.waitForTimeout(3000); console.log(await p.evaluate(() => { try { const j = groundJob(W.life, G.ball.x, G.ball.z); let r, n = 0; do { r = j.next(); n++; } while (!r.done && n < 100000); return 'ok ' + n + ' ' + W.life.gMesh.count; } catch (e) { return 'ERR ' + e.stack.split('\n').slice(0, 3).join(' | '); } })); console.log(await p.evaluate(() => JSON.stringify({ lite: PERF.lite, gfx: settings.gfx, life: !!W.life, gm: W.life && W.life.gMesh ? W.life.gMesh.count : -1, NG: W.life && W.life.NG, hm: W.life && W.life.hMesh ? W.life.hMesh.count : -1, vis: W.life && W.life.gMesh && W.life.gMesh.visible }))); await p.waitForTimeout(2500); await p.screenshot({ path: '/tmp/rothley/shots/rough.png' });
  await p.evaluate(() => { G.weather = WEATHERS[3]; setWeather(G.weather); G.wxK = 4; G.wxN = 8; }); await p.waitForTimeout(5000); await p.screenshot({ path: '/tmp/rothley/shots/rain.png' });
  await b.close();
})();
