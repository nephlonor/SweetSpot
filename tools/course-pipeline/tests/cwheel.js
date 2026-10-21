// the leaderboard's course wheel: shows, turns, switches the board; the sheet keeps its height with few scores
const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: process.env.THREE, contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => { openBoard(); }); await p.waitForTimeout(1200);
  const st = () => p.evaluate(() => { const w = document.querySelector('.cwheel'), sh = $('boardSheet').getBoundingClientRect(); return JSON.stringify({ items: document.querySelectorAll('.cwi').length, top: Math.round(w.scrollTop), sel: [...document.querySelectorAll('.cwi')].filter(d => d.getAttribute('aria-selected') === 'true').map(d => d.textContent), name: $('boardName').textContent, sheetH: Math.round(sh.height) }); });
  console.log('open', await st()); await p.screenshot({ path: '/tmp/pbs/wheel0.png' });
  await p.evaluate(() => document.querySelector('.cwheel').scrollTo({ top: 44 * 5, behavior: 'smooth' }));
  for (let i = 0; i < 8; i++) { await p.waitForTimeout(300); console.log('  t', i, await st()); }
  console.log('after turn to the 6th', await st()); await p.screenshot({ path: '/tmp/pbs/wheel1.png' });
  await p.evaluate(() => document.querySelectorAll('.cwi')[1].click()); await p.waitForTimeout(4000);
  console.log('after tap on the 2nd', await st());
  await b.close();
})();
