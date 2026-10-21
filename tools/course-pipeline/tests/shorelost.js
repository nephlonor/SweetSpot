const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.stack.split('\n').slice(0, 4).join(' | ')));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: process.env.THREE || (__dirname + '/three.min.js'), contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  const mode = process.argv[2] || 'found', pick = process.argv[3] || 'play';
  await p.evaluate(() => loadData('pebblebeach').then(() => setCourse('pebblebeach')));
  await p.evaluate(() => { $('title').classList.remove('on'); G.weather = WEATHERS[0]; G.wxNext = WEATHERS[0]; G.wxLeft = 9; startRound(); startHole(17); beginHole(); });
  await p.waitForFunction(() => G.state === 'address', null, { timeout: 400000 }); await p.waitForTimeout(800);
  console.log('strokes before', await p.evaluate(() => {
    const orig = simulateShot; window.simulateShot = (C, o) => {
      if (!C.real || o.putt) return orig(C, o); if (window.__done) return window.__r;
      const sp = Math.hypot(o.v[0], o.v[2]);
      for (let a = 0; a < 360; a += 3) { const ang = Math.atan2(o.v[2], o.v[0]) + a * Math.PI / 180, v = [Math.cos(ang) * sp, o.v[1], Math.sin(ang) * sp], r = orig(C, Object.assign({}, o, { v })); if (r.shore) { window.__done = true; window.__r = r; return r; } }
      return orig(C, o);
    };
    G.club = 0; const now = performance.now(); Object.assign(SW, { phase: 'swing', t0: now - 900, tTop: now - 450, pMax: .85 }); impact(now); return G.strokes;
  }));
  const st = () => p.evaluate(() => JSON.stringify({ state: G.state, strokes: G.strokes, hint: $('searchHint').classList.contains('on'), relief: $('reliefSheet').classList.contains('on'), shore: !!(G.shot && G.shot.res.shore) }));
  for (let i = 0; i < 240; i++) { await p.waitForTimeout(500); const s = JSON.parse(await st()); if (i % 10 === 0) console.log('t', i / 2, JSON.stringify(s)); if (s.state === 'search') break; }
  await p.waitForTimeout(3800); console.log('search', await st());
  const pt = await p.evaluate(m => { const r = G.search.r, v = new THREE.Vector3(r.final.x + (m === 'found' ? 0.8 : 14), G.C.h(r.final.x, r.final.z), r.final.z).project(W.cam), rc = $('gl').getBoundingClientRect(); return [(v.x + 1) / 2 * rc.width + rc.left, (1 - v.y) / 2 * rc.height + rc.top]; }, mode);
  const taps = mode === 'found' ? 1 : 3;
  for (let k = 0; k < taps; k++) { await p.mouse.click(pt[0], pt[1]); await p.waitForTimeout(900); }
  await p.waitForTimeout(3500); console.log('after search', await st());
  console.log('options', await p.evaluate(() => [...document.querySelectorAll('#reliefBody .rt')].map(e => e.textContent).join(' | ') + ' // ' + $('reliefTitle').textContent + ' // ' + $('reliefText').textContent));
  await p.screenshot({ path: '/tmp/pbs/relief.png' });
  await p.evaluate(pk => { const i = pk === 'play' ? 0 : 1; document.querySelectorAll('#reliefBody .mli')[i].click(); }, pick);
  await p.waitForTimeout(1500);
  console.log('after choice', await st(), await p.evaluate(() => JSON.stringify({ ball: [G.ball.x, G.ball.z].map(v => +v.toFixed(1)), pens: G.pens[G.hole], ob: G.C.isOB(G.ball.x, G.ball.z) })));
  await b.close();
})();
