import React, { useState, useEffect, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useLocation } from 'react-router-dom';
import { api } from '../services/api';
import { 
  PlusIcon, 
  DocumentArrowUpIcon, 
  EyeIcon, 
  TrashIcon,
  XMarkIcon,
  CheckCircleIcon,
  MagnifyingGlassIcon,
  DocumentTextIcon,
  CalendarIcon,
  UserIcon,
  BuildingOfficeIcon,
  ArrowUpIcon,
  FunnelIcon,
  ArrowPathIcon,
  ExclamationTriangleIcon,
  PaperClipIcon,
  ChatBubbleLeftRightIcon
} from '@heroicons/react/24/outline';
import { useNotifications } from '../hooks/useNotifications';

const SupplierReportsPage = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const location = useLocation();
  const { showSuccess, showError } = useNotifications();
  
  // Estados principales
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedIncidentId, setSelectedIncidentId] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Query para obtener reportes de proveedores con datos de incidencia
  const { data: reports, isLoading: reportsLoading } = useQuery({
    queryKey: ['supplier-reports', { report_type: 'proveedor' }],
    queryFn: async () => {
      const response = await api.get('/documents/supplier-reports/', {
        params: { 
          report_type: 'proveedor',
          include_incident_data: true,
          expand: 'incident'
        }
      });
      console.log('Supplier Reports response:', response.data); // Debug
      return response.data;
    }
  });

  // Query para obtener incidencias escaladas desde reportes internos de calidad
  const { data: escalatedIncidents, isLoading: incidentsLoading } = useQuery({
    queryKey: ['escalatedIncidentsForSupplier'],
    queryFn: async () => {
      const response = await api.get('/incidents/escalated/', {
        params: { 
          from_quality_reports: true,
          ready_for_supplier: true
        }
      });
      return response.data;
    }
  });

  // Filtrar reportes por término de búsqueda
  const filteredReports = useMemo(() => {
    if (!reports?.results) return [];
    
    return reports.results.filter(report => 
      !searchTerm || 
      report.report_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      report.incident_code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      report.supplier_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      report.cliente?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [reports?.results, searchTerm]);

  // Manejar creación de reporte para proveedor
  const handleCreateReport = () => {
    if (!selectedIncidentId) {
      showError('Por favor selecciona una incidencia');
      return;
    }
    
    // Redirigir al formulario específico de reporte para proveedor
    navigate(`/supplier-report-form/${selectedIncidentId}?report_type=proveedor`);
  };

  // Manejar subida de documento
  const handleUploadDocument = async () => {
    if (!selectedIncidentId) {
      showError('Por favor selecciona una incidencia');
      return;
    }

    // Crear input de archivo dinámicamente
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.pdf,.doc,.docx';
    input.onchange = async (e) => {
      const file = e.target.files[0];
      if (!file) return;

      setIsSubmitting(true);
      try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('incident_id', selectedIncidentId);
        formData.append('report_type', 'proveedor');

        const response = await api.post('/documents/upload/supplier-report/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        if (response.data.success) {
          setShowUploadModal(false);
          setSelectedIncidentId('');
          queryClient.invalidateQueries(['supplier-reports']);
          showSuccess('Documento adjuntado exitosamente');
        }
      } catch (error) {
        console.error('Error uploading document:', error);
        showError('Error al subir el documento');
      } finally {
        setIsSubmitting(false);
      }
    };
    input.click();
  };

  // Manejar apertura de documento
  const handleOpenDocument = async (report) => {
    console.log('Report data:', report); // Debug
    
    try {
      const incidentId = report.incident_id || report.incident?.id || report.related_incident_id;
      const filename = report.filename || report.report_number || `supplier_report_${report.id}`;
      
      if (!incidentId) {
        const { API_ORIGIN } = await import('../services/api');
        const directUrl = `${API_ORIGIN}/api/documents/supplier-reports/${report.id}/view/`;
        window.open(directUrl, '_blank');
        return;
      }
      
      const { API_ORIGIN } = await import('../services/api');
      const urls = [
        `${API_ORIGIN}/api/documents/open/supplier-report/${incidentId}/${encodeURIComponent(filename)}`,
        `${API_ORIGIN}/api/documents/supplier-reports/${report.id}/view/`,
        `${API_ORIGIN}/api/documents/real-files/supplier-report/${encodeURIComponent(filename)}/serve/`
      ];
      
      // Intentar el primer endpoint
      try {
        const response = await fetch(urls[0]);
        if (response.ok) {
          window.open(urls[0], '_blank');
          return;
        }
      } catch (error) {
        console.log('First URL failed, trying second...');
      }
      
      // Intentar el segundo endpoint
      try {
        const response = await fetch(urls[1]);
        if (response.ok) {
          window.open(urls[1], '_blank');
          return;
        }
      } catch (error) {
        console.log('Second URL failed, trying third...');
      }
      
      // Intentar el tercer endpoint
      window.open(urls[2], '_blank');
      
    } catch (error) {
      console.error('Error opening document:', error);
      showError('Error al abrir el documento. Verifique que el archivo existe.');
    }
  };

  // Manejar descarga de documento
  const handleDownloadDocument = async (report) => {
    try {
      const incidentId = report.incident_id || report.incident?.id || report.related_incident_id;
      const filename = report.filename || report.report_number || `supplier_report_${report.id}`;
      
      const { API_ORIGIN } = await import('../services/api');
      const urls = [
        incidentId ? `${API_ORIGIN}/api/documents/open/supplier-report/${incidentId}/${encodeURIComponent(filename)}` : null,
        `${API_ORIGIN}/api/documents/supplier-reports/${report.id}/download/`,
        `${API_ORIGIN}/api/documents/real-files/supplier-report/${encodeURIComponent(filename)}/serve/`
      ].filter(Boolean);
      
      // Intentar cada URL hasta que una funcione
      for (const url of urls) {
        try {
          const response = await fetch(url);
          if (response.ok) {
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            link.click();
            return;
          }
        } catch (error) {
          console.log(`URL ${url} failed, trying next...`);
        }
      }
      
      showError('No se pudo descargar el documento. Verifique que el archivo existe.');
      
    } catch (error) {
      console.error('Error downloading document:', error);
      showError('Error al descargar el documento.');
    }
  };

  // Manejar generación de documento PDF
  const handleGenerateDocument = async (report) => {
    try {
      const response = await api.post(`/documents/supplier-reports/${report.id}/generate/`);
      if (response.data.success) {
        showSuccess('Documento PDF generado exitosamente');
        queryClient.invalidateQueries(['supplier-reports']);
      }
    } catch (error) {
      console.error('Error generating document:', error);
      showError('Error al generar el documento PDF');
    }
  };

  // Manejar escalamiento desde reporte interno de calidad
  const handleEscalateFromQuality = async (incidentId) => {
    if (!window.confirm('¿Estás seguro de que quieres escalar esta incidencia a proveedor desde el reporte interno de calidad?')) {
      return;
    }

    try {
      const incidentIdValue = typeof incidentId === 'object' ? incidentId.id : incidentId;
      const response = await api.post(`/incidents/${incidentIdValue}/escalate/supplier/`, {
        reason: 'Escalado desde reporte interno de calidad',
        from_quality_report: true
      });
      
      if (response.data.success) {
        queryClient.invalidateQueries(['supplier-reports']);
        showSuccess('Incidencia escalada a proveedor exitosamente. Se ha enviado un correo de notificación.');
      }
    } catch (error) {
      console.error('Error escalating from quality:', error);
      showError('Error al escalar la incidencia a proveedor');
    }
  };

  // Manejar cierre de incidencia
  const handleCloseIncident = async (incidentId) => {
    if (window.confirm('¿Estás seguro de que quieres cerrar esta incidencia?')) {
      try {
        const incidentIdValue = typeof incidentId === 'object' ? incidentId.id : incidentId;
        const response = await api.post(`/incidents/${incidentIdValue}/close/`);
        
        if (response.data.success) {
          queryClient.invalidateQueries(['supplier-reports']);
          showSuccess('Incidencia cerrada exitosamente');
        }
      } catch (error) {
        console.error('Error closing incident:', error);
        showError('Error al cerrar la incidencia');
      }
    }
  };

  // Manejar eliminación de reporte
  const handleDeleteReport = async (reportId) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este reporte?')) {
      try {
        await api.delete(`/documents/supplier-reports/${reportId}/`);
        queryClient.invalidateQueries(['supplier-reports']);
        showSuccess('Reporte eliminado exitosamente');
      } catch (error) {
        console.error('Error deleting report:', error);
        showError('Error al eliminar el reporte');
      }
    }
  };

  if (reportsLoading || incidentsLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-green-600 mx-auto mb-6"></div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Cargando Reportes</h3>
          <p className="text-gray-600">Preparando la información...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <BuildingOfficeIcon className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4">
                <h1 className="text-xl font-semibold text-gray-900">
                  Reportes para Proveedores
                </h1>
                <p className="text-sm text-gray-500">
                  Gestión de reportes escalados a proveedores desde calidad interna
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowCreateModal(true)}
                className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-xl text-white bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 shadow-lg hover:shadow-xl transition-all duration-200"
              >
                <PlusIcon className="h-5 w-5 mr-2" />
                Crear Reporte
              </button>
              <button
                onClick={() => setShowUploadModal(true)}
                className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-xl text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 shadow-lg hover:shadow-xl transition-all duration-200"
              >
                <DocumentArrowUpIcon className="h-5 w-5 mr-2" />
                Adjuntar Documento
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filtros y Búsqueda */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6 relative z-10">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-gray-900">Filtros y Búsqueda</h2>
            <button
              onClick={() => setSearchTerm('')}
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              <ArrowPathIcon className="h-4 w-4 mr-2" />
              Limpiar
            </button>
          </div>
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar por número de reporte, código de incidencia, proveedor o cliente..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Lista de Reportes */}
        <div className="bg-white rounded-lg shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-medium text-gray-900">
                Reportes para Proveedores Generados
              </h2>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                {filteredReports.length} reportes
              </span>
            </div>
          </div>
          
          {filteredReports.length > 0 ? (
            <div className="table-container">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Reporte
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Incidencia
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Proveedor
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Cliente
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Fecha
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
                  {filteredReports.map((report) => (
                    <tr key={report.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <div className="h-10 w-10 rounded-full bg-green-100 flex items-center justify-center">
                              <DocumentTextIcon className="h-5 w-5 text-green-600" />
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">
                              {report.report_number}
                            </div>
                            <div className="text-sm text-gray-500">
                              {report.title}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {report.incident?.code || report.incident_code || report.related_incident?.code || 'N/A'}
                        </div>
                        <div className="text-sm text-gray-500">
                          {report.incident?.categoria || report.categoria || report.related_incident?.categoria || 'N/A'}
                        </div>
                        {(report.incident?.subcategoria || report.related_incident?.subcategoria) && (
                          <div className="text-xs text-gray-500">
                            {report.incident?.subcategoria || report.related_incident?.subcategoria}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {report.supplier_name || report.incident?.provider || report.related_incident?.provider || 'N/A'}
                        </div>
                        <div className="text-sm text-gray-500">
                          {report.supplier_contact || 'Sin contacto'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {report.incident?.cliente || report.cliente || report.related_incident?.cliente || 'N/A'}
                        </div>
                        <div className="text-sm text-gray-500">
                          {report.incident?.obra || report.obra || report.related_incident?.obra || 'N/A'}
                        </div>
                        {(report.incident?.proyecto || report.related_incident?.proyecto) && (
                          <div className="text-xs text-gray-500">
                            {report.incident?.proyecto || report.related_incident?.proyecto}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {new Date(report.created_at).toLocaleDateString()}
                        </div>
                        <div className="text-sm text-gray-500">
                          {new Date(report.created_at).toLocaleTimeString()}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          report.status === 'cerrado' ? 'bg-green-100 text-green-800' :
                          report.status === 'responded' ? 'bg-blue-100 text-blue-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {report.status === 'cerrado' ? 'CERRADO' : 
                           report.status === 'responded' ? 'RESPONDIDO' : 'PENDIENTE'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => handleOpenDocument(report)}
                            className="text-blue-600 hover:text-blue-900 p-1 rounded-md hover:bg-blue-50"
                            title="Ver reporte"
                          >
                            <EyeIcon className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleDownloadDocument(report)}
                            className="text-green-600 hover:text-green-900 p-1 rounded-md hover:bg-green-50"
                            title="Descargar reporte"
                          >
                            <DocumentArrowUpIcon className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleGenerateDocument(report)}
                            className="text-purple-600 hover:text-purple-900 p-1 rounded-md hover:bg-purple-50"
                            title="Generar documento PDF"
                          >
                            <DocumentTextIcon className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteReport(report.id)}
                            className="text-red-600 hover:text-red-900 p-1 rounded-md hover:bg-red-50"
                            title="Eliminar reporte"
                          >
                            <TrashIcon className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12">
              <BuildingOfficeIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No hay reportes</h3>
              <p className="mt-1 text-sm text-gray-500">
                Comienza creando un nuevo reporte para proveedor.
              </p>
              <div className="mt-6">
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                >
                  <PlusIcon className="h-4 w-4 mr-2" />
                  Crear Primer Reporte
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Sección de Escalamiento desde Calidad Interna */}
        {escalatedIncidents?.incidents && escalatedIncidents.incidents.length > 0 && (
          <div className="mt-8 bg-white rounded-lg shadow-sm">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-medium text-gray-900 flex items-center">
                  <ExclamationTriangleIcon className="h-5 w-5 text-orange-500 mr-2" />
                  Incidencias Listas para Escalamiento a Proveedor
                </h2>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                  {escalatedIncidents.incidents.length} incidencias
                </span>
              </div>
            </div>
            
            <div className="table-container">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Incidencia
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Cliente
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Proveedor
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Fecha Escalamiento
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Acciones
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {escalatedIncidents.incidents.map((incident) => (
                    <tr key={incident.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <div className="h-10 w-10 rounded-full bg-orange-100 flex items-center justify-center">
                              <ExclamationTriangleIcon className="h-5 w-5 text-orange-600" />
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">
                              {incident.code}
                            </div>
                            <div className="text-sm text-gray-500">
                              {incident.categoria}
                            </div>
                            {incident.subcategoria && (
                              <div className="text-xs text-gray-500">
                                {incident.subcategoria}
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {incident.cliente}
                        </div>
                        <div className="text-sm text-gray-500">
                          {incident.obra}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {incident.provider}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {new Date(incident.escalation_date).toLocaleDateString()}
                        </div>
                        <div className="text-sm text-gray-500">
                          {new Date(incident.escalation_date).toLocaleTimeString()}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => handleEscalateFromQuality(incident.id)}
                            className="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md text-white bg-orange-600 hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500"
                          >
                            <ArrowUpIcon className="h-3 w-3 mr-1" />
                            Escalar a Proveedor
                          </button>
                          <button
                            onClick={() => handleCloseIncident(incident.id)}
                            className="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                          >
                            <CheckCircleIcon className="h-3 w-3 mr-1" />
                            Cerrar
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Modal de Crear Reporte */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
          <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-md">
            <div className="px-6 py-4 bg-gradient-to-r from-green-600 to-emerald-600 rounded-t-2xl">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white flex items-center">
                  <PlusIcon className="h-5 w-5 mr-2" />
                  Crear Reporte para Proveedor
                </h3>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="text-white hover:text-gray-200 transition-colors duration-200"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
            </div>
            <div className="p-6">
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Seleccionar Incidencia
                </label>
                <select
                  value={selectedIncidentId}
                  onChange={(e) => setSelectedIncidentId(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="">Seleccionar incidencia...</option>
                  {(escalatedIncidents?.incidents || []).map((incident) => (
                    <option key={incident.id} value={incident.id}>
                      {incident.code} - {incident.cliente} - {incident.provider}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex justify-end pt-4 border-t border-gray-200 space-x-3">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-6 py-2 text-sm font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleCreateReport}
                  disabled={!selectedIncidentId}
                  className="px-6 py-2 text-sm font-semibold text-white bg-green-600 hover:bg-green-700 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Crear Reporte
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Subida de Documento */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
          <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-md">
            <div className="px-6 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-t-2xl">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white flex items-center">
                  <DocumentArrowUpIcon className="h-5 w-5 mr-2" />
                  Adjuntar Documento
                </h3>
                <button
                  onClick={() => setShowUploadModal(false)}
                  className="text-white hover:text-gray-200 transition-colors duration-200"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
            </div>
            <div className="p-6">
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Seleccionar Incidencia
                </label>
                <select
                  value={selectedIncidentId}
                  onChange={(e) => setSelectedIncidentId(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Seleccionar incidencia...</option>
                  {(escalatedIncidents?.incidents || []).map((incident) => (
                    <option key={incident.id} value={incident.id}>
                      {incident.code} - {incident.cliente} - {incident.provider}
                    </option>
                  ))}
                </select>
              </div>

              <div className="mb-6">
                <button
                  onClick={handleUploadDocument}
                  disabled={!selectedIncidentId || isSubmitting}
                  className="w-full flex items-center justify-center px-6 py-4 border-2 border-dashed border-gray-300 text-sm font-semibold rounded-xl text-gray-700 bg-white hover:bg-gray-50 hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <DocumentArrowUpIcon className="h-5 w-5 mr-3" />
                  {isSubmitting ? 'Subiendo...' : '📎 Seleccionar Archivo'}
                </button>
              </div>

              <div className="flex justify-end pt-4 border-t border-gray-200">
                <button
                  onClick={() => setShowUploadModal(false)}
                  className="px-6 py-2 text-sm font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
                >
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SupplierReportsPage;