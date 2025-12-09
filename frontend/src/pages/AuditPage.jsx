import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  ShieldCheckIcon, 
  MagnifyingGlassIcon, 
  ArrowDownTrayIcon,
  CalendarIcon,
  FunnelIcon,
  ArrowPathIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { auditAPI } from '../services/api';
import { useNotifications } from '../hooks/useNotifications';

const AuditPage = () => {
  const { showSuccess, showError } = useNotifications();
  
  // Estados para filtros
  const [filters, setFilters] = useState({
    action: '',
    user: '',
    date_from: '',
    date_to: '',
    search: '',
  });
  
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 20;

  // Fetch audit logs
  const { data: auditData, isLoading, error, refetch } = useQuery({
    queryKey: ['audit-logs', filters, currentPage],
    queryFn: async () => {
      const params = {
        ...filters,
        page: currentPage,
        page_size: pageSize
      };
      
      const response = await auditAPI.logs(params);
      return response.data;
    },
    retry: 1,
    retryDelay: 1000,
  });

  const auditLogs = auditData?.results || [];

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setCurrentPage(1);
  };

  const handleExport = async () => {
    try {
      const params = { ...filters };
      const response = await auditAPI.logs(params);
      const data = response.data;
      
      const blob = new Blob([JSON.stringify(data.results || [], null, 2)], { 
        type: 'application/json' 
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `auditoria_${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      showSuccess('Logs de auditoría exportados exitosamente');
      
    } catch (error) {
      console.error('Error exporting audit logs:', error);
      showError('Error al exportar logs de auditoría');
    }
  };

  const clearFilters = () => {
    setFilters({
      action: '',
      user: '',
      date_from: '',
      date_to: '',
      search: '',
    });
    setCurrentPage(1);
  };

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    } catch (error) {
      return dateString;
    }
  };

  const getActionBadgeStyle = (action) => {
    const colorMap = {
      'login': 'bg-green-100 text-green-800',
      'logout': 'bg-gray-100 text-gray-800',
      'crear': 'bg-blue-100 text-blue-800',
      'actualizar': 'bg-yellow-100 text-yellow-800',
      'eliminar': 'bg-red-100 text-red-800',
      'ver': 'bg-gray-100 text-gray-800',
      'subir': 'bg-blue-100 text-blue-800',
      'descargar': 'bg-green-100 text-green-800',
      'escalar': 'bg-orange-100 text-orange-800',
      'cerrar': 'bg-green-100 text-green-800',
      'aprobar': 'bg-green-100 text-green-800',
      'rechazar': 'bg-red-100 text-red-800',
      'exportar': 'bg-purple-100 text-purple-800',
      'buscar': 'bg-blue-100 text-blue-800',
      'filtrar': 'bg-gray-100 text-gray-800',
      'error': 'bg-red-100 text-red-800',
    };
    return colorMap[action] || 'bg-gray-100 text-gray-800';
  };

  const getActionIcon = (action) => {
    const iconMap = {
      'login': '🔑',
      'logout': '🚪',
      'crear': '➕',
      'actualizar': '✏️',
      'eliminar': '🗑️',
      'ver': '👁️',
      'subir': '📤',
      'descargar': '📥',
      'escalar': '⬆️',
      'cerrar': '✅',
      'aprobar': '👍',
      'rechazar': '👎',
      'exportar': '📊',
      'buscar': '🔍',
      'filtrar': '🔽',
      'error': '❌',
    };
    return iconMap[action] || '📝';
  };

  if (isLoading && !auditData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-6"></div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Cargando Auditoría</h3>
          <p className="text-gray-600">Preparando la información...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-red-500 mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Error al cargar auditoría</h3>
          <p className="text-gray-600 mb-4">
            No se pudo conectar con el servidor de auditoría. Verifica que el backend esté funcionando.
          </p>
          <button
            onClick={() => refetch()}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ShieldCheckIcon className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <h1 className="text-xl font-semibold text-gray-900">
                  Auditoría del Sistema
                </h1>
                <p className="text-sm text-gray-500">
                  Registro de todas las actividades y acciones del sistema
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                {auditData?.count || 0} registros
              </span>
              <button
                onClick={handleExport}
                className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
                Exportar
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filtros */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-gray-900 flex items-center">
              <FunnelIcon className="h-5 w-5 mr-2" />
              Filtros de Búsqueda
            </h2>
            <button
              onClick={clearFilters}
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <ArrowPathIcon className="h-4 w-4 mr-2" />
              Limpiar
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Buscar
              </label>
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Usuario, acción, descripción..."
                  value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Acción
              </label>
              <select
                value={filters.action}
                onChange={(e) => handleFilterChange('action', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Todas las acciones</option>
                <option value="login">🔑 Iniciar Sesión</option>
                <option value="logout">🚪 Cerrar Sesión</option>
                <option value="crear">➕ Crear</option>
                <option value="actualizar">✏️ Actualizar</option>
                <option value="eliminar">🗑️ Eliminar</option>
                <option value="ver">👁️ Ver</option>
                <option value="subir">📤 Subir Archivo</option>
                <option value="descargar">📥 Descargar Archivo</option>
                <option value="escalar">⬆️ Escalar</option>
                <option value="cerrar">✅ Cerrar</option>
                <option value="aprobar">👍 Aprobar</option>
                <option value="rechazar">👎 Rechazar</option>
                <option value="exportar">📊 Exportar</option>
                <option value="buscar">🔍 Buscar</option>
                <option value="filtrar">🔽 Filtrar</option>
                <option value="error">❌ Error</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Usuario
              </label>
              <input
                type="text"
                placeholder="Nombre de usuario"
                value={filters.user}
                onChange={(e) => handleFilterChange('user', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Fecha Desde
              </label>
              <input
                type="date"
                value={filters.date_from}
                onChange={(e) => handleFilterChange('date_from', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Fecha Hasta
              </label>
              <input
                type="date"
                value={filters.date_to}
                onChange={(e) => handleFilterChange('date_to', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Lista de Logs de Auditoría */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">
              Registros de Auditoría
            </h2>
          </div>
          
          {auditLogs.length > 0 ? (
            <div className="divide-y divide-gray-200">
              {auditLogs.map((log) => (
                <div key={log.id} className="px-6 py-4 hover:bg-gray-50 transition-colors duration-150">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-4">
                      <div className="flex-shrink-0">
                        <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                          <span className="text-lg">{getActionIcon(log.action_code || log.action)}</span>
                        </div>
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-3 mb-2">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getActionBadgeStyle(log.action_code || log.action)}`}>
                            {getActionIcon(log.action_code || log.action)} {log.action || 'Acción'}
                          </span>
                          <span className="text-sm text-gray-500">{log.user || 'Sistema'}</span>
                        </div>
                        
                        <p className="text-sm text-gray-900 mb-2">{log.description || 'Sin descripción'}</p>
                        
                        <div className="flex items-center space-x-4 text-xs text-gray-500">
                          <div className="flex items-center">
                            <CalendarIcon className="h-3 w-3 mr-1" />
                            {formatDate(log.timestamp)}
                          </div>
                          {log.ip_address && log.ip_address !== 'N/A' && (
                            <div className="flex items-center">
                              <span className="mr-1">🌐</span>
                              {log.ip_address}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <ShieldCheckIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No hay registros</h3>
              <p className="mt-1 text-sm text-gray-500">
                No se encontraron registros con los filtros aplicados
              </p>
              <p className="text-sm text-gray-500 mt-2">
                Los registros de auditoría aparecerán aquí cuando se realicen acciones en el sistema
              </p>
            </div>
          )}

          {/* Paginación */}
          {auditData?.total_pages > 1 && (
            <div className="px-6 py-4 border-t border-gray-200">
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-700">
                  Mostrando página {currentPage} de {auditData.total_pages}
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                    disabled={currentPage === 1}
                    className="px-3 py-1 text-sm border border-gray-300 rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Anterior
                  </button>
                  <button
                    onClick={() => setCurrentPage(prev => Math.min(auditData.total_pages, prev + 1))}
                    disabled={currentPage === auditData.total_pages}
                    className="px-3 py-1 text-sm border border-gray-300 rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Siguiente
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AuditPage;