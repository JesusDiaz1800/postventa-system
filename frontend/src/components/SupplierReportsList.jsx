import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  TruckIcon,
  PlusIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  CheckCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  PaperAirplaneIcon,
  DocumentTextIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import { useNotifications } from '../hooks/useNotifications';
import PDFViewer from './PDFViewer';

const SupplierReportsList = () => {
  const navigate = useNavigate();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
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

  // Obtener informes para proveedores
  const { data: reports, isLoading, error } = useQuery({
    queryKey: ['supplier-reports'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/documents/supplier-reports/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) throw new Error('Error al cargar informes para proveedores');
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

  // Mutación para eliminar informe
  const deleteReportMutation = useMutation({
    mutationFn: async (id) => {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/documents/supplier-reports/${id}/`, {
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
      queryClient.invalidateQueries(['supplier-reports']);
      showSuccess('Informe para proveedor eliminado exitosamente');
      setShowDeleteModal(false);
      setSelectedReport(null);
    },
    onError: (error) => {
      showError('Error al eliminar informe: ' + error.message);
    },
  });

  // Filtrar incidencias que ya tienen reportes de proveedor
  const availableIncidents = useMemo(() => {
    if (!openIncidents?.results || !reports) return [];

    // Extraer el array de reportes de la respuesta
    const reportsArray = reports?.results || reports?.data || reports || [];

    const incidentIdsWithSupplierReports = new Set(
      reportsArray.map(report => report.related_incident?.id).filter(Boolean)
    );

    return openIncidents.results.filter(incident =>
      !incidentIdsWithSupplierReports.has(incident.id)
    );
  }, [openIncidents, reports]);

  // Mutación para subir documento adjunto
  const uploadDocumentMutation = useMutation({
    mutationFn: async ({ incidentId, file }) => {
      const token = localStorage.getItem('access_token');
      const formData = new FormData();
      formData.append('incident_id', incidentId);
      formData.append('document_type', 'supplier_report');
      formData.append('file', file);
      formData.append('title', `Informe para Proveedor - ${file.name}`);
      formData.append('description', 'Documento adjunto de informe para proveedor');

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
      queryClient.invalidateQueries(['supplier-reports']);
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

  // Mutación para crear informe para proveedor
  const createSupplierReportMutation = useMutation({
    mutationFn: async (incidentId) => {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/documents/supplier-reports/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          related_incident_id: incidentId,
          report_date: new Date().toISOString().split('T')[0],
          supplier_name: 'Proveedor por definir',
          supplier_contact: '',
          supplier_email: '',
          subject: 'Comunicación técnica pendiente',
          introduction: '',
          problem_description: '',
          technical_analysis: '',
          recommendations: '',
          expected_improvements: '',
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
      showSuccess('Informe para proveedor creado exitosamente');
      queryClient.invalidateQueries(['supplier-reports']);
      setShowCreateModal(false);
      setSelectedIncidentId('');
      // Abrir el reporte creado para edición
      if (data && data.id) {
        window.open(`/documents/supplier-reports/${data.id}/edit`, '_blank');
      }
    },
    onError: (error) => {
      console.error('Error creating supplier report:', error);
      showError('Error al crear informe: ' + error.message);
    },
  });

  // Mutación para generar documento
  const generateDocumentMutation = useMutation({
    mutationFn: async (reportId) => {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/documents/generate/supplier-report/${reportId}/`, {
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
      queryClient.invalidateQueries(['supplier-reports']);
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
      setPdfUrl(`/api/documents/shared/supplier_reports/${report.pdf_path.split('/').pop()}/view/`);
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
        return <PaperAirplaneIcon className="h-5 w-5 text-blue-500" />;
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
        <TruckIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Error al cargar informes para proveedores</h3>
        <p className="text-gray-600">{error.message}</p>
      </div>
    );
  }

  const filteredReports = (reports?.results || reports?.data || reports || []).filter(report =>
    report.report_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
    report.supplier_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    report.subject.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-8">
      {/* Modern Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-slate-800 to-slate-600">
            🚚 Reportes de Proveedores
          </h1>
          <p className="mt-1 text-slate-500 font-medium">Gestione y supervise la comunicación técnica con sus proveedores</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center px-6 py-2.5 bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-bold rounded-xl shadow-lg shadow-indigo-200 hover:shadow-indigo-300 transform hover:-translate-y-0.5 transition-all duration-200"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Nuevo Informe
          </button>
        </div>
      </div>

      {/* Search Bar Professional */}
      <div className="bg-gradient-to-r from-violet-600 to-indigo-600 rounded-2xl p-6 shadow-xl shadow-indigo-100 text-white">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
            <DocumentTextIcon className="h-6 w-6 text-white" />
          </div>
          <div className="flex-1">
            <label className="block text-xs font-semibold text-indigo-100 uppercase tracking-wide mb-1">
              Búsqueda Rápida
            </label>
            <input
              type="text"
              placeholder="Buscar por número, proveedor o asunto..."
              className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white placeholder-white/60 focus:outline-none focus:bg-white/20 focus:border-white/40 transition-all font-medium"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* Modern Glass List */}
      <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-slate-100">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-100">
            <thead className="bg-slate-50/50">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Estado</th>
                <th className="px-6 py-4 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Detalles del Informe</th>
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
                          report.status === 'pending_review' ? 'bg-amber-50 text-amber-700 border-amber-200' :
                            'bg-slate-50 text-slate-600 border-slate-200'
                      }`}>
                      {getStatusIcon(report.status)}
                      <span className="ml-2">{getStatusText(report.status)}</span>
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-col">
                      <span className="text-sm font-bold text-slate-800">{report.report_number}</span>
                      <span className="text-sm text-slate-600 font-medium">{report.supplier_name}</span>
                      <span className="text-xs text-slate-400 mt-1">{report.subject}</span>
                      {report.related_incident?.code && (
                        <span className="inline-flex items-center mt-1 text-xs font-medium text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded w-fit">
                          Ref: {report.related_incident.code}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm font-medium text-slate-500">
                    {new Date(report.report_date).toLocaleDateString()}
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
              <TruckIcon className="w-16 h-16 mx-auto mb-4 text-slate-200" />
              <p className="text-lg font-medium">No se encontraron reportes</p>
              <p className="text-sm">Intente cambiar el filtro o cree uno nuevo.</p>
            </div>
          )}
        </div>
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
              filename={selectedReport?.report_number ? `Informe_Proveedor_${selectedReport.report_number}.pdf` : 'Informe_Proveedor.pdf'}
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
                <h3 className="text-lg font-medium text-gray-900">Nuevo Informe para Proveedor</h3>
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
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
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
                      createSupplierReportMutation.mutate(selectedIncidentId);
                    }}
                    disabled={createSupplierReportMutation.isPending || !selectedIncidentId}
                    className="px-4 py-2 text-sm font-medium text-white bg-orange-600 hover:bg-orange-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {createSupplierReportMutation.isPending ? 'Creando...' : 'Crear Informe'}
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

export default SupplierReportsList;
