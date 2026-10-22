// Trailer capture: the game runs on a virtual clock (rAF, timers, performance.now, Math.random seeded) that this script steps one frame at a time,
// scripted thumbs drive the real pointer handlers, and every frame is a screenshot. Frame time in the slow software renderer does not matter.
const { chromium } = require('/opt/node-tools/node_modules/playwright'); const fs = require('fs');
const THREE = process.env.THREE || '/tmp/claude-0/-home-user-SweetSpot/42254a9d-b7ad-52d7-9d2e-d0f8e3c6d97d/scratchpad/three.min.js';
const INIT = () => {
  let vt = 1000, seed = 12345, rafQ = [], timers = [], tid = 1;
  const rnd = () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  Math.random = rnd; window.__seed = s => { seed = s; };
  performance.now = () => vt; Date.now = () => 1.7e12 + vt;
  window.requestAnimationFrame = f => { rafQ.push(f); return rafQ.length; }; window.cancelAnimationFrame = () => { };
  window.setTimeout = (f, ms = 0, ...a) => { const id = tid++; timers.push({ id, t: vt + Math.max(0, +ms || 0), f, a }); return id; };
  window.setInterval = (f, ms = 0, ...a) => { const id = tid++; timers.push({ id, t: vt + Math.max(1, +ms || 1), f, a, iv: Math.max(1, +ms || 1) }); return id; };
  window.clearTimeout = window.clearInterval = id => { timers = timers.filter(x => x.id !== id); };
  const runTimers = () => { for (let k = 0; k < 50; k++) { const due = timers.filter(x => x.t <= vt).sort((a, b) => a.t - b.t)[0]; if (!due) break; if (due.iv) due.t += due.iv; else timers = timers.filter(x => x !== due); try { due.f(...due.a); } catch (e) { console.error(e); } } };
  // thumbs: soft pads that follow the scripted pointers, with a fading trail on the left one
  const pads = {};
  const mk = (id) => { const d = document.createElement('div'); d.style.cssText = 'position:fixed;left:0;top:0;width:64px;height:64px;margin:-32px 0 0 -32px;border-radius:50%;pointer-events:none;z-index:99999;opacity:0;background:radial-gradient(circle at 42% 38%,rgba(255,255,255,.62),rgba(255,255,255,.28) 62%,rgba(255,255,255,.12));box-shadow:0 0 0 2px rgba(255,255,255,.55),0 6px 18px rgba(0,0,0,.35);transition:none'; document.body.appendChild(d); const trail = []; for (let i = 0; i < 9; i++) { const t = document.createElement('div'); t.style.cssText = `position:fixed;left:0;top:0;width:${34 - i * 2.5}px;height:${34 - i * 2.5}px;margin:${-(17 - i * 1.25)}px 0 0 ${-(17 - i * 1.25)}px;border-radius:50%;pointer-events:none;z-index:99998;opacity:0;background:rgba(255,255,255,${.34 - i * .033})`; document.body.appendChild(t); trail.push(t); } return pads[id] = { d, trail, hist: [] }; };
  window.__pad = (id, x, y, down, press) => { const p = pads[id] || mk(id); if (document.body.classList.contains('cine')) down = false; p.d.style.opacity = down ? 1 : 0; p.d.style.transform = `translate(${x}px,${y}px) scale(${press ? .86 : 1})`; if (down) { p.hist.unshift([x, y]); p.hist.length = Math.min(p.hist.length, 10); } else p.hist = []; p.trail.forEach((t, i) => { const h = p.hist[i + 1]; t.style.opacity = h && id === 'L' ? 1 : 0; if (h) t.style.transform = `translate(${h[0]}px,${h[1]}px)`; }); };
  window.__ptr = (type, x, y, id) => { const el = document.elementFromPoint(x, y) || document.body; const e = new PointerEvent(type, { bubbles: true, cancelable: true, pointerId: id, pointerType: 'touch', isPrimary: id === 1, clientX: x, clientY: y, view: window }); Object.defineProperty(e, 'timeStamp', { value: vt }); el.dispatchEvent(e); };
  // one frame: sub-steps of 1/120 s carry the thumb events (their own timestamps), the rAF callbacks run once at the end
  window.__frame = (dtMs, evs) => { const n = 4, h = dtMs / n; evs = evs || []; for (let i = 0; i < n; i++) { vt += h; for (const e of evs[i] || []) { if (e[0] === 'pad') window.__pad(e[1], e[2], e[3], e[4], e[5]); else window.__ptr(e[0], e[1], e[2], e[3]); } runTimers(); } const q = rafQ; rafQ = []; for (const f of q) try { f(vt); } catch (e) { console.error(e); } return vt; };
};
async function open(opts = {}) {
  const W = opts.w || 405, H = opts.h || 720, DSF = opts.dsf || 2;
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--disable-gpu-vsync'] });
  const p = await (await b.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: DSF, hasTouch: true })).newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => { localStorage.setItem('ssg-intro-seen', '1'); localStorage.setItem('ssg-dev', 'trailerdev1'); }); await p.addInitScript(INIT);
  await p.route('**/three.min.js', r => r.fulfill({ path: THREE, contentType: 'application/javascript' })); await p.route('**/fonts.googleapis.com/**', r => r.abort()); await p.route('https://**/*', r => r.request().url().includes('three') ? r.fallback() : r.abort());
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.evaluate(() => __frame(16, []));
  return { b, p, W, H };
}
module.exports = { open };
