const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  console.log(await p.evaluate(() => {
    const m = (n, d, by, at) => ({ name: n, strokes: 72 + d, toPar: d, at, holes: 18, by });
    Board.gh.gccb = [m('Florian', 3, 'f', 1), m('Florian', 5, 'f', 2), m('Florian', 3, 'f', 3), m('ULRICH', 0, 'u1', 4), m('ulrich', 2, 'u2', 5), m('TYWO', 1, 't', 6), m('TYLER WOOD', 4, 't', 7), m('Zain', 9, 'z', 8)];
    Board.tab = 'world'; Board.view = 'gccb'; openBoard(); Board.ghAt.gccb = Date.now();
    return [...document.querySelectorAll('#boardBody .lb .row')].map(r => r.querySelector('.nm').firstChild.textContent + ' ' + r.querySelector('.tp').textContent).join(' | ');
  }));
  await b.close();
})();
