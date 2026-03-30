import React, { useState, useEffect, useRef } from 'react';
import {
  BellIcon,
  XMarkIcon,
  CheckIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  ClockIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import { useNotifications } from '../hooks/useNotifications';
import { motion, AnimatePresence } from 'framer-motion';

const NotificationCenter = () => {
  const {
    notifications,
    unreadCount,
    isConnected,
    isLoading,
    loadNotifications,
    markAsRead,
    markAllAsRead
  } = useNotifications();

  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('all');
  const dropdownRef = useRef(null);

  // Reload when dropdown opens to ensure fresh data
  useEffect(() => {
    if (isOpen) {
      loadNotifications();
    }
  }, [isOpen, loadNotifications]);

  // Click outside handler
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'system_alert':
      case 'deadline_exceeded':
        return <ExclamationTriangleIcon className="w-5 h-5 text-red-400" />;
      case 'incident_created':
      case 'incident_updated':
        return <InformationCircleIcon className="w-5 h-5 text-blue-400" />;
      default:
        return <InformationCircleIcon className="w-5 h-5 text-emerald-400" />;
    }
  };

  const getNotificationStyles = (notification) => {
    if (notification.is_important) return 'border-l-red-500 bg-red-500/5';
    if (!notification.is_read) return 'border-l-blue-500 bg-blue-500/5';
    return 'border-l-slate-700 bg-white/2';
  };

  const formatTimeAgo = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Ahora';
    if (diffMins < 60) return `Hace ${diffMins}m`;
    if (diffHours < 24) return `Hace ${diffHours}h`;
    return `Hace ${diffDays}d`;
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
      {/* Notification button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`relative p-2 rounded-xl transition-all duration-300 group ${isOpen ? 'bg-blue-600/10 text-white' : 'text-slate-400 hover:text-white hover:bg-white/5'
          }`}
        title="Notificaciones"
      >
        <BellIcon className={`w-6 h-6 transition-transform duration-300 ${isOpen ? 'scale-110' : ''}`} />

        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-600 text-white text-[10px] font-black rounded-lg h-5 w-5 flex items-center justify-center shadow-[0_0_10px_rgba(239,68,68,0.5)] border border-red-500/50">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}

        {/* Connection indicator */}
        <div className={`absolute bottom-0.5 right-0.5 w-2 h-2 rounded-full border-2 border-[#030014] ${isConnected ? 'bg-emerald-500' : 'bg-orange-500 animate-pulse'
          }`} />
      </button>

      {/* Dropdown */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="absolute right-0 mt-3 w-96 bg-[#0b1120] rounded-2xl shadow-[0_20px_60px_rgba(0,0,0,0.6)] border border-white/5 overflow-hidden z-50 ring-1 ring-white/5"
          >
            {/* Header */}
            <div className="p-5 border-b border-white/5 bg-white/5">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <h3 className="text-sm font-black text-white uppercase tracking-tight">
                    Notificaciones
                  </h3>
                  <div className="px-2 py-0.5 rounded bg-blue-500/10 border border-blue-500/20 text-[9px] font-bold text-blue-400 uppercase tracking-widest">
                    {unreadCount} Nuevas
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={loadNotifications}
                    className="p-1.5 text-slate-400 hover:text-white hover:bg-white/5 rounded-lg transition-all"
                    title="Actualizar"
                  >
                    <ArrowPathIcon className={`w-4 h-4 ${isLoading ? 'animate-spin text-blue-400' : ''}`} />
                  </button>
                  <button
                    onClick={() => setIsOpen(false)}
                    className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-red-500/5 rounded-lg transition-all"
                  >
                    <XMarkIcon className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* Tabs */}
              <div className="flex gap-1 bg-black/20 p-1 rounded-xl">
                {[
                  { key: 'all', label: 'Todas' },
                  { key: 'unread', label: 'No leídas' },
                  { key: 'important', label: 'Alertas' }
                ].map(tab => (
                  <button
                    key={tab.key}
                    onClick={() => setActiveTab(tab.key)}
                    className={`flex-1 px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider rounded-lg transition-all ${activeTab === tab.key
                        ? 'bg-blue-600 text-white shadow-lg'
                        : 'text-slate-400 hover:text-white hover:bg-white/5'
                      }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Notification list */}
            <div className="max-h-[420px] overflow-y-auto custom-scrollbar bg-black/10">
              {isLoading && notifications.length === 0 ? (
                <div className="p-12 text-center">
                  <div className="w-10 h-10 border-2 border-blue-500/20 border-t-blue-500 rounded-full animate-spin mx-auto mb-4"></div>
                  <p className="text-xs font-bold text-slate-500 uppercase tracking-widest">Sincronizando...</p>
                </div>
              ) : filteredNotifications.length === 0 ? (
                <div className="p-12 text-center">
                  <div className="relative w-16 h-16 mx-auto mb-4">
                    <BellIcon className="w-full h-full text-slate-800" />
                    <div className="absolute inset-0 bg-blue-500/5 blur-xl rounded-full" />
                  </div>
                  <p className="text-xs font-bold text-slate-500 uppercase tracking-widest leading-relaxed">
                    Sin notificaciones<br />pendientes
                  </p>
                </div>
              ) : (
                <div className="divide-y divide-white/2">
                  {filteredNotifications.map(notification => (
                    <div
                      key={notification.id}
                      className={`p-4 border-l-4 transition-all hover:bg-white/5 cursor-pointer ${getNotificationStyles(notification)}`}
                    >
                      <div className="flex items-start gap-4">
                        <div className="p-2 rounded-xl bg-white/5 mt-0.5">
                          {getNotificationIcon(notification.notification_type)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between gap-2">
                            <p className="text-[13px] font-bold text-white truncate leading-snug">
                              {notification.title}
                            </p>
                            <span className="text-[9px] font-bold text-slate-500 whitespace-nowrap">
                              {formatTimeAgo(notification.created_at)}
                            </span>
                          </div>
                          <p className="text-xs text-slate-400 mt-1 leading-relaxed line-clamp-2 italic">
                            {notification.message}
                          </p>

                          {!notification.is_read && (
                            <div className="flex items-center justify-end mt-3 gap-3">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  markAsRead(notification.id);
                                }}
                                className="px-2 py-1 text-[9px] font-black uppercase text-blue-400 hover:text-white bg-blue-400/10 hover:bg-blue-500 rounded-md transition-all tracking-tighter"
                              >
                                Marcar leída
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-white/5 bg-white/2 flex items-center justify-between">
              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="px-3 py-1.5 text-[10px] font-black text-emerald-400 hover:text-white hover:bg-emerald-500/20 rounded-lg transition-all uppercase tracking-tighter flex items-center gap-2"
                >
                  <CheckIcon className="w-4 h-4" />
                  Leer todo
                </button>
              )}

              <div className="flex items-center gap-2 ml-auto">
                <span className={`w-1.5 h-1.5 rounded-full ${isConnected ? 'bg-emerald-500' : 'bg-orange-500 animate-pulse'}`} />
                <span className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">
                  {isConnected ? 'Sincronizado' : 'Offline'}
                </span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default NotificationCenter;
