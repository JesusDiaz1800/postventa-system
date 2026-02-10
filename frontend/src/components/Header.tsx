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
import NotificationCenter from './NotificationCenter';

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

  const userMenuRef = useRef<HTMLDivElement>(null);

  // Cerrar dropdowns al hacer clic fuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (isUserMenuOpen && userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setIsUserMenuOpen(false);
      }
    };

    if (isUserMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isUserMenuOpen]);

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
            <NotificationCenter />

            {/* Menú de usuario */}
            <div className="relative" ref={userMenuRef}>
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
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      onLogout?.();
                      setIsUserMenuOpen(false);
                    }}
                    className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors duration-200"
                    data-testid="logout-button"
                    type="button"
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
