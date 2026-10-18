const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => loadData('rothley').then(() => setCourse('rothley')));
  const [h, e, n, ang] = process.argv.slice(2).map(Number);
  await p.evaluate(h => { $('title').classList.remove('on'); startHole(h); beginHole(); }, h);
  await p.waitForFunction(() => G.state === 'address', null, { timeout: 400000 });
  console.log(await p.evaluate(([e, n, ang]) => {
    const C = G.C, a = ang * Math.PI / 180, px = -Math.sin(a), py = Math.cos(a), prof = [];   // across the water
    for (let k = -10; k <= 10; k++) { const q = C.loc(e + px * k, n + py * k), x = q[0], z = -q[1]; prof.push([k, +C.h(x, z).toFixed(2), +C.wl(x, z).toFixed(2), C.surf(x, z)]); }
    let wetTrees = 0; for (const t of GC.trees) { const q = C.loc(t.e, t.n), x = q[0], z = -q[1]; if (C.wl(x, z) > C.h(x, z) - .05 && Math.hypot(t.e - e, t.n - n) < 200) wetTrees++; }
    return JSON.stringify({ prof, wetTrees });
  }, [e, n, ang]));
  await b.close();
})();
