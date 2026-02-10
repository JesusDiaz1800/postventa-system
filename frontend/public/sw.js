const CACHE_NAME = 'postventa-v2';  // Incrementar versión para forzar actualización
const urlsToCache = [
    '/',
    '/index.html',
    '/manifest.json',
    '/icons/app.svg',
    '/offline.html'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('[SW] Cache abierto');
                return cache.addAll(urlsToCache).catch(err => {
                    console.warn('[SW] No se pudieron cachear algunos recursos:', err);
                });
            })
    );
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('[SW] Eliminando caché antigua:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

self.addEventListener('fetch', (event) => {
    // Ignorar peticiones que no sean GET
    if (event.request.method !== 'GET') return;

    // Ignorar WebSocket y extensiones de Chrome
    if (event.request.url.startsWith('ws://') ||
        event.request.url.startsWith('wss://') ||
        event.request.url.includes('chrome-extension://')) {
        return;
    }

    event.respondWith(
        // Estrategia: Network First, fallback a Cache
        fetch(event.request)
            .then((response) => {
                // Si la respuesta es válida, cachearla
                if (response && response.status === 200) {
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, responseClone);
                    });
                }
                return response;
            })
            .catch(() => {
                // Si falla el fetch, buscar en caché
                return caches.match(event.request).then((cachedResponse) => {
                    if (cachedResponse) {
                        return cachedResponse;
                    }
                    // Si es navegación y no hay caché, mostrar página offline
                    if (event.request.mode === 'navigate') {
                        return caches.match('/offline.html');
                    }
                    // Para otros recursos, retornar respuesta vacía válida
                    return new Response('', { status: 503, statusText: 'Service Unavailable' });
                });
            })
    );
});

// Manejador de mensajes para evitar "Uncaught (in promise) Error: A listener indicated an asynchronous response..."
// Esto ocurre cuando una extensión o el navegador envía un mensaje y el SW no responde o cierra el canal.
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    // Responder para mantener el canal abierto si es necesario, o simplemente no hacer nada pero capturar el evento.
    // En muchos casos, solo tener el listener evita el error no controlado.
});
