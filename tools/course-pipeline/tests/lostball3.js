const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.stack.split('\n').slice(0, 4).join(' | ')));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  const mode = process.argv[2] || 'found';
  await p.evaluate(() => loadData('stpatricks').then(() => setCourse('stpatricks')));
  await p.evaluate(() => { $('title').classList.remove('on'); G.weather = WEATHERS[0]; G.wxNext = WEATHERS[0]; G.wxLeft = 9; startRound(); startHole(1); beginHole(); });
  await p.waitForFunction(() => G.state === 'address', null, { timeout: 400000 }); await p.waitForTimeout(800);
  await p.evaluate(() => {
    const orig = simulateShot; window.simulateShot = (C, o) => { const r = orig(C, o); r.lost = true; if (r.land) { const f = r.final, k = r.n - 1; r.final = { x: r.land.x + 3, y: C.h(r.land.x + 3, r.land.z + 2), z: r.land.z + 2 }; for (let i = 0; i < r.n; i++) if (r.frames[i * 5] > r.land.t + 1.2) { r.frames[i * 5 + 1] = r.final.x; r.frames[i * 5 + 3] = r.final.z; r.frames[i * 5 + 2] = r.final.y; r.frames[i * 5 + 4] = 1; } r.finalSurf = S.DEEP; } return r; };
    G.club = 0; const now = performance.now(); Object.assign(SW, { phase: 'swing', t0: now - 900, tTop: now - 450, pMax: .85 }); impact(now);
  });
  const st = () => p.evaluate(() => JSON.stringify({ state: G.state, vis: W.ball.visible, op: +W.ball.material.opacity.toFixed(2), hint: $('searchHint').classList.contains('on'), strokes: G.strokes, sl: G.shot && G.shot.slow, pt: G.shot && +G.playT.toFixed(2), dur: G.shot && +G.shot.res.duration.toFixed(1), lostf: G.shot && G.shot.res.lost, ft: !!(G.shot && G.shot.fadeT) }));
  for (let i = 0; i < 240; i++) { await p.waitForTimeout(500); const s = JSON.parse(await st()); if (i % 8 === 0) console.log('t', i / 2, JSON.stringify(s)); if (s.state === 'search') break; }
  await p.waitForTimeout(2600); await p.screenshot({ path: '/tmp/stpat/shots/search.png' }); console.log('search', await st());
  const tapAt = async off => { const pt = await p.evaluate(o => { const r = G.search.r, v = new THREE.Vector3(r.final.x + o, G.C.h(r.final.x, r.final.z), r.final.z).project(W.cam), rc = $('gl').getBoundingClientRect(); return [(v.x + 1) / 2 * rc.width + rc.left, (1 - v.y) / 2 * rc.height + rc.top]; }, off); await p.mouse.click(pt[0], pt[1]); await p.waitForTimeout(900); };
  const info = () => p.evaluate(() => JSON.stringify({ state: G.state, tries: G.search && G.search.tries, hint: $('searchHint').classList.contains('on'), txt: $('searchHint').querySelector('span').textContent, marks: (W.sMarks || []).filter(m => m.visible).length, strokes: G.strokes, pens: G.pens[G.hole], lost: ST.lost }));
  const seq = process.argv[2] === 'found' ? [12, -12, 1] : [12, -12, 14];
  for (const o of seq) { await tapAt(o); console.log('tap', o, await info()); }
  await p.waitForTimeout(4500); console.log('later', await info());
  await b.close();
})();
