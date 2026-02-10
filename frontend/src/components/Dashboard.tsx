"use client";

import { Logo } from './Logo';
import { InteractivePieChart } from './InteractivePieChart';
import {
  FileText,
  AlertTriangle,
  CheckCircle,
  Clock,
  TrendingUp,
  Users,
  Brain,
  BarChart3,
  Sparkles
} from 'lucide-react';

interface DashboardProps {
  stats: {
    totalIncidents: number;
    pendingIncidents: number;
    resolvedIncidents: number;
    averageResolutionTime: number;
    aiAnalyses: number;
    activeUsers: number;
  };
  recentIncidents: Array<{
    id: string;
    code: string;
    client: string;
    status: string;
    priority: string;
    createdAt: string;
  }>;
}

export function Dashboard({ stats, recentIncidents }: DashboardProps) {
  const statCards = [
    {
      name: 'Total Incidencias',
      value: stats.totalIncidents,
      icon: FileText,
      gradient: 'from-blue-500 to-indigo-600',
      bgGradient: 'from-blue-50 to-indigo-50',
      change: '+12%',
      changeType: 'positive'
    },
    {
      name: 'Pendientes',
      value: stats.pendingIncidents,
      icon: Clock,
      gradient: 'from-amber-500 to-orange-600',
      bgGradient: 'from-amber-50 to-orange-50',
      change: '-5%',
      changeType: 'positive'
    },
    {
      name: 'Resueltas',
      value: stats.resolvedIncidents,
      icon: CheckCircle,
      gradient: 'from-emerald-500 to-green-600',
      bgGradient: 'from-emerald-50 to-green-50',
      change: '+8%',
      changeType: 'positive'
    },
    {
      name: 'Tiempo Promedio',
      value: `${stats.averageResolutionTime}d`,
      icon: TrendingUp,
      gradient: 'from-purple-500 to-pink-600',
      bgGradient: 'from-purple-50 to-pink-50',
      change: '-2d',
      changeType: 'positive'
    },
    {
      name: 'Análisis IA',
      value: stats.aiAnalyses,
      icon: Brain,
      gradient: 'from-cyan-500 to-blue-600',
      bgGradient: 'from-cyan-50 to-blue-50',
      change: '+25%',
      changeType: 'positive'
    },
    {
      name: 'Usuarios Activos',
      value: stats.activeUsers,
      icon: Users,
      gradient: 'from-rose-500 to-pink-600',
      bgGradient: 'from-rose-50 to-pink-50',
      change: '+3',
      changeType: 'positive'
    }
  ];

  // Datos de ejemplo para el gráfico de torta con subcategorías
  const incidentCategoryData = [
    {
      name: 'Fallas Técnicas',
      value: 45,
      color: '#3b82f6',
      subcategories: [
        { name: 'Rotura de Tubería', value: 18, color: '#60a5fa' },
        { name: 'Falla de Accesorios', value: 15, color: '#3b82f6' },
        { name: 'Defecto de Fabricación', value: 12, color: '#1d4ed8' }
      ]
    },
    {
      name: 'Garantías',
      value: 30,
      color: '#10b981',
      subcategories: [
        { name: 'Producto Defectuoso', value: 15, color: '#34d399' },
        { name: 'Instalación Incorrecta', value: 10, color: '#10b981' },
        { name: 'Desgaste Prematuro', value: 5, color: '#059669' }
      ]
    },
    {
      name: 'Consultas',
      value: 20,
      color: '#f59e0b',
      subcategories: [
        { name: 'Especificaciones Técnicas', value: 12, color: '#fbbf24' },
        { name: 'Instalación', value: 8, color: '#f59e0b' }
      ]
    },
    {
      name: 'Reclamos',
      value: 15,
      color: '#ef4444',
      subcategories: [
        { name: 'Entrega Tardía', value: 8, color: '#f87171' },
        { name: 'Producto Incorrecto', value: 7, color: '#ef4444' }
      ]
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'abierto': return 'bg-red-100 text-red-700 border border-red-200';
      case 'en_proceso': return 'bg-amber-100 text-amber-700 border border-amber-200';
      case 'resuelto': return 'bg-emerald-100 text-emerald-700 border border-emerald-200';
      case 'cerrado': return 'bg-slate-100 text-slate-700 border border-slate-200';
      default: return 'bg-slate-100 text-slate-700 border border-slate-200';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critica': return 'bg-red-100 text-red-700 border border-red-200';
      case 'alta': return 'bg-orange-100 text-orange-700 border border-orange-200';
      case 'media': return 'bg-yellow-100 text-yellow-700 border border-yellow-200';
      case 'baja': return 'bg-green-100 text-green-700 border border-green-200';
      default: return 'bg-slate-100 text-slate-700 border border-slate-200';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/20">
      {/* Header Premium con glassmorphism sutil */}
      <div className="bg-white/80 backdrop-blur-md shadow-sm border-b border-slate-200/60 sticky top-0 z-10">
        <div className="w-full px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-slate-800 to-slate-600 bg-clip-text text-transparent">
                Dashboard
              </h1>
              <p className="text-slate-600 text-sm mt-1">Sistema de Gestión de Incidencias Postventa</p>
            </div>
            <div className="h-8 w-48">
              <Logo className="h-full w-full" />
            </div>
          </div>
        </div>
      </div>

      <div className="w-full px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards Premium con glassmorphism */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {statCards.map((stat) => {
            const Icon = stat.icon;
            return (
              <div
                key={stat.name}
                className="group relative bg-white/70 backdrop-blur-sm rounded-2xl border border-slate-200/60 p-6 shadow-lg transition-all duration-300 hover:shadow-xl hover:scale-[1.02] hover:border-slate-300/60"
              >
                {/* Glow effect sutil en hover */}
                <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${stat.bgGradient} opacity-0 group-hover:opacity-20 transition-opacity duration-300`}></div>

                <div className="relative flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-600 mb-1">{stat.name}</p>
                    <p className="text-3xl font-black bg-gradient-to-r from-slate-800 to-slate-600 bg-clip-text text-transparent">
                      {stat.value}
                    </p>
                  </div>
                  <div className={`p-3.5 rounded-xl bg-gradient-to-br ${stat.gradient} shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                    <Icon className="h-7 w-7 text-white" />
                  </div>
                </div>

                <div className="relative mt-4 flex items-center gap-2">
                  <span className={`text-sm font-bold ${stat.changeType === 'positive' ? 'text-emerald-600' : 'text-red-600'}`}>
                    {stat.change}
                  </span>
                  <span className="text-sm text-slate-500">vs mes anterior</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Gráfico Interactivo de Torta */}
        <div className="mb-8">
          <InteractivePieChart data={incidentCategoryData} />
        </div>

        {/* Recent Incidents Table Premium */}
        <div className="bg-white/70 backdrop-blur-sm rounded-2xl border border-slate-200/60 shadow-lg overflow-hidden">
          <div className="px-6 py-5 border-b border-slate-200/60 bg-gradient-to-r from-slate-50 to-transparent">
            <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-blue-500" />
              Incidencias Recientes
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200/60">
              <thead className="bg-slate-50/50">
                <tr>
                  <th className="px-6 py-3.5 text-left text-xs font-bold text-slate-600 uppercase tracking-wider">
                    Código
                  </th>
                  <th className="px-6 py-3.5 text-left text-xs font-bold text-slate-600 uppercase tracking-wider">
                    Cliente
                  </th>
                  <th className="px-6 py-3.5 text-left text-xs font-bold text-slate-600 uppercase tracking-wider">
                    Estado
                  </th>
                  <th className="px-6 py-3.5 text-left text-xs font-bold text-slate-600 uppercase tracking-wider">
                    Prioridad
                  </th>
                  <th className="px-6 py-3.5 text-left text-xs font-bold text-slate-600 uppercase tracking-wider">
                    Fecha
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white/30 divide-y divide-slate-200/40">
                {recentIncidents.map((incident) => (
                  <tr key={incident.id} className="hover:bg-white/60 transition-colors duration-150">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-slate-800">
                      {incident.code}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                      {incident.client}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-3 py-1 text-xs font-bold rounded-full ${getStatusColor(incident.status)}`}>
                        {incident.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-3 py-1 text-xs font-bold rounded-full ${getPriorityColor(incident.priority)}`}>
                        {incident.priority}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                      {new Date(incident.createdAt).toLocaleDateString('es-ES', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric'
                      })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
