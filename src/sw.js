// Service worker: caches the app on install, and each game's data and sprites the first time you open that game,
// so the planner works offline for the games you use. build_site.py fills in VERSION and PRECACHE.
const VERSION = '__VERSION__';
const PRECACHE = __PRECACHE__;
const CACHE = `living-dex-${VERSION}`;
const FONT_HOSTS = ['fonts.googleapis.com', 'fonts.gstatic.com'];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE).then((c) => c.addAll(PRECACHE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k.startsWith('living-dex-') && k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin === self.location.origin) {
    // cache first: every file is versioned by the cache name
    event.respondWith(
      caches.match(req, { ignoreSearch: true }).then((hit) => hit || fetch(req).then((res) => {
        if (res.ok) { const copy = res.clone(); caches.open(CACHE).then((c) => c.put(req, copy)); }
        return res;
      })),
    );
  } else if (FONT_HOSTS.includes(url.hostname)) {
    // fonts: serve the cached copy, refresh it in the background
    event.respondWith(
      caches.open(CACHE).then((c) => c.match(req).then((hit) => {
        const update = fetch(req).then((res) => { if (res.ok || res.type === 'opaque') c.put(req, res.clone()); return res; }).catch(() => hit);
        return hit || update;
      })),
    );
  }
});
