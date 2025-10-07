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
  ClipboardDocumentListIcon,
  ArrowPathIcon,
  ArrowUpIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';

const VisitReportsPage = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const location = useLocation();
  
  // Estados principales
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  
  const [selectedIncidentId, setSelectedIncidentId] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [uploadedDocuments, setUploadedDocuments] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Formulario de creación (mantenido para funcionalidad completa)
  const [formData, setFormData] = useState({
    related_incident_id: '',
    order_number: `ORD-${Date.now()}`,
    visit_date: new Date().toISOString().split('T')[0],
    project_name: '',
    client_name: '',
    address: '',
    salesperson: '',
    technician: '',
    commune: '',
    city: '',
    visit_reason: '',
    general_observations: '',
    status: 'draft'
  });

  // Query para obtener reportes de visita
  const { data: reports, isLoading: reportsLoading } = useQuery({
    queryKey: ['visit-reports'],
    queryFn: async () => {
      const response = await api.get('/documents/visit-reports/');
      return response.data;
    }
  });

  // Query para obtener incidencias abiertas
  const { data: openIncidents, isLoading: incidentsLoading } = useQuery({
    queryKey: ['incidents', { estado: 'abierto' }],
    queryFn: async () => {
      const response = await api.get('/incidents/', {
        params: { estado: 'abierto' }
      });
      return response.data;
    }
  });

  // Mutación para crear reporte (restaurada)
  const createVisitReportMutation = useMutation({
    mutationFn: (data) => api.post('/documents/visit-reports/', data),
    onSuccess: () => {
      queryClient.invalidateQueries(['visit-reports']);
      setShowCreateModal(false);
      resetForm();
      alert('Reporte creado exitosamente');
    },
    onError: (error) => {
      console.error('Error creating report:', error);
      alert('Error al crear el reporte');
    }
  });

  // Mutación para subir documento (restaurada)
  const uploadDocumentMutation = useMutation({
    mutationFn: (data) => api.post('/documents/upload/visit-report/', data, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
    onSuccess: () => {
      queryClient.invalidateQueries(['visit-reports']);
      setShowUploadModal(false);
      setSelectedIncidentId('');
      alert('Documento adjuntado exitosamente');
    },
    onError: (error) => {
      console.error('Error uploading document:', error);
      alert('Error al subir el documento');
    }
  });

  // Filtrar reportes por término de búsqueda
  const filteredReports = useMemo(() => {
    if (!reports?.results) return [];
    
    return reports.results.filter(report => 
      !searchTerm || 
      report.order_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      report.incident_code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      report.client_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      report.project_name?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [reports?.results, searchTerm]);

  // Manejar cambios en el formulario (restaurada)
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Resetear formulario (restaurada)
  const resetForm = () => {
    setFormData({
      related_incident_id: '',
      order_number: `ORD-${Date.now()}`,
      visit_date: new Date().toISOString().split('T')[0],
      project_name: '',
      client_name: '',
      address: '',
      salesperson: '',
      technician: '',
      commune: '',
      city: '',
      visit_reason: '',
      general_observations: '',
      status: 'draft'
    });
  };

  // Manejar envío del formulario (restaurada)
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      await createVisitReportMutation.mutateAsync(formData);
    } catch (error) {
      console.error('Error submitting form:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Manejar creación de reporte (redirigir al formulario específico)
  const handleCreateReport = () => {
    if (!selectedIncidentId) {
      alert('Por favor selecciona una incidencia');
      return;
    }
    
    // Redirigir al formulario específico de reporte de visita
    navigate(`/visit-report-form?incident_id=${selectedIncidentId}&report_type=cliente`);
  };

  // Manejar subida de documento (restaurada con mejoras)
  const handleUploadDocument = () => {
    if (!selectedIncidentId) {
      alert('Por favor selecciona una incidencia');
      return;
    }

    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.pdf,.doc,.docx';
    input.onchange = (e) => {
      const file = e.target.files[0];
      if (file) {
        const uploadData = new FormData();
        uploadData.append('file', file);
        uploadData.append('incident_id', selectedIncidentId);
        uploadData.append('document_type', 'visit-report');
        uploadData.append('report_type', 'cliente'); // Siempre cliente para reportes de visita
        
        uploadDocumentMutation.mutate(uploadData);
      }
    };
    input.click();
  };

  // Manejar apertura de documento
  const handleOpenDocument = async (report) => {
    // Verificar que los valores necesarios estén disponibles
    if (!report.related_incident) {
      alert('No se puede abrir el documento: faltan datos del reporte');
      return;
    }
    
    const incidentId = typeof report.related_incident === 'object' 
      ? report.related_incident.id 
      : report.related_incident;
    
    // Usar la URL de descarga del reporte si está disponible
    if (report.download_url) {
      const { API_ORIGIN } = await import('../services/api');
      const url = `${API_ORIGIN}${report.download_url}`;
      window.open(url, '_blank');
    } else {
      alert('No hay documento disponible para este reporte');
    }
  };

  // Manejar eliminación de reporte
  const handleDeleteReport = async (reportId) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este reporte?')) {
      try {
        await api.delete(`/documents/visit-reports/${reportId}/`);
        queryClient.invalidateQueries(['visit-reports']);
        alert('Reporte eliminado exitosamente');
      } catch (error) {
        console.error('Error deleting report:', error);
        alert('Error al eliminar el reporte');
      }
    }
  };

  // Manejar escalamiento a calidad
  const handleEscalateToQuality = async (report) => {
    if (!window.confirm('¿Estás seguro de que quieres escalar esta incidencia a calidad?')) {
      return;
    }

    try {
      const incidentId = typeof report.related_incident === 'object' ? report.related_incident.id : report.related_incident;
      const response = await api.post(`/incidents/${incidentId}/escalate/quality/`, {
        reason: 'Escalado automáticamente desde reporte de visita'
      });
      
      if (response.data.success) {
        queryClient.invalidateQueries(['visit-reports']);
        alert('Incidencia escalada a calidad exitosamente. Se ha enviado un correo de notificación.');
      }
    } catch (error) {
      console.error('Error escalating to quality:', error);
      alert('Error al escalar la incidencia a calidad');
    }
  };

  // Manejar cierre de incidencia
  const handleCloseIncident = async (incidentId) => {
    if (window.confirm('¿Estás seguro de que quieres cerrar esta incidencia?')) {
      try {
        const incidentIdValue = typeof incidentId === 'object' ? incidentId.id : incidentId;
        const response = await api.post(`/incidents/${incidentIdValue}/close/`);
        
        if (response.data.success) {
          queryClient.invalidateQueries(['visit-reports']);
          alert('Incidencia cerrada exitosamente');
        }
      } catch (error) {
        console.error('Error closing incident:', error);
        alert('Error al cerrar la incidencia');
      }
    }
  };

  if (reportsLoading || incidentsLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-6"></div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Cargando Reportes</h3>
          <p className="text-gray-600">Preparando la información...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ClipboardDocumentListIcon className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <h1 className="text-xl font-semibold text-gray-900">
                  Reportes de Visita
                </h1>
                <p className="text-sm text-gray-500">
                  Gestión de reportes de visita de incidencias
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowCreateModal(true)}
                className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-xl text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 shadow-lg hover:shadow-xl transition-all duration-200"
              >
                <PlusIcon className="h-5 w-5 mr-2" />
                Crear Reporte
              </button>
              <button
                onClick={() => setShowUploadModal(true)}
                className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-xl text-white bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 shadow-lg hover:shadow-xl transition-all duration-200"
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
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-gray-900">Filtros y Búsqueda</h2>
            <button
              onClick={() => setSearchTerm('')}
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <ArrowPathIcon className="h-4 w-4 mr-2" />
              Limpiar
            </button>
          </div>
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar por número de orden, código de incidencia, cliente o proyecto..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Lista de Reportes */}
        <div className="bg-white rounded-lg shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-medium text-gray-900">
                Reportes de Visita Generados
              </h2>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
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
                      Categoría
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
                            <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                              <DocumentTextIcon className="h-5 w-5 text-blue-600" />
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">
                              {report.order_number}
                            </div>
                            <div className="text-sm text-gray-500">
                              {report.project_name}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{report.categoria}</div>
                        {report.subcategoria && (
                          <div className="text-sm text-gray-500">{report.subcategoria}</div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{report.client_name}</div>
                        <div className="text-sm text-gray-500">{report.address}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {new Date(report.visit_date).toLocaleDateString()}
                        </div>
                        <div className="text-sm text-gray-500">
                          {report.salesperson}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          report.status === 'cerrado' ? 'bg-green-100 text-green-800' :
                          report.status === 'laboratorio' ? 'bg-purple-100 text-purple-800' :
                          'bg-blue-100 text-blue-800'
                        }`}>
                          {report.status === 'cerrado' ? 'Cerrado' :
                           report.status === 'laboratorio' ? 'Laboratorio' :
                           'Abierto'}
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
                          {!report.escalated_to_quality && (
                            <button
                              onClick={() => handleEscalateToQuality(report)}
                              className="text-orange-600 hover:text-orange-900 p-1 rounded-md hover:bg-orange-50"
                              title="Escalar a Calidad"
                            >
                              <ArrowUpIcon className="h-4 w-4" />
                            </button>
                          )}
                          <button
                            onClick={() => handleCloseIncident(report.related_incident)}
                            className="text-green-600 hover:text-green-900 p-1 rounded-md hover:bg-green-50"
                            title="Cerrar Incidencia"
                          >
                            <CheckCircleIcon className="h-4 w-4" />
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
              <ClipboardDocumentListIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No hay reportes</h3>
              <p className="mt-1 text-sm text-gray-500">
                Comienza creando un nuevo reporte de visita.
              </p>
              <div className="mt-6">
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <PlusIcon className="h-4 w-4 mr-2" />
                  Crear Primer Reporte
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Modal de Crear Reporte - SOLO SELECCIÓN DE INCIDENCIA */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
          <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-md">
            <div className="px-6 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-t-2xl">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white flex items-center">
                  <PlusIcon className="h-5 w-5 mr-2" />
                  Crear Reporte de Visita
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
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Seleccionar incidencia...</option>
                  {(openIncidents?.data?.results || openIncidents?.results || []).map((incident) => (
                    <option key={incident.id} value={incident.id}>
                      {incident.code} - {incident.cliente} - {incident.provider}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex justify-end pt-4 border-t border-gray-200">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-6 py-2 text-sm font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gray-500 mr-3"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleCreateReport}
                  disabled={!selectedIncidentId}
                  className="px-6 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
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
            <div className="px-6 py-4 bg-gradient-to-r from-green-600 to-emerald-600 rounded-t-2xl">
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
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="">Seleccionar incidencia...</option>
                  {(openIncidents?.data?.results || openIncidents?.results || []).map((incident) => (
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
                  className="w-full flex items-center justify-center px-6 py-4 border-2 border-dashed border-gray-300 text-sm font-semibold rounded-xl text-gray-700 bg-white hover:bg-gray-50 hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-all duration-200 shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
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

export default VisitReportsPage;