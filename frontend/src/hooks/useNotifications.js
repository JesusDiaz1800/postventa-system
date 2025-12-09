import { useState, useEffect, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import notificationService from '../services/notificationService';

// Hook principal para notificaciones con WebSocket
export const useNotifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isConnected, setIsConnected] = useState(false);
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

  return {
    notifications,
    unreadCount,
    isConnected,
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