import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  ClipboardDocumentListIcon, 
  PlusIcon, 
  EyeIcon, 
  PencilIcon, 
  TrashIcon,
  CheckCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  DocumentTextIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import { useNotifications } from '../hooks/useNotifications';
import PDFViewer from './PDFViewer';

const VisitReportsList = () => {
  const navigate = useNavigate();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedIncidentId, setSelectedIncidentId] = useState('');
  const [createMode, setCreateMode] = useState('form'); // 'form' o 'upload'
  const [selectedFile, setSelectedFile] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showPDFViewer, setShowPDFViewer] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);
  const [pdfUrl, setPdfUrl] = useState(null);
  const { showSuccess, showError } = useNotifications();
  const queryClient = useQueryClient();

  // Obtener reportes de visita
  const { data: reports, isLoading, error } = useQuery({
    queryKey: ['visit-reports'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/documents/visit-reports/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) throw new Error('Error al cargar reportes de visita');
      return response.json();
    },
  });

  // Obtener incidencias abiertas
  const { data: openIncidents, isLoading: openIncidentsLoading, error: openIncidentsError } = useQuery({
    queryKey: ['open-incidents'],
    queryFn: async () => {
      console.log('=== EXECUTING OPEN INCIDENTS QUERY ===');
      const token = localStorage.getItem('access_token');
      console.log('Token exists:', !!token);
      console.log('Token preview:', token ? token.substring(0, 20) + '...' : 'No token');
      
      const response = await fetch('/api/incidents/?estado=abierto', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      console.log('Response status:', response.status);
      console.log('Response ok:', response.ok);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.log('Error response:', errorText);
        throw new Error(`Error al cargar incidencias: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('=== OPEN INCIDENTS DEBUG ===');
      console.log('Open incidents response:', data);
      console.log('Data structure:', data?.data);
      console.log('Incidents array:', data?.results);
      console.log('Incidents count:', data?.results?.length);
      return data;
    },
    retry: 1,
    retryDelay: 1000,
  });

  // Filtrar incidencias que ya tienen reportes de visita
  const availableIncidents = useMemo(() => {
    if (!openIncidents?.results || !reports) return [];
    
    // Extraer el array de reportes de la respuesta
    const reportsArray = reports?.results || reports?.data || reports || [];
    
    const incidentIdsWithVisitReports = new Set(
      reportsArray.map(report => report.related_incident?.id).filter(Boolean)
    );
    
    return openIncidents.results.filter(incident => 
      !incidentIdsWithVisitReports.has(incident.id)
    );
  }, [openIncidents, reports]);

  // Mutación para subir documento adjunto
  const uploadDocumentMutation = useMutation({
    mutationFn: async ({ incidentId, file }) => {
      const token = localStorage.getItem('access_token');
      const formData = new FormData();
      formData.append('incident_id', incidentId);
      formData.append('document_type', 'visit_report');
      formData.append('file', file);
      formData.append('title', `Reporte de Visita - ${file.name}`);
      formData.append('description', 'Documento adjunto de reporte de visita');

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
      showSuccess('Documento adjunto subido exitosamente');
      queryClient.invalidateQueries(['visit-reports']);
      setShowCreateModal(false);
      setSelectedIncidentId('');
      setSelectedFile(null);
      setCreateMode('form');
    },
    onError: (error) => {
      console.error('Error uploading document:', error);
      showError('Error al subir documento: ' + error.message);
    },
  });

  // Mutación para crear reporte de visita
  const createVisitReportMutation = useMutation({
    mutationFn: async (incidentId) => {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/documents/visit-reports/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          related_incident_id: incidentId,
          order_number: `ORD-${new Date().getFullYear()}-${String(Date.now()).slice(-3)}`,
          visit_date: new Date().toISOString(),
          project_name: 'Proyecto por definir',
          project_id: '',
          client_name: 'Cliente por definir',
          client_rut: '',
          address: 'Dirección por definir',
          construction_company: '',
          salesperson: 'Vendedor por asignar',
          technician: 'Técnico por asignar',
          installer: '',
          installer_phone: '',
          commune: 'Comuna por definir',
          city: 'Ciudad por definir',
          visit_reason: 'Inspección técnica',
          machine_data: {},
          wall_observations: '',
          matrix_observations: '',
          slab_observations: '',
          storage_observations: '',
          pre_assembled_observations: '',
          exterior_observations: '',
          general_observations: 'Observaciones pendientes de completar',
          status: 'draft'
        }),
      });
      if (!response.ok) {
        let errorMessage = `Error del servidor (${response.status})`;
        try {
          const errorData = await response.json();
          console.error('Error response:', errorData);
          errorMessage = errorData.error || errorData.detail || errorMessage;
        } catch (e) {
          // Si no se puede parsear como JSON, usar el status
          console.error('Error response (not JSON):', response.status, response.statusText);
        }
        throw new Error(errorMessage);
      }
      return response.json();
    },
    onSuccess: (data) => {
      showSuccess('Reporte de visita creado exitosamente');
      queryClient.invalidateQueries(['visit-reports']);
      setShowCreateModal(false);
      setSelectedIncidentId('');
      // Abrir el reporte creado para edición
      if (data && data.id) {
        window.open(`/documents/visit-reports/${data.id}/edit`, '_blank');
      }
    },
    onError: (error) => {
      console.error('Error creating visit report:', error);
      showError('Error al crear reporte: ' + error.message);
    },
  });

  // Mutación para generar documento
  const generateDocumentMutation = useMutation({
    mutationFn: async (reportId) => {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/documents/generate/visit-report/${reportId}/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error al generar documento');
      }
      return response.json();
    },
    onSuccess: (data) => {
      showSuccess('Documento generado exitosamente: ' + data.filename);
      queryClient.invalidateQueries(['visit-reports']);
    },
    onError: (error) => {
      showError('Error al generar documento: ' + error.message);
    },
  });

  // Mutación para eliminar reporte
  const deleteReportMutation = useMutation({
    mutationFn: async (id) => {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/documents/visit-reports/${id}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error al eliminar reporte');
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['visit-reports']);
      showSuccess('Reporte de visita eliminado exitosamente');
      setShowDeleteModal(false);
      setSelectedReport(null);
    },
    onError: (error) => {
      showError('Error al eliminar reporte: ' + error.message);
    },
  });

  const handleEdit = (report) => {
    setSelectedReport(report);
    setShowEditModal(true);
  };

  const handleDelete = (report) => {
    setSelectedReport(report);
    setShowDeleteModal(true);
  };

  const handleDeleteConfirm = () => {
    if (selectedReport) {
      deleteReportMutation.mutate(selectedReport.id);
    }
  };

  const handleGenerateDocument = (report) => {
    generateDocumentMutation.mutate(report.id);
  };

  const handleViewPDF = (report) => {
    if (report.pdf_path) {
      // Si ya existe un PDF generado, mostrarlo
      setPdfUrl(`/api/documents/shared/visit_reports/${report.pdf_path.split('/').pop()}/view/`);
      setShowPDFViewer(true);
    } else {
      showError('No hay PDF generado para este reporte. Genere el documento primero.');
    }
  };

  const handleOpenDocument = async (report) => {
    try {
      const filename = report.pdf_filename || 'documento.pdf';
      const encodedFilename = encodeURIComponent(filename);
      const { API_ORIGIN } = await import('../services/api');
      const url = `${API_ORIGIN}/api/documents/open/visit-report/${report.related_incident?.id}/${encodedFilename}`;
      
      // Abrir directamente en el navegador
      window.open(url, '_blank');
      showSuccess('Documento abierto exitosamente');
    } catch (error) {
      console.error('Error opening document:', error);
      showError('Error al abrir documento: ' + error.message);
    }
  };

  const handleClosePDFViewer = () => {
    setShowPDFViewer(false);
    setPdfUrl(null);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'approved':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'sent':
        return <CheckCircleIcon className="h-5 w-5 text-blue-500" />;
      case 'pending_review':
        return <ClockIcon className="h-5 w-5 text-yellow-500" />;
      case 'draft':
        return <ExclamationTriangleIcon className="h-5 w-5 text-gray-500" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'approved':
        return 'Aprobado';
      case 'sent':
        return 'Enviado';
      case 'pending_review':
        return 'Pendiente de Revisión';
      case 'draft':
        return 'Borrador';
      default:
        return status;
    }
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
        <ClipboardDocumentListIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Error al cargar reportes de visita</h3>
        <p className="text-gray-600">{error.message}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header con botón de crear */}
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-medium text-gray-900">Reportes de Visita</h3>
          <p className="text-sm text-gray-500">Gestión de reportes de visita técnica</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <PlusIcon className="h-4 w-4 mr-2" />
          Nuevo Reporte
        </button>
      </div>

      {/* Lista de Reportes */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {(reports?.results || reports?.data || reports || []).map((report) => (
            <li key={report.id}>
              <div className="px-4 py-4 flex items-center justify-between">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    {getStatusIcon(report.status)}
                  </div>
                  <div className="ml-4">
                    <div className="flex items-center">
                      <p className="text-sm font-medium text-gray-900">
                        {report.report_number}
                      </p>
                      <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                        {getStatusText(report.status)}
                      </span>
                    </div>
                    <div className="mt-1">
                      <p className="text-sm text-gray-600">
                        <strong>Proyecto:</strong> {report.project_name}
                      </p>
                      <p className="text-sm text-gray-600">
                        <strong>Cliente:</strong> {report.client_name}
                      </p>
                      <p className="text-sm text-gray-600">
                        <strong>Incidencia:</strong> {report.related_incident?.code || 'N/A'}
                      </p>
                      <p className="text-sm text-gray-600">
                        <strong>Fecha:</strong> {new Date(report.visit_date).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleGenerateDocument(report)}
                    disabled={generateDocumentMutation.isPending}
                    className="text-green-600 hover:text-green-900 disabled:opacity-50"
                    title="Generar documento DOCX"
                  >
                    <DocumentTextIcon className="h-4 w-4" />
                  </button>
                  {report.pdf_path && (
                    <button
                      onClick={() => handleViewPDF(report)}
                      className="text-purple-600 hover:text-purple-900"
                      title="Ver PDF generado"
                    >
                      <EyeIcon className="h-4 w-4" />
                    </button>
                  )}
                  {report.pdf_path && (
                    <button
                      onClick={() => handleOpenDocument(report)}
                      className="text-green-600 hover:text-green-900"
                      title="Abrir documento en carpeta compartida"
                    >
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
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
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>

      {/* Modal de Confirmación de Eliminación */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3 text-center">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
                <TrashIcon className="h-6 w-6 text-red-600" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mt-4">
                ¿Eliminar reporte?
              </h3>
              <div className="mt-2">
                <p className="text-sm text-gray-500">
                  ¿Estás seguro de que deseas eliminar el reporte {selectedReport?.report_number}? 
                  Esta acción no se puede deshacer.
                </p>
              </div>
              <div className="flex justify-center space-x-3 mt-4">
                <button
                  onClick={() => {
                    setShowDeleteModal(false);
                    setSelectedReport(null);
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleDeleteConfirm}
                  disabled={deleteReportMutation.isPending}
                  className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 disabled:opacity-50"
                >
                  {deleteReportMutation.isPending ? 'Eliminando...' : 'Eliminar'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Visor PDF */}
      {showPDFViewer && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="w-full max-w-6xl max-h-full">
            <PDFViewer
              pdfUrl={pdfUrl}
              filename={selectedReport?.report_number ? `Reporte_Visita_${selectedReport.report_number}.pdf` : 'Reporte_Visita.pdf'}
              onClose={handleClosePDFViewer}
              showDownload={true}
              showPrint={true}
            />
          </div>
        </div>
      )}

      {/* Modal de Creación */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Nuevo Reporte de Visita</h3>
                <button
                  onClick={() => {
                    setShowCreateModal(false);
                    setCreateMode('form');
                    setSelectedFile(null);
                    setSelectedIncidentId('');
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
              
              {/* Opciones de creación */}
              <div className="mb-6">
                <div className="flex space-x-4">
                  <button
                    onClick={() => setCreateMode('form')}
                    className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                      createMode === 'form'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    📝 Crear con Formulario
                  </button>
                  <button
                    onClick={() => setCreateMode('upload')}
                    className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                      createMode === 'upload'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    📎 Adjuntar Documento
                  </button>
                </div>
              </div>
              
              <div className="space-y-4">
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
                  {openIncidentsError && (
                    <p className="text-red-500 text-sm mt-1">
                      Error: {openIncidentsError.message}
                    </p>
                  )}
                                {openIncidents?.results?.length === 0 && !openIncidentsLoading && (
                                    <p className="text-yellow-600 text-sm mt-1">
                                        No hay incidencias abiertas disponibles
                                    </p>
                                )}
                </div>

                {/* Contenido según el modo seleccionado */}
                {createMode === 'form' ? (
                  <div className="bg-blue-50 p-4 rounded-md">
                    <p className="text-sm text-blue-800">
                      📝 Se creará un nuevo reporte de visita con formulario que se guardará en la carpeta compartida como PDF.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="bg-green-50 p-4 rounded-md">
                      <p className="text-sm text-green-800">
                        📎 Se adjuntará un documento existente que se copiará a la carpeta compartida para trazabilidad.
                      </p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Seleccionar Archivo
                      </label>
                      <input
                        type="file"
                        accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png"
                        onChange={(e) => setSelectedFile(e.target.files[0])}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                      {selectedFile && (
                        <p className="text-sm text-gray-600 mt-1">
                          Archivo seleccionado: {selectedFile.name}
                        </p>
                      )}
                    </div>
                  </div>
                )}
                
                <div className="flex justify-end space-x-3">
                  <button
                    onClick={() => setShowCreateModal(false)}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
                  >
                    Cancelar
                  </button>
                  <button
                    onClick={() => {
                      if (!selectedIncidentId) {
                        showError('Por favor selecciona una incidencia');
                        return;
                      }
                      
                      if (createMode === 'form') {
                        createVisitReportMutation.mutate(selectedIncidentId);
                      } else {
                        if (!selectedFile) {
                          showError('Por favor selecciona un archivo');
                          return;
                        }
                        uploadDocumentMutation.mutate({ incidentId: selectedIncidentId, file: selectedFile });
                      }
                    }}
                    disabled={
                      createVisitReportMutation.isPending || 
                      uploadDocumentMutation.isPending || 
                      !selectedIncidentId || 
                      (createMode === 'upload' && !selectedFile)
                    }
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {createVisitReportMutation.isPending || uploadDocumentMutation.isPending 
                      ? 'Procesando...' 
                      : createMode === 'form' 
                        ? 'Crear Reporte' 
                        : 'Subir Documento'
                    }
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VisitReportsList;
