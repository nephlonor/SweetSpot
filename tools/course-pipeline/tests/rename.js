const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.route('**/index.html', async r => { const t = require('fs').readFileSync('/home/user/SweetSpot/index.html', 'utf8').replace('const ghKey = () => {', 'const ghKey = () => "k"; const ghKeyOld = () => {'); r.fulfill({ body: t, contentType: 'text/html' }); }); await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  console.log(await p.evaluate(async () => {
    const calls = []; window.fetch = async (u, o) => { calls.push(o && o.body ? JSON.parse(o.body).title + ' | ' + (JSON.parse(o.body).body.match(/```json\n([\s\S]*?)\n```/) || [])[1] : u); return { ok: true, json: async () => [] }; };
    settings.name = 'Tom'; settings.nameSent = 'Tom';
    localStorage.setItem(BOARD_KEY, JSON.stringify([{ name: 'Tom', strokes: 80, toPar: 8, at: Date.now(), holes: 18, posted: true }]));
    await renameSync(); const same = calls.length;                       // unchanged name: nothing sent
    settings.name = 'Tim'; await renameSync();                           // changed: one rename issue
    await renameSync();                                                  // again: nothing more
    delete settings.nameSent; settings.name = 'Tam'; await renameSync();  // no nameSent: falls back to the name on the last posted round (now Tim)
    return JSON.stringify({ same, calls, nameSent: settings.nameSent, local: localRounds().map(r => r.name) });
  }));
  await b.close();
})();
