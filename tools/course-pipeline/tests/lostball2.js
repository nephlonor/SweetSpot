const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 }, hasTouch: true, isMobile: true })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.stack.split('\n').slice(0, 4).join(' | ')));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => loadData('stpatricks').then(() => setCourse('stpatricks')));
  await p.evaluate(() => { $('title').classList.remove('on'); G.weather = WEATHERS[0]; G.wxNext = WEATHERS[0]; G.wxLeft = 9; startRound(); startHole(1); beginHole(); });
  await p.waitForFunction(() => G.state === 'address', null, { timeout: 400000 }); await p.waitForTimeout(800);
  await p.evaluate(() => {
    const orig = simulateShot; window.simulateShot = (C, o) => { const r = orig(C, o); r.lost = true; if (r.land) { r.final = { x: r.land.x + 3, y: C.h(r.land.x + 3, r.land.z + 2), z: r.land.z + 2 }; for (let i = 0; i < r.n; i++) if (r.frames[i * 5] > r.land.t + 1.2) { r.frames[i * 5 + 1] = r.final.x; r.frames[i * 5 + 3] = r.final.z; r.frames[i * 5 + 2] = r.final.y; r.frames[i * 5 + 4] = 1; } r.finalSurf = S.DEEP; } return r; };
    G.club = 0; const now = performance.now(); Object.assign(SW, { phase: 'swing', t0: now - 900, tTop: now - 450, pMax: .85 }); impact(now);
  });
  const st = () => p.evaluate(() => JSON.stringify({ state: G.state, vis: W.ball.visible, op: +W.ball.material.opacity.toFixed(2), pt: +G.playT.toFixed(2), fz: !!(G.shot && G.shot.camFreeze), ta: G.shot && G.shot.tApex && +G.shot.tApex.toFixed(2), tl: G.shot && G.shot.tLand && +G.shot.tLand.toFixed(2), tracer: W.tracer.visible }));
  await p.evaluate(() => { window.__cs = []; let last = null; const f = () => { if (G.shot && G.state === 'flight') { const c = W.cam.position, t = G.playT; if (last && t > last.t) window.__cs.push([+t.toFixed(2), +(c.distanceTo(last.c) / (t - last.t)).toFixed(1)]); last = { c: c.clone(), t }; } requestAnimationFrame(f); }; f(); });
  for (let i = 0; i < 400; i++) { await p.waitForTimeout(800); const s = JSON.parse(await st()); if (i % 6 === 0) console.log(JSON.stringify(s)); if (s.state === 'search') break; }
  console.log('cam speed (m/s) by playT:', await p.evaluate(() => JSON.stringify(window.__cs.filter((v, i) => i % 3 === 0).slice(0, 40))));
  await p.waitForTimeout(2800);
  // is the ball always inside the frame whatever the random offset? (re-roll the view centre many times, project the hidden ball)
  console.log(await p.evaluate(() => {
    const r = G.search.r, C = G.C; let bad = 0, N = 300; const v = new THREE.Vector3();
    for (let i = 0; i < N; i++) {
      const ox = (Math.random() * 2 - 1) * 13, oz = (Math.random() * 2 - 1) * 5, S2 = G.search, P = r.land, ux = S2.dx, uz = S2.dz, cx = P.x + ux * ox - uz * oz, cz = P.z + uz * ox + ux * oz, h = C.h(cx, cz);
      const cam = W.cam.clone(); cam.position.set(cx - ux * 7, h + 50, cz - uz * 7); cam.lookAt(cx, h, cz); cam.updateMatrixWorld(true); cam.updateProjectionMatrix();
      v.set(r.final.x, C.h(r.final.x, r.final.z), r.final.z).project(cam); if (Math.abs(v.x) > .92 || v.y > .72 || v.y < -.55) bad++;
    }
    return 'ball outside the safe part of the frame in ' + bad + ' of ' + N + ' random views; fov ' + W.cam.fov + ', grass meshes ' + G.search.grass.map(m => m.count).join('+');
  }));
  await p.screenshot({ path: '/tmp/stpat/shots/search2.png' });
  const pt = await p.evaluate(() => { const r = G.search.r, v = new THREE.Vector3(r.final.x + .8, G.C.h(r.final.x, r.final.z), r.final.z).project(W.cam), rc = $('gl').getBoundingClientRect(); return [(v.x + 1) / 2 * rc.width + rc.left, (1 - v.y) / 2 * rc.height + rc.top]; });
  await p.mouse.click(pt[0], pt[1]); await p.waitForTimeout(900);
  console.log('after tap', await st(), await p.evaluate(() => JSON.stringify({ grass: !!(G.search && G.search.grass), marks: (W.sMarks || []).filter(m => m.visible).length })));
  await p.waitForTimeout(3500); console.log('later', await p.evaluate(() => JSON.stringify({ state: G.state, scene: W.scene.children.filter(o => o.isInstancedMesh).length })));
  await b.close();
})();
