import { useState, useEffect, useCallback } from 'react';

// Hook para gestionar PWA
export const usePWA = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isInstalled, setIsInstalled] = useState(false);
  const [canInstall, setCanInstall] = useState(false);
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [swRegistration, setSwRegistration] = useState(null);
  const [updateAvailable, setUpdateAvailable] = useState(false);

  // Detectar estado de conexión
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Detectar si la app está instalada
  useEffect(() => {
    const checkInstalled = () => {
      // Verificar si se está ejecutando en modo standalone
      const isStandalone = window.matchMedia('(display-mode: standalone)').matches;
      const isInStandaloneMode = window.navigator.standalone === true;

      setIsInstalled(isStandalone || isInStandaloneMode);
    };

    checkInstalled();

    // Escuchar cambios en el modo de visualización
    const mediaQuery = window.matchMedia('(display-mode: standalone)');
    mediaQuery.addEventListener('change', checkInstalled);

    return () => {
      mediaQuery.removeEventListener('change', checkInstalled);
    };
  }, []);

  // Detectar si se puede instalar
  useEffect(() => {
    const handleBeforeInstallPrompt = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setCanInstall(true);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, []);

  // Registrar Service Worker
  useEffect(() => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js')
        .then((registration) => {
          setSwRegistration(registration);

          // Verificar actualizaciones
          registration.addEventListener('updatefound', () => {
            const newWorker = registration.installing;
            newWorker.addEventListener('statechange', () => {
              if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                setUpdateAvailable(true);
              }
            });
          });

          // Escuchar mensajes del Service Worker
          navigator.serviceWorker.addEventListener('message', (event) => {
            const { type, payload } = event.data;

            switch (type) {
              case 'UPDATE_AVAILABLE':
                setUpdateAvailable(true);
                break;
              case 'OFFLINE_MODE':
                setIsOnline(false);
                break;
              case 'ONLINE_MODE':
                setIsOnline(true);
                break;
              default:
                console.log('Mensaje del Service Worker:', type, payload);
            }
          });
        })
        .catch((error) => {
          console.error('Error registrando Service Worker:', error);
        });
    }
  }, []);

  // Función para instalar la app
  const installApp = useCallback(async () => {
    if (!deferredPrompt) {
      console.log('No se puede instalar la app');
      return false;
    }

    try {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;

      if (outcome === 'accepted') {
        console.log('Usuario aceptó instalar la app');
        setCanInstall(false);
        setDeferredPrompt(null);
        return true;
      } else {
        console.log('Usuario rechazó instalar la app');
        return false;
      }
    } catch (error) {
      console.error('Error instalando la app:', error);
      return false;
    }
  }, [deferredPrompt]);

  // Función para actualizar la app
  const updateApp = useCallback(() => {
    if (swRegistration && swRegistration.waiting) {
      swRegistration.waiting.postMessage({ type: 'SKIP_WAITING' });
      window.location.reload();
    }
  }, [swRegistration]);

  // Función para limpiar cache
  const clearCache = useCallback(async () => {
    if (swRegistration) {
      try {
        await swRegistration.unregister();
        if ('caches' in window) {
          const cacheNames = await caches.keys();
          await Promise.all(
            cacheNames.map(cacheName => caches.delete(cacheName))
          );
        }
        window.location.reload();
        return true;
      } catch (error) {
        console.error('Error limpiando cache:', error);
        return false;
      }
    }
    return false;
  }, [swRegistration]);

  // Función para cachear URLs específicas
  const cacheUrls = useCallback(async (urls) => {
    if (swRegistration && swRegistration.active) {
      return new Promise((resolve, reject) => {
        const messageChannel = new MessageChannel();

        messageChannel.port1.onmessage = (event) => {
          if (event.data.success) {
            resolve(true);
          } else {
            reject(new Error(event.data.error));
          }
        };

        swRegistration.active.postMessage(
          { type: 'CACHE_URLS', payload: { urls } },
          [messageChannel.port2]
        );
      });
    }
    return false;
  }, [swRegistration]);

  // Función para obtener información del cache
  const getCacheInfo = useCallback(async () => {
    if ('caches' in window) {
      const cacheNames = await caches.keys();
      const cacheInfo = await Promise.all(
        cacheNames.map(async (cacheName) => {
          const cache = await caches.open(cacheName);
          const keys = await cache.keys();
          return {
            name: cacheName,
            size: keys.length,
            urls: keys.map(request => request.url)
          };
        })
      );
      return cacheInfo;
    }
    return [];
  }, []);

  // Función para sincronizar en segundo plano
  const syncInBackground = useCallback(async (tag = 'background-sync') => {
    if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
      try {
        await navigator.serviceWorker.ready;
        await navigator.serviceWorker.register('/sw.js');
        const registration = await navigator.serviceWorker.ready;
        await registration.sync.register(tag);
        return true;
      } catch (error) {
        console.error('Error registrando sincronización en segundo plano:', error);
        return false;
      }
    }
    return false;
  }, []);

  // Función para suscribirse a notificaciones push
  const subscribeToPush = useCallback(async () => {
    if ('serviceWorker' in navigator && 'PushManager' in window) {
      try {
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: process.env.REACT_APP_VAPID_PUBLIC_KEY
        });
        return subscription;
      } catch (error) {
        console.error('Error suscribiéndose a notificaciones push:', error);
        return null;
      }
    }
    return null;
  }, []);

  // Función para cancelar suscripción a notificaciones push
  const unsubscribeFromPush = useCallback(async () => {
    if ('serviceWorker' in navigator && 'PushManager' in window) {
      try {
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.getSubscription();
        if (subscription) {
          await subscription.unsubscribe();
          return true;
        }
        return false;
      } catch (error) {
        console.error('Error cancelando suscripción a notificaciones push:', error);
        return false;
      }
    }
    return false;
  }, []);

  // Función para verificar permisos de notificación
  const checkNotificationPermission = useCallback(() => {
    if ('Notification' in window) {
      return Notification.permission;
    }
    return 'denied';
  }, []);

  // Función para solicitar permisos de notificación
  const requestNotificationPermission = useCallback(async () => {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission();
      return permission;
    }
    return 'denied';
  }, []);

  // Función para mostrar notificación local
  const showNotification = useCallback((title, options = {}) => {
    if ('Notification' in window && Notification.permission === 'granted') {
      const notification = new Notification(title, {
        icon: '/icons/icon-192x192.png',
        badge: '/icons/badge-72x72.png',
        tag: 'postventa-notification',
        ...options
      });

      notification.onclick = () => {
        window.focus();
        notification.close();
      };

      return notification;
    }
    return null;
  }, []);

  // Función para obtener información del dispositivo
  const getDeviceInfo = useCallback(() => {
    return {
      userAgent: navigator.userAgent,
      platform: navigator.platform,
      language: navigator.language,
      onLine: navigator.onLine,
      cookieEnabled: navigator.cookieEnabled,
      doNotTrack: navigator.doNotTrack,
      hardwareConcurrency: navigator.hardwareConcurrency,
      maxTouchPoints: navigator.maxTouchPoints,
      deviceMemory: navigator.deviceMemory,
      connection: navigator.connection ? {
        effectiveType: navigator.connection.effectiveType,
        downlink: navigator.connection.downlink,
        rtt: navigator.connection.rtt,
        saveData: navigator.connection.saveData
      } : null
    };
  }, []);

  // Función para detectar si es móvil
  const isMobile = useCallback(() => {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  }, []);

  // Función para detectar si es iOS
  const isIOS = useCallback(() => {
    return /iPad|iPhone|iPod/.test(navigator.userAgent);
  }, []);

  // Función para detectar si es Android
  const isAndroid = useCallback(() => {
    return /Android/.test(navigator.userAgent);
  }, []);

  // Función para compartir contenido
  const shareContent = useCallback(async (data) => {
    if (navigator.share) {
      try {
        await navigator.share(data);
        return true;
      } catch (error) {
        console.error('Error compartiendo contenido:', error);
        return false;
      }
    }
    return false;
  }, []);

  // Función para copiar al portapapeles
  const copyToClipboard = useCallback(async (text) => {
    if (navigator.clipboard) {
      try {
        await navigator.clipboard.writeText(text);
        return true;
      } catch (error) {
        console.error('Error copiando al portapapeles:', error);
        return false;
      }
    }
    return false;
  }, []);

  // Función para leer del portapapeles
  const readFromClipboard = useCallback(async () => {
    if (navigator.clipboard) {
      try {
        const text = await navigator.clipboard.readText();
        return text;
      } catch (error) {
        console.error('Error leyendo del portapapeles:', error);
        return null;
      }
    }
    return null;
  }, []);

  return {
    // Estado
    isOnline,
    isInstalled,
    canInstall,
    updateAvailable,

    // Funciones de instalación
    installApp,
    updateApp,

    // Funciones de cache
    clearCache,
    cacheUrls,
    getCacheInfo,

    // Funciones de sincronización
    syncInBackground,

    // Funciones de notificaciones
    subscribeToPush,
    unsubscribeFromPush,
    checkNotificationPermission,
    requestNotificationPermission,
    showNotification,

    // Funciones de dispositivo
    getDeviceInfo,
    isMobile,
    isIOS,
    isAndroid,

    // Funciones de compartir
    shareContent,
    copyToClipboard,
    readFromClipboard,

    // Service Worker
    swRegistration
  };
};

// Hook para gestionar notificaciones
export const useNotifications = () => {
  const [permission, setPermission] = useState(Notification.permission);
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    if ('Notification' in window) {
      setPermission(Notification.permission);
    }
  }, []);

  const requestPermission = useCallback(async () => {
    if ('Notification' in window) {
      const newPermission = await Notification.requestPermission();
      setPermission(newPermission);
      return newPermission;
    }
    return 'denied';
  }, []);

  const showNotification = useCallback((title, options = {}) => {
    if (permission === 'granted') {
      const notification = new Notification(title, {
        icon: '/icons/icon-192x192.png',
        badge: '/icons/badge-72x72.png',
        tag: 'postventa-notification',
        ...options
      });

      setNotifications(prev => [...prev, notification]);

      notification.onclose = () => {
        setNotifications(prev => prev.filter(n => n !== notification));
      };

      return notification;
    }
    return null;
  }, [permission]);

  const clearNotifications = useCallback(() => {
    notifications.forEach(notification => notification.close());
    setNotifications([]);
  }, [notifications]);

  return {
    permission,
    notifications,
    requestPermission,
    showNotification,
    clearNotifications
  };
};

// Hook para gestionar estado offline
export const useOffline = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [offlineQueue, setOfflineQueue] = useState([]);

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      // Procesar cola offline cuando vuelva la conexión
      processOfflineQueue();
    };

    const handleOffline = () => {
      setIsOnline(false);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const addToOfflineQueue = useCallback((action) => {
    setOfflineQueue(prev => [...prev, { ...action, timestamp: Date.now() }]);
  }, []);

  const processOfflineQueue = useCallback(async () => {
    if (offlineQueue.length > 0) {
      console.log('Procesando cola offline:', offlineQueue.length, 'elementos');

      for (const action of offlineQueue) {
        try {
          // Ejecutar acción
          await action.execute();
        } catch (error) {
          console.error('Error procesando acción offline:', error);
        }
      }

      setOfflineQueue([]);
    }
  }, [offlineQueue]);

  const clearOfflineQueue = useCallback(() => {
    setOfflineQueue([]);
  }, []);

  return {
    isOnline,
    offlineQueue,
    addToOfflineQueue,
    processOfflineQueue,
    clearOfflineQueue
  };
};
