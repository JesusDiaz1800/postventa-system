import { useState, useCallback, useMemo, useEffect } from 'react';

/**
 * Hook personalizado para optimizaciones de rendimiento
 * Proporciona funcionalidades para mejorar la carga y rendimiento de la aplicación
 */
export const usePerformanceOptimization = () => {
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [optimizationHistory, setOptimizationHistory] = useState([]);
  const [cacheSize, setCacheSize] = useState(0);
  const [memoryUsage, setMemoryUsage] = useState(0);

  // Configuraciones de optimización
  const optimizationConfig = useMemo(() => ({
    lazyLoading: {
      enabled: true,
      threshold: 0.1, // Cargar cuando el elemento esté 10% visible
      rootMargin: '50px'
    },
    imageCompression: {
      enabled: true,
      quality: 0.8,
      maxWidth: 1920,
      maxHeight: 1080
    },
    virtualScrolling: {
      enabled: true,
      itemHeight: 100,
      overscan: 5
    },
    caching: {
      enabled: true,
      maxAge: 5 * 60 * 1000, // 5 minutos
      maxSize: 50 * 1024 * 1024 // 50MB
    }
  }), []);

  // Optimización de carga diferida
  const enableLazyLoading = useCallback((elements, callback) => {
    if (!window.IntersectionObserver) {
      // Fallback para navegadores que no soportan IntersectionObserver
      elements.forEach(callback);
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            callback(entry.target);
            observer.unobserve(entry.target);
          }
        });
      },
      {
        threshold: optimizationConfig.lazyLoading.threshold,
        rootMargin: optimizationConfig.lazyLoading.rootMargin
      }
    );

    elements.forEach((element) => {
      if (element) observer.observe(element);
    });

    return () => observer.disconnect();
  }, [optimizationConfig.lazyLoading]);

  // Compresión de imágenes
  const compressImage = useCallback((file, options = {}) => {
    return new Promise((resolve, reject) => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const img = new Image();

      img.onload = () => {
        const { maxWidth = 1920, maxHeight = 1080, quality = 0.8 } = options;
        
        // Calcular nuevas dimensiones manteniendo la proporción
        let { width, height } = img;
        if (width > maxWidth || height > maxHeight) {
          const ratio = Math.min(maxWidth / width, maxHeight / height);
          width *= ratio;
          height *= ratio;
        }

        canvas.width = width;
        canvas.height = height;

        // Dibujar imagen redimensionada
        ctx.drawImage(img, 0, 0, width, height);

        // Convertir a blob con compresión
        canvas.toBlob(
          (blob) => {
            if (blob) {
              resolve(blob);
            } else {
              reject(new Error('Error al comprimir la imagen'));
            }
          },
          'image/jpeg',
          quality
        );
      };

      img.onerror = () => reject(new Error('Error al cargar la imagen'));
      img.src = URL.createObjectURL(file);
    });
  }, []);

  // Optimización de caché
  const optimizeCache = useCallback(async () => {
    setIsOptimizing(true);
    
    try {
      // Limpiar caché del navegador
      if ('caches' in window) {
        const cacheNames = await caches.keys();
        await Promise.all(
          cacheNames.map(cacheName => caches.delete(cacheName))
        );
      }

      // Limpiar localStorage de elementos antiguos
      const now = Date.now();
      const maxAge = optimizationConfig.caching.maxAge;
      
      Object.keys(localStorage).forEach(key => {
        try {
          const item = JSON.parse(localStorage.getItem(key));
          if (item.timestamp && (now - item.timestamp) > maxAge) {
            localStorage.removeItem(key);
          }
        } catch (error) {
          // Si no es un objeto JSON válido, lo eliminamos
          localStorage.removeItem(key);
        }
      });

      // Actualizar estadísticas de caché
      setCacheSize(0);
      
      // Registrar optimización
      setOptimizationHistory(prev => [...prev, {
        type: 'cache_optimization',
        timestamp: new Date(),
        success: true
      }]);

    } catch (error) {
      console.error('Error en optimización de caché:', error);
      setOptimizationHistory(prev => [...prev, {
        type: 'cache_optimization',
        timestamp: new Date(),
        success: false,
        error: error.message
      }]);
    } finally {
      setIsOptimizing(false);
    }
  }, [optimizationConfig.caching.maxAge]);

  // Optimización de memoria
  const optimizeMemory = useCallback(() => {
    // Forzar garbage collection si está disponible
    if (window.gc) {
      window.gc();
    }

    // Limpiar referencias a objetos grandes
    const cleanup = () => {
      // Limpiar imágenes no utilizadas
      const images = document.querySelectorAll('img[data-lazy]');
      images.forEach(img => {
        if (!img.complete) {
          img.src = '';
        }
      });

      // Limpiar event listeners no utilizados
      // Esto es más complejo y requeriría un sistema de tracking
    };

    cleanup();

    // Actualizar uso de memoria estimado
    if (performance.memory) {
      setMemoryUsage(performance.memory.usedJSHeapSize);
    }
  }, []);

  // Optimización de red
  const optimizeNetwork = useCallback(async () => {
    setIsOptimizing(true);
    
    try {
      // Prefetch de recursos críticos
      const criticalResources = [
        '/api/documents/',
        '/api/incidents/',
        '/static/css/main.css',
        '/static/js/main.js'
      ];

      await Promise.all(
        criticalResources.map(resource => {
          const link = document.createElement('link');
          link.rel = 'prefetch';
          link.href = resource;
          document.head.appendChild(link);
        })
      );

      // Registrar optimización
      setOptimizationHistory(prev => [...prev, {
        type: 'network_optimization',
        timestamp: new Date(),
        success: true
      }]);

    } catch (error) {
      console.error('Error en optimización de red:', error);
      setOptimizationHistory(prev => [...prev, {
        type: 'network_optimization',
        timestamp: new Date(),
        success: false,
        error: error.message
      }]);
    } finally {
      setIsOptimizing(false);
    }
  }, []);

  // Optimización completa
  const runFullOptimization = useCallback(async () => {
    setIsOptimizing(true);
    
    try {
      await Promise.all([
        optimizeCache(),
        optimizeMemory(),
        optimizeNetwork()
      ]);

      setOptimizationHistory(prev => [...prev, {
        type: 'full_optimization',
        timestamp: new Date(),
        success: true
      }]);

    } catch (error) {
      console.error('Error en optimización completa:', error);
      setOptimizationHistory(prev => [...prev, {
        type: 'full_optimization',
        timestamp: new Date(),
        success: false,
        error: error.message
      }]);
    } finally {
      setIsOptimizing(false);
    }
  }, [optimizeCache, optimizeMemory, optimizeNetwork]);

  // Monitoreo de rendimiento
  useEffect(() => {
    const monitorPerformance = () => {
      if (performance.memory) {
        setMemoryUsage(performance.memory.usedJSHeapSize);
      }
    };

    const interval = setInterval(monitorPerformance, 30000); // Cada 30 segundos
    return () => clearInterval(interval);
  }, []);

  // Estadísticas de rendimiento
  const performanceStats = useMemo(() => ({
    isOptimizing,
    cacheSize,
    memoryUsage: memoryUsage / 1024 / 1024, // Convertir a MB
    optimizationHistory: optimizationHistory.slice(-10), // Últimas 10 optimizaciones
    config: optimizationConfig
  }), [isOptimizing, cacheSize, memoryUsage, optimizationHistory, optimizationConfig]);

  return {
    // Funciones de optimización
    enableLazyLoading,
    compressImage,
    optimizeCache,
    optimizeMemory,
    optimizeNetwork,
    runFullOptimization,
    
    // Estado y estadísticas
    performanceStats,
    isOptimizing,
    
    // Configuración
    optimizationConfig
  };
};

export default usePerformanceOptimization;
