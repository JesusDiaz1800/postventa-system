import React, { useState, useCallback, useMemo, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  DocumentTextIcon,
  DocumentArrowUpIcon,
  PlusIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  PaperClipIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  UserIcon,
  CalendarIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  ArrowPathIcon,
  CloudArrowUpIcon,
  BeakerIcon,
  XMarkIcon,
  PaperAirplaneIcon,
  ArrowTopRightOnSquareIcon,
  BuildingOfficeIcon
} from '@heroicons/react/24/outline';

import { useNotifications } from '../hooks/useNotifications';
import { api, incidentsAPI, qualityReportsAPI } from '../services/api';
import useReportsManager from '../hooks/useReportsManager';
import ReportAttachments from '../components/ReportAttachments';
import DocumentManager from '../components/DocumentManager';
import DocumentViewer from '../components/DocumentViewer';
import IncidentClosureForm from '../components/IncidentClosureForm';
import { openDocument, downloadDocument, generateDocument } from '../utils/documentUtils';

/**
 * Página profesional para gestión de reportes de calidad interna
 * Permite crear, visualizar, escalar y gestionar reportes
 */
const InternalQualityReportsPage = () => {
  const navigate = useNavigate();
  const { showSuccess, showError } = useNotifications();
  const queryClient = useQueryClient();
  const {
    createInternalQualityReport,
    escalateInternalReport,
    escalateToSupplier,
    deleteQualityReport,
    generateReport,
    isGenerating
  } = useReportsManager();

  // Estados
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [sortBy, setSortBy] = useState('date');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showEscalateModal, setShowEscalateModal] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [selectedIncidentId, setSelectedIncidentId] = useState('');
  const [showIncidentClosure, setShowIncidentClosure] = useState(false);
  const [showSupplierEscalateModal, setShowSupplierEscalateModal] = useState(false); // Nuevo estado
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Estado para el modal de cierre estandarizado
  const [closureData, setClosureData] = useState({
    stage: 'calidad',
    reason: '',
    closure_summary: '',
    closure_attachment: null
  });

  // Scroll to top on page mount
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  // Obtener reportes de calidad interna
  const {
    data: reports = [],
    isLoading: reportsLoading,
    error: reportsError,
    refetch: refetchReports
  } = useQuery({
    queryKey: ['internal-quality-reports', { search: searchTerm }],
    queryFn: async () => {
      const response = await api.get('/documents/quality-reports/internal/', {
        params: { search: searchTerm }
      });
      return response.data?.reports || [];
    },
    keepPreviousData: true,
    staleTime: 60000,
    retry: 1
  });

  // Obtener incidencias escaladas a calidad (para reportes internos)
  const {
    data: incidents = [],
    isLoading: incidentsLoading
  } = useQuery({
    queryKey: ['incidents-escalated-quality'],
    queryFn: async () => {
      // Usar endpoint específico para incidencias escaladas a calidad interna
      const response = await api.get('/incidents/escalated/', {
        params: { escalated_to_internal: 'true', without_quality_report: 'true' }
      });
      return response.data?.incidents || [];
    },
  });

  // Estados para el flujo de creación optimizado
  const [showSelectionModal, setShowSelectionModal] = useState(false);

  // Filtrar y ordenar reportes (Búsqueda Server-Side, Ordenamiento Client-Side)
  const filteredReports = useMemo(() => {
    let filtered = Array.isArray(reports) ? reports : [];

    // Filter by status if selected (Client-side is fine for status dropdown)
    if (filterStatus !== 'all') {
      filtered = filtered.filter(report => report.status === filterStatus);
    }

    return filtered.sort((a, b) => {
      if (sortBy === 'date') return new Date(b.created_at) - new Date(a.created_at);
      if (sortBy === 'incident') return (a.incident_code || '').localeCompare(b.incident_code || '');
      return 0;
    });
  }, [reports, filterStatus, sortBy]);


  // --- Handlers ---

  const handleCreateReportClick = () => {
    setShowSelectionModal(true);
  };

  const handleIncidentSelect = (incidentId) => {
    setSelectedIncidentId(incidentId);
    setShowSelectionModal(false);
    navigate(`/quality-report-form/${incidentId}?internal=true`); // Navegación a la nueva página
  };

  const handleCreateReport = async (formData) => {
    try {
      if (!selectedIncidentId) {
        showError('Debes seleccionar una incidencia');
        return;
      }
      await createInternalQualityReport(selectedIncidentId, formData);
      setShowCreateModal(false);
      refetchReports();
    } catch (error) {
      console.error(error);
      // Error handled in hook
    }
  };

  const handleEscalate = async (report) => {
    setSelectedReport(report);
    setShowEscalateModal(true);
  };

  const handleEscalateToSupplierAction = (report) => {
    setSelectedReport(report);
    setShowSupplierEscalateModal(true);
  };

  const handleConfirmEscalation = async () => {
    if (!selectedReport) return;
    try {
      await escalateInternalReport(selectedReport.id, "Escalado a cliente");
      setShowEscalateModal(false);
      refetchReports();
    } catch (error) {
      console.error(error);
    }
  };

  const handleConfirmSupplierEscalation = async () => {
    if (!selectedReport) return;
    try {
      // Use mutateAsync from the hook object
      await escalateToSupplier.mutateAsync({
        reportId: selectedReport.id,
        escalationData: {
          supplier_name: selectedReport.incident?.provider || 'Proveedor',
          supplier_email: 'contacto@proveedor.com',
          subject: `Escalamiento de Incidencia ${selectedReport.incident_code || ''}`,
          message: 'Se ha escalado esta incidencia para su revisión.',
          reason: 'Escalado a proveedor desde interno'
        }
      });
      setShowSupplierEscalateModal(false);
      refetchReports();
    } catch (error) {
      console.error(error);
    }
  };

  const handleDelete = async (reportId) => {
    if (confirm('¿Estás seguro de eliminar este reporte?')) {
      try {
        await deleteQualityReport.mutateAsync(reportId);
        refetchReports();
      } catch (error) {
        console.error(error);
      }
    }
  };

  const handleUploadDocument = async () => {
    if (!selectedIncidentId) {
      showError('Por favor selecciona una incidencia primero.');
      return;
    }

    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.pdf,.doc,.docx';
    fileInput.onchange = async (e) => {
      const file = e.target.files[0];
      if (!file) return;

      setIsSubmitting(true);
      const formData = new FormData();
      formData.append('file', file);
      formData.append('incident_id', selectedIncidentId);
      formData.append('report_type', 'interno'); // Important for backend distinction

      try {
        await api.post('/documents/upload/quality-report/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        showSuccess('Documento subido exitosamente');
        setShowUploadModal(false);
        refetchReports();
      } catch (error) {
        console.error(error);
        showError('Error al subir documento');
      } finally {
        setIsSubmitting(false);
      }
    };
    fileInput.click();
  };

  const handleOpenDocumentWrapper = (report) => {
    // Check if report has a download URL (preferred) or legacy path
    const baseUrl = api.defaults.baseURL.replace('/api', '');

    if (report.download_url) {
      // Use the proper download URL provided by backend
      const url = `${baseUrl}${report.download_url}`;
      window.open(url, '_blank');
      return;
    }

    // Fallback for legacy paths
    if (report.pdf_path) {
      const url = report.pdf_path.startsWith('http') ? report.pdf_path : `${baseUrl}${report.pdf_path}`;
      window.open(url, '_blank');
    } else {
      showError("No hay documento PDF disponible.");
    }
  };


  return (
    <div className="scroll-container-sticky">
      <div className="scroll-content-wrapper">
        <div className="w-full px-4 sm:px-6 lg:px-8 space-y-6 py-8">

          {/* Compact Professional Header Section */}
          <div className="relative mb-6 p-4 rounded-2xl bg-gradient-to-br from-slate-50 to-white border border-slate-200 shadow-sm overflow-hidden group flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-purple-500/5 to-indigo-500/5 rounded-full blur-3xl -mr-16 -mt-16 pointer-events-none"></div>

            <div className="flex items-center gap-4 relative z-10">
              <div className="p-2.5 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-xl shadow-md shadow-purple-500/20 group-hover:scale-105 transition-transform duration-500">
                <BeakerIcon className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-800 tracking-tight flex items-center gap-2">
                  Reportes Internos
                  <span className="px-2 py-0.5 rounded-full bg-purple-50 text-purple-700 text-[10px] font-bold uppercase tracking-wider border border-purple-100">
                    Gestión Técnica
                  </span>
                </h1>
                <p className="text-xs text-slate-500 font-medium mt-0.5">
                  Documentación y análisis interno de calidad
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3 relative z-10">
              <button
                onClick={() => setShowUploadModal(true)}
                className="px-6 py-4 bg-white hover:bg-slate-50 text-slate-600 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all flex items-center gap-3 border border-slate-200 shadow-sm"
              >
                <DocumentArrowUpIcon className="h-5 w-5 text-indigo-500" />
                ADJUNTAR
              </button>
              <button
                onClick={handleCreateReportClick}
                className="px-8 py-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-2xl text-[10px] font-black uppercase tracking-widest shadow-xl shadow-indigo-200 transition-all flex items-center gap-3"
              >
                <PlusIcon className="h-5 w-5 text-indigo-200" />
                NUEVO REPORTE
              </button>
            </div>
          </div>

          {/* Filters & Search - Glassmorphism */}
          <div className="bg-white/40 backdrop-blur-md rounded-2xl p-1.5 mb-8 shadow-sm border border-white/50">
            <div className="flex flex-col md:flex-row gap-4 p-2 justify-between items-center">
              <div className="flex-1 relative w-full md:max-w-xl group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <MagnifyingGlassIcon className="h-5 w-5 text-gray-400 group-focus-within:text-blue-600 transition-colors" />
                </div>
                <input
                  type="text"
                  className="block w-full pl-10 pr-3 py-2.5 bg-white/60 backdrop-blur-sm border-transparent text-gray-900 placeholder-gray-500 focus:outline-none focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-transparent rounded-xl transition-all duration-200 shadow-sm font-medium"
                  placeholder="Buscar reporte..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <div className="flex items-center gap-3 w-full md:w-auto">
                <div className="relative">
                  <select
                    value={filterStatus}
                    onChange={(e) => setFilterStatus(e.target.value)}
                    className="appearance-none block w-full pl-3 pr-10 py-2.5 bg-white/60 backdrop-blur-sm border-transparent text-gray-900 focus:outline-none focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-transparent rounded-xl transition-all duration-200 shadow-sm font-medium cursor-pointer"
                  >
                    <option value="all">Todos los estados</option>
                    <option value="draft">Borrador</option>
                    <option value="final">Finalizado</option>
                  </select>
                  <FunnelIcon className="h-5 w-5 text-gray-400 absolute right-3 top-2.5 pointer-events-none" />
                </div>

                <div className="relative">
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="appearance-none block w-full pl-3 pr-10 py-2.5 bg-white/60 backdrop-blur-sm border-transparent text-gray-900 focus:outline-none focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-transparent rounded-xl transition-all duration-200 shadow-sm font-medium cursor-pointer"
                  >
                    <option value="date">Más recientes</option>
                    <option value="incident">Por Incidencia</option>
                  </select>
                  <CalendarIcon className="h-5 w-5 text-gray-400 absolute right-3 top-2.5 pointer-events-none" />
                </div>
              </div>
            </div>
          </div>

          {/* Reports Table - Modern Glass */}
          <div className="bg-white/60 backdrop-blur-2xl rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-white/60 overflow-hidden">
            <div className="overflow-x-visible scroll-horizontal-sticky min-h-[400px]">
              <table className="min-w-full">
                <thead>
                  <tr className="bg-slate-50/50 border-b border-slate-200">
                    <th className="px-6 py-4 text-[11px] font-black text-slate-400 uppercase tracking-widest w-64">Reporte</th>
                    <th className="px-6 py-4 text-[11px] font-black text-slate-400 uppercase tracking-widest">Incidencia</th>
                    <th className="px-6 py-4 text-[11px] font-black text-slate-400 uppercase tracking-widest">Cliente / Obra</th>
                    <th className="px-6 py-4 text-[11px] font-black text-slate-400 uppercase tracking-widest text-center">Estado</th>
                    <th className="px-6 py-4 text-[11px] font-black text-slate-400 uppercase tracking-widest">Fecha</th>
                    <th className="px-6 py-4 text-[11px] font-black text-slate-400 uppercase tracking-widest text-right">Gestión</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100/50">
                  {filteredReports.map((report) => (
                    <tr key={report.id} className="group hover:bg-white/60 transition-colors duration-150">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-9 w-9 bg-indigo-50 rounded-lg flex items-center justify-center text-indigo-600 mr-3 shadow-sm border border-indigo-100">
                            <DocumentTextIcon className="h-5 w-5" />
                          </div>
                          <div className="min-w-0">
                            <div className="text-sm font-bold text-gray-900 bg-clip-text bg-gradient-to-r from-gray-900 to-gray-700 truncate max-w-[180px]" title={report.title}>{report.title}</div>
                            <div className="text-xs text-gray-500">ID: {report.id}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2.5 py-1 text-xs font-bold text-gray-600 bg-gray-100/80 rounded-lg border border-gray-200 backdrop-blur-sm">
                          {report.incident_code || '-'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex flex-col">
                          <span className="text-sm font-bold text-gray-900">{report.incident?.cliente || report.cliente || 'Sin Cliente'}</span>
                          <span className="text-xs text-gray-500 flex items-center mt-0.5">
                            <BuildingOfficeIcon className="h-3 w-3 mr-1" />
                            {report.incident?.obra || report.obra || 'Sin Obra'}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-center whitespace-nowrap">
                        <span className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-black uppercase tracking-tight border ${report.incident?.estado === 'cerrado' || report.status === 'final' || report.status === 'closed'
                          ? 'bg-slate-100 text-slate-600 border-slate-200'
                          : report.status === 'escalated'
                            ? 'bg-purple-50 text-purple-700 border-purple-100'
                            : 'bg-emerald-50 text-emerald-700 border-emerald-100'
                          }`}>
                          {report.incident?.estado === 'cerrado' || report.status === 'final' || report.status === 'closed' ? <CheckCircleIcon className="w-3.5 h-3.5 mr-1.5" /> :
                            report.status === 'escalated' ? <ArrowTopRightOnSquareIcon className="w-3.5 h-3.5 mr-1.5" /> :
                              <ClockIcon className="w-3.5 h-3.5 mr-1.5" />}
                          {report.incident?.estado === 'cerrado' || report.status === 'final' || report.status === 'closed' ? 'CERRADO' :
                            report.status === 'escalated' ? 'ESCALADO' :
                              'LISTO'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500 font-bold">
                        {new Date(report.created_at).toLocaleDateString('es-CL')}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center justify-end gap-3">
                          <button
                            onClick={() => handleOpenDocumentWrapper(report)}
                            className="w-12 h-12 flex items-center justify-center rounded-2xl bg-blue-50 text-blue-600 hover:bg-blue-600 hover:text-white transition-all shadow-sm"
                            title="Explorar Documento"
                          >
                            <EyeIcon className="w-6 h-6" />
                          </button>

                          {report.incident?.estado !== 'cerrado' && (
                            <button
                              onClick={() => handleEscalate(report)}
                              className="w-12 h-12 flex items-center justify-center rounded-2xl bg-purple-50 text-purple-600 hover:bg-purple-600 hover:text-white transition-all shadow-sm"
                              title="Escalar a Cliente"
                            >
                              <ArrowTopRightOnSquareIcon className="w-6 h-6" />
                            </button>
                          )}

                          {report.incident?.estado !== 'cerrado' && (
                            <button
                              onClick={() => handleEscalateToSupplierAction(report)}
                              className="w-12 h-12 flex items-center justify-center rounded-2xl bg-orange-50 text-orange-600 hover:bg-orange-600 hover:text-white transition-all shadow-sm"
                              title="Escalar a Proveedor"
                            >
                              <PaperAirplaneIcon className="w-6 h-6" />
                            </button>
                          )}

                          {report.incident?.estado !== 'cerrado' && (
                            <button
                              onClick={() => {
                                setSelectedReport(report);
                                setClosureData({ stage: 'calidad', reason: '', closure_summary: '', closure_attachment: null });
                                setShowIncidentClosure(true);
                              }}
                              className="w-12 h-12 flex items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600 hover:bg-emerald-600 hover:text-white transition-all shadow-sm"
                              title="Cerrar Incidencia"
                            >
                              <CheckCircleIcon className="w-6 h-6" />
                            </button>
                          )}

                          <button
                            onClick={() => handleDelete(report.id)}
                            className="w-12 h-12 flex items-center justify-center rounded-2xl bg-rose-50 text-rose-500 hover:bg-rose-500 hover:text-white transition-all shadow-sm"
                            title="Eliminar Registro"
                          >
                            <TrashIcon className="w-6 h-6" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {filteredReports.length === 0 && (
                    <tr>
                      <td colSpan="6" className="px-6 py-20 text-center text-gray-500">
                        <div className="flex flex-col items-center justify-center">
                          <div className="bg-gray-50/50 backdrop-blur-sm p-6 rounded-full mb-4">
                            <DocumentTextIcon className="h-10 w-10 text-gray-300" />
                          </div>
                          <p className="text-lg font-medium text-gray-600">No hay reportes internos</p>
                          <p className="text-sm">Crea uno nuevo para comenzar</p>
                        </div>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      </div>

      {/* MODAL 1: SELECCIONAR INCIDENCIA */}
      {
        showSelectionModal && (
          <div className="fixed inset-0 bg-gray-900/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full border border-white/20 p-6">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-bold text-gray-900">Seleccionar Incidencia</h3>
                <button onClick={() => setShowSelectionModal(false)} className="text-gray-400 hover:text-gray-600">
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>

              <div className="space-y-4">
                <div className="bg-blue-50 p-4 rounded-xl mb-4">
                  <p className="text-sm text-blue-800 font-medium flex items-center">
                    <ExclamationTriangleIcon className="h-5 w-5 mr-2" />
                    Solo se muestran incidencias escaladas a calidad.
                  </p>
                </div>

                {incidents.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="bg-orange-50 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                      <ExclamationTriangleIcon className="h-8 w-8 text-orange-400" />
                    </div>
                    <h3 className="text-lg font-medium text-gray-900">No hay incidencias escaladas disponibles</h3>
                    <p className="text-gray-500 mt-2">
                      No se encontraron incidencias escaladas desde reportes de calidad a clientes.
                    </p>
                    <button
                      onClick={() => setShowSelectionModal(false)}
                      className="mt-6 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50"
                    >
                      Cerrar
                    </button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {incidents.map((incident) => (
                      <div
                        key={incident.id}
                        onClick={() => handleIncidentSelect(incident.id)}
                        className="p-4 border border-gray-200 rounded-xl hover:border-blue-500 hover:bg-blue-50 cursor-pointer transition-all group"
                      >
                        <div className="flex justify-between items-start mb-2">
                          <span className="font-bold text-gray-900 bg-white px-2 py-0.5 rounded border border-gray-200 group-hover:border-blue-200 trantision-colors">
                            {incident.code}
                          </span>
                          <span className="text-xs text-gray-500 flex items-center bg-gray-100 px-2 py-0.5 rounded-full">
                            <CalendarIcon className="h-3 w-3 mr-1" />
                            {new Date(incident.created_at).toLocaleDateString()}
                          </span>
                        </div>
                        <div className="mb-2">
                          <h4 className="font-semibold text-gray-800 mb-1">{incident.cliente}</h4>
                          <p className="text-sm text-gray-600 line-clamp-2">{incident.description}</p>
                        </div>
                        <div className="flex items-center gap-2 mt-3 pt-3 border-t border-gray-100">
                          <span className="px-2 py-0.5 text-xs rounded bg-blue-100 text-blue-700 font-medium">
                            {incident.obra || 'Sin obra'}
                          </span>
                          <span className="px-2 py-0.5 text-xs rounded bg-amber-100 text-amber-700 font-medium ml-auto">
                            Escalado de Calidad
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )
      }

      {/* MODAL 2: FORMULARIO FULL SCREEN */}
      {/* El formulario ahora es una página independiente */}

      {/* Upload Modal (Added for completeness) */}
      {
        showUploadModal && (
          <div className="fixed inset-0 bg-gray-900/60 backdrop-blur-sm overflow-y-auto h-full w-full z-50 flex items-center justify-center">
            <div className="bg-white/90 backdrop-blur-xl rounded-3xl p-8 max-w-md w-full shadow-2xl border border-white/50">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Adjuntar Documento Interno</h3>

              <div className="mb-4">
                <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">
                  Seleccionar Incidencia
                </label>
                <div className="relative">
                  <select
                    value={selectedIncidentId}
                    onChange={(e) => setSelectedIncidentId(e.target.value)}
                    className="w-full pl-4 pr-10 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 appearance-none font-medium text-gray-700"
                  >
                    <option value="">Seleccionar...</option>
                    {(Array.isArray(incidents) ? incidents : (incidents?.results || []))
                      .map(incident => (
                        <option key={incident.id} value={incident.id}>
                          {incident.code} - {incident.title || incident.cliente}
                        </option>
                      ))}
                  </select>
                  <div className="absolute inset-y-0 right-0 flex items-center px-3 pointer-events-none text-gray-500">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
                  </div>
                </div>
              </div>

              <p className="text-sm text-gray-500 mb-6">Selecciona el archivo PDF/DOC del reporte firmado o documento técnico.</p>

              <div className={`border-2 border-dashed border-gray-300 rounded-2xl p-8 text-center transition-all cursor-pointer group ${!selectedIncidentId ? 'opacity-50 cursor-not-allowed' : 'hover:bg-white/50 hover:border-indigo-400'}`}
                onClick={() => selectedIncidentId && handleUploadDocument()}
              >
                <CloudArrowUpIcon className="h-12 w-12 text-gray-400 group-hover:text-indigo-500 transition-colors mx-auto mb-3" />
                <span className="text-sm font-bold text-indigo-600">Click para seleccionar archivo</span>
              </div>

              <button
                onClick={() => setShowUploadModal(false)}
                className="mt-6 w-full py-3 bg-gray-100 text-gray-700 font-bold rounded-xl hover:bg-gray-200 transition-colors"
              >
                Cancelar
              </button>
            </div>
          </div>
        )
      }

      {/* Escalate Modal */}
      {
        showEscalateModal && (
          <div className="fixed inset-0 bg-gray-900/60 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="bg-white rounded-2xl p-6 max-w-sm w-full shadow-2xl border border-white/20">
              <h3 className="text-xl font-bold text-gray-900 mb-2">Confirmar Escalado</h3>
              <p className="text-gray-500 mb-6 text-sm">¿Deseas escalar este reporte para revisión de cliente?</p>
              <div className="flex justify-end gap-3">
                <button
                  onClick={() => setShowEscalateModal(false)}
                  className="px-4 py-2 text-gray-600 font-bold bg-gray-100 hover:bg-gray-200 rounded-xl transition-colors"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleConfirmEscalation}
                  className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white font-bold rounded-xl shadow-lg shadow-purple-500/30 transition-all"
                >
                  Confirmar
                </button>
              </div>
            </div>
          </div>
        )
      }

      {/* Supplier Escalate Modal */}
      {
        showSupplierEscalateModal && (
          <div className="fixed inset-0 bg-gray-900/60 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="bg-white rounded-2xl p-6 max-w-sm w-full shadow-2xl border border-white/20">
              <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center mb-4 text-orange-600">
                <PaperAirplaneIcon className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Escalar a Proveedor</h3>
              <p className="text-gray-500 mb-6 text-sm">Se notificará al equipo de proveedores y se cambiará el estado.</p>
              <div className="flex justify-end gap-3">
                <button
                  onClick={() => setShowSupplierEscalateModal(false)}
                  className="px-4 py-2 text-gray-600 font-bold bg-gray-100 hover:bg-gray-200 rounded-xl transition-colors"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleConfirmSupplierEscalation}
                  className="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white font-bold rounded-xl shadow-lg shadow-orange-500/30 transition-all"
                >
                  Escalar
                </button>
              </div>
            </div>
          </div>
        )
      }

      {/* Close Incident Modal */}
      {
        showIncidentClosure && selectedReport && (
          <div className="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
            <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
              <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" onClick={() => setShowIncidentClosure(false)}></div>

              <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

              <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
                <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                  <div className="sm:flex sm:items-start">
                    <div className="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-green-100 sm:mx-0 sm:h-10 sm:w-10">
                      <CheckCircleIcon className="h-6 w-6 text-green-600" aria-hidden="true" />
                    </div>
                    <div className="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
                      <h3 className="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                        Cerrar Incidencia
                      </h3>
                      <div className="mt-2">
                        <p className="text-sm text-gray-500 mb-4">
                          Cerrando incidencia <b>{selectedReport.incident_code}</b>. Esta acción es definitiva.
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-6">
                    {/* Etapa de Cierre */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Etapa de Cierre <span className="text-red-500">*</span>
                      </label>
                      <select
                        value={closureData.stage}
                        onChange={(e) => setClosureData({ ...closureData, stage: e.target.value })}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors"
                      >
                        <option value="calidad">Cerrada en Calidad</option>
                        <option value="proveedor">Cerrada en Proveedor</option>
                        <option value="reporte_visita">Cerrada en Reporte de Visita</option>
                        <option value="incidencia">Cerrada en Incidencia</option>
                      </select>
                    </div>

                    {/* Motivo de Cierre */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Motivo de Cierre <span className="text-red-500">*</span>
                      </label>
                      <select
                        value={closureData.reason || ''}
                        onChange={(e) => setClosureData({ ...closureData, reason: e.target.value })}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors"
                      >
                        <option value="">-- Seleccionar motivo --</option>
                        <option value="Resuelto satisfactoriamente">Resuelto satisfactoriamente</option>
                        <option value="Sin garantía aplicable">Sin garantía aplicable</option>
                        <option value="Producto reemplazado">Producto reemplazado</option>
                        <option value="Crédito emitido">Crédito emitido</option>
                        <option value="Problema no reproducible">Problema no reproducible</option>
                        <option value="Solicitud del cliente">Solicitud del cliente</option>
                        <option value="Otro">Otro</option>
                      </select>
                    </div>

                    {/* Resumen Obligatorio */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Resumen de Acciones y Conclusiones <span className="text-red-500">*</span>
                      </label>
                      <textarea
                        value={closureData.closure_summary}
                        onChange={(e) => setClosureData({ ...closureData, closure_summary: e.target.value })}
                        rows={5}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors"
                        placeholder="Describa las acciones tomadas y conclusiones (mínimo 10 caracteres)..."
                      />
                      <p className={`mt-1 text-sm ${closureData.closure_summary.length < 10 ? 'text-red-500' : 'text-green-600'}`}>
                        {closureData.closure_summary.length}/10 caracteres mínimos
                      </p>
                    </div>

                    {/* Archivo Adjunto Opcional */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Archivo Adjunto (opcional)
                      </label>
                      <div className="flex items-center space-x-3">
                        <input
                          type="file"
                          id="closure-file-internal"
                          className="hidden"
                          onChange={(e) => setClosureData({ ...closureData, closure_attachment: e.target.files[0] || null })}
                          accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.txt"
                        />
                        <label
                          htmlFor="closure-file-internal"
                          className="px-4 py-2 bg-gray-100 text-gray-700 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-200 transition-colors"
                        >
                          Seleccionar Archivo
                        </label>
                        {closureData.closure_attachment && (
                          <div className="flex items-center space-x-2 text-sm text-gray-600">
                            <PaperClipIcon className="h-4 w-4" />
                            <span className="truncate max-w-[150px]">{closureData.closure_attachment.name}</span>
                            <button
                              type="button"
                              onClick={() => setClosureData({ ...closureData, closure_attachment: null })}
                              className="text-red-500 hover:text-red-700"
                            >
                              <XMarkIcon className="h-4 w-4" />
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                  <button
                    type="button"
                    disabled={isSubmitting || closureData.closure_summary.length < 10 || !closureData.reason}
                    onClick={async () => {
                      if (!closureData.reason) {
                        showError('Por favor selecciona un motivo de cierre');
                        return;
                      }
                      if (closureData.closure_summary.length < 10) {
                        showError('El resumen debe tener al menos 10 caracteres');
                        return;
                      }
                      setIsSubmitting(true);
                      try {
                        const incidentId = selectedReport.incident_id || selectedReport.incident?.id;
                        const finalSummary = `[Motivo: ${closureData.reason}] ${closureData.closure_summary}`;
                        await incidentsAPI.close(incidentId, {
                          stage: closureData.stage,
                          closure_summary: finalSummary
                        });
                        showSuccess('Incidencia cerrada exitosamente');
                        setShowIncidentClosure(false);
                        refetchReports();
                        queryClient.invalidateQueries(['incidents-escalated-quality']);
                      } catch (error) {
                        showError('Error al cerrar: ' + (error.response?.data?.error || error.message));
                      } finally {
                        setIsSubmitting(false);
                      }
                    }}
                    className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-green-600 text-base font-medium text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50"
                  >
                    {isSubmitting ? 'Cerrando...' : 'Confirmar Cierre'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowIncidentClosure(false)}
                    className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
                  >
                    Cancelar
                  </button>
                </div>
              </div>
            </div>
          </div>
        )
      }

    </div >
  );
};

export default InternalQualityReportsPage;