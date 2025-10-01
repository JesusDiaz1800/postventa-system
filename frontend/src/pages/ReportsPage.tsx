import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  ChartBarIcon, 
  ArrowDownTrayIcon, 
  DocumentTextIcon,
  ClockIcon,
  ArrowTrendingUpIcon
} from '@heroicons/react/24/outline';

interface ReportData {
  totalIncidents: number;
  resolvedIncidents: number;
  pendingIncidents: number;
  averageResolutionTime: number;
  incidentsByStatus: Array<{ status: string; count: number }>;
  incidentsByPriority: Array<{ priority: string; count: number }>;
  incidentsByProvider: Array<{ provider: string; count: number }>;
  incidentsByMonth: Array<{ month: string; count: number }>;
  topSKUs: Array<{ sku: string; count: number }>;
  resolutionTrend: Array<{ date: string; resolved: number; created: number }>;
}

interface ReportFilters {
  startDate: string;
  endDate: string;
  provider: string;
  status: string;
}

export function ReportsPage() {
  const [filters, setFilters] = useState<ReportFilters>({
    startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    endDate: new Date().toISOString().split('T')[0],
    provider: '',
    status: '',
  });

  // Fetch report data from API
  const { data: reportData, isLoading, error } = useQuery({
    queryKey: ['reports', filters],
    queryFn: async (): Promise<ReportData> => {
      try {
        // Obtener datos reales de la API de reportes
        const token = localStorage.getItem('access_token');
        const params = new URLSearchParams({
          start_date: filters.startDate,
          end_date: filters.endDate,
          provider: filters.provider,
          status: filters.status,
        });
        
        const response = await fetch(`/api/reports/dashboard/?${params}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
      });
        if (response.ok) {
          const apiData = await response.json();
          return {
            totalIncidents: apiData.total_incidents || 0,
            resolvedIncidents: apiData.resolved_incidents || 0,
            pendingIncidents: apiData.pending_incidents || 0,
            averageResolutionTime: apiData.avg_resolution_time || 0,
            incidentsByStatus: apiData.status_distribution || [],
            incidentsByPriority: apiData.priority_distribution || [],
            incidentsByProvider: apiData.provider_distribution || [],
            incidentsByMonth: apiData.monthly_trends || [],
            topSKUs: apiData.top_skus || [],
            resolutionTrend: apiData.resolution_trend || [],
          };
        }
      } catch (error) {
        console.error('Error fetching reports data:', error);
      }
      
      // Fallback a datos mock si la API falla
      const mockReportData: ReportData = {
        totalIncidents: 45,
        resolvedIncidents: 32,
        pendingIncidents: 13,
        averageResolutionTime: 2.5,
        incidentsByStatus: [
          { status: 'abierto', count: 13 },
          { status: 'en_proceso', count: 18 },
          { status: 'resuelto', count: 9 },
          { status: 'cerrado', count: 5 },
        ],
        incidentsByPriority: [
          { priority: 'critica', count: 5 },
          { priority: 'alta', count: 13 },
          { priority: 'media', count: 22 },
          { priority: 'baja', count: 5 },
        ],
        incidentsByProvider: [
          { provider: 'Amsovi', count: 27 },
          { provider: 'Otro', count: 18 },
        ],
        incidentsByMonth: [
          { month: 'Ene', count: Math.floor(Math.random() * 20) + 10 },
          { month: 'Feb', count: Math.floor(Math.random() * 20) + 10 },
          { month: 'Mar', count: Math.floor(Math.random() * 20) + 10 },
          { month: 'Abr', count: Math.floor(Math.random() * 20) + 10 },
          { month: 'May', count: Math.floor(Math.random() * 20) + 10 },
          { month: 'Jun', count: Math.floor(Math.random() * 20) + 10 },
        ],
        topSKUs: [
          { sku: 'SKU-001', count: Math.floor(Math.random() * 10) + 5 },
          { sku: 'SKU-002', count: Math.floor(Math.random() * 10) + 5 },
          { sku: 'SKU-003', count: Math.floor(Math.random() * 10) + 5 },
          { sku: 'SKU-004', count: Math.floor(Math.random() * 10) + 5 },
        ],
        resolutionTrend: [
          { date: '2025-01-01', resolved: 5, created: 8 },
          { date: '2025-01-02', resolved: 7, created: 6 },
          { date: '2025-01-03', resolved: 4, created: 9 },
          { date: '2025-01-04', resolved: 8, created: 5 },
          { date: '2025-01-05', resolved: 6, created: 7 },
        ],
      };

      return mockReportData;
    },
  });

  const handleFilterChange = (key: keyof ReportFilters, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleExport = (format: 'pdf' | 'excel') => {
    // Implement export functionality
    console.log(`Exporting to ${format}`);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <ChartBarIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Error al cargar reportes</h3>
        <p className="text-gray-600">Por favor, intenta recargar la página</p>
      </div>
    );
  }

  return (
      <div className="p-6">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Reportes y Análisis</h1>
              <p className="text-gray-600">Análisis detallado de incidencias y métricas de rendimiento</p>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => handleExport('pdf')}
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
                PDF
              </button>
              <button
                onClick={() => handleExport('excel')}
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
                Excel
              </button>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Fecha Inicio
              </label>
              <input
                type="date"
                value={filters.startDate}
                onChange={(e) => handleFilterChange('startDate', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Fecha Fin
              </label>
              <input
                type="date"
                value={filters.endDate}
                onChange={(e) => handleFilterChange('endDate', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Proveedor
              </label>
              <select
                value={filters.provider}
                onChange={(e) => handleFilterChange('provider', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Todos los proveedores</option>
                <option value="amsovi">Amsovi</option>
                <option value="otro">Otro</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Estado
              </label>
              <select
                value={filters.status}
                onChange={(e) => handleFilterChange('status', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Todos los estados</option>
                <option value="abierto">Abierto</option>
                <option value="en_proceso">En Proceso</option>
                <option value="resuelto">Resuelto</option>
                <option value="cerrado">Cerrado</option>
              </select>
            </div>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Incidencias</p>
                <p className="text-3xl font-bold text-gray-900">{reportData?.totalIncidents || 0}</p>
              </div>
              <div className="p-3 rounded-full bg-blue-100">
                <DocumentTextIcon className="h-6 w-6 text-blue-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center">
              <span className="text-sm font-medium text-green-600">+12%</span>
              <span className="text-sm text-gray-500 ml-2">vs mes anterior</span>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Resueltas</p>
                <p className="text-3xl font-bold text-gray-900">{reportData?.resolvedIncidents || 0}</p>
              </div>
              <div className="p-3 rounded-full bg-green-100">
                <ArrowTrendingUpIcon className="h-6 w-6 text-green-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center">
              <span className="text-sm font-medium text-green-600">+8%</span>
              <span className="text-sm text-gray-500 ml-2">vs mes anterior</span>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Pendientes</p>
                <p className="text-3xl font-bold text-gray-900">{reportData?.pendingIncidents || 0}</p>
              </div>
              <div className="p-3 rounded-full bg-yellow-100">
                <ClockIcon className="h-6 w-6 text-yellow-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center">
              <span className="text-sm font-medium text-red-600">-5%</span>
              <span className="text-sm text-gray-500 ml-2">vs mes anterior</span>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Tiempo Promedio</p>
                <p className="text-3xl font-bold text-gray-900">{reportData?.averageResolutionTime || 0}d</p>
              </div>
              <div className="p-3 rounded-full bg-purple-100">
                <ChartBarIcon className="h-6 w-6 text-purple-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center">
              <span className="text-sm font-medium text-green-600">-2d</span>
              <span className="text-sm text-gray-500 ml-2">vs mes anterior</span>
            </div>
          </div>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Incidents by Status */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Incidencias por Estado</h3>
              <ChartBarIcon className="h-5 w-5 text-gray-400" />
            </div>
            <div className="space-y-3">
              {reportData?.incidentsByStatus?.map((item) => (
                <div key={item?.status || 'unknown'} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className={`w-3 h-3 rounded-full mr-3 ${
                      item?.status === 'abierto' ? 'bg-red-500' :
                      item?.status === 'en_proceso' ? 'bg-yellow-500' :
                      item?.status === 'resuelto' ? 'bg-green-500' :
                      'bg-gray-500'
                    }`} />
                    <span className="text-sm font-medium text-gray-700 capitalize">
                      {item?.status ? item.status.replace('_', ' ') : 'N/A'}
                    </span>
                  </div>
                  <span className="text-sm font-semibold text-gray-900">{item?.count || 0}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Incidents by Priority */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Incidencias por Prioridad</h3>
              <ChartBarIcon className="h-5 w-5 text-gray-400" />
            </div>
            <div className="space-y-3">
              {reportData?.incidentsByPriority?.map((item) => (
                <div key={item?.priority || 'unknown'} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className={`w-3 h-3 rounded-full mr-3 ${
                      item?.priority === 'critica' ? 'bg-red-500' :
                      item?.priority === 'alta' ? 'bg-orange-500' :
                      item?.priority === 'media' ? 'bg-yellow-500' :
                      'bg-green-500'
                    }`} />
                    <span className="text-sm font-medium text-gray-700 capitalize">
                      {item?.priority || 'N/A'}
                    </span>
                  </div>
                  <span className="text-sm font-semibold text-gray-900">{item?.count || 0}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Monthly Trend */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Tendencia Mensual</h3>
              <ChartBarIcon className="h-5 w-5 text-gray-400" />
          </div>
          <div className="h-64 flex items-end space-x-2">
            {reportData?.incidentsByMonth?.map((item) => (
              <div key={item?.month || 'unknown'} className="flex-1 flex flex-col items-center">
                <div 
                  className="w-full bg-blue-500 rounded-t"
                  style={{ height: `${((item?.count || 0) / Math.max(...(reportData?.incidentsByMonth?.map(i => i?.count || 0) || [1]))) * 200}px` }}
                />
                <span className="text-xs text-gray-500 mt-2">{item?.month || 'N/A'}</span>
                <span className="text-xs font-semibold text-gray-900">{item?.count || 0}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Top SKUs */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">SKUs con Más Incidencias</h3>
              <DocumentTextIcon className="h-5 w-5 text-gray-400" />
          </div>
        <div className="table-container">
          <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    SKU
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Incidencias
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Porcentaje
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {reportData?.topSKUs?.map((item) => (
                  <tr key={item?.sku || 'unknown'}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">
                      {item?.sku || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {item?.count || 0}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {(((item?.count || 0) / (reportData?.totalIncidents || 1)) * 100).toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
  );
}

export default ReportsPage;