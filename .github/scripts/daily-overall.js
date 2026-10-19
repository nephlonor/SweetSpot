// Rebuilds leaderboard/daily-index.json (one line per finished daily challenge) and leaderboard/daily-overall.json (merit points) from
// leaderboard/daily-<day>.json. Only days that are over (US Eastern) count. Points: 25 18 15 12 10 8 6 4 2 1 for places 1-10, and 1 for finishing.
const fs = require('fs');
const POINTS = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1];
const COURSES = ['gccb', 'alsace', 'augusta'], COURSES4 = ['rothley', 'gccb', 'alsace', 'augusta'], D4 = 20745, COURSES5 = ['stpatricks', 'gccb', 'alsace', 'augusta', 'rothley'], D5 = 20746; // Rothley Park joins the turn on 2026-10-19, St Patrick's on 2026-10-20
module.exports = function build(today) {
  const days = fs.readdirSync('leaderboard').map(f => /^daily-(\d{4}-\d{2}-\d{2})\.json$/.exec(f)).filter(Boolean).map(m => m[1]).filter(d => d < today).sort().reverse();
  const index = [], tot = {};
  for (const d of days) {
    let rows; try { rows = JSON.parse(fs.readFileSync(`leaderboard/daily-${d}.json`, 'utf8')); } catch (e) { continue; }
    if (!Array.isArray(rows) || !rows.length) continue;
    rows = rows.slice().sort((a, b) => a.toPar - b.toPar || a.at - b.at);
    const dn = Math.floor(Date.UTC(+d.slice(0, 4), +d.slice(5, 7) - 1, +d.slice(8, 10)) / 864e5);
    index.push({ d, c: dn >= D5 ? COURSES5[(dn - D5) % 5] : dn >= D4 ? COURSES4[(dn - D4) % 4] : COURSES[dn % 3], n: rows.length, w: rows[0].name, wb: rows[0].by, t: rows[0].toPar });
    let rank = 0;
    rows.forEach((x, i) => {
      if (i === 0 || x.toPar !== rows[i - 1].toPar) rank = i + 1; // players level on the score share the place
      const p = rank <= 10 ? POINTS[rank - 1] : 1, o = tot[x.by] || (tot[x.by] = { by: x.by, n: x.name, p: 0, d: 0, w: 0, pod: 0, best: 99, at: 0 });
      o.p += p; o.d++; if (rank === 1) o.w++; if (rank <= 3) o.pod++; if (x.toPar < o.best) o.best = x.toPar;
      if (x.at >= o.at) { o.at = x.at; o.n = x.name; }
    });
  }
  const overall = Object.values(tot).sort((a, b) => b.p - a.p || b.w - a.w || a.d - b.d || a.at - b.at).slice(0, 300).map(o => ({ by: o.by, n: o.n, p: o.p, d: o.d, w: o.w, pod: o.pod, best: o.best }));
  fs.writeFileSync('leaderboard/daily-index.json', JSON.stringify(index) + '\n');
  fs.writeFileSync('leaderboard/daily-overall.json', JSON.stringify(overall) + '\n');
  return ['leaderboard/daily-index.json', 'leaderboard/daily-overall.json'];
};
