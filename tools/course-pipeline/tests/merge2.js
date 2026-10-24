// Two devices, one name: the real workflow script (leaderboard.yml) runs on a temporary copy of leaderboard/ behind both browsers' GitHub requests.
// Needs: node, playwright, three.min.js (THREE=path). Prints each step; any PAGEERR is a failure.
const { chromium } = require('/opt/node-tools/node_modules/playwright'); const fs = require('fs'), crypto = require('crypto'), path = require('path');
const yml = fs.readFileSync(path.join(__dirname, '../../../.github/workflows/leaderboard.yml'), 'utf8');
const AF = Object.getPrototypeOf(async function () { }).constructor;
const W = '/tmp/mg2/work'; fs.rmSync('/tmp/mg2', { recursive: true, force: true }); fs.mkdirSync(W + '/leaderboard', { recursive: true }); fs.mkdirSync(W + '/.github/scripts', { recursive: true });
fs.copyFileSync(path.join(__dirname, '../../../.github/scripts/daily-overall.js'), W + '/.github/scripts/daily-overall.js');
// the workflow's script text: the github-script step of the 'record' job
const scr = require('child_process').execFileSync('python3', ['-c', "import yaml,sys;print(yaml.safe_load(open(sys.argv[1]))['jobs']['record']['steps'][1]['with']['script'])", path.join(__dirname, '../../../.github/workflows/leaderboard.yml')]).toString();
let n = 0, log = [];
async function workflow(title, body) {
  const out = []; process.chdir(W); process.env.GITHUB_WORKSPACE = W;
  const github = { rest: { issues: { createComment: async o => out.push(o.body), update: async () => { } } } };
  const context = { repo: { owner: 'o', repo: 'r' }, payload: { issue: { number: ++n, title, body, user: { login: 'u' } } } };
  const exec = { exec: async () => 0, getExecOutput: async () => ({ stdout: '' }) };
  await new AF('github', 'context', 'core', 'exec', 'require', scr)(github, context, { warning: () => { } }, exec, require);
  log.push(title.slice(0, 30) + ' -> ' + out.join('|')); return out.join('|');
}
async function device(b, name) {
  const p = await (await b.newContext({ viewport: { width: 405, height: 720 } })).newPage();
  p.on('pageerror', e => console.log(name, 'PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: process.env.THREE || (__dirname + '/three.min.js'), contentType: 'application/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.abort());
  await p.route('**/api.github.com/repos/**/issues', async r => { const j = JSON.parse(r.request().postData()); await workflow(j.title, j.body); r.fulfill({ status: 201, contentType: 'application/json', body: '{}' }); });
  await p.route('**/raw.githubusercontent.com/**', r => { const f = r.request().url().split('/leaderboard/')[1].split('?')[0]; const fp = W + '/leaderboard/' + f; if (fs.existsSync(fp)) r.fulfill({ status: 200, contentType: 'application/json', body: fs.readFileSync(fp) }); else r.fulfill({ status: 404, body: '' }); });
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2500); p.devname = name; return p;
}
const sha = d => crypto.createHash('sha1').update(String(d).toLowerCase()).digest('hex').slice(0, 8);
const stats = p => p.evaluate(() => ({ name: settings.name, rounds: ST.rounds, xp: ST.xp, drive: ST.rec.drive.v, mgP: settings.mgP || null, own: profileCompact(true).r, dlg: MG.dlg && MG.dlg.kind }));
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  let A = await device(b, 'A'), B = await device(b, 'B');
  // device A: the established player Zoe, 5 rounds; device B: new, 1 round
  const setup = (p, nm, r, xp, dr) => p.evaluate(([nm, r, xp, dr]) => { settings.name = nm; settings.nameSent = nm; saveSettings(); ST.rounds = r; ST.xp = xp; ST.rec.drive.v = dr; saveStats(); }, [nm, r, xp, dr]);
  await setup(A, 'Zoe', 5, 900, 250); const hA = await A.evaluate(() => dlMe()), pfA = await A.evaluate(() => profileCompact(true));
  fs.writeFileSync(W + '/leaderboard/players.json', JSON.stringify({ [hA]: { n: 'Zoe', pf: pfA, at: Date.now() } }));
  await setup(B, 'Max', 1, 100, 180);
  // the rest of each account: scorecard history, best scores, trophies, holes in one shot, rain holes, a finished daily
  const rich = (p, rounds, hs, rh, trophy, daily) => p.evaluate(([rounds, hs, rh, trophy, daily]) => {
    localStorage.setItem(COURSES.gccb.board, JSON.stringify(rounds)); localStorage.setItem(COURSES.gccb.best, String(Math.min(...rounds.map(r => r.strokes))));
    ST.holedShots = hs; ST.rainHoles = rh; ST.trophies = trophy ? [trophy] : []; saveStats();
    if (daily) { const a = {}; a[daily.day] = daily; localStorage.setItem('ssg-daily', JSON.stringify(a)); }
  }, [rounds, hs, rh, trophy, daily]);
  const rd = (nm, st, at) => ({ name: nm, strokes: st, toPar: st - 72, holes: 18, at, v: 1, h: Array(18).fill(st / 18 | 0).map((v, i) => i < st - 18 * (st / 18 | 0) ? v + 1 : v), pt: Array(18).fill(2) });
  await rich(A, [rd('Zoe', 80, 1790000000000), rd('Zoe', 85, 1790100000000)], 2, 3, { day: '2026-10-20', course: 'gccb', tp: -2, s: 70, n: 5 }, { day: '2026-10-22', course: 'gccb', status: 'done', h: Array(18).fill(4), tp: 0, strokes: 72, at: 1790200000000 });
  await rich(B, [rd('Max', 90, 1790300000000)], 1, 4, null, null);
  // B types the name Zoe
  await B.evaluate(() => { $('title').classList.add('on'); $('nameIn').focus(); }); await B.fill('#nameIn', 'zoe'); await B.evaluate(() => $('nameIn').blur()); await B.waitForTimeout(4000);
  console.log('B after typing zoe:', JSON.stringify(await stats(B)));
  await B.screenshot({ path: '/tmp/mg2/b_ask.png' });
  await B.click('#mgOk'); await B.waitForTimeout(1500);
  console.log('B after Merge:', JSON.stringify(await stats(B)), await B.evaluate(() => $('mgT').textContent));
  console.log(log.join('\n')); console.log('merges.json:', fs.existsSync(W + '/leaderboard/merges.json') ? fs.readFileSync(W + '/leaderboard/merges.json', 'utf8').replace(/\d{12,}/g, 'T') : '(none)');
  // A launches again (same storage): the request is shown, and A accepts it
  const launch = async p => { await p.reload(); await p.waitForTimeout(2500); await p.evaluate(() => { $('title').classList.add('on'); }); await p.waitForTimeout(5500); };
  await launch(A); console.log('A at launch:', JSON.stringify(await stats(A)), await A.evaluate(() => $('mgB').textContent.slice(0, 60)));
  await A.screenshot({ path: '/tmp/mg2/a_accept.png' });
  await A.click('#mgOk'); await A.waitForTimeout(1200);
  console.log('A after Merge (waiting for the workflow result):', JSON.stringify(await stats(A)));
  await A.evaluate(() => mgCheck()); await A.waitForTimeout(1500);
  console.log('A after check:', JSON.stringify(await stats(A)), await A.evaluate(() => $('mgT').textContent));
  await A.screenshot({ path: '/tmp/mg2/a_done.png' });
  console.log('merges.json:', fs.readFileSync(W + '/leaderboard/merges.json', 'utf8').replace(/\d{12,}/g, 'T'));
  // B's next check: merged, takes A's name and A's share
  await B.evaluate(() => mgCheck()); await B.waitForTimeout(1500);
  console.log('B after check:', JSON.stringify(await stats(B)), await B.evaluate(() => $('nameIn').value));
  // A plays on: 2 more rounds; B takes the change over after A's sync and B's next check
  await A.evaluate(() => { ST.rounds += 2; ST.xp += 60; ST.rec.drive.v = 300; saveStats(); mgSyncSend(true); }); await A.waitForTimeout(1200);
  await B.evaluate(() => mgCheck()); await B.waitForTimeout(1500);
  console.log('after A plays 2 more -> A:', JSON.stringify(await stats(A)), ' B:', JSON.stringify(await stats(B)));
  // B renames: A follows at its next launch
  await B.evaluate(() => { openSheet('menuSheet'); menuPage('player'); }); await B.fill('#mName', 'Zoey'); await B.evaluate(() => $('mName').dispatchEvent(new Event('change'))); await B.waitForTimeout(1500);
  console.log('B renamed:', JSON.stringify(await stats(B)));
  await launch(A); console.log('A at launch after the rename:', JSON.stringify(await stats(A)), await A.evaluate(() => [$('nameIn').value, $('mName').value].join('/')));
  const acct = p => p.evaluate(() => ({ gccbRounds: localRounds('gccb').map(r => r.strokes + '/' + r.name).join(','), best: localStorage.getItem(COURSES.gccb.best), trophies: ST.trophies.map(t => t.day).join(','), hs: ST.holedShots, rh: ST.rainHoles, daily: Object.keys(dlRecs()).join(','), dailyStatus: Object.values(dlRecs()).map(r => r.status).join(',') }));
  console.log('account A:', JSON.stringify(await acct(A))); console.log('account B:', JSON.stringify(await acct(B)));
  console.log('public players.json:', fs.readFileSync(W + '/leaderboard/players.json', 'utf8').replace(/"bs":\[\],?/g, ''));
  console.log('--- workflow log'); console.log(log.join('\n'));
  await b.close();
})();
