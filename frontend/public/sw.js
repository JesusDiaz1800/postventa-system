// Service Worker para el Sistema de Postventa
// Maneja el cache de recursos estáticos y evita errores con esquemas no compatibles

const CACHE_NAME = 'postventa-system-v1';
const urlsToCache = [
  '/',
  '/static/css/',
  '/static/js/',
  '/manifest.json'
];

// Instalación del Service Worker
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Service Worker: Cache abierto');
        return cache.addAll(urlsToCache);
      })
  );
});

// Activación del Service Worker
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Service Worker: Eliminando cache antiguo', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Interceptación de solicitudes
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  
  // Ignorar solicitudes con esquemas no compatibles
  if (url.protocol === 'chrome-extension:' || 
      url.protocol === 'moz-extension:' || 
      url.protocol === 'data:' ||
      url.protocol === 'blob:' ||
      url.hostname === 'localhost' && url.port === '3001') {
    return;
  }

  // Solo cachear solicitudes GET
  if (event.request.method !== 'GET') {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Si está en cache, devolverlo
        if (response) {
          return response;
        }

        // Si no está en cache, hacer fetch y cachear
        return fetch(event.request)
          .then((fetchResponse) => {
            // Verificar que la respuesta sea válida
            if (!fetchResponse || fetchResponse.status !== 200 || fetchResponse.type !== 'basic') {
              return fetchResponse;
            }

            // Clonar la respuesta
            const responseToCache = fetchResponse.clone();

            caches.open(CACHE_NAME)
              .then((cache) => {
                cache.put(event.request, responseToCache);
              });

            return fetchResponse;
          })
          .catch((error) => {
            console.log('Service Worker: Error en fetch', error);
            // En caso de error, devolver una respuesta por defecto si es posible
            if (event.request.destination === 'document') {
              return caches.match('/');
            }
          });
      })
  );
});
