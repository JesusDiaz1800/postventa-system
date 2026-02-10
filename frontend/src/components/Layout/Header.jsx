import React from 'react';
import { useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { usePWA } from '../../context/PWAContext';
import NotificationCenter from '../NotificationCenter';
import {
  Bars3Icon,
  ArrowRightOnRectangleIcon,
  DevicePhoneMobileIcon,
} from '@heroicons/react/24/outline';

const InstallAppButton = () => {
  const { deferredPrompt, install, isStandalone } = usePWA();
  if (isStandalone || !deferredPrompt) return null;

  return (
    <button
      onClick={install}
      className="hidden md:flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-md transition-colors"
    >
      <DevicePhoneMobileIcon className="w-5 h-5" />
      <span>Instalar App</span>
    </button>
  );
};

const Header = ({ onMenuClick }) => {
  const { user, logout } = useAuth();
  const location = useLocation();

  const getPageTitle = (pathname) => {
    const path = pathname.endsWith('/') && pathname.length > 1 ? pathname.slice(0, -1) : pathname;
    const routes = {
      '/dashboard': 'Dashboard',
      '/incidents': 'Incidencias',
      '/create-incident': 'Nueva Incidencia',
      '/reports': 'Reportes y Analíticas',
      '/users': 'Gestión de Usuarios',
      '/audit': 'Auditoría',
      '/settings': 'Configuración',
      '/documents': 'Documentos',
      '/visit-reports': 'Reportes de Visita',
    };
    if (routes[path]) return routes[path];
    if (path.includes('/incidents/')) return 'Detalle de Incidencia';
    return 'Sistema de Postventa';
  };

  const pageTitle = getPageTitle(location.pathname);

  return (
    <header className="sticky top-0 z-40 w-full bg-white border-b border-gray-200">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center gap-4">
            <button
              onClick={onMenuClick}
              className="p-2 text-gray-400 hover:text-gray-600 focus:outline-none"
            >
              <Bars3Icon className="w-6 h-6" />
            </button>

            <h1 className="text-lg font-semibold text-gray-900 truncate">
              {pageTitle}
            </h1>
          </div>

          <div className="flex items-center gap-4 sm:gap-6">
            <InstallAppButton />

            <div className="flex items-center border-x border-gray-100 px-4 sm:px-6">
              <NotificationCenter />
            </div>

            <div className="flex items-center gap-3">
              <div className="hidden text-right lg:block">
                <p className="text-sm font-medium text-gray-900">
                  {user?.full_name || user?.username}
                </p>
                <p className="text-xs text-gray-500 capitalize">
                  {user?.role || 'Usuario'}
                </p>
              </div>

              <div className="flex-shrink-0 relative">
                <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm font-medium">
                  {user?.username?.charAt(0).toUpperCase() || 'U'}
                </div>
                <div className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-green-500 border-2 border-white rounded-full"></div>
              </div>
            </div>

            <button
              onClick={logout}
              className="p-2 text-gray-400 hover:text-red-600 transition-colors"
              title="Cerrar sesión"
            >
              <ArrowRightOnRectangleIcon className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export { Header };
export default Header;
