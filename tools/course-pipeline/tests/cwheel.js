// the leaderboard's horizontal course wheel: a drag with speed keeps spinning after the finger lifts, slows down and selects the name it stops on; a tap rolls to a name
const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 }, hasTouch: true })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: process.env.THREE, contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => openBoard()); await p.waitForTimeout(1200);
  const st = () => p.evaluate(() => JSON.stringify({ sel: [...document.querySelectorAll('.cwi')].filter(d => d.getAttribute('aria-selected') === 'true').map(d => d.textContent), name: $('boardName').textContent, sheetH: Math.round($('boardSheet').getBoundingClientRect().height) }));
  console.log('open', await st()); await p.screenshot({ path: '/tmp/pbs/hwheel0.png' });
  const r = await p.evaluate(() => { const q = document.querySelector('.cwrap').getBoundingClientRect(); return [q.left, q.top + q.height / 2, q.width]; });
  // a quick flick to the left: the finger moves 90 px in about 80 ms, then lifts
  await p.mouse.move(r[0] + r[2] * .7, r[1]); await p.mouse.down();
  for (let i = 1; i <= 6; i++) { await p.mouse.move(r[0] + r[2] * .7 - i * 15, r[1]); await p.waitForTimeout(13); }
  await p.mouse.up();
  const seen = []; for (let i = 0; i < 12; i++) { await p.waitForTimeout(250); seen.push(await p.evaluate(() => [...document.querySelectorAll('.cwi')].map(d => +d.style.opacity > .9 ? d.textContent : null).filter(Boolean).join(',') || '-')); }
  console.log('after the flick, every 250 ms:', seen.join(' | ')); await p.waitForTimeout(6000); console.log('settled', await st()); await p.screenshot({ path: '/tmp/pbs/hwheel1.png' });
  // a slow drag then lift after a pause: no momentum, comes to rest on the nearest name
  await p.mouse.move(r[0] + r[2] * .5, r[1]); await p.mouse.down(); await p.mouse.move(r[0] + r[2] * .5 + 100, r[1], { steps: 10 }); await p.waitForTimeout(400); await p.mouse.up(); await p.waitForTimeout(9000);
  console.log('after a slow drag back', await st());
  await b.close();
})();
