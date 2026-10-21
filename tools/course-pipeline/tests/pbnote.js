// Pebble Beach: the "being built" note shows when a round starts and goes away on a tap; practice shows it once per session
const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.stack.split('\n').slice(0, 3).join(' | ')));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: '/tmp/claude-0/-home-user-SweetSpot/42254a9d-b7ad-52d7-9d2e-d0f8e3c6d97d/scratchpad/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  const on = () => p.evaluate(() => $('pbNote').classList.contains('on'));
  await p.evaluate(() => loadData('mountainvalley').then(() => setCourse('mountainvalley')));
  console.log('before round', await on());
  await p.evaluate(() => { $('title').classList.remove('on'); startRound(); });
  await p.waitForTimeout(1500); console.log('round start', await on());
  await p.screenshot({ path: '/tmp/pbs/note.png' });
  await p.click('#pbNoteOk'); await p.waitForTimeout(600); console.log('after OK', await on());
  await p.evaluate(() => { startPractice(3); }); await p.waitForTimeout(500); console.log('practice 1st', await on());
  await p.click('#pbNoteOk'); await p.evaluate(() => { startPractice(4); }); await p.waitForTimeout(500); console.log('practice 2nd', await on());
  await p.evaluate(() => { loadData('gccb'); setCourse('gccb'); startRound(); }); await p.waitForTimeout(800); console.log('other course', await on());
  await b.close();
})();
