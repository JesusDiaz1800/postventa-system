import React, { useState, useMemo, useEffect } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { api, incidentsAPI, supplierReportsAPI } from '../services/api';
import { normalizeText } from '../utils/stringUtils';
import { exportToExcel } from '../utils/exportUtils';
import {
  PlusIcon,
  DocumentArrowUpIcon,
  EyeIcon,
  TrashIcon,
  XMarkIcon,
  MagnifyingGlassIcon,
  DocumentTextIcon,
  BuildingOfficeIcon,
  ArrowPathIcon,
  EnvelopeIcon,
  PaperClipIcon,
  ArrowDownTrayIcon,
  CheckCircleIcon,
  PaperAirplaneIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const SupplierReportsPage = () => {
  const queryClient = useQueryClient();

  // Estados
  const [showCreateModal, setShowCreateModal] = useState(false); // Used for Selection Modal for Create
  const [showUploadModal, setShowUploadModal] = useState(false); // Used for Upload Modal
  const [showEmailModal, setShowEmailModal] = useState(false);

  const [showIncidentClosure, setShowIncidentClosure] = useState(false);
  const [selectedIncidentForClosure, setSelectedIncidentForClosure] = useState(null);

  // Closure modal states (Simple version)
  const [showCloseModal, setShowCloseModal] = useState(false);
  const [selectedReportForClose, setSelectedReportForClose] = useState(null);
  const [isClosing, setIsClosing] = useState(false);
  const [closureData, setClosureData] = useState({
    stage: 'proveedor',
    reason: '',
    closure_summary: '',
    closure_attachment: null
  });

  const [selectedIncidentId, setSelectedIncidentId] = useState('');
  const [selectedReport, setSelectedReport] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [emailData, setEmailData] = useState({
    to: '',
    subject: '',
    message: ''
  });

  // Scroll to top on page mount
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  // Query para obtener reportes de proveedores
  const { data: reports, isLoading: reportsLoading, refetch } = useQuery({
    queryKey: ['supplier-reports'],
    queryFn: async () => {
      const response = await api.get('/documents/supplier-reports/');
      return response.data;
    }
  });

  // Query para obtener incidencias disponibles (Filtrado para proveedores)
  const { data: openIncidents, isLoading: incidentsLoading } = useQuery({
    queryKey: ['supplier-incidents'],
    queryFn: async () => {
      // Fetch open incidents and filter client-side for flexibility or use specific endpoint
      const response = await api.get('/incidents/', {
        params: { estado: 'proveedor', page_size: 100 }
      });
      const allIncidents = response.data?.results || response.data || [];

      // Filter ONLY escalated to supplier (estado proveedor = en etapa proveedor)
      const escalatedIncidents = allIncidents.filter(i => i.escalated_to_supplier || i.estado === 'proveedor');

      // IMPORTANTE: Filtrar incidencias que YA tienen reporte de proveedor
      const incidentsWithReports = reports?.results?.map(r =>
        r.incident_id || r.incident?.id || r.related_incident?.id
      ).filter(Boolean) || [];

      return escalatedIncidents.filter(incident =>
        !incidentsWithReports.includes(incident.id)
      );
    },
    enabled: !!reports?.results, // Solo ejecutar cuando reports esté disponible
  });

  // Filtrar reportes
  const filteredReports = useMemo(() => {
    if (!reports?.results) return [];
    return reports.results.filter(report => {
      const normalizedSearch = normalizeText(searchTerm);
      if (!normalizedSearch) return true;

      const reportNumber = normalizeText(report.report_number || '');
      const incidentCode = normalizeText(report.related_incident?.code || report.incident_code || '');
      const supplierName = normalizeText(report.supplier_name || '');

      const matchesSearch = reportNumber.includes(normalizedSearch) ||
        incidentCode.includes(normalizedSearch) ||
        supplierName.includes(normalizedSearch);
      const matchesStatus = !statusFilter || report.status === statusFilter;
      return matchesSearch && matchesStatus;
    });
  }, [reports?.results, searchTerm, statusFilter]);

  // Handlers
  const handleCreateReportClick = () => {
    setShowCreateModal(true); // Abre modal de selección
  };

  const handleIncidentSelectForCreate = (incidentId) => {
    window.open(`/supplier-report-form?incident_id=${incidentId}`, '_blank');
    setShowCreateModal(false);
  };

  const handleUploadDocument = async () => {
    // Only proceed if incident selected, otherwise Open Upload Modal
    if (!selectedIncidentId) {
      setShowUploadModal(true);
      return;
    }

    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.pdf,.doc,.docx,.xls,.xlsx';
    input.onchange = async (e) => {
      const file = e.target.files[0];
      if (!file) return;

      setIsSubmitting(true);
      try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('incident_id', selectedIncidentId);
        formData.append('report_type', 'proveedor');

        await api.post('/documents/upload/supplier-report/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });

        setShowUploadModal(false);
        setSelectedIncidentId('');
        queryClient.invalidateQueries(['supplier-reports']);
        toast.success('Documento adjuntado exitosamente');
      } catch (error) {
        toast.error('Error al subir el documento');
      } finally {
        setIsSubmitting(false);
      }
    };
    input.click();
  };

  const handleViewReport = async (report) => {
    try {
      const { API_ORIGIN } = await import('../services/api');
      window.open(`${API_ORIGIN}/api/documents/supplier-reports/${report.id}/download/`, '_blank');
    } catch (error) {
      toast.error('Error al abrir el documento');
    }
  };

  const handleDeleteReport = async (reportId) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este reporte?')) {
      try {
        await api.delete(`/documents/supplier-reports/${reportId}/`);
        queryClient.invalidateQueries(['supplier-reports']);
        toast.success('Reporte eliminado exitosamente');
      } catch (error) {
        toast.error('Error al eliminar el reporte');
      }
    }
  };

  // Helper function for secure download
  const handleDownloadReport = async (reportId, filename) => {
    try {
      const response = await api.get(`/documents/supplier-reports/${reportId}/download/`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename || `Reporte_Proveedor_${reportId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      return true;
    } catch (error) {
      console.error('Error downloading report:', error);
      toast.error('No se pudo descargar el reporte automáticamente. Por favor inténtelo desde la tabla.');
      return false;
    }
  };

  const handleOpenEmailModal = (report) => {
    setSelectedReport(report);
    // Solo necesitamos el correo del proveedor para el modal simplificado
    setEmailData({
      to: report.supplier_email || '',
      // Mantenemos subject y message para armar el mailto, pero NO se muestran en el modal
      subject: `[IMPORTANTE] Reporte de Calidad - Proyecto ${report.obra || report.incident?.obra || 'Sin Nombre'} - Incidencia ${report.incident_code || report.incident?.code}`,
      message: `Estimado Proveedor ${report.supplier_name || ''},

Esperando que se encuentre muy bien.

Le informamos que se ha generado un nuevo Reporte de No Conformidad (N° ${report.report_number}) asociado a la obra ${report.obra || report.incident?.obra || 'Sin Nombre'}.

Adjunto a este correo encontrará el reporte detallado con las observaciones y evidencias correspondientes.

Solicitamos su gestión para:
1. Revisar los antecedentes adjuntos.
2. Generar el análisis de causa raíz.
3. Proponer acciones correctivas.
4. Confirmar plazos de solución.

Quedamos a la espera de su respuesta dentro de las próximas 48 horas.

Atentamente,

Departamento de Control de Calidad
POLIFUSION S.A.`
    });
    setShowEmailModal(true);
  };

  const handleSendEmail = async () => {
    // Validación básica
    if (!emailData.to) {
      toast.error('Por favor ingresa el correo del proveedor');
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(emailData.to)) {
      toast.error('Por favor ingresa un correo electrónico válido');
      return;
    }

    setIsSubmitting(true);
    try {
      toast.loading('Preparando envío...', { id: 'email-toast' });

      // 1. Iniciar Descarga Segura (Autenticada)
      const downloadSuccess = await handleDownloadReport(selectedReport.id, `Reporte_${selectedReport.report_number}.pdf`);
      if (!downloadSuccess) {
        toast.dismiss('email-toast');
        setIsSubmitting(false);
        return;
      }

      // 2. Preparar Mailto para Outlook
      const mailtoLink = `mailto:${emailData.to}?subject=${encodeURIComponent(emailData.subject)}&body=${encodeURIComponent(emailData.message)}`;

      // Abrir cliente de correo
      setTimeout(() => {
        window.location.href = mailtoLink;
      }, 800);

      // 3. Registrar en Backend (Log Only)
      await api.post(`/documents/supplier-reports/${selectedReport.id}/send-email/`, {
        to: emailData.to,
        action: 'log_only'
      });

      toast.success('Abriendo Outlook... Por favor ADJUNTA el reporte descargado.', {
        id: 'email-toast',
        duration: 8000,
        icon: '📎'
      });

      setShowEmailModal(false);
      queryClient.invalidateQueries(['supplier-reports']);

    } catch (error) {
      console.error('Error in email flow:', error);
      toast.error('Se abrió el correo pero falló el registro en el sistema.', { id: 'email-toast' });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Open closure modal (simplified version)
  const openClosureModal = (incident) => {
    setSelectedIncidentForClosure(incident);
    setClosureData({
      stage: 'proveedor',
      reason: '',
      closure_summary: '',
      closure_attachment: null
    });
    setShowCloseModal(true);
  };

  const handleClosureSubmit = async () => {
    if (!selectedIncidentForClosure) return;

    // Validar que la incidencia no esté ya cerrada
    if (selectedIncidentForClosure.estado === 'cerrado' || selectedIncidentForClosure.estado === 'closed') {
      toast.error('Esta incidencia ya está cerrada');
      setShowCloseModal(false);
      return;
    }

    if (!closureData.reason) {
      toast.error('Por favor selecciona un motivo de cierre');
      return;
    }

    if (closureData.closure_summary.length < 10) {
      toast.error('El resumen debe tener al menos 10 caracteres');
      return;
    }

    setIsClosing(true);
    try {
      const incidentId = selectedIncidentForClosure.id;
      const finalSummary = `[Motivo: ${closureData.reason}] ${closureData.closure_summary}`;

      // 1. Si hay archivo adjunto, subirlo como "Respuesta del Proveedor"
      if (closureData.closure_attachment) {
        try {
          console.log('📎 Iniciando subida de archivo:', closureData.closure_attachment.name);
          const formData = new FormData();
          formData.append('file', closureData.closure_attachment);
          formData.append('incident_id', incidentId);
          formData.append('document_type', 'supplier_response');
          formData.append('description', 'Respuesta del Proveedor - Cierre de Incidencia');

          const uploadResponse = await api.post('/documents/upload-attachment/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          });

          console.log('✅ Archivo subido exitosamente:', uploadResponse.data);
          toast.success(`Archivo "${closureData.closure_attachment.name}" adjuntado correctamente`);
        } catch (uploadError) {
          console.error('❌ Error al subir archivo adjunto:', uploadError);
          console.error('Detalles del error:', uploadError.response?.data);
          toast.error('La incidencia se cerrará, pero hubo un error al adjuntar el archivo.');
        }
      }

      // 2. Cerrar la incidencia
      await incidentsAPI.close(incidentId, {
        stage: closureData.stage,
        closure_summary: finalSummary
      });

      // 3. Actualizar estado del reporte de proveedor relacionado
      console.log('Buscando reporte relacionado para incidencia:', incidentId);
      console.log('Reportes disponibles:', reports?.results);

      // Buscar de manera más exhaustiva
      let relatedReport = null;
      if (reports?.results) {
        relatedReport = reports.results.find(r => {
          const matches = (
            r.incident_id === incidentId ||
            r.incident?.id === incidentId ||
            r.related_incident?.id === incidentId ||
            r.related_incident === incidentId
          );
          console.log(`Comparando reporte ${r.id}:`, {
            incident_id: r.incident_id,
            'incident?.id': r.incident?.id,
            'related_incident?.id': r.related_incident?.id,
            'related_incident': r.related_incident,
            'matches': matches
          });
          return matches;
        });
      }

      console.log('Reporte encontrado:', relatedReport);

      if (relatedReport) {
        try {
          console.log(`Actualizando estado del reporte ${relatedReport.id} a cerrado`);
          await api.patch(`/documents/supplier-reports/${relatedReport.id}/`, {
            status: 'closed'  // IMPORTANTE: 'closed' no 'cerrado'
          });
          console.log('Estado actualizado exitosamente');
        } catch (statusError) {
          console.error('Error al actualizar el estado del reporte:', statusError);
          toast.error('No se pudo actualizar el estado del reporte');
        }
      } else {
        console.warn('No se encontró reporte relacionado con la incidencia', incidentId);
        toast.warning('Incidencia cerrada, pero no se encontró el reporte asociado para actualizar');
      }

      toast.success('Incidencia cerrada y reporte actualizado exitosamente');
      setShowCloseModal(false);
      setSelectedIncidentForClosure(null);
      setClosureData({ stage: 'proveedor', reason: '', closure_summary: '', closure_attachment: null });

      // Forzar actualización de datos
      await queryClient.invalidateQueries(['supplier-reports']);
      await queryClient.invalidateQueries(['supplier-incidents']);
      await queryClient.invalidateQueries(['incident-documents', incidentId]); // IMPORTANTE: Para refrescar documentos

      // Pequeño delay para asegurar que el backend procesó el cambio
      setTimeout(() => {
        refetch(); // Refrescar la lista de reportes
      }, 500);
    } catch (error) {
      console.error('Error al cerrar incidencia:', error);
      toast.error('Error al cerrar: ' + (error.response?.data?.error || error.message));
    } finally {
      setIsClosing(false);
    }
  };


  if (reportsLoading || incidentsLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600"></div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <div className="flex-1 overflow-auto">
        <div className="w-full px-4 sm:px-6 lg:px-8 space-y-6 py-8">

          {/* Header */}
          <div className="mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-gray-900 to-gray-600 tracking-tight">Reportes a Proveedores</h1>
              <p className="mt-1 text-sm text-gray-500 font-medium">
                Gestión de reclamos y calidad con proveedores externos
              </p>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => exportToExcel(
                  filteredReports,
                  [
                    { key: 'report_number', label: 'Número Reporte' },
                    { key: 'incident_code', label: 'Incidencia' },
                    { key: 'supplier_name', label: 'Proveedor' },
                    { key: 'status', label: 'Estado' },
                    { key: 'created_at', label: 'Fecha Creación' }
                  ],
                  'reportes_proveedores'
                )}
                className="px-6 py-4 bg-white/60 hover:bg-white text-slate-700 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all flex items-center gap-3 backdrop-blur-md border border-white/40 shadow-sm"
              >
                <ArrowDownTrayIcon className="h-5 w-5 text-emerald-600" />
                EXCEL
              </button>
              <button
                onClick={() => setShowUploadModal(true)}
                className="px-6 py-4 bg-white/60 hover:bg-white text-slate-700 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all flex items-center gap-3 backdrop-blur-md border border-white/40 shadow-sm"
              >
                <DocumentArrowUpIcon className="h-5 w-5 text-teal-600" />
                ADJUNTAR
              </button>
              <button
                onClick={() => setShowCreateModal(true)}
                className="px-8 py-4 bg-gradient-to-r from-teal-600 to-emerald-600 text-white rounded-2xl text-[10px] font-black uppercase tracking-widest shadow-lg shadow-teal-500/30 hover:shadow-teal-500/40 transition-all flex items-center gap-3"
              >
                <PlusIcon className="h-5 w-5 text-teal-100" />
                NUEVO REPORTE
              </button>
            </div>
          </div>

          {/* Filters - Glassmorphism */}
          <div className="bg-white/40 backdrop-blur-md rounded-2xl p-1.5 mb-8 shadow-sm border border-white/50">
            <div className="flex flex-col md:flex-row gap-4 p-2 justify-between items-center">
              <div className="flex-1 relative w-full md:max-w-xl group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <MagnifyingGlassIcon className="h-5 w-5 text-gray-400 group-focus-within:text-teal-600 transition-colors" />
                </div>
                <input
                  type="text"
                  className="block w-full pl-10 pr-3 py-2.5 bg-white/60 backdrop-blur-sm border-transparent text-gray-900 placeholder-gray-500 focus:outline-none focus:bg-white focus:ring-2 focus:ring-teal-500/20 focus:border-transparent rounded-xl transition-all duration-200 shadow-sm font-medium"
                  placeholder="Buscar por número, código o proveedor..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <div className="w-full md:w-56">
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="block w-full pl-3 pr-10 py-2.5 bg-white/60 backdrop-blur-sm border-transparent text-gray-900 focus:outline-none focus:bg-white focus:ring-2 focus:ring-teal-500/20 focus:border-transparent rounded-xl transition-all duration-200 shadow-sm font-medium cursor-pointer"
                >
                  <option value="">Todos los estados</option>
                  <option value="pendiente">Pendiente</option>
                  <option value="enviado">Enviado</option>
                  <option value="responded">Respondido</option>
                  <option value="cerrado">Cerrado</option>
                </select>
              </div>
              <button
                onClick={() => refetch()}
                className="p-2.5 bg-white/60 backdrop-blur-sm border border-white/40 text-gray-500 hover:text-teal-600 rounded-xl hover:bg-white transition-all shadow-sm"
                title="Actualizar"
              >
                <ArrowPathIcon className="h-5 w-5" />
              </button>
            </div>
          </div>

          {/* Table - Modern Glass */}
          <div className="bg-white/60 backdrop-blur-2xl rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-white/60 overflow-hidden">
            {filteredReports.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-20 px-4 text-center">
                <div className="bg-teal-50/50 backdrop-blur-sm p-6 rounded-full mb-4">
                  <BuildingOfficeIcon className="h-10 w-10 text-teal-300" />
                </div>
                <h3 className="text-lg font-bold text-gray-800">No hay reportes</h3>
                <p className="text-gray-500 mt-1 text-sm">No se encontraron registros de proveedores.</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr className="bg-slate-50/50 border-b border-slate-200">
                      <th className="px-6 py-4 text-[11px] font-black text-slate-400 uppercase tracking-widest">Reporte</th>
                      <th className="px-6 py-4 text-[11px] font-black text-slate-400 uppercase tracking-widest">Incidencia</th>
                      <th className="px-6 py-4 text-[11px] font-black text-slate-400 uppercase tracking-widest">Proveedor</th>
                      <th className="px-6 py-4 text-[11px] font-black text-slate-400 uppercase tracking-widest">Fecha</th>
                      <th className="px-6 py-4 text-[11px] font-black text-slate-400 uppercase tracking-widest text-center">Estado</th>
                      <th className="px-6 py-4 text-[11px] font-black text-slate-400 uppercase tracking-widest text-right">Gestión</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100/50">
                    {filteredReports.map((report) => (
                      <tr key={report.id} className="group hover:bg-white/60 transition-colors duration-150">
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            <div className="p-2 bg-teal-50 rounded-lg shadow-sm border border-teal-100">
                              <DocumentTextIcon className="h-5 w-5 text-teal-600" />
                            </div>
                            <div>
                              <p className="text-sm font-bold text-gray-900">{report.report_number || `Reporte #${report.id}`}</p>
                              <p className="text-xs text-gray-500">{report.title || 'Solicitud de Garantía'}</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <p className="text-sm font-bold text-gray-800">{report.incident_code || report.incident?.code || 'N/A'}</p>
                          <p className="text-xs text-gray-500">{report.categoria || report.incident?.categoria || '-'}</p>
                        </td>
                        <td className="px-6 py-4">
                          <p className="text-sm font-medium text-gray-900">{report.supplier_name || 'Sin proveedor'}</p>
                          <p className="text-xs text-gray-500">{report.supplier_email || '-'}</p>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500 font-medium">
                          {report.created_at ? new Date(report.created_at).toLocaleDateString() : '-'}
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-black uppercase tracking-tight border ${report.status === 'closed' ? 'bg-slate-100 text-slate-600 border-slate-200' :
                            report.status === 'enviado' ? 'bg-blue-50 text-blue-700 border-blue-100' :
                              report.status === 'responded' ? 'bg-purple-50 text-purple-700 border-purple-100' :
                                'bg-emerald-50 text-emerald-700 border-emerald-100' // Default / Pendiente -> Listo
                            }`}>
                            {report.status === 'closed' ? <CheckCircleIcon className="w-3.5 h-3.5 mr-1.5" /> :
                              report.status === 'enviado' ? <PaperAirplaneIcon className="w-3.5 h-3.5 mr-1.5" /> :
                                report.status === 'responded' ? <EnvelopeIcon className="w-3.5 h-3.5 mr-1.5" /> :
                                  <CheckCircleIcon className="w-3.5 h-3.5 mr-1.5" />}
                            {report.status === 'closed' ? 'CERRADO' :
                              report.status === 'enviado' ? 'ENVIADO' :
                                report.status === 'responded' ? 'RESPONDIDO' :
                                  'LISTO'}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <div className="flex items-center justify-end gap-3 opacity-80 group-hover:opacity-100 transition-opacity">
                            <button
                              onClick={() => {
                                if (report.download_url) {
                                  const { API_ORIGIN } = api; // Check import context in real app
                                  // Simplified valid URL handling
                                  const url = report.download_url.startsWith('http') ? report.download_url : `${api.defaults.baseURL.replace('/api', '')}${report.download_url}`;
                                  window.open(url, '_blank');
                                } else {
                                  handleViewReport(report);
                                }
                              }}
                              className="w-12 h-12 flex items-center justify-center rounded-2xl bg-teal-50 text-teal-600 hover:bg-teal-600 hover:text-white transition-all shadow-sm"
                              title="Ver Reporte"
                            >
                              <EyeIcon className="w-6 h-6" />
                            </button>
                            <button
                              onClick={() => handleOpenEmailModal(report)}
                              className="w-12 h-12 flex items-center justify-center rounded-2xl bg-blue-50 text-blue-600 hover:bg-blue-600 hover:text-white transition-all shadow-sm"
                              title="Enviar por Email"
                            >
                              <EnvelopeIcon className="w-6 h-6" />
                            </button>

                            {(report.status !== 'cerrado' && report.incident?.estado !== 'cerrado') && (
                              <button
                                onClick={() => openClosureModal(report.incident || { id: report.incident_id })}
                                className="w-12 h-12 flex items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600 hover:bg-emerald-600 hover:text-white transition-all shadow-sm"
                                title="Cerrar Incidencia"
                              >
                                <CheckCircleIcon className="w-6 h-6" />
                              </button>
                            )}

                            <button
                              onClick={() => handleDeleteReport(report.id)}
                              className="w-12 h-12 flex items-center justify-center rounded-2xl bg-rose-50 text-rose-500 hover:bg-rose-500 hover:text-white transition-all shadow-sm"
                              title="Eliminar"
                            >
                              <TrashIcon className="w-6 h-6" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

        </div>
      </div>

      {/* Modal Crear/Adjuntar - Modern Glass */}
      {(showCreateModal || showUploadModal) && (
        <div className="fixed inset-0 bg-gray-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white/90 backdrop-blur-xl rounded-3xl shadow-2xl w-full max-w-md border border-white/50">
            <div className="px-6 py-5 border-b border-gray-100 flex items-center justify-between">
              <h3 className="text-xl font-bold text-gray-900">
                {showCreateModal ? 'Nuevo Reporte Proveedor' : 'Adjuntar Documento'}
              </h3>
              <button
                onClick={() => { setShowCreateModal(false); setShowUploadModal(false); setSelectedIncidentId(''); }}
                className="text-gray-400 hover:text-gray-600"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>
            <div className="p-8">
              <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">
                Seleccionar Incidencia
              </label>
              <div className="relative">
                <select
                  value={selectedIncidentId}
                  onChange={(e) => setSelectedIncidentId(e.target.value)}
                  className="w-full pl-4 pr-10 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 appearance-none font-medium text-gray-700"
                >
                  <option value="">Seleccionar...</option>
                  {(openIncidents || []).map((incident) => (
                    <option key={incident.id} value={incident.id}>
                      {incident.code} - {incident.cliente || incident.client_name || 'Sin Cliente'} | {incident.obra || incident.project_name || 'Sin Proyecto'}
                    </option>
                  ))}
                </select>
                <div className="absolute inset-y-0 right-0 flex items-center px-3 pointer-events-none text-gray-500">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
                </div>
              </div>

              {showUploadModal && selectedIncidentId && (
                <div
                  onClick={handleUploadDocument}
                  className="mt-6 border-2 border-dashed border-gray-300 rounded-2xl p-6 text-center hover:bg-teal-50/50 hover:border-teal-400 transition-all cursor-pointer group"
                >
                  <DocumentArrowUpIcon className="h-10 w-10 mx-auto mb-2 text-gray-400 group-hover:text-teal-500 transition-colors" />
                  <span className="text-sm font-bold text-teal-600">{isSubmitting ? 'Subiendo...' : 'Click para subir archivo'}</span>
                </div>
              )}
            </div>
            <div className="px-6 py-4 bg-gray-50/50 border-t border-gray-100 flex justify-end gap-3 rounded-b-3xl">
              <button
                onClick={() => { setShowCreateModal(false); setShowUploadModal(false); setSelectedIncidentId(''); }}
                className="px-5 py-2.5 text-gray-600 font-bold hover:bg-gray-100 rounded-xl transition-colors"
              >
                Cancelar
              </button>
              {showCreateModal && (
                <button
                  onClick={() => handleIncidentSelectForCreate(selectedIncidentId)}
                  disabled={!selectedIncidentId}
                  className="px-5 py-2.5 bg-gradient-to-r from-teal-600 to-emerald-600 text-white font-bold rounded-xl shadow-lg shadow-teal-500/30 hover:-translate-y-0.5 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Continuar
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Modal Enviar Email - Modern Glass */}
      {showEmailModal && selectedReport && (
        <div className="fixed inset-0 bg-gray-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl shadow-2xl w-full max-w-lg overflow-hidden border border-white/40">
            <div className="px-6 py-4 bg-gray-50/80 backdrop-blur-md border-b border-gray-100 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <PaperAirplaneIcon className="h-5 w-5 text-blue-600" />
                </div>
                <h3 className="text-lg font-bold text-gray-900">Contactar Proveedor</h3>
              </div>
              <button onClick={() => setShowEmailModal(false)} className="text-gray-400 hover:text-gray-600">
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>
            {/* Modal Body */}
            <div className="p-6 space-y-4">

              {/* Destinatario */}
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Correo del Proveedor (Para)
                </label>
                <input
                  type="email"
                  value={emailData.to}
                  onChange={(e) => setEmailData({ ...emailData, to: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-lg text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                  placeholder="ejemplo@proveedor.com"
                />
              </div>

              {/* Instrucciones del Flujo */}
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-800 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-blue-800 dark:text-blue-300 mb-2 flex items-center gap-2">
                  ℹ️ Flujo de Envío Profesional
                </h4>
                <ol className="list-decimal list-inside text-sm text-blue-700 dark:text-blue-400 space-y-1">
                  <li>Al hacer clic en <strong>Enviar Correo</strong>, se descargará el reporte PDF.</li>
                  <li>Se abrirá tu <strong>Outlook</strong> automáticamente.</li>
                  <li>Debes <strong>ADJUNTAR MANUALMENTE</strong> el archivo descargado al correo.</li>
                </ol>
              </div>

              {/* Attachment Preview (Visual only) */}
              <div className="flex items-center gap-3 p-3 bg-slate-100 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
                <div className="p-2 bg-white dark:bg-slate-700 rounded-md shadow-sm">
                  <PaperClipIcon className="w-5 h-5 text-slate-500" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-700 dark:text-slate-200 truncate">
                    Reporte_{selectedReport?.report_number}.pdf
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Se descargará automáticamente
                  </p>
                </div>
              </div>

            </div>

            {/* Footer */}
            <div className="flex items-center justify-end gap-3 p-6 border-t border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 rounded-b-2xl">
              <button
                onClick={() => setShowEmailModal(false)}
                className="px-4 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-lg transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleSendEmail}
                disabled={isSubmitting}
                className="flex items-center gap-2 px-6 py-2 text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 rounded-lg shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed transform active:scale-95"
              >
                {isSubmitting ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Procesando...
                  </>
                ) : (
                  <>
                    <EnvelopeIcon className="w-4 h-4" />
                    Enviar Correo
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Incident Closure Modal */}
      {showIncidentClosure && selectedIncidentForClosure && (
        <IncidentClosureForm
          incident={selectedIncidentForClosure}
          onSubmit={handleClosureSubmit}
          onCancel={() => {
            setShowIncidentClosure(false);
            setSelectedIncidentForClosure(null);
          }}
          isLoading={isSubmitting}
        />
      )}
      {/* Selection Modal for Create Report */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-gray-900/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full border border-white/20 p-6">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold text-gray-900">Crear Reporte para Proveedor</h3>
              <button onClick={() => setShowCreateModal(false)} className="text-gray-400 hover:text-gray-600">
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>

            <div className="space-y-4">
              <div className="bg-teal-50 p-4 rounded-xl mb-4">
                <p className="text-sm text-teal-800 font-medium flex items-center">
                  <ExclamationTriangleIcon className="h-5 w-5 mr-2" />
                  Seleccione una incidencia escalada a proveedor.
                </p>
              </div>

              <label className="block text-sm font-bold text-gray-700 mb-2">Incidencia</label>
              <select
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-teal-500 focus:border-teal-500 bg-white"
                onChange={(e) => {
                  if (e.target.value) handleIncidentSelectForCreate(e.target.value);
                }}
                defaultValue=""
              >
                <option value="" disabled>Seleccione para continuar...</option>
                {(Array.isArray(openIncidents) ? openIncidents : (openIncidents?.results || []))
                  .map(incident => (
                    <option key={incident.id} value={incident.id}>
                      {incident.code} - {incident.provider || 'Sin Proveedor'}
                    </option>
                  ))}
              </select>

              <div className="mt-6 flex justify-end">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-gray-600 font-medium hover:bg-gray-100 rounded-lg"
                >
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-gray-900/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white/90 backdrop-blur-xl rounded-3xl p-8 max-w-md w-full shadow-2xl border border-white/50">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Adjuntar Reporte Externo</h3>

            <div className="mb-4">
              <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">
                Seleccionar Incidencia
              </label>
              <div className="relative">
                <select
                  value={selectedIncidentId}
                  onChange={(e) => setSelectedIncidentId(e.target.value)}
                  className="w-full pl-4 pr-10 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 appearance-none font-medium text-gray-700"
                >
                  <option value="">Seleccionar...</option>
                  {(Array.isArray(openIncidents) ? openIncidents : (openIncidents?.results || []))
                    .map(incident => (
                      <option key={incident.id} value={incident.id}>
                        {incident.code} - {incident.provider}
                      </option>
                    ))}
                </select>
              </div>
            </div>

            <p className="text-sm text-gray-500 mb-6 font-medium">Subir PDF, Word o Excel enviado por el proveedor.</p>

            <button
              className={`w-full py-4 border-2 border-dashed border-gray-300 rounded-2xl text-center transition-all group ${!selectedIncidentId ? 'opacity-50 cursor-not-allowed' : 'hover:bg-teal-50 hover:border-teal-400'}`}
              onClick={() => selectedIncidentId && handleUploadDocument()} // This handles the click if ID set
            >
              <PaperClipIcon className="h-8 w-8 text-gray-400 group-hover:text-teal-500 mx-auto mb-2" />
              <span className="block text-sm font-bold text-teal-600">Seleccionar Archivo</span>
            </button>

            <button
              onClick={() => setShowUploadModal(false)}
              className="mt-6 w-full py-3 bg-gray-100 text-gray-700 font-bold rounded-xl hover:bg-gray-200 transition-colors"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}


      {/* Close Incident Modal - Simple Version (like Visit Reports) */}
      {showCloseModal && selectedIncidentForClosure && (
        <div className="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
          <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" onClick={() => setShowCloseModal(false)}></div>

            <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="sm:flex sm:items-start">
                  <div className="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-green-100 sm:mx-0 sm:h-10 sm:w-10">
                    <CheckCircleIcon className="h-6 w-6 text-green-600" aria-hidden="true" />
                  </div>
                  <div className="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
                    <h3 className="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                      Cerrar Incidencia desde Proveedor
                    </h3>
                    <div className="mt-2">
                      <p className="text-sm text-gray-500 mb-4">
                        Estás cerrando la incidencia <b>{selectedIncidentForClosure.code}</b> desde la etapa de Proveedor.
                        Esta acción es definitiva.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="space-y-6">
                  {/* Etapa de Cierre (Pre-selected as 'proveedor') */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Etapa de Cierre <span className="text-red-500">*</span>
                    </label>
                    <select
                      value={closureData.stage}
                      onChange={(e) => setClosureData({ ...closureData, stage: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors bg-gray-50"
                      disabled
                    >
                      <option value="proveedor">Proveedor</option>
                    </select>
                    <p className="mt-1 text-xs text-gray-500">Esta etapa está pre-seleccionada automáticamente</p>
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
                      <option value="Resuelto por el proveedor">Resuelto por el proveedor</option>
                      <option value="Respuesta satisfactoria del proveedor">Respuesta satisfactoria del proveedor</option>
                      <option value="Producto reemplazado">Producto reemplazado</option>
                      <option value="Crédito otorgado">Crédito otorgado</option>
                      <option value="Solución técnica aplicada">Solución técnica aplicada</option>
                      <option value="Sin garantía aplicable">Sin garantía aplicable</option>
                      <option value="Otro">Otro</option>
                    </select>
                  </div>

                  {/* Resumen Obligatorio */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Resumen de la Respuesta del Proveedor <span className="text-red-500">*</span>
                    </label>
                    <textarea
                      value={closureData.closure_summary}
                      onChange={(e) => setClosureData({ ...closureData, closure_summary: e.target.value })}
                      rows={5}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors"
                      placeholder="Describa la respuesta y acciones del proveedor, soluciones aplicadas y conclusiones (mínimo 10 caracteres)..."
                    />
                    <p className={`mt-1 text-sm ${closureData.closure_summary.length < 10 ? 'text-red-500' : 'text-green-600'}`}>
                      {closureData.closure_summary.length}/10 caracteres mínimos
                    </p>
                  </div>

                  {/* Archivo Adjunto Opcional (Respuesta del Proveedor) */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      <PaperClipIcon className="h-4 w-4 inline mr-1" />
                      Respuesta del Proveedor (Archivo - opcional)
                    </label>
                    <p className="text-xs text-gray-500 mb-2">Se registrará en Trazabilidad Documental</p>
                    <div className="flex items-center space-x-3">
                      <input
                        type="file"
                        id="closure-file-supplier"
                        className="hidden"
                        onChange={(e) => setClosureData({ ...closureData, closure_attachment: e.target.files[0] || null })}
                        accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.txt"
                      />
                      <label
                        htmlFor="closure-file-supplier"
                        className="px-4 py-2 bg-gray-100 text-gray-700 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-200 transition-colors"
                      >
                        Seleccionar Archivo
                      </label>
                      {closureData.closure_attachment && (
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                          <span className="font-medium truncate max-w-[200px]">{closureData.closure_attachment.name}</span>
                          <span className="text-gray-400">({(closureData.closure_attachment.size / 1024).toFixed(1)} KB)</span>
                          <button
                            type="button"
                            onClick={() => setClosureData({ ...closureData, closure_attachment: null })}
                            className="text-red-500 hover:text-red-700"
                          >
                            ✕
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                <div className="mt-8 flex justify-end space-x-4">
                  <button
                    onClick={() => setShowCloseModal(false)}
                    className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
                    disabled={isClosing}
                  >
                    Cancelar
                  </button>
                  <button
                    onClick={handleClosureSubmit}
                    disabled={isClosing || closureData.closure_summary.length < 10 || !closureData.reason}
                    className={`px-6 py-3 rounded-lg font-medium transition-colors flex items-center ${(closureData.closure_summary.length < 10 || !closureData.reason)
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : 'bg-green-600 text-white hover:bg-green-700'
                      }`}
                  >
                    {isClosing ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Cerrando...
                      </>
                    ) : (
                      <>
                        <CheckCircleIcon className="h-5 w-5 mr-2" />
                        Cerrar Incidencia
                      </>
                    )}
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

export default SupplierReportsPage;