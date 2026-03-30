import React, { useState, useRef, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { usePWA } from '../../context/PWAContext';
import NotificationCenter from '../NotificationCenter';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Bars3Icon,
  ArrowRightOnRectangleIcon,
  DevicePhoneMobileIcon,
  UserIcon,
  MagnifyingGlassIcon,
  PlusIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline';
import LogoutModal from '../LogoutModal';

const InstallAppButton = () => {
  const { deferredPrompt, install, isStandalone } = usePWA();
  if (isStandalone || !deferredPrompt) return null;

  return (
    <button
      onClick={install}
      className="hidden lg:flex items-center gap-2 px-3 py-1.5 text-[10px] font-black text-blue-400 bg-blue-500/10 border border-blue-500/20 rounded-lg hover:bg-blue-500/20 transition-all uppercase tracking-widest"
    >
      <DevicePhoneMobileIcon className="w-3.5 h-3.5" />
      <span>Instalar App</span>
    </button>
  );
};

const CountryFlag = () => {
  const [country, setCountry] = useState({ code: 'CL', flag: '🇨🇱' });

  useEffect(() => {
    const code = localStorage.getItem('country_code') || 'CL';
    const countryMap = {
      'CL': { code: 'CL', flag: '🇨🇱', path: '/assets/flags/cl.png' },
      'PE': { code: 'PE', flag: '🇵🇪', path: '/assets/flags/pe.png' },
      'CO': { code: 'CO', flag: '🇨🇴', path: '/assets/flags/co.png' }
    };
    setCountry(countryMap[code] || countryMap['CL']);
  }, []);

  return (
    <div className="flex items-center justify-center w-14 h-9 overflow-hidden shadow-sm" title={`País: ${country.code}`}>
      <img
        src={country.path}
        alt={country.code}
        className="w-full h-full object-cover"
        onError={(e) => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'block'; }}
      />
      <span className="text-sm hidden">{country.flag}</span>
    </div>
  );
};

const Header = ({ onMenuClick }) => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const userMenuRef = useRef(null);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isLogoutModalOpen, setIsLogoutModalOpen] = useState(false);
  const searchInputRef = useRef(null);

  const handleLogoutConfirm = () => {
    logout();
    setIsLogoutModalOpen(false);
  };

  // Cerrar dropdown al hacer clic fuera
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (isUserMenuOpen && userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setIsUserMenuOpen(false);
      }
    };
    if (isUserMenuOpen) document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isUserMenuOpen]);

  useEffect(() => {
    if (isSearchOpen && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isSearchOpen]);

  const toggleSearch = () => setIsSearchOpen(!isSearchOpen);

  const getPageTitle = (pathname) => {
    const path = pathname.endsWith('/') && pathname.length > 1 ? pathname.slice(0, -1) : pathname;
    const routes = {
      '/dashboard': 'Analítica y Rendimiento',
      '/incidents': 'Gestión de Incidencias',
      '/create-incident': 'Nueva Incidencia',
      '/reports': 'Reportes y Analíticas',
      '/users': 'Gestión de Usuarios',
      '/audit': 'Auditoría del Sistema',
      '/documents': 'Gestión Documental',
      '/visit-reports': 'Reportes de Visita',
      '/quality-reports/client': 'Calidad - Cliente',
      '/quality-reports/internal': 'Calidad - Interna',
      '/supplier-reports': 'Reportes a Proveedores',
      '/ai': 'Inteligencia Artificial'
    };
    if (routes[path]) return routes[path];
    if (path.includes('/incidents/')) return 'Detalle de Incidencia';
    return 'Sistema de Postventa';
  };

  const pageTitle = getPageTitle(location.pathname);

  return (
    <header className="sticky top-0 z-40 w-full no-print bg-[#030014]/80 backdrop-blur-xl border-b border-white/5">
      <div className="h-16 flex justify-between items-center px-8 transition-all duration-300">

        {/* Left Section: Menu & Title */}
        <div className="flex items-center gap-6">
          <button
            onClick={onMenuClick}
            className="p-2 text-slate-400 hover:text-white hover:bg-white/5 rounded-xl transition-all active:scale-95"
          >
            <Bars3Icon className="w-6 h-6" />
          </button>

          <div className="hidden sm:block">
            <h1 className="text-sm font-black text-white uppercase tracking-widest flex items-center gap-3">
              {pageTitle}
              <span className="w-1 h-1 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]"></span>
              <span className="text-[10px] text-slate-500 font-bold opacity-50">v 1.0</span>
            </h1>
          </div>
        </div>

        {/* Right Section: Actions & Profile */}
        <div className="flex items-center gap-4">

          {/* Quick Search - Interactive Version */}
          <div className="relative flex items-center">
            <AnimatePresence>
              {isSearchOpen && (
                <motion.div
                  initial={{ width: 0, opacity: 0 }}
                  animate={{ width: 240, opacity: 1 }}
                  exit={{ width: 0, opacity: 0 }}
                  className="overflow-hidden mr-2"
                >
                  <input
                    ref={searchInputRef}
                    type="text"
                    placeholder="BUSCAR..."
                    className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-[10px] font-bold text-white uppercase tracking-widest focus:outline-none focus:border-blue-500/50 transition-all placeholder:text-slate-600"
                    onBlur={() => !searchInputRef.current?.value && setIsSearchOpen(false)}
                    onKeyDown={(e) => e.key === 'Enter' && e.currentTarget.value && (window.location.search = `?q=${e.currentTarget.value}`)}
                  />
                </motion.div>
              )}
            </AnimatePresence>
            <button
              onClick={toggleSearch}
              className={`flex items-center gap-2 px-3 py-1.5 text-[10px] font-bold transition-all uppercase tracking-widest group rounded-lg ${isSearchOpen ? 'text-blue-400 bg-blue-500/10' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}
            >
              <MagnifyingGlassIcon className={`w-4 h-4 group-hover:scale-110 transition-transform ${isSearchOpen ? 'scale-110' : ''}`} />
              <span className="hidden lg:inline">{isSearchOpen ? 'BUSCANDO' : 'Búsqueda'}</span>
            </button>
          </div>

          <div className="flex items-center ml-2">
            <NotificationCenter />
          </div>

          <div className="h-4 w-px bg-white/10 mx-1" />

          <CountryFlag />

          <div className="h-4 w-px bg-white/10 mx-1" />

          {/* Direct Logout Action */}
          <button
            onClick={() => setIsLogoutModalOpen(true)}
            className="p-2 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-xl transition-all active:scale-95 group"
            title="Cerrar Sesión"
          >
            <ArrowRightOnRectangleIcon className="w-6 h-6 group-hover:rotate-12 transition-transform" />
          </button>
        </div>
      </div>
      <LogoutModal
        isOpen={isLogoutModalOpen}
        onClose={() => setIsLogoutModalOpen(false)}
        onConfirm={handleLogoutConfirm}
      />
    </header>
  );
};

export { Header };
export default Header;
