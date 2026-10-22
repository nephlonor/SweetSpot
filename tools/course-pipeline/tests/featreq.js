// feature requests: menu button, list sorted by votes, voting (optimistic, posted), archive tab, new request
const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await (await b.newContext({ viewport: { width: 405, height: 780 } })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  const posted = []; await p.route('https://api.github.com/**', r => { posted.push(JSON.parse(r.request().postData()).title); r.fulfill({ status: 201, contentType: 'application/json', body: '{}' }); });
  await p.route('**/leaderboard/features.json*', r => r.fulfill({ contentType: 'application/json', body: JSON.stringify([
    { id: 5, t: 'Night golf <i>', d: 'Floodlights on the range', n: 'ANNA', by: 'a1', at: 1760000000000, s: 'open', v: { a1: 1, b2: 1, c3: -1 } },
    { id: 6, t: 'More courses in Scotland', d: '', n: '', by: 'b2', at: 1761000000000, s: 'open', v: { b2: 1, c3: 1, d4: 1 } },
    { id: 2, t: 'Wind arrow', d: 'Show the wind', n: 'BEN', by: 'a1', at: 1750000000000, s: 'done', done: 1759000000000, v: { a1: 1 } }]) }));
  await p.addInitScript(() => { localStorage.setItem('ssg-intro-seen', '1'); });
  await p.route('**/three.min.js', r => r.fulfill({ path: process.env.THREE, contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => { settings.name = 'TEST'; saveSettings(); openSheet('menuSheet'); menuPage('home'); });
  await p.evaluate(() => document.querySelector('#menuSheet').scrollTop = 9999); await p.waitForTimeout(300);
  await p.screenshot({ path: '/tmp/pbs/fr_menu.png' });
  await p.click('.mli[data-go="feature"]'); await p.waitForTimeout(1200);
  console.log('order:', await p.evaluate(() => [...document.querySelectorAll('#frList .frC b')].map(e => e.textContent)));
  await p.screenshot({ path: '/tmp/pbs/fr_list.png' });
  await p.click('#frList button[data-id="5"][data-v="1"]'); await p.waitForTimeout(400);
  console.log('after up:', await p.evaluate(() => [...document.querySelectorAll('#frList .frV button')].map(e => e.textContent + (e.classList.contains('on') ? '*' : ''))));
  await p.click('#frList button[data-id="5"][data-v="1"]'); await p.waitForTimeout(400);
  console.log('toggled off:', await p.evaluate(() => [...document.querySelectorAll('#frList .frV button')].map(e => e.textContent + (e.classList.contains('on') ? '*' : ''))));
  await p.fill('#frT', 'Left-handed mode'); await p.fill('#frD', 'Mirror the swing'); await p.click('#frSend'); await p.waitForTimeout(600);
  console.log('sent list:', await p.evaluate(() => $('frList').innerText.slice(0, 120).replace(/\n/g, ' | ')), '\nposted:', posted);
  await p.click('.frTabs button[data-t="done"]'); await p.waitForTimeout(300);
  console.log('archive:', await p.evaluate(() => $('frList').innerText.replace(/\n/g, ' | '))); await p.screenshot({ path: '/tmp/pbs/fr_arch.png' });
  await b.close();
})();
