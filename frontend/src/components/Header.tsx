"use client";

import { useState, useEffect, useRef } from 'react';
// import { Logo } from './Logo'; // Removed to avoid repetitive logo
import { cn } from '@/lib/utils';
import { 
  Bell, 
  User, 
  Settings, 
  LogOut, 
  Menu,
  X
} from 'lucide-react';

interface HeaderProps {
  user?: {
    username: string;
    role: string;
    email: string;
  };
  onLogout?: () => void;
  currentPage?: string;
  onMenuToggle?: () => void;
  isSidebarOpen?: boolean;
}

export function Header({ user, onLogout, currentPage, onMenuToggle, isSidebarOpen }: HeaderProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const notificationsRef = useRef<HTMLDivElement>(null);
  const [notifications, setNotifications] = useState([
    {
      id: 1,
      title: 'Nueva incidencia reportada',
      message: 'Se ha reportado una nueva incidencia en el sistema',
      time: 'Hace 5 minutos',
      type: 'info',
      read: false
    },
    {
      id: 2,
      title: 'Incidencia resuelta',
      message: 'La incidencia #INC-001 ha sido marcada como resuelta',
      time: 'Hace 1 hora',
      type: 'success',
      read: false
    },
    {
      id: 3,
      title: 'Recordatorio de seguimiento',
      message: 'Tienes 3 incidencias pendientes de seguimiento',
      time: 'Hace 2 horas',
      type: 'warning',
      read: true
    }
  ]);

  // Cerrar dropdowns al hacer clic fuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (notificationsRef.current && !notificationsRef.current.contains(event.target as Node)) {
        setIsNotificationsOpen(false);
      }
    };

    if (isNotificationsOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isNotificationsOpen]);

  // Navigation removed - sidebar handles all navigation

  const getPageTitle = (path: string) => {
    const pageTitles: { [key: string]: string } = {
      '/': 'Dashboard',
      '/dashboard': 'Dashboard',
      '/incidents': 'Incidencias',
      '/visit-reports': 'Reportes de Visita',
      '/quality-reports/client': 'Reportes de Calidad - Cliente',
      '/quality-reports/internal': 'Informes Internos de Calidad',
      '/supplier-reports': 'Informes para Proveedores',
      '/users': 'Usuarios',
      '/ai': 'IA & Análisis',
      '/workflows': 'Workflows',
      '/settings': 'Configuración',
      '/audit': 'Auditoría',
    };
    return pageTitles[path] || 'Sistema de Gestión de Incidencias';
  };

  const getRoleDisplay = (role: string) => {
    const roleMap = {
      'admin': 'Administrador',
      'supervisor': 'Supervisor',
      'analista': 'Analista Técnico',
      'atencion_cliente': 'Atención al Cliente',
      'proveedor': 'Proveedor',
    };
    return roleMap[role as keyof typeof roleMap] || role;
  };

  return (
    <header className="bg-white/95 backdrop-blur-md shadow-lg border-b border-gray-200/30 relative z-30 mb-6">
      <div className="w-full px-6 sm:px-8 lg:px-10">
        <div className="flex justify-between items-center h-20">
          {/* Botón de menú y título dinámico */}
          <div className="flex items-center space-x-4 flex-1 min-w-0">
            {/* Botón para contraer/expandir sidebar */}
            <button
              onClick={onMenuToggle}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors duration-200 flex-shrink-0"
              title={isSidebarOpen ? 'Contraer menú' : 'Expandir menú'}
            >
              {isSidebarOpen ? (
                <X className="h-5 w-5" />
              ) : (
                <Menu className="h-5 w-5" />
              )}
            </button>
            
            <div className="flex-1 min-w-0 overflow-hidden">
              <h1 className="text-base font-semibold text-gray-800 truncate" title={currentPage ? getPageTitle(currentPage) : 'Sistema de Gestión de Incidencias'}>
                {currentPage ? getPageTitle(currentPage) : 'Sistema de Gestión de Incidencias'}
              </h1>
            </div>
          </div>

          {/* Lado derecho */}
          <div className="flex items-center space-x-4 flex-shrink-0">
            {/* Notificaciones */}
            <div className="relative">
              <button 
                onClick={() => setIsNotificationsOpen(!isNotificationsOpen)}
                className="p-2 text-gray-400 hover:text-gray-500 relative"
              >
                <Bell className="w-5 h-5" />
                {notifications.filter(n => !n.read).length > 0 && (
                  <span className="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-400 ring-2 ring-white"></span>
                )}
              </button>

              {/* Dropdown de notificaciones */}
              {isNotificationsOpen && (
                <>
                  {/* Overlay para cerrar al hacer clic fuera */}
                  <div 
                    className="fixed inset-0 z-[9998] bg-black bg-opacity-25 backdrop-blur-sm" 
                    onClick={() => setIsNotificationsOpen(false)}
                  />
                  <div ref={notificationsRef} className="fixed right-4 top-20 w-80 bg-white rounded-lg shadow-2xl py-1 z-[9999] border border-gray-200 max-h-96 overflow-hidden">
                  <div className="px-4 py-2 border-b border-gray-100">
                    <div className="flex items-center justify-between">
                      <h3 className="text-sm font-medium text-gray-900">Notificaciones</h3>
                      <button 
                        onClick={() => {
                          setNotifications(notifications.map(n => ({ ...n, read: true })));
                        }}
                        className="text-xs text-blue-600 hover:text-blue-800"
                      >
                        Marcar todas como leídas
                      </button>
                    </div>
                  </div>
                  
                  <div className="max-h-64 overflow-y-auto">
                    {notifications.length > 0 ? (
                      notifications.map((notification) => (
                        <div
                          key={notification.id}
                          className={`px-4 py-3 border-b border-gray-100 hover:bg-gray-50 cursor-pointer ${
                            !notification.read ? 'bg-blue-50' : ''
                          }`}
                          onClick={() => {
                            setNotifications(notifications.map(n => 
                              n.id === notification.id ? { ...n, read: true } : n
                            ));
                          }}
                        >
                          <div className="flex items-start">
                            <div className={`w-2 h-2 rounded-full mt-2 mr-3 ${
                              notification.type === 'success' ? 'bg-green-500' :
                              notification.type === 'warning' ? 'bg-yellow-500' :
                              'bg-blue-500'
                            }`}></div>
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-gray-900">{notification.title}</p>
                              <p className="text-sm text-gray-600 mt-1">{notification.message}</p>
                              <p className="text-xs text-gray-500 mt-1">{notification.time}</p>
                            </div>
                            {!notification.read && (
                              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                            )}
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="px-4 py-8 text-center">
                        <Bell className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                        <p className="text-sm text-gray-500">No hay notificaciones</p>
                      </div>
                    )}
                  </div>
                  
                  {notifications.length > 0 && (
                    <div className="px-4 py-2 border-t border-gray-100">
                      <button className="text-sm text-blue-600 hover:text-blue-800 w-full text-left">
                        Ver todas las notificaciones
                      </button>
                    </div>
                  )}
                  </div>
                </>
              )}
            </div>

            {/* Menú de usuario */}
            <div className="relative">
              <button
                onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                className="flex items-center space-x-3 p-2 rounded-md hover:bg-gray-50 transition-colors duration-200"
              >
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                  <User className="w-4 h-4 text-white" />
                </div>
                <div className="hidden md:block text-left">
                  <p className="text-sm font-medium text-gray-700">{user?.username}</p>
                  <p className="text-xs text-gray-500">{getRoleDisplay(user?.role || '')}</p>
                </div>
              </button>

              {/* Dropdown del usuario */}
              {isUserMenuOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-200">
                  <div className="px-4 py-2 border-b border-gray-100">
                    <p className="text-sm font-medium text-gray-900">{user?.username}</p>
                    <p className="text-xs text-gray-500">{user?.email}</p>
                    <p className="text-xs text-blue-600">{getRoleDisplay(user?.role || '')}</p>
                  </div>
                  
                  <a
                    href="/profile"
                    className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    onClick={() => setIsUserMenuOpen(false)}
                  >
                    <User className="w-4 h-4 mr-3" />
                    Mi Perfil
                  </a>
                  
                  <a
                    href="/settings"
                    className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    onClick={() => setIsUserMenuOpen(false)}
                  >
                    <Settings className="w-4 h-4 mr-3" />
                    Configuración
                  </a>
                  
                  <div className="border-t border-gray-100"></div>
                  
                  <button
                    onClick={() => {
                      onLogout?.();
                      setIsUserMenuOpen(false);
                    }}
                    className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                  >
                    <LogOut className="w-4 h-4 mr-3" />
                    Cerrar Sesión
                  </button>
                </div>
              )}
            </div>

            {/* Botón de menú móvil */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden p-2 text-gray-400 hover:text-gray-500"
            >
              {isMenuOpen ? (
                <X className="w-6 h-6" />
              ) : (
                <Menu className="w-6 h-6" />
              )}
            </button>
          </div>
        </div>

        {/* Menú móvil - Solo para mostrar/ocultar sidebar */}
        {isMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 border-t border-gray-200">
              <p className="text-sm text-gray-500 px-3 py-2">
                Usa el menú lateral para navegar
              </p>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
