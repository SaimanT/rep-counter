// Offline support: serve from network when possible, fall back to cache.
const CACHE = 'rep-counter-a1d287c0';
const FILES = [
  './',
  'index.html',
  'app.css',
  'app.js',
  'icon.svg',
  'icon-192.png',
  'icon-512.png',
  'manifest.webmanifest',
  'ru/manifest.webmanifest',
  'push-up-counter/',
  'squat-counter/',
  'pull-up-counter/',
  'sit-up-counter/',
  'burpee-counter/',
  'lunge-counter/',
  'ru/',
  'ru/otzhimaniya/',
  'ru/prisedaniya/',
  'ru/podtyagivaniya/',
  'ru/press/',
  'ru/berpi/',
  'ru/vypady/',
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    fetch(e.request)
      .then(res => {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(e.request, copy));
        return res;
      })
      .catch(() => caches.match(e.request, { ignoreSearch: true }))
  );
});
