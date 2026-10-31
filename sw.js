// Offline cache. __BUILD__ is stamped at deploy time.
const V = '__BUILD__', SHELL = 'ssg-shell-' + V, LIB = 'ssg-lib';
const PRE = ['./', 'index.html', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png', 'apple-touch-icon.png', 'swing-poster.jpg', 'splash.jpg', 'logo.png'];
self.addEventListener('install', e => {
  e.waitUntil(caches.open(SHELL).then(c => c.addAll(PRE)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('ssg-shell-') && k !== SHELL).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const r = e.request, u = new URL(r.url);
  if (r.method !== 'GET' || r.headers.has('range')) return;
  if (u.origin === location.origin) {
    if (u.pathname.endsWith('version.txt') || u.pathname.endsWith('.mp4')) return;
    if (r.mode === 'navigate' || u.pathname.endsWith('index.html')) {
      e.respondWith(fetch(r).then(res => { const cp = res.clone(); caches.open(SHELL).then(c => c.put('index.html', cp)); return res; }).catch(() => caches.match('index.html')));
      return;
    }
    e.respondWith(caches.open(SHELL).then(c => c.match(r).then(h => h || fetch(r).then(res => { if (res.ok) c.put(r, res.clone()); return res; }))));
    return;
  }
  if (u.hostname === 'cdnjs.cloudflare.com' || u.hostname === 'fonts.googleapis.com' || u.hostname === 'fonts.gstatic.com') {
    e.respondWith(caches.open(LIB).then(c => c.match(r).then(h => {
      const f = fetch(r).then(res => { if (res.ok || res.type === 'opaque') c.put(r, res.clone()); return res; }).catch(() => h);
      return h || f;
    })));
  }
});
