const { open } = require('./lib'); const fs = require('fs');
(async () => {
  const { b, p } = await open();
  for (let i = 0; i < 60; i++) await p.evaluate(() => __frame(33.3, []));
  await p.evaluate(() => { settings.name = 'TRAILER'; $('title').classList.remove('on'); });
  await p.evaluate(c => loadData(c).then(() => setCourse(c)), 'pebblebeach');
  await p.evaluate(() => { G.weather = WEATHERS[0]; startHole(6); beginHole(); });
  let t0 = Date.now(); for (let i = 0; i < 400; i++) { await p.evaluate(() => __frame(33.3, [])); if (await p.evaluate(() => G.state === 'address')) { console.log('address after', i, 'frames'); break; } }
  console.log('wall', Date.now() - t0);
  t0 = Date.now(); for (let i = 0; i < 5; i++) { await p.evaluate(() => __frame(33.3, [])); await p.screenshot({ path: `/tmp/pbs/pr${i}.jpg`, type: 'jpeg', quality: 88 }); } console.log('5 frames+shots ms', Date.now() - t0);
  console.log(await p.evaluate(() => ({ st: G.state, club: G.club, yaw: G.yaw, tp: UI.trackPx, fc: [UI.faceCX, UI.faceCY] })));
  await b.close();
})();
