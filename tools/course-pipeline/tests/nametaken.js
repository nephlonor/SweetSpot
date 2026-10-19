const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(3500);
  await p.evaluate(() => { Board.gh.gccb = [{ name: 'Tom', strokes: 80, toPar: 8, at: 1, holes: 18, by: 'other1' }]; DL.players = { other2: { n: 'Zed' }, [dlMe()]: { n: 'Mine' } }; DL.playersAt = Date.now() + 1e9; _namesAt = Date.now(); });
  const hint = () => p.evaluate(() => { const h = $('nameHintT'); return h.hidden ? '(none)' : h.textContent; });
  await p.fill('#nameIn', 'tom'); console.log('tom ->', await hint());
  await p.fill('#nameIn', 'ZED'); console.log('ZED ->', await hint());
  await p.fill('#nameIn', 'Mine'); console.log('Mine ->', await hint());
  await p.fill('#nameIn', 'Fresh'); console.log('Fresh ->', await hint());
  await p.fill('#nameIn', 'Tom'); await p.screenshot({ path: '/tmp/stpat/shots/nametaken.png' });
  await p.evaluate(() => { openSheet('menuSheet'); menuPage('player'); }); await p.fill('#mName', 'zed'); console.log('menu zed ->', await p.evaluate(() => { const h = $('nameHintM'); return h.hidden ? '(none)' : h.textContent; }), '| name still', await p.evaluate(() => settings.name));
  await b.close();
})();
