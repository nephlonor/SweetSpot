// The request goes to one device id of a name, another device of that name answers it (no popup on the id it was sent to is not needed).
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
  const B = await device(b, 'B'), C = await device(b, 'C');
  // a player called Zoe is known by the id 'deadbeef' (a device that is not at hand); B is new; C carries the name Zoe too
  const setName = (p, nm, r) => p.evaluate(([nm, r]) => { settings.name = nm; settings.nameSent = nm; saveSettings(); ST.rounds = r; saveStats(); }, [nm, r]);
  fs.writeFileSync(W + '/leaderboard/players.json', JSON.stringify({ deadbeef: { n: 'Zoe', pf: { r: 5, h: 90, xp: 900 }, at: Date.now() } }));
  await setName(B, 'Max', 1); await setName(C, 'Zoe', 4);
  await B.evaluate(() => { $('title').classList.add('on'); $('nameIn').focus(); }); await B.fill('#nameIn', 'zoe'); await B.evaluate(() => $('nameIn').blur()); await B.waitForTimeout(4000);
  console.log('B asked:', await B.evaluate(() => MG.dlg && MG.dlg.kind)); await B.click('#mgOk'); await B.waitForTimeout(1500);
  console.log('merges:', fs.readFileSync(W + '/leaderboard/merges.json', 'utf8').replace(/\d{12,}/g, 'T'));
  // C is not the id the request names, but it has the name: it is asked
  await C.reload(); await C.waitForTimeout(2500); await C.evaluate(() => { $('title').classList.add('on'); }); await C.waitForTimeout(6000);
  console.log('C dialog:', await C.evaluate(() => MG.dlg && [MG.dlg.kind, $('mgB').textContent.slice(0, 50)]));
  await C.click('#mgOk'); await C.waitForTimeout(1500); await C.evaluate(() => mgCheck()); await C.waitForTimeout(1500);
  console.log('merges:', fs.readFileSync(W + '/leaderboard/merges.json', 'utf8').replace(/\d{12,}/g, 'T'));
  console.log('C:', await C.evaluate(() => ({ mgP: settings.mgP || null, dlg: MG.dlg && MG.dlg.kind, rounds: ST.rounds })));
  await B.evaluate(() => mgCheck()); await B.waitForTimeout(1500);
  console.log('B:', await B.evaluate(() => ({ mgP: settings.mgP || null, dlg: MG.dlg && MG.dlg.kind, rounds: ST.rounds, name: settings.name })));
  console.log('--- workflow log'); console.log(log.join('\n'));
  await b.close();
})();
