import React, { useState, useEffect } from 'react';
import {
  HeartIcon,
  CpuChipIcon,
  ServerIcon,
  DatabaseIcon,
  WifiIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ClockIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline';

/**
 * Monitor de salud del sistema en tiempo real
 */
const SystemHealthMonitor = () => {
  const [systemHealth, setSystemHealth] = useState({
    overall: 95,
    server: 98,
    database: 92,
    network: 96,
    storage: 88,
    memory: 85,
    cpu: 72,
    uptime: '15d 8h 23m'
  });

  const [alerts, setAlerts] = useState([]);
  const [metrics, setMetrics] = useState([]);
  const [isExpanded, setIsExpanded] = useState(false);

  // Simular datos en tiempo real
  useEffect(() => {
    const interval = setInterval(() => {
      setSystemHealth(prev => ({
        ...prev,
        overall: Math.max(60, Math.min(100, prev.overall + (Math.random() - 0.5) * 10)),
        server: Math.max(80, Math.min(100, prev.server + (Math.random() - 0.5) * 5)),
        database: Math.max(85, Math.min(100, prev.database + (Math.random() - 0.5) * 8)),
        network: Math.max(90, Math.min(100, prev.network + (Math.random() - 0.5) * 3)),
        storage: Math.max(70, Math.min(100, prev.storage + (Math.random() - 0.5) * 6)),
        memory: Math.max(60, Math.min(95, prev.memory + (Math.random() - 0.5) * 12)),
        cpu: Math.max(50, Math.min(90, prev.cpu + (Math.random() - 0.5) * 15))
      }));

      // Generar alertas ocasionales
      if (Math.random() < 0.1) {
        const alertTypes = [
          { type: 'warning', message: 'Uso de CPU alto detectado', component: 'CPU' },
          { type: 'info', message: 'Backup automático completado', component: 'Sistema' },
          { type: 'error', message: 'Conexión de base de datos lenta', component: 'Base de Datos' },
          { type: 'success', message: 'Optimización de memoria aplicada', component: 'Memoria' }
        ];
        
        const alert = alertTypes[Math.floor(Math.random() * alertTypes.length)];
        setAlerts(prev => [{
          id: Date.now(),
          ...alert,
          timestamp: new Date()
        }, ...prev.slice(0, 9)]);
      }
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const getHealthColor = (value) => {
    if (value >= 90) return 'text-green-600 bg-green-100';
    if (value >= 75) return 'text-yellow-600 bg-yellow-100';
    if (value >= 60) return 'text-orange-600 bg-orange-100';
    return 'text-red-600 bg-red-100';
  };

  const getHealthIcon = (value) => {
    if (value >= 90) return <CheckCircleIcon className="h-4 w-4" />;
    if (value >= 75) return <ExclamationTriangleIcon className="h-4 w-4" />;
    return <XCircleIcon className="h-4 w-4" />;
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 1) return 'Ahora';
    if (minutes < 60) return `Hace ${minutes}m`;
    return `Hace ${Math.floor(minutes / 60)}h`;
  };

  const systemComponents = [
    { key: 'server', name: 'Servidor', icon: ServerIcon, value: systemHealth.server },
    { key: 'database', name: 'Base de Datos', icon: DatabaseIcon, value: systemHealth.database },
    { key: 'network', name: 'Red', icon: WifiIcon, value: systemHealth.network },
    { key: 'storage', name: 'Almacenamiento', icon: CpuChipIcon, value: systemHealth.storage },
    { key: 'memory', name: 'Memoria', icon: HeartIcon, value: systemHealth.memory },
    { key: 'cpu', name: 'CPU', icon: CpuChipIcon, value: systemHealth.cpu }
  ];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 bg-gradient-to-r from-green-600 to-emerald-600">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-white/20 rounded-lg">
              <HeartIcon className="h-6 w-6 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">Salud del Sistema</h3>
              <p className="text-green-100 text-sm">Monitoreo en tiempo real</p>
            </div>
          </div>
          <div className="text-right text-white">
            <div className="text-2xl font-bold">{systemHealth.overall.toFixed(0)}%</div>
            <div className="text-sm text-green-100">Estado General</div>
          </div>
        </div>
      </div>

      {/* Métricas principales */}
      <div className="p-6">
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
          {systemComponents.map((component) => {
            const Icon = component.icon;
            return (
              <div key={component.key} className="text-center">
                <div className="flex items-center justify-center mb-2">
                  <Icon className="h-5 w-5 text-gray-600" />
                </div>
                <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getHealthColor(component.value)}`}>
                  {getHealthIcon(component.value)}
                  <span className="ml-1">{component.value.toFixed(0)}%</span>
                </div>
                <p className="text-xs text-gray-600 mt-1">{component.name}</p>
              </div>
            );
          })}
        </div>

        {/* Barra de progreso general */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Estado General del Sistema</span>
            <span className="text-sm text-gray-500">{systemHealth.overall.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className={`h-3 rounded-full transition-all duration-500 ${
                systemHealth.overall >= 90 ? 'bg-green-500' :
                systemHealth.overall >= 75 ? 'bg-yellow-500' :
                systemHealth.overall >= 60 ? 'bg-orange-500' : 'bg-red-500'
              }`}
              style={{ width: `${systemHealth.overall}%` }}
            ></div>
          </div>
        </div>

        {/* Información adicional */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="flex items-center space-x-2 mb-1">
              <ClockIcon className="h-4 w-4 text-gray-600" />
              <span className="text-sm font-medium text-gray-700">Tiempo Activo</span>
            </div>
            <p className="text-lg font-semibold text-gray-900">{systemHealth.uptime}</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="flex items-center space-x-2 mb-1">
              <CpuChipIcon className="h-4 w-4 text-gray-600" />
              <span className="text-sm font-medium text-gray-700">Última Actualización</span>
            </div>
            <p className="text-lg font-semibold text-gray-900">Hace 3s</p>
          </div>
        </div>

        {/* Botón para expandir */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full flex items-center justify-center space-x-2 py-2 px-4 text-sm font-medium text-gray-600 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <Cog6ToothIcon className="h-4 w-4" />
          <span>{isExpanded ? 'Ocultar Detalles' : 'Ver Detalles'}</span>
        </button>
      </div>

      {/* Panel expandido */}
      {isExpanded && (
        <div className="border-t border-gray-200 bg-gray-50">
          <div className="p-6">
            {/* Alertas recientes */}
            <div className="mb-6">
              <h4 className="text-sm font-semibold text-gray-900 mb-3">Alertas Recientes</h4>
              <div className="space-y-2 max-h-32 overflow-y-auto">
                {alerts.length === 0 ? (
                  <p className="text-sm text-gray-500 text-center py-4">No hay alertas recientes</p>
                ) : (
                  alerts.map((alert) => (
                    <div key={alert.id} className="flex items-center space-x-3 p-2 bg-white rounded border">
                      <div className={`p-1 rounded ${
                        alert.type === 'error' ? 'bg-red-100' :
                        alert.type === 'warning' ? 'bg-yellow-100' :
                        alert.type === 'success' ? 'bg-green-100' : 'bg-blue-100'
                      }`}>
                        {alert.type === 'error' ? (
                          <XCircleIcon className="h-3 w-3 text-red-600" />
                        ) : alert.type === 'warning' ? (
                          <ExclamationTriangleIcon className="h-3 w-3 text-yellow-600" />
                        ) : alert.type === 'success' ? (
                          <CheckCircleIcon className="h-3 w-3 text-green-600" />
                        ) : (
                          <CpuChipIcon className="h-3 w-3 text-blue-600" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-medium text-gray-900 truncate">{alert.message}</p>
                        <p className="text-xs text-gray-500">{alert.component} • {formatTimeAgo(alert.timestamp)}</p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Métricas detalladas */}
            <div>
              <h4 className="text-sm font-semibold text-gray-900 mb-3">Métricas Detalladas</h4>
              <div className="space-y-3">
                {systemComponents.map((component) => {
                  const Icon = component.icon;
                  return (
                    <div key={component.key} className="flex items-center justify-between p-3 bg-white rounded border">
                      <div className="flex items-center space-x-3">
                        <Icon className="h-4 w-4 text-gray-600" />
                        <span className="text-sm font-medium text-gray-700">{component.name}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="w-16 bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${
                              component.value >= 90 ? 'bg-green-500' :
                              component.value >= 75 ? 'bg-yellow-500' :
                              component.value >= 60 ? 'bg-orange-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${component.value}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium text-gray-900 w-8 text-right">
                          {component.value.toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SystemHealthMonitor;
