import { useState, useCallback } from 'react';

export const useNotifications = () => {
  const [notifications, setNotifications] = useState([]);

  const addNotification = useCallback((notification) => {
    const id = Date.now() + Math.random();
    const newNotification = {
      id,
      type: 'info',
      duration: 5000,
      ...notification,
    };
    
    setNotifications(prev => [...prev, newNotification]);
    return id;
  }, []);

  const removeNotification = useCallback((id) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  }, []);

  const showSuccess = useCallback((message, title = 'Éxito') => {
    return addNotification({
      type: 'success',
      title,
      message,
    });
  }, [addNotification]);

  const showError = useCallback((message, title = 'Error') => {
    return addNotification({
      type: 'error',
      title,
      message,
      duration: 7000, // Los errores se muestran más tiempo
    });
  }, [addNotification]);

  const showWarning = useCallback((message, title = 'Advertencia') => {
    return addNotification({
      type: 'warning',
      title,
      message,
    });
  }, [addNotification]);

  const showInfo = useCallback((message, title = 'Información') => {
    return addNotification({
      type: 'info',
      title,
      message,
    });
  }, [addNotification]);

  return {
    notifications,
    addNotification,
    removeNotification,
    showSuccess,
    showError,
    showWarning,
    showInfo,
  };
};
