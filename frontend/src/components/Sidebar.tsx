"use client";

import { Logo } from './Logo';
import { motion } from 'framer-motion';
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
  LayoutDashboard,
  Sun,
  Moon
} from 'lucide-react';
import { usePermissions } from '../hooks/usePermissions';
import { useQueryClient } from '@tanstack/react-query';
import { incidentsAPI, dashboardAPI } from '../services/api';

interface SidebarProps {
  currentPath: string;
  onNavigate: (path: string) => void;
  userName?: string;
  userRole: string;
  isOpen?: boolean;
  onClose?: () => void;
}

// Versión limpia sin motor de temas - Estilo Oscuro Permanente Premium
export function Sidebar({ currentPath, onNavigate, userName, userRole, isOpen = true, onClose }: SidebarProps) {
  const { accessiblePages = [] } = usePermissions();
  const queryClient = useQueryClient();

  const prefetchData = (path: string) => {
    if (path === '/reports') {
      queryClient.prefetchQuery({
        queryKey: ['dashboard-metrics'],
        queryFn: () => dashboardAPI.getMetrics(),
        staleTime: 60000
      });
    } else if (path === '/incidents') {
      queryClient.prefetchQuery({
        queryKey: ['incidents', { page: 1, page_size: 10, search: '', estado: '' }],
        queryFn: () => incidentsAPI.list({ page: 1, page_size: 10, search: '', estado: '' }),
        staleTime: 60000
      });
    }
  };

  const operationsNav = [
    { name: 'Panel de Control', href: '/reports', icon: LayoutDashboard, roles: ['admin', 'administrador', 'management', 'technical_service', 'servicio_tecnico', 'tecnico', 'quality', 'supervisor', 'analyst', 'customer_service'] },
    { name: 'Incidencias', href: '/incidents', icon: FileText, roles: ['admin', 'administrador', 'management', 'technical_service', 'servicio_tecnico', 'tecnico', 'quality', 'supervisor', 'analyst', 'customer_service'] },
    { name: 'Documentos', href: '/documents', icon: FileText, roles: ['admin', 'administrador', 'management', 'technical_service', 'servicio_tecnico', 'tecnico', 'quality', 'supervisor'] },
    { name: 'Reportes de Visita', href: '/visit-reports', icon: ClipboardList, roles: ['admin', 'administrador', 'management', 'technical_service', 'servicio_tecnico', 'tecnico', 'quality', 'supervisor', 'analyst'] },
  ];

  const qualityNav = [
    { name: 'Calidad (Cliente)', href: '/quality-reports/client', icon: Beaker, roles: ['admin', 'administrador', 'management', 'quality', 'supervisor', 'analyst'] },
    { name: 'Calidad Interna', href: '/quality-reports/internal', icon: Beaker, roles: ['admin', 'administrador', 'management', 'quality', 'supervisor'] },
    { name: 'Reportes Proveedor', href: '/supplier-reports', icon: Truck, roles: ['admin', 'administrador', 'management', 'quality', 'supervisor'] },
  ];

  const systemNav = [
    { name: 'Usuarios', href: '/users', icon: Users, roles: ['admin', 'administrador'] },
    { name: 'Chat IA', href: '/ai', icon: Brain, roles: ['admin', 'administrador', 'management', 'supervisor', 'analyst'] },
    { name: 'Auditoría', href: '/audit', icon: Shield, roles: ['admin', 'administrador'] },
  ];

  const getRoleDisplay = (role: string) => {
    const roleMap: { [key: string]: string } = {
      'admin': 'Administrador',
      'administrador': 'Administrador',
      'management': 'Gerencia',
      'technical_service': 'Servicio Técnico',
      'servicio_tecnico': 'Servicio Técnico',
      'tecnico': 'Técnico',
      'quality': 'Calidad',
      'supervisor': 'Supervisor',
      'analyst': 'Analista',
      'analista': 'Analista',
      'customer_service': 'Atención al Cliente',
      'atencion_cliente': 'Atención al Cliente',
      'proveedor': 'Proveedor',
    };
    return roleMap[role.toLowerCase()] || role;
  };

  const filterByRole = (items: typeof operationsNav) => {
    // Map hrefs to accessible_pages keys
    const pageKeyMap: { [key: string]: string } = {
      '/reports': 'reports',
      '/incidents': 'incidents',
      '/documents': 'documents',
      '/visit-reports': 'visit-reports',
      '/quality-reports/client': 'quality-reports/client',
      '/quality-reports/internal': 'quality-reports/internal',
      '/supplier-reports': 'supplier-reports',
      '/users': 'users',
      '/ai': 'ai',
      '/audit': 'audit',
    };

    return items.filter(item => {
      if (userRole === 'admin' || userRole === 'administrador') return true;

      const pageKey = pageKeyMap[item.href];

      // If we have a specific permission key for this page, iterate
      if (pageKey) {
        // If the key is in accessiblePages, allow.
        // But for backward compatibility, if accessiblePages is empty (legacy), fallback to role.
        if (accessiblePages && accessiblePages.length > 0) {
          return accessiblePages.includes(pageKey);
        }
      }

      // Fallback to role-based
      return item.roles.includes(userRole);
    });
  };

  const renderNavItem = (item: typeof operationsNav[0]) => {
    const isActive = currentPath === item.href || (item.href !== '/reports' && currentPath.startsWith(item.href));
    return (
      <motion.button
        key={item.name}
        onClick={() => onNavigate(item.href)}
        onMouseEnter={() => prefetchData(item.href)}
        whileHover={{ x: 4 }}
        whileTap={{ scale: 0.98 }}
        className={`group relative flex w-full items-center gap-3 px-3 py-2.5 my-1 rounded-xl transition-all duration-300 outline-none overflow-hidden
          ${isActive
            ? 'bg-blue-600/10 text-blue-400 font-bold border border-blue-500/20 shadow-[0_0_15px_rgba(59,130,246,0.15)]'
            : 'text-slate-400 hover:bg-white/5 hover:text-white border border-transparent'
          }`}
      >
        {isActive && (
          <motion.div 
            layoutId="activeTab"
            className="absolute left-0 top-0 bottom-0 w-1 bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.8)]" 
          />
        )}
        <item.icon
          size={18}
          className={`flex-shrink-0 transition-all duration-300 ${isActive ? 'text-blue-400 scale-110' : 'text-slate-500 group-hover:text-slate-300'}`}
        />
        <span className="text-sm truncate font-medium tracking-wide">
          {item.name}
        </span>

        {/* Hover Glow Effect */}
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
      </motion.button>
    );
  };

  const SectionLabel = ({ label }: { label: string }) => (
    <div className="px-4 mt-8 mb-3">
      <span className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] leading-none flex items-center gap-2">
        {label}
        <div className="h-px flex-1 bg-slate-800/50" />
      </span>
    </div>
  );

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm md:hidden transition-opacity"
          onClick={onClose}
        />
      )}

      {/* Sidebar Container - Premium Deep Glass */}
      <aside
        className={`fixed left-0 top-0 z-50 h-screen w-72 flex flex-col border-r border-white/5 bg-[#030014]/95 backdrop-blur-3xl transition-all duration-500 shadow-[20px_0_50px_rgba(0,0,0,0.5)] ${isOpen ? 'translate-x-0' : '-translate-x-full'}`}
      >
        {/* Background Ambient Glow */}
        <div className="absolute top-0 left-0 w-full h-96 bg-blue-500/10 blur-[100px] pointer-events-none select-none" />
        <div className="absolute bottom-0 right-0 w-full h-96 bg-purple-500/5 blur-[100px] pointer-events-none select-none" />

        {/* Header - Integrated with Main Header */}
        <div className="relative z-10 flex h-16 items-center px-6 border-b border-white/5 bg-[#030014]/50">
          <div className="h-10 cursor-pointer opacity-90 hover:opacity-100 transition-all duration-500 hover:scale-105 filter drop-shadow-[0_0_10px_rgba(255,255,255,0.2)]" onClick={() => onNavigate('/reports')}>
            <Logo className="h-full w-auto text-white" variant="white" />
          </div>
        </div>

        {/* Navigation Scrollable */}
        <nav className="relative z-10 flex-1 overflow-y-auto px-4 py-6 space-y-1 custom-scrollbar">

          {/* Operations Section */}
          <div className="space-y-0.5">
            {filterByRole(operationsNav).map(renderNavItem)}
          </div>

          <SectionLabel label="Gestión Técnica" />
          <div className="space-y-0.5">
            {filterByRole(qualityNav).map(renderNavItem)}
          </div>

          <SectionLabel label="Administración" />
          <div className="space-y-0.5">
            {filterByRole(systemNav).map(renderNavItem)}
          </div>
        </nav>

        {/* User Footer */}
        <div className="relative z-10 border-t border-white/5 p-4 bg-[#0b1120]/50 backdrop-blur-xl">
          <div className="flex items-center gap-3 p-2 rounded-xl border border-white/5 bg-white/5 hover:bg-white/10 transition-colors group cursor-pointer">
            <div className="relative">
              <div className="absolute inset-0 bg-blue-500 blur-md opacity-20 group-hover:opacity-40 transition-opacity" />
              <div className="relative h-10 w-10 min-w-[2.5rem] rounded-xl bg-[#0f172a] border border-white/10 flex items-center justify-center shadow-lg ring-1 ring-white/5 group-hover:scale-105 transition-transform">
                <span className="font-black text-xs text-blue-400">
                  {(userName || userRole)?.substring(0, 2).toUpperCase() || 'AD'}
                </span>
              </div>
            </div>

            <div className="flex flex-col min-w-0">
              <span className="text-sm font-bold text-white truncate group-hover:text-blue-100 transition-colors">
                {userName || 'Usuario'}
              </span>
              <span className="text-[10px] text-slate-400 font-bold uppercase truncate tracking-wider">
                {getRoleDisplay(userRole || 'admin')}
              </span>
            </div>

            <div className="ml-auto opacity-0 group-hover:opacity-100 transition-opacity text-slate-400">
              <Cog size={14} />
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
