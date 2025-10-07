import React, { useState, useEffect } from 'react';
import { 
  BellIcon, 
  XMarkIcon, 
  CheckIcon, 
  ExclamationTriangleIcon,
  InformationCircleIcon,
  DocumentTextIcon,
  UserIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import { useNotifications, useNotificationAPI } from '../hooks/useNotifications';

const NotificationCenter = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [showAll, setShowAll] = useState(false);
  
  const {
    notifications: wsNotifications,
    unreadCount: wsUnreadCount,
    isConnected,
    markAsRead: wsMarkAsRead,
    markAllAsRead: wsMarkAllAsRead,
    getRecentNotifications
  } = useNotifications();

  const {
    notifications: apiNotifications,
    unreadCount: apiUnreadCount,
    isLoading,
    markAsRead: apiMarkAsRead,
    markAllAsRead: apiMarkAllAsRead,
    isMarkingAllAsRead
  } = useNotificationAPI();

  // Usar notificaciones de WebSocket si están disponibles, sino de API
  const notifications = (wsNotifications && wsNotifications.length > 0) ? wsNotifications : (apiNotifications || []);
  const unreadCount = (typeof wsUnreadCount === 'number' && wsUnreadCount > 0) ? wsUnreadCount : (apiUnreadCount || 0);

  // Obtener notificaciones recientes al abrir
  useEffect(() => {
    if (isOpen && (!notifications || notifications.length === 0)) {
      getRecentNotifications(20);
    }
  }, [isOpen, notifications.length, getRecentNotifications]);

  const handleMarkAsRead = (notificationId) => {
    if (wsNotifications && wsNotifications.length > 0) {
      wsMarkAsRead(notificationId);
    } else {
      apiMarkAsRead(notificationId);
    }
  };

  const handleMarkAllAsRead = () => {
    if (wsNotifications && wsNotifications.length > 0) {
      wsMarkAllAsRead();
    } else {
      apiMarkAllAsRead();
    }
  };

  const getNotificationIcon = (type, isImportant) => {
    if (isImportant) {
      return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
    }

    switch (type) {
      case 'incident_created':
      case 'incident_updated':
      case 'incident_escalated':
      case 'incident_closed':
        return <ExclamationTriangleIcon className="h-5 w-5 text-blue-500" />;
      case 'document_uploaded':
      case 'document_approved':
      case 'document_rejected':
        return <DocumentTextIcon className="h-5 w-5 text-green-500" />;
      case 'workflow_step_completed':
      case 'workflow_approval_required':
        return <CheckIcon className="h-5 w-5 text-purple-500" />;
      case 'user_assigned':
        return <UserIcon className="h-5 w-5 text-indigo-500" />;
      case 'system_alert':
        return <InformationCircleIcon className="h-5 w-5 text-yellow-500" />;
      default:
        return <InformationCircleIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getNotificationTypeLabel = (type) => {
    const labels = {
      'incident_created': 'Nueva Incidencia',
      'incident_updated': 'Incidencia Actualizada',
      'incident_escalated': 'Incidencia Escalada',
      'incident_closed': 'Incidencia Cerrada',
      'document_uploaded': 'Documento Subido',
      'document_approved': 'Documento Aprobado',
      'document_rejected': 'Documento Rechazado',
      'workflow_step_completed': 'Paso Completado',
      'workflow_approval_required': 'Aprobación Requerida',
      'user_assigned': 'Usuario Asignado',
      'system_alert': 'Alerta del Sistema',
      'deadline_approaching': 'Fecha Límite Próxima',
      'deadline_exceeded': 'Fecha Límite Excedida',
    };
    return labels[type] || 'Notificación';
  };

  const formatTimeAgo = (createdAt) => {
    if (!createdAt) return 'Ahora';
    
    const now = new Date();
    const created = new Date(createdAt);
    const diff = now - created;
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (days > 0) return `${days}d`;
    if (hours > 0) return `${hours}h`;
    if (minutes > 0) return `${minutes}m`;
    return 'Ahora';
  };

  const displayedNotifications = showAll ? notifications : notifications.slice(0, 5);

  return (
    <div className="relative">
      {/* Botón de notificaciones */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 rounded-full"
      >
        <BellIcon className="h-6 w-6" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
        {/* Indicador de conexión WebSocket */}
        <span className={`absolute -bottom-1 -right-1 h-3 w-3 rounded-full ${
          isConnected ? 'bg-green-500' : 'bg-gray-400'
        }`} />
      </button>

      {/* Panel de notificaciones */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
          {/* Header */}
          <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">
              Notificaciones
              {unreadCount > 0 && (
                <span className="ml-2 bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full">
                  {unreadCount} nueva{unreadCount !== 1 ? 's' : ''}
                </span>
              )}
            </h3>
            <div className="flex items-center space-x-2">
              {unreadCount > 0 && (
                <button
                  onClick={handleMarkAllAsRead}
                  disabled={isMarkingAllAsRead}
                  className="text-sm text-indigo-600 hover:text-indigo-800 disabled:opacity-50"
                >
                  {isMarkingAllAsRead ? 'Marcando...' : 'Marcar todas'}
                </button>
              )}
              <button
                onClick={() => setIsOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XMarkIcon className="h-5 w-5" />
              </button>
            </div>
          </div>

          {/* Lista de notificaciones */}
          <div className="max-h-96 overflow-y-auto">
            {isLoading ? (
              <div className="p-4 text-center text-gray-500">
                Cargando notificaciones...
              </div>
            ) : displayedNotifications.length === 0 ? (
              <div className="p-4 text-center text-gray-500">
                No hay notificaciones
              </div>
            ) : (
              displayedNotifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`p-4 border-b border-gray-100 hover:bg-gray-50 cursor-pointer ${
                    !notification.is_read ? 'bg-blue-50' : ''
                  }`}
                  onClick={() => handleMarkAsRead(notification.id)}
                >
                  <div className="flex items-start space-x-3">
                    {getNotificationIcon(notification.notification_type, notification.is_important)}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {notification.title}
                        </p>
                        <div className="flex items-center space-x-2">
                          <span className="text-xs text-gray-500 flex items-center">
                            <ClockIcon className="h-3 w-3 mr-1" />
                            {formatTimeAgo(notification.created_at)}
                          </span>
                          {!notification.is_read && (
                            <div className="h-2 w-2 bg-blue-500 rounded-full" />
                          )}
                        </div>
                      </div>
                      <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                        {notification.message}
                      </p>
                      <div className="mt-2 flex items-center justify-between">
                        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                          {getNotificationTypeLabel(notification.notification_type)}
                        </span>
                        {notification.is_important && (
                          <span className="text-xs text-red-600 bg-red-100 px-2 py-1 rounded">
                            Importante
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          {notifications.length > 5 && (
            <div className="px-4 py-3 border-t border-gray-200">
              <button
                onClick={() => setShowAll(!showAll)}
                className="w-full text-sm text-indigo-600 hover:text-indigo-800 text-center"
              >
                {showAll ? 'Ver menos' : `Ver todas (${notifications.length})`}
              </button>
            </div>
          )}

          {/* Estado de conexión */}
          <div className="px-4 py-2 border-t border-gray-200 bg-gray-50">
            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>
                {isConnected ? 'Conectado en tiempo real' : 'Modo offline'}
              </span>
              <span>
                {notifications.length} notificación{notifications.length !== 1 ? 'es' : ''}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationCenter;
