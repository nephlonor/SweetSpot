// Metropolis Links: eighteen holes laid into six real cities, three holes each: New York, London, Paris, Tokyo, Amsterdam, Rio de Janeiro.
// The cities are drawn as they stand in OpenStreetMap (every building's outline and height, the rivers, canals and sea, the parks, the beaches,
// the street trees), the ground of Montmartre and Rio from SRTM; nothing has been moved or left out to make room. The holes run where there was
// room: down the streets and squares, through the parks, over the rivers, and on two holes from roof to roof (the street below is out of bounds).
// A ball that hits a building comes off it keeping 93 % of its pace; one that comes down on a roof out of play is out of bounds.
// A hole is an ordinary made-up hole (makeCourse) with def.city set; index.html calls metroPrep, metroRoofH, metroFinish and metroBuild.
// Everything is in the hole's own frame: x to the right, f forward from the tee (world z = -f). The data (METRO_DATA) is written by build.py.

/* ---------------- the cities' facades and colours (where OpenStreetMap gives no colour) ---------------- */
const METRO_STYLE = {
  ny: { tex: ['brick', 'office', 'glass'], tall: 'glass', cols: { brick: [0x9a5b46, 0x8a6a58, 0xb07a5a, 0xa4705c, 0xc9b9a0], office: [0xd8d2c4, 0xb9b3a8, 0xa0a4a8, 0xe2dccd], glass: [0x9fc0d8, 0x7fa3bf, 0xb7cfe0, 0x8db0c4] }, roof: 0x6d6a66 },
  london: { tex: ['stone', 'brick', 'office'], tall: 'glass', cols: { stone: [0xe6dcc8, 0xd9cdb4, 0xece4d2], brick: [0xa0604a, 0x8e5642, 0xb47a5e, 0xc9a27e], office: [0xd8d2c4, 0xc4c8cc], glass: [0x9db8c8, 0x8aa6b8] }, roof: 0x5f6870 },
  paris: { tex: ['hauss'], tall: 'glass', mansard: true, cols: { hauss: [0xeee3cc, 0xe9dcc2, 0xf1e8d6, 0xe4d6bb], glass: [0x9db8c8] }, roof: 0x5d6873 },
  tokyo: { tex: ['office', 'tile', 'glass'], tall: 'glass', cols: { office: [0xe8e6e0, 0xc8c8c4, 0xd6d0c4, 0xb4b8bc], glass: [0x9cb8c8, 0x86a2b6, 0xaec4d2], tile: [0xe9e2d6, 0xd4cfc6, 0xc4b8a6] }, roof: 0x7a7d80 },
  ams: { tex: ['canal'], tall: 'office', gable: true, cols: { canal: [0x7a3b2e, 0x5e3a2c, 0x8c4a34, 0x3a3532, 0xe8e2d6, 0x46584a, 0x9a5a3c, 0x6b4a3a], office: [0xd8d2c4, 0xb9b3a8] }, roof: 0x4a4644 },
  rio: { tex: ['tower', 'favela', 'office'], tall: 'tower', cols: { tower: [0xf2efe6, 0xe9d8b8, 0xd8e6ee, 0xf0d6c4, 0xe6efe0], favela: [0xe9a35a, 0x5fa8d3, 0xe8d36a, 0xd8665a, 0x8cc47a, 0xf0ece0, 0xc98bd0, 0xe07f4f], office: [0xeae6dc, 0xd4d8dc] }, roof: 0x9a958c }
};
const MT_T4 = [{ f: -6, c: 0x6fa8dc }, { f: -2, c: 0xffffff }, { f: 3, c: 0xffd966 }, { f: 6, c: 0xf4a0a0 }], MT_T3 = [{ f: -4, c: 0x6fa8dc }, { f: 0, c: 0xffffff }, { f: 4, c: 0xffd966 }];
const MT_INSPO = {
  'Times Square': 'New York: up Broadway through the bow tie of Times Square, under the billboards, to a green by the red steps',
  'Skyline': 'New York, Midtown: from roof to roof along a row of real blocks some sixty metres up; the cross streets below are out of bounds',
  'Central Park': 'New York: down the Great Lawn with the ballfields, to a green above Turtle Pond and Belvedere Castle',
  'Westminster': 'London: down the Victoria Embankment beside the Thames, the Eye across the river, to Big Ben',
  'Over the Thames': 'London: from beside City Hall over the Thames to a green in the moat of the Tower of London, Tower Bridge on the right',
  'Bank Job': 'London, the City: through the narrow streets past the Walkie-Talkie; play the corners off the walls',
  'Champs-Élysées': "Paris: up the Champs-Élysées between the plane trees, the Arc de Triomphe beyond the green",
  'La Tour Eiffel': "Paris: from the Trocadéro over the Seine, under (or over) the Eiffel Tower, down the Champ de Mars",
  'Montmartre': 'Paris: straight up the butte through the Square Louise-Michel to a green under the Sacré-Cœur',
  'Shibuya Crossing': 'Tokyo: down the streets of Shibuya to a green on the scramble crossing',
  'Tokyo Tower': 'Tokyo: from one tower roof to a lower one across the street, Tokyo Tower beyond',
  'Sensō-ji': 'Tokyo, Asakusa: from the Thunder Gate up Nakamise-dōri, over the Hōzōmon to the main hall, the pagoda alongside',
  'Dam': 'Amsterdam: up from the canals to a green on Dam Square in front of the Royal Palace',
  'Leidseplein': 'Amsterdam: along the canal ring to Leidseplein; the canals are water hazards all the way',
  'Museumplein': 'Amsterdam: across Museumplein to a green in front of the Rijksmuseum',
  'Copacabana': 'Rio: along the Avenida Atlântica between the hotels and the beach, the Atlantic beyond the sand',
  'Pão de Açúcar': 'Rio: from Praia Vermelha out to an island green in the sea, under Sugarloaf',
  'Jockey Club': 'Rio: down the infield of the Jockey Club racecourse, the Lagoa beyond, Christ the Redeemer high on Corcovado'
};
let METRO_LIST = null;
function metroDefs() {
  if (METRO_LIST) return METRO_LIST;
  return METRO_LIST = METRO_DATA.map((d, i) => {
    const o = d.def, trees = [];
    for (const [x, f] of d.T) { if (Math.hypot(x - o.green.x, f - o.green.f) < o.green.rx + 4 || Math.hypot(x, f) < 8) continue; const k = hash2(Math.round(x), Math.round(f), 3); trees.push({ x, f, kind: 'oak', h: 9 + 6 * k, r: 3.2 + 2 * k }); }
    return Object.assign({
      teeMarkers: o.par === 3 ? MT_T3 : MT_T4, fairwayPods: [], roughIslands: [], waters: [], creeks: [], paths: [], ob: () => false, obLines: [],
      treeLines: [], treeClusters: [], landmarks: trees, shape: () => 0, hum: .1, blocks: [], roofs: [], inspo: MT_INSPO[o.name] || ''
    }, o, { real3d: true });
  });
}

/* ---------------- the data of a hole: buildings, water, parks, sand, the ground ---------------- */
const MT_CACHE = {};
function mtData(i) {
  if (MT_CACHE[i]) return MT_CACHE[i];
  const d = METRO_DATA[i], B = b64i16(d.B), out = { blds: [], water: [], parks: [], sand: [] };
  let k = 1;
  for (let n = B[0], q = 0; q < n; q++) {
    const m = B[k], h = B[k + 1] / 10, minh = B[k + 2] / 10, roof = B[k + 3] & 1, ci = B[k + 4]; k += 5;
    const P = new Float32Array(m * 2); let x0 = 1e9, x1 = -1e9, z0 = 1e9, z1 = -1e9;
    for (let j = 0; j < m; j++) { const x = B[k + 2 * j] / 10, z = -B[k + 2 * j + 1] / 10; P[2 * j] = x; P[2 * j + 1] = z; x0 = Math.min(x0, x); x1 = Math.max(x1, x); z0 = Math.min(z0, z); z1 = Math.max(z1, z); }
    k += 2 * m;
    out.blds.push({ P, h, minh, roof: !!roof, col: ci === -32768 ? null : ci + 32768 - 1, bb: [x0, x1, z0, z1], id: q });
  }
  const polys = s => { const A = b64i16(s), res = []; let j = 1; for (let n = A[0], q = 0; q < n; q++) { const nr = A[j++], rings = []; for (let r = 0; r < nr; r++) { const m = A[j++], R = new Float32Array(m * 2); for (let t = 0; t < m; t++) { R[2 * t] = A[j + 2 * t] / 10; R[2 * t + 1] = -A[j + 2 * t + 1] / 10; } j += 2 * m; rings.push(R); } res.push(rings); } return res; };
  out.water = polys(d.W); out.parks = polys(d.P); out.sand = polys(d.S);
  if (d.D) { const A = b64i16(d.D.d); out.dem = { res: d.D.res, n: d.D.n, a: A }; }
  return MT_CACHE[i] = out;
}
function mtDem(dm, x, z) { // metres above the tee, bilinear
  if (!dm) return 0; const f = -z, n = dm.n, u = x / dm.res + n / 2, v = f / dm.res + n / 2, j = Math.floor(u), i = Math.floor(v);
  if (i < 0 || j < 0 || i >= n - 1 || j >= n - 1) return 0;
  const a = dm.a, fu = u - j, fv = v - i, k = i * n + j;
  return ((a[k] * (1 - fu) + a[k + 1] * fu) * (1 - fv) + (a[k + n] * (1 - fu) + a[k + n + 1] * fu) * fv) / 10;
}
function mtInRing(R, x, z) { let ins = false; for (let i = 0, n = R.length >> 1, j = n - 1; i < n; j = i++) { const xi = R[2 * i], zi = R[2 * i + 1], xj = R[2 * j], zj = R[2 * j + 1]; if ((zi > z) !== (zj > z) && x < (xj - xi) * (z - zi) / (zj - zi) + xi) ins = !ins; } return ins; }
// the class raster: water, turf (parks), sand, at 1.5 m, antialiased; coverage 0..1 per class
function mtRaster(C, D) {
  const I = C.inner, res = 1.5, x0 = I.minX - 40, z0 = I.minZ - 40, w = Math.ceil((I.maxX + 40 - x0) / res), h = Math.ceil((I.maxZ + 40 - z0) / res);
  const cv = document.createElement('canvas'); cv.width = w; cv.height = h; const g = cv.getContext('2d'); g.globalCompositeOperation = 'lighter';
  const draw = (list, col) => { g.fillStyle = col; for (const rings of list) { g.beginPath(); for (const R of rings) { for (let t = 0; t < R.length; t += 2) { const px = (R[t] - x0) / res, py = (R[t + 1] - z0) / res; t ? g.lineTo(px, py) : g.moveTo(px, py); } g.closePath(); } g.fill('evenodd'); } };
  draw(D.water, '#ff0000'); draw(D.parks, '#00ff00'); draw(D.sand, '#0000ff');
  const img = g.getImageData(0, 0, w, h).data;
  return { x0, z0, w, h, res, img };
}
function mtCls(C, x, z, ch) { // coverage of class ch (0 water, 1 turf, 2 sand) at a point; beyond the raster: none (turf in the hills)
  const R = C.mtR; if (!R) return 0; const u = (x - R.x0) / R.res - .5, v = (z - R.z0) / R.res - .5, i = Math.floor(u), j = Math.floor(v);
  if (i < 0 || j < 0 || i >= R.w - 1 || j >= R.h - 1) return ch === 1 && C.dem ? 1 : 0;
  const a = R.img, fu = u - i, fv = v - j, k = (j * R.w + i) * 4 + ch, W = R.w * 4;
  return ((a[k] * (1 - fu) + a[k + 4] * fu) * (1 - fv) + (a[k + W] * (1 - fu) + a[k + W + 4] * fu) * fv) / 255;
}
function metroPrep(C) {
  const def = C.def, D = mtData(def.data);
  C.mtD = D; C.dem = D.dem || null;
  // the roofs a rooftop hole is played on: the ground is raised to them
  C.roofs = D.blds.filter(b => b.roof);
  C.offRoof = C.roofs.length ? (x, z) => !C.roofs.some(b => x >= b.bb[0] && x <= b.bb[1] && z >= b.bb[2] && z <= b.bb[3] && mtInRing(b.P, x, z)) : () => false;
  for (const b of D.blds) { let lo = 1e9; for (let t = 0; t < b.P.length; t += 2) lo = Math.min(lo, mtDem(C.dem, b.P[t], b.P[t + 1])); b.base = lo; b.y0 = lo + b.minh; b.y1 = lo + b.h; }
  C.mtLevel = C.dem ? Math.max(-80, mtDem(C.dem, 1e9, 1e9) - 0) : -1.3; // (the water's surface: 1.3 m under the street; on the hills it is set in metroFinish)
}
function metroRoofH(C, x, z) {
  let h = mtDem(C.dem, x, z);
  for (const b of C.roofs) {
    if (x < b.bb[0] - .3 || x > b.bb[1] + .3 || z < b.bb[2] - .3 || z > b.bb[3] + .3) continue;
    const ins = mtInRing(b.P, x, z), d = mtEdge(b.P, x, z).d, s = ins ? d : -d;
    if (s > -.1) h = Math.max(h, b.y1 * smooth(-.1, .25, s) + mtDem(C.dem, x, z) * (1 - smooth(-.1, .25, s)));
  }
  return h;
}
const _me = { d: 0, nx: 0, nz: 0, px: 0, pz: 0 };
function mtEdge(R, x, z) { // the nearest point of a ring's outline, and the outward normal there (for a ring drawn either way round)
  let best = 1e18, n = R.length >> 1;
  let area = 0; for (let i = 0, j = n - 1; i < n; j = i++) area += (R[2 * j] - R[2 * i]) * (R[2 * j + 1] + R[2 * i + 1]);
  const sg = area > 0 ? 1 : -1;
  for (let i = 0, j = n - 1; i < n; j = i++) {
    const ax = R[2 * j], az = R[2 * j + 1], bx = R[2 * i], bz = R[2 * i + 1], vx = bx - ax, vz = bz - az, l2 = vx * vx + vz * vz || 1e-9;
    let t = ((x - ax) * vx + (z - az) * vz) / l2; t = t < 0 ? 0 : t > 1 ? 1 : t;
    const px = ax + vx * t, pz = az + vz * t, d2 = (x - px) ** 2 + (z - pz) ** 2;
    if (d2 < best) { best = d2; const l = Math.sqrt(l2); _me.nx = sg * vz / l; _me.nz = -sg * vx / l; _me.px = px; _me.pz = pz; }
  }
  _me.d = Math.sqrt(best); return _me;
}
function metroFinish(C) {
  const def = C.def, D = C.mtD, hw = def.hw;
  C.mtR = mtRaster(C, D);
  // the water's surface: on the flat cities 1.3 m under the street; on the hills, the lowest ground round it
  if (C.dem) { let lo = 1e9; for (const rings of D.water) { const R = rings[0]; for (let t = 0; t < R.length; t += 6) lo = Math.min(lo, mtDem(C.dem, R[t], R[t + 1])); } C.mtLevel = lo < 1e8 ? lo - .6 : -1.3; }
  const lv = C.mtLevel, baseH0 = C.h, grad0 = C.grad, wl0 = C.wl, si0 = C.surfInfo, f0 = C.fields;
  const wet = (x, z) => def.island && blobS(C.island, x, z) < 1.04 ? 0 : mtCls(C, x, z, 0);
  // the ground drops into the water at the quay
  C.h = (x, z) => { const h = baseH0(x, z), w = wet(x, z); return w > .02 ? lerp(h, Math.min(h, lv - 1.4), smooth(.02, .6, w)) : h; };
  C.grad = (x, z, o) => { const e = .2; o[0] = (C.h(x + e, z) - C.h(x - e, z)) / (2 * e); o[1] = (C.h(x, z + e) - C.h(x, z - e)) / (2 * e); return o; };
  C.wl = (x, z) => wet(x, z) > .02 ? lv : wl0(x, z);
  C.surfInfo = (x, z, hh) => {
    const inf = si0(x, z, hh); if (inf.surf === S.WATER) return inf;
    const h = hh != null ? hh : C.h(x, z);
    if (wet(x, z) > .3 && h < lv - .02) { inf.surf = S.WATER; inf.water = 300; inf.stripe = 0; return inf; }
    if (inf.surf === S.DEEP && !C.offRoof(x, z)) { // beyond the turf: a park is rough, a beach is sand, the rest is the street
      if (mtCls(C, x, z, 2) > .5) { inf.surf = S.SAND; inf.waste = true; } else if (mtCls(C, x, z, 1) > .5) inf.surf = S.ROUGH;
    }
    return inf;
  };
  C.surf = (x, z) => C.surfInfo(x, z).surf;
  C.fields = (x, z) => {
    const F = f0(x, z); if (C.offRoof(x, z)) return F;
    const t = mtCls(C, x, z, 1), s = mtCls(C, x, z, 2);
    if (t > 0) F.deep = Math.min(F.deep, (.5 - t) * 3);
    if (s > 0) { const sd = (.5 - s) * 3; F.sand = Math.min(F.sand, sd); F.waste = Math.min(F.waste, sd); F.deep = Math.max(F.deep, -sd); }
    if (wet(x, z) > .02) F.wl = lv;
    return F;
  };
  // out of bounds: a long way off the hole, in the street under a rooftop hole
  const lines = [mkPoly(def.route, null)], lineD = (x, z) => { let d = 1e6; for (const l of lines) d = Math.min(d, polyQ(l, x, z, hw + 6).d); return d; };
  C.cityLine = lines[0];
  const ob0 = C.isOB; C.isOB = (x, z) => ob0(x, z) || C.offRoof(x, z) || lineD(x, z) > hw + 2;
  // every building (and every landmark's parts) stops a ball; the hash the ball looks them up in
  const boxes = C.boxes = [], names = C.colNames = {}, cell = 20, hash = new Map();
  for (const b of D.blds) { b.out = !b.roof; b.kind = 'poly'; b.yc = b.roof ? b.y1 - .3 : b.y1; b.id = 100001 + boxes.length; names[b.id] = b.roof ? 'Off the wall!' : 'Off the building!'; boxes.push(b); }
  C.mons = [];
  for (const m of def.mons || []) {
    const base = mtDem(C.dem, m.x, -m.f), s = m.s || 1, a = (m.rot || 0) * DEG, ux = Math.cos(a), uz = -Math.sin(a), vx = -uz, vz = ux, X = m.x, Z = -m.f;
    C.mons.push({ m, base }); if (m.far) continue;
    const k = MT_MON[m.kind]; if (!k || !k.cols) continue;
    for (const [lx, lz, w, d, y0, y1, out] of k.cols(m)) {
      const cx = X + s * (lx * ux + lz * vx), cz = Z + s * (lx * uz + lz * vz), hw2 = s * w / 2, hd2 = s * d / 2, P = new Float32Array(8);
      [[-1, -1], [1, -1], [1, 1], [-1, 1]].forEach(([i, j], q) => { P[2 * q] = cx + i * hw2 * ux + j * hd2 * vx; P[2 * q + 1] = cz + i * hw2 * uz + j * hd2 * vz; });
      const b = { P, bb: [Math.min(P[0], P[2], P[4], P[6]), Math.max(P[0], P[2], P[4], P[6]), Math.min(P[1], P[3], P[5], P[7]), Math.max(P[1], P[3], P[5], P[7])], y0: y0 < 0 ? -40 : base + s * y0, y1: base + s * y1, out: out !== false, kind: 'poly', mon: true };
      b.yc = b.y1; b.id = 100001 + boxes.length; names[b.id] = k.name || 'Off the wall!'; boxes.push(b);
    }
  }
  for (const b of boxes) for (let gx = Math.floor(b.bb[0] / cell); gx <= Math.floor(b.bb[1] / cell); gx++) for (let gz = Math.floor(b.bb[2] / cell); gz <= Math.floor(b.bb[3] / cell); gz++) { const k = gx * 73856 + gz; if (!hash.has(k)) hash.set(k, []); hash.get(k).push(b); }
  C.boxHit = (x, y, z, Q) => {
    const a = hash.get(Math.floor(x / cell) * 73856 + Math.floor(z / cell)); if (!a) return null;
    for (let i = 0; i < a.length; i++) {
      const b = a[i]; if (y >= b.yc || y < b.y0 || x < b.bb[0] || x > b.bb[1] || z < b.bb[2] || z > b.bb[3] || !mtInRing(b.P, x, z)) continue;
      const e = mtEdge(b.P, x, z), pt = b.yc - y, pb = b.minh > .5 || b.y0 > -30 && b.mon ? y - b.y0 : 1e9, m = Math.min(e.d, pt, pb);
      Q.top = m === pt; Q.bot = !Q.top && m === pb; Q.id = b.id;
      if (!Q.top && !Q.bot) { Q.nx = e.nx; Q.nz = e.nz; Q.px = e.px + e.nx * .05; Q.pz = e.pz + e.nz * .05; }
      return b;
    }
    return null;
  };
  // a fog that lets the mountains of Rio be seen
  C.fogK = C.dem && def.city === 'rio' ? 3 : 1;
}

/* ---------------- drawing ---------------- */
const MT_TEX = {};
function mtTex(kind) { // one bay by one storey of a facade, white where the wall is (the building's colour tints it)
  if (MT_TEX[kind]) return MT_TEX[kind];
  const cv = document.createElement('canvas'); cv.width = cv.height = 128; const x = cv.getContext('2d');
  x.fillStyle = '#ffffff'; x.fillRect(0, 0, 128, 128);
  const win = (x0, y0, w, h, glass, frame) => { if (frame) { x.fillStyle = frame; x.fillRect(x0 - 4, y0 - 4, w + 8, h + 8); } x.fillStyle = glass; x.fillRect(x0, y0, w, h); x.fillStyle = 'rgba(255,255,255,.22)'; x.fillRect(x0, y0, w * .3, h); };
  if (kind === 'brick') { x.fillStyle = 'rgba(0,0,0,.06)'; for (let j = 0; j < 128; j += 8) x.fillRect(0, j, 128, 1); win(34, 26, 60, 70, '#3e4c5a', '#e8e2d8'); x.fillStyle = '#d9d2c6'; x.fillRect(28, 98, 72, 6); }
  else if (kind === 'stone') { x.fillStyle = 'rgba(0,0,0,.05)'; for (let j = 0; j < 128; j += 16) x.fillRect(0, j, 128, 1); win(38, 20, 52, 80, '#46525c', '#f4efe6'); }
  else if (kind === 'office') { x.fillStyle = '#4a5b6a'; x.fillRect(0, 34, 128, 66); x.fillStyle = 'rgba(255,255,255,.75)'; for (let i = 0; i < 128; i += 32) x.fillRect(i, 34, 4, 66); x.fillStyle = 'rgba(255,255,255,.18)'; x.fillRect(0, 34, 128, 14); }
  else if (kind === 'glass') { const g = x.createLinearGradient(0, 0, 0, 128); g.addColorStop(0, '#d8e6ee'); g.addColorStop(1, '#8aa2b4'); x.fillStyle = g; x.fillRect(0, 0, 128, 128); x.fillStyle = 'rgba(255,255,255,.8)'; x.fillRect(0, 0, 3, 128); x.fillRect(0, 0, 128, 3); x.fillStyle = 'rgba(255,255,255,.25)'; x.fillRect(64, 0, 2, 128); }
  else if (kind === 'hauss') { x.fillStyle = 'rgba(0,0,0,.05)'; x.fillRect(0, 0, 128, 6); win(42, 16, 44, 92, '#4b5866', '#f6f1e6'); x.fillStyle = '#2b2e33'; x.fillRect(30, 80, 68, 4); for (let i = 32; i < 98; i += 6) x.fillRect(i, 84, 2, 24); }
  else if (kind === 'tile') { x.fillStyle = 'rgba(0,0,0,.05)'; for (let j = 0; j < 128; j += 6) x.fillRect(0, j, 128, 1); win(10, 30, 108, 56, '#52606c', null); }
  else if (kind === 'canal') { win(18, 22, 34, 78, '#36424c', '#f2efe8'); win(76, 22, 34, 78, '#36424c', '#f2efe8'); x.fillStyle = '#f2efe8'; x.fillRect(18, 58, 34, 4); x.fillRect(76, 58, 34, 4); x.fillRect(33, 22, 4, 78); x.fillRect(91, 22, 4, 78); }
  else if (kind === 'tower') { x.fillStyle = 'rgba(0,0,0,.05)'; x.fillRect(0, 100, 128, 6); win(20, 30, 88, 60, '#4d6474', null); x.fillStyle = '#ffffff'; x.fillRect(14, 92, 100, 8); }
  else if (kind === 'favela') { x.fillStyle = 'rgba(0,0,0,.08)'; for (let j = 0; j < 128; j += 10) x.fillRect(0, j + ((j / 10) % 2) * 3, 128, 1); win(48, 44, 32, 34, '#3a3a3a', '#f0ece4'); }
  const t = new THREE.CanvasTexture(cv); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 4;
  return MT_TEX[kind] = t;
}
const MT_TILE = { brick: [4, 3.5], stone: [4, 3.6], office: [3.6, 3.8], glass: [3, 3.8], hauss: [4, 3.4], tile: [4, 3.6], canal: [3.2, 3.1], tower: [4, 3.1], favela: [3, 2.8] };
// buffers for merged geometry: quads with outward normals, optional uv, vertex colours
function mtBuf() { return { pos: [], nor: [], col: [], uv: [] }; }
const _mc = new THREE.Color();
function mtQuad(B, a, b, c, d, n, col, uv) { // a b c d counter-clockwise seen from the side n points to
  const e1 = [b[0] - a[0], b[1] - a[1], b[2] - a[2]], e2 = [c[0] - a[0], c[1] - a[1], c[2] - a[2]], cr = [e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0]];
  if (cr[0] * n[0] + cr[1] * n[1] + cr[2] * n[2] < 0) { const t = b; b = d; d = t; if (uv) uv = [uv[0], uv[3], uv[2], uv[1]]; }
  _mc.set(col);
  for (const [p, k] of [[a, 0], [b, 1], [c, 2], [a, 0], [c, 2], [d, 3]]) { B.pos.push(p[0], p[1], p[2]); B.nor.push(n[0], n[1], n[2]); B.col.push(_mc.r, _mc.g, _mc.b); if (uv) B.uv.push(uv[k][0], uv[k][1]); }
}
// a box: four walls (textured into T if given, with tile size), a lid into P
function mtSolid(T, P, b, y0, y1, col, roofCol, tile, noLid) {
  const cs = [[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([i, j]) => [b.x + i * b.hw * b.ux + j * b.hd * b.vx, b.z + i * b.hw * b.uz + j * b.hd * b.vz]);
  const cx = b.x, cz = b.z;
  for (let k = 0; k < 4; k++) {
    const p = cs[k], q = cs[(k + 1) % 4], mx = (p[0] + q[0]) / 2 - cx, mz = (p[1] + q[1]) / 2 - cz, ml = Math.hypot(mx, mz) || 1, n = [mx / ml, 0, mz / ml], L = Math.hypot(q[0] - p[0], q[1] - p[1]);
    const uv = tile ? [[0, 0], [L / tile[0], 0], [L / tile[0], (y1 - y0) / tile[1]], [0, (y1 - y0) / tile[1]]] : null;
    mtQuad(tile ? T : P, [p[0], y0, p[1]], [q[0], y0, q[1]], [q[0], y1, q[1]], [p[0], y1, p[1]], n, col, uv);
  }
  if (!noLid) mtQuad(P, [cs[0][0], y1, cs[0][1]], [cs[1][0], y1, cs[1][1]], [cs[2][0], y1, cs[2][1]], [cs[3][0], y1, cs[3][1]], [0, 1, 0], roofCol);
}
function mtMesh(grp, B, mat) {
  if (!B.pos.length) return null;
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(B.pos, 3)); g.setAttribute('normal', new THREE.Float32BufferAttribute(B.nor, 3)); g.setAttribute('color', new THREE.Float32BufferAttribute(B.col, 3));
  if (B.uv.length) g.setAttribute('uv', new THREE.Float32BufferAttribute(B.uv, 2));
  const m = new THREE.Mesh(g, mat); m.castShadow = true; m.receiveShadow = true; grp.add(m); return m;
}
// billboards and neon: an atlas of 4 x 4 made-up adverts
let MT_ADS = null;
function mtAds() {
  if (MT_ADS) return MT_ADS;
  const cv = document.createElement('canvas'); cv.width = cv.height = 512; const x = cv.getContext('2d');
  const ads = [['SWEET SPOT', '#ff3d7f', '#ffd23d'], ['FORE!', '#1e88e5', '#ffffff'], ['EAGLE', '#111111', '#ffcc00'], ['BIRDIE', '#00c2a8', '#ffffff'], ['ゴルフ', '#e8323c', '#ffffff'], ['HOLE IN ONE', '#7b2ff7', '#f9f871'], ['イーグル', '#ff6a00', '#111111'], ['PAR 3', '#0b3d91', '#ff8fa3'],
    ['GOLF', '#ffea00', '#d81b60'], ['バーディー', '#00b0ff', '#ffffff'], ['NEON', '#ff1744', '#00e5ff'], ['FAIRWAY', '#2e7d32', '#ffffff'], ['スイート', '#f50057', '#ffff8d'], ['TEE TIME', '#212121', '#00e676'], ['ALBATROSS', '#6200ea', '#ffffff'], ['CADDIE', '#ff9100', '#212121']];
  ads.forEach(([t, bg, fg], i) => {
    const X = (i % 4) * 128, Y = ((i / 4) | 0) * 128, g = x.createLinearGradient(X, Y, X + 128, Y + 128); g.addColorStop(0, bg); g.addColorStop(1, '#000000');
    x.fillStyle = g; x.fillRect(X, Y, 128, 128); x.fillStyle = fg; x.globalAlpha = .25; x.beginPath(); x.arc(X + 96, Y + 30, 40, 0, TAU); x.fill(); x.globalAlpha = 1;
    x.font = `700 ${t.length > 7 ? 18 : 28}px Fredoka, sans-serif`; x.textAlign = 'center'; x.fillText(t, X + 64, Y + 74); x.fillRect(X + 20, Y + 90, 88, 4);
  });
  const t = new THREE.CanvasTexture(cv); return MT_ADS = t;
}

/* ---------------- drawing the city ---------------- */
function mtColOf(b, ST, k, r) {
  if (b.col != null && b.col >= 0) { const c = b.col; return (((c >> 8) & 15) * 17 << 16) | (((c >> 4) & 15) * 17 << 8) | ((c & 15) * 17); }
  const a = ST.cols[k] || ST.cols[ST.tex[0]]; return a[(hash2(b.id, 7, 11) * a.length) | 0];
}
function metroBuild(C, grp) {
  const def = C.def, D = C.mtD, ST = METRO_STYLE[def.city], r = mulberry32(def.seed * 7 + 3), texB = {}, P = mtBuf(), ADS = mtBuf();
  const bufFor = k => texB[k] || (texB[k] = mtBuf());
  const line = C.cityLine;
  for (const b of D.blds) {
    const n = b.P.length >> 1; if (n < 3) continue;
    const tall = b.h > 90 && ST.tall, k = tall ? ST.tall : ST.tex[(hash2(b.id, 3, 5) * ST.tex.length) | 0], col = mtColOf(b, ST, k, r), tile = MT_TILE[k], T = bufFor(k);
    const y0 = b.minh > .5 ? b.y0 : b.base - 2, y1 = b.roof ? b.y1 - .05 : b.y1; // (a roof in play: the ground is raised to it and covers it)
    let area = 0; for (let i = 0, j = n - 1; i < n; j = i++) area += (b.P[2 * j] - b.P[2 * i]) * (b.P[2 * j + 1] + b.P[2 * i + 1]);
    const sg = area > 0 ? 1 : -1; let u0 = 0;
    for (let i = 0, j = n - 1; i < n; j = i++) {
      const ax = b.P[2 * j], az = b.P[2 * j + 1], bx = b.P[2 * i], bz = b.P[2 * i + 1], L = Math.hypot(bx - ax, bz - az); if (L < .05) continue;
      const nx = sg * (bz - az) / L, nz = -sg * (bx - ax) / L;
      mtQuad(T, [ax, y0, az], [bx, y0, bz], [bx, y1, bz], [ax, y1, az], [nx, 0, nz], col, [[u0 / tile[0], 0], [(u0 + L) / tile[0], 0], [(u0 + L) / tile[0], (y1 - y0) / tile[1]], [u0 / tile[0], (y1 - y0) / tile[1]]]);
      u0 += L;
      // Times Square and Shibuya: adverts on the walls that face the hole
      if (def.neon && L > 7 && b.h > 12 && !b.roof) {
        const mx = (ax + bx) / 2, mz = (az + bz) / 2, q = polyQ(line, mx, mz, 70);
        if (q.d < 70) {
          const p = polyAt(line, q.along), tx = p[0] - mx, tz = p[1] - mz;
          if (tx * nx + tz * nz > .3 * Math.hypot(tx, tz) && r() < .8) {
            const w = Math.min(L * .8, 6 + r() * 12), hh = w * (.45 + r() * .5), yb = b.base + 5 + r() * Math.max(1, Math.min(b.h - hh - 4, 40)), t0 = .5 + (r() - .5) * (1 - w / L) * .9;
            const cx = ax + (bx - ax) * t0 + nx * .3, cz = az + (bz - az) * t0 + nz * .3, ex = (bx - ax) / L * w / 2, ez = (bz - az) / L * w / 2, j2 = (r() * 16) | 0, uu = (j2 % 4) / 4, vv = .75 - ((j2 / 4) | 0) / 4;
            mtQuad(ADS, [cx - ex, yb, cz - ez], [cx + ex, yb, cz + ez], [cx + ex, yb + hh, cz + ez], [cx - ex, yb + hh, cz - ez], [nx, 0, nz], 0xffffff, [[uu, vv], [uu + .25, vv], [uu + .25, vv + .25], [uu, vv + .25]]);
          }
        }
      }
    }
    // the roof (and the underside of a part held up off the ground)
    const pts = []; for (let t = 0; t < n; t++) pts.push(new THREE.Vector2(b.P[2 * t], b.P[2 * t + 1]));
    let tri; try { tri = THREE.ShapeUtils.triangulateShape(pts, []); } catch (e) { tri = []; }
    const rc = b.roof ? 0x8f8a82 : ST.roof;
    if (!b.roof) for (const [i0, i1, i2] of tri) {
      const A = [pts[i0].x, y1, pts[i0].y], Bv = [pts[i1].x, y1, pts[i1].y], Cv = [pts[i2].x, y1, pts[i2].y];
      mtTri(P, A, Bv, Cv, [0, 1, 0], rc);
      if (b.minh > .5) mtTri(P, [A[0], y0, A[2]], [Bv[0], y0, Bv[2]], [Cv[0], y0, Cv[2]], [0, -1, 0], 0x6a6560);
    }
    if (ST.mansard && b.h > 14 && b.h < 40 && n <= 8 && !b.roof && b.minh < .5) { // (Paris: a band of grey zinc along the top)
      for (let i = 0, j = n - 1; i < n; j = i++) { const ax = b.P[2 * j], az = b.P[2 * j + 1], bx = b.P[2 * i], bz = b.P[2 * i + 1], L = Math.hypot(bx - ax, bz - az); if (L < .05) continue; const nx = sg * (bz - az) / L * .08, nz = -sg * (bx - ax) / L * .08; mtQuad(P, [ax + nx, y1 - 3.2, az + nz], [bx + nx, y1 - 3.2, bz + nz], [bx + nx, y1, bz + nz], [ax + nx, y1, az + nz], [nx / .08, 0, nz / .08], 0x6f7a85); }
    }
  }
  for (const k in texB) mtMesh(grp, texB[k], new THREE.MeshLambertMaterial({ map: mtTex(k), vertexColors: true }));
  mtMesh(grp, P, new THREE.MeshLambertMaterial({ vertexColors: true }));
  const adm = mtMesh(grp, ADS, new THREE.MeshBasicMaterial({ map: mtAds(), side: THREE.DoubleSide })); if (adm) adm.castShadow = false;
  // the water: the rivers, canals and the sea, at their level
  const wm = new THREE.MeshPhongMaterial({ color: 0x7fb6c8, transparent: true, opacity: .9, shininess: 70, specular: 0xeefcff });
  for (const rings of D.water) {
    const outer = []; for (let t = 0; t < rings[0].length; t += 2) outer.push(new THREE.Vector2(rings[0][t], -rings[0][t + 1]));
    const sh = new THREE.Shape(outer);
    for (const R of rings.slice(1)) { const hp = []; for (let t = 0; t < R.length; t += 2) hp.push(new THREE.Vector2(R[t], -R[t + 1])); sh.holes.push(new THREE.Path(hp)); }
    const g = new THREE.ShapeGeometry(sh); g.rotateX(-Math.PI / 2); const m = new THREE.Mesh(g, wm); m.position.y = C.mtLevel; m.receiveShadow = true; grp.add(m); (W.waterMeshes = W.waterMeshes || []).push(m);
  }
  if (def.city === 'rio' && D.water.length) { const sea = new THREE.Mesh(new THREE.PlaneGeometry(9000, 9000), wm); sea.rotation.x = -Math.PI / 2; sea.position.set(0, C.mtLevel - .25, 0); grp.add(sea); }
  // the landmarks drawn as models, where they stand
  for (const { m, base } of C.mons) {
    const k = MT_MON[m.kind]; if (!k) continue;
    const g = k.build(m, C, r); g.position.set(m.x, m.y != null ? m.y : base, -m.f); g.rotation.y = (m.rot || 0) * DEG; g.scale.setScalar(m.s || 1);
    g.traverse(o => { if (o.isMesh) { o.castShadow = !m.far; o.receiveShadow = true; } }); grp.add(g);
  }
  mtStreet(C, grp, r);
}
function mtTri(B, a, b, c, n, col) {
  const e1 = [b[0] - a[0], b[1] - a[1], b[2] - a[2]], e2 = [c[0] - a[0], c[1] - a[1], c[2] - a[2]], cy = e1[2] * e2[0] - e1[0] * e2[2];
  if (cy * n[1] < 0) { const t = b; b = c; c = t; }
  _mc.set(col); for (const p of [a, b, c]) { B.pos.push(p[0], p[1], p[2]); B.nor.push(n[0], n[1], n[2]); B.col.push(_mc.r, _mc.g, _mc.b); }
}
// street lamps along the line of play, where it is street; cars parked along it
function mtStreet(C, grp, r) {
  const def = C.def, line = C.cityLine, lamp = instancer(grp, unitBox, 160), car = instancer(grp, unitBox, 300);
  const street = (x, z) => C.surf(x, z) === S.DEEP && !C.offRoof(x, z) && !C.boxHit(x, C.h(x, z) + .5, z, BOXQ) && C.wl(x, z) < C.h(x, z) - .1;
  if (C.roofs.length) { lamp.done(); car.done(); return; }
  const cc = { ny: [0xf6c431, 0xf6c431, 0x2b2b2e, 0xe8e8e8], london: [0x2b2b2e, 0xc8262b, 0xe8e8e8, 0x6a7580], paris: [0x3f5f8a, 0x2b2b2e, 0xe8e8e8, 0x8a2b2b], tokyo: [0x2b2b2e, 0xf2f2f2, 0x6a7580], ams: [0x6b8a5a, 0x2b2b2e, 0xe8e8e8], rio: [0xe2e2e2, 0xf2c94c, 0x2b2b2e] }[def.city];
  for (let s = 6; s < line.L; s += 7) {
    const p = polyAt(line, s), q = polyAt(line, Math.min(line.L, s + 1)), b = polyAt(line, Math.max(0, s - 1)); let tx = q[0] - b[0], tz = q[1] - b[1]; const tl = Math.hypot(tx, tz) || 1; tx /= tl; tz /= tl;
    const a = Math.atan2(tx, tz);
    for (const sd of [-1, 1]) {
      // the kerb: walk out from the line until the street ends
      let off = 0; for (let o = 6; o < 40; o += 1.5) { const x = p[0] - tz * sd * o, z = p[1] + tx * sd * o; if (C.boxHit(x, C.h(x, z) + .5, z, BOXQ) || C.wl(x, z) > C.h(x, z) - .1) break; off = o; }
      if (off < 9) continue;
      const lx = p[0] - tz * sd * (off - 1), lz = p[1] + tx * sd * (off - 1);
      if (s % 28 < 7 && street(lx, lz)) { const y = C.h(lx, lz); lamp.add(lx, y + 3.5, lz, .18, 7, .18, 0, 0x3a3f44); lamp.add(lx + tz * sd * .8, y + 7, lz - tx * sd * .8, .3, .18, 1.6, a + Math.PI / 2, 0x3a3f44); }
      const cx = p[0] - tz * sd * (off - 3.5), cz = p[1] + tx * sd * (off - 3.5);
      if (r() < .45 && street(cx, cz)) { const y = C.h(cx, cz), c = cc[(r() * cc.length) | 0]; car.add(cx, y + .65, cz, 1.85, .8, 4.5, a, c); car.add(cx, y + 1.3, cz, 1.6, .6, 2.4, a, 0x39424a); }
    }
  }
  lamp.done(); car.done();
}
const pick2 = (r, a) => a[(r() * a.length) | 0];

/* ---------------- the landmarks, at full size ---------------- */
const MT_MON = {};

/* ---------------- the landmarks ---------------- */
function mtG() { return new THREE.Group(); }
function mtB(g, w, h, d, col, x, y, z, ry) { const o = new THREE.Mesh(unitBox, typeof col === 'number' ? lambert(col) : col); o.scale.set(w, h, d); o.position.set(x || 0, (y || 0) + h / 2, z || 0); if (ry) o.rotation.y = ry; g.add(o); return o; }
function mtBeam(g, p, q, t, col) { // a square beam from p to q
  const dx = q[0] - p[0], dy = q[1] - p[1], dz = q[2] - p[2], L = Math.hypot(dx, dy, dz), o = new THREE.Mesh(unitBox, lambert(col));
  o.scale.set(t, t, L); o.position.set((p[0] + q[0]) / 2, (p[1] + q[1]) / 2, (p[2] + q[2]) / 2); o.lookAt(q[0], q[1], q[2]); g.add(o); return o;
}
function mtCyl(g, r0, r1, h, col, x, y, z, seg) { const o = new THREE.Mesh(new THREE.CylinderGeometry(r1, r0, h, seg || 12), lambert(col)); o.position.set(x || 0, (y || 0) + h / 2, z || 0); g.add(o); return o; }
function mtCone(g, r, h, col, x, y, z, seg, ry) { const o = new THREE.Mesh(new THREE.ConeGeometry(r, h, seg || 4), lambert(col)); o.position.set(x || 0, (y || 0) + h / 2, z || 0); o.rotation.y = ry != null ? ry : Math.PI / 4; g.add(o); return o; }
function mtSph(g, r, col, x, y, z, sx, sy, sz, emi) { const m = lambert(col); if (emi) m.emissive.setHex(emi); const o = new THREE.Mesh(new THREE.SphereGeometry(r, 18, 12), m); o.position.set(x || 0, y || 0, z || 0); o.scale.set(sx || 1, sy || 1, sz || 1); g.add(o); return o; }
// a lattice tower on four legs (the Eiffel Tower, Tokyo Tower): P = { b: half base, k1: half width at the first deck, y1, k2, y2, top, col, band }
function mtLattice(g, P) {
  const legs = [[1, 1], [1, -1], [-1, 1], [-1, -1]], col = i => P.band && i % 2 ? P.band : P.col;
  const seg = (y0, y1, k0, k1, t, n) => { for (let i = 0; i < n; i++) { const ya = y0 + (y1 - y0) * i / n, yb = y0 + (y1 - y0) * (i + 1) / n, ka = k0 + (k1 - k0) * i / n, kb = k0 + (k1 - k0) * (i + 1) / n; for (const [sx, sz] of legs) mtBeam(g, [sx * ka, ya, sz * ka], [sx * kb, yb, sz * kb], t * (1 - .35 * i / n), col(i)); } };
  seg(0, P.y1, P.b, P.k1, P.t0, 3);
  for (const [sx, sz] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) { // the arches between the legs
    const n = 9; let prev = null;
    for (let i = 0; i <= n; i++) { const u = i / n * 2 - 1, k = P.b * .78, y = P.y1 * (.55 + .4 * Math.sqrt(1 - u * u)), p = sx ? [sx * k, y, u * k] : [u * k, y, sz * k]; if (prev) mtBeam(g, prev, p, 1.1, P.col); prev = p; }
  }
  mtB(g, P.k1 * 2 + 6, 3, P.k1 * 2 + 6, P.deck || P.col, 0, P.y1, 0);
  seg(P.y1 + 3, P.y2, P.k1, P.k2, P.t0 * .55, 3);
  mtB(g, P.k2 * 2 + 4, 2.2, P.k2 * 2 + 4, P.deck || P.col, 0, P.y2, 0);
  seg(P.y2 + 2.2, P.top, P.k2, 1.2, P.t0 * .32, 4);
  mtB(g, 3.4, 5, 3.4, P.col, 0, P.top, 0); mtCyl(g, .5, .25, P.top * .14, P.band || P.col, 0, P.top + 5, 0, 6);
}
MT_MON.eiffel = { // 330 m: legs 125 m apart, the first floor at 57 m, the second at 116 m, the top at 276 m
  name: 'Off the Eiffel Tower!',
  build: () => { const g = mtG(); mtLattice(g, { b: 54, k1: 31, y1: 57, k2: 19, y2: 116, top: 276, t0: 8, col: 0x7d6650 }); return g; },
  cols: () => [[48, 48, 22, 22, -1, 42], [-48, 48, 22, 22, -1, 42], [48, -48, 22, 22, -1, 42], [-48, -48, 22, 22, -1, 42], [0, 0, 68, 68, 54, 61], [0, 0, 42, 42, 61, 116], [0, 0, 42, 42, 116, 119], [0, 0, 14, 14, 119, 300]]
};
MT_MON.tokyotower = { // 333 m: the main deck at 150 m, the top deck at 250 m
  name: 'Off Tokyo Tower!',
  build: () => { const g = mtG(); mtLattice(g, { b: 38, k1: 15, y1: 145, k2: 8, y2: 223, top: 290, t0: 7, col: 0xe8502c, band: 0xf2f0ea, deck: 0xdfe6ea }); return g; },
  cols: () => [[30, 30, 14, 14, -1, 70], [-30, 30, 14, 14, -1, 70], [30, -30, 14, 14, -1, 70], [-30, -30, 14, 14, -1, 70], [0, 0, 40, 40, 70, 150], [0, 0, 22, 22, 150, 225], [0, 0, 10, 10, 225, 330]]
};
MT_MON.arc = { name: 'Off the Arc de Triomphe!',
  build: () => {
    const g = mtG(), st = 0xe6dac2, dk = 0xd6c8ac;
    mtB(g, 15.2, 50, 22, st, -14.9, 0, 0); mtB(g, 15.2, 50, 22, st, 14.9, 0, 0); mtB(g, 14.6, 21, 22, st, 0, 29, 0);
    mtB(g, 47, 2.2, 24, dk, 0, 42, 0); mtB(g, 45, 6, 22, st, 0, 50, 0); mtB(g, 46, 1, 23, dk, 0, 56, 0);
    for (const sx of [-1, 1]) for (const sz of [-1, 1]) mtB(g, 3, 12, 1.2, dk, sx * 14.9, 6, sz * 11.4); // the sculpture groups on the piers
    const ring = new THREE.Mesh(new THREE.TorusGeometry(7.3, .9, 6, 20, Math.PI), lambert(dk)); ring.position.set(0, 29, 11.2); g.add(ring);
    return g;
  },
  cols: () => [[-14.9, 0, 15.2, 22, -1, 57], [14.9, 0, 15.2, 22, -1, 57], [0, 0, 14.6, 22, 29, 57]]
};
MT_MON.bigben = { name: 'Off Big Ben!',
  build: () => {
    const g = mtG(), st = 0xd9c58e, dk = 0xb79f64, roof = 0x3d4a52, face = lambert(0xfdfbf2); face.emissive.setHex(0x3a3a30);
    mtB(g, 12, 62, 12, st, 0, 0, 0); for (const sx of [-1, 1]) for (const sz of [-1, 1]) mtB(g, 1.2, 62, 1.2, dk, sx * 6, 0, sz * 6);
    mtB(g, 14, 14, 14, st, 0, 62, 0);
    for (const [x, z, ry] of [[0, 7.05, 0], [0, -7.05, Math.PI], [7.05, 0, Math.PI / 2], [-7.05, 0, -Math.PI / 2]]) { const c = new THREE.Mesh(new THREE.CircleGeometry(4.6, 24), face); c.position.set(x, 69, z); c.rotation.y = ry; g.add(c); const h = mtB(g, .3, 3.4, .1, 0x1a1a1a, x * 1.01, 68.6, z * 1.01, ry); h.rotation.z = .9; }
    mtB(g, 12, 8, 12, dk, 0, 76, 0); mtCone(g, 8.6, 22, roof, 0, 84, 0, 4); mtCyl(g, .3, .1, 6, 0xc9a94a, 0, 106, 0, 6);
    return g;
  },
  cols: () => [[0, 0, 14, 14, -1, 96]]
};
MT_MON.eye = {
  build: () => {
    const g = mtG(), w = lambert(0xf2f4f6), R = 60, hub = 68;
    const ring = new THREE.Mesh(new THREE.TorusGeometry(R, 1.3, 6, 72), w); ring.position.y = hub; g.add(ring);
    for (let i = 0; i < 20; i++) { const a = i / 20 * TAU; mtBeam(g, [0, hub, 0], [Math.cos(a) * R, hub + Math.sin(a) * R, 0], .35, 0xdfe4e8); }
    for (let i = 0; i < 32; i++) { const a = i / 32 * TAU; mtSph(g, 2.2, 0xbfe0f0, Math.cos(a) * (R + 2.5), hub + Math.sin(a) * (R + 2.5), 0, 1.5, .9, 1); }
    mtBeam(g, [0, hub, 0], [0, 0, 26], 2, 0xdfe4e8); mtBeam(g, [0, hub, 0], [0, 0, -26], 2, 0xdfe4e8); mtSph(g, 4, 0xdfe4e8, 0, hub, 0);
    return g;
  }
};
MT_MON.christ = {
  build: (m, C) => {
    const g = mtG(), w = 0xf2f0ea, s = mtG(); g.add(s); // (30 m on an 8 m pedestal, on the summit of Corcovado)
    mtB(s, 8, 8, 8, 0xd8d2c4, 0, 0, 0); mtCyl(s, 3.6, 2.4, 20, w, 0, 8, 0, 10); mtB(s, 4.6, 6, 3.4, w, 0, 25, 0); mtB(s, 28, 2.4, 2.2, w, 0, 27, 0); mtSph(s, 1.6, w, 0, 33, 0, 1, 1.15, 1);
    return g;
  },
  cols: () => [[0, 0, 8, 8, -1, 34]]
};
