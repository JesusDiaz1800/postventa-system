import React, { useState, useEffect, useMemo } from 'react';
import {
  ChartBarIcon,
  DocumentIcon,
  UserGroupIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  EyeIcon,
  Cog6ToothIcon,
  BellIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';

/**
 * Dashboard avanzado con métricas en tiempo real y análisis de rendimiento
 */
const AdvancedDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [metrics, setMetrics] = useState({
    totalIncidents: 0,
    openIncidents: 0,
    closedIncidents: 0,
    totalDocuments: 0,
    avgResolutionTime: 0,
    userActivity: 0,
    systemHealth: 100,
    performanceScore: 85
  });

  const [recentActivity, setRecentActivity] = useState([]);
  const [performanceData, setPerformanceData] = useState([]);

  // Simular datos en tiempo real
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(prev => ({
        ...prev,
        totalIncidents: Math.floor(Math.random() * 100) + 150,
        openIncidents: Math.floor(Math.random() * 20) + 10,
        closedIncidents: Math.floor(Math.random() * 80) + 120,
        totalDocuments: Math.floor(Math.random() * 500) + 800,
        avgResolutionTime: Math.floor(Math.random() * 48) + 24,
        userActivity: Math.floor(Math.random() * 50) + 30,
        systemHealth: Math.floor(Math.random() * 20) + 80,
        performanceScore: Math.floor(Math.random() * 30) + 70
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  // Métricas calculadas
  const calculatedMetrics = useMemo(() => {
    const resolutionRate = metrics.totalIncidents > 0 
      ? ((metrics.closedIncidents / metrics.totalIncidents) * 100).toFixed(1)
      : 0;

    const trend = metrics.performanceScore > 80 ? 'up' : 'down';
    
    return {
      resolutionRate: parseFloat(resolutionRate),
      trend,
      efficiency: Math.min(100, (metrics.performanceScore * 1.2))
    };
  }, [metrics]);

  // Datos de gráficos
  const chartData = useMemo(() => {
    return [
      { name: 'Lun', incidents: 12, documents: 45 },
      { name: 'Mar', incidents: 19, documents: 52 },
      { name: 'Mié', incidents: 15, documents: 38 },
      { name: 'Jue', incidents: 22, documents: 61 },
      { name: 'Vie', incidents: 18, documents: 47 },
      { name: 'Sáb', incidents: 8, documents: 23 },
      { name: 'Dom', incidents: 5, documents: 15 }
    ];
  }, []);

  const tabs = [
    { id: 'overview', name: 'Resumen', icon: ChartBarIcon },
    { id: 'performance', name: 'Rendimiento', icon: ArrowTrendingUpIcon },
    { id: 'documents', name: 'Documentos', icon: DocumentIcon },
    { id: 'users', name: 'Usuarios', icon: UserGroupIcon },
    { id: 'security', name: 'Seguridad', icon: ShieldCheckIcon },
    { id: 'settings', name: 'Configuración', icon: Cog6ToothIcon }
  ];

  const MetricCard = ({ title, value, subtitle, icon: Icon, trend, color = 'blue' }) => (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
          {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
        </div>
        <div className={`p-3 rounded-lg bg-${color}-50`}>
          <Icon className={`h-6 w-6 text-${color}-600`} />
        </div>
      </div>
      {trend && (
        <div className="mt-4 flex items-center">
          {trend === 'up' ? (
            <ArrowTrendingUpIcon className="h-4 w-4 text-green-500 mr-1" />
          ) : (
            <ArrowTrendingDownIcon className="h-4 w-4 text-red-500 mr-1" />
          )}
          <span className={`text-sm font-medium ${trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
            {trend === 'up' ? '+' : '-'}5.2%
          </span>
          <span className="text-sm text-gray-500 ml-1">vs mes anterior</span>
        </div>
      )}
    </div>
  );

  const ActivityItem = ({ activity, time, type }) => (
    <div className="flex items-center space-x-3 py-3 border-b border-gray-100 last:border-b-0">
      <div className={`p-2 rounded-full ${
        type === 'success' ? 'bg-green-100' : 
        type === 'warning' ? 'bg-yellow-100' : 
        'bg-blue-100'
      }`}>
        {type === 'success' ? (
          <CheckCircleIcon className="h-4 w-4 text-green-600" />
        ) : type === 'warning' ? (
          <ExclamationTriangleIcon className="h-4 w-4 text-yellow-600" />
        ) : (
          <EyeIcon className="h-4 w-4 text-blue-600" />
        )}
      </div>
      <div className="flex-1">
        <p className="text-sm font-medium text-gray-900">{activity}</p>
        <p className="text-xs text-gray-500">{time}</p>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <ChartBarIcon className="h-8 w-8 text-indigo-600" />
              <h1 className="text-2xl font-bold text-gray-900">Dashboard Avanzado</h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span>Sistema Activo</span>
              </div>
              <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100">
                <BellIcon className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="mb-8">
          <nav className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? 'border-indigo-500 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Contenido del tab activo */}
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Métricas principales */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <MetricCard
                title="Total Incidencias"
                value={metrics.totalIncidents}
                subtitle={`${metrics.openIncidents} abiertas`}
                icon={ExclamationTriangleIcon}
                trend="up"
                color="red"
              />
              <MetricCard
                title="Documentos"
                value={metrics.totalDocuments}
                subtitle="Total en sistema"
                icon={DocumentIcon}
                trend="up"
                color="blue"
              />
              <MetricCard
                title="Tiempo Promedio"
                value={`${metrics.avgResolutionTime}h`}
                subtitle="Resolución"
                icon={ClockIcon}
                trend="down"
                color="green"
              />
              <MetricCard
                title="Eficiencia"
                value={`${calculatedMetrics.efficiency.toFixed(0)}%`}
                subtitle="Rendimiento del sistema"
                icon={CheckCircleIcon}
                trend={calculatedMetrics.trend}
                color="purple"
              />
            </div>

            {/* Gráficos y actividad reciente */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Gráfico de actividad semanal */}
              <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Actividad Semanal</h3>
                <div className="space-y-4">
                  {chartData.map((day, index) => (
                    <div key={day.name} className="flex items-center space-x-4">
                      <div className="w-12 text-sm text-gray-600">{day.name}</div>
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <div className="flex-1 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-blue-500 h-2 rounded-full" 
                              style={{ width: `${(day.incidents / 25) * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-sm text-gray-600 w-8">{day.incidents}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className="flex-1 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-green-500 h-2 rounded-full" 
                              style={{ width: `${(day.documents / 70) * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-sm text-gray-600 w-8">{day.documents}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="flex items-center space-x-4 mt-4 pt-4 border-t border-gray-200">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                    <span className="text-sm text-gray-600">Incidencias</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <span className="text-sm text-gray-600">Documentos</span>
                  </div>
                </div>
              </div>

              {/* Actividad reciente */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Actividad Reciente</h3>
                <div className="space-y-2">
                  <ActivityItem
                    activity="Nueva incidencia creada #INC-2025-001"
                    time="Hace 5 minutos"
                    type="info"
                  />
                  <ActivityItem
                    activity="Documento aprobado por calidad"
                    time="Hace 15 minutos"
                    type="success"
                  />
                  <ActivityItem
                    activity="Alerta: Sistema con alta carga"
                    time="Hace 30 minutos"
                    type="warning"
                  />
                  <ActivityItem
                    activity="Usuario nuevo registrado"
                    time="Hace 1 hora"
                    type="info"
                  />
                  <ActivityItem
                    activity="Backup completado exitosamente"
                    time="Hace 2 horas"
                    type="success"
                  />
                </div>
              </div>
            </div>

            {/* Estado del sistema */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Estado del Sistema</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600">{metrics.systemHealth}%</div>
                  <p className="text-sm text-gray-600">Salud del Sistema</p>
                  <div className="mt-2 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-500 h-2 rounded-full" 
                      style={{ width: `${metrics.systemHealth}%` }}
                    ></div>
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600">{metrics.userActivity}</div>
                  <p className="text-sm text-gray-600">Usuarios Activos</p>
                  <div className="mt-2 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full" 
                      style={{ width: `${(metrics.userActivity / 100) * 100}%` }}
                    ></div>
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-purple-600">{calculatedMetrics.resolutionRate}%</div>
                  <p className="text-sm text-gray-600">Tasa de Resolución</p>
                  <div className="mt-2 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-purple-500 h-2 rounded-full" 
                      style={{ width: `${calculatedMetrics.resolutionRate}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'performance' && (
          <div className="space-y-8">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Análisis de Rendimiento</h3>
              <p className="text-gray-600">Métricas detalladas de rendimiento del sistema...</p>
            </div>
          </div>
        )}

        {activeTab === 'documents' && (
          <div className="space-y-8">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Gestión de Documentos</h3>
              <p className="text-gray-600">Análisis y gestión avanzada de documentos...</p>
            </div>
          </div>
        )}

        {activeTab === 'users' && (
          <div className="space-y-8">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Gestión de Usuarios</h3>
              <p className="text-gray-600">Administración y análisis de usuarios...</p>
            </div>
          </div>
        )}

        {activeTab === 'security' && (
          <div className="space-y-8">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Seguridad del Sistema</h3>
              <p className="text-gray-600">Monitoreo de seguridad y auditoría...</p>
            </div>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="space-y-8">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Configuración Avanzada</h3>
              <p className="text-gray-600">Configuraciones del sistema y personalización...</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdvancedDashboard;
