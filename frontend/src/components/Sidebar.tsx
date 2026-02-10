"use client";

import { Logo } from './Logo';
import {
  FileText,
  Users,
  Cog,
  Shield,
  Brain,
  ClipboardList,
  Beaker,
  Truck,
  ChevronLeft,
  LayoutDashboard
} from 'lucide-react';

interface SidebarProps {
  currentPath: string;
  onNavigate: (path: string) => void;
  userName?: string;
  userRole: string;
  isOpen?: boolean;
  onClose?: () => void;
}

export function Sidebar({ currentPath, onNavigate, userName, userRole, isOpen = true, onClose }: SidebarProps) {
  const navigation = [
    { name: 'Dashboard', href: '/reports', icon: LayoutDashboard, roles: ['admin', 'administrador', 'management', 'technical_service', 'servicio_tecnico', 'tecnico', 'quality', 'supervisor', 'analyst', 'customer_service'] },
    { name: 'Incidencias', href: '/incidents', icon: FileText, roles: ['admin', 'administrador', 'management', 'technical_service', 'servicio_tecnico', 'tecnico', 'quality', 'supervisor', 'analyst', 'customer_service'] },
    { name: 'Documentos', href: '/documents', icon: FileText, roles: ['admin', 'administrador', 'management', 'technical_service', 'servicio_tecnico', 'tecnico', 'quality', 'supervisor'] },
    { name: 'Reportes de Visita', href: '/visit-reports', icon: ClipboardList, roles: ['admin', 'administrador', 'management', 'technical_service', 'servicio_tecnico', 'tecnico', 'quality', 'supervisor', 'analyst'] },
    { name: 'Calidad (Cliente)', href: '/quality-reports/client', icon: Beaker, roles: ['admin', 'administrador', 'management', 'quality', 'supervisor', 'analyst'] },
    { name: 'Calidad Interna', href: '/quality-reports/internal', icon: Beaker, roles: ['admin', 'administrador', 'management', 'quality', 'supervisor'] },
    { name: 'Reportes Proveedor', href: '/supplier-reports', icon: Truck, roles: ['admin', 'administrador', 'management', 'quality', 'supervisor'] },
    { name: 'Usuarios', href: '/users', icon: Users, roles: ['admin', 'administrador'] },
    { name: 'Chat IA', href: '/ai', icon: Brain, roles: ['admin', 'administrador', 'management', 'supervisor', 'analyst'] },
    { name: 'Configuración', href: '/settings', icon: Cog, roles: ['admin', 'administrador'] },
    { name: 'Auditoría', href: '/audit', icon: Shield, roles: ['admin', 'administrador'] },
  ];

  const filteredNavigation = navigation.filter(item => {
    if (userRole === 'admin' || userRole === 'administrador') return true;
    return item.roles.includes(userRole);
  });

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-gray-900/60 backdrop-blur-sm md:hidden transition-opacity"
          onClick={onClose}
        />
      )}

      {/* Sidebar Container: Original Professional Navy Blue */}
      <aside
        className={`fixed left-0 top-0 z-40 h-screen w-64 transform border-r border-white/5 bg-[#1e3a8a] transition-transform duration-300 ease-in-out shadow-xl ${isOpen ? 'translate-x-0' : '-translate-x-full'
          }`}
      >
        <div className="flex h-full flex-col">
          {/* Logo Area */}
          <div className="flex h-20 items-center justify-between px-6 bg-black/10 border-b border-white/5">
            <div className="h-8 w-auto cursor-pointer transform hover:scale-105 transition-transform" onClick={() => onNavigate('/reports')}>
              <Logo className="h-full w-auto" variant="white" />
            </div>
          </div>

          {/* Navigation Items */}
          <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-6 custom-scrollbar">
            {filteredNavigation.map((item) => {
              const isActive = currentPath === item.href || (item.href !== '/reports' && currentPath.startsWith(item.href));
              return (
                <button
                  key={item.name}
                  onClick={() => onNavigate(item.href)}
                  className={`group relative flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold transition-all duration-200 ${isActive
                    ? 'bg-white/10 text-white shadow-lg'
                    : 'text-blue-100 hover:bg-white/5 hover:text-white'
                    }`}
                >
                  <item.icon
                    size={18}
                    className={`transition-colors duration-200 ${isActive ? 'text-white' : 'text-blue-300 group-hover:text-white'
                      }`}
                  />
                  <span className="truncate">{item.name}</span>
                  {isActive && (
                    <div className="ml-auto h-1 w-1 rounded-full bg-blue-400" />
                  )}
                </button>
              );
            })}
          </nav>

          {/* Compact User Info / Footer */}
          <div className="border-t border-white/5 p-4 bg-black/20">
            <div className="flex items-center gap-3 px-1">
              <div className="h-9 w-9 rounded-lg bg-white/10 flex items-center justify-center text-white font-black text-[10px] uppercase border border-white/5">
                {(userName || userRole)?.substring(0, 2) || 'AD'}
              </div>
              <div className="flex flex-col min-w-0">
                <span className="text-xs font-bold text-white capitalize truncate leading-none">{userName || userRole}</span>
                <span className="text-[9px] font-bold text-blue-300/50 uppercase tracking-widest mt-1">{userRole}</span>
              </div>
            </div>

            <div className="mt-4 px-1 flex justify-between items-center opacity-30 text-[8px] font-bold text-white uppercase tracking-widest leading-none">
              <span>Polifusión S.A.</span>
              <span>v1.0.4</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
