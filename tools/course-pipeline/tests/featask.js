// the feature-request pop-up: once, after the round's scorecard is closed; "See requests" opens the page; never again
const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: process.env.THREE, contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.route('**/leaderboard/features.json*', r => r.fulfill({ contentType: 'application/json', body: '[]' }));
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  const on = () => p.evaluate(() => $('featAsk').classList.contains('on'));
  await p.evaluate(() => { settings.name = 'TEST'; saveSettings(); G.scores = G.scores.map(() => 4); G.putts = G.putts.map(() => 2); showScorecard(true); }); await p.waitForTimeout(1200);
  console.log('while card open:', await on());
  await p.evaluate(() => $('scClose').click()); await p.waitForTimeout(1500);
  console.log('after close:', await on(), 'asked flag:', await p.evaluate(() => settings.featAsked)); await p.screenshot({ path: '/tmp/pbs/featask.png' });
  await p.click('#faOk'); await p.waitForTimeout(900);
  console.log('page open:', await p.evaluate(() => [$('featAsk').classList.contains('on'), !!document.querySelector('#menuSheet.on .mpg.on[data-pg="feature"]')]));
  await p.evaluate(() => { closeSheets(); showScorecard(true); }); await p.waitForTimeout(800); await p.evaluate(() => $('scClose').click()); await p.waitForTimeout(1500);
  console.log('second time:', await on()); await b.close();
})();
