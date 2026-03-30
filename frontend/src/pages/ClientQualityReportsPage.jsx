import React, { useState, useEffect, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useLocation } from 'react-router-dom';
import { api, incidentsAPI, qualityReportsAPI, aiAPI } from '../services/api';
import {
  PlusIcon,
  EyeIcon,
  TrashIcon,
  XMarkIcon,
  CheckCircleIcon,
  MagnifyingGlassIcon,
  CalendarIcon,
  UserIcon,
  BuildingOfficeIcon,
  BeakerIcon,
  FunnelIcon,
  ArrowUpIcon,
  PaperClipIcon,
  CloudArrowUpIcon,
  ExclamationTriangleIcon,
  DocumentTextIcon,
  ArrowPathIcon,
  EnvelopeIcon,
  PaperAirplaneIcon,
  DocumentChartBarIcon,
  ClockIcon,
  ArrowTopRightOnSquareIcon
} from '@heroicons/react/24/outline';

import IncidentDocuments from '../components/IncidentDocuments';
import IncidentClosureForm from '../components/IncidentClosureForm';
import { openDocument, downloadDocument } from '../utils/documentUtils';
import { useNotifications } from '../hooks/useNotifications';

const ClientQualityReportsPage = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const location = useLocation();

  // Estados principales
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showSelectionModal, setShowSelectionModal] = useState(false); // New state for selection flow
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showIncidentClosure, setShowIncidentClosure] = useState(false);

  const [selectedIncidentId, setSelectedIncidentId] = useState('');
  const [selectedIncidentForClosure, setSelectedIncidentForClosure] = useState(null);

  const [searchTerm, setSearchTerm] = useState('');
  const [uploadedDocuments, setUploadedDocuments] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);
  const [emailData, setEmailData] = useState({
    to: '',
    subject: '',
    message: ''
  });

  // Estado para el modal de cierre estandarizado
  const [closureData, setClosureData] = useState({
    stage: 'calidad',
    reason: '',
    closure_summary: '',
    closure_attachment: null
  });
  const [isGeneratingAI, setIsGeneratingAI] = useState(false);

  const handleGenerateAIClosure = async () => {
    if (!selectedIncidentForClosure || !closureData.stage) {
      alert('Por favor selecciona una etapa de cierre primero.');
      return;
    }

    setIsGeneratingAI(true);
    try {
      const response = await aiAPI.analyzeClosure({
        incident_id: selectedIncidentForClosure.id,
        stage: closureData.stage
      });

      if (response.data && response.data.analysis) {
        setClosureData(prev => ({
          ...prev,
          closure_summary: response.data.analysis
        }));
      }
    } catch (error) {
      console.error('Error generating AI closure:', error);
      alert('Error al generar la conclusión con IA. Por favor intenta manualmente.');
    } finally {
      setIsGeneratingAI(false);
    }
  };

  // Scroll to top on page mount
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  // Query para obtener reportes de calidad para cliente con datos de incidencia
  const { data: reports, isLoading: reportsLoading } = useQuery({
    queryKey: ['quality-reports', { report_type: 'cliente', search: searchTerm }],
    queryFn: async () => {
      const response = await api.get('/documents/quality-reports/', {
        params: {
          report_type: 'cliente',
          include_incident_data: true,
          expand: 'incident',
          search: searchTerm
        }
      });
      return response.data;
    },
    keepPreviousData: true // Mantener datos previos mientras carga para evitar parpadeo
  });

  // Query para obtener incidencias escaladas a calidad
  const { data: openIncidents, isLoading: incidentsLoading } = useQuery({
    queryKey: ['escalatedIncidents'],
    queryFn: async () => {
      const response = await api.get('/incidents/escalated/', {
        params: {
          // fetch all escalated, filter locally
          report_type: 'cliente'
        }
      });
      return response.data;
    }
  });

  // Filtrar incidencias disponibles (que no tengan reporte aún)
  const availableIncidents = useMemo(() => {
    if (!openIncidents?.results && !openIncidents?.incidents) return [];

    // Lista base de incidencias
    const rawIncidents = openIncidents.results || openIncidents.incidents || [];

    // IDs de incidencias que YA tienen reporte en la lista actual
    const incidentsWithReports = new Set(reports?.results?.map(r => r.incident_id || r.incident?.id).filter(Boolean));

    // Filtrar: Solo mostrar si NO tiene reporte
    return rawIncidents.filter(inc => !incidentsWithReports.has(inc.id));
  }, [openIncidents, reports]);

  // Filtrar reportes para la tabla
  // Filtrar reportes para la tabla (Ahora Server-Side)
  const filteredReports = useMemo(() => {
    return reports?.results || [];
  }, [reports?.results]);

  // Handlers
  const handleCreateReportClick = () => {
    setShowSelectionModal(true);
  };

  const handleIncidentSelectForCreate = (incidentId) => {
    setSelectedIncidentId(incidentId);
    setShowSelectionModal(false);
    navigate(`/quality-report-form/${incidentId}`);
  };

  // Handlers for report actions
  const handleOpenDocument = async (report) => {
    try {
      const url = `/documents/quality-reports/${report.id}/download/`;
      const response = await api.get(url, { responseType: 'blob' });
      const file = new Blob([response.data], { type: 'application/pdf' });
      const fileURL = URL.createObjectURL(file);
      window.open(fileURL, '_blank');
    } catch (error) {
      console.error('Error opening document:', error);
      alert('Error al visualizar el documento. Verifique permisos o disponibilidad.');
    }
  };



  const handleEscalateToInternal = async (report) => {
    const incidentId = report.incident_id || report.incident?.id;
    if (!incidentId) {
      alert('No se encontró la incidencia asociada.');
      return;
    }

    if (confirm(`¿Estás seguro de escalar este reporte a Calidad Interna? Solamente se habilitará en el sistema.`)) {
      try {
        // 1. Update Incident to allow internal report creation
        await incidentsAPI.update(incidentId, { escalated_to_internal_quality: true });

        // 2. Update Report Status to 'escalated'
        await api.patch(`/documents/quality-reports/${report.id}/`, { status: 'escalated' });

        alert('Reporte escalado a Calidad Interna correctamente.');
        queryClient.invalidateQueries(['quality-reports']);
      } catch (error) {
        console.error('Error escalando:', error);
        alert('Error al escalar el reporte.');
      }
    }
  };

  const handleEscalateToSupplier = async (incident) => {
    if (!incident || !incident.id) {
      alert('Incidencia no válida');
      return;
    }
    if (confirm(`¿Desea escalar la incidencia ${incident.code} a proveedor?`)) {
      try {
        await api.post(`/incidents/${incident.id}/escalate/supplier/`);
        alert('Incidencia escalada a proveedor');
        queryClient.invalidateQueries(['quality-reports']);
        queryClient.invalidateQueries(['escalatedIncidents']);
      } catch (error) {
        console.error(error);
        alert('Error al escalar incidencia');
      }
    }
  };

  const handleDeleteReport = async (reportId) => {
    if (confirm('¿Estás seguro de que deseas eliminar este reporte?')) {
      try {
        await qualityReportsAPI.delete(reportId);
        queryClient.invalidateQueries(['quality-reports']);
        alert('Reporte eliminado correctamente');
      } catch (error) {
        console.error('Error deleting report:', error);
        alert('Error al eliminar el reporte');
      }
    }
  };

  // Helper function for secure download
  const handleDownloadQualityReport = async (reportId, filename) => {
    try {
      const response = await api.get(`/documents/quality-reports/${reportId}/download/`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename || `Reporte_Calidad_${reportId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      return true;
    } catch (error) {
      console.error('Error downloading quality report:', error);
      alert('No se pudo descargar el reporte automáticamente. Por favor inténtelo desde la tabla.');
      return false;
    }
  };

  const handleIncidentClosure = async (formData) => {
    if (!selectedIncidentForClosure) return;
    setIsSubmitting(true);
    try {
      const payload = new FormData();
      payload.append('stage', formData.stage);
      payload.append('closure_summary', formData.closure_summary);
      if (formData.closure_attachment) {
        payload.append('closure_attachment', formData.closure_attachment);
      }

      await incidentsAPI.close(selectedIncidentForClosure.id, payload);
      alert('Incidencia cerrada exitosamente');
      setShowIncidentClosure(false);
      queryClient.invalidateQueries(['quality-reports']);
      queryClient.invalidateQueries(['escalatedIncidents']);
    } catch (error) {
      alert('Error al cerrar: ' + (error.response?.data?.error || error.message));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOpenEmailModal = (report) => {
    setSelectedReport(report);

    // Recuperar correo guardado del cliente
    const clientName = report.incident?.cliente || report.cliente;
    let savedEmail = report.client_email || '';

    if (!savedEmail && clientName) {
      try {
        const clientEmails = JSON.parse(localStorage.getItem('client_emails') || '{}');
        savedEmail = clientEmails[clientName] || '';
      } catch (e) {
        console.warn('Error reading client emails from local storage', e);
      }
    }

    // Template profesional SIN enlaces (cliente no tiene acceso)
    const professionalBody = `Estimado Cliente ${clientName || ''},

Esperamos que se encuentre muy bien.

Adjunto a este correo encontrará el Reporte de Calidad N° ${report.report_number || report.id} correspondiente a su proyecto ${report.incident?.obra || report.obra || 'Sin Nombre'}.

Este documento contiene:
• Detalle completo de la incidencia reportada
• Análisis técnico y evaluación
• Resultados de ensayos de laboratorio (si aplica)
• Especificaciones y normativas aplicables
• Conclusiones y recomendaciones

El informe ha sido elaborado por nuestro equipo técnico de Control de Calidad y Postventa, garantizando la trazabilidad y transparencia del proceso.

Si tiene alguna consulta o requiere información adicional sobre este reporte, no dude en contactarnos.

Atentamente,

Departamento de Control de Calidad
POLIFUSION S.A.`;

    setEmailData({
      to: savedEmail,
      subject: `Reporte de Calidad N° ${report.report_number || report.id} - Proyecto ${report.incident?.obra || report.obra || 'Sin Nombre'}`,
      message: professionalBody
    });
    setShowEmailModal(true);
  };

  const handleSendEmail = async () => {
    if (!selectedReport) return;

    // Validación de email
    if (!emailData.to) {
      alert('Por favor ingresa el correo del cliente');
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(emailData.to)) {
      alert('Por favor ingresa un correo electrónico válido');
      return;
    }

    setIsSubmitting(true);

    try {
      // 1. Guardar email del cliente
      const clientName = selectedReport.incident?.cliente || selectedReport.cliente;
      if (clientName && emailData.to) {
        try {
          const clientEmails = JSON.parse(localStorage.getItem('client_emails') || '{}');
          clientEmails[clientName] = emailData.to;
          localStorage.setItem('client_emails', JSON.stringify(clientEmails));
        } catch (e) {
          console.warn('Error saving client email', e);
        }
      }

      // 2. Descargar PDF de forma segura
      const downloadSuccess = await handleDownloadQualityReport(
        selectedReport.id,
        `Reporte_Calidad_${selectedReport.report_number}.pdf`
      );

      if (!downloadSuccess) {
        setIsSubmitting(false);
        return;
      }

      // 3. Abrir Outlook con mensaje profesional
      const mailtoLink = `mailto:${emailData.to}?subject=${encodeURIComponent(emailData.subject)}&body=${encodeURIComponent(emailData.message)}`;

      setTimeout(() => {
        window.location.href = mailtoLink;
      }, 800);

      // 4. Registrar en backend (Log Only)
      await api.post(`/documents/quality-reports/${selectedReport.id}/send-email/`, {
        to: emailData.to,
        action: 'log_only'
      });

      alert('Abriendo Outlook... Por favor ADJUNTA el reporte descargado.');

      setShowEmailModal(false);
      setEmailData({ to: '', subject: '', message: '' });
      queryClient.invalidateQueries(['quality-reports']);

    } catch (error) {
      console.error('Error in email flow:', error);
      alert('Se abrió el correo pero falló el registro en el sistema.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUploadDocument = async () => {
    if (!selectedIncidentId || !uploadedDocuments[selectedIncidentId]) {
      // Logic for single file upload from modal
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
        formData.append('report_type', 'cliente');

        try {
          await api.post('/documents/upload/quality-report/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          });
          alert('Documento subido exitosamente');
          setShowUploadModal(false);
          queryClient.invalidateQueries(['quality-reports']);
          setIsSubmitting(false);
        } catch (error) {
          console.error(error);
          alert('Error al subir documento');
          setIsSubmitting(false);
        }
      };
      fileInput.click();
    } else {
      // Logic for dragged file in modal
      setIsSubmitting(true);
      const formData = new FormData();
      formData.append('file', uploadedDocuments[selectedIncidentId]);
      formData.append('incident_id', selectedIncidentId);
      formData.append('report_type', 'cliente');

      try {
        await api.post('/documents/upload/quality-report/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        alert('Documento subido exitosamente');
        setShowUploadModal(false);
        setUploadedDocuments(prev => {
          const newState = { ...prev };
          delete newState[selectedIncidentId];
          return newState;
        });
        queryClient.invalidateQueries(['quality-reports']);
        setIsSubmitting(false);
      } catch (error) {
        console.error(error);
        alert('Error al subir documento');
        setIsSubmitting(false);
      }
    }
  };

  if (reportsLoading || incidentsLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="scroll-container-sticky">
      <div className="scroll-content-wrapper">
        <div className="w-full px-4 sm:px-6 lg:px-8 space-y-6 py-8">

          {/* Compact Professional Header Section */}
          <div className="relative mb-6 p-4 rounded-2xl bg-gradient-to-br from-slate-50 to-white border border-slate-200 shadow-sm overflow-hidden group flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-blue-500/5 to-cyan-500/5 rounded-full blur-3xl -mr-16 -mt-16 pointer-events-none"></div>

            <div className="flex items-center gap-4 relative z-10">
              <div className="p-2.5 bg-gradient-to-br from-blue-600 to-cyan-600 rounded-xl shadow-md shadow-blue-500/20 group-hover:scale-105 transition-transform duration-500">
                <BeakerIcon className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-800 tracking-tight flex items-center gap-2">
                  Reportes de Clientes
                  <span className="px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 text-[10px] font-bold uppercase tracking-wider border border-blue-100">
                    Control de Calidad
                  </span>
                </h1>
                <p className="text-xs text-slate-500 font-medium mt-0.5">
                  Gestión detallada de informes externos y auditorías
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3 relative z-10">
              <button
                onClick={() => setShowUploadModal(true)}
                className="px-6 py-4 bg-white hover:bg-slate-50 text-slate-600 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all flex items-center gap-3 border border-slate-200 shadow-sm"
              >
                <ArrowUpIcon className="h-5 w-5 text-slate-400" />
                SUBIR REPORTE
              </button>
              <button
                onClick={handleCreateReportClick}
                className="px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-2xl text-[10px] font-black uppercase tracking-widest shadow-xl shadow-blue-200 transition-all flex items-center gap-3"
              >
                <PlusIcon className="h-5 w-5 text-blue-200" />
                NUEVO REPORTE
              </button>
            </div>
          </div>

          {/* Filter Section - Minimalist Glass */}
          <div className="bg-white/40 backdrop-blur-md rounded-2xl p-1.5 mb-8 shadow-sm border border-white/50">
            <div className="flex flex-col md:flex-row items-center justify-between gap-4 p-2">
              <div className="relative w-full md:max-w-md group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <MagnifyingGlassIcon className="h-5 w-5 text-gray-400 group-focus-within:text-blue-600 transition-colors" />
                </div>
                <input
                  type="text"
                  className="block w-full pl-10 pr-3 py-2.5 bg-white/60 backdrop-blur-sm border-transparent text-gray-900 placeholder-gray-500 focus:outline-none focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-transparent rounded-xl transition-all duration-200 shadow-sm font-medium"
                  placeholder="Buscar por cliente, obra o N° reporte..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              {searchTerm && (
                <button
                  onClick={() => setSearchTerm('')}
                  className="flex-shrink-0 px-4 py-2 bg-red-50 text-red-600 rounded-xl hover:bg-red-100 transition-colors text-sm font-bold border border-red-100/50"
                >
                  Limpiar búsqueda
                </button>
              )}
            </div>
          </div>



          {/* Reports Table - Modern Glass */}
          <div className="bg-white/60 backdrop-blur-2xl rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-white/60 overflow-hidden">
            {filteredReports.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-20 px-4 text-center">
                <div className="bg-gray-50/50 backdrop-blur-sm p-6 rounded-full mb-4">
                  <DocumentTextIcon className="h-10 w-10 text-gray-400" />
                </div>
                <h3 className="text-lg font-bold text-gray-800">No hay reportes</h3>
                <p className="text-gray-500 mt-1 text-sm">No se encontraron documentos.</p>
              </div>
            ) : (
              <div className="overflow-x-visible scroll-horizontal-sticky">
                <table className="min-w-full">
                  <thead>
                    <tr className="bg-slate-50/50 border-b border-slate-200">
                      <th className="px-6 py-4 text-[11px] font-black text-slate-400 uppercase tracking-widest">N° Reporte</th>
                      <th className="px-6 py-4 text-[11px] font-black text-slate-400 uppercase tracking-widest">Incidencia</th>
                      <th className="px-6 py-4 text-[11px] font-black text-slate-400 uppercase tracking-widest">Cliente / Obra</th>
                      <th className="px-6 py-4 text-[11px] font-black text-slate-400 uppercase tracking-widest">Fecha</th>
                      <th className="px-6 py-4 text-[11px] font-black text-slate-400 uppercase tracking-widest">Estado</th>
                      <th className="px-6 py-4 text-[11px] font-black text-slate-400 uppercase tracking-widest text-right">Gestión</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100/50">
                    {filteredReports.map((report) => (
                      <tr key={report.id} className="group hover:bg-white/60 transition-colors duration-150">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="flex-shrink-0 h-9 w-9 bg-blue-50 rounded-lg flex items-center justify-center text-blue-600 mr-3 shadow-sm border border-blue-100">
                              <DocumentTextIcon className="h-5 w-5" />
                            </div>
                            <div>
                              <div className="text-sm font-bold text-gray-900 bg-clip-text bg-gradient-to-r from-gray-900 to-gray-700">{report.report_number || 'S/N'}</div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="px-2.5 py-1 text-xs font-bold text-gray-600 bg-gray-100/80 rounded-lg border border-gray-200 backdrop-blur-sm">
                            {report.incident_code || report.incident?.code || '-'}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm font-semibold text-gray-900">{report.cliente}</div>
                          <div className="text-xs text-gray-500 font-medium">{report.obra}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-medium">
                          {new Date(report.created_at).toLocaleDateString('es-CL')}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {(() => {
                            const incidentStatus = report.incident?.estado;
                            const status = report.status || 'draft';

                            // Check for closed incident FIRST
                            // Check for closed incident FIRST
                            if (incidentStatus === 'cerrado') {
                              return (
                                <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-black uppercase tracking-tight border bg-slate-100 text-slate-600 border-slate-200">
                                  <CheckCircleIcon className="w-3.5 h-3.5 mr-1.5" />
                                  CERRADO
                                </span>
                              );
                            }

                            const styles = {
                              final: 'bg-slate-100 text-slate-600 border-slate-200', // Cerrado
                              draft: 'bg-emerald-50 text-emerald-700 border-emerald-100', // Listo
                              pending: 'bg-emerald-50 text-emerald-700 border-emerald-100', // Listo (alias)
                              sent: 'bg-blue-50 text-blue-700 border-blue-100', // Enviado
                              escalated: 'bg-purple-50 text-purple-700 border-purple-100' // Escalado
                            };
                            const labels = {
                              final: 'CERRADO',
                              draft: 'LISTO',
                              pending: 'LISTO',
                              sent: 'ENVIADO',
                              escalated: 'ESCALADO'
                            };
                            return (
                              <span className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-black uppercase tracking-tight border ${styles[status] || styles.draft}`}>
                                {status === 'final' ? <CheckCircleIcon className="w-3.5 h-3.5 mr-1.5" /> :
                                  status === 'sent' ? <PaperAirplaneIcon className="w-3.5 h-3.5 mr-1.5" /> :
                                    status === 'escalated' ? <ArrowTopRightOnSquareIcon className="w-3.5 h-3.5 mr-1.5" /> :
                                      <CheckCircleIcon className="w-3.5 h-3.5 mr-1.5" />}
                                {labels[status] || labels.draft}
                              </span>
                            );
                          })()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                          <div className="flex items-center justify-end gap-3 opacity-80 group-hover:opacity-100 transition-opacity">
                            <button
                              onClick={() => handleOpenDocument(report)}
                              className="w-12 h-12 flex items-center justify-center rounded-2xl bg-blue-50 text-blue-600 hover:bg-blue-600 hover:text-white transition-all shadow-sm"
                              title="Ver PDF"
                            >
                              <EyeIcon className="w-6 h-6" />
                            </button>

                            <button
                              onClick={() => handleOpenEmailModal(report)}
                              className="w-12 h-12 flex items-center justify-center rounded-2xl bg-indigo-50 text-indigo-600 hover:bg-indigo-600 hover:text-white transition-all shadow-sm"
                              title="Enviar Email"
                            >
                              <EnvelopeIcon className="w-6 h-6" />
                            </button>

                            {report.incident?.estado !== 'cerrado' && (
                              <button
                                onClick={() => {
                                  setSelectedIncidentForClosure(report.incident || { id: report.incident_id, code: report.incident_code });
                                  setClosureData({ stage: 'calidad', reason: '', closure_summary: '', closure_attachment: null });
                                  setShowIncidentClosure(true);
                                }}
                                className="w-12 h-12 flex items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600 hover:bg-emerald-600 hover:text-white transition-all shadow-sm"
                                title="Cerrar Incidencia"
                              >
                                <CheckCircleIcon className="w-6 h-6" />
                              </button>
                            )}

                            {report.status !== 'escalated' && report.status !== 'final' && report.incident?.estado !== 'cerrado' && (
                              <button
                                onClick={() => handleEscalateToInternal(report)}
                                className="w-12 h-12 flex items-center justify-center rounded-2xl bg-purple-50 text-purple-600 hover:bg-purple-600 hover:text-white transition-all shadow-sm"
                                title="Escalar a Calidad Interna"
                              >
                                <ArrowTopRightOnSquareIcon className="w-6 h-6" />
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

      {/* Selection Modal for Create Report - Blue Theme */}
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
                    Solo se muestran incidencias escaladas a calidad pendientes.
                  </p>
                </div>

                <label className="block text-sm font-bold text-gray-700 mb-2">Incidencia</label>
                <select
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
                  onChange={(e) => {
                    if (e.target.value) handleIncidentSelectForCreate(e.target.value);
                  }}
                  defaultValue=""
                >
                  <option value="" disabled>Seleccione para continuar...</option>
                  {availableIncidents.map((incident) => (
                    <option key={incident.id} value={incident.id}>
                      {incident.code} — {incident.cliente || 'Sin cliente'}
                    </option>
                  ))}
                </select>

                <div className="mt-6 flex justify-end">
                  <button
                    onClick={() => setShowSelectionModal(false)}
                    className="px-4 py-2 text-gray-600 font-medium hover:bg-gray-100 rounded-lg"
                  >
                    Cancelar
                  </button>
                </div>
              </div>
            </div>
          </div>
        )
      }

      {/* Create Modal - Full Screen */}
      {
        showCreateModal && (
          <QualityReportForm
            isOpen={showCreateModal}
            onClose={() => setShowCreateModal(false)}
            incidentId={selectedIncidentId}
            onSuccess={() => {
              setShowCreateModal(false);
              queryClient.invalidateQueries(['quality-reports']);
              queryClient.invalidateQueries(['escalatedIncidents']);
            }}
            fullScreen={true}
          />
        )
      }

      {/* Upload Modal */}
      {
        showUploadModal && (
          <div className="fixed inset-0 bg-gray-900/60 backdrop-blur-sm overflow-y-auto h-full w-full z-50 flex items-center justify-center">
            <div className="bg-white/90 backdrop-blur-xl rounded-3xl p-8 max-w-md w-full shadow-2xl border border-white/50">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Subir Reporte Externo</h3>
              <div className="mb-4">
                <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">
                  Seleccionar Incidencia
                </label>
                <div className="relative">
                  <select
                    value={selectedIncidentId}
                    onChange={(e) => setSelectedIncidentId(e.target.value)}
                    className="w-full pl-4 pr-10 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 appearance-none font-medium text-gray-700"
                  >
                    <option value="">Selecciona una opción...</option>
                    {availableIncidents.map((incident) => (
                      <option key={incident.id} value={incident.id}>
                        {incident.code} — {incident.cliente || 'Sin cliente'}
                      </option>
                    ))}
                  </select>
                  <div className="absolute inset-y-0 right-0 flex items-center px-3 pointer-events-none text-gray-500">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
                  </div>
                </div>
              </div>

              <p className="text-sm text-gray-500 mb-6">Selecciona o arrastra el archivo PDF del reporte firmado.</p>

              <div className={`border-2 border-dashed border-gray-300 rounded-2xl p-8 text-center transition-all cursor-pointer group ${!selectedIncidentId ? 'opacity-50 cursor-not-allowed' : 'hover:bg-white/50 hover:border-blue-400'}`}
                onClick={() => selectedIncidentId && handleUploadDocument()}
              >
                <CloudArrowUpIcon className="h-12 w-12 text-gray-400 group-hover:text-blue-500 transition-colors mx-auto mb-3" />
                <span className="text-sm font-bold text-blue-600">Click para seleccionar</span>
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

      {
        showEmailModal && (
          <div className="fixed inset-0 bg-gray-900/60 backdrop-blur-sm overflow-y-auto h-full w-full z-50 flex items-center justify-center">
            <div className="bg-white rounded-3xl p-0 max-w-lg w-full shadow-2xl border border-white/40 overflow-hidden">
              <div className="px-6 py-4 bg-gray-50/80 backdrop-blur-sm border-b border-gray-100 flex justify-between items-center">
                <h3 className="text-lg font-bold text-gray-900">Enviar Reporte por Correo</h3>
                <button onClick={() => setShowEmailModal(false)} className="text-gray-400 hover:text-gray-600"><XMarkIcon className="h-6 w-6" /></button>
              </div>
              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Destinatario</label>
                  <input
                    type="email"
                    value={emailData.to}
                    onChange={(e) => setEmailData({ ...emailData, to: e.target.value })}
                    className="w-full px-4 py-2 border border-blue-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none"
                    placeholder="correo@cliente.com"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Asunto</label>
                  <input
                    type="text"
                    value={emailData.subject}
                    onChange={(e) => setEmailData({ ...emailData, subject: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Mensaje</label>
                  <textarea
                    value={emailData.message}
                    onChange={(e) => setEmailData({ ...emailData, message: e.target.value })}
                    rows={6}
                    className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 outline-none text-sm"
                  />
                </div>
                <button
                  onClick={handleSendEmail}
                  className="w-full py-3 bg-blue-600 text-white font-bold rounded-xl hover:bg-blue-700 shadow-lg shadow-blue-500/30 transition-all hover:-translate-y-0.5"
                >
                  Abrir Correo
                </button>
              </div>
            </div>
          </div>
        )
      }

      {/* Standardized Close Incident Modal */}
      {showIncidentClosure && selectedIncidentForClosure && (
        <IncidentClosureForm
          incident={selectedIncidentForClosure}
          onCancel={() => setShowIncidentClosure(false)}
          onSubmit={handleIncidentClosure}
          isClosing={isSubmitting}
          defaultStage="calidad"
        />
      )}

      {/* Email Modal - Professional Outlook Workflow */}
      {showEmailModal && selectedReport && (
        <div className="fixed inset-0 bg-gray-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl shadow-2xl w-full max-w-lg overflow-hidden border border-white/40">
            {/* Header */}
            <div className="px-6 py-4 bg-gray-50/80 backdrop-blur-md border-b border-gray-100 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <PaperAirplaneIcon className="h-5 w-5 text-blue-600" />
                </div>
                <h3 className="text-lg font-bold text-gray-900">Enviar Reporte al Cliente</h3>
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
                  Correo del Cliente
                </label>
                <input
                  type="email"
                  value={emailData.to}
                  onChange={(e) => setEmailData({ ...emailData, to: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-lg text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                  placeholder="cliente@ejemplo.com"
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
                    Reporte_Calidad_{selectedReport?.report_number}.pdf
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
    </div >
  );
};

export default ClientQualityReportsPage;
