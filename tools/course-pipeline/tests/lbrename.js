const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(3500);
  console.log(await p.evaluate(() => {
    const me = dlMe(), at = Date.now() - 1000, m = (n, d, a, by) => ({ name: n, strokes: 71 + d, toPar: d, at: a, holes: 18, by });
    // the world file still has the old name; the local round was already renamed to the new one
    Board.gh.rothley = [m('Florian', -10, at, me), m('Anna', 0, 1, 'a1')]; Board.ghAt.rothley = Date.now();
    settings.name = 'Florian 2'; localStorage.setItem(COURSES.rothley.board, JSON.stringify([{ name: 'Florian 2', strokes: 61, toPar: -10, at, holes: 18, posted: true }]));
    Board.tab = 'world'; Board.view = 'rothley'; COURSE.key === 'rothley' || setCourse('rothley'); openBoard();
    return [...document.querySelectorAll('#boardBody .lb .row')].map(r => r.querySelector('.nm').firstChild.textContent + ' ' + r.querySelector('.tp').textContent).join(' | ');
  }));
  await b.close();
})();
