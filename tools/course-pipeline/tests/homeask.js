// the home-course pop-up: appears on the title screen after ten rounds (once), saves, shows in the menu and is filed; "Not now" leaves the menu fields
const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  const posted = []; await p.route('https://api.github.com/**', r => { posted.push(r.request().postData()); r.fulfill({ status: 201, contentType: 'application/json', body: '{}' }); });
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: process.env.THREE, contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  const on = () => p.evaluate(() => $('homeAsk').classList.contains('on'));
  await p.evaluate(() => { ST.rounds = 9; homeAskCheck(); }); console.log('9 rounds:', await on());
  await p.evaluate(() => { ST.rounds = 10; homeAskCheck(); }); await p.waitForTimeout(600); console.log('10 rounds:', await on()); await p.screenshot({ path: '/tmp/pbs/homeask.png' });
  await p.click('#haOk'); console.log('empty save keeps it open:', await on());
  await p.fill('#haC', 'Pine Hollow GC'); await p.fill('#haR', 'Ohio, USA'); await p.click('#haOk'); await p.waitForTimeout(600);
  console.log('after save: open', await on(), JSON.stringify(await p.evaluate(() => ({ c: settings.homeC, r: settings.homeR, asked: settings.homeAsked, sent: settings.homeSent || null }))));
  await p.evaluate(() => { openSheet('menuSheet'); menuPage('player'); syncMenu(); }); await p.waitForTimeout(500);
  console.log('menu fields:', await p.evaluate(() => [$('mHomeC').value, $('mHomeR').value]));
  await p.fill('#mHomeC', 'Mountain Valley'); await p.fill('#mHomeR', 'Pennsylvania'); await p.evaluate(() => $('mHomeR').dispatchEvent(new Event('change'))); await p.waitForTimeout(5000);
  console.log('after menu edit:', await p.evaluate(() => [settings.homeC, settings.homeR]), 'issues posted', posted.length);
  await p.evaluate(() => { settings.homeC = ''; settings.homeR = ''; settings.homeAsked = false; ST.rounds = 12; closeSheets(); $('title').classList.add('on'); homeAskCheck(); }); await p.waitForTimeout(400);
  await p.click('#haNo'); console.log('not now: open', await on(), 'asked again?', await p.evaluate(() => { homeAskCheck(); return $('homeAsk').classList.contains('on'); }));
  await b.close();
})();
