import React, { useState, useMemo, useEffect } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { api, incidentsAPI } from '../services/api';
import { normalizeText } from '../utils/stringUtils';
import { useNotifications } from '../hooks/useNotifications';
import { useDebounce } from '../hooks/useDebounce';
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
  PhotoIcon,
  PaperAirplaneIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  CalendarDaysIcon
} from '@heroicons/react/24/outline';

const VisitReportsPage = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { showSuccess, showError } = useNotifications();

  // Estados principales
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showCloseModal, setShowCloseModal] = useState(false);
  const [showImagesModal, setShowImagesModal] = useState(false);
  const [selectedReportForImages, setSelectedReportForImages] = useState(null);
  const [reportImages, setReportImages] = useState([]);
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

  // Query para obtener TODAS las incidencias
  const { data: allIncidentsData, isLoading: incidentsLoading } = useQuery({
    queryKey: ['all-incidents-for-reports'],
    queryFn: async () => {
      try {
        const response = await incidentsAPI.list({ page_size: 200 });
        const data = response.data?.results || response.data || [];
        return Array.isArray(data) ? data : [];
      } catch (error) {
        console.error('Error fetching incidents:', error);
        return [];
      }
    }
  });

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

  const allIncidents = useMemo(() => {
    const data = allIncidentsData?.results || allIncidentsData || [];
    return Array.isArray(data) ? data : [];
  }, [allIncidentsData]);

  // IDs de incidencias que ya tienen reporte de visita
  const incidentsWithReport = useMemo(() => {
    const ids = new Set();
    reports.forEach(report => {
      const incidentId = typeof report.related_incident === 'object'
        ? report.related_incident?.id
        : report.related_incident;
      if (incidentId) ids.add(incidentId);
    });
    return ids;
  }, [reports]);

  // Incidencias disponibles para crear reporte (abiertas y sin reporte de visita)
  const availableIncidents = useMemo(() => {
    return allIncidents.filter(incident =>
      incident.estado !== 'cerrado' &&
      !incidentsWithReport.has(incident.id)
    );
  }, [allIncidents, incidentsWithReport]);

  // Los reportes ya vienen filtrados y ordenados del servidor
  const filteredReports = reports;

  const handleRefresh = () => {
    refetchReports();
    queryClient.invalidateQueries(['all-incidents-for-reports']);
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
          formData.append('visit_reason', '01-Visita Técnica');
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
        // Construir mailto: link para abrir Outlook
        const to = 'vlutz@polifusion.cl;jdiaz@polifusion.cl;cmunizaga@polifusion.cl';
        const cc = 'rcruz@polifusion.cl;srojas@polifusion.cl';
        const subject = encodeURIComponent(`[ESCALACIÓN CALIDAD] ${incidentCode} - ${selectedReportForEscalation.client_name || 'Cliente'}`);

        // URL para ver el reporte en la app
        const reportUrl = `${window.location.origin}/visit-reports`;
        const fechaVisita = selectedReportForEscalation.visit_date
          ? new Date(selectedReportForEscalation.visit_date).toLocaleDateString('es-CL')
          : 'No especificada';

        const body = encodeURIComponent(
          `Estimado equipo de Calidad,

Por medio del presente, se informa que la incidencia ${incidentCode} ha sido escalada al Departamento de Calidad para su revisión y gestión correspondiente.

A continuación se detallan los antecedentes del caso:

    Código de Incidencia: ${incidentCode}
    N° Reporte de Visita: ${selectedReportForEscalation.order_number || 'N/A'}
    Fecha de Visita Técnica: ${fechaVisita}
    Cliente: ${selectedReportForEscalation.client_name || 'No especificado'}
    Proyecto/Obra: ${selectedReportForEscalation.project_name || 'No especificado'}

Descripción del Problema:
${selectedReportForEscalation.problem_description || selectedReportForEscalation.description || escalationData.message || 'Se requiere revisión de calidad según reporte de visita técnica.'}

Para mayor detalle, se puede acceder al reporte completo en el siguiente enlace:
${reportUrl}

Se solicita revisar la información y coordinar las acciones correctivas que correspondan. Quedamos atentos a su respuesta.

Saludos cordiales,

Sistema de Gestión de Incidencias
Polifusión S.A.
`
        );

        // Abrir Outlook con mailto:
        const mailtoUrl = `mailto:${to}?cc=${cc}&subject=${subject}&body=${body}`;
        window.location.href = mailtoUrl;

        showSuccess('Incidencia escalada. Se abrirá Outlook para enviar el correo.');
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
  const handleConfirmClose = async () => {
    if (!selectedReportForClose) return;

    // Validate both reason and summary
    if (!closureData.reason) {
      showError('Por favor selecciona un motivo de cierre');
      return;
    }

    if (closureData.closure_summary.length < 10) {
      showError('El resumen de cierre debe tener al menos 10 caracteres');
      return;
    }

    setIsClosing(true);
    try {
      // Get Incident ID from report
      const incidentId = typeof selectedReportForClose.related_incident === 'object'
        ? selectedReportForClose.related_incident.id
        : selectedReportForClose.related_incident;

      if (!incidentId) {
        throw new Error("No hay incidencia relacionada para cerrar");
      }

      // If there's a file, upload it first as an attachment
      let attachmentPath = '';
      if (closureData.closure_attachment) {
        const formData = new FormData();
        formData.append('file', closureData.closure_attachment);
        formData.append('title', `Cierre: ${closureData.closure_attachment.name}`);
        formData.append('description', 'Archivo adjunto de cierre de incidencia');
        formData.append('is_public', 'false');

        try {
          const uploadResponse = await incidentsAPI.uploadAttachment(incidentId, formData);
          attachmentPath = uploadResponse.data?.filename || closureData.closure_attachment.name;
        } catch (uploadErr) {
          console.warn('Failed to upload closure attachment:', uploadErr);
        }
      }

      // Combine Reason + Summary for traceability
      const finalSummary = `[Motivo: ${closureData.reason}] ${closureData.closure_summary}`;

      // Close with JSON data
      await incidentsAPI.close(incidentId, {
        stage: closureData.stage,
        closure_summary: finalSummary,
        closure_attachment: attachmentPath
      });

      // UPDATE REPORT STATUS TO CLOSED
      try {
        // Assuming visitReportsAPI.update exists and supports partial update (PATCH)
        await visitReportsAPI.update(selectedReportForClose.id, { status: 'closed' });
      } catch (statusErr) {
        console.warn('Could not update report status to closed:', statusErr);
      }

      queryClient.invalidateQueries(['visit-reports']);
      queryClient.invalidateQueries(['all-incidents-for-reports']);
      showSuccess('Incidencia y reporte cerrados exitosamente');
    } catch (error) {
      console.error('Error closing incident:', error);
      showError('Error al cerrar la incidencia: ' + (error.response?.data?.error || error.response?.data?.closure_summary?.[0] || error.message));
    } finally {
      setIsClosing(false);
      setShowCloseModal(false);
      setSelectedReportForClose(null);
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

  if (reportsLoading || incidentsLoading) {
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
    <div className="p-4 bg-gradient-to-br from-gray-50 to-blue-50 min-h-screen">
      {/* Header */}
      <div className="mb-8">
        <div className="flex flex-col lg:flex-row lg:justify-between lg:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center">
              <ClipboardDocumentListIcon className="h-6 w-6 mr-3 text-blue-600" />
              Reportes de Visita
            </h1>
            <p className="mt-2 text-gray-600">
              Gestión de reportes de visita técnica para incidencias
            </p>
          </div>
          <div className="flex items-center gap-3 flex-wrap">
            <button
              onClick={handleRefresh}
              className="inline-flex items-center px-4 py-2.5 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 shadow-sm"
              title="Actualizar"
            >
              <ArrowPathIcon className="h-5 w-5 text-gray-600" />
            </button>
            <button
              onClick={() => { setSelectedIncidentId(''); setShowUploadModal(true); }}
              className="inline-flex items-center px-5 py-2.5 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-xl hover:from-green-600 hover:to-green-700 shadow-lg"
            >
              <DocumentArrowUpIcon className="h-5 w-5 mr-2" />
              Adjuntar PDF
            </button>
            <button
              onClick={() => { setSelectedIncidentId(''); setShowCreateModal(true); }}
              className="inline-flex items-center px-5 py-2.5 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl hover:from-blue-600 hover:to-blue-700 shadow-lg"
            >
              <PlusIcon className="h-5 w-5 mr-2" />
              Crear Reporte
            </button>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl p-3 sm:p-4 text-white shadow-lg hover-scale animate-stagger-in">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-xs sm:text-sm font-medium">Total Reportes</p>
              <p className="text-xl sm:text-2xl font-bold mt-1">{stats.total}</p>
            </div>
            <div className="p-2 bg-white/20 rounded-lg">
              <ClipboardDocumentListIcon className="h-5 w-5 sm:h-6 sm:w-6" />
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-2xl p-3 sm:p-4 text-white shadow-lg hover-scale animate-stagger-in" style={{ animationDelay: '0.1s' }}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-xs sm:text-sm font-medium">Completados</p>
              <p className="text-xl sm:text-2xl font-bold mt-1">{stats.completed}</p>
            </div>
            <div className="p-2 bg-white/20 rounded-lg">
              <CheckCircleIcon className="h-5 w-5 sm:h-6 sm:w-6" />
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl p-3 sm:p-4 text-white shadow-lg hover-scale animate-stagger-in" style={{ animationDelay: '0.2s' }}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-xs sm:text-sm font-medium">En Laboratorio</p>
              <p className="text-xl sm:text-2xl font-bold mt-1">{stats.in_lab}</p>
            </div>
            <div className="p-2 bg-white/20 rounded-lg">
              <ExclamationTriangleIcon className="h-5 w-5 sm:h-6 sm:w-6" />
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl p-3 sm:p-4 text-white shadow-lg hover-scale animate-stagger-in" style={{ animationDelay: '0.3s' }}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100 text-xs sm:text-sm font-medium">Inc. Pendientes</p>
              <p className="text-xl sm:text-2xl font-bold mt-1">{stats.pending_incidents}</p>
            </div>
            <div className="p-2 bg-white/20 rounded-lg">
              <CalendarDaysIcon className="h-5 w-5 sm:h-6 sm:w-6" />
            </div>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar por número de orden, cliente, proyecto..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              className="p-2 text-gray-400 hover:text-gray-600"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          )}
        </div>
      </div>

      {/* Reports Table */}
      <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white flex items-center">
              <DocumentTextIcon className="h-5 w-5 mr-2" />
              Reportes Generados
            </h2>
            <span className="bg-white/20 text-white px-3 py-1 rounded-full text-sm font-medium">
              {filteredReports.length} reportes
            </span>
          </div>
        </div>

        {filteredReports.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Reporte
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Incidencia
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Cliente / Proyecto
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Fecha Visita
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Estado
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Documento
                  </th>
                  <th className="px-4 py-2 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredReports.map((report) => (
                  <tr key={report.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-2 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-blue-100 to-indigo-100 flex items-center justify-center">
                          <ClipboardDocumentListIcon className="h-5 w-5 text-blue-600" />
                        </div>
                        <div className="ml-3">
                          <p className="text-sm font-semibold text-gray-900">
                            {report.order_number || `REP-${report.id}`}
                          </p>
                          <p className="text-xs text-gray-500">
                            ID: {report.id}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-2 whitespace-nowrap">
                      <p className="text-sm font-medium text-blue-600">
                        {report.incident_code || (typeof report.related_incident === 'object' ? report.related_incident?.code : '-')}
                      </p>
                    </td>
                    <td className="px-4 py-2">
                      <p className="text-sm font-medium text-gray-900">{report.client_name || '-'}</p>
                      <p className="text-xs text-gray-500">{report.project_name || '-'}</p>
                    </td>
                    <td className="px-4 py-2 whitespace-nowrap">
                      <div className="flex items-center text-sm text-gray-600">
                        <CalendarIcon className="h-4 w-4 mr-1.5 text-gray-400" />
                        {report.visit_date ? new Date(report.visit_date).toLocaleDateString('es-ES') : '-'}
                      </div>
                    </td>
                    <td className="px-4 py-2 whitespace-nowrap">
                      {getStatusBadge(report)}
                    </td>
                    <td className="px-4 py-2 whitespace-nowrap">
                      {(report.pdf_path || report.download_url) ? (
                        <span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded bg-green-50 text-green-700">
                          <PaperClipIcon className="h-3.5 w-3.5 mr-1" />
                          PDF
                        </span>
                      ) : (
                        <span className="text-xs text-gray-400">Sin documento</span>
                      )}
                      {report.attachment_count > 0 && (
                        <span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded bg-purple-50 text-purple-700 ml-1">
                          <PhotoIcon className="h-3.5 w-3.5 mr-1" />
                          {report.attachment_count}
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-2 whitespace-nowrap">
                      <div className="flex items-center justify-center gap-1">
                        <button
                          onClick={() => handleOpenDocument(report)}
                          className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                          title="Ver documento PDF"
                        >
                          <EyeIcon className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => report.attachment_count > 0 ? handleViewImages(report) : handleUploadImages(report.id)}
                          className={`p-1.5 rounded-lg transition-colors ${report.attachment_count > 0 ? 'text-purple-600 hover:bg-purple-50' : 'text-gray-400 hover:bg-gray-50'}`}
                          title={report.attachment_count > 0 ? `Ver ${report.attachment_count} imagen(es)` : 'Agregar imágenes'}
                          disabled={isUploading}
                        >
                          <PhotoIcon className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleEscalateToQuality(report)}
                          disabled={report.status === 'closed' || report.related_incident?.estado === 'cerrado' || report.escalated_to_quality || report.related_incident?.escalated_to_quality}
                          className={`p-1.5 rounded-lg transition-colors ${(report.status === 'closed' || report.related_incident?.estado === 'cerrado' || report.escalated_to_quality || report.related_incident?.escalated_to_quality)
                            ? 'text-gray-400 cursor-not-allowed opacity-50'
                            : 'text-orange-600 hover:bg-orange-50'
                            }`}
                          title={(report.status === 'closed' || report.related_incident?.estado === 'cerrado') ? "No se puede escalar: Incidencia Cerrada" :
                            (report.escalated_to_quality || report.related_incident?.escalated_to_quality) ? "Ya escalado a Calidad" : "Escalar a Calidad"}
                        >
                          <ArrowUpIcon className="h-4 w-4" />
                        </button>
                        {report.related_incident && (
                          <button
                            onClick={() => openCloseModal(report)}
                            className={`p-1.5 rounded-lg transition-colors ${(report.status === 'closed' || report.related_incident?.estado === 'cerrado' || report.escalated_to_quality || report.related_incident?.escalated_to_quality)
                              ? 'text-gray-400 cursor-not-allowed opacity-50'
                              : 'text-green-600 hover:bg-green-50'
                              }`}
                            disabled={report.status === 'closed' || report.related_incident?.estado === 'cerrado' || report.escalated_to_quality || report.related_incident?.escalated_to_quality}
                            title={
                              (report.status === 'closed' || report.related_incident?.estado === 'cerrado')
                                ? "Incidencia ya cerrada"
                                : (report.escalated_to_quality || report.related_incident?.escalated_to_quality)
                                  ? "Incidencia escalada a Calidad (Gestionar allá)"
                                  : "Cerrar Incidencia"
                            }
                          >
                            <CheckCircleIcon className="h-4 w-4" />
                          </button>
                        )}
                        <button
                          onClick={() => handleDeleteReport(report.id)}
                          className="p-1.5 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          title="Eliminar"
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

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-8 flex items-center justify-between bg-white px-6 py-4 rounded-2xl shadow-sm border border-gray-100">
          <div className="flex-1 flex justify-between sm:hidden">
            <button
              onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
              className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              Anterior
            </button>
            <button
              onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
              disabled={currentPage === totalPages}
              className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              Siguiente
            </button>
          </div>
          <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-gray-700">
                Mostrando <span className="font-medium">{(currentPage - 1) * pageSize + 1}</span> a{' '}
                <span className="font-medium">{Math.min(currentPage * pageSize, totalCount)}</span> de{' '}
                <span className="font-medium">{totalCount}</span> resultados
              </p>
            </div>
            <div className="flex items-center gap-4">
              <select
                value={pageSize}
                onChange={(e) => {
                  setPageSize(Number(e.target.value));
                  setCurrentPage(1);
                }}
                className="px-3 py-2 bg-white border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all font-medium text-gray-600"
              >
                <option value={10}>10 por página</option>
                <option value={20}>20 por página</option>
                <option value={50}>50 por página</option>
              </select>

              <nav className="relative z-0 inline-flex rounded-lg shadow-sm -space-x-px" aria-label="Pagination">
                <button
                  onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                  disabled={currentPage === 1}
                  className="relative inline-flex items-center px-2 py-2 rounded-l-lg border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                >
                  <span className="sr-only">Anterior</span>
                  <ChevronLeftIcon className="h-5 w-5" aria-hidden="true" />
                </button>
                {[...Array(totalPages)].map((_, i) => {
                  const pageNum = i + 1;
                  // Mostrar solo algunas páginas si hay demasiadas
                  if (
                    totalPages > 7 &&
                    pageNum !== 1 &&
                    pageNum !== totalPages &&
                    Math.abs(pageNum - currentPage) > 1
                  ) {
                    if (pageNum === 2 || pageNum === totalPages - 1) {
                      return <span key={pageNum} className="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700">...</span>;
                    }
                    return null;
                  }
                  return (
                    <button
                      key={pageNum}
                      onClick={() => setCurrentPage(pageNum)}
                      className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${currentPage === pageNum
                        ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                        : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                        }`}
                    >
                      {pageNum}
                    </button>
                  );
                })}
                <button
                  onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                  disabled={currentPage === totalPages}
                  className="relative inline-flex items-center px-2 py-2 rounded-r-lg border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                >
                  <span className="sr-only">Siguiente</span>
                  <ChevronRightIcon className="h-5 w-5" aria-hidden="true" />
                </button>
              </nav>
            </div>
          </div>
        </div>
      )}

      {/* Modal Crear Reporte */}
      {showCreateModal && (
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
              {availableIncidents.length === 0 ? (
                <div className="text-center py-8">
                  <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-yellow-500" />
                  <p className="mt-4 text-gray-600">
                    No hay incidencias disponibles para crear reporte.
                  </p>
                  <p className="mt-2 text-sm text-gray-500">
                    Todas las incidencias abiertas ya tienen un reporte de visita.
                  </p>
                </div>
              ) : (
                <>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Seleccionar Incidencia
                  </label>
                  <p className="text-xs text-gray-500 mb-3">
                    Solo se muestran incidencias abiertas sin reporte de visita
                  </p>
                  <select
                    value={selectedIncidentId}
                    onChange={(e) => setSelectedIncidentId(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">-- Seleccionar incidencia --</option>
                    {availableIncidents.map((incident) => (
                      <option key={incident.id} value={incident.id}>
                        {incident.code} - {incident.cliente} ({incident.provider || 'Sin proveedor'})
                      </option>
                    ))}
                  </select>
                </>
              )}

              <div className="flex justify-end gap-3 mt-6 pt-4 border-t">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2.5 text-gray-700 bg-gray-100 rounded-xl hover:bg-gray-200 font-medium"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleCreateReport}
                  disabled={!selectedIncidentId || availableIncidents.length === 0}
                  className="px-6 py-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                >
                  Continuar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}



      {/* Escalation Modal */}
      {showEscalationModal && selectedReportForEscalation && (
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
      )}

      {/* Modal Subir Documento */}
      {showUploadModal && (
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
              {availableIncidents.length === 0 ? (
                <div className="text-center py-8">
                  <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-yellow-500" />
                  <p className="mt-4 text-gray-600">
                    No hay incidencias disponibles.
                  </p>
                </div>
              ) : (
                <>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Seleccionar Incidencia
                  </label>
                  <select
                    value={selectedIncidentId}
                    onChange={(e) => setSelectedIncidentId(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-green-500"
                  >
                    <option value="">-- Seleccionar incidencia --</option>
                    {availableIncidents.map((incident) => (
                      <option key={incident.id} value={incident.id}>
                        {incident.code} - {incident.cliente}
                      </option>
                    ))}
                  </select>

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
              )}

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
      )}

      {/* Modal Ver Imágenes */}
      {showImagesModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl overflow-hidden max-h-[90vh]">
            <div className="px-6 py-4 bg-gradient-to-r from-purple-600 to-purple-700">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white flex items-center">
                  <PhotoIcon className="h-5 w-5 mr-2" />
                  Imágenes del Reporte - {selectedReportForImages?.order_number}
                </h3>
                <button onClick={() => setShowImagesModal(false)} className="text-white/80 hover:text-white">
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
            </div>
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
              {reportImages.length === 0 ? (
                <div className="text-center py-12">
                  <PhotoIcon className="h-16 w-16 mx-auto text-gray-300 mb-4" />
                  <p className="text-gray-500">No hay imágenes adjuntas</p>
                  <button
                    onClick={() => {
                      setShowImagesModal(false);
                      handleUploadImages(selectedReportForImages?.id);
                    }}
                    className="mt-4 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                  >
                    Agregar Imágenes
                  </button>
                </div>
              ) : (
                <>
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                    {reportImages.map((image, index) => (
                      <div
                        key={image.id}
                        className="relative group cursor-pointer rounded-lg overflow-hidden border border-gray-200 hover:border-purple-400 transition-colors"
                        onClick={() => handleViewImage(image)}
                      >
                        <div className="aspect-square bg-gray-100 flex items-center justify-center">
                          <PhotoIcon className="h-12 w-12 text-gray-400" />
                        </div>
                        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-colors flex items-center justify-center">
                          <EyeIcon className="h-8 w-8 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
                        </div>
                        <div className="absolute bottom-0 left-0 right-0 bg-black/60 text-white text-xs p-2 truncate">
                          {image.filename || `Imagen ${index + 1}`}
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="mt-6 pt-4 border-t flex justify-between items-center">
                    <span className="text-sm text-gray-500">{reportImages.length} imagen(es)</span>
                    <button
                      onClick={() => {
                        setShowImagesModal(false);
                        handleUploadImages(selectedReportForImages?.id);
                      }}
                      className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                    >
                      Agregar más imágenes
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Escalation Modal */}
      {showEscalationModal && selectedReportForEscalation && (
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
      )}

      {/* Close Incident Modal - Diálogo Obligatorio (igual que en Incidents.jsx) */}
      {showCloseModal && selectedReportForClose && (
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
                      Cerrar Incidencia Asociada
                    </h3>
                    <div className="mt-2">
                      <p className="text-sm text-gray-500 mb-4">
                        Estás cerrando la incidencia asociada al reporte <b>{selectedReportForClose.order_number}</b>.
                        Esta acción es definitiva.
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
                      <option value="incidencia">Cerrada en Incidencia</option>
                      <option value="reporte_visita">Cerrada en Reporte de Visita</option>
                      <option value="calidad">Cerrada en Calidad</option>
                      <option value="proveedor">Cerrada en Proveedor</option>
                    </select>
                  </div>

                  {/* Motivo de Cierre (Restaurado) */}
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
                      Resumen de Acciones, Conclusiones y Decisiones <span className="text-red-500">*</span>
                    </label>
                    <textarea
                      value={closureData.closure_summary}
                      onChange={(e) => setClosureData({ ...closureData, closure_summary: e.target.value })}
                      rows={5}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors"
                      placeholder="Describa las acciones tomadas, conclusiones alcanzadas y decisiones finales sobre esta incidencia (mínimo 10 caracteres)..."
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
                        id="closure-file-visit"
                        className="hidden"
                        onChange={(e) => setClosureData({ ...closureData, closure_attachment: e.target.files[0] || null })}
                        accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.txt"
                      />
                      <label
                        htmlFor="closure-file-visit"
                        className="px-4 py-2 bg-gray-100 text-gray-700 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-200 transition-colors"
                      >
                        Seleccionar Archivo
                      </label>
                      {closureData.closure_attachment && (
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                          <span className="font-medium">{closureData.closure_attachment.name}</span>
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
                    onClick={handleConfirmClose}
                    disabled={isClosing || closureData.closure_summary.length < 10}
                    className={`px-6 py-3 rounded-lg font-medium transition-colors flex items-center ${closureData.closure_summary.length < 10
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

export default VisitReportsPage;