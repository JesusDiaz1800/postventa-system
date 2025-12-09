import React, { useState, useEffect, useRef } from 'react';
import { 
  BellIcon, 
  XMarkIcon, 
  CheckIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import notificationService from '../services/notificationService';

const NotificationCenter = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isConnected, setIsConnected] = useState(false);
  const [activeTab, setActiveTab] = useState('all'); // 'all', 'unread', 'important'
  const [isLoading, setIsLoading] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    // Conectar al servicio de notificaciones
    notificationService.connect();

    // Suscribirse a eventos
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

    // Cargar notificaciones iniciales
    loadNotifications();

    // Cerrar dropdown al hacer clic fuera
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);

    return () => {
      notificationService.off('connected', handleConnected);
      notificationService.off('disconnected', handleDisconnected);
      notificationService.off('notification_added', handleNotificationAdded);
      notificationService.off('notification_updated', handleNotificationUpdated);
      notificationService.off('notification_removed', handleNotificationRemoved);
      notificationService.off('unread_count_update', handleUnreadCountUpdate);
      notificationService.off('notifications_list', handleNotificationsList);
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const loadNotifications = () => {
    setIsLoading(true);
    console.log('🔌 Cargando notificaciones via WebSocket...');
    
    // Esperar a que el WebSocket esté conectado antes de enviar mensaje
    if (notificationService.isConnected) {
      notificationService.getNotifications(20, 1, activeTab);
    } else {
      // Si no está conectado, esperar un momento y reintentar
      const checkConnection = () => {
        if (notificationService.isConnected) {
          notificationService.getNotifications(20, 1, activeTab);
        } else {
          setTimeout(checkConnection, 100);
        }
      };
      setTimeout(checkConnection, 100);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadNotifications();
    }
  }, [isOpen, activeTab]);

  const handleMarkAsRead = (notificationId) => {
    notificationService.markAsRead(notificationId);
    setNotifications(prev =>
      prev.map(n =>
        n.id === notificationId ? { ...n, is_read: true } : n
      )
    );
    setUnreadCount(prev => Math.max(0, prev - 1));
  };

  const handleMarkAllAsRead = () => {
    notificationService.markAllAsRead();
    setNotifications(prev =>
      prev.map(n => ({ ...n, is_read: true }))
    );
    setUnreadCount(0);
  };

  const handleMarkAsImportant = (notificationId, important) => {
    notificationService.markAsImportant(notificationId, important);
    setNotifications(prev =>
      prev.map(n =>
        n.id === notificationId ? { ...n, is_important: important } : n
      )
    );
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'system_alert':
      case 'deadline_exceeded':
        return <ExclamationTriangleIcon className="w-5 h-5 text-red-500" />;
      case 'incident_created':
      case 'incident_updated':
        return <InformationCircleIcon className="w-5 h-5 text-blue-500" />;
      default:
        return <InformationCircleIcon className="w-5 h-5 text-gray-500" />;
    }
  };

  const getNotificationColor = (notification) => {
    if (notification.is_important) return 'border-l-red-500 bg-red-50';
    if (!notification.is_read) return 'border-l-blue-500 bg-blue-50';
    return 'border-l-gray-300 bg-white';
  };

  const filteredNotifications = notifications.filter(notification => {
    switch (activeTab) {
      case 'unread':
        return !notification.is_read;
      case 'important':
        return notification.is_important;
      default:
        return true;
    }
  });

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Botón de notificaciones */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors duration-200"
        title="Notificaciones"
      >
        <BellIcon className="w-6 h-6" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-medium">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
        {/* Indicador de conexión WebSocket */}
        <div className={`absolute bottom-0 right-0 w-2 h-2 rounded-full ${
          isConnected ? 'bg-green-500' : 'bg-red-500'
        }`} />
      </button>

      {/* Dropdown de notificaciones */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
          {/* Header */}
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">
                Notificaciones
              </h3>
              <div className="flex items-center space-x-2">
                {/* Indicador de conexión */}
                <div className={`w-2 h-2 rounded-full ${
                  isConnected ? 'bg-green-500' : 'bg-red-500'
                }`} />
                <span className="text-xs text-gray-500">
                  {isConnected ? 'En línea' : 'Desconectado'}
                </span>
                <button
                  onClick={() => setIsOpen(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Tabs */}
            <div className="flex space-x-1 mt-3">
              {[
                { key: 'all', label: 'Todas' },
                { key: 'unread', label: 'No leídas' },
                { key: 'important', label: 'Importantes' }
              ].map(tab => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={`px-3 py-1 text-sm rounded-md transition-colors ${
                    activeTab === tab.key
                      ? 'bg-blue-500 text-white'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Acciones */}
            {unreadCount > 0 && (
              <button
                onClick={handleMarkAllAsRead}
                className="mt-2 text-sm text-blue-600 hover:text-blue-800 flex items-center"
              >
                <CheckIcon className="w-4 h-4 mr-1" />
                Marcar todas como leídas
              </button>
            )}
          </div>

          {/* Lista de notificaciones */}
          <div className="max-h-96 overflow-y-auto">
            {isLoading ? (
              <div className="p-4 text-center text-gray-500">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mx-auto"></div>
                <p className="mt-2">Cargando notificaciones...</p>
              </div>
            ) : filteredNotifications.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <BellIcon className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                <p>No hay notificaciones</p>
              </div>
            ) : (
              filteredNotifications.map(notification => (
                <div
                  key={notification.id}
                  className={`p-4 border-l-4 ${getNotificationColor(notification)} hover:bg-gray-50 transition-colors`}
                >
                  <div className="flex items-start space-x-3">
                    {getNotificationIcon(notification.notification_type)}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {notification.title}
                        </p>
                        <div className="flex items-center space-x-1">
                          {!notification.is_read && (
                            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                          )}
                          <button
                            onClick={() => handleMarkAsImportant(
                              notification.id, 
                              !notification.is_important
                            )}
                            className={`p-1 rounded ${
                              notification.is_important 
                                ? 'text-red-500 hover:text-red-600' 
                                : 'text-gray-400 hover:text-red-500'
                            }`}
                            title={notification.is_important ? 'Quitar importancia' : 'Marcar como importante'}
                          >
                            <ExclamationTriangleIcon className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">
                        {notification.message}
                      </p>
                      <div className="flex items-center justify-between mt-2">
                        <div className="flex items-center text-xs text-gray-500">
                          <ClockIcon className="w-3 h-3 mr-1" />
                          {notification.time_ago}
                        </div>
                        {!notification.is_read && (
                          <button
                            onClick={() => handleMarkAsRead(notification.id)}
                            className="text-xs text-blue-600 hover:text-blue-800 flex items-center"
                          >
                            <CheckIcon className="w-3 h-3 mr-1" />
                            Marcar como leída
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          {filteredNotifications.length > 0 && (
            <div className="p-3 border-t border-gray-200 bg-gray-50">
              <button
                onClick={loadNotifications}
                className="w-full text-sm text-gray-600 hover:text-gray-800 py-1"
              >
                Ver todas las notificaciones
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default NotificationCenter;
