import { useState, useEffect, useCallback } from 'react';
import { toast } from 'react-hot-toast';
import { notificationsAPI } from '../services/api';
import notificationService from '../services/notificationService';

/**
 * Hook principal para notificaciones en tiempo real
 * Integra WebSocket (via NotificationService) y API REST
 */
export const useNotifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isConnected, setIsConnected] = useState(notificationService.isConnected);
  const [isLoading, setIsLoading] = useState(false);

  // Funciones helper para mostrar notificaciones (toast) - Mantener compatibilidad
  const showSuccess = useCallback((message) => toast.success(message), []);
  const showError = useCallback((message) => toast.error(message), []);
  const showInfo = useCallback((message) => toast(message, { icon: 'ℹ️' }), []);
  const showWarning = useCallback((message) => toast(message, { icon: '⚠️' }), []);

  // Cargar notificaciones iniciales via HTTP
  const loadNotifications = useCallback(async () => {
    setIsLoading(true);
    try {
      const [recentRes, unreadRes] = await Promise.all([
        notificationsAPI.recent(),
        notificationsAPI.unreadCount()
      ]);
      setNotifications(recentRes.data || []);
      setUnreadCount(unreadRes.data.unread_count || 0);
    } catch (error) {
      console.error('Error cargando notificaciones:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Suscribirse a eventos WebSocket
  useEffect(() => {
    // Carga inicial
    loadNotifications();

    // Asegurar conexión WS
    notificationService.connect();

    // Handlers de eventos
    const handleNewNotification = (notification) => {
      setNotifications(prev => [notification, ...prev]);
      setUnreadCount(prev => prev + 1);

      // Notificación visual flotante
      toast(notification.title, {
        icon: '🔔',
        duration: 4000,
        position: 'top-right'
      });
    };

    const handleUnreadUpdate = (data) => {
      if (data.count !== undefined) {
        setUnreadCount(data.count);
      }
    };

    const handleConnected = () => setIsConnected(true);
    const handleDisconnected = () => setIsConnected(false);

    // Registrar listeners
    notificationService.on('notification_added', handleNewNotification);
    notificationService.on('unread_count_update', handleUnreadUpdate);
    notificationService.on('connected', handleConnected);
    notificationService.on('disconnected', handleDisconnected);

    return () => {
      notificationService.off('notification_added', handleNewNotification);
      notificationService.off('unread_count_update', handleUnreadUpdate);
      notificationService.off('connected', handleConnected);
      notificationService.off('disconnected', handleDisconnected);
    };
  }, [loadNotifications]);

  // Acciones
  const markAsRead = async (id) => {
    try {
      // Optimistic update
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n));
      setUnreadCount(prev => Math.max(0, prev - 1));

      await notificationsAPI.markAsRead(id);
    } catch (error) {
      console.error('Error marcando como leída:', error);
      // Revertir si falla (opcional, por simplicidad omitimos revert complejo)
      loadNotifications();
    }
  };

  const markAllAsRead = async () => {
    try {
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      setUnreadCount(0);

      await notificationsAPI.markAllAsRead();
    } catch (error) {
      console.error('Error marcando todas leídas:', error);
      loadNotifications();
    }
  };

  return {
    // Estado
    notifications,
    unreadCount,
    isConnected,
    isLoading,

    // Acciones Datos
    loadNotifications,
    markAsRead,
    markAllAsRead,

    // Toasts helpers
    showSuccess,
    showError,
    showInfo,
    showWarning,

    // Control WS (wrappers)
    connect: () => notificationService.connect(),
    disconnect: () => notificationService.disconnect(),
    connectWebSocket: () => notificationService.connect(), // Alias legacy
  };
};

// Exports de compatibilidad para evitar romper imports existentes
export { useNotifications as useNotificationAPI };
export { useNotifications as useNotificationPreferences };
export { useNotifications as useCreateNotification };
export { useNotifications as useNotificationStats };

export default useNotifications;