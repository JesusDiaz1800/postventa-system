"use client";

import { Logo } from './Logo';
import { 
  Home, 
  FileText, 
  BarChart3, 
  Users, 
  Cog,
  Shield,
  Brain,
  Workflow,
  ClipboardList,
  Beaker,
  Truck
} from 'lucide-react';

interface SidebarProps {
  currentPath: string;
  onNavigate: (path: string) => void;
  userRole: string;
  isOpen?: boolean;
}

export function Sidebar({ currentPath, onNavigate, userRole, isOpen = true }: SidebarProps) {
  const navigation = [
    { name: 'Reportes', href: '/reports', icon: BarChart3, roles: ['admin', 'administrador', 'management', 'technical_service', 'servicio_tecnico', 'tecnico', 'quality', 'supervisor', 'analyst', 'customer_service'] },
    { name: 'Incidencias', href: '/incidents', icon: FileText, roles: ['admin', 'administrador', 'management', 'technical_service', 'servicio_tecnico', 'tecnico', 'quality', 'supervisor', 'analyst', 'customer_service'] },
    { name: 'Documentos', href: '/documents', icon: FileText, roles: ['admin', 'administrador', 'management', 'technical_service', 'servicio_tecnico', 'tecnico', 'quality', 'supervisor'] },
    { name: 'Reportes de Visita', href: '/visit-reports', icon: ClipboardList, roles: ['admin', 'administrador', 'management', 'technical_service', 'servicio_tecnico', 'tecnico', 'quality', 'supervisor', 'analyst'] },
    { name: 'Reportes de Calidad - Cliente', href: '/quality-reports/client', icon: Beaker, roles: ['admin', 'administrador', 'management', 'quality', 'supervisor', 'analyst'] },
    { name: 'Informes Internos de Calidad', href: '/quality-reports/internal', icon: Beaker, roles: ['admin', 'administrador', 'management', 'quality', 'supervisor'] },
    { name: 'Informes para Proveedores', href: '/supplier-reports', icon: Truck, roles: ['admin', 'administrador', 'management', 'quality', 'supervisor'] },
    { name: 'Usuarios', href: '/users', icon: Users, roles: ['admin', 'administrador'] },
    { name: 'IA & Análisis', href: '/ai', icon: Brain, roles: ['admin', 'administrador', 'management', 'supervisor', 'analyst'] },
    { name: 'Workflows', href: '/workflows', icon: Workflow, roles: ['admin', 'administrador', 'management', 'supervisor'] },
    { name: 'Configuración', href: '/settings', icon: Cog, roles: ['admin', 'administrador'] },
    { name: 'Auditoría', href: '/audit', icon: Shield, roles: ['admin', 'administrador'] },
  ];

  const filteredNavigation = navigation.filter(item => {
    // Admin y administrador tienen acceso a todo
    if (userRole === 'admin' || userRole === 'administrador') return true;
    
    // Otros roles según configuración
    return item.roles.includes(userRole);
  });

  return (
    <div className={`hidden md:flex md:flex-col md:fixed md:inset-y-0 transition-all duration-300 ease-in-out z-40 ${
      isOpen ? 'md:w-64' : 'md:w-0'
    }`}>
      <div className={`flex-1 flex flex-col min-h-0 bg-gradient-to-b from-slate-900 via-blue-900 to-slate-800 border-r border-blue-800/50 shadow-2xl transition-all duration-300 ease-in-out ${
        isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
      }`}>
        {/* Logo */}
        <div className="flex items-center h-16 flex-shrink-0 px-6 border-b border-blue-800/30 bg-gradient-to-r from-blue-800/20 to-slate-800/20 backdrop-blur-sm">
          <div className="h-8 w-48">
            <Logo className="h-full w-full" />
          </div>
        </div>

        {/* Navegación */}
        <div className="flex-1 flex flex-col overflow-y-auto">
          <nav className="flex-1 px-2 py-4 space-y-1">
            {filteredNavigation.map((item) => {
              const Icon = item.icon;
              const isActive = currentPath === item.href;
              
              return (
                <button
                  key={item.name}
                  onClick={() => onNavigate(item.href)}
                  className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md w-full text-left transition-colors duration-200 ${
                    isActive
                      ? 'bg-blue-600/20 text-blue-100 border-r-2 border-blue-400 shadow-lg backdrop-blur-sm'
                      : 'text-slate-300 hover:bg-blue-800/30 hover:text-blue-100 hover:shadow-md transition-all duration-200'
                  }`}
                >
                  <Icon className={`mr-3 h-5 w-5 ${
                    isActive ? 'text-blue-300' : 'text-slate-400 group-hover:text-blue-200'
                  }`} />
                  {item.name}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Footer */}
        <div className="flex-shrink-0 flex border-t border-blue-800/30 p-4 bg-gradient-to-r from-slate-800/50 to-blue-900/50 backdrop-blur-sm">
          <div className="text-xs text-slate-300">
            <p className="font-semibold text-blue-100">Sistema de Gestión de Incidencias</p>
            <p className="text-slate-400">Polifusión S.A.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
