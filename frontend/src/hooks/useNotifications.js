<<<<<<< HEAD
import { useState, useEffect, useCallback, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';

// Hook para notificaciones con WebSocket
=======
import { useState, useEffect, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import notificationService from '../services/notificationService';

// Hook principal para notificaciones con WebSocket
>>>>>>> 674c244 (tus cambios)
export const useNotifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isConnected, setIsConnected] = useState(false);
<<<<<<< HEAD
  const wsRef = useRef(null);
  const queryClient = useQueryClient();

  // Conectar WebSocket
  const connectWebSocket = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

  // Build WS URL from current location so it matches http vs https (ws vs wss)
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.host; // includes port when present
  const wsUrl = `${protocol}//${host}/ws/notifications/`;
  const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      console.log('WebSocket conectado para notificaciones');
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        switch (data.type) {
          case 'connection_established':
            setUnreadCount(data.unread_count);
            break;
            
          case 'new_notification':
            const newNotification = data.notification;
            setNotifications(prev => [newNotification, ...prev]);
            setUnreadCount(prev => prev + 1);
            
            // Mostrar notificación del navegador si está permitido
            if (Notification.permission === 'granted') {
              new Notification(newNotification.title, {
                body: newNotification.message,
                icon: '/favicon.ico',
                badge: '/favicon.ico'
              });
            }
            break;
            
          case 'notification_updated':
            setNotifications(prev => 
              prev.map(notif => 
                notif.id === data.notification.id ? data.notification : notif
              )
            );
            break;
            
          case 'notification_deleted':
            setNotifications(prev => 
              prev.filter(notif => notif.id !== data.notification_id)
            );
            break;
            
          case 'unread_count_update':
            setUnreadCount(data.count);
            break;
            
          case 'notifications_list':
            setNotifications(data.notifications);
            break;
            
          case 'unread_count':
            setUnreadCount(data.count);
            break;
            
          case 'error':
            console.error('Error en WebSocket:', data.message);
            break;
            
          default:
            console.log('Mensaje WebSocket no manejado:', data);
        }
      } catch (error) {
        console.error('Error parseando mensaje WebSocket:', error);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket desconectado');
      setIsConnected(false);
      // Reconectar después de 3 segundos
      setTimeout(connectWebSocket, 3000);
    };

    ws.onerror = (error) => {
      console.error('Error en WebSocket:', error);
      setIsConnected(false);
    };

    wsRef.current = ws;
  }, []);

  // Desconectar WebSocket
  const disconnectWebSocket = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
      setIsConnected(false);
    }
  }, []);

  // Conectar al montar el componente
  useEffect(() => {
    connectWebSocket();
    
    // Solicitar permisos para notificaciones del navegador
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }

    return () => {
      disconnectWebSocket();
    };
  }, [connectWebSocket, disconnectWebSocket]);

  // Enviar mensaje por WebSocket
  const sendWebSocketMessage = useCallback((message) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  // Marcar notificación como leída
  const markAsRead = useCallback((notificationId) => {
    sendWebSocketMessage({
      type: 'mark_as_read',
      notification_id: notificationId
    });
  }, [sendWebSocketMessage]);

  // Marcar todas como leídas
  const markAllAsRead = useCallback(() => {
    sendWebSocketMessage({
      type: 'mark_all_as_read'
    });
  }, [sendWebSocketMessage]);

  // Obtener notificaciones recientes
  const getRecentNotifications = useCallback((limit = 10) => {
    sendWebSocketMessage({
      type: 'get_notifications',
      limit
    });
  }, [sendWebSocketMessage]);

  // Obtener conteo de no leídas
  const getUnreadCount = useCallback(() => {
    sendWebSocketMessage({
      type: 'get_unread_count'
    });
  }, [sendWebSocketMessage]);
=======
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Solo conectar si no hay conexión activa
    if (!notificationService.isConnected && !notificationService.isConnecting) {
      console.log('🔌 Conectando WebSocket para notificaciones en tiempo real...');
      notificationService.connect();
    }

    // Suscribirse a eventos del servicio
    const handleConnected = () => setIsConnected(true);
    const handleDisconnected = () => setIsConnected(false);
    const handleNotificationAdded = (notification) => {
      setNotifications(prev => [notification, ...prev]);
      if (!notification.is_read) {
        setUnreadCount(prev => prev + 1);
      }
    };
    const handleNotificationUpdated = (notification) => {
      setNotifications(prev => 
        prev.map(n => n.id === notification.id ? notification : n)
      );
    };
    const handleNotificationRemoved = (notification) => {
      setNotifications(prev => prev.filter(n => n.id !== notification.id));
      if (!notification.is_read) {
        setUnreadCount(prev => Math.max(0, prev - 1));
      }
    };
    const handleUnreadCountUpdate = (data) => {
      setUnreadCount(data.count);
    };
    const handleNotificationsList = (data) => {
      setNotifications(data.notifications);
      setIsLoading(false);
    };

    notificationService.on('connected', handleConnected);
    notificationService.on('disconnected', handleDisconnected);
    notificationService.on('notification_added', handleNotificationAdded);
    notificationService.on('notification_updated', handleNotificationUpdated);
    notificationService.on('notification_removed', handleNotificationRemoved);
    notificationService.on('unread_count_update', handleUnreadCountUpdate);
    notificationService.on('notifications_list', handleNotificationsList);

    // Cargar notificaciones iniciales solo si no hay conexión activa
    if (!notificationService.isConnected) {
      loadNotifications();
    }

    return () => {
      notificationService.off('connected', handleConnected);
      notificationService.off('disconnected', handleDisconnected);
      notificationService.off('notification_added', handleNotificationAdded);
      notificationService.off('notification_updated', handleNotificationUpdated);
      notificationService.off('notification_removed', handleNotificationRemoved);
      notificationService.off('unread_count_update', handleUnreadCountUpdate);
      notificationService.off('notifications_list', handleNotificationsList);
    };
  }, []);

  const loadNotifications = useCallback((limit = 20, page = 1, filterType = 'all') => {
    setIsLoading(true);
    
    // Esperar a que el WebSocket esté conectado antes de enviar mensaje
    if (notificationService.isConnected) {
      notificationService.getNotifications(limit, page, filterType);
    } else {
      // Si no está conectado, esperar un momento y reintentar
      const checkConnection = () => {
        if (notificationService.isConnected) {
          notificationService.getNotifications(limit, page, filterType);
        } else {
          setTimeout(checkConnection, 100);
        }
      };
      setTimeout(checkConnection, 100);
    }
  }, []);

  const markAsRead = useCallback((notificationId) => {
    notificationService.markAsRead(notificationId);
    setNotifications(prev =>
      prev.map(n =>
        n.id === notificationId ? { ...n, is_read: true } : n
      )
    );
    setUnreadCount(prev => Math.max(0, prev - 1));
  }, []);

  const markAllAsRead = useCallback(() => {
    notificationService.markAllAsRead();
    setNotifications(prev =>
      prev.map(n => ({ ...n, is_read: true }))
    );
    setUnreadCount(0);
  }, []);

  const markAsImportant = useCallback((notificationId, important = true) => {
    notificationService.markAsImportant(notificationId, important);
    setNotifications(prev =>
      prev.map(n =>
        n.id === notificationId ? { ...n, is_important: important } : n
      )
    );
  }, []);

  const connect = useCallback(() => {
    notificationService.connect();
  }, []);

  const disconnect = useCallback(() => {
    notificationService.disconnect();
  }, []);

  const reconnectAfterLogin = useCallback(() => {
    notificationService.disconnect();
    setTimeout(() => {
      notificationService.connect();
    }, 1000);
  }, []);

  const sendMessage = useCallback((message) => {
    notificationService.send(message);
  }, []);
>>>>>>> 674c244 (tus cambios)

  return {
    notifications,
    unreadCount,
    isConnected,
<<<<<<< HEAD
    markAsRead,
    markAllAsRead,
    getRecentNotifications,
    getUnreadCount
=======
    isLoading,
    loadNotifications,
    markAsRead,
    markAllAsRead,
    markAsImportant,
    connect,
    disconnect,
    reconnectAfterLogin,
    sendMessage,
    // Mantener compatibilidad con la API anterior
    connectWebSocket: connect,
    disconnectWebSocket: disconnect,
    sendWebSocketMessage: sendMessage
>>>>>>> 674c244 (tus cambios)
  };
};

// Hook para gestión de notificaciones con API REST
export const useNotificationAPI = () => {
  const queryClient = useQueryClient();

  // Obtener notificaciones
  const { data: notifications, isLoading, error } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => api.get('/notifications/notifications/').then(res => res.data),
    staleTime: 30000, // 30 segundos
  });

  // Obtener conteo de no leídas
  const { data: unreadCount } = useQuery({
    queryKey: ['notifications', 'unread-count'],
    queryFn: () => api.get('/notifications/notifications/unread_count/').then(res => res.data),
    staleTime: 10000, // 10 segundos
    refetchInterval: 30000, // Refrescar cada 30 segundos
  });

  // Marcar como leída
  const markAsReadMutation = useMutation({
    mutationFn: (notificationId) => 
      api.post(`/notifications/notifications/${notificationId}/mark_read/`),
    onSuccess: () => {
      queryClient.invalidateQueries(['notifications']);
      queryClient.invalidateQueries(['notifications', 'unread-count']);
    },
  });

  // Marcar todas como leídas
  const markAllAsReadMutation = useMutation({
    mutationFn: () => 
      api.post('/notifications/notifications/mark_all_read/'),
    onSuccess: () => {
      queryClient.invalidateQueries(['notifications']);
      queryClient.invalidateQueries(['notifications', 'unread-count']);
    },
  });

  // Obtener notificaciones recientes
  const { data: recentNotifications } = useQuery({
    queryKey: ['notifications', 'recent'],
    queryFn: () => api.get('/notifications/notifications/recent/').then(res => res.data),
    staleTime: 60000, // 1 minuto
  });

  // Obtener notificaciones importantes
  const { data: importantNotifications } = useQuery({
    queryKey: ['notifications', 'important'],
    queryFn: () => api.get('/notifications/notifications/important/').then(res => res.data),
    staleTime: 60000, // 1 minuto
  });

  return {
    notifications,
    unreadCount: unreadCount?.unread_count || 0,
    recentNotifications,
    importantNotifications,
    isLoading,
    error,
    markAsRead: markAsReadMutation.mutate,
    markAllAsRead: markAllAsReadMutation.mutate,
    isMarkingAsRead: markAsReadMutation.isLoading,
    isMarkingAllAsRead: markAllAsReadMutation.isLoading,
  };
};

// Hook para preferencias de notificación
export const useNotificationPreferences = () => {
  const queryClient = useQueryClient();

  // Obtener preferencias
  const { data: preferences, isLoading } = useQuery({
    queryKey: ['notification-preferences'],
    queryFn: () => api.get('/notifications/preferences/my_preferences/').then(res => res.data),
  });

  // Actualizar preferencias
  const updatePreferencesMutation = useMutation({
    mutationFn: (data) => 
      api.put('/notifications/preferences/my_preferences/', data),
    onSuccess: () => {
      queryClient.invalidateQueries(['notification-preferences']);
    },
  });

  return {
    preferences,
    isLoading,
    updatePreferences: updatePreferencesMutation.mutate,
    isUpdating: updatePreferencesMutation.isLoading,
  };
};

// Hook para crear notificaciones
export const useCreateNotification = () => {
  const queryClient = useQueryClient();

  const createNotificationMutation = useMutation({
    mutationFn: (notificationData) => 
      api.post('/notifications/notifications/', notificationData),
    onSuccess: () => {
      queryClient.invalidateQueries(['notifications']);
      queryClient.invalidateQueries(['notifications', 'unread-count']);
    },
  });

  return {
    createNotification: createNotificationMutation.mutate,
    isCreating: createNotificationMutation.isLoading,
    error: createNotificationMutation.error,
  };
};

// Hook para estadísticas de notificaciones
export const useNotificationStats = () => {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['notifications', 'stats'],
    queryFn: () => api.get('/notifications/notifications/stats/').then(res => res.data),
    staleTime: 300000, // 5 minutos
  });

  return {
    stats,
    isLoading,
  };
};