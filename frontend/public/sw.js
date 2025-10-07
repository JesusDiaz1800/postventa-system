const CACHE_NAME = 'postventa-system-v1.0.1';
const STATIC_CACHE_NAME = 'postventa-static-v1.0.1';
const DYNAMIC_CACHE_NAME = 'postventa-dynamic-v1.0.1';

// Archivos estáticos para cachear
const STATIC_FILES = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js',
  '/manifest.json',
  '/icons/app.svg',
  '/offline.html'
];

// Rutas que deben ser cacheadas dinámicamente
const DYNAMIC_ROUTES = [
  // No cache for authenticated API calls to avoid HTTPS/http issues in dev
  // '/api/',
  '/incidents/',
  '/documents/',
  '/reports/',
  '/dashboard/'
];

// Instalar Service Worker
self.addEventListener('install', (event) => {
  console.log('Service Worker: Instalando...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE_NAME)
      .then((cache) => {
        console.log('Service Worker: Cacheando archivos estáticos');
        return cache.addAll(STATIC_FILES);
      })
      .then(() => {
        console.log('Service Worker: Instalación completada');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('Service Worker: Error en la instalación', error);
      })
  );
});

// Activar Service Worker
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activando...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE_NAME && cacheName !== DYNAMIC_CACHE_NAME) {
            console.log('Service Worker: Eliminando cache antiguo', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
      .then(() => {
        console.log('Service Worker: Activación completada');
        return self.clients.claim();
      })
  );
});

// Interceptar peticiones
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Solo interceptar peticiones HTTP/HTTPS
  if (url.protocol !== 'http:' && url.protocol !== 'https:') {
    return;
  }
  
  // Estrategia para archivos estáticos
  if (STATIC_FILES.includes(url.pathname)) {
    event.respondWith(
      caches.match(request)
        .then((response) => {
          if (response) {
            return response;
          }
          return fetch(request);
        })
    );
    return;
  }

  // Estrategia para rutas dinámicas
  if (DYNAMIC_ROUTES.some(route => url.pathname.startsWith(route))) {
    event.respondWith(
      caches.open(DYNAMIC_CACHE_NAME)
        .then((cache) => {
          return cache.match(request)
            .then((response) => {
              if (response) {
                // Devolver respuesta cacheada y actualizar en segundo plano
                fetch(request)
                  .then((fetchResponse) => {
                    if (fetchResponse.status === 200) {
                      cache.put(request, fetchResponse.clone());
                    }
                  })
                  .catch(() => {
                    // Ignorar errores de actualización en segundo plano
                  });
                return response;
              }
              
              // Si no hay respuesta cacheada, hacer petición a la red
              return fetch(request)
                .then((fetchResponse) => {
                  if (fetchResponse.status === 200) {
                    cache.put(request, fetchResponse.clone());
                  }
                  return fetchResponse;
                })
                .catch(() => {
                  // Si falla la red, devolver página offline
                  if (request.destination === 'document') {
                    return caches.match('/offline.html');
                  }
                  throw new Error('Sin conexión');
                });
            });
        })
    );
    return;
  }

  // Estrategia por defecto: Network First
  event.respondWith(
    fetch(request)
      .then((response) => {
        // Si es una respuesta exitosa, cachearla
        if (response.status === 200 && request.method === 'GET') {
          const responseClone = response.clone();
          caches.open(DYNAMIC_CACHE_NAME)
            .then((cache) => {
              cache.put(request, responseClone);
            });
        }
        return response;
      })
      .catch(() => {
        // Si falla la red, intentar devolver desde cache
        return caches.match(request)
          .then((response) => {
        if (response) {
          return response;
        }
            // Si no hay respuesta cacheada y es una página, devolver offline
            if (request.destination === 'document') {
              return caches.match('/offline.html');
            }
            throw new Error('Sin conexión');
          });
      })
  );
});

// Manejar mensajes del cliente
self.addEventListener('message', (event) => {
  const { type, payload } = event.data;
  
  switch (type) {
    case 'SKIP_WAITING':
      self.skipWaiting();
      break;
      
    case 'GET_VERSION':
      event.ports[0].postMessage({ version: CACHE_NAME });
      break;
      
    case 'CLEAR_CACHE':
      caches.keys()
        .then((cacheNames) => {
          return Promise.all(
            cacheNames.map((cacheName) => {
              return caches.delete(cacheName);
            })
          );
        })
        .then(() => {
          event.ports[0].postMessage({ success: true });
        })
        .catch((error) => {
          event.ports[0].postMessage({ success: false, error: error.message });
        });
      break;
      
    case 'CACHE_URLS':
      const urlsToCache = payload.urls;
      caches.open(DYNAMIC_CACHE_NAME)
              .then((cache) => {
          return Promise.all(
            urlsToCache.map((url) => {
              return fetch(url)
                .then((response) => {
                  if (response.status === 200) {
                    return cache.put(url, response);
                  }
                })
                .catch(() => {
                  // Ignorar errores de URLs individuales
                });
            })
          );
        })
        .then(() => {
          event.ports[0].postMessage({ success: true });
          })
          .catch((error) => {
          event.ports[0].postMessage({ success: false, error: error.message });
        });
      break;
      
    default:
      console.log('Service Worker: Mensaje desconocido', type);
  }
});

// Manejar notificaciones push
self.addEventListener('push', (event) => {
  console.log('Service Worker: Push recibido');
  
  let notificationData = {
    title: 'Sistema de Postventa',
    body: 'Tienes una nueva notificación',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/badge-72x72.png',
    tag: 'postventa-notification',
    requireInteraction: true,
    actions: [
      {
        action: 'view',
        title: 'Ver',
        icon: '/icons/view-icon.png'
      },
      {
        action: 'dismiss',
        title: 'Descartar',
        icon: '/icons/dismiss-icon.png'
      }
    ]
  };
  
  if (event.data) {
    try {
      const data = event.data.json();
      notificationData = { ...notificationData, ...data };
    } catch (error) {
      console.error('Service Worker: Error parseando datos push', error);
    }
  }
  
  event.waitUntil(
    self.registration.showNotification(notificationData.title, notificationData)
  );
});

// Manejar clics en notificaciones
self.addEventListener('notificationclick', (event) => {
  console.log('Service Worker: Click en notificación');
  
  event.notification.close();
  
  const action = event.action;
  
  if (action === 'dismiss') {
    return;
  }
  
  const urlToOpen = event.notification.data?.url || '/';
  
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then((clientList) => {
        // Buscar si ya hay una ventana abierta
        for (const client of clientList) {
          if (client.url.includes(urlToOpen) && 'focus' in client) {
            return client.focus();
          }
        }
        
        // Si no hay ventana abierta, abrir una nueva
        if (clients.openWindow) {
          return clients.openWindow(urlToOpen);
        }
      })
  );
});

// Manejar cierre de notificaciones
self.addEventListener('notificationclose', (event) => {
  console.log('Service Worker: Notificación cerrada');
  
  // Opcional: Enviar evento de analytics
  if (event.notification.data?.analytics) {
    // Enviar evento de analytics
  }
});

// Manejar errores del Service Worker
self.addEventListener('error', (event) => {
  console.error('Service Worker: Error', event.error);
});

// Manejar promesas rechazadas
self.addEventListener('unhandledrejection', (event) => {
  console.error('Service Worker: Promesa rechazada', event.reason);
});

// Sincronización en segundo plano
self.addEventListener('sync', (event) => {
  console.log('Service Worker: Sincronización en segundo plano', event.tag);
  
  switch (event.tag) {
    case 'background-sync':
      event.waitUntil(doBackgroundSync());
      break;
      
    case 'incident-sync':
      event.waitUntil(syncIncidents());
      break;
      
    case 'document-sync':
      event.waitUntil(syncDocuments());
      break;
      
    default:
      console.log('Service Worker: Sincronización desconocida', event.tag);
  }
});

// Funciones de sincronización
async function doBackgroundSync() {
  try {
    console.log('Service Worker: Ejecutando sincronización en segundo plano');
    
    // Sincronizar datos pendientes
    const pendingData = await getPendingData();
    
    for (const data of pendingData) {
      try {
        await syncData(data);
        await markAsSynced(data.id);
      } catch (error) {
        console.error('Service Worker: Error sincronizando dato', error);
      }
    }
    
    console.log('Service Worker: Sincronización completada');
  } catch (error) {
    console.error('Service Worker: Error en sincronización', error);
  }
}

async function syncIncidents() {
  try {
    console.log('Service Worker: Sincronizando incidentes');
    
    // Implementar lógica de sincronización de incidentes
    const incidents = await getPendingIncidents();
    
    for (const incident of incidents) {
      try {
        await syncIncident(incident);
        await markIncidentAsSynced(incident.id);
      } catch (error) {
        console.error('Service Worker: Error sincronizando incidente', error);
      }
    }
  } catch (error) {
    console.error('Service Worker: Error en sincronización de incidentes', error);
  }
}

async function syncDocuments() {
  try {
    console.log('Service Worker: Sincronizando documentos');
    
    // Implementar lógica de sincronización de documentos
    const documents = await getPendingDocuments();
    
    for (const document of documents) {
      try {
        await syncDocument(document);
        await markDocumentAsSynced(document.id);
      } catch (error) {
        console.error('Service Worker: Error sincronizando documento', error);
      }
    }
  } catch (error) {
    console.error('Service Worker: Error en sincronización de documentos', error);
  }
}

// Funciones auxiliares (implementar según necesidades)
async function getPendingData() {
  // Implementar lógica para obtener datos pendientes
  return [];
}

async function syncData(data) {
  // Implementar lógica para sincronizar datos
  return Promise.resolve();
}

async function markAsSynced(id) {
  // Implementar lógica para marcar como sincronizado
  return Promise.resolve();
}

async function getPendingIncidents() {
  // Implementar lógica para obtener incidentes pendientes
  return [];
}

async function syncIncident(incident) {
  // Implementar lógica para sincronizar incidente
  return Promise.resolve();
}

async function markIncidentAsSynced(id) {
  // Implementar lógica para marcar incidente como sincronizado
  return Promise.resolve();
}

async function getPendingDocuments() {
  // Implementar lógica para obtener documentos pendientes
  return [];
}

async function syncDocument(document) {
  // Implementar lógica para sincronizar documento
  return Promise.resolve();
}

async function markDocumentAsSynced(id) {
  // Implementar lógica para marcar documento como sincronizado
  return Promise.resolve();
}