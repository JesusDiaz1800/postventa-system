import { useState, useEffect, useCallback } from 'react';
import { toast } from 'react-hot-toast';
import notificationService from '../services/notificationService';

/**
 * Hook para manejar las notificaciones del sistema en tiempo real.
 * Conectado al servicio de WebSockets de Sertec.
 */
export const useNotifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isConnected, setIsConnected] = useState(false);

  // Sincronizar estado con el servicio global
  useEffect(() => {
    // Escuchar cambios de conexión
    const unsubConnection = notificationService.onConnectionChange(setIsConnected);
    
    // Escuchar nuevas notificaciones
    const unsubNotifications = notificationService.onNotification((notif) => {
      setNotifications(prev => [notif, ...prev].slice(0, 50));
      setUnreadCount(prev => prev + 1);
      
      // Mostrar Toast automático
      if (notif.notification_type === 'success' || notif.notification_type === 'sap') {
        toast.success(notif.message || notif.title);
      } else if (notif.notification_type === 'error') {
        toast.error(notif.message || notif.title);
      } else {
        toast(notif.message || notif.title, { icon: '🔔' });
      }
    });

    return () => {
      unsubConnection();
      unsubNotifications();
    };
  }, []);

  const markAsRead = async (id) => {
    await notificationService.markAsRead(id);
    setUnreadCount(prev => Math.max(0, prev - 1));
  };

  const markAllAsRead = async () => {
    await notificationService.markAllAsRead();
    setUnreadCount(0);
  };

  return {
    notifications,
    unreadCount,
    isConnected,
    isLoading: false,
    markAsRead,
    markAllAsRead,
    showSuccess: (m) => toast.success(m),
    showError: (m) => toast.error(m),
    showInfo: (m) => toast(m, { icon: 'ℹ️' }),
    showWarning: (m) => toast(m, { icon: '⚠️' }),
  };
};

export default useNotifications;