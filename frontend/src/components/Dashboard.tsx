"use client";

import { Logo } from './Logo';
import { 
  FileText, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  TrendingUp,
  Users,
  Brain,
  BarChart3
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
      color: 'blue',
      change: '+12%',
      changeType: 'positive'
    },
    {
      name: 'Pendientes',
      value: stats.pendingIncidents,
      icon: Clock,
      color: 'yellow',
      change: '-5%',
      changeType: 'positive'
    },
    {
      name: 'Resueltas',
      value: stats.resolvedIncidents,
      icon: CheckCircle,
      color: 'green',
      change: '+8%',
      changeType: 'positive'
    },
    {
      name: 'Tiempo Promedio',
      value: `${stats.averageResolutionTime}d`,
      icon: TrendingUp,
      color: 'purple',
      change: '-2d',
      changeType: 'positive'
    },
    {
      name: 'Análisis IA',
      value: stats.aiAnalyses,
      icon: Brain,
      color: 'indigo',
      change: '+25%',
      changeType: 'positive'
    },
    {
      name: 'Usuarios Activos',
      value: stats.activeUsers,
      icon: Users,
      color: 'pink',
      change: '+3',
      changeType: 'positive'
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'abierto': return 'bg-red-100 text-red-800';
      case 'en_proceso': return 'bg-yellow-100 text-yellow-800';
      case 'resuelto': return 'bg-green-100 text-green-800';
      case 'cerrado': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critica': return 'bg-red-100 text-red-800';
      case 'alta': return 'bg-orange-100 text-orange-800';
      case 'media': return 'bg-yellow-100 text-yellow-800';
      case 'baja': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
              <p className="text-gray-600">Sistema de Gestión de Incidencias Postventa</p>
            </div>
            <div className="h-8 w-48">
              <Logo className="h-full w-full" />
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {statCards.map((stat) => {
            const Icon = stat.icon;
            return (
              <div key={stat.name} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                    <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                  </div>
                  <div className={`p-3 rounded-full bg-${stat.color}-100`}>
                    <Icon className={`h-6 w-6 text-${stat.color}-600`} />
                  </div>
                </div>
                <div className="mt-4 flex items-center">
                  <span className={`text-sm font-medium ${
                    stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {stat.change}
                  </span>
                  <span className="text-sm text-gray-500 ml-2">vs mes anterior</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Recent Incidents */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Incidencias Recientes</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Código
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Cliente
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Estado
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Prioridad
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Fecha
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {recentIncidents.map((incident) => (
                  <tr key={incident.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {incident.code}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {incident.client}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(incident.status)}`}>
                        {incident.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getPriorityColor(incident.priority)}`}>
                        {incident.priority}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(incident.createdAt).toLocaleDateString()}
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
