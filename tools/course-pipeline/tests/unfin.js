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
    const t = dayId(), y = dayAdd(t, -1), cy = dailyCourse(y), ct = dailyCourse(t), par = COURSES[cy].defs.map(d => d.par), parT = COURSES[ct].defs.map(d => d.par);
    const ent = (n, c, pars, th, done) => ({ n, c, h: pars.map((v, i) => i < th ? v : 0), th, done, at: 1 });
    DL.rows[y] = new Map([['g1', ent('Grayson Brubak', cy, par, 7, false)], ['f1', ent('Fin Player', cy, par, 18, true)]]); DL.files[y] = [];
    DL.rows[t] = new Map([['g2', ent('Walker', ct, parT, 9, false)], ['f2', ent('Done Dan', ct, parT, 18, true)]]); DL.files[t] = [];
    dlSet({ day: t, course: ct, status: 'playing', startAt: Date.now(), h: parT.map((v, i) => i < 9 ? v : 0), tp: 0 }); window.__t = []; for (const [tab, d] of [['yesterday', y], ['today', t]]) { DL.tab = tab; fillDaily($('dailyBody')); window.__t.push(tab + ': ' + [...document.querySelectorAll('#dailyBody .lb .row')].map(r => r.querySelector('.nm').firstChild.textContent + (r.classList.contains('unfin') ? ' [grey]' : '')).join(', ')); }
    return window.__t.join(' || ');
  }));
  await b.close();
})();
