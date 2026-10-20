const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 }, hasTouch: true, isMobile: true, deviceScaleFactor: 2 })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.stack.split('\n').slice(0, 3).join(' | ')));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => loadData('stpatricks').then(() => setCourse('stpatricks')));
  await p.evaluate(() => { $('title').classList.remove('on'); G.weather = WEATHERS[0]; G.wxNext = WEATHERS[0]; G.wxLeft = 9; startRound(); startHole(1); beginHole(); });
  await p.waitForFunction(() => G.state === 'address', null, { timeout: 400000 }); await p.waitForTimeout(800);
  await p.evaluate(() => {
    const orig = simulateShot; window.simulateShot = (C, o) => { const r = orig(C, o); r.lost = true; return r; };
    G.club = 0; const now = performance.now(); Object.assign(SW, { phase: 'swing', t0: now - 900, tTop: now - 450, pMax: .85, thumb: true, tx: 300, ty: 600, sid: 5 }); impact(now);
  });
  await p.waitForFunction(() => G.state === 'search', null, { timeout: 600000 }); await p.waitForTimeout(2500);
  console.log(await p.evaluate(() => {
    const out = [];
    for (const [x, y] of [[231, 544], [263, 620], [200, 360]]) out.push([x, y, document.elementsFromPoint(x, y).slice(0, 6).map(e => e.tagName + (e.id ? '#' + e.id : '') + (e.className && e.className.baseVal === undefined ? '.' + String(e.className).split(' ').join('.') : ''))]);
    const vis = [...document.querySelectorAll('body *')].filter(e => { const r = e.getBoundingClientRect(), cs = getComputedStyle(e); return r.width > 20 && r.height > 20 && cs.visibility !== 'hidden' && cs.display !== 'none' && +cs.opacity > .05 && r.bottom > 0 && r.top < 720 && !['HTML', 'BODY'].includes(e.tagName) && (e.id || '').match(/./) && ['gl'].indexOf(e.id) < 0; }).map(e => e.id + ':' + Math.round(+getComputedStyle(e).opacity * 100) + '%');
    return JSON.stringify({ out, vis });
  }));
  await p.screenshot({ path: '/tmp/stpat/shots/searchui.png' });
  await b.close();
})();
