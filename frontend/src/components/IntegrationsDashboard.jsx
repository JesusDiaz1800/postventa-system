import React, { useState, useMemo } from 'react';
import { 
  useIntegrationStatistics,
  useExternalSystems,
  useIntegrationInstances,
  useWebhookEndpoints
} from '../hooks/useIntegrations';
import { 
  ChartBarIcon, 
  ArrowTrendingUpIcon, 
  CheckCircleIcon, 
  XCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

const IntegrationsDashboard = () => {
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');
  
  const { data: statistics, isLoading: statsLoading } = useIntegrationStatistics();
  const { data: externalSystems, isLoading: systemsLoading } = useExternalSystems();
  const { data: instances, isLoading: instancesLoading } = useIntegrationInstances();
  const { data: webhooks, isLoading: webhooksLoading } = useWebhookEndpoints();

  const isLoading = statsLoading || systemsLoading || instancesLoading || webhooksLoading;

  // Calcular métricas
  const metrics = useMemo(() => {
    if (!statistics) return {};

    const { externalSystems: systemsStats, instances: instancesStats, webhooks: webhooksStats } = statistics;

    // Métricas de sistemas externos
    const activeSystems = systemsStats?.active_systems || 0;
    const totalSystems = systemsStats?.total_systems || 0;
    const systemHealth = totalSystems > 0 ? (activeSystems / totalSystems) * 100 : 0;

    // Métricas de instancias
    const completedInstances = instancesStats?.by_status?.completed || 0;
    const failedInstances = instancesStats?.by_status?.failed || 0;
    const runningInstances = instancesStats?.by_status?.running || 0;
    const totalInstances = instancesStats?.total_instances || 0;
    const successRate = totalInstances > 0 ? (completedInstances / totalInstances) * 100 : 0;

    // Métricas de webhooks
    const activeWebhooks = webhooksStats?.active_endpoints || 0;
    const totalWebhooks = webhooksStats?.total_endpoints || 0;
    const recentRequests = webhooksStats?.recent_activity?.total_requests || 0;
    const successfulRequests = webhooksStats?.recent_activity?.successful_requests || 0;
    const webhookSuccessRate = recentRequests > 0 ? (successfulRequests / recentRequests) * 100 : 0;

    return {
      systemHealth,
      activeSystems,
      totalSystems,
      successRate,
      completedInstances,
      failedInstances,
      runningInstances,
      totalInstances,
      webhookSuccessRate,
      activeWebhooks,
      totalWebhooks,
      recentRequests,
      successfulRequests,
    };
  }, [statistics]);

  const timeRangeOptions = [
    { value: '1d', label: 'Último día' },
    { value: '7d', label: 'Últimos 7 días' },
    { value: '30d', label: 'Últimos 30 días' },
    { value: '90d', label: 'Últimos 90 días' },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard de Integraciones</h1>
          <p className="text-gray-600">Visión general del estado de las integraciones</p>
        </div>
        
        <div className="flex items-center space-x-4">
          <select
            value={selectedTimeRange}
            onChange={(e) => setSelectedTimeRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {timeRangeOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Métricas principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Salud del Sistema */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ChartBarIcon className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Salud del Sistema</p>
              <p className="text-2xl font-bold text-gray-900">
                {metrics.systemHealth?.toFixed(1) || 0}%
              </p>
            </div>
          </div>
          <div className="mt-4">
            <div className="flex items-center text-sm text-gray-600">
              <span>{metrics.activeSystems} de {metrics.totalSystems} sistemas activos</span>
            </div>
          </div>
        </div>

        {/* Tasa de Éxito */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ArrowTrendingUpIcon className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Tasa de Éxito</p>
              <p className="text-2xl font-bold text-gray-900">
                {metrics.successRate?.toFixed(1) || 0}%
              </p>
            </div>
          </div>
          <div className="mt-4">
            <div className="flex items-center text-sm text-gray-600">
              <span>{metrics.completedInstances} de {metrics.totalInstances} completadas</span>
            </div>
          </div>
        </div>

        {/* Instancias Activas */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ClockIcon className="h-8 w-8 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Instancias Activas</p>
              <p className="text-2xl font-bold text-gray-900">
                {metrics.runningInstances || 0}
              </p>
            </div>
          </div>
          <div className="mt-4">
            <div className="flex items-center text-sm text-gray-600">
              <span>{metrics.failedInstances} fallidas</span>
            </div>
          </div>
        </div>

        {/* Webhooks */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CheckCircleIcon className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Webhooks Activos</p>
              <p className="text-2xl font-bold text-gray-900">
                {metrics.activeWebhooks || 0}
              </p>
            </div>
          </div>
          <div className="mt-4">
            <div className="flex items-center text-sm text-gray-600">
              <span>{metrics.webhookSuccessRate?.toFixed(1) || 0}% éxito</span>
            </div>
          </div>
        </div>
      </div>

      {/* Gráficos y tablas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Estado de Sistemas Externos */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Estado de Sistemas Externos</h3>
          <div className="space-y-4">
            {statistics?.externalSystems?.by_type && Object.entries(statistics.externalSystems.by_type).map(([type, count]) => (
              <div key={type} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-blue-500 rounded-full mr-3"></div>
                  <span className="text-sm font-medium text-gray-700 capitalize">{type}</span>
                </div>
                <span className="text-sm text-gray-500">{count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Estado de Instancias */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Estado de Instancias</h3>
          <div className="space-y-4">
            {statistics?.instances?.by_status && Object.entries(statistics.instances.by_status).map(([status, count]) => {
              const statusConfig = {
                completed: { color: 'bg-green-500', icon: CheckCircleIcon },
                failed: { color: 'bg-red-500', icon: XCircleIcon },
                running: { color: 'bg-yellow-500', icon: ClockIcon },
                pending: { color: 'bg-gray-500', icon: ClockIcon },
                cancelled: { color: 'bg-gray-400', icon: XCircleIcon },
              };
              
              const config = statusConfig[status] || { color: 'bg-gray-500', icon: ClockIcon };
              const Icon = config.icon;
              
              return (
                <div key={status} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Icon className="h-4 w-4 text-gray-500 mr-3" />
                    <span className="text-sm font-medium text-gray-700 capitalize">{status}</span>
                  </div>
                  <span className="text-sm text-gray-500">{count}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Actividad Reciente */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Actividad Reciente de Webhooks</h3>
        <div className="overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Endpoint
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Método
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  IP
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Timestamp
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {webhooks?.results?.slice(0, 5).map((webhook) => (
                <tr key={webhook.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {webhook.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {webhook.http_method}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      webhook.is_active 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {webhook.is_active ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    -
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(webhook.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Alertas y Notificaciones */}
      {metrics.failedInstances > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex">
            <ExclamationTriangleIcon className="h-5 w-5 text-red-400" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">
                Instancias Fallidas
              </h3>
              <div className="mt-2 text-sm text-red-700">
                <p>
                  Tienes {metrics.failedInstances} instancias de integración que han fallado. 
                  Revisa los logs para más detalles.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default IntegrationsDashboard;
