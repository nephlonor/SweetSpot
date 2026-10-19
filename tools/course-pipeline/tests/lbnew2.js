const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  const sh = () => p.evaluate(() => { const r = document.querySelector('#boardBody .row.lbNew'); return r ? getComputedStyle(r).boxShadow.slice(0, 30) + ' ' + r.getAnimations().map(a => Math.round(a.currentTime) + a.playState).join(',') : null; });
  const bells = () => p.evaluate(() => window.__bells);
  await p.evaluate(() => { window.__bells = 0; const o = SFX.bell; SFX.bell = () => { window.__bells++; o(); };
    const n = HOLE_DEFS.length, mk = (nm, d, at) => ({ name: nm, strokes: 72 + d, toPar: d, at, holes: n });
    localStorage.setItem(BOARD_KEY, JSON.stringify([mk('Anna', 2, 1e12)])); Board.tab = 'device'; openBoard(); });
  await p.waitForTimeout(500);
  // a score arrives while the board is closed
  await p.evaluate(() => { closeSheets(); const a = JSON.parse(localStorage.getItem(BOARD_KEY)); a.push({ name: 'Cleo', strokes: 70, toPar: -2, at: 1e12 + 5, holes: HOLE_DEFS.length }); localStorage.setItem(BOARD_KEY, JSON.stringify(a)); refreshBoards(); });
  await p.waitForTimeout(3000); console.log('closed 3 s, glow rows:', await p.evaluate(() => LBNEW.at.size), 'bells', await bells());
  await p.evaluate(() => openBoard()); await p.waitForTimeout(1000); console.log('open +1 s', await sh(), 'bells', await bells());
  await p.waitForTimeout(2500); await p.evaluate(() => closeSheets()); console.log('closed at ~3.5 s', await sh());
  await p.waitForTimeout(6000); console.log('closed 6 s later', await sh());
  await p.evaluate(() => openBoard()); await p.waitForTimeout(500); console.log('reopened +0.5', await sh(), 'bells', await bells());
  await p.waitForTimeout(4000); console.log('+4.5 total ~8', await sh());
  await p.waitForTimeout(1500); await p.evaluate(() => refreshBoards()); console.log('after', await sh(), await p.evaluate(() => LBNEW.at.size));
  await b.close();
})();
