import React, { useState, useEffect } from 'react';
import { 
  useMonitoringRules, useAlerts, useHealthChecks, useSystemMetrics,
  useMonitoringStatistics, useAlertStatistics, useHealthCheckStatistics,
  useExecuteMonitoringRule, useExecuteHealthCheck, useAcknowledgeAlert,
  useResolveAlert
} from '../hooks/useMonitoring';
import { 
  ExclamationTriangleIcon, CheckCircleIcon, XCircleIcon,
  ClockIcon, ChartBarIcon, ServerIcon, BellIcon,
  PlayIcon, PauseIcon, StopIcon, EyeIcon
} from '@heroicons/react/24/outline';

const MonitoringDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedAlert, setSelectedAlert] = useState(null);
  
  // Hooks para datos
  const { data: rules, isLoading: rulesLoading } = useMonitoringRules();
  const { data: alerts, isLoading: alertsLoading } = useAlerts();
  const { data: healthChecks, isLoading: healthChecksLoading } = useHealthChecks();
  const { data: systemMetrics, isLoading: systemMetricsLoading } = useSystemMetrics();
  const { data: monitoringStats } = useMonitoringStatistics();
  const { data: alertStats } = useAlertStatistics();
  const { data: healthCheckStats } = useHealthCheckStatistics();
  
  // Hooks para acciones
  const executeRuleMutation = useExecuteMonitoringRule();
  const executeHealthCheckMutation = useExecuteHealthCheck();
  const acknowledgeAlertMutation = useAcknowledgeAlert();
  const resolveAlertMutation = useResolveAlert();
  
  // Estado para filtros
  const [filters, setFilters] = useState({
    status: '',
    severity: '',
    type: '',
    dateFrom: '',
    dateTo: ''
  });
  
  // Función para formatear fecha
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString('es-ES');
  };
  
  // Función para formatear duración
  const formatDuration = (seconds) => {
    if (!seconds) return 'N/A';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };
  
  // Función para obtener color del estado
  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
      case 'completed':
      case 'resolved':
        return 'text-green-600 bg-green-100';
      case 'running':
      case 'active':
        return 'text-blue-600 bg-blue-100';
      case 'unhealthy':
      case 'failed':
        return 'text-red-600 bg-red-100';
      case 'pending':
      case 'degraded':
        return 'text-yellow-600 bg-yellow-100';
      case 'acknowledged':
        return 'text-orange-600 bg-orange-100';
      case 'cancelled':
      case 'suppressed':
        return 'text-gray-600 bg-gray-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };
  
  // Función para obtener color de severidad
  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'low':
        return 'text-green-600 bg-green-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'high':
        return 'text-orange-600 bg-orange-100';
      case 'critical':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };
  
  // Función para obtener icono del estado
  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
      case 'completed':
      case 'resolved':
        return <CheckCircleIcon className="h-4 w-4" />;
      case 'running':
      case 'active':
        return <ClockIcon className="h-4 w-4" />;
      case 'unhealthy':
      case 'failed':
        return <XCircleIcon className="h-4 w-4" />;
      case 'pending':
      case 'degraded':
        return <ExclamationTriangleIcon className="h-4 w-4" />;
      case 'acknowledged':
        return <EyeIcon className="h-4 w-4" />;
      case 'cancelled':
      case 'suppressed':
        return <StopIcon className="h-4 w-4" />;
      default:
        return <ExclamationTriangleIcon className="h-4 w-4" />;
    }
  };
  
  // Función para ejecutar regla
  const handleExecuteRule = async (ruleId) => {
    try {
      await executeRuleMutation.mutateAsync(ruleId);
      alert('Regla ejecutada exitosamente');
    } catch (error) {
      alert(`Error ejecutando regla: ${error.message}`);
    }
  };
  
  // Función para ejecutar verificación de salud
  const handleExecuteHealthCheck = async (healthCheckId) => {
    try {
      await executeHealthCheckMutation.mutateAsync(healthCheckId);
      alert('Verificación de salud ejecutada exitosamente');
    } catch (error) {
      alert(`Error ejecutando verificación: ${error.message}`);
    }
  };
  
  // Función para reconocer alerta
  const handleAcknowledgeAlert = async (alertId) => {
    try {
      await acknowledgeAlertMutation.mutateAsync(alertId);
      alert('Alerta reconocida exitosamente');
    } catch (error) {
      alert(`Error reconociendo alerta: ${error.message}`);
    }
  };
  
  // Función para resolver alerta
  const handleResolveAlert = async (alertId) => {
    try {
      await resolveAlertMutation.mutateAsync(alertId);
      alert('Alerta resuelta exitosamente');
    } catch (error) {
      alert(`Error resolviendo alerta: ${error.message}`);
    }
  };
  
  // Renderizar vista general
  const renderOverview = () => (
    <div className="space-y-6">
      {/* Estadísticas principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <ChartBarIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Reglas</p>
              <p className="text-2xl font-bold text-gray-900">
                {monitoringStats?.total_rules || 0}
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-lg">
              <BellIcon className="h-6 w-6 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Alertas Activas</p>
              <p className="text-2xl font-bold text-gray-900">
                {monitoringStats?.active_alerts || 0}
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <ServerIcon className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Verificaciones Saludables</p>
              <p className="text-2xl font-bold text-gray-900">
                {monitoringStats?.health_checks_healthy || 0}
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <ChartBarIcon className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Métricas del Sistema</p>
              <p className="text-2xl font-bold text-gray-900">
                {monitoringStats?.system_metrics_count || 0}
              </p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Gráficos y métricas adicionales */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Alertas por severidad */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Alertas por Severidad</h3>
          <div className="space-y-3">
            {alertStats?.by_severity && Object.entries(alertStats.by_severity).map(([severity, count]) => (
              <div key={severity} className="flex justify-between items-center">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(severity)}`}>
                  {severity.toUpperCase()}
                </span>
                <span className="text-sm font-medium text-gray-900">{count}</span>
              </div>
            ))}
          </div>
        </div>
        
        {/* Estado de verificaciones de salud */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Estado de Verificaciones de Salud</h3>
          <div className="space-y-3">
            {healthCheckStats?.by_status && Object.entries(healthCheckStats.by_status).map(([status, count]) => (
              <div key={status} className="flex justify-between items-center">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(status)}`}>
                  {getStatusIcon(status)}
                  <span className="ml-1 capitalize">{status}</span>
                </span>
                <span className="text-sm font-medium text-gray-900">{count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
  
  // Renderizar lista de reglas
  const renderRules = () => (
    <div className="bg-white shadow rounded-lg">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Reglas de Monitoreo</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Nombre
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Tipo
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Métrica
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Umbral
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Severidad
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Estado
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {rulesLoading ? (
              <tr>
                <td colSpan="7" className="px-6 py-4 text-center text-gray-500">
                  Cargando reglas...
                </td>
              </tr>
            ) : rules?.length === 0 ? (
              <tr>
                <td colSpan="7" className="px-6 py-4 text-center text-gray-500">
                  No hay reglas de monitoreo
                </td>
              </tr>
            ) : (
              rules?.map((rule) => (
                <tr key={rule.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{rule.name}</div>
                      <div className="text-sm text-gray-500">{rule.description}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-900 capitalize">{rule.metric_type}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-900">{rule.metric_name}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-900">{rule.threshold_value}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(rule.severity)}`}>
                      {rule.severity.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${rule.is_active ? 'text-green-600 bg-green-100' : 'text-gray-600 bg-gray-100'}`}>
                      {rule.is_active ? 'Activa' : 'Inactiva'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => handleExecuteRule(rule.id)}
                      disabled={executeRuleMutation.isPending}
                      className="text-blue-600 hover:text-blue-900 disabled:opacity-50"
                    >
                      <PlayIcon className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
  
  // Renderizar lista de alertas
  const renderAlerts = () => (
    <div className="bg-white shadow rounded-lg">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Alertas</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Título
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Regla
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Severidad
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Estado
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Activada
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {alertsLoading ? (
              <tr>
                <td colSpan="6" className="px-6 py-4 text-center text-gray-500">
                  Cargando alertas...
                </td>
              </tr>
            ) : alerts?.length === 0 ? (
              <tr>
                <td colSpan="6" className="px-6 py-4 text-center text-gray-500">
                  No hay alertas
                </td>
              </tr>
            ) : (
              alerts?.map((alert) => (
                <tr key={alert.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{alert.title}</div>
                      <div className="text-sm text-gray-500">{alert.message}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-900">{alert.rule_name}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(alert.severity)}`}>
                      {alert.severity.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(alert.status)}`}>
                      {getStatusIcon(alert.status)}
                      <span className="ml-1 capitalize">{alert.status}</span>
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(alert.triggered_at)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      {alert.status === 'active' && (
                        <button
                          onClick={() => handleAcknowledgeAlert(alert.id)}
                          disabled={acknowledgeAlertMutation.isPending}
                          className="text-orange-600 hover:text-orange-900 disabled:opacity-50"
                        >
                          <EyeIcon className="h-4 w-4" />
                        </button>
                      )}
                      {alert.status === 'acknowledged' && (
                        <button
                          onClick={() => handleResolveAlert(alert.id)}
                          disabled={resolveAlertMutation.isPending}
                          className="text-green-600 hover:text-green-900 disabled:opacity-50"
                        >
                          <CheckCircleIcon className="h-4 w-4" />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
  
  // Renderizar lista de verificaciones de salud
  const renderHealthChecks = () => (
    <div className="bg-white shadow rounded-lg">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Verificaciones de Salud</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Nombre
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Tipo
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Estado
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Última Verificación
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {healthChecksLoading ? (
              <tr>
                <td colSpan="5" className="px-6 py-4 text-center text-gray-500">
                  Cargando verificaciones...
                </td>
              </tr>
            ) : healthChecks?.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-4 text-center text-gray-500">
                  No hay verificaciones de salud
                </td>
              </tr>
            ) : (
              healthChecks?.map((healthCheck) => (
                <tr key={healthCheck.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{healthCheck.name}</div>
                      <div className="text-sm text-gray-500">{healthCheck.description}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-900 capitalize">{healthCheck.check_type}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(healthCheck.status)}`}>
                      {getStatusIcon(healthCheck.status)}
                      <span className="ml-1 capitalize">{healthCheck.status}</span>
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(healthCheck.last_check)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => handleExecuteHealthCheck(healthCheck.id)}
                      disabled={executeHealthCheckMutation.isPending}
                      className="text-blue-600 hover:text-blue-900 disabled:opacity-50"
                    >
                      <PlayIcon className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
  
  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard de Monitoreo</h1>
        <p className="text-gray-600">Monitorea el estado del sistema y gestiona alertas</p>
      </div>
      
      {/* Tabs */}
      <div className="mb-6">
        <nav className="flex space-x-8">
          {[
            { id: 'overview', name: 'Vista General' },
            { id: 'rules', name: 'Reglas' },
            { id: 'alerts', name: 'Alertas' },
            { id: 'health-checks', name: 'Verificaciones de Salud' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.name}
            </button>
          ))}
        </nav>
      </div>
      
      {/* Contenido de tabs */}
      {activeTab === 'overview' && renderOverview()}
      {activeTab === 'rules' && renderRules()}
      {activeTab === 'alerts' && renderAlerts()}
      {activeTab === 'health-checks' && renderHealthChecks()}
    </div>
  );
};

export default MonitoringDashboard;
