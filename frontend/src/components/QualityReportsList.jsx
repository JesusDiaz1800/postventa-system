import React, { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  PlusIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  DocumentTextIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import { useNotifications } from '../hooks/useNotifications';
import PDFViewer from './PDFViewer';

const QualityReportsList = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { showSuccess, showError } = useNotifications();
  
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedIncidentId, setSelectedIncidentId] = useState('');
  const [selectedReportType, setSelectedReportType] = useState('cliente');
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showPDFViewer, setShowPDFViewer] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);
  const [pdfUrl, setPdfUrl] = useState(null);
  const [showAttachModal, setShowAttachModal] = useState(false);
  const [attachIncidentId, setAttachIncidentId] = useState('');
  const [attachReportType, setAttachReportType] = useState('cliente');
  const [selectedFile, setSelectedFile] = useState(null);

  // Query para obtener reportes de calidad
  const { data: qualityReportsData, isLoading, error } = useQuery({
    queryKey: ['quality-reports'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/documents/quality-reports/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) throw new Error('Error al cargar reportes de calidad');
      return response.json();
    },
  });

  // Query para obtener incidencias abiertas
  const { data: openIncidents, isLoading: openIncidentsLoading, error: openIncidentsError } = useQuery({
    queryKey: ['open-incidents'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/incidents/?estado=abierto', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) throw new Error('Error al cargar incidencias');
      return response.json();
    },
  });

  // Filtrar incidencias que no tienen reportes de calidad del tipo seleccionado
  const availableIncidents = useMemo(() => {
    if (!openIncidents?.results || !qualityReportsData) return [];
    
    // Extraer el array de reportes de la respuesta
    const reportsArray = qualityReportsData?.results || qualityReportsData?.data || qualityReportsData || [];
    
    const incidentIdsWithQualityReports = new Set(
      reportsArray
        .filter(report => report.report_type === selectedReportType)
        .map(report => report.related_incident?.id)
        .filter(Boolean)
    );
    
    return openIncidents.results.filter(incident => 
      !incidentIdsWithQualityReports.has(incident.id)
    );
  }, [openIncidents, qualityReportsData, selectedReportType]);

  // Mutación para crear reporte de calidad
  const createQualityReportMutation = useMutation({
    mutationFn: async ({ incidentId, reportType }) => {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/documents/quality-reports/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          report_type: reportType,
          related_incident_id: incidentId,
          title: `Informe de Calidad ${reportType === 'cliente' ? 'para Cliente' : 'Interno'} - ${new Date().toLocaleDateString()}`,
          executive_summary: 'Resumen ejecutivo pendiente de completar',
          problem_description: 'Descripción del problema pendiente de completar',
          root_cause_analysis: 'Análisis de causa raíz pendiente de completar',
          corrective_actions: 'Acciones correctivas pendientes de completar',
          preventive_measures: 'Medidas preventivas pendientes de completar',
          recommendations: 'Recomendaciones pendientes de completar',
          technical_details: reportType === 'interno' ? 'Detalles técnicos pendientes de completar' : '',
          internal_notes: reportType === 'interno' ? 'Notas internas pendientes de completar' : '',
          status: 'draft'
        }),
      });
      if (!response.ok) {
        let errorMessage = `Error del servidor (${response.status})`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.error || errorData.detail || errorMessage;
        } catch (e) {
          console.error('Error response (not JSON):', response.status, response.statusText);
        }
        throw new Error(errorMessage);
      }
      return response.json();
    },
    onSuccess: (data) => {
      showSuccess('Reporte de calidad creado exitosamente');
      queryClient.invalidateQueries(['quality-reports']);
      setShowCreateModal(false);
      setSelectedIncidentId('');
      setSelectedReportType('cliente');
      // Abrir el reporte creado para edición
      if (data && data.id) {
        window.open(`/documents/quality-reports/${data.id}/edit`, '_blank');
      }
    },
    onError: (error) => {
      console.error('Error creating quality report:', error);
      showError('Error al crear reporte: ' + error.message);
    },
  });

  // Mutación para eliminar reporte
  const deleteQualityReportMutation = useMutation({
    mutationFn: async (reportId) => {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/documents/quality-reports/${reportId}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (!response.ok) throw new Error('Error al eliminar reporte');
    },
    onSuccess: () => {
      showSuccess('Reporte eliminado exitosamente');
      queryClient.invalidateQueries(['quality-reports']);
      setShowDeleteModal(false);
      setSelectedReport(null);
    },
    onError: (error) => {
      showError('Error al eliminar reporte: ' + error.message);
    },
  });

  // Mutación para subir documento
  const uploadDocumentMutation = useMutation({
    mutationFn: async ({ incidentId, reportType, file, title }) => {
      const token = localStorage.getItem('access_token');
      const formData = new FormData();
      formData.append('incident_id', incidentId);
      formData.append('document_type', 'quality-report');
      formData.append('report_type', reportType);
      formData.append('title', title);
      formData.append('file', file);

      const response = await fetch('/api/documents/upload/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        let errorMessage = `Error del servidor (${response.status})`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.error || errorData.detail || errorMessage;
        } catch (e) {
          console.error('Error response (not JSON):', response.status, response.statusText);
        }
        throw new Error(errorMessage);
      }
      return response.json();
    },
    onSuccess: (data) => {
      showSuccess('Documento adjuntado exitosamente');
      queryClient.invalidateQueries(['quality-reports']);
      setShowAttachModal(false);
      setAttachIncidentId('');
      setAttachReportType('cliente');
      setSelectedFile(null);
    },
    onError: (error) => {
      console.error('Error uploading document:', error);
      showError('Error al adjuntar documento: ' + error.message);
    },
  });

  const handleCreate = () => {
    if (!selectedIncidentId) {
      showError('Por favor selecciona una incidencia');
      return;
    }
    createQualityReportMutation.mutate({ 
      incidentId: selectedIncidentId, 
      reportType: selectedReportType 
    });
  };

  const handleEdit = (report) => {
    navigate(`/documents/quality-reports/${report.id}/edit`);
  };

  const handleDelete = (report) => {
    setSelectedReport(report);
    setShowDeleteModal(true);
  };

  const handleConfirmDelete = () => {
    if (selectedReport) {
      deleteQualityReportMutation.mutate(selectedReport.id);
    }
  };

  const handleViewPDF = (report) => {
    if (report.pdf_path) {
      setPdfUrl(`/api/documents/shared/quality_reports/${report.pdf_path.split('/').pop()}/view/`);
      setShowPDFViewer(true);
    } else {
      showError('No hay PDF generado para este reporte. Genere el documento primero.');
    }
  };

  const handleClosePDFViewer = () => {
    setShowPDFViewer(false);
    setPdfUrl(null);
  };

  const handleAttachDocument = () => {
    if (!attachIncidentId) {
      showError('Por favor selecciona una incidencia');
      return;
    }
    if (!selectedFile) {
      showError('Por favor selecciona un archivo');
      return;
    }
    
    const title = `Documento ${attachReportType === 'cliente' ? 'para Cliente' : 'Interno'} - ${selectedFile.name}`;
    uploadDocumentMutation.mutate({ 
      incidentId: attachIncidentId, 
      reportType: attachReportType,
      file: selectedFile,
      title: title
    });
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
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
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <p className="text-red-800">Error al cargar reportes de calidad: {error.message}</p>
      </div>
    );
  }

  const reports = qualityReportsData?.results || qualityReportsData?.data || qualityReportsData || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Reportes de Calidad</h2>
          <p className="text-gray-600">Gestión de informes para cliente e internos</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowAttachModal(true)}
            className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <DocumentTextIcon className="h-4 w-4 mr-2" />
            Adjuntar Documento
          </button>
          <button
            onClick={() => navigate('/quality-reports/form')}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Nuevo Reporte
          </button>
        </div>
      </div>

      {/* Filtros */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="flex space-x-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tipo de Reporte
            </label>
            <select
              value={selectedReportType}
              onChange={(e) => setSelectedReportType(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="cliente">Informe para Cliente</option>
              <option value="interno">Informe Interno</option>
            </select>
          </div>
        </div>
      </div>

      {/* Tabla de reportes */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <div className="px-4 py-5 sm:p-6">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Número
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Tipo
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Incidencia
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Título
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Estado
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Creado
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {reports.map((report) => (
                  <tr key={report.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {report.report_number}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        report.report_type === 'cliente' 
                          ? 'bg-blue-100 text-blue-800' 
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {report.report_type === 'cliente' ? 'Cliente' : 'Interno'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {report.related_incident?.code || 'N/A'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {report.title}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        report.status === 'draft' ? 'bg-gray-100 text-gray-800' :
                        report.status === 'approved' ? 'bg-green-100 text-green-800' :
                        report.status === 'sent' ? 'bg-blue-100 text-blue-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {report.status === 'draft' ? 'Borrador' :
                         report.status === 'approved' ? 'Aprobado' :
                         report.status === 'sent' ? 'Enviado' :
                         report.status === 'review' ? 'En Revisión' : 'Cerrado'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(report.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                      {report.pdf_path && (
                        <button
                          onClick={() => handleViewPDF(report)}
                          className="text-purple-600 hover:text-purple-900"
                          title="Ver PDF generado"
                        >
                          <EyeIcon className="h-4 w-4" />
                        </button>
                      )}
                      <button
                        onClick={() => handleEdit(report)}
                        className="text-blue-600 hover:text-blue-900"
                        title="Editar reporte"
                      >
                        <PencilIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(report)}
                        className="text-red-600 hover:text-red-900"
                        title="Eliminar reporte"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {reports.length === 0 && (
            <div className="text-center py-8">
              <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No hay reportes de calidad</h3>
              <p className="mt-1 text-sm text-gray-500">Comienza creando un nuevo reporte de calidad.</p>
            </div>
          )}
        </div>
      </div>

      {/* Modal de Creación */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Nuevo Reporte de Calidad</h3>
                <button
                  onClick={() => {
                    setShowCreateModal(false);
                    setSelectedIncidentId('');
                    setSelectedReportType('cliente');
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tipo de Reporte
                  </label>
                  <select
                    value={selectedReportType}
                    onChange={(e) => setSelectedReportType(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="cliente">📋 Informe para Cliente</option>
                    <option value="interno">🔍 Informe Interno de la Incidencia</option>
                  </select>
                  <p className="text-sm text-gray-500 mt-1">
                    {selectedReportType === 'cliente' 
                      ? 'Versión para el cliente (información comercial)'
                      : 'Versión interna (causa real del problema)'
                    }
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Seleccionar Incidencia
                  </label>
                  <select
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={openIncidentsLoading}
                    value={selectedIncidentId}
                    onChange={(e) => setSelectedIncidentId(e.target.value)}
                  >
                    <option value="">
                      {openIncidentsLoading 
                        ? "Cargando incidencias..." 
                        : openIncidentsError 
                          ? "Error al cargar incidencias" 
                          : "Selecciona una incidencia abierta"
                      }
                    </option>
                    {availableIncidents?.map((incident) => (
                      <option key={incident.id} value={incident.id}>
                        {incident.code} - {incident.cliente} - {incident.sku}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleCreate}
                  disabled={createQualityReportMutation.isPending || !selectedIncidentId}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {createQualityReportMutation.isPending ? 'Creando...' : 'Crear Reporte'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Confirmación de Eliminación */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3 text-center">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
                <TrashIcon className="h-6 w-6 text-red-600" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mt-4">Eliminar Reporte</h3>
              <div className="mt-2">
                <p className="text-sm text-gray-500">
                  ¿Estás seguro de que quieres eliminar el reporte {selectedReport?.report_number}?
                  Esta acción no se puede deshacer.
                </p>
              </div>
              <div className="flex justify-center space-x-3 mt-6">
                <button
                  onClick={() => setShowDeleteModal(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleConfirmDelete}
                  disabled={deleteQualityReportMutation.isPending}
                  className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md disabled:opacity-50"
                >
                  {deleteQualityReportMutation.isPending ? 'Eliminando...' : 'Eliminar'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Adjuntar Documento */}
      {showAttachModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Adjuntar Documento de Calidad</h3>
                <button
                  onClick={() => {
                    setShowAttachModal(false);
                    setAttachIncidentId('');
                    setAttachReportType('cliente');
                    setSelectedFile(null);
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tipo de Documento
                  </label>
                  <select
                    value={attachReportType}
                    onChange={(e) => setAttachReportType(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="cliente">📋 Documento para Cliente</option>
                    <option value="interno">🔍 Documento Interno</option>
                  </select>
                  <p className="text-sm text-gray-500 mt-1">
                    {attachReportType === 'cliente' 
                      ? 'Documento que se compartirá con el cliente'
                      : 'Documento interno para análisis técnico'
                    }
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Seleccionar Incidencia
                  </label>
                  <select
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={openIncidentsLoading}
                    value={attachIncidentId}
                    onChange={(e) => setAttachIncidentId(e.target.value)}
                  >
                    <option value="">
                      {openIncidentsLoading 
                        ? "Cargando incidencias..." 
                        : openIncidentsError 
                          ? "Error al cargar incidencias" 
                          : "Selecciona una incidencia abierta"
                      }
                    </option>
                    {openIncidents?.results?.map((incident) => (
                      <option key={incident.id} value={incident.id}>
                        {incident.code} - {incident.cliente} - {incident.sku}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Seleccionar Archivo
                  </label>
                  <input
                    type="file"
                    onChange={handleFileSelect}
                    accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  {selectedFile && (
                    <p className="text-sm text-green-600 mt-1">
                      Archivo seleccionado: {selectedFile.name}
                    </p>
                  )}
                </div>
              </div>
              
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => setShowAttachModal(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleAttachDocument}
                  disabled={uploadDocumentMutation.isPending || !attachIncidentId || !selectedFile}
                  className="px-4 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {uploadDocumentMutation.isPending ? 'Adjuntando...' : 'Adjuntar Documento'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Visor de PDF */}
      {showPDFViewer && (
        <PDFViewer
          pdfUrl={pdfUrl}
          onClose={handleClosePDFViewer}
          title="Reporte de Calidad"
        />
      )}
    </div>
  );
};

export default QualityReportsList;
