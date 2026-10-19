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
  const [h, e, n, name] = [+process.argv[2], +process.argv[3], +process.argv[4], process.argv[5]];
  await p.evaluate(h => { $('title').classList.remove('on'); const sty = document.createElement('style'); sty.textContent = '#hud,#pinTag,#ballTag,#aimHint,.hint{opacity:0!important}'; document.head.appendChild(sty); G.weather = WEATHERS[1]; G.wxNext = WEATHERS[1]; G.wxLeft = 9; startHole(h); beginHole(); G.snapCam = true; }, h);
  await p.waitForFunction(() => G.state === 'address', null, { timeout: 400000 });
  console.log(await p.evaluate(([e, n]) => { const q = G.C.loc(e, n), x = q[0], z = -q[1]; placeBall(x, z, false); G.prev = { x, z }; autoClubAndAim(); updateAim(true); G.snapCam = true; return [x, z, G.C.surf(x, z), G.C.wl(x, z) > G.C.h(x, z)]; }, [e, n]));
  await p.waitForTimeout(3000); await p.evaluate(() => { G.snapCam = true; const j = groundJob(W.life, W.cam.position.x, W.cam.position.z); let r; do { r = j.next(); } while (!r.done); });
  await p.waitForTimeout(4000); await p.screenshot({ path: `/tmp/stpat/shots/${name}_a.png` }); await p.evaluate(() => { W.life.mMesh.visible = false; }); await p.waitForTimeout(800); await p.screenshot({ path: `/tmp/stpat/shots/${name}_b.png` }); await p.evaluate(() => { W.life.gMesh.visible = false; W.holeGroup.traverse(o => { if (o.isInstancedMesh) o.visible = false; }); }); await p.waitForTimeout(800); await p.screenshot({ path: `/tmp/stpat/shots/${name}_c.png` }); await p.evaluate(() => { W.holeGroup.traverse(o => { if (o.isMesh && !o.isInstancedMesh && o.material && o.material.customProgramCacheKey) o.visible = false; }); }); await p.waitForTimeout(800); await p.screenshot({ path: `/tmp/stpat/shots/${name}_d.png` });
  await b.close();
})();
