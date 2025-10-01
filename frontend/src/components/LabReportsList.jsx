import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  BeakerIcon,
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

const LabReportsList = () => {
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

  // Obtener informes de laboratorio
  const { data: reports, isLoading, error } = useQuery({
    queryKey: ['lab-reports'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/documents/lab-reports/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) throw new Error('Error al cargar informes de laboratorio');
      return response.json();
    },
  });

  // Obtener incidencias abiertas
  const { data: openIncidents } = useQuery({
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

  // Filtrar incidencias que ya tienen reportes de laboratorio
  const availableIncidents = useMemo(() => {
    if (!openIncidents?.results || !reports) return [];
    
    // Extraer el array de reportes de la respuesta
    const reportsArray = reports?.results || reports?.data || reports || [];
    
    const incidentIdsWithLabReports = new Set(
      reportsArray.map(report => report.related_incident?.id).filter(Boolean)
    );
    
    return openIncidents.results.filter(incident => 
      !incidentIdsWithLabReports.has(incident.id)
    );
  }, [openIncidents, reports]);

  // Mutación para eliminar informe
  const deleteReportMutation = useMutation({
    mutationFn: async (id) => {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/documents/lab-reports/${id}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error al eliminar informe');
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['lab-reports']);
      showSuccess('Informe de laboratorio eliminado exitosamente');
      setShowDeleteModal(false);
      setSelectedReport(null);
    },
    onError: (error) => {
      showError('Error al eliminar informe: ' + error.message);
    },
  });

  // Mutación para subir documento adjunto
  const uploadDocumentMutation = useMutation({
    mutationFn: async ({ incidentId, file }) => {
      const token = localStorage.getItem('access_token');
      const formData = new FormData();
      formData.append('incident_id', incidentId);
      formData.append('document_type', 'lab_report');
      formData.append('file', file);
      formData.append('title', `Informe de Laboratorio - ${file.name}`);
      formData.append('description', 'Documento adjunto de informe de laboratorio');

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
      queryClient.invalidateQueries(['lab-reports']);
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

  // Mutación para crear informe de laboratorio
  const createLabReportMutation = useMutation({
    mutationFn: async (incidentId) => {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/documents/lab-reports/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          related_incident_id: incidentId,
          form_number: 'FORM-SERTEC-0007',
          request_date: new Date().toISOString().split('T')[0],
          applicant: 'POLIFUSION',
          client: 'Cliente por definir',
          description: 'Análisis técnico pendiente de completar',
          project_background: '',
          tests_performed: {},
          comments: '',
          conclusions: '',
          recommendations: '',
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
      showSuccess('Informe de laboratorio creado exitosamente');
      queryClient.invalidateQueries(['lab-reports']);
      setShowCreateModal(false);
      setSelectedIncidentId('');
      // Abrir el reporte creado para edición
      if (data && data.id) {
        window.open(`/documents/lab-reports/${data.id}/edit`, '_blank');
      }
    },
    onError: (error) => {
      console.error('Error creating lab report:', error);
      showError('Error al crear informe: ' + error.message);
    },
  });

  // Mutación para generar documento
  const generateDocumentMutation = useMutation({
    mutationFn: async (reportId) => {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/documents/generate/lab-report/${reportId}/`, {
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
      queryClient.invalidateQueries(['lab-reports']);
    },
    onError: (error) => {
      showError('Error al generar documento: ' + error.message);
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

  const handleViewPDF = (report) => {
    if (report.pdf_path) {
      // Si ya existe un PDF generado, mostrarlo
      setPdfUrl(`/api/documents/shared/lab_reports/${report.pdf_path.split('/').pop()}/view/`);
      setShowPDFViewer(true);
    } else {
      showError('No hay PDF generado para este informe. Genere el documento primero.');
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
        <BeakerIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Error al cargar informes de laboratorio</h3>
        <p className="text-gray-600">{error.message}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header con botón de crear */}
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-medium text-gray-900">Informes de Laboratorio</h3>
          <p className="text-sm text-gray-500">Gestión de informes de análisis de laboratorio</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
        >
          <PlusIcon className="h-4 w-4 mr-2" />
          Nuevo Informe
        </button>
      </div>

      {/* Lista de Informes */}
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
                        <strong>Cliente:</strong> {report.client}
                      </p>
                      <p className="text-sm text-gray-600">
                        <strong>Incidencia:</strong> {report.related_incident?.code || 'N/A'}
                      </p>
                      <p className="text-sm text-gray-600">
                        <strong>Reporte de Visita:</strong> {report.related_visit_report?.report_number || 'N/A'}
                      </p>
                      <p className="text-sm text-gray-600">
                        <strong>Fecha:</strong> {new Date(report.request_date).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
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
                    title="Editar informe"
                  >
                    <PencilIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(report)}
                    className="text-red-600 hover:text-red-900"
                    title="Eliminar informe"
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
                ¿Eliminar informe?
              </h3>
              <div className="mt-2">
                <p className="text-sm text-gray-500">
                  ¿Estás seguro de que deseas eliminar el informe {selectedReport?.report_number}? 
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
              filename={selectedReport?.report_number ? `Informe_Lab_${selectedReport.report_number}.pdf` : 'Informe_Lab.pdf'}
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
                <h3 className="text-lg font-medium text-gray-900">Nuevo Informe de Laboratorio</h3>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Seleccionar Incidencia
                  </label>
                  <select 
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                    value={selectedIncidentId}
                    onChange={(e) => setSelectedIncidentId(e.target.value)}
                  >
                    <option value="">Selecciona una incidencia abierta</option>
                                    {availableIncidents?.map((incident) => (
                                        <option key={incident.id} value={incident.id}>
                                            {incident.code} - {incident.cliente} - {incident.sku}
                                        </option>
                                    ))}
                  </select>
                  {availableIncidents?.length === 0 && !openIncidentsLoading && (
                    <p className="text-yellow-600 text-sm mt-1">
                      No hay incidencias abiertas disponibles para crear reportes de laboratorio
                    </p>
                  )}
                </div>
                
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
                      createLabReportMutation.mutate(selectedIncidentId);
                    }}
                    disabled={createLabReportMutation.isPending || !selectedIncidentId}
                    className="px-4 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {createLabReportMutation.isPending ? 'Creando...' : 'Crear Informe'}
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

export default LabReportsList;
