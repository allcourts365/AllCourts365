// Service Worker for AllCourts365 PWA
const CACHE_NAME = 'allcourts365-v2';
const PRECACHE_ASSETS = [
  '/',
  '/offline/',
  '/manifest.json',
  '/static/css/style.css?v=1.2',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png',
  '/static/icons/apple-touch-icon.png'
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return Promise.allSettled(
        PRECACHE_ASSETS.map((url) => cache.add(url).catch((err) => {
          // Precache is best-effort to avoid install failure on dynamic/auth paths
          console.debug('Precache item skipped:', url, err);
        }))
      );
    })
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    Promise.all([
      self.clients.claim(),
      caches.keys().then((keys) => {
        return Promise.all(
          keys.map((key) => {
            if (key !== CACHE_NAME) {
              return caches.delete(key);
            }
          })
        );
      })
    ])
  );
});

// Network-first strategy for GET requests; bypass non-GET and sensitive endpoints
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') {
    return;
  }

  const url = new URL(event.request.url);

  // Skip Django admin, ckeditor, authentication or API endpoints that require always live data
  if (
    url.pathname.startsWith('/admin/') ||
    url.pathname.startsWith('/ckeditor/') ||
    url.pathname.startsWith('/accounts/') ||
    url.pathname.startsWith('/api/')
  ) {
    return;
  }

  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        // Cache static files, manifest and offline template
        if (
          networkResponse &&
          networkResponse.status === 200 &&
          (url.pathname.startsWith('/static/') || url.pathname === '/manifest.json' || url.pathname === '/offline/')
        ) {
          const responseClone = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseClone);
          });
        }
        return networkResponse;
      })
      .catch(() => {
        // Fallback to cache if network is offline
        return caches.match(event.request).then((cachedResponse) => {
          if (cachedResponse) {
            return cachedResponse;
          }
          if (event.request.headers.get('accept')?.includes('text/html')) {
            return caches.match('/offline/');
          }
        });
      })
  );
});
