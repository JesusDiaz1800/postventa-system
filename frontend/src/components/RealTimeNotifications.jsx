import React, { useState, useEffect, useRef } from 'react';
import {
  BellIcon,
  XMarkIcon,
  CheckIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  CheckCircleIcon,
  ClockIcon,
  UserIcon,
  DocumentIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline';

/**
 * Sistema de notificaciones en tiempo real con WebSocket
 */
const RealTimeNotifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [settings, setSettings] = useState({
    sound: true,
    desktop: true,
    autoClose: 5000
  });
  
  const wsRef = useRef(null);
  const audioRef = useRef(null);

  // Simular notificaciones en tiempo real
  useEffect(() => {
    const mockNotifications = [
      {
        id: 1,
        type: 'success',
        title: 'Documento Aprobado',
        message: 'El documento "Reporte de Calidad Q4" ha sido aprobado por el supervisor.',
        timestamp: new Date(Date.now() - 5 * 60 * 1000),
        read: false,
        action: 'view_document'
      },
      {
        id: 2,
        type: 'warning',
        title: 'Alerta de Sistema',
        message: 'El servidor está experimentando alta carga. Tiempo de respuesta: 3.2s',
        timestamp: new Date(Date.now() - 15 * 60 * 1000),
        read: false,
        action: 'system_status'
      },
      {
        id: 3,
        type: 'info',
        title: 'Nueva Incidencia',
        message: 'Se ha creado una nueva incidencia: INC-2025-001 - Tubería PPR',
        timestamp: new Date(Date.now() - 30 * 60 * 1000),
        read: true,
        action: 'view_incident'
      },
      {
        id: 4,
        type: 'error',
        title: 'Error de Carga',
        message: 'No se pudo cargar el documento "Manual Técnico v2.1.pdf"',
        timestamp: new Date(Date.now() - 45 * 60 * 1000),
        read: true,
        action: 'retry_upload'
      }
    ];

    setNotifications(mockNotifications);
    setUnreadCount(mockNotifications.filter(n => !n.read).length);

    // Simular nuevas notificaciones
    const interval = setInterval(() => {
      const newNotification = {
        id: Date.now(),
        type: ['success', 'warning', 'info', 'error'][Math.floor(Math.random() * 4)],
        title: ['Documento Procesado', 'Sistema Actualizado', 'Nueva Tarea', 'Recordatorio'][Math.floor(Math.random() * 4)],
        message: 'Notificación automática del sistema generada en tiempo real.',
        timestamp: new Date(),
        read: false,
        action: 'view_details'
      };

      setNotifications(prev => [newNotification, ...prev]);
      setUnreadCount(prev => prev + 1);

      // Reproducir sonido si está habilitado
      if (settings.sound && audioRef.current) {
        audioRef.current.play().catch(() => {});
      }

      // Notificación de escritorio si está habilitada
      if (settings.desktop && 'Notification' in window && Notification.permission === 'granted') {
        new Notification(newNotification.title, {
          body: newNotification.message,
          icon: '/favicon.ico'
        });
      }
    }, 30000); // Cada 30 segundos

    return () => clearInterval(interval);
  }, [settings]);

  // Solicitar permisos de notificación
  useEffect(() => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'success':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'warning':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
      case 'error':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <InformationCircleIcon className="h-5 w-5 text-blue-500" />;
    }
  };

  const getNotificationColor = (type) => {
    switch (type) {
      case 'success':
        return 'border-l-green-500 bg-green-50';
      case 'warning':
        return 'border-l-yellow-500 bg-yellow-50';
      case 'error':
        return 'border-l-red-500 bg-red-50';
      default:
        return 'border-l-blue-500 bg-blue-50';
    }
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Ahora';
    if (minutes < 60) return `Hace ${minutes}m`;
    if (hours < 24) return `Hace ${hours}h`;
    return `Hace ${days}d`;
  };

  const markAsRead = (id) => {
    setNotifications(prev => 
      prev.map(notif => 
        notif.id === id ? { ...notif, read: true } : notif
      )
    );
    setUnreadCount(prev => Math.max(0, prev - 1));
  };

  const markAllAsRead = () => {
    setNotifications(prev => 
      prev.map(notif => ({ ...notif, read: true }))
    );
    setUnreadCount(0);
  };

  const deleteNotification = (id) => {
    setNotifications(prev => {
      const notification = prev.find(n => n.id === id);
      if (notification && !notification.read) {
        setUnreadCount(prev => Math.max(0, prev - 1));
      }
      return prev.filter(n => n.id !== id);
    });
  };

  const clearAll = () => {
    setNotifications([]);
    setUnreadCount(0);
  };

  return (
    <div className="relative">
      {/* Audio para notificaciones */}
      <audio ref={audioRef} preload="auto">
        <source src="/notification.mp3" type="audio/mpeg" />
      </audio>

      {/* Botón de notificaciones */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
      >
        <BellIcon className="h-6 w-6" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-medium">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Panel de notificaciones */}
      {isOpen && (
        <>
          {/* Overlay */}
          <div 
            className="fixed inset-0 z-40" 
            onClick={() => setIsOpen(false)}
          />
          
          {/* Panel */}
          <div className="absolute right-0 top-full mt-2 w-96 bg-white rounded-xl shadow-lg border border-gray-200 z-50 max-h-96 overflow-hidden">
            {/* Header */}
            <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-gray-900">Notificaciones</h3>
                <div className="flex items-center space-x-2">
                  {unreadCount > 0 && (
                    <button
                      onClick={markAllAsRead}
                      className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                    >
                      Marcar todas como leídas
                    </button>
                  )}
                  <button
                    onClick={() => setIsOpen(false)}
                    className="p-1 text-gray-400 hover:text-gray-600 rounded"
                  >
                    <XMarkIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>

            {/* Lista de notificaciones */}
            <div className="max-h-80 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="px-4 py-8 text-center text-gray-500">
                  <BellIcon className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                  <p>No hay notificaciones</p>
                </div>
              ) : (
                <div className="divide-y divide-gray-100">
                  {notifications.map((notification) => (
                    <div
                      key={notification.id}
                      className={`px-4 py-3 border-l-4 hover:bg-gray-50 transition-colors ${
                        notification.read ? 'bg-white' : 'bg-blue-50'
                      } ${getNotificationColor(notification.type)}`}
                    >
                      <div className="flex items-start space-x-3">
                        {getNotificationIcon(notification.type)}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <p className={`text-sm font-medium ${
                              notification.read ? 'text-gray-900' : 'text-gray-900'
                            }`}>
                              {notification.title}
                            </p>
                            <div className="flex items-center space-x-1">
                              <span className="text-xs text-gray-500">
                                {formatTimeAgo(notification.timestamp)}
                              </span>
                              {!notification.read && (
                                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                              )}
                            </div>
                          </div>
                          <p className="text-sm text-gray-600 mt-1">
                            {notification.message}
                          </p>
                          <div className="flex items-center space-x-2 mt-2">
                            {!notification.read && (
                              <button
                                onClick={() => markAsRead(notification.id)}
                                className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                              >
                                Marcar como leída
                              </button>
                            )}
                            <button
                              onClick={() => deleteNotification(notification.id)}
                              className="text-xs text-red-600 hover:text-red-800 font-medium"
                            >
                              Eliminar
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Footer */}
            {notifications.length > 0 && (
              <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
                <div className="flex items-center justify-between">
                  <button
                    onClick={clearAll}
                    className="text-xs text-red-600 hover:text-red-800 font-medium"
                  >
                    Limpiar todas
                  </button>
                  <button
                    onClick={() => setIsOpen(false)}
                    className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                  >
                    Ver todas las notificaciones
                  </button>
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default RealTimeNotifications;
