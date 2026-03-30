import React, { useState, useMemo, useEffect } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { api, incidentsAPI } from '../services/api';
import { normalizeText } from '../utils/stringUtils';
import { useNotifications } from '../hooks/useNotifications';
import { useDebounce } from '../hooks/useDebounce';
import IncidentSearchSelect from '../components/IncidentSearchSelect';
import {
  PlusIcon,
  DocumentArrowUpIcon,
  EyeIcon,
  TrashIcon,
  XMarkIcon,
  CheckCircleIcon,
  MagnifyingGlassIcon,
  DocumentTextIcon,
  ClipboardDocumentListIcon,
  ArrowPathIcon,
  ArrowUpIcon,
  FolderOpenIcon,
  ExclamationTriangleIcon,
  PaperClipIcon,
  CalendarIcon,
  UserIcon,
  BuildingOfficeIcon,
  PaperAirplaneIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  CalendarDaysIcon,
  PencilSquareIcon
} from '@heroicons/react/24/outline';
import IncidentClosureForm from '../components/IncidentClosureForm';


const VisitReportsPage = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { showSuccess, showError } = useNotifications();

  // Estados principales
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showCloseModal, setShowCloseModal] = useState(false);
  const [selectedIncidentId, setSelectedIncidentId] = useState('');

  const [selectedReportForClose, setSelectedReportForClose] = useState(null);
  const [closureData, setClosureData] = useState({ stage: 'reporte_visita', closure_summary: '', closure_attachment: null });
  const [isClosing, setIsClosing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const debouncedSearchTerm = useDebounce(searchTerm, 500);

  // Reiniciar a la primera página cuando cambie la búsqueda
  useEffect(() => {
    setCurrentPage(1);
  }, [debouncedSearchTerm]);

  // Escalation Modal State
  const [showEscalationModal, setShowEscalationModal] = useState(false);
  const [selectedReportForEscalation, setSelectedReportForEscalation] = useState(null);
  const [escalationData, setEscalationData] = useState({
    subject: '',
    message: '',
    files: []
  });

  // Scroll to top on page mount
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  // Query para obtener reportes de visita existentes con paginación
  const { data: reportsResponse, isLoading: reportsLoading, refetch: refetchReports } = useQuery({
    queryKey: ['visit-reports', currentPage, pageSize, debouncedSearchTerm],
    queryFn: async () => {
      try {
        const response = await api.get('/documents/visit-reports/', {
          params: {
            page: currentPage,
            page_size: pageSize,
            search: normalizeText(debouncedSearchTerm)
          }
        });
        return response.data;
      } catch (error) {
        console.error('Error fetching reports:', error);
        return { results: [], count: 0 };
      }
    },
    keepPreviousData: true
  });

  const reports = useMemo(() => {
    if (!reportsResponse) return [];
    return reportsResponse.results || (Array.isArray(reportsResponse) ? reportsResponse : []);
  }, [reportsResponse]);

  const totalCount = reportsResponse?.count || reports.length;
  const totalPages = Math.ceil(totalCount / pageSize);

  // Query removed for performance: all-incidents-for-reports is now handled asynchronously by IncidentSearchSelect

  // Query para estadísticas globales
  const { data: statsData, isLoading: statsLoading } = useQuery({
    queryKey: ['visit-reports-stats'],
    queryFn: async () => {
      try {
        const response = await api.get('/documents/dashboard/');
        return response.data;
      } catch (error) {
        console.error('Error fetching stats:', error);
        return { visit_reports: null };
      }
    }
  });

  const stats = statsData?.visit_reports || {
    total: 0,
    completed: 0,
    in_lab: 0,
    pending_incidents: 0
  };

  // availableIncidents logic removed: filtering is now handled by the search component or on selection

  // Los reportes ya vienen filtrados y ordenados del servidor
  const filteredReports = reports;

  const handleRefresh = () => {
    refetchReports();
    showSuccess('Datos actualizados');
  };

  // Manejar creación de reporte
  const handleCreateReport = () => {
    if (!selectedIncidentId) {
      showError('Por favor selecciona una incidencia');
      return;
    }
    setShowCreateModal(false);
    navigate(`/visit-report-form?incident_id=${selectedIncidentId}&report_type=cliente`);
  };

  // Manejar subida de documento - CREA un nuevo registro de reporte de visita
  const handleUploadDocument = () => {
    if (!selectedIncidentId) {
      showError('Por favor selecciona una incidencia');
      return;
    }

    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.pdf,.doc,.docx';
    input.onchange = async (e) => {
      const file = e.target.files[0];
      if (file) {
        setIsUploading(true);
        try {
          // Find the selected incident to get its data
          const incident = allIncidents.find(i => i.id === parseInt(selectedIncidentId));

          // Get order number from API linked to the incident (RV-YYYY-XXX)
          let orderNumber = null;
          try {
            const orderResponse = await api.get(`/documents/generate-order-number/?incident_id=${selectedIncidentId}`);
            orderNumber = orderResponse.data.order_number;
          } catch (err) {
            console.warn('Could not get order number from API, will let backend generate it');
          }

          // Create FormData with file and required fields
          const formData = new FormData();
          formData.append('file', file);  // View handles this from request.FILES
          formData.append('related_incident_id', parseInt(selectedIncidentId));
          if (orderNumber) {
            formData.append('order_number', orderNumber);
          }
          formData.append('visit_date', new Date().toISOString().split('T')[0]);
          formData.append('project_name', incident?.obra || '');
          formData.append('client_name', incident?.cliente || '');
          formData.append('client_rut', incident?.cliente_rut || '');
          formData.append('address', incident?.direccion_cliente || incident?.address || 'No especificada');
          formData.append('commune', incident?.comuna || '');
          formData.append('city', incident?.ciudad || incident?.city || '');
          formData.append('salesperson', incident?.salesperson || 'No asignado');
          formData.append('technician', (typeof incident?.responsable === 'object' ? incident?.responsable?.name : incident?.responsable) || 'No asignado');
          formData.append('visit_reason', 'Post Venta');
          formData.append('status', 'approved');

          // POST to visit-reports to create a new record with the file
          await api.post('/documents/visit-reports/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          });

          showSuccess('Reporte de visita creado con el documento adjunto');
          setShowUploadModal(false);
          setSelectedIncidentId('');
          refetchReports();
          queryClient.invalidateQueries(['all-incidents-for-reports']);
        } catch (error) {
          console.error('Error uploading:', error);
          const errorMsg = error.response?.data?.related_incident ||
            error.response?.data?.non_field_errors?.[0] ||
            error.response?.data?.detail ||
            'Error al subir el documento';
          showError(errorMsg);
        } finally {
          setIsUploading(false);
        }
      }
    };
    input.click();
  };

  // Manejar apertura de documento
  const handleOpenDocument = async (report) => {
    if (!report.pdf_path && !report.download_url && !report.has_document) {
      showError('No hay documento disponible');
      return;
    }

    try {
      // Use authenticated API call to fetch the PDF as blob
      const response = await api.get(`/documents/visit-reports/${report.id}/download/`, {
        responseType: 'blob'
      });

      // Create a blob URL and open it
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      window.open(url, '_blank');

      // Clean up blob URL after a delay
      setTimeout(() => window.URL.revokeObjectURL(url), 60000);
    } catch (error) {
      console.error('Error opening document:', error);
      showError('Error al abrir el documento');
    }
  };

  // Manejar eliminación de reporte
  const handleDeleteReport = async (reportId) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este reporte?')) {
      try {
        await api.delete(`/documents/visit-reports/${reportId}/`);
        showSuccess('Reporte eliminado');
        refetchReports();
      } catch (error) {
        console.error('Error deleting:', error);
        showError('Error al eliminar el reporte');
      }
    }
  };

  // Manejar escalamiento a calidad
  // Open Escalate Modal
  const openEscalationModal = (report) => {
    setSelectedReportForEscalation(report);
    // Pre-fill
    const incidentCode = report.related_incident?.code || (typeof report.related_incident === 'object' ? report.related_incident.code : 'INC-????');
    setEscalationData({
      subject: `Escalación a Calidad: ${incidentCode}`,
      message: `Se solicita revisión de calidad para la incidencia ${incidentCode}.\n\nAdjunto reporte de visita.\n\nSaludos.`,
      files: []
    });
    setShowEscalationModal(true);
  };

  // Submit Escalation
  const handleConfirmEscalation = async () => {
    if (!selectedReportForEscalation) return;

    setIsUploading(true);
    try {
      const incidentId = typeof selectedReportForEscalation.related_incident === 'object'
        ? selectedReportForEscalation.related_incident.id
        : selectedReportForEscalation.related_incident;

      const incidentCode = selectedReportForEscalation.related_incident?.code ||
        (typeof selectedReportForEscalation.related_incident === 'object'
          ? selectedReportForEscalation.related_incident.code
          : `INC-${incidentId}`);

      // Llamar al backend para registrar el escalamiento
      const response = await api.post(`/incidents/${incidentId}/escalate/quality/`, {
        reason: 'Escalado desde reporte de visita',
        visit_report_id: selectedReportForEscalation.id
      });

      if (response.data?.success) {
        showSuccess(response.data.message || 'Incidencia escalada a Calidad y correo enviado automáticamente.');
      } else {
        showSuccess('Incidencia escalada a Calidad.');
      }

      setShowEscalationModal(false);
      setSelectedReportForEscalation(null);
      refetchReports();
    } catch (error) {
      console.error('Error escalating:', error);
      showError(error.response?.data?.error || 'Error al escalar la incidencia');
    } finally {
      setIsUploading(false);
    }
  };

  // Manejar escalamiento a calidad (Old function replaced/redirected)
  const handleEscalateToQuality = (report) => {
    openEscalationModal(report);
  };

  // Abrir modal de cierre (estilo Incidents.jsx)
  const openCloseModal = (report) => {
    setSelectedReportForClose(report);
    setClosureData({
      stage: 'reporte_visita',
      closure_summary: '',
      closure_attachment: null,
      reason: '' // Added reason for traceability
    });
    setShowCloseModal(true);
  };

  // Confirmar cierre de incidencia con diálogo obligatorio (estilo Incidents.jsx)
  const handleIncidentClosure = async (formData) => {
    if (!selectedReportForClose) return;
    setIsClosing(true);
    try {
      const incidentId = selectedReportForClose.related_incident?.id || selectedReportForClose.related_incident;
      
      const payload = new FormData();
      payload.append('stage', formData.stage);
      payload.append('closure_summary', formData.closure_summary);
      if (formData.closure_attachment) {
        payload.append('closure_attachment', formData.closure_attachment);
      }
      if (selectedReportForClose?.technician_id) {
        payload.append('technician_code', selectedReportForClose.technician_id);
      }

      await incidentsAPI.close(incidentId, payload);

      // Opcional: Actualizar estado del reporte si es necesario (ya se hace en backend usualmente)
      try {
        await api.patch(`/documents/visit-reports/${selectedReportForClose.id}/`, { status: 'closed' });
      } catch (patchErr) {
        console.warn('Could not update report status via patch:', patchErr);
      }

      queryClient.invalidateQueries(['visit-reports']);
      queryClient.invalidateQueries(['all-incidents-for-reports']);
      showSuccess('Incidencia y reporte cerrados exitosamente');
      setShowCloseModal(false);
      setSelectedReportForClose(null);
    } catch (error) {
      console.error('Error closing incident:', error);
      showError('Error al cerrar la incidencia: ' + (error.response?.data?.error || error.message));
    } finally {
      setIsClosing(false);
    }
  };

  // Manejar subida de imágenes adicionales a un reporte
  const handleUploadImages = (reportId) => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.multiple = true;
    input.onchange = async (e) => {
      const files = Array.from(e.target.files);
      if (files.length === 0) return;

      setIsUploading(true);
      let successCount = 0;

      try {
        for (const file of files) {
          const formData = new FormData();
          formData.append('file', file);
          formData.append('document_type', 'visit_image');

          await api.post(`/documents/report-attachments/${reportId}/visit/upload/`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          });
          successCount++;
        }

        showSuccess(`${successCount} imagen(es) subida(s) exitosamente`);
        refetchReports();
      } catch (error) {
        console.error('Error uploading images:', error);
        showError('Error al subir las imágenes');
      } finally {
        setIsUploading(false);
      }
    };
    input.click();
  };

  // Ver imágenes adjuntas de un reporte
  const handleViewImages = async (report) => {
    setSelectedReportForImages(report);
    try {
      const response = await api.get(`/documents/report-attachments/${report.id}/visit/`);
      const data = response.data;
      const images = Array.isArray(data) ? data : (data?.results || []);
      setReportImages(images);
      setShowImagesModal(true);
    } catch (error) {
      console.error('Error fetching images:', error);
      setReportImages([]);
      setShowImagesModal(true);
    }
  };

  // Abrir imagen en nueva pestaña
  const handleViewImage = async (image) => {
    try {
      const response = await api.get(`/documents/report-attachments/${selectedReportForImages.id}/visit/${image.id}/view/`, {
        responseType: 'blob'
      });
      const blob = new Blob([response.data], { type: image.content_type || 'image/jpeg' });
      const url = window.URL.createObjectURL(blob);
      window.open(url, '_blank');
      setTimeout(() => window.URL.revokeObjectURL(url), 60000);
    } catch (error) {
      console.error('Error viewing image:', error);
      showError('Error al ver la imagen');
    }
  };

  // Helper para obtener badge de estado (3 estados simplificados)
  const getStatusBadge = (report) => {
    const status = report.status;
    const escalatedToQuality = report.escalated_to_quality;

    // Get incident status from either nested object or direct field
    const incidentStatus = typeof report.related_incident === 'object'
      ? report.related_incident?.estado
      : null;

    // 1. Cerrado (PRIORITY OVER ALL OTHERS)
    if (status === 'closed' || status === 'completed' || incidentStatus === 'cerrado') {
      return <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-gray-200 text-gray-700">Cerrado</span>;
    }

    // 2. Laboratorio (escalado a calidad)
    if (escalatedToQuality) {
      return <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-purple-100 text-purple-800">Laboratorio</span>;
    }

    // 3. Creado (cualquier otro estado)
    return <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">Creado</span>;
  };

  if (reportsLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando reportes de visita...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 px-4 pb-8">
      {/* Page Header - Rediseñado para mayor claridad */}
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6 bg-white/80 backdrop-blur-xl p-6 rounded-2xl border border-white/60 shadow-xl">
        <div className="flex items-center gap-4">
          <div className="bg-blue-600 p-3 rounded-xl shadow-lg shadow-blue-200">
            <ClipboardDocumentListIcon className="h-7 w-7 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-slate-900 tracking-tight leading-none flex items-center">
              Reportes de <span className="text-blue-600 ml-2">Visita</span>
            </h1>
            <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mt-1.5 opacity-70">
              Gestión técnica y validación de campo
            </p>
          </div>
        </div>

        <div className="flex flex-wrap gap-4 w-full lg:w-auto">
          <button
            onClick={handleRefresh}
            className="w-12 h-12 flex items-center justify-center text-slate-400 hover:text-blue-600 bg-white border border-slate-100 rounded-2xl shadow-sm transition-all"
            title="Refrescar datos"
          >
            <ArrowPathIcon className="w-5 h-5" />
          </button>

          <button
            onClick={() => { setSelectedIncidentId(''); setShowUploadModal(true); }}
            className="px-6 py-4 bg-slate-50 hover:bg-slate-100 text-slate-600 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all flex items-center gap-3 border border-slate-100 shadow-sm"
          >
            <DocumentArrowUpIcon className="h-5 w-5 text-blue-500" />
            ADJUNTAR PDF
          </button>

          <button
            onClick={() => { setSelectedIncidentId(''); setShowCreateModal(true); }}
            className="px-8 py-4 bg-slate-900 hover:bg-blue-600 text-white rounded-2xl text-[10px] font-black uppercase tracking-widest shadow-xl shadow-slate-200 transition-all flex items-center gap-3"
          >
            <PlusIcon className="h-5 w-5 text-blue-300" />
            CREAR REPORTE
          </button>
        </div>
      </div>

      {/* Stats Cards - Más espaciosas y legibles */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Total Reportes', val: stats.total, icon: ClipboardDocumentListIcon, color: 'text-slate-900', bg: 'bg-white', iconColor: 'text-slate-400' },
          { label: 'Completados', val: stats.completed, icon: CheckCircleIcon, color: 'text-emerald-700', bg: 'bg-emerald-50/40', iconColor: 'text-emerald-500' },
          { label: 'En Laboratorio', val: stats.in_lab, icon: ExclamationTriangleIcon, color: 'text-purple-700', bg: 'bg-purple-50/40', iconColor: 'text-purple-500' },
          { label: 'Inc. Pendientes', val: stats.pending_incidents, icon: CalendarDaysIcon, color: 'text-amber-700', bg: 'bg-amber-50/40', iconColor: 'text-amber-500' }
        ].map((k, i) => (
          <div key={i} className={`p-5 rounded-2xl border border-white/60 ${k.bg} backdrop-blur-xl shadow-sm hover:shadow-md transition-all border border-slate-200/60`}>
            <div className="flex justify-between items-start mb-3">
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest italic">{k.label}</p>
              <k.icon className={`w-5 h-5 ${k.iconColor}`} />
            </div>
            <div className="flex items-baseline gap-2">
              <p className={`text-3xl font-black ${k.color} tracking-tight leading-none`}>
                {k.val}
              </p>
              <span className="text-[10px] font-bold text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded uppercase">Registros</span>
            </div>
          </div>
        ))}
      </div>

      {/* Search Bar - Más integrada y espaciosa */}
      <div className="bg-white/70 backdrop-blur-xl rounded-2xl shadow-xl shadow-slate-200/50 p-6 border border-white/60">
        <div className="flex flex-col md:flex-row items-center gap-4">
          <div className="flex-1 relative w-full">
            <MagnifyingGlassIcon className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-slate-400" />
            <input
              type="text"
              placeholder="Buscar por número de orden, cliente, proyecto..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-12 py-3.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 transition-all text-sm font-medium text-slate-700 placeholder:text-slate-400"
            />
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                className="absolute right-4 top-1/2 transform -translate-y-1/2 p-1 text-slate-400 hover:text-slate-600 transition-colors"
              >
                <XMarkIcon className="h-5 w-5" />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Reports Table - Diseño Premium y Espacioso */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xl shadow-slate-200/40 overflow-hidden">
        <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <DocumentTextIcon className="h-5 w-5 text-blue-600" />
            </div>
            <h2 className="text-sm font-black text-slate-800 uppercase tracking-widest italic">
              Reportes Generados
            </h2>
          </div>
          <span className="bg-blue-600/10 text-blue-700 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider">
            {totalCount} registros totales
          </span>
        </div>

        {filteredReports.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50/50 border-b border-slate-200">
                  <th className="px-6 py-4 text-[11px] font-black text-slate-400 uppercase tracking-widest">N° Reporte</th>
                  <th className="px-6 py-4 text-[11px] font-black text-slate-400 uppercase tracking-widest">Incidencia</th>
                  <th className="px-6 py-4 text-[11px] font-black text-slate-400 uppercase tracking-widest">Clasificación</th>
                  <th className="px-6 py-4 text-[11px] font-black text-slate-400 uppercase tracking-widest">Cliente / Obra</th>
                  <th className="px-6 py-4 text-[11px] font-black text-slate-400 uppercase tracking-widest">Fecha Visita</th>
                  <th className="px-6 py-4 text-[11px] font-black text-slate-400 uppercase tracking-widest text-center">Estado</th>
                  <th className="px-6 py-4 text-[11px] font-black text-slate-400 uppercase tracking-widest text-right">Gestión</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 italic">
                {filteredReports.map((report) => (
                  <tr key={report.id} className="hover:bg-blue-50/40 transition-colors group">
                    <td className="px-6 py-4">
                      <div className="flex flex-col">
                        <span className="text-sm font-black text-slate-900 group-hover:text-blue-600 transition-colors">
                          {report.order_number || `REP-${report.id}`}
                        </span>
                        <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Reporte Interno</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-black bg-blue-50 text-blue-700 border border-blue-100 uppercase tracking-tight">
                        {report.related_incident?.code || (typeof report.related_incident === 'object' ? report.related_incident?.code : '-')}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-col">
                        <span className="text-sm font-bold text-slate-700 uppercase mb-1">
                          {report.categoria ? report.categoria.replace(/_/g, ' ') : 'S/C'}
                        </span>
                        {report.subcategoria && (
                          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wide">
                            {report.subcategoria}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 max-w-[280px]">
                      <div className="text-sm font-black text-slate-800 uppercase truncate leading-snug">
                        {report.client_name || 'Sin Nombre de Cliente'}
                      </div>
                      <div className="text-xs font-bold text-slate-400 mt-0.5 uppercase truncate flex items-center gap-1.5 leading-none">
                        <BuildingOfficeIcon className="w-3 h-3" />
                        {report.project_name || 'Sin Obra Especificada'}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm font-bold text-slate-600 tabular-nums">
                      <div className="flex items-center gap-2">
                        <CalendarIcon className="w-4 h-4 text-slate-300" />
                        {report.visit_date ? new Date(report.visit_date).toLocaleDateString('es-CL') : 'N/A'}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-center">{getStatusBadge(report)}</td>
                    <td className="px-10 py-6">
                      {/* Lógica de Gestión Centralizada */}
                      {(() => {
                        const rStatus = report.status;
                        const incidentStatus = typeof report.related_incident === 'object' 
                          ? report.related_incident?.estado 
                          : null;
                        
                        const isClosed = rStatus === 'closed' || rStatus === 'completed' || incidentStatus === 'cerrado';
                        
                        return (
                          <div className="flex items-center justify-center gap-3">
                            <button
                              onClick={(e) => { e.stopPropagation(); handleOpenDocument(report); }}
                              className="w-12 h-12 flex items-center justify-center rounded-2xl bg-blue-50 text-blue-600 hover:bg-blue-600 hover:text-white transition-all shadow-sm"
                              title="Explorar Documento"
                            >
                              <EyeIcon className="w-6 h-6" />
                            </button>
                            
                            {!isClosed && (
                              <button
                                onClick={(e) => { e.stopPropagation(); navigate(`/visit-report-form/${report.id}`); }}
                                className="w-12 h-12 flex items-center justify-center rounded-2xl bg-indigo-50 text-indigo-600 hover:bg-indigo-600 hover:text-white transition-all shadow-sm"
                                title="Editar Reporte"
                              >
                                <PencilSquareIcon className="w-6 h-6" />
                              </button>
                            )}

                            {!isClosed && !report.escalated_to_quality && (
                              <>
                                <button
                                  onClick={(e) => { e.stopPropagation(); handleEscalateToQuality(report); }}
                                  className="w-12 h-12 flex items-center justify-center rounded-2xl bg-amber-50 text-amber-600 hover:bg-amber-600 hover:text-white transition-all shadow-sm"
                                  title="Escalar a Calidad"
                                >
                                  <ArrowUpIcon className="w-6 h-6" />
                                </button>
                                <button
                                  onClick={(e) => { e.stopPropagation(); openCloseModal(report); }}
                                  className="w-12 h-12 flex items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600 hover:bg-emerald-600 hover:text-white transition-all shadow-sm"
                                  title="Cerrar Reporte"
                                >
                                  <CheckCircleIcon className="w-6 h-6" />
                                </button>
                              </>
                            )}
                            
                            <button
                              onClick={(e) => { e.stopPropagation(); handleDeleteReport(report.id); }}
                              className="w-12 h-12 flex items-center justify-center rounded-2xl bg-rose-50 text-rose-500 hover:bg-rose-500 hover:text-white transition-all shadow-sm"
                              title="Eliminar registro"
                            >
                              <TrashIcon className="w-6 h-6" />
                            </button>
                          </div>
                        );
                      })()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-16">
            <FolderOpenIcon className="mx-auto h-16 w-16 text-gray-300" />
            <h3 className="mt-4 text-lg font-medium text-gray-900">No hay reportes de visita</h3>
            <p className="mt-2 text-gray-500">
              Crea un nuevo reporte seleccionando una incidencia
            </p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="mt-6 inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <PlusIcon className="h-4 w-4 mr-2" />
              Crear Reporte
            </button>
          </div>
        )}
      </div>

      {/* Pagination - Rediseñada para mayor claridad */}
      {
        totalPages > 1 && (
          <div className="mt-8 flex items-center justify-between bg-white px-8 py-5 rounded-2xl shadow-xl shadow-slate-200/40 border border-slate-100">
            <div className="flex-1 flex justify-between sm:hidden">
              <button
                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                disabled={currentPage === 1}
                className="relative inline-flex items-center px-4 py-2 border border-slate-300 text-sm font-black rounded-xl text-slate-700 bg-white hover:bg-slate-50 disabled:opacity-30 transition-all uppercase tracking-wider"
              >
                Anterior
              </button>
              <button
                onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                disabled={currentPage === totalPages}
                className="ml-3 relative inline-flex items-center px-4 py-2 border border-slate-300 text-sm font-black rounded-xl text-slate-700 bg-white hover:bg-slate-50 disabled:opacity-30 transition-all uppercase tracking-wider"
              >
                Siguiente
              </button>
            </div>
            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p className="text-sm font-bold text-slate-500 uppercase tracking-widest italic">
                  Mostrando <span className="text-slate-900">{(currentPage - 1) * pageSize + 1}</span> a{' '}
                  <span className="text-slate-900">{Math.min(currentPage * pageSize, totalCount)}</span> de{' '}
                  <span className="text-blue-600 font-black">{totalCount}</span> resultados
                </p>
              </div>
              <div className="flex items-center gap-6">
                <div className="flex items-center gap-3">
                  <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Filas:</span>
                  <select
                    value={pageSize}
                    onChange={(e) => {
                      setPageSize(Number(e.target.value));
                      setCurrentPage(1);
                    }}
                    className="px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 transition-all font-black text-slate-700 outline-none"
                  >
                    <option value={10}>10</option>
                    <option value={20}>20</option>
                    <option value={50}>50</option>
                  </select>
                </div>

                <nav className="relative z-0 inline-flex rounded-xl shadow-sm -space-x-px overflow-hidden border border-slate-200" aria-label="Pagination">
                  <button
                    onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                    disabled={currentPage === 1}
                    className="relative inline-flex items-center px-3 py-2 bg-white text-slate-500 hover:bg-blue-50 disabled:opacity-30 transition-all border-r border-slate-200"
                  >
                    <span className="sr-only">Anterior</span>
                    <ChevronLeftIcon className="h-5 w-5" aria-hidden="true" />
                  </button>
                  {[...Array(totalPages)].map((_, i) => {
                    const pageNum = i + 1;
                    // Lógica para mostrar número limitado de páginas si hay muchas
                    if (
                      pageNum === 1 ||
                      pageNum === totalPages ||
                      (pageNum >= currentPage - 1 && pageNum <= currentPage + 1)
                    ) {
                      return (
                        <button
                          key={pageNum}
                          onClick={() => setCurrentPage(pageNum)}
                          className={`relative inline-flex items-center px-4 py-2 text-xs font-black uppercase transition-colors ${currentPage === pageNum
                            ? 'bg-blue-600 text-white'
                            : 'bg-white text-slate-500 hover:bg-blue-50 text-slate-700'
                            } border-r border-slate-200 last:border-r-0`}
                        >
                          {pageNum}
                        </button>
                      );
                    }
                    if (pageNum === currentPage - 2 || pageNum === currentPage + 2) {
                      return <span key={pageNum} className="px-4 py-2 bg-white text-slate-300 border-r border-slate-200 last:border-r-0">...</span>;
                    }
                    return null;
                  })}
                  <button
                    onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                    disabled={currentPage === totalPages}
                    className="relative inline-flex items-center px-4 py-2 bg-white text-slate-500 hover:bg-blue-50 disabled:opacity-30 transition-all"
                  >
                    <span className="sr-only">Siguiente</span>
                    <ChevronRightIcon className="h-5 w-5" aria-hidden="true" />
                  </button>
                </nav>
              </div>
            </div>
          </div>
        )
      }

      {/* Modals Section */}
      {
        showCreateModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden">
              <div className="px-6 py-4 bg-gradient-to-r from-blue-600 to-indigo-600">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-white flex items-center">
                    <PlusIcon className="h-5 w-5 mr-2" />
                    Crear Reporte de Visita
                  </h3>
                  <button onClick={() => setShowCreateModal(false)} className="text-white/80 hover:text-white">
                    <XMarkIcon className="h-6 w-6" />
                  </button>
                </div>
              </div>
              <div className="p-6">
                  <>
                    <IncidentSearchSelect 
                      label="Seleccionar Incidencia"
                      value={selectedIncidentId}
                      onChange={setSelectedIncidentId}
                      placeholder="Busca por código (INC-...) o cliente..."
                      onlyAvailable={true}
                    />
                    <p className="text-[10px] text-slate-500 mt-2 italic">
                      Solo se pueden crear reportes para incidencias abiertas.
                    </p>
                  </>

                <div className="flex justify-end gap-3 mt-6 pt-4 border-t">
                  <button
                    onClick={() => setShowCreateModal(false)}
                    className="px-4 py-2.5 text-gray-700 bg-gray-100 rounded-xl hover:bg-gray-200 font-medium"
                  >
                    Cancelar
                  </button>
                  <button
                    onClick={handleCreateReport}
                    disabled={!selectedIncidentId}
                    className="px-6 py-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                  >
                    Continuar
                  </button>
                </div>
              </div>
            </div>
          </div>
        )
      }



      {/* Escalation Modal */}
      {
        showEscalationModal && selectedReportForEscalation && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
            <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl animate-fade-in border border-gray-100">
              <div className="px-6 py-4 bg-gradient-to-r from-orange-500 to-red-600 rounded-t-2xl flex items-center justify-between">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <ArrowUpIcon className="h-5 w-5" />
                  Escalar a Calidad
                </h3>
                <button
                  onClick={() => setShowEscalationModal(false)}
                  className="text-white/70 hover:text-white p-1 rounded-lg hover:bg-white/10 transition-colors"
                >
                  <XMarkIcon className="h-5 w-5" />
                </button>
              </div>

              <div className="p-6 space-y-5">
                <div className="bg-orange-50 border border-orange-100 rounded-xl p-4 text-sm text-orange-800 flex items-start gap-3">
                  <ExclamationTriangleIcon className="h-5 w-5 text-orange-600 shrink-0 mt-0.5" />
                  <div>
                    <p className="font-medium">Confirmación de Escalamiento</p>
                    <p className="mt-1 text-orange-700/80">
                      Se notificará al departamento de Calidad y se adjuntará automáticamente el reporte de visita actual.
                    </p>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1.5">Asunto del Correo</label>
                  <input
                    type="text"
                    value={escalationData.subject}
                    onChange={(e) => setEscalationData({ ...escalationData, subject: e.target.value })}
                    className="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 bg-gray-50 focus:bg-white transition-all"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1.5">Mensaje Adicional</label>
                  <textarea
                    value={escalationData.message}
                    onChange={(e) => setEscalationData({ ...escalationData, message: e.target.value })}
                    rows={4}
                    className="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 bg-gray-50 focus:bg-white transition-all resize-none"
                    placeholder="Describe el motivo del escalamiento..."
                  />
                </div>

              </div>

              <div className="px-6 py-4 bg-gray-50 border-t border-gray-100 rounded-b-2xl flex justify-end gap-3">
                <button
                  onClick={() => setShowEscalationModal(false)}
                  className="px-5 py-2.5 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 font-medium text-sm transition-colors shadow-sm"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleConfirmEscalation}
                  disabled={isUploading}
                  className="px-5 py-2.5 bg-orange-600 text-white rounded-lg font-semibold hover:bg-orange-700 shadow-md hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed text-sm flex items-center gap-2"
                >
                  {isUploading ? (
                    <>
                      <ArrowPathIcon className="h-4 w-4 animate-spin" />
                      Escalando...
                    </>
                  ) : (
                    <>
                      <span>Confirmar Escalamiento</span>
                      <PaperAirplaneIcon className="h-4 w-4 -rotate-45" />
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        )
      }

      {/* Modal Subir Documento */}
      {
        showUploadModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden">
              <div className="px-6 py-4 bg-gradient-to-r from-green-600 to-emerald-600">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-white flex items-center">
                    <DocumentArrowUpIcon className="h-5 w-5 mr-2" />
                    Adjuntar Reporte de Visita (PDF)
                  </h3>
                  <button onClick={() => setShowUploadModal(false)} className="text-white/80 hover:text-white">
                    <XMarkIcon className="h-6 w-6" />
                  </button>
                </div>
              </div>
              <div className="p-6">
                  <>
                    <IncidentSearchSelect 
                      label="Seleccionar Incidencia"
                      value={selectedIncidentId}
                      onChange={setSelectedIncidentId}
                      placeholder="Busca por código o cliente..."
                      onlyAvailable={true}
                    />

                    <button
                      onClick={handleUploadDocument}
                      disabled={!selectedIncidentId || isUploading}
                      className="w-full mt-6 flex items-center justify-center px-4 py-4 border-2 border-dashed border-gray-300 rounded-xl hover:border-green-400 hover:bg-green-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      <DocumentArrowUpIcon className="h-6 w-6 mr-3 text-gray-500" />
                      <span className="text-gray-700 font-medium">
                        {isUploading ? 'Subiendo...' : 'Seleccionar archivo PDF'}
                      </span>
                    </button>
                  </>

                <div className="flex justify-end mt-6 pt-4 border-t">
                  <button
                    onClick={() => setShowUploadModal(false)}
                    className="px-4 py-2.5 text-gray-700 bg-gray-100 rounded-xl hover:bg-gray-200 font-medium"
                  >
                    Cerrar
                  </button>
                </div>
              </div>
            </div>
          </div>
        )
      }


      {/* Escalation Modal */}

      {
        showEscalationModal && selectedReportForEscalation && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
            <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl animate-fade-in border border-gray-100">
              <div className="px-6 py-4 bg-gradient-to-r from-orange-500 to-red-600 rounded-t-2xl flex items-center justify-between">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <ArrowUpIcon className="h-5 w-5" />
                  Escalar a Calidad
                </h3>
                <button
                  onClick={() => setShowEscalationModal(false)}
                  className="text-white/70 hover:text-white p-1 rounded-lg hover:bg-white/10 transition-colors"
                >
                  <XMarkIcon className="h-5 w-5" />
                </button>
              </div>

              <div className="p-6 space-y-5">
                <div className="bg-orange-50 border border-orange-100 rounded-xl p-4 text-sm text-orange-800 flex items-start gap-3">
                  <ExclamationTriangleIcon className="h-5 w-5 text-orange-600 shrink-0 mt-0.5" />
                  <div>
                    <p className="font-medium">Confirmación de Escalamiento</p>
                    <p className="mt-1 text-orange-700/80">
                      Se notificará al departamento de Calidad y se adjuntará automáticamente el reporte de visita actual.
                    </p>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1.5">Asunto del Correo</label>
                  <input
                    type="text"
                    value={escalationData.subject}
                    onChange={(e) => setEscalationData({ ...escalationData, subject: e.target.value })}
                    className="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 bg-gray-50 focus:bg-white transition-all"
                  />
                </div>




              </div>

              <div className="px-6 py-4 bg-gray-50 border-t border-gray-100 rounded-b-2xl flex justify-end gap-3">
                <button
                  onClick={() => setShowEscalationModal(false)}
                  className="px-5 py-2.5 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 font-medium text-sm transition-colors shadow-sm"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleConfirmEscalation}
                  disabled={isUploading}
                  className="px-5 py-2.5 bg-orange-600 text-white rounded-lg font-semibold hover:bg-orange-700 shadow-md hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed text-sm flex items-center gap-2"
                >
                  {isUploading ? (
                    <>
                      <ArrowPathIcon className="h-4 w-4 animate-spin" />
                      Escalando...
                    </>
                  ) : (
                    <>
                      <span>Confirmar Escalamiento</span>
                      <PaperAirplaneIcon className="h-4 w-4 -rotate-45" />
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        )
      }

      {/* Standardized Close Incident Modal */}
      {showCloseModal && selectedReportForClose && (
        <IncidentClosureForm
          incident={selectedReportForClose.related_incident}
          onSubmit={handleIncidentClosure}
          onCancel={() => setShowCloseModal(false)}
          isClosing={isClosing}
          defaultStage="reporte_visita"
        />
      )}
    </div >
  );
};

export default VisitReportsPage;