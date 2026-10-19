const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => { DL.players = { z1: { n: 'Flo', pf: { xp: 500, r: 3, h: 54 }, on: ['Flo', 'Florian <b>'] } }; DL.playersAt = Date.now() + 1e9; openPlayer({ name: 'Flo', id: 'z1' }); });
  await p.waitForTimeout(900);
  console.log(await p.evaluate(() => { const el = $('playerBody'), subs = [...el.querySelectorAll('.sub span')].map(x => x.textContent); const i = subs.indexOf('Other usernames used in the past'); const rows = [...el.querySelectorAll('.stRow span:first-child')].map(x => x.textContent).slice(-2); el.scrollIntoView(false); $('playerSheet').scrollTop = 1e5; return JSON.stringify({ subs, i, rows, bold: el.querySelectorAll('b').length }); }));
  await p.waitForTimeout(600); await p.screenshot({ path: '/tmp/stpat/shots/oldnames.png' });
  await p.evaluate(() => { closeSheets(); settings.oldNames = ['Tom']; openPlayer({ name: 'Me', me: true }); }); await p.waitForTimeout(600);
  console.log(await p.evaluate(() => [...$('playerBody').querySelectorAll('.sub span')].map(x => x.textContent).slice(-2).join(' / ')));
  await b.close();
})();
