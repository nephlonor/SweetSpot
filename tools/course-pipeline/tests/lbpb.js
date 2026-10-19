const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  const st = () => p.evaluate(() => ({ gold: [...document.querySelectorAll('#boardBody .row.lbNew .nm')].map(n => n.firstChild.textContent), blue: [...document.querySelectorAll('#boardBody .row.lbPb .nm')].map(n => n.firstChild.textContent), bells: window.__bells }));
  await p.evaluate(() => { window.__bells = []; const o = SFX.bell; SFX.bell = s => { window.__bells.push(s ? 'soft' : 'full'); o(s); };
    const m = (n, d, at) => ({ name: n, strokes: 72 + d, toPar: d, at, holes: 18, by: n });
    Board.gh.gccb = [m('Anna', 0, 1), m('Tom', 4, 2)]; Board.ghAt.gccb = Date.now(); settings.name = 'Tom'; Board.tab = 'world'; Board.view = 'gccb';
    localStorage.setItem(BOARD_KEY, '[]'); openBoard(); });
  await p.waitForTimeout(400); console.log('baseline', JSON.stringify(await st()));
  await p.evaluate(() => closeSheets());
  // 1) Tom plays +9: worse than his +4
  await p.evaluate(() => { submitRound({ name: 'Tom', strokes: 81, toPar: 9, at: Date.now(), holes: 18 }); closeSheets(); openBoard(); }); await p.waitForTimeout(600);
  console.log('worse round', JSON.stringify(await st()));
  await p.waitForTimeout(3300); await p.evaluate(() => refreshBoards()); console.log('after 3 s', JSON.stringify(await st()));
  // 2) Tom improves to +1
  await p.evaluate(() => { closeSheets(); submitRound({ name: 'Tom', strokes: 73, toPar: 1, at: 99, holes: 18 }); Board.gh.gccb = [{ name: 'Anna', strokes: 72, toPar: 0, at: 1, holes: 18, by: 'Anna' }, { name: 'Tom', strokes: 73, toPar: 1, at: 99, holes: 18, by: 'Tom' }]; LBNEW.bell = 0; openBoard(); }); await p.waitForTimeout(600);
  console.log('improved', JSON.stringify(await st()));
  await b.close();
})();
