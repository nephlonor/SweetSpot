// the leaderboard swipe: a board arriving (refreshBoards) while the wheel turns must not cut the turn short; quick successive swipes move on by one each
const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 }, hasTouch: true })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: process.env.THREE, contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort()); await p.route('**/raw.githubusercontent.com/**', async r => { await new Promise(x => setTimeout(x, 120)); r.fulfill({ status: 200, contentType: 'application/json', body: '[]' }); });
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => openBoard()); await p.waitForTimeout(1200);
  const swipe = (dx, refreshAt) => p.evaluate(([dx, refreshAt]) => new Promise(res => {
    const bb = document.getElementById('boardBody'), q = bb.getBoundingClientRect(), x = q.left + q.width / 2, y = q.top + 150;
    const mk = (type, X) => { const t = new Touch({ identifier: 1, target: bb, clientX: X, clientY: y }); bb.dispatchEvent(new TouchEvent(type, { touches: type === 'touchend' ? [] : [t], changedTouches: [t], bubbles: true })); };
    mk('touchstart', x); mk('touchend', x + dx);
    if (refreshAt != null) setTimeout(() => refreshBoards(), refreshAt);
    setTimeout(res, 700);
  }), [dx, refreshAt]);
  const view = () => p.evaluate(() => Board.view + ' / ' + $('boardName').textContent);
  console.log('start', await view());
  await swipe(-120, 80); console.log('swipe left, board refresh at 80 ms:', await view());
  await swipe(-120, 120); console.log('swipe left again, refresh at 120 ms:', await view());
  await swipe(120, 40); console.log('swipe right, refresh at 40 ms:', await view());
  await p.evaluate(() => { window.__v = []; }); 
  // two swipes in quick succession
  await p.evaluate(() => { const bb = document.getElementById('boardBody'), q = bb.getBoundingClientRect(), y = q.top + 150; const go = dx => { const x = q.left + q.width / 2, t0 = new Touch({ identifier: 1, target: bb, clientX: x, clientY: y }), t1 = new Touch({ identifier: 1, target: bb, clientX: x + dx, clientY: y }); bb.dispatchEvent(new TouchEvent('touchstart', { touches: [t0], changedTouches: [t0], bubbles: true })); bb.dispatchEvent(new TouchEvent('touchend', { touches: [], changedTouches: [t1], bubbles: true })); }; go(-120); setTimeout(() => go(-120), 100); });
  await p.waitForTimeout(900); console.log('two quick swipes left:', await view());
  await b.close();
})();
