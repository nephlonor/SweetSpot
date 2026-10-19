const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=swiftshader'] });
  const p = await b.newPage(); p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.addInitScript(() => localStorage.setItem('ssg-intro-seen', '1'));
  await p.route('**/three.min.js', r => r.fulfill({ path: __dirname + '/three.min.js', contentType: 'application/javascript' }));
  await p.goto('file:///home/user/SweetSpot/index.html'); await p.waitForTimeout(2000);
  console.log(await p.evaluate(() => {
    const out = [];
    for (const lip of [0, .006, .01, .014, .018, .025]) {
      CUP_LIP = lip; CUP_IN = CUP_RIM + lip + .03; CUP_OUT = CUP_RIM + lip + VIS_R + .08;
      const C = { cup: { x: 0, y: 0, z: 0 }, h: () => 0, grad: (x, z, o) => { o[0] = 0; o[1] = 0; return o; } };
      let n = 0, inn = 0, nb = 0, inb = 0, lt = 0, lin = 0;
      for (let bo = 0; bo <= CUP_RIM + VIS_R + .02; bo += .006) for (let v = .1; v <= 1.8; v += .025) {
        const x0 = -Math.sqrt(CUP_IN * CUP_IN - bo * bo) + .001, ev = [], q = cupZone(C, { flag: false }, x0, 0, bo, v, 0, 0, 0, [], ev, SURF[S.GREEN].mu, false, null);
        const lipIn = ev.some(e => e.type === 'lipin'), lipOut = ev.some(e => e.type === 'lip'); if (lipIn || lipOut) { lt++; if (lipIn) lin++; }
        n++; if (q.kind === 'in') inn++;
        if (bo > CUP_RIM * .6) { nb++; if (q.kind === 'in') inb++; } // the borderline ones: struck at the edge half of the hole
      }
      out.push(`lip ${lip}: on the lip ${lt}, lipped in ${lin} (${(100 * lin / lt).toFixed(1)}%) | holed ${inn}/${n} (${(100 * inn / n).toFixed(1)}%), edge putts ${inb}/${nb} (${(100 * inb / nb).toFixed(1)}%)`);
    }
    return out.join('\n');
  }));
  await b.close();
})();
