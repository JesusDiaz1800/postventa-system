/**
 * Servicio de Notificaciones en Tiempo Real
 * Maneja WebSocket, notificaciones del navegador y estado global
 */

// Usamos la misma configuración de backend que el resto de la app
// para que funcione tanto en desarrollo como en producción.
import { API_ORIGIN } from './api';

class NotificationService {
  constructor() {
    this.ws = null;
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 3000; // 3 segundos
    this.heartbeatInterval = null;
    this.listeners = new Map();
    this.notifications = [];
    this.unreadCount = 0;
    this.connectionTimeout = null;
    this.isConnecting = false;
    this.messageQueue = []; // Cola de mensajes pendientes
  }

  /**
   * Conectar al WebSocket
   */
  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) {
      if (import.meta.env.DEV) {
        console.log('WebSocket ya está conectado');
      }
      return;
    }
    
    // Evitar múltiples conexiones simultáneas
    if (this.isConnecting) {
      if (import.meta.env.DEV) {
        console.log('Ya hay una conexión en proceso...');
      }
      return;
    }
    
    // Cerrar conexión existente si está en estado de conexión
    if (this.ws?.readyState === WebSocket.CONNECTING) {
      if (import.meta.env.DEV) {
        console.log('Cerrando conexión previa en proceso...');
      }
      this.ws.close();
      this.ws = null;
    }

    const token = this.getToken();
    if (!token) {
      console.warn('No hay token disponible para WebSocket');
      return;
    }
    
    this.isConnecting = true;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';

    // Resolver host y puerto del backend de forma dinámica:
    // - En desarrollo: usar mismo hostname que el frontend y puerto 8000 (o VITE_BACKEND_WS_PORT)
    // - En producción: usar el mismo host/puerto que sirve la app (reverse proxy)
    let hostname = window.location.hostname;
    let port = window.location.port;

    if (import.meta.env.DEV) {
      // Usar puerto configurable para backend ASGI en desarrollo
      const devPort = import.meta.env.VITE_BACKEND_WS_PORT || '8000';
      port = devPort;
    }

    // Si API_ORIGIN está definido con un host específico (por ejemplo en producción),
    // respetar ese host para asegurar coherencia con el backend real.
    try {
      const apiUrl = new URL(API_ORIGIN, window.location.origin);
      hostname = apiUrl.hostname || hostname;
      // Si API_ORIGIN ya define un puerto explícito, respetarlo en producción
      if (!import.meta.env.DEV && apiUrl.port) {
        port = apiUrl.port;
      }
    } catch {
      // Si falla el parseo, seguimos con hostname/port derivados de window.location
    }

    const backendHost = port ? `${hostname}:${port}` : hostname;
    const wsUrl = `${protocol}//${backendHost}/ws/notifications/?token=${token}`;
    
    if (import.meta.env.DEV) {
      console.log('Conectando a WebSocket:', wsUrl);
    }

    try {
      this.ws = new WebSocket(wsUrl);
      this.setupEventHandlers();
    } catch (error) {
      console.error('Error creando WebSocket:', error);
      this.scheduleReconnect();
    }
  }

  /**
   * Configurar manejadores de eventos WebSocket
   */
  setupEventHandlers() {
    this.ws.onopen = (event) => {
      console.log('✅ WebSocket conectado');
      this.isConnected = true;
      this.isConnecting = false;
      this.reconnectAttempts = 0;
      this.startHeartbeat();
      
      // Procesar cola de mensajes pendientes
      this.processMessageQueue();
      
      this.emit('connected', { event });
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.handleMessage(data);
      } catch (error) {
        console.error('Error parseando mensaje WebSocket:', error);
      }
    };

    this.ws.onclose = (event) => {
      console.log('🔌 WebSocket desconectado:', event.code, event.reason);
      this.isConnected = false;
      this.isConnecting = false;
      this.stopHeartbeat();
      this.emit('disconnected', { event });
      
      if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
        this.scheduleReconnect();
      }
    };

    this.ws.onerror = (error) => {
      console.warn('⚠️ Error WebSocket (reintentando):', error);
      this.isConnecting = false;
      this.emit('error', { error });
      // No intentar reconectar inmediatamente para evitar spam
    };
  }

  /**
   * Manejar mensajes del WebSocket
   */
  handleMessage(data) {
    console.log('📨 Mensaje WebSocket recibido:', data);

    switch (data.type) {
      case 'connection_established':
        this.emit('connection_established', data);
        break;
        
      case 'new_notification':
        this.addNotification(data.notification);
        this.showBrowserNotification(data.notification);
        break;
        
      case 'unread_count_update':
        this.unreadCount = data.count;
        this.emit('unread_count_update', data);
        break;
        
      case 'notifications_list':
        this.notifications = data.notifications;
        this.emit('notifications_list', data);
        break;
        
      case 'notification_updated':
        this.updateNotification(data.notification);
        break;
        
      case 'notification_deleted':
        this.removeNotification(data.notification_id);
        break;
        
      case 'system_notification':
        this.handleSystemNotification(data.notification);
        break;
        
      case 'system_alert':
        this.handleSystemAlert(data.alert);
        break;
        
      case 'ping':
        // Responder al ping del servidor
        this.send({ type: 'pong' });
        break;
        
      case 'pong':
        // Respuesta al heartbeat
        break;
        
      case 'error':
        console.warn('Error del servidor WebSocket:', data.message);
        this.emit('server_error', data);
        break;
        
      default:
        console.warn('Tipo de mensaje WebSocket no manejado:', data.type);
    }
  }

  /**
   * Agregar notificación
   */
  addNotification(notification) {
    this.notifications.unshift(notification);
    if (!notification.is_read) {
      this.unreadCount++;
    }
    this.emit('notification_added', notification);
  }

  /**
   * Actualizar notificación
   */
  updateNotification(notification) {
    const index = this.notifications.findIndex(n => n.id === notification.id);
    if (index !== -1) {
      this.notifications[index] = notification;
      this.emit('notification_updated', notification);
    }
  }

  /**
   * Eliminar notificación
   */
  removeNotification(notificationId) {
    const index = this.notifications.findIndex(n => n.id === notificationId);
    if (index !== -1) {
      const notification = this.notifications[index];
      this.notifications.splice(index, 1);
      if (!notification.is_read) {
        this.unreadCount = Math.max(0, this.unreadCount - 1);
      }
      this.emit('notification_removed', notification);
    }
  }

  /**
   * Mostrar notificación del navegador
   */
  showBrowserNotification(notification) {
    if ('Notification' in window && Notification.permission === 'granted') {
      const browserNotification = new Notification(notification.title, {
        body: notification.message,
        icon: '/icons/icon-192x192.png',
        badge: '/icons/icon-144x144.png',
        tag: `notification-${notification.id}`,
        requireInteraction: notification.is_important,
        actions: [
          {
            action: 'view',
            title: 'Ver'
          },
          {
            action: 'dismiss',
            title: 'Descartar'
          }
        ]
      });

      browserNotification.onclick = () => {
        window.focus();
        if (notification.related_url) {
          window.location.href = notification.related_url;
        }
        browserNotification.close();
      };
    }
  }

  /**
   * Manejar notificación del sistema
   */
  handleSystemNotification(notification) {
    console.log('🔔 Notificación del sistema:', notification);
    this.emit('system_notification', notification);
  }

  /**
   * Manejar alerta del sistema
   */
  handleSystemAlert(alert) {
    console.warn('⚠️ Alerta del sistema:', alert);
    this.emit('system_alert', alert);
  }

  /**
   * Enviar mensaje por WebSocket
   */
  send(message) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify(message));
      } catch (error) {
        console.error('Error enviando mensaje WebSocket:', error);
      }
    } else if (this.ws?.readyState === WebSocket.CONNECTING) {
      // Si está conectando, agregar a la cola
      this.messageQueue.push(message);
    } else {
      // Si no está conectado, agregar a la cola y intentar conectar
      this.messageQueue.push(message);
      if (!this.isConnecting) {
        this.connect();
      }
    }
  }

  /**
   * Procesar cola de mensajes pendientes
   */
  processMessageQueue() {
    while (this.messageQueue.length > 0 && this.ws?.readyState === WebSocket.OPEN) {
      const message = this.messageQueue.shift();
      try {
        this.ws.send(JSON.stringify(message));
      } catch (error) {
        console.error('Error enviando mensaje de la cola:', error);
      }
    }
  }

  /**
   * Marcar notificación como leída
   */
  markAsRead(notificationId) {
    this.send({
      type: 'mark_as_read',
      notification_id: notificationId
    });
  }

  /**
   * Marcar todas como leídas
   */
  markAllAsRead() {
    this.send({
      type: 'mark_all_as_read'
    });
  }

  /**
   * Obtener notificaciones
   */
  getNotifications(limit = 10, page = 1, filterType = 'all') {
    this.send({
      type: 'get_notifications',
      limit,
      page,
      filter_type: filterType
    });
  }

  /**
   * Obtener conteo de no leídas
   */
  getUnreadCount() {
    this.send({
      type: 'get_unread_count'
    });
  }

  /**
   * Obtener notificaciones importantes
   */
  getImportantNotifications() {
    this.send({
      type: 'get_important'
    });
  }

  /**
   * Marcar como importante
   */
  markAsImportant(notificationId, important = true) {
    this.send({
      type: 'mark_as_important',
      notification_id: notificationId,
      important
    });
  }

  /**
   * Heartbeat para mantener conexión viva
   */
  startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.isConnected) {
        this.send({ type: 'ping' });
      }
    }, 30000); // Cada 30 segundos
  }

  /**
   * Detener heartbeat
   */
  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  /**
   * Programar reconexión
   */
  scheduleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectInterval * this.reconnectAttempts;
      
      console.log(`🔄 Reintentando conexión WebSocket en ${delay}ms (intento ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        this.connect();
      }, delay);
    } else {
      console.error('❌ Máximo de intentos de reconexión alcanzado');
      this.emit('max_reconnect_attempts_reached');
    }
  }

  /**
   * Desconectar WebSocket
   */
  disconnect() {
    if (this.ws) {
      this.ws.close(1000, 'Desconexión normal');
      this.ws = null;
    }
    this.isConnected = false;
    this.stopHeartbeat();
  }

  /**
   * Obtener token de autenticación
   */
  getToken() {
    // Intentar obtener token de localStorage
    let token = localStorage.getItem('access_token');
    
    if (!token) {
      // Intentar obtener de postventa_auth
      const authData = localStorage.getItem('postventa_auth');
      if (authData) {
        try {
          const parsed = JSON.parse(authData);
          token = parsed.token || parsed.access_token;
        } catch (e) {
          console.warn('Error parseando auth data:', e);
        }
      }
    }

    if (!token) {
      // Intentar obtener de sessionStorage
      token = sessionStorage.getItem('access_token');
    }

    return token;
  }

  /**
   * Suscribirse a eventos
   */
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  /**
   * Desuscribirse de eventos
   */
  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  /**
   * Emitir evento
   */
  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error en callback de evento ${event}:`, error);
        }
      });
    }
  }

  /**
   * Obtener estado de conexión
   */
  getConnectionStatus() {
    return {
      isConnected: this.isConnected,
      reconnectAttempts: this.reconnectAttempts,
      unreadCount: this.unreadCount,
      notificationsCount: this.notifications.length
    };
  }

  /**
   * Limpiar datos
   */
  cleanup() {
    this.disconnect();
    this.listeners.clear();
    this.notifications = [];
    this.unreadCount = 0;
  }
}

// Crear instancia singleton
const notificationService = new NotificationService();

// Exportar tanto la clase como la instancia
export { NotificationService };
export default notificationService;
