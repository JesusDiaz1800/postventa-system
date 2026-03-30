/**
 * Servicio de Notificaciones en Tiempo Real (Profesional V2)
 * Arquitectura: Singleton con manejo robusto de desconexiones y estado.
 */

import { API_ORIGIN } from './api';
import toast from 'react-hot-toast';

class NotificationService {
  static instance = null;

  constructor() {
    if (NotificationService.instance) {
      return NotificationService.instance;
    }

    // Estado y Configuración
    this.ws = null;
    this.isConnected = false;
    this.isConnecting = false;
    this.listeners = new Map();
    this.messageQueue = [];

    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 1; // Reducido de 3 a 1 para evitar spam
    this.baseReconnectInterval = 5000;
    this.maxReconnectInterval = 30000;

    // Identificadores de Timers
    this.heartbeatInterval = null;
    this.reconnectTimeout = null;

    NotificationService.instance = this;

    // Bindings
    this.handleVisibilityChange = this.handleVisibilityChange.bind(this);
    document.addEventListener('visibilitychange', this.handleVisibilityChange);
  }

  // --- Singleton Accessor ---
  static getInstance() {
    if (!NotificationService.instance) {
      NotificationService.instance = new NotificationService();
    }
    return NotificationService.instance;
  }

  // --- Gestión de Conexión ---

  connect() {
    // Evitar conexiones duplicadas
    if (this.isConnecting) return;
    if (this.ws?.readyState === WebSocket.OPEN || this.ws?.readyState === WebSocket.CONNECTING) {
      return;
    }

    this.isConnecting = true;
    const token = this.getToken();

    if (!token) {
      this.isConnecting = false;
      // No loggear si no hay token - es comportamiento esperado
      return;
    }

    try {
      const wsUrl = this.buildWebSocketURL(token);
      // Only log first attempt and every 5th retry to reduce noise
      if (this.reconnectAttempts === 0 || this.reconnectAttempts % 5 === 0) {
        console.log(`🔌 [NS] Connecting to: ${wsUrl.split('?')[0]} (attempt ${this.reconnectAttempts + 1})`);
      }

      this.ws = new WebSocket(wsUrl);
      this.setupEventHandlers();
    } catch (error) {
      console.error('❌ [NS] WebSocket instant failure:', error);
      this.handleConnectionError();
    }
  }

  handleConnectionError(err) {
    this.isConnecting = false;
    this.isConnected = false;
    console.error('❌ [NS] Detailed Connection Error:', err);
    this.scheduleReconnect();
  }

  disconnect() {
    if (this.ws) {
      // Remover listeners para evitar "falsos positivos" de desconexión durante cierre manual
      this.ws.onclose = null;
      this.ws.onerror = null;
      this.ws.close(1000, 'Manual disconnect');
      this.ws = null;
    }
    this.isConnected = false;
    this.isConnecting = false;
    this.stopHeartbeat();
    if (this.reconnectTimeout) clearTimeout(this.reconnectTimeout);

    // console.log('🔌 [NS] Disconnected manually');
    this.emit('disconnected');
  }

  // --- Helpers Internos ---

  buildWebSocketURL(token) {
    // When Vite runs with HTTPS (SSL certs), browser is on https:// so we MUST use wss://
    // Vite's proxy handles the WSS -> WS downgrade to the backend (Daphne on http://)
    // This is the correct behavior: browser <--WSS--> Vite <--WS--> Daphne
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const countryCode = localStorage.getItem('country_code') || 'CL';
    return `${protocol}//${host}/ws/notifications/?token=${token}&country=${countryCode}`;
  }

  setupEventHandlers() {
    if (!this.ws) return;

    this.ws.onopen = () => {
      // console.log('✅ [NS] Connected');
      this.isConnected = true;
      this.isConnecting = false;
      this.reconnectAttempts = 0;
      this.startHeartbeat();
      this.processMessageQueue();
      this.emit('connected');
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.handleServerMessage(data);
      } catch (e) {
        console.error('❌ [NS] Failed to parse message:', e);
      }
    };

    this.ws.onclose = (event) => {
      this.isConnected = false;
      this.isConnecting = false;
      this.stopHeartbeat();
      this.emit('disconnected');

      // Códigos de cierre que NO deberían reintentar
      // 4001: Envío de token inválido/sin auth
      // 1000: Cierre normal
      // 1008: Policy violation (e.g. too many connections)
      if (event.code !== 1000 && event.code !== 4001 && event.code !== 1008 && event.code !== 1006) {
        console.warn(`⚠️ [NS] Disconnected unexpectedly (Code: ${event.code}). Reconnecting...`);
        this.scheduleReconnect();
      } else {
        // Code 1006 is often abnormal but can happen on navigation/reload, reducing noise
        if (event.code === 1006) {
          console.debug(`ℹ️ [NS] Connection closed (Code: ${event.code}) - Likely navigation/reload`);
          this.scheduleReconnect();
        } else {
          console.debug(`ℹ️ [NS] Connection closed cleanly (Code: ${event.code})`);
        }
      }
    };

    this.ws.onerror = (error) => {
      // Solo loggear primer error para evitar spam en consola
      if (this.reconnectAttempts === 0) {
        console.warn('⚠️ [NS] WebSocket no disponible (normal en desarrollo sin backend activo)');
      }
      this.handleConnectionError(error);
    };
  }

  handleServerMessage(data) {
    // console.debug('📩 [NS] RX:', data.type);

    switch (data.type) {
      case 'new_notification':
        this.emit('notification_added', data.notification);
        break;
      case 'unread_count_update':
        this.emit('unread_count_update', data);
        break;
      case 'notifications_list':
        this.emit('notifications_list', data);
        break;
      case 'notification_updated':
        this.emit('notification_updated', data.notification);
        break;
      case 'pong':
      case 'ping':
        // Alive
        break;
      case 'error':
        // Ignorar errores de ping del servidor (ruido de heartbeat)
        if (data.message && (data.message.includes('unknown message') || data.message.includes('desconocido: ping'))) {
          break;
        }
        console.error('🔥 [NS] Server Error:', data.message);
        break;
      default:
        // Pass-through other events
        if (data.type) this.emit(data.type, data);
    }
  }

  // --- Lógica de Negocio ---

  send(type, payload = {}) {
    const message = JSON.stringify({ type, ...payload });

    if (this.isConnected && this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(message);
    } else {
      // Cola limitada para evitar desbordamiento
      if (this.messageQueue.length < 50) {
        this.messageQueue.push(message);
      }
      if (!this.isConnecting && !this.isConnected) {
        this.connect();
      }
    }
  }

  processMessageQueue() {
    while (this.messageQueue.length > 0 && this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(this.messageQueue.shift());
    }
  }

  // --- Utility Methods ---

  getNotifications(limit = 10, page = 1) {
    this.send('get_notifications', { limit, page });
  }

  markAsRead(id) {
    this.send('mark_as_read', { notification_id: id });
  }

  markAllAsRead() {
    this.send('mark_all_as_read');
  }

  // --- Reconexión y Heartbeat ---

  scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      // Silent after max attempts - only show toast once
      if (this.reconnectAttempts === this.maxReconnectAttempts) {
        console.warn('⚠️ [NS] Max reconnect attempts reached. Notifications will work via REST API.');
        // Don't show toast error - this is not critical, REST fallback works
      }
      return;
    }

    // Exponential Backoff con Jitter - longer delays to reduce noise
    const delay = Math.min(
      this.baseReconnectInterval * Math.pow(2, this.reconnectAttempts),
      this.maxReconnectInterval
    ) + (Math.random() * 1000);

    this.reconnectAttempts++;

    if (this.reconnectTimeout) clearTimeout(this.reconnectTimeout);
    this.reconnectTimeout = setTimeout(() => {
      this.isConnecting = false;
      this.connect();
    }, delay);
  }

  handleConnectionError() {
    this.isConnecting = false;
    this.scheduleReconnect();
  }

  startHeartbeat() {
    this.stopHeartbeat();
    this.heartbeatInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000); // 30s keep-alive
  }

  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  handleVisibilityChange() {
    if (document.visibilityState === 'visible' && !this.isConnected) {
      // console.log('👀 [NS] Tab visible, checking connection...');
      // Verify token exists before attempting connection to avoid noise
      if (this.getToken()) {
        this.reconnectAttempts = 0; // Reset attempts on manual interaction
        this.connect();
      }
    }
  }

  getToken() {
    let token = localStorage.getItem('access_token');
    if (!token) {
      try {
        const auth = JSON.parse(localStorage.getItem('postventa_auth') || '{}');
        token = auth.token || auth.access_token;
      } catch (e) { }
    }
    return token;
  }

  // --- Event Emitter Simple ---

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event).add(callback);
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).delete(callback);
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(cb => cb(data));
    }
  }
}

// Export singleton instance
const notificationService = new NotificationService();
export default notificationService;
export { NotificationService };
