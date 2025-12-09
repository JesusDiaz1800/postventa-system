<<<<<<< HEAD
import React, { useState, useCallback, useMemo } from 'react';
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
  BuildingOfficeIcon,
  ChatBubbleLeftRightIcon,
} from '@heroicons/react/24/outline';
import { useNotifications } from '../hooks/useNotifications';
import { api } from '../services/api';
import useReportsManager from '../hooks/useReportsManager';
import ReportAttachments from '../components/ReportAttachments';
import IncidentClosureForm from '../components/IncidentClosureForm';
import { openDocument, downloadDocument, generateDocument } from '../utils/documentUtils';

/**
 * Página profesional para gestión de reportes de proveedores
 * Permite crear, visualizar, adjuntar respuestas y cerrar incidencias
 */
const SupplierReportsPage = () => {
  const { showSuccess, showError } = useNotifications();
  const queryClient = useQueryClient();
  const { 
    createSupplierReport, 
    attachSupplierResponse, 
    closeIncident,
    generateReport,
    isGenerating 
  } = useReportsManager();

  // Estados
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [sortBy, setSortBy] = useState('date');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showResponseModal, setShowResponseModal] = useState(false);
  const [showClosureModal, setShowClosureModal] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);
  const [showIncidentClosure, setShowIncidentClosure] = useState(false);
  const [selectedIncident, setSelectedIncident] = useState(null);

  // Obtener reportes de proveedores
  const { 
    data: reports = [], 
    isLoading: reportsLoading, 
    error: reportsError,
    refetch: refetchReports 
  } = useQuery({
    queryKey: ['supplier-reports'],
    queryFn: async () => {
      const response = await api.get('/documents/supplier-reports/');
      return response.data || [];
    },
  });

  // Obtener incidencias disponibles
  const { 
    data: incidents = [], 
    isLoading: incidentsLoading 
  } = useQuery({
    queryKey: ['incidents-for-supplier-reports'],
    queryFn: async () => {
      const response = await api.get('/incidents/');
      return Array.isArray(response.data) ? response.data : (response.data?.results || []);
    },
  });

  // Filtrar y ordenar reportes
  const filteredReports = useMemo(() => {
    let filtered = Array.isArray(reports) ? reports : [];

    // Filtrar por término de búsqueda
    if (searchTerm) {
      filtered = filtered.filter(report =>
      report.incident_code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      report.supplier_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        report.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        report.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filtrar por estado
    if (filterStatus !== 'all') {
      filtered = filtered.filter(report => {
        switch (filterStatus) {
          case 'pending':
            return report.status === 'pending';
          case 'responded':
            return report.status === 'responded';
          case 'closed':
            return report.status === 'closed';
          case 'overdue':
            return report.status === 'overdue';
          default:
            return true;
        }
      });
    }

    // Ordenar
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'title':
          return (a.title || '').localeCompare(b.title || '');
        case 'supplier':
          return (a.supplier_name || '').localeCompare(b.supplier_name || '');
        case 'incident':
          return (a.incident_code || '').localeCompare(b.incident_code || '');
        case 'date':
        default:
          return new Date(b.created_at) - new Date(a.created_at);
      }
    });

    return filtered;
  }, [reports, searchTerm, filterStatus, sortBy]);

  // Crear reporte de proveedor
  const handleCreateReport = useCallback(async (formData) => {
    try {
      await createSupplierReport.mutateAsync({
        incidentId: formData.incidentId,
        reportData: {
          title: formData.title,
          description: formData.description,
          supplier_name: formData.supplier_name,
          supplier_contact: formData.supplier_contact,
          issue_description: formData.issue_description,
          expected_response_date: formData.expected_response_date,
          priority: formData.priority,
        },
        attachments: formData.attachments || [],
      });
      
      setShowCreateModal(false);
      showSuccess('Reporte de proveedor creado exitosamente');
    } catch (error) {
      console.error('Error creating supplier report:', error);
      showError('Error al crear el reporte de proveedor');
    }
  }, [createSupplierReport, showSuccess, showError]);

  // Adjuntar respuesta del proveedor
  const handleAttachResponse = useCallback(async (responseData) => {
    if (!selectedReport) return;
    
    try {
      await attachSupplierResponse.mutateAsync({
        reportId: selectedReport.id,
        responseData: {
          response_text: responseData.response_text,
          response_date: responseData.response_date,
          corrective_actions: responseData.corrective_actions,
          preventive_measures: responseData.preventive_measures,
          supplier_contact: responseData.supplier_contact,
        },
        attachments: responseData.attachments || [],
      });
      
      setShowResponseModal(false);
      setSelectedReport(null);
      showSuccess('Respuesta del proveedor adjuntada exitosamente');
    } catch (error) {
      console.error('Error attaching supplier response:', error);
      showError('Error al adjuntar la respuesta del proveedor');
    }
  }, [selectedReport, attachSupplierResponse, showSuccess, showError]);

  // Cerrar incidencia
  const handleCloseIncident = useCallback(async (closureData) => {
    if (!selectedIncident) return;
    
    try {
      await closeIncident.mutateAsync({
        incidentId: selectedIncident.id,
        resolutionData: {
          resolution: closureData.resolution,
          rootCause: closureData.rootCause,
          closureDate: closureData.closureDate,
        },
        finalActions: {
          actionsTaken: closureData.actionsTaken,
          preventiveMeasures: closureData.preventiveMeasures,
          responsiblePerson: closureData.responsiblePerson,
        },
        attachments: closureData.attachments || [],
      });
      
      setShowClosureModal(false);
      setSelectedIncident(null);
      showSuccess('Incidencia cerrada exitosamente');
    } catch (error) {
      console.error('Error closing incident:', error);
      showError('Error al cerrar la incidencia');
    }
  }, [selectedIncident, closeIncident, showSuccess, showError]);

  // Generar reporte automático
  const handleGenerateReport = useCallback(async (incidentId) => {
    try {
      await generateReport('supplier', incidentId);
      showSuccess('Reporte generado exitosamente');
    } catch (error) {
      console.error('Error generating report:', error);
      showError('Error al generar el reporte');
    }
  }, [generateReport, showSuccess, showError]);

  // Función unificada para abrir documentos
  const handleOpenDocument = useCallback((report) => {
    openDocument(report, 'supplier-report', showSuccess, showError);
  }, [showSuccess, showError]);

  // Función unificada para descargar documentos
  const handleDownloadDocument = useCallback((report) => {
    downloadDocument(report, 'supplier-report', showSuccess, showError);
  }, [showSuccess, showError]);

  // Función unificada para generar documentos
  const handleGenerateDocument = useCallback(async (report) => {
    await generateDocument(report, 'supplier-report', showSuccess, showError);
  }, [showSuccess, showError]);

  // Función para seleccionar reporte
  const handleSelectReport = useCallback((report) => {
    setSelectedReport(report);
  }, []);

  // Formatear fecha
  const formatDate = useCallback((dateString) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }, []);

  // Obtener color del estado
  const getStatusColor = useCallback((status) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'responded':
        return 'bg-blue-100 text-blue-800';
      case 'closed':
        return 'bg-green-100 text-green-800';
      case 'overdue':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  }, []);

  // Obtener icono del estado
  const getStatusIcon = useCallback((status) => {
    switch (status) {
      case 'pending':
        return <ClockIcon className="h-4 w-4" />;
      case 'responded':
        return <ChatBubbleLeftRightIcon className="h-4 w-4" />;
      case 'closed':
        return <CheckCircleIcon className="h-4 w-4" />;
      case 'overdue':
        return <ExclamationTriangleIcon className="h-4 w-4" />;
      default:
        return <DocumentTextIcon className="h-4 w-4" />;
    }
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
            <div className="flex items-center">
                <BuildingOfficeIcon className="h-8 w-8 text-blue-600 mr-3" />
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">
                    Reportes de Proveedores
                </h1>
                  <p className="text-gray-600">
                    Gestiona reportes y respuestas de proveedores
                </p>
              </div>
            </div>
              <div className="flex items-center space-x-3">
              <button
                onClick={() => setShowCreateModal(true)}
                  className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
              >
                  <PlusIcon className="h-4 w-4 mr-2" />
                  Nuevo Reporte
              </button>
              <button
                  onClick={() => refetchReports()}
                  className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
              >
                  <ArrowPathIcon className="h-4 w-4 mr-2" />
                  Actualizar
              </button>
=======
import React, { useState, useEffect, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useLocation } from 'react-router-dom';
import { api } from '../services/api';
import { 
  PlusIcon, 
  DocumentArrowUpIcon, 
  EyeIcon, 
  TrashIcon,
  XMarkIcon,
  CheckCircleIcon,
  MagnifyingGlassIcon,
  DocumentTextIcon,
  CalendarIcon,
  UserIcon,
  BuildingOfficeIcon,
  ArrowUpIcon,
  FunnelIcon,
  ArrowPathIcon,
  ExclamationTriangleIcon,
  PaperClipIcon,
  ChatBubbleLeftRightIcon
} from '@heroicons/react/24/outline';
import { useNotifications } from '../hooks/useNotifications';

const SupplierReportsPage = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const location = useLocation();
  const { showSuccess, showError } = useNotifications();
  
  // Estados principales
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedIncidentId, setSelectedIncidentId] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Query para obtener reportes de proveedores con datos de incidencia
  const { data: reports, isLoading: reportsLoading } = useQuery({
    queryKey: ['supplier-reports', { report_type: 'proveedor' }],
    queryFn: async () => {
      const response = await api.get('/documents/supplier-reports/', {
        params: { 
          report_type: 'proveedor',
          include_incident_data: true,
          expand: 'incident'
        }
      });
      console.log('Supplier Reports response:', response.data); // Debug
      return response.data;
    }
  });

  // Query para obtener incidencias escaladas desde reportes internos de calidad
  const { data: escalatedIncidents, isLoading: incidentsLoading } = useQuery({
    queryKey: ['escalatedIncidentsForSupplier'],
    queryFn: async () => {
      const response = await api.get('/incidents/escalated/', {
        params: { 
          from_quality_reports: true,
          ready_for_supplier: true
        }
      });
      return response.data;
    }
  });

  // Filtrar reportes por término de búsqueda
  const filteredReports = useMemo(() => {
    if (!reports?.results) return [];
    
    return reports.results.filter(report => 
      !searchTerm || 
      report.report_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      report.incident_code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      report.supplier_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      report.cliente?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [reports?.results, searchTerm]);

  // Manejar creación de reporte para proveedor
  const handleCreateReport = () => {
    if (!selectedIncidentId) {
      showError('Por favor selecciona una incidencia');
      return;
    }
    
    // Redirigir al formulario específico de reporte para proveedor
    navigate(`/supplier-report-form/${selectedIncidentId}?report_type=proveedor`);
  };

  // Manejar subida de documento
  const handleUploadDocument = async () => {
    if (!selectedIncidentId) {
      showError('Por favor selecciona una incidencia');
      return;
    }

    // Crear input de archivo dinámicamente
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.pdf,.doc,.docx';
    input.onchange = async (e) => {
      const file = e.target.files[0];
      if (!file) return;

      setIsSubmitting(true);
      try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('incident_id', selectedIncidentId);
        formData.append('report_type', 'proveedor');

        const response = await api.post('/documents/upload/supplier-report/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        if (response.data.success) {
          setShowUploadModal(false);
          setSelectedIncidentId('');
          queryClient.invalidateQueries(['supplier-reports']);
          showSuccess('Documento adjuntado exitosamente');
        }
      } catch (error) {
        console.error('Error uploading document:', error);
        showError('Error al subir el documento');
      } finally {
        setIsSubmitting(false);
      }
    };
    input.click();
  };

  // Manejar apertura de documento
  const handleOpenDocument = async (report) => {
    console.log('Report data:', report); // Debug
    
    try {
      const incidentId = report.incident_id || report.incident?.id || report.related_incident_id;
      const filename = report.filename || report.report_number || `supplier_report_${report.id}`;
      
      if (!incidentId) {
        const { API_ORIGIN } = await import('../services/api');
        const directUrl = `${API_ORIGIN}/api/documents/supplier-reports/${report.id}/view/`;
        window.open(directUrl, '_blank');
        return;
      }
      
      const { API_ORIGIN } = await import('../services/api');
      const urls = [
        `${API_ORIGIN}/api/documents/open/supplier-report/${incidentId}/${encodeURIComponent(filename)}`,
        `${API_ORIGIN}/api/documents/supplier-reports/${report.id}/view/`,
        `${API_ORIGIN}/api/documents/real-files/supplier-report/${encodeURIComponent(filename)}/serve/`
      ];
      
      // Intentar el primer endpoint
      try {
        const response = await fetch(urls[0]);
        if (response.ok) {
          window.open(urls[0], '_blank');
          return;
        }
      } catch (error) {
        console.log('First URL failed, trying second...');
      }
      
      // Intentar el segundo endpoint
      try {
        const response = await fetch(urls[1]);
        if (response.ok) {
          window.open(urls[1], '_blank');
          return;
        }
      } catch (error) {
        console.log('Second URL failed, trying third...');
      }
      
      // Intentar el tercer endpoint
      window.open(urls[2], '_blank');
      
    } catch (error) {
      console.error('Error opening document:', error);
      showError('Error al abrir el documento. Verifique que el archivo existe.');
    }
  };

  // Manejar descarga de documento
  const handleDownloadDocument = async (report) => {
    try {
      const incidentId = report.incident_id || report.incident?.id || report.related_incident_id;
      const filename = report.filename || report.report_number || `supplier_report_${report.id}`;
      
      const { API_ORIGIN } = await import('../services/api');
      const urls = [
        incidentId ? `${API_ORIGIN}/api/documents/open/supplier-report/${incidentId}/${encodeURIComponent(filename)}` : null,
        `${API_ORIGIN}/api/documents/supplier-reports/${report.id}/download/`,
        `${API_ORIGIN}/api/documents/real-files/supplier-report/${encodeURIComponent(filename)}/serve/`
      ].filter(Boolean);
      
      // Intentar cada URL hasta que una funcione
      for (const url of urls) {
        try {
          const response = await fetch(url);
          if (response.ok) {
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            link.click();
            return;
          }
        } catch (error) {
          console.log(`URL ${url} failed, trying next...`);
        }
      }
      
      showError('No se pudo descargar el documento. Verifique que el archivo existe.');
      
    } catch (error) {
      console.error('Error downloading document:', error);
      showError('Error al descargar el documento.');
    }
  };

  // Manejar generación de documento PDF
  const handleGenerateDocument = async (report) => {
    try {
      const response = await api.post(`/documents/supplier-reports/${report.id}/generate/`);
      if (response.data.success) {
        showSuccess('Documento PDF generado exitosamente');
        queryClient.invalidateQueries(['supplier-reports']);
      }
    } catch (error) {
      console.error('Error generating document:', error);
      showError('Error al generar el documento PDF');
    }
  };

  // Manejar escalamiento desde reporte interno de calidad
  const handleEscalateFromQuality = async (incidentId) => {
    if (!window.confirm('¿Estás seguro de que quieres escalar esta incidencia a proveedor desde el reporte interno de calidad?')) {
      return;
    }

    try {
      const incidentIdValue = typeof incidentId === 'object' ? incidentId.id : incidentId;
      const response = await api.post(`/incidents/${incidentIdValue}/escalate/supplier/`, {
        reason: 'Escalado desde reporte interno de calidad',
        from_quality_report: true
      });
      
      if (response.data.success) {
        queryClient.invalidateQueries(['supplier-reports']);
        showSuccess('Incidencia escalada a proveedor exitosamente. Se ha enviado un correo de notificación.');
      }
    } catch (error) {
      console.error('Error escalating from quality:', error);
      showError('Error al escalar la incidencia a proveedor');
    }
  };

  // Manejar cierre de incidencia
  const handleCloseIncident = async (incidentId) => {
    if (window.confirm('¿Estás seguro de que quieres cerrar esta incidencia?')) {
      try {
        const incidentIdValue = typeof incidentId === 'object' ? incidentId.id : incidentId;
        const response = await api.post(`/incidents/${incidentIdValue}/close/`);
        
        if (response.data.success) {
          queryClient.invalidateQueries(['supplier-reports']);
          showSuccess('Incidencia cerrada exitosamente');
        }
      } catch (error) {
        console.error('Error closing incident:', error);
        showError('Error al cerrar la incidencia');
      }
    }
  };

  // Manejar eliminación de reporte
  const handleDeleteReport = async (reportId) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este reporte?')) {
      try {
        await api.delete(`/documents/supplier-reports/${reportId}/`);
        queryClient.invalidateQueries(['supplier-reports']);
        showSuccess('Reporte eliminado exitosamente');
      } catch (error) {
        console.error('Error deleting report:', error);
        showError('Error al eliminar el reporte');
      }
    }
  };

  if (reportsLoading || incidentsLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-green-600 mx-auto mb-6"></div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Cargando Reportes</h3>
          <p className="text-gray-600">Preparando la información...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <BuildingOfficeIcon className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4">
                <h1 className="text-xl font-semibold text-gray-900">
                  Reportes para Proveedores
                </h1>
                <p className="text-sm text-gray-500">
                  Gestión de reportes escalados a proveedores desde calidad interna
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowCreateModal(true)}
                className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-xl text-white bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 shadow-lg hover:shadow-xl transition-all duration-200"
              >
                <PlusIcon className="h-5 w-5 mr-2" />
                Crear Reporte
              </button>
              <button
                onClick={() => setShowUploadModal(true)}
                className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-xl text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 shadow-lg hover:shadow-xl transition-all duration-200"
              >
                <DocumentArrowUpIcon className="h-5 w-5 mr-2" />
                Adjuntar Documento
              </button>
            </div>
>>>>>>> 674c244 (tus cambios)
          </div>
        </div>
      </div>

<<<<<<< HEAD
          {/* Filtros */}
          <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Búsqueda */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Buscar
                </label>
          <div className="relative">
                  <MagnifyingGlassIcon className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Buscar por código, proveedor, título..."
                    className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
=======
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filtros y Búsqueda */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6 relative z-10">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-gray-900">Filtros y Búsqueda</h2>
            <button
              onClick={() => setSearchTerm('')}
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              <ArrowPathIcon className="h-4 w-4 mr-2" />
              Limpiar
            </button>
          </div>
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar por número de reporte, código de incidencia, proveedor o cliente..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
>>>>>>> 674c244 (tus cambios)
            />
          </div>
        </div>

<<<<<<< HEAD
              {/* Filtro por estado */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Estado
                </label>
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="all">Todos los estados</option>
                  <option value="pending">Pendiente</option>
                  <option value="responded">Respondido</option>
                  <option value="closed">Cerrado</option>
                  <option value="overdue">Vencido</option>
                </select>
              </div>

              {/* Ordenar por */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Ordenar por
                </label>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="date">Fecha (más reciente)</option>
                  <option value="title">Título (A-Z)</option>
                  <option value="supplier">Proveedor (A-Z)</option>
                  <option value="incident">Código de incidencia</option>
                </select>
              </div>
            </div>
            </div>
          </div>
          
        {/* Lista de reportes */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          {reportsLoading ? (
            <div className="p-6">
              <div className="animate-pulse space-y-4">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="flex items-center space-x-4">
                    <div className="w-10 h-10 bg-gray-200 rounded"></div>
                    <div className="flex-1 space-y-2">
                      <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                      <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : filteredReports.length === 0 ? (
            <div className="p-6 text-center">
              <BuildingOfficeIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No hay reportes de proveedores
              </h3>
              <p className="text-gray-500 mb-4">
                Crea tu primer reporte de proveedor
              </p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Crear Reporte
              </button>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
                  {filteredReports.map((report) => (
                <div key={report.id} className="p-6 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {report.title || 'Sin título'}
                        </h3>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(report.status)}`}>
                          {getStatusIcon(report.status)}
                          <span className="ml-1 capitalize">{report.status}</span>
                        </span>
                      </div>
                      
                      <p className="text-gray-600 mb-3 line-clamp-2">
                        {report.description || 'Sin descripción'}
                      </p>
                      
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <div className="flex items-center">
                          <BuildingOfficeIcon className="h-4 w-4 mr-1" />
                          {report.supplier_name || 'Sin proveedor'}
                            </div>
                        <div className="flex items-center">
                          <DocumentTextIcon className="h-4 w-4 mr-1" />
                          {report.incident_code || 'Sin código'}
                          </div>
                        <div className="flex items-center">
                          <CalendarIcon className="h-4 w-4 mr-1" />
                          {formatDate(report.created_at)}
                            </div>
                        <div className="flex items-center">
                          <UserIcon className="h-4 w-4 mr-1" />
                          {report.created_by || 'Sistema'}
                            </div>
                          </div>
                        </div>
                    
                    <div className="flex items-center space-x-2 ml-4">
                          <button
                        onClick={() => handleOpenDocument(report)}
                        className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        title="Ver reporte"
                          >
                            <EyeIcon className="h-4 w-4" />
                          </button>
                          
                          <button
                        onClick={() => handleDownloadDocument(report)}
                        className="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                        title="Descargar reporte"
                          >
                            <DocumentArrowUpIcon className="h-4 w-4" />
                          </button>
                          
                          <button
                        onClick={() => handleGenerateDocument(report)}
                        className="p-2 text-gray-400 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
                        title="Generar documento PDF"
                          >
                            <DocumentTextIcon className="h-4 w-4" />
                          </button>
                          
                          <button
                        onClick={() => handleSelectReport(report)}
                        className="p-2 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                        title="Adjuntar documentos"
                          >
                            <PaperClipIcon className="h-4 w-4" />
                          </button>
                      
                      {report.status === 'pending' && (
                        <button
                          onClick={() => {
                            setSelectedReport(report);
                            setShowResponseModal(true);
                          }}
                          className="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                          title="Adjuntar respuesta"
                        >
                          <ChatBubbleLeftRightIcon className="h-4 w-4" />
                        </button>
                      )}
                      
                      {report.status === 'responded' && (
                          <button
                          onClick={() => {
                            setSelectedIncident({ id: report.incident_id, code: report.incident_code });
                            setShowClosureModal(true);
                          }}
                          className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          title="Cerrar incidencia"
                        >
                          <CheckCircleIcon className="h-4 w-4" />
                          </button>
                      )}
                      
                <button
                        onClick={() => handleGenerateReport(report.incident_id)}
                        disabled={isGenerating}
                        className="p-2 text-gray-400 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition-colors disabled:opacity-50"
                        title="Generar reporte"
                      >
                        <CloudArrowUpIcon className="h-4 w-4" />
                </button>
              </div>
            </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Modal de creación */}
        {showCreateModal && (
          <CreateSupplierReportModal
            incidents={incidents}
            onSubmit={handleCreateReport}
            onClose={() => setShowCreateModal(false)}
          />
        )}

        {/* Sección de adjuntos para reportes */}
        {selectedReport && (
          <div className="mt-6">
            <ReportAttachments
              reportId={selectedReport.id}
              reportType="supplier_report"
              onAttachmentUploaded={() => {
                refetchReports();
                showSuccess('Documento adjuntado exitosamente');
              }}
              onAttachmentDeleted={() => {
                refetchReports();
                showSuccess('Documento eliminado exitosamente');
              }}
            />
          </div>
        )}

        {/* Modal de respuesta */}
        {showResponseModal && selectedReport && (
          <SupplierResponseModal
            report={selectedReport}
            onSubmit={handleAttachResponse}
            onClose={() => {
              setShowResponseModal(false);
              setSelectedReport(null);
            }}
          />
        )}

        {/* Modal de cierre */}
        {showClosureModal && selectedIncident && (
          <IncidentClosureModal
            incident={selectedIncident}
            onSubmit={handleCloseIncident}
            onClose={() => {
              setShowClosureModal(false);
              setSelectedIncident(null);
            }}
          />
          )}
        </div>
      </div>
  );
};

// Componente para modal de creación de reporte de proveedor
const CreateSupplierReportModal = ({ incidents, onSubmit, onClose }) => {
  const [formData, setFormData] = useState({
    incidentId: '',
    title: '',
    description: '',
    supplier_name: '',
    supplier_contact: '',
    issue_description: '',
    expected_response_date: '',
    priority: 'medium',
    attachments: [],
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    setFormData(prev => ({
      ...prev,
      attachments: [...prev.attachments, ...files]
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Crear Reporte de Proveedor
                </h3>
              </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Incidencia
                </label>
                <select
              name="incidentId"
              value={formData.incidentId}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Seleccionar incidencia</option>
              {incidents.map(incident => (
                    <option key={incident.id} value={incident.id}>
                  {incident.code} - {incident.title}
=======
        {/* Lista de Reportes */}
        <div className="bg-white rounded-lg shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-medium text-gray-900">
                Reportes para Proveedores Generados
              </h2>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                {filteredReports.length} reportes
              </span>
            </div>
          </div>
          
          {filteredReports.length > 0 ? (
            <div className="table-container">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Reporte
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Incidencia
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Proveedor
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Cliente
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Fecha
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Estado
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Acciones
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredReports.map((report) => (
                    <tr key={report.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <div className="h-10 w-10 rounded-full bg-green-100 flex items-center justify-center">
                              <DocumentTextIcon className="h-5 w-5 text-green-600" />
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">
                              {report.report_number}
                            </div>
                            <div className="text-sm text-gray-500">
                              {report.title}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {report.incident?.code || report.incident_code || report.related_incident?.code || 'N/A'}
                        </div>
                        <div className="text-sm text-gray-500">
                          {report.incident?.categoria || report.categoria || report.related_incident?.categoria || 'N/A'}
                        </div>
                        {(report.incident?.subcategoria || report.related_incident?.subcategoria) && (
                          <div className="text-xs text-gray-500">
                            {report.incident?.subcategoria || report.related_incident?.subcategoria}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {report.supplier_name || report.incident?.provider || report.related_incident?.provider || 'N/A'}
                        </div>
                        <div className="text-sm text-gray-500">
                          {report.supplier_contact || 'Sin contacto'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {report.incident?.cliente || report.cliente || report.related_incident?.cliente || 'N/A'}
                        </div>
                        <div className="text-sm text-gray-500">
                          {report.incident?.obra || report.obra || report.related_incident?.obra || 'N/A'}
                        </div>
                        {(report.incident?.proyecto || report.related_incident?.proyecto) && (
                          <div className="text-xs text-gray-500">
                            {report.incident?.proyecto || report.related_incident?.proyecto}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {new Date(report.created_at).toLocaleDateString()}
                        </div>
                        <div className="text-sm text-gray-500">
                          {new Date(report.created_at).toLocaleTimeString()}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          report.status === 'cerrado' ? 'bg-green-100 text-green-800' :
                          report.status === 'responded' ? 'bg-blue-100 text-blue-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {report.status === 'cerrado' ? 'CERRADO' : 
                           report.status === 'responded' ? 'RESPONDIDO' : 'PENDIENTE'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => handleOpenDocument(report)}
                            className="text-blue-600 hover:text-blue-900 p-1 rounded-md hover:bg-blue-50"
                            title="Ver reporte"
                          >
                            <EyeIcon className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleDownloadDocument(report)}
                            className="text-green-600 hover:text-green-900 p-1 rounded-md hover:bg-green-50"
                            title="Descargar reporte"
                          >
                            <DocumentArrowUpIcon className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleGenerateDocument(report)}
                            className="text-purple-600 hover:text-purple-900 p-1 rounded-md hover:bg-purple-50"
                            title="Generar documento PDF"
                          >
                            <DocumentTextIcon className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteReport(report.id)}
                            className="text-red-600 hover:text-red-900 p-1 rounded-md hover:bg-red-50"
                            title="Eliminar reporte"
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
            <div className="text-center py-12">
              <BuildingOfficeIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No hay reportes</h3>
              <p className="mt-1 text-sm text-gray-500">
                Comienza creando un nuevo reporte para proveedor.
              </p>
              <div className="mt-6">
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                >
                  <PlusIcon className="h-4 w-4 mr-2" />
                  Crear Primer Reporte
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Sección de Escalamiento desde Calidad Interna */}
        {escalatedIncidents?.incidents && escalatedIncidents.incidents.length > 0 && (
          <div className="mt-8 bg-white rounded-lg shadow-sm">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-medium text-gray-900 flex items-center">
                  <ExclamationTriangleIcon className="h-5 w-5 text-orange-500 mr-2" />
                  Incidencias Listas para Escalamiento a Proveedor
                </h2>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                  {escalatedIncidents.incidents.length} incidencias
                </span>
              </div>
            </div>
            
            <div className="table-container">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Incidencia
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Cliente
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Proveedor
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Fecha Escalamiento
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Acciones
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {escalatedIncidents.incidents.map((incident) => (
                    <tr key={incident.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <div className="h-10 w-10 rounded-full bg-orange-100 flex items-center justify-center">
                              <ExclamationTriangleIcon className="h-5 w-5 text-orange-600" />
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">
                              {incident.code}
                            </div>
                            <div className="text-sm text-gray-500">
                              {incident.categoria}
                            </div>
                            {incident.subcategoria && (
                              <div className="text-xs text-gray-500">
                                {incident.subcategoria}
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {incident.cliente}
                        </div>
                        <div className="text-sm text-gray-500">
                          {incident.obra}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {incident.provider}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {new Date(incident.escalation_date).toLocaleDateString()}
                        </div>
                        <div className="text-sm text-gray-500">
                          {new Date(incident.escalation_date).toLocaleTimeString()}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => handleEscalateFromQuality(incident.id)}
                            className="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md text-white bg-orange-600 hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500"
                          >
                            <ArrowUpIcon className="h-3 w-3 mr-1" />
                            Escalar a Proveedor
                          </button>
                          <button
                            onClick={() => handleCloseIncident(incident.id)}
                            className="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                          >
                            <CheckCircleIcon className="h-3 w-3 mr-1" />
                            Cerrar
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Modal de Crear Reporte */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
          <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-md">
            <div className="px-6 py-4 bg-gradient-to-r from-green-600 to-emerald-600 rounded-t-2xl">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white flex items-center">
                  <PlusIcon className="h-5 w-5 mr-2" />
                  Crear Reporte para Proveedor
                </h3>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="text-white hover:text-gray-200 transition-colors duration-200"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
            </div>
            <div className="p-6">
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Seleccionar Incidencia
                </label>
                <select
                  value={selectedIncidentId}
                  onChange={(e) => setSelectedIncidentId(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="">Seleccionar incidencia...</option>
                  {(escalatedIncidents?.incidents || []).map((incident) => (
                    <option key={incident.id} value={incident.id}>
                      {incident.code} - {incident.cliente} - {incident.provider}
>>>>>>> 674c244 (tus cambios)
                    </option>
                  ))}
                </select>
              </div>

<<<<<<< HEAD
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Título del Reporte
            </label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nombre del Proveedor
              </label>
              <input
                type="text"
                name="supplier_name"
                value={formData.supplier_name}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Contacto del Proveedor
              </label>
              <input
                type="text"
                name="supplier_contact"
                value={formData.supplier_contact}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Descripción del Problema
            </label>
            <textarea
              name="issue_description"
              value={formData.issue_description}
              onChange={handleChange}
              rows={4}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Descripción del Reporte
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Fecha Esperada de Respuesta
              </label>
              <input
                type="date"
                name="expected_response_date"
                value={formData.expected_response_date}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Prioridad
              </label>
              <select
                name="priority"
                value={formData.priority}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="low">Baja</option>
                <option value="medium">Media</option>
                <option value="high">Alta</option>
                <option value="critical">Crítica</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Archivos Adjuntos
            </label>
            <input
              type="file"
              multiple
              onChange={handleFileChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.jpg,.jpeg,.png"
            />
          </div>

          <div className="flex justify-end space-x-3 pt-4">
                <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
=======
              <div className="flex justify-end pt-4 border-t border-gray-200 space-x-3">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-6 py-2 text-sm font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
>>>>>>> 674c244 (tus cambios)
                >
                  Cancelar
                </button>
                <button
<<<<<<< HEAD
              type="submit"
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700"
                >
              Crear Reporte
                </button>
              </div>
        </form>
            </div>
          </div>
  );
};

// Componente para modal de respuesta del proveedor
const SupplierResponseModal = ({ report, onSubmit, onClose }) => {
  const [responseData, setResponseData] = useState({
    response_text: '',
    response_date: new Date().toISOString().split('T')[0],
    corrective_actions: '',
    preventive_measures: '',
    supplier_contact: '',
    attachments: [],
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setResponseData(prev => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    setResponseData(prev => ({
      ...prev,
      attachments: [...prev.attachments, ...files]
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(responseData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Adjuntar Respuesta del Proveedor
          </h3>
          <p className="text-sm text-gray-500">
            Reporte: {report.title}
          </p>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Respuesta del Proveedor
            </label>
            <textarea
              name="response_text"
              value={responseData.response_text}
              onChange={handleChange}
              required
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Describe la respuesta del proveedor..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Acciones Correctivas
            </label>
            <textarea
              name="corrective_actions"
              value={responseData.corrective_actions}
              onChange={handleChange}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Describe las acciones correctivas propuestas..."
            />
        </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Medidas Preventivas
            </label>
            <textarea
              name="preventive_measures"
              value={responseData.preventive_measures}
              onChange={handleChange}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Describe las medidas preventivas implementadas..."
            />
              </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Fecha de Respuesta
              </label>
              <input
                type="date"
                name="response_date"
                value={responseData.response_date}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Contacto del Proveedor
                </label>
              <input
                type="text"
                name="supplier_contact"
                value={responseData.supplier_contact}
                onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              </div>
              </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Documentos de Respuesta
                </label>
            <input
              type="file"
              multiple
              onChange={handleFileChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.jpg,.jpeg,.png"
            />
              </div>

          <div className="flex justify-end space-x-3 pt-4">
                <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
              type="submit"
              className="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-lg hover:bg-green-700"
                >
              Adjuntar Respuesta
                </button>
              </div>
        </form>
              </div>
            </div>
  );
};

// Componente para modal de cierre de incidencia
const IncidentClosureModal = ({ incident, onSubmit, onClose }) => {
  const [closureData, setClosureData] = useState({
    resolution: '',
    rootCause: '',
    actionsTaken: '',
    preventiveMeasures: '',
    responsiblePerson: '',
    closureDate: new Date().toISOString().split('T')[0],
    attachments: [],
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setClosureData(prev => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    setClosureData(prev => ({
      ...prev,
      attachments: [...prev.attachments, ...files]
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(closureData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Cerrar Incidencia
          </h3>
          <p className="text-sm text-gray-500">
            Incidencia: {incident.code}
          </p>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Resolución Final
            </label>
            <textarea
              name="resolution"
              value={closureData.resolution}
              onChange={handleChange}
              required
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Describe la resolución final del problema..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Causa Raíz
            </label>
            <textarea
              name="rootCause"
              value={closureData.rootCause}
              onChange={handleChange}
              required
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Identifica la causa raíz del problema..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Acciones Tomadas
            </label>
            <textarea
              name="actionsTaken"
              value={closureData.actionsTaken}
              onChange={handleChange}
              required
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Detalla todas las acciones realizadas..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Medidas Preventivas
            </label>
            <textarea
              name="preventiveMeasures"
              value={closureData.preventiveMeasures}
              onChange={handleChange}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Describe las medidas preventivas implementadas..."
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Persona Responsable
              </label>
              <input
                type="text"
                name="responsiblePerson"
                value={closureData.responsiblePerson}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Fecha de Cierre
                </label>
              <input
                type="date"
                name="closureDate"
                value={closureData.closureDate}
                onChange={handleChange}
                required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
          </div>
        </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Documentos de Respaldo
            </label>
            <input
              type="file"
              multiple
              onChange={handleFileChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.jpg,.jpeg,.png"
            />
              </div>

          <div className="flex justify-end space-x-3 pt-4">
                <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancelar
                </button>
            <button
              type="submit"
              className="px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-lg hover:bg-red-700"
            >
              Cerrar Incidencia
                </button>
              </div>
        </form>
          </div>

        {/* Formulario de cierre de incidencia */}
        {showIncidentClosure && selectedIncident && (
          <IncidentClosureForm
            incident={selectedIncident}
            onSubmit={handleCloseIncident}
            onCancel={() => {
              setShowIncidentClosure(false);
              setSelectedIncident(null);
            }}
            isLoading={closeIncident.isPending}
          />
=======
                  onClick={handleCreateReport}
                  disabled={!selectedIncidentId}
                  className="px-6 py-2 text-sm font-semibold text-white bg-green-600 hover:bg-green-700 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Crear Reporte
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Subida de Documento */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
          <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-md">
            <div className="px-6 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-t-2xl">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white flex items-center">
                  <DocumentArrowUpIcon className="h-5 w-5 mr-2" />
                  Adjuntar Documento
                </h3>
                <button
                  onClick={() => setShowUploadModal(false)}
                  className="text-white hover:text-gray-200 transition-colors duration-200"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
            </div>
            <div className="p-6">
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Seleccionar Incidencia
                </label>
                <select
                  value={selectedIncidentId}
                  onChange={(e) => setSelectedIncidentId(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Seleccionar incidencia...</option>
                  {(escalatedIncidents?.incidents || []).map((incident) => (
                    <option key={incident.id} value={incident.id}>
                      {incident.code} - {incident.cliente} - {incident.provider}
                    </option>
                  ))}
                </select>
              </div>

              <div className="mb-6">
                <button
                  onClick={handleUploadDocument}
                  disabled={!selectedIncidentId || isSubmitting}
                  className="w-full flex items-center justify-center px-6 py-4 border-2 border-dashed border-gray-300 text-sm font-semibold rounded-xl text-gray-700 bg-white hover:bg-gray-50 hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <DocumentArrowUpIcon className="h-5 w-5 mr-3" />
                  {isSubmitting ? 'Subiendo...' : '📎 Seleccionar Archivo'}
                </button>
              </div>

              <div className="flex justify-end pt-4 border-t border-gray-200">
                <button
                  onClick={() => setShowUploadModal(false)}
                  className="px-6 py-2 text-sm font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
                >
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        </div>
>>>>>>> 674c244 (tus cambios)
      )}
    </div>
  );
};

export default SupplierReportsPage;