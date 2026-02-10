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
  const [searchTerm, setSearchTerm] = useState('');
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

  const filteredReports = reports.filter(report => {
    const matchesSearch =
      report.report_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      report.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (report.related_incident?.code || '').toLowerCase().includes(searchTerm.toLowerCase());

    // El filtro de tipo ya se hace en el backend? No, se hace en availableIncidents filters.
    // Pero la lista 'reports' trae TODOS? 
    // Viendo queryFn: fetch('/api/documents/quality-reports/') -> Trae todos.
    // Así que filtraremos por tipo aquí para la vista.
    const matchesType = report.report_type === selectedReportType;

    return matchesSearch && matchesType;
  });

  return (
    <div className="space-y-8">
      {/* Modern Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-slate-800 to-slate-600">
            🧪 Reportes de Calidad
          </h1>
          <p className="mt-1 text-slate-500 font-medium">Gestión integral de calidad (Interna y Cliente)</p>
        </div>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={() => setShowAttachModal(true)}
            className="flex items-center px-5 py-2.5 bg-white border border-slate-200 text-slate-700 font-bold rounded-xl shadow-sm hover:bg-slate-50 hover:border-slate-300 transition-all duration-200"
          >
            <DocumentTextIcon className="h-5 w-5 mr-2 text-slate-500" />
            Adjuntar
          </button>
          <button
            onClick={() => navigate('/quality-reports/form')}
            className="flex items-center px-6 py-2.5 bg-gradient-to-r from-blue-600 to-cyan-600 text-white font-bold rounded-xl shadow-lg shadow-blue-200 hover:shadow-blue-300 transform hover:-translate-y-0.5 transition-all duration-200"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Nuevo Reporte
          </button>
        </div>
      </div>

      {/* Search Bar & Tabs Container */}
      <div className="bg-gradient-to-r from-violet-600 to-fuchsia-600 rounded-2xl p-6 shadow-xl shadow-fuchsia-100 text-white space-y-6">
        {/* Search */}
        <div className="flex items-center gap-4">
          <div className="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
            <EyeIcon className="h-6 w-6 text-white" />
          </div>
          <div className="flex-1">
            <label className="block text-xs font-semibold text-fuchsia-100 uppercase tracking-wide mb-1">
              Búsqueda Inteligente
            </label>
            <input
              type="text"
              placeholder="Buscar por título, número o incidencia..."
              className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white placeholder-white/60 focus:outline-none focus:bg-white/20 focus:border-white/40 transition-all font-medium"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        {/* Modern Tabs */}
        <div className="flex space-x-1 bg-black/20 p-1 rounded-xl w-fit">
          <button
            onClick={() => setSelectedReportType('cliente')}
            className={`px-6 py-2 rounded-lg text-sm font-bold transition-all duration-200 ${selectedReportType === 'cliente'
                ? 'bg-white text-violet-600 shadow-md'
                : 'text-white/70 hover:bg-white/10 hover:text-white'
              }`}
          >
            📋 Para Cliente
          </button>
          <button
            onClick={() => setSelectedReportType('interno')}
            className={`px-6 py-2 rounded-lg text-sm font-bold transition-all duration-200 ${selectedReportType === 'interno'
                ? 'bg-white text-violet-600 shadow-md'
                : 'text-white/70 hover:bg-white/10 hover:text-white'
              }`}
          >
            🔍 Interno
          </button>
        </div>
      </div>

      {/* Modern Glass List */}
      <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-slate-100">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-100">
            <thead className="bg-slate-50/50">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Estado</th>
                <th className="px-6 py-4 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Reporte</th>
                <th className="px-6 py-4 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Incidencia</th>
                <th className="px-6 py-4 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Fecha</th>
                <th className="px-6 py-4 text-right text-xs font-bold text-slate-500 uppercase tracking-wider">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50 bg-white">
              {filteredReports.map((report) => (
                <tr key={report.id} className="hover:bg-slate-50/80 transition-colors duration-150">
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold border ${report.status === 'approved' ? 'bg-green-50 text-green-700 border-green-200' :
                        report.status === 'sent' ? 'bg-blue-50 text-blue-700 border-blue-200' :
                          report.status === 'draft' ? 'bg-slate-50 text-slate-600 border-slate-200' :
                            'bg-amber-50 text-amber-700 border-amber-200'
                      }`}>
                      {report.status === 'draft' ? 'Borrador' :
                        report.status === 'approved' ? 'Aprobado' :
                          report.status === 'sent' ? 'Enviado' : 'Revisión'}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-col">
                      <span className="text-sm font-bold text-slate-800">{report.report_number}</span>
                      <span className="text-sm text-slate-600 font-medium line-clamp-1">{report.title}</span>
                      <span className="text-xs text-slate-400 mt-1 uppercase tracking-wider font-semibold">
                        {report.report_type}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    {report.related_incident?.code ? (
                      <span className="inline-flex items-center text-xs font-medium text-fuchsia-600 bg-fuchsia-50 px-2 py-1 rounded-md">
                        {report.related_incident.code}
                      </span>
                    ) : <span className="text-slate-400 text-xs">N/A</span>}
                  </td>
                  <td className="px-6 py-4 text-sm font-medium text-slate-500">
                    {new Date(report.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-right space-x-2">
                    {report.pdf_path && (
                      <button
                        onClick={() => handleViewPDF(report)}
                        className="text-white bg-purple-100 hover:bg-purple-200 p-2 rounded-lg transition-colors group"
                        title="Ver PDF"
                      >
                        <EyeIcon className="h-5 w-5 text-purple-600 group-hover:text-purple-700" />
                      </button>
                    )}
                    <button
                      onClick={() => handleEdit(report)}
                      className="text-white bg-blue-100 hover:bg-blue-200 p-2 rounded-lg transition-colors group"
                      title="Editar"
                    >
                      <PencilIcon className="h-5 w-5 text-blue-600 group-hover:text-blue-700" />
                    </button>
                    <button
                      onClick={() => handleDelete(report)}
                      className="text-white bg-red-100 hover:bg-red-200 p-2 rounded-lg transition-colors group"
                      title="Eliminar"
                    >
                      <TrashIcon className="h-5 w-5 text-red-600 group-hover:text-red-700" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filteredReports.length === 0 && (
            <div className="p-12 text-center text-slate-400">
              <DocumentTextIcon className="w-16 h-16 mx-auto mb-4 text-slate-200" />
              <p className="text-lg font-medium">No se encontraron reportes</p>
              <p className="text-sm">Cambie el tipo de filtro o cree un nuevo reporte.</p>
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
