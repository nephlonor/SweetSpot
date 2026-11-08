// Rebuilds leaderboard/daily-index.json (one line per finished daily challenge) and leaderboard/daily-overall.json (the Tournament: merit points
// of the last TOUR finished days, a rolling window) from leaderboard/daily-<day>.json. Only days that are over (US Eastern) count. Points: 25 18 15 12
// 10 8 6 4 2 1 for places 1-10, and 1 for finishing. A day nobody (or not this player) played still takes its place in the window. Each player keeps
// r: {day: [place, toPar]}, so the game can move the window on by itself when the rebuild is late.
const fs = require('fs');
const POINTS = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1], TOUR = 4;
const COURSES = ['gccb', 'alsace', 'augusta'], COURSES4 = ['rothley', 'gccb', 'alsace', 'augusta'], D4 = 20745, COURSES5 = ['stpatricks', 'gccb', 'alsace', 'augusta', 'rothley'], D5 = 20746, COURSES7 = ['pebblebeach', 'mountainvalley', 'rothley', 'stpatricks', 'gccb', 'alsace', 'augusta'], D7 = 20750, COURSES8 = ['fourmile', 'pebblebeach', 'mountainvalley', 'rothley', 'stpatricks', 'gccb', 'alsace', 'augusta'], D8 = 20758, COURSES11 = ['ledgeview', 'westminster', 'landmand', 'fourmile', 'pebblebeach', 'mountainvalley', 'rothley', 'stpatricks', 'gccb', 'alsace', 'augusta'], D11 = 20765; // from 2026-11-08 every course but The Isles; Rothley Park joins the turn on 2026-10-19, St Patrick's on 2026-10-20
// players level on the best score all won the day: ws/wbs list every winner (only when there are several)
const tieW = rows => { const w = rows.filter(x => x.toPar === rows[0].toPar); return w.length > 1 ? { ws: w.map(x => x.name), wbs: w.map(x => x.by) } : {}; };
module.exports = function build(today) {
  const days = fs.readdirSync('leaderboard').map(f => /^daily-(\d{4}-\d{2}-\d{2})\.json$/.exec(f)).filter(Boolean).map(m => m[1]).filter(d => d < today).sort().reverse();
  const index = [], tot = {}, dnum = d => Math.floor(Date.UTC(+d.slice(0, 4), +d.slice(5, 7) - 1, +d.slice(8, 10)) / 864e5), first = dnum(today) - TOUR; // the window: the TOUR days before today
  for (const d of days) {
    let rows; try { rows = JSON.parse(fs.readFileSync(`leaderboard/daily-${d}.json`, 'utf8')); } catch (e) { continue; }
    if (!Array.isArray(rows) || !rows.length) continue;
    rows = rows.slice().sort((a, b) => a.toPar - b.toPar || a.at - b.at);
    { const seen = new Set(); rows = rows.filter(x => { const k = String(x.name).toLowerCase(); if (seen.has(k)) return false; seen.add(k); return true; }); } // one player per name and day: the better result
    const dn = dnum(d);
    index.push(Object.assign({ d, c: dn >= D11 ? COURSES11[(dn - D11) % 11] : dn >= D8 ? COURSES8[(dn - D8) % 8] : dn === 20757 ? 'gccb' : dn >= D7 ? COURSES7[(dn - D7) % 7] : dn >= D5 ? COURSES5[(dn - D5) % 5] : dn >= D4 ? COURSES4[(dn - D4) % 4] : COURSES[dn % 3], n: rows.length, w: rows[0].name, wb: rows[0].by, t: rows[0].toPar }, tieW(rows)));
    if (dn < first) continue; // older than the window: archive only
    let rank = 0;
    rows.forEach((x, i) => {
      if (i === 0 || x.toPar !== rows[i - 1].toPar) rank = i + 1; // players level on the score share the place
      const nk = String(x.name).toLowerCase(), p = rank <= 10 ? POINTS[rank - 1] : 1, o = tot[nk] || (tot[nk] = { by: x.by, bys: [], n: x.name, p: 0, d: 0, w: 0, pod: 0, best: 99, at: 0, r: {} }); // a name is one player, even on two devices: their points are added up
      if (!o.bys.includes(x.by)) o.bys.push(x.by);
      o.r[d] = [rank, x.toPar]; o.p += p; o.d++; if (rank === 1) o.w++; if (rank <= 3) o.pod++; if (x.toPar < o.best) o.best = x.toPar;
      if (x.at >= o.at) { o.at = x.at; o.n = x.name; o.by = x.by; }
    });
  }
  const overall = Object.values(tot).filter(o => o.p > 0).sort((a, b) => b.p - a.p || b.w - a.w || a.d - b.d || a.at - b.at).slice(0, 300).map(o => Object.assign({ by: o.by, n: o.n, p: o.p, d: o.d, w: o.w, pod: o.pod, best: o.best, r: o.r }, o.bys.length > 1 ? { bys: o.bys } : {}));
  fs.writeFileSync('leaderboard/daily-index.json', JSON.stringify(index) + '\n');
  fs.writeFileSync('leaderboard/daily-overall.json', JSON.stringify(overall) + '\n');
  return ['leaderboard/daily-index.json', 'leaderboard/daily-overall.json'];
};
