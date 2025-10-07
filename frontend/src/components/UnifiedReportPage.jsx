import React, { useState, useCallback, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  PlusIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  DocumentArrowUpIcon,
  EyeIcon,
  DocumentArrowDownIcon,
  TrashIcon,
  CalendarIcon,
  UserIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XMarkIcon,
  CloudArrowUpIcon,
  DocumentTextIcon,
  PaperClipIcon,
} from '@heroicons/react/24/outline';
import { useNotifications } from '../hooks/useNotifications';
import { api } from '../services/api';
import useDocumentManager from '../hooks/useDocumentManager';
import ReportAttachments from './ReportAttachments';
import IncidentClosureForm from './IncidentClosureForm';

/**
 * Componente unificado para todas las páginas de reportes
 * Maneja la lógica común de reportes de manera profesional
 */
const UnifiedReportPage = ({ 
  reportType, 
  reportTitle, 
  reportDescription,
  createModal: CreateModal,
  responseModal: ResponseModal,
  closureModal: ClosureModal,
  escalateModal: EscalateModal,
  className = ""
}) => {
  const { showSuccess, showError } = useNotifications();
  const {
    uploadDocument,
    deleteDocument,
    downloadDocument,
    openDocument,
    uploadProgress,
    isUploading,
  } = useDocumentManager();

  // Estados
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [sortBy, setSortBy] = useState('date');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showResponseModal, setShowResponseModal] = useState(false);
  const [showClosureModal, setShowClosureModal] = useState(false);
  const [showEscalateModal, setShowEscalateModal] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [showIncidentClosure, setShowIncidentClosure] = useState(false);

  // Obtener reportes
  const { 
    data: reports = [], 
    isLoading: reportsLoading, 
    error: reportsError,
    refetch: refetchReports 
  } = useQuery({
    queryKey: [`${reportType}-reports`],
    queryFn: async () => {
      const response = await api.get(`/documents/${reportType}/`);
      return response.data || [];
    },
  });

  // Obtener incidencias disponibles
  const { 
    data: incidents = [], 
    isLoading: incidentsLoading 
  } = useQuery({
    queryKey: ['incidents-for-reports'],
    queryFn: async () => {
      const response = await api.get('/incidents/');
      return Array.isArray(response.data) ? response.data : (response.data?.results || []);
    },
  });

  // Filtrar y ordenar reportes
  const filteredReports = useMemo(() => {
    let filtered = Array.isArray(reports) ? reports : [];
    
    // Filtrar por término de búsqueda
    if (searchTerm) {
      filtered = filtered.filter(report =>
        report.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        report.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        report.incident_code?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    // Filtrar por estado
    if (filterStatus !== 'all') {
      filtered = filtered.filter(report => report.status === filterStatus);
    }
    
    // Ordenar
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'title':
          return (a.title || '').localeCompare(b.title || '');
        case 'status':
          return (a.status || '').localeCompare(b.status || '');
        case 'date':
        default:
          return new Date(b.created_at || 0) - new Date(a.created_at || 0);
      }
    });
    
    return filtered;
  }, [reports, searchTerm, filterStatus, sortBy]);

  // Obtener estadísticas
  const stats = useMemo(() => {
    const stats = {
      total: reports.length,
      pending: 0,
      in_progress: 0,
      completed: 0,
      overdue: 0,
    };
    
    reports.forEach(report => {
      switch (report.status) {
        case 'pending':
          stats.pending++;
          break;
        case 'in_progress':
          stats.in_progress++;
          break;
        case 'completed':
          stats.completed++;
          break;
        case 'overdue':
          stats.overdue++;
          break;
      }
    });
    
    return stats;
  }, [reports]);

  // Handlers
  const handleSelectReport = useCallback((report) => {
    setSelectedReport(report);
  }, []);

  const handleCreateReport = useCallback(async (reportData) => {
    try {
      const response = await api.post(`/documents/${reportType}/`, reportData);
      refetchReports();
      showSuccess('Reporte creado exitosamente');
      setShowCreateModal(false);
      return true;
    } catch (error) {
      console.error('Error creating report:', error);
      showError('Error al crear el reporte');
      return false;
    }
  }, [reportType, refetchReports, showSuccess, showError]);

  const handleAttachResponse = useCallback(async (responseData) => {
    if (!selectedReport) return;
    
    try {
      await api.post(`/documents/${reportType}/${selectedReport.id}/attach-response/`, responseData);
      refetchReports();
      showSuccess('Respuesta adjuntada exitosamente');
      setShowResponseModal(false);
      setSelectedReport(null);
    } catch (error) {
      console.error('Error attaching response:', error);
      showError('Error al adjuntar la respuesta');
    }
  }, [selectedReport, reportType, refetchReports, showSuccess, showError]);

  const handleCloseReport = useCallback(async (closureData) => {
    if (!selectedReport) return;
    
    try {
      await api.post(`/documents/${reportType}/${selectedReport.id}/close/`, closureData);
      refetchReports();
      showSuccess('Reporte cerrado exitosamente');
      setShowClosureModal(false);
      setSelectedReport(null);
    } catch (error) {
      console.error('Error closing report:', error);
      showError('Error al cerrar el reporte');
    }
  }, [selectedReport, reportType, refetchReports, showSuccess, showError]);

  const handleEscalateReport = useCallback(async (escalationData) => {
    if (!selectedReport) return;
    
    try {
      await api.post(`/documents/${reportType}/${selectedReport.id}/escalate/`, escalationData);
      refetchReports();
      showSuccess('Reporte escalado exitosamente');
      setShowEscalateModal(false);
      setSelectedReport(null);
    } catch (error) {
      console.error('Error escalating report:', error);
      showError('Error al escalar el reporte');
    }
  }, [selectedReport, reportType, refetchReports, showSuccess, showError]);

  const handleCloseIncident = useCallback(async (closureData) => {
    try {
      // Implementar lógica de cierre de incidencia
      showSuccess('Incidencia cerrada exitosamente');
      setShowIncidentClosure(false);
      setSelectedIncident(null);
      return true;
    } catch (error) {
      console.error('Error closing incident:', error);
      showError('Error al cerrar la incidencia');
      return false;
    }
  }, [showSuccess, showError]);

  const handleGenerateDocument = useCallback(async () => {
    if (!selectedReport) return;
    
    try {
      await api.post(`/documents/generate/${reportType}/${selectedReport.id}/`);
      showSuccess('Documento generado exitosamente');
    } catch (error) {
      console.error('Error generating document:', error);
      showError('Error al generar el documento');
    }
  }, [selectedReport, reportType, showSuccess, showError]);

  const handleViewDocument = useCallback(async (report) => {
    try {
      const filename = report.pdf_filename || report.filename || 'documento.pdf';
      const encodedFilename = encodeURIComponent(filename);
      const { API_ORIGIN } = await import('../services/api');
      const url = `${API_ORIGIN}/api/documents/open/${reportType}/${report.related_incident?.id}/${encodedFilename}`;
      window.open(url, '_blank');
      showSuccess('Documento abierto exitosamente');
    } catch (error) {
      console.error('Error opening document:', error);
      showError('Error al abrir el documento');
    }
  }, [reportType, showSuccess, showError]);

  const getStatusColor = useCallback((status) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'overdue':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  }, []);

  const getStatusText = useCallback((status) => {
    switch (status) {
      case 'pending':
        return 'Pendiente';
      case 'in_progress':
        return 'En Progreso';
      case 'completed':
        return 'Completado';
      case 'overdue':
        return 'Vencido';
      default:
        return status;
    }
  }, []);

  return (
    <div className={`min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{reportTitle}</h1>
              <p className="mt-2 text-gray-600">{reportDescription}</p>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
            >
              <PlusIcon className="h-4 w-4 mr-2" />
              Crear {reportTitle}
            </button>
          </div>
        </div>

        {/* Estadísticas */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <DocumentTextIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.total}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <ClockIcon className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Pendientes</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.pending}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckCircleIcon className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Completados</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.completed}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-red-100 rounded-lg">
                <ExclamationTriangleIcon className="h-6 w-6 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Vencidos</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.overdue}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Filtros y búsqueda */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="p-6">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <MagnifyingGlassIcon className="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Buscar reportes..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
              
              <div className="flex gap-2">
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">Todos los estados</option>
                  <option value="pending">Pendiente</option>
                  <option value="in_progress">En Progreso</option>
                  <option value="completed">Completado</option>
                  <option value="overdue">Vencido</option>
                </select>
                
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="date">Fecha</option>
                  <option value="title">Título</option>
                  <option value="status">Estado</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Lista de reportes */}
        <div className="bg-white rounded-lg shadow">
          {reportsLoading ? (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-500">Cargando reportes...</p>
            </div>
          ) : reportsError ? (
            <div className="p-8 text-center">
              <ExclamationTriangleIcon className="h-12 w-12 mx-auto mb-4 text-red-400" />
              <p className="text-red-600">Error al cargar reportes</p>
              <button
                onClick={() => refetchReports()}
                className="mt-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
              >
                Reintentar
              </button>
            </div>
          ) : filteredReports.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <DocumentTextIcon className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>No hay reportes disponibles</p>
              <p className="text-sm">Crea tu primer reporte para comenzar</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {filteredReports.map((report) => (
                <div
                  key={report.id}
                  className="p-6 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-3">
                        <h3 className="text-lg font-medium text-gray-900 truncate">
                          {report.title}
                        </h3>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(report.status)}`}>
                          {getStatusText(report.status)}
                        </span>
                      </div>
                      
                      <p className="mt-1 text-sm text-gray-600 truncate">
                        {report.description}
                      </p>
                      
                      <div className="mt-2 flex items-center space-x-4 text-sm text-gray-500">
                        <span className="flex items-center">
                          <CalendarIcon className="h-4 w-4 mr-1" />
                          {new Date(report.created_at).toLocaleDateString('es-ES')}
                        </span>
                        <span className="flex items-center">
                          <UserIcon className="h-4 w-4 mr-1" />
                          {report.created_by?.username || 'Sistema'}
                        </span>
                        {report.incident_code && (
                          <span className="text-blue-600 font-medium">
                            {report.incident_code}
                          </span>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2 ml-4">
                      <button
                        onClick={() => handleViewDocument(report)}
                        className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                        title="Ver documento"
                      >
                        <EyeIcon className="h-4 w-4" />
                      </button>
                      
                      <button
                        onClick={() => handleGenerateDocument()}
                        className="p-2 text-gray-400 hover:text-green-600 transition-colors"
                        title="Generar documento"
                      >
                        <DocumentArrowUpIcon className="h-4 w-4" />
                      </button>
                      
                      <button
                        onClick={() => handleSelectReport(report)}
                        className="px-3 py-1 text-sm font-medium text-blue-600 bg-blue-100 rounded-lg hover:bg-blue-200 transition-colors"
                      >
                        Gestionar
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Modales */}
        {showCreateModal && CreateModal && (
          <CreateModal
            incidents={incidents}
            onSubmit={handleCreateReport}
            onClose={() => setShowCreateModal(false)}
          />
        )}

        {showResponseModal && selectedReport && ResponseModal && (
          <ResponseModal
            report={selectedReport}
            onSubmit={handleAttachResponse}
            onClose={() => setShowResponseModal(false)}
          />
        )}

        {showClosureModal && selectedReport && ClosureModal && (
          <ClosureModal
            report={selectedReport}
            onSubmit={handleCloseReport}
            onClose={() => setShowClosureModal(false)}
          />
        )}

        {showEscalateModal && selectedReport && EscalateModal && (
          <EscalateModal
            report={selectedReport}
            onSubmit={handleEscalateReport}
            onClose={() => setShowEscalateModal(false)}
          />
        )}

        {/* Adjuntos de reportes */}
        {selectedReport && (
          <div className="mt-6">
            <ReportAttachments
              reportId={selectedReport.id}
              reportType={reportType}
              onAttachmentUploaded={() => {
                refetchReports();
                showSuccess('Documento adjuntado exitosamente');
              }}
              onAttachmentDeleted={() => {
                refetchReports();
                showSuccess('Documento eliminado exitosamente');
              }}
            />
          </div>
        )}

        {/* Formulario de cierre de incidencia */}
        {showIncidentClosure && selectedIncident && (
          <IncidentClosureForm
            incident={selectedIncident}
            onSubmit={handleCloseIncident}
            onCancel={() => {
              setShowIncidentClosure(false);
              setSelectedIncident(null);
            }}
            isLoading={false}
          />
        )}
      </div>
    </div>
  );
};

export default UnifiedReportPage;
