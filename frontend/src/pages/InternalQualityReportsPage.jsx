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
  BeakerIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';
import QualityReportForm from '../components/QualityReportForm';
import { useNotifications } from '../hooks/useNotifications';
import { api } from '../services/api';
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
  const { showSuccess, showError } = useNotifications();
  const queryClient = useQueryClient();
  const { 
    createInternalQualityReport, 
    escalateInternalReport, 
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

  // Obtener reportes de calidad interna
  const { 
    data: reports = [], 
    isLoading: reportsLoading, 
    error: reportsError,
    refetch: refetchReports 
  } = useQuery({
    queryKey: ['internal-quality-reports'],
    queryFn: async () => {
      const response = await api.get('/documents/quality-reports/internal/');
      return response.data || [];
    },
  });

  // Obtener incidencias disponibles
  const { 
    data: incidents = [], 
    isLoading: incidentsLoading 
  } = useQuery({
    queryKey: ['incidents-for-reports'],
    queryFn: async () => {
      const response = await api.get('/incidents/');
      return Array.isArray(response.data) ? response.data : (response.data?.results || []);
    },
  });

  // Filtrar y ordenar reportes
  const filteredReports = useMemo(() => {
    let filtered = Array.isArray(reports) ? reports : [];

    // Filtrar solo reportes de incidencias escaladas a calidad
    filtered = filtered.filter(report => {
      const relatedIncident = incidents.find(incident => incident.id === report.incident_id);
      return relatedIncident && relatedIncident.escalated_to_quality === true;
    });

    // Filtrar por término de búsqueda
    if (searchTerm) {
      filtered = filtered.filter(report =>
      report.incident_code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        report.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        report.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filtrar por estado
    if (filterStatus !== 'all') {
      filtered = filtered.filter(report => {
        switch (filterStatus) {
          case 'draft':
            return report.status === 'draft';
          case 'pending':
            return report.status === 'pending';
          case 'escalated':
            return report.status === 'escalated';
          case 'completed':
            return report.status === 'completed';
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
        case 'incident':
          return (a.incident_code || '').localeCompare(b.incident_code || '');
        case 'date':
        default:
          return new Date(b.created_at) - new Date(a.created_at);
      }
    });

    return filtered;
  }, [reports, incidents, searchTerm, filterStatus, sortBy]);

  // Crear reporte
  const handleCreateReport = useCallback(async (formData) => {
    try {
      await createInternalQualityReport.mutateAsync({
        incidentId: formData.incidentId,
        reportData: {
          title: formData.title,
          description: formData.description,
          findings: formData.findings,
          recommendations: formData.recommendations,
          priority: formData.priority,
        },
        attachments: formData.attachments || [],
      });
      
      setShowCreateModal(false);
      showSuccess('Reporte de calidad interna creado exitosamente');
      } catch (error) {
      console.error('Error creating report:', error);
      showError('Error al crear el reporte');
    }
  }, [createInternalQualityReport, showSuccess, showError]);

  // Manejar subida de documento
  const handleUploadDocument = useCallback(async (formData) => {
    try {
        const response = await api.post('/documents/upload/quality-report/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        if (response.data.success) {
          setShowUploadModal(false);
        showSuccess('Documento adjuntado exitosamente');
        refetchReports();
        }
      } catch (error) {
        console.error('Error uploading document:', error);
      showError('Error al adjuntar el documento');
    }
  }, [showSuccess, showError, refetchReports]);

  // Función unificada para abrir documentos
  const handleOpenDocument = useCallback((report) => {
    openDocument(report, 'quality-report', showSuccess, showError);
  }, [showSuccess, showError]);

  // Función unificada para descargar documentos
  const handleDownloadDocument = useCallback((report) => {
    downloadDocument(report, 'quality-report', showSuccess, showError);
  }, [showSuccess, showError]);

  // Función unificada para generar documentos
  const handleGenerateDocument = useCallback(async (report) => {
    await generateDocument(report, 'quality-report', showSuccess, showError);
  }, [showSuccess, showError]);

  // Función para seleccionar reporte
  const handleSelectReport = useCallback((report) => {
    setSelectedReport(report);
  }, []);

  // Escalar reporte
  const handleEscalateReport = useCallback(async (escalationData) => {
    if (!selectedReport) return;
    
    try {
      await escalateInternalReport.mutateAsync({
        reportId: selectedReport.id,
        escalationData,
      });
      
      setShowEscalateModal(false);
      setSelectedReport(null);
      showSuccess('Reporte escalado exitosamente');
    } catch (error) {
      console.error('Error escalating report:', error);
      showError('Error al escalar el reporte');
    }
  }, [selectedReport, escalateInternalReport, showSuccess, showError]);

  // Generar reporte automático
  const handleGenerateReport = useCallback(async (incidentId) => {
    try {
      await generateReport('internal-quality', incidentId);
      showSuccess('Reporte generado exitosamente');
      } catch (error) {
      console.error('Error generating report:', error);
      showError('Error al generar el reporte');
    }
  }, [generateReport, showSuccess, showError]);

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
      case 'draft':
        return 'bg-gray-100 text-gray-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'escalated':
        return 'bg-orange-100 text-orange-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  }, []);

  // Obtener icono del estado
  const getStatusIcon = useCallback((status) => {
    switch (status) {
      case 'draft':
        return <DocumentTextIcon className="h-4 w-4" />;
      case 'pending':
        return <ClockIcon className="h-4 w-4" />;
      case 'escalated':
        return <ExclamationTriangleIcon className="h-4 w-4" />;
      case 'completed':
        return <CheckCircleIcon className="h-4 w-4" />;
      default:
        return <DocumentTextIcon className="h-4 w-4" />;
    }
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <BeakerIcon className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <h1 className="text-xl font-semibold text-gray-900">
                  Reportes de Calidad Interna
                </h1>
                <p className="text-sm text-gray-500">
                  Gestión de reportes de control de calidad interno (solo incidencias escaladas)
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowCreateModal(true)}
                className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-xl text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 shadow-lg hover:shadow-xl transition-all duration-200"
              >
                <PlusIcon className="h-5 w-5 mr-2" />
                Crear Reporte
              </button>
              <button
                onClick={() => setShowUploadModal(true)}
                className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-xl text-white bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 shadow-lg hover:shadow-xl transition-all duration-200"
              >
                <DocumentArrowUpIcon className="h-5 w-5 mr-2" />
                Adjuntar Documento
              </button>
            </div>
          </div>
        </div>
      </div>

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
                    placeholder="Buscar por código, título o descripción..."
                    className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

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
                  <option value="draft">Borrador</option>
                  <option value="pending">Pendiente</option>
                  <option value="escalated">Escalado</option>
                  <option value="completed">Completado</option>
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
                  <option value="incident">Código de incidencia</option>
                </select>
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
              <DocumentTextIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No hay reportes
              </h3>
              <p className="text-gray-500 mb-4">
                Crea tu primer reporte de calidad interna
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
                            setShowEscalateModal(true);
                          }}
                          className="p-2 text-gray-400 hover:text-orange-600 hover:bg-orange-50 rounded-lg transition-colors"
                          title="Escalar reporte"
                        >
                          <ExclamationTriangleIcon className="h-4 w-4" />
                          </button>
                          )}
                      
                <button
                        onClick={() => handleGenerateReport(report.incident_id)}
                        disabled={isGenerating}
                        className="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors disabled:opacity-50"
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
          <CreateReportModal
            incidents={incidents}
            onSubmit={handleCreateReport}
            onClose={() => setShowCreateModal(false)}
            reportType="interno"
          />
        )}

        {/* Modal de adjuntar documento */}
        {showUploadModal && (
          <UploadDocumentModal
            incidents={incidents}
            onSubmit={handleUploadDocument}
            onClose={() => setShowUploadModal(false)}
          />
        )}

        {/* Sección de adjuntos para reportes */}
        {selectedReport && (
              <div className="mt-6">
            <ReportAttachments
              reportId={selectedReport.id}
              reportType="quality_report"
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

        {/* Modal de escalamiento */}
        {showEscalateModal && selectedReport && (
          <EscalateReportModal
            report={selectedReport}
            onSubmit={handleEscalateReport}
            onClose={() => {
              setShowEscalateModal(false);
              setSelectedReport(null);
            }}
          />
        )}

        {/* Formulario de cierre de incidencia */}
        {showIncidentClosure && selectedIncident && (
          <IncidentClosureForm
            incident={selectedIncident}
            onSubmit={handleCloseIncident}
            onCancel={() => {
              setShowIncidentClosure(false);
              setSelectedIncident(null);
            }}
            isLoading={false}
          />
          )}
        </div>
      </div>
  );
};

// Modal unificado para crear reportes - FORMULARIO PROFESIONAL COMPLETO
const CreateReportModal = ({ incidents, onSubmit, onClose, reportType = "cliente" }) => {
  const [formData, setFormData] = useState({
    incidentId: '',
    title: '',
    description: '',
    findings: '',
    recommendations: '',
    priority: 'medium',
    status: 'draft',
    category: '',
    subcategory: '',
    severity: 'medium',
    impact: 'medium',
    urgency: 'medium',
    responsible_person: '',
    department: '',
    location: '',
    equipment_involved: '',
    test_methods: '',
    standards_applied: '',
    non_conformities: '',
    corrective_actions: '',
    preventive_actions: '',
    follow_up_date: '',
    estimated_completion: '',
    budget_impact: '',
    resources_required: '',
    attachments: [],
    additional_notes: '',
    client_contact: '',
    supplier_contact: '',
    regulatory_requirements: '',
    compliance_status: '',
    risk_assessment: '',
    mitigation_measures: '',
    lessons_learned: '',
    improvement_suggestions: ''
  });

  const [currentStep, setCurrentStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState({});

  const totalSteps = 5;

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({ 
      ...prev, 
      [name]: type === 'checkbox' ? checked : value 
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    setFormData(prev => ({
      ...prev,
      attachments: [...prev.attachments, ...files]
    }));
  };

  const removeAttachment = (index) => {
    setFormData(prev => ({
      ...prev,
      attachments: prev.attachments.filter((_, i) => i !== index)
    }));
  };

  const validateStep = (step) => {
    const newErrors = {};
    
    switch (step) {
      case 1:
        if (!formData.incidentId) newErrors.incidentId = 'Debe seleccionar una incidencia';
        if (!formData.title.trim()) newErrors.title = 'El título es obligatorio';
        if (!formData.description.trim()) newErrors.description = 'La descripción es obligatoria';
        break;
      case 2:
        if (!formData.findings.trim()) newErrors.findings = 'Los hallazgos son obligatorios';
        if (!formData.recommendations.trim()) newErrors.recommendations = 'Las recomendaciones son obligatorias';
        break;
      case 3:
        if (!formData.category) newErrors.category = 'La categoría es obligatoria';
        if (!formData.severity) newErrors.severity = 'La severidad es obligatoria';
        break;
      case 4:
        if (!formData.responsible_person.trim()) newErrors.responsible_person = 'La persona responsable es obligatoria';
        if (!formData.department.trim()) newErrors.department = 'El departamento es obligatorio';
        break;
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => Math.min(prev + 1, totalSteps));
    }
  };

  const handlePrevious = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateStep(currentStep)) return;
    
    setIsSubmitting(true);
    try {
      await onSubmit(formData);
    } catch (error) {
      console.error('Error submitting form:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getTitle = () => {
    return reportType === "cliente" 
      ? "Crear Reporte de Calidad para Cliente"
      : "Crear Reporte de Calidad Interna";
  };

  const getDescription = () => {
    return reportType === "cliente"
      ? "Gestión profesional de reportes de control de calidad para clientes"
      : "Gestión profesional de reportes de control de calidad interno (solo incidencias escaladas)";
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="text-lg font-semibold text-blue-900 mb-2">Información Básica</h4>
              <p className="text-blue-700 text-sm">Complete la información fundamental del reporte</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <span className="text-red-500">*</span> Incidencia Relacionada
              </label>
              <select
                name="incidentId"
                value={formData.incidentId}
                onChange={handleChange}
                className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.incidentId ? 'border-red-500' : 'border-gray-300'
                }`}
              >
                <option value="">Seleccionar incidencia...</option>
                {incidents
                  .filter(incident => reportType === "interno" ? incident.escalated_to_quality === true : true)
                  .map(incident => (
                    <option key={incident.id} value={incident.id}>
                      {incident.code} - {incident.title || incident.cliente}
                    </option>
                  ))}
              </select>
              {errors.incidentId && <p className="text-red-500 text-sm mt-1">{errors.incidentId}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <span className="text-red-500">*</span> Título del Reporte
              </label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleChange}
                className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.title ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Título descriptivo del reporte de calidad..."
              />
              {errors.title && <p className="text-red-500 text-sm mt-1">{errors.title}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <span className="text-red-500">*</span> Descripción General
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows={4}
                className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.description ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Descripción detallada del problema o situación..."
              />
              {errors.description && <p className="text-red-500 text-sm mt-1">{errors.description}</p>}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Estado del Reporte
                </label>
                <select
                  name="status"
                  value={formData.status}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="draft">Borrador</option>
                  <option value="pending">Pendiente</option>
                  <option value="in_review">En Revisión</option>
                  <option value="approved">Aprobado</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Prioridad
                </label>
                <select
                  name="priority"
                  value={formData.priority}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="low">Baja</option>
                  <option value="medium">Media</option>
                  <option value="high">Alta</option>
                  <option value="critical">Crítica</option>
                </select>
              </div>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <div className="bg-green-50 p-4 rounded-lg">
              <h4 className="text-lg font-semibold text-green-900 mb-2">Análisis Técnico</h4>
              <p className="text-green-700 text-sm">Detalle los hallazgos y recomendaciones técnicas</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <span className="text-red-500">*</span> Hallazgos Técnicos
              </label>
              <textarea
                name="findings"
                value={formData.findings}
                onChange={handleChange}
                rows={6}
                className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.findings ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Detalle todos los hallazgos técnicos encontrados durante la investigación..."
              />
              {errors.findings && <p className="text-red-500 text-sm mt-1">{errors.findings}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <span className="text-red-500">*</span> Recomendaciones
              </label>
              <textarea
                name="recommendations"
                value={formData.recommendations}
                onChange={handleChange}
                rows={6}
                className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.recommendations ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Proporcione recomendaciones específicas para resolver los problemas identificados..."
              />
              {errors.recommendations && <p className="text-red-500 text-sm mt-1">{errors.recommendations}</p>}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Métodos de Prueba Utilizados
                </label>
                <textarea
                  name="test_methods"
                  value={formData.test_methods}
                  onChange={handleChange}
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Describa los métodos de prueba utilizados..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Estándares Aplicados
                </label>
                <textarea
                  name="standards_applied"
                  value={formData.standards_applied}
                  onChange={handleChange}
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Especifique los estándares de calidad aplicados..."
                />
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <div className="bg-yellow-50 p-4 rounded-lg">
              <h4 className="text-lg font-semibold text-yellow-900 mb-2">Clasificación y Evaluación</h4>
              <p className="text-yellow-700 text-sm">Categorice y evalúe el impacto del problema</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <span className="text-red-500">*</span> Categoría
                </label>
                <select
                  name="category"
                  value={formData.category}
                  onChange={handleChange}
                  className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    errors.category ? 'border-red-500' : 'border-gray-300'
                  }`}
                >
                  <option value="">Seleccionar categoría...</option>
                  <option value="product_quality">Calidad del Producto</option>
                  <option value="process_quality">Calidad del Proceso</option>
                  <option value="supplier_quality">Calidad del Proveedor</option>
                  <option value="service_quality">Calidad del Servicio</option>
                  <option value="system_quality">Calidad del Sistema</option>
                  <option value="regulatory">Regulatorio</option>
                  <option value="safety">Seguridad</option>
                  <option value="environmental">Ambiental</option>
                </select>
                {errors.category && <p className="text-red-500 text-sm mt-1">{errors.category}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Subcategoría
                </label>
                <input
                  type="text"
                  name="subcategory"
                  value={formData.subcategory}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Especifique la subcategoría..."
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <span className="text-red-500">*</span> Severidad
                </label>
                <select
                  name="severity"
                  value={formData.severity}
                  onChange={handleChange}
                  className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    errors.severity ? 'border-red-500' : 'border-gray-300'
                  }`}
                >
                  <option value="low">Baja</option>
                  <option value="medium">Media</option>
                  <option value="high">Alta</option>
                  <option value="critical">Crítica</option>
                </select>
                {errors.severity && <p className="text-red-500 text-sm mt-1">{errors.severity}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Impacto
                </label>
                <select
                  name="impact"
                  value={formData.impact}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="low">Bajo</option>
                  <option value="medium">Medio</option>
                  <option value="high">Alto</option>
                  <option value="critical">Crítico</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Urgencia
                </label>
                <select
                  name="urgency"
                  value={formData.urgency}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="low">Baja</option>
                  <option value="medium">Media</option>
                  <option value="high">Alta</option>
                  <option value="critical">Crítica</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ubicación del Problema
              </label>
              <input
                type="text"
                name="location"
                value={formData.location}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Especifique la ubicación donde ocurrió el problema..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Equipos Involucrados
              </label>
              <input
                type="text"
                name="equipment_involved"
                value={formData.equipment_involved}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Liste los equipos o sistemas involucrados..."
              />
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <div className="bg-purple-50 p-4 rounded-lg">
              <h4 className="text-lg font-semibold text-purple-900 mb-2">Responsabilidades y Recursos</h4>
              <p className="text-purple-700 text-sm">Asigne responsables y defina los recursos necesarios</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <span className="text-red-500">*</span> Persona Responsable
                </label>
                <input
                  type="text"
                  name="responsible_person"
                  value={formData.responsible_person}
                  onChange={handleChange}
                  className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    errors.responsible_person ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="Nombre del responsable principal..."
                />
                {errors.responsible_person && <p className="text-red-500 text-sm mt-1">{errors.responsible_person}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <span className="text-red-500">*</span> Departamento
                </label>
                <input
                  type="text"
                  name="department"
                  value={formData.department}
                  onChange={handleChange}
                  className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    errors.department ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="Departamento responsable..."
                />
                {errors.department && <p className="text-red-500 text-sm mt-1">{errors.department}</p>}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Fecha de Seguimiento
                </label>
                <input
                  type="date"
                  name="follow_up_date"
                  value={formData.follow_up_date}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Fecha Estimada de Completación
                </label>
                <input
                  type="date"
                  name="estimated_completion"
                  value={formData.estimated_completion}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Impacto Presupuestario
                </label>
                <input
                  type="number"
                  name="budget_impact"
                  value={formData.budget_impact}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0.00"
                  step="0.01"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Recursos Requeridos
                </label>
                <textarea
                  name="resources_required"
                  value={formData.resources_required}
                  onChange={handleChange}
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Describa los recursos necesarios..."
                />
              </div>
            </div>
          </div>
        );

      case 5:
        return (
          <div className="space-y-6">
            <div className="bg-indigo-50 p-4 rounded-lg">
              <h4 className="text-lg font-semibold text-indigo-900 mb-2">Acciones y Documentación</h4>
              <p className="text-indigo-700 text-sm">Defina las acciones correctivas y adjunte documentación</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                No Conformidades Identificadas
              </label>
              <textarea
                name="non_conformities"
                value={formData.non_conformities}
                onChange={handleChange}
                rows={4}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Detalle las no conformidades encontradas..."
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Acciones Correctivas
                </label>
                <textarea
                  name="corrective_actions"
                  value={formData.corrective_actions}
                  onChange={handleChange}
                  rows={4}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Describa las acciones correctivas..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Acciones Preventivas
                </label>
                <textarea
                  name="preventive_actions"
                  value={formData.preventive_actions}
                  onChange={handleChange}
                  rows={4}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Describa las acciones preventivas..."
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Adjuntar Documentos
              </label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors">
                <input
                  type="file"
                  multiple
                  onChange={handleFileChange}
                  className="hidden"
                  id="file-upload"
                  accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.jpg,.jpeg,.png,.gif,.bmp,.tiff"
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  <CloudArrowUpIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-lg font-medium text-gray-700 mb-2">
                    Arrastra archivos aquí o haz clic para seleccionar
                  </p>
                  <p className="text-sm text-gray-500">
                    PDF, DOC, XLS, PPT, imágenes y más
                  </p>
                </label>
              </div>
              
              {formData.attachments.length > 0 && (
                <div className="mt-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">Archivos seleccionados:</p>
                  <div className="space-y-2">
                    {formData.attachments.map((file, index) => (
                      <div key={index} className="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
                        <div className="flex items-center">
                          <DocumentTextIcon className="h-5 w-5 text-gray-400 mr-2" />
                          <span className="text-sm text-gray-700">{file.name}</span>
                          <span className="text-xs text-gray-500 ml-2">
                            ({(file.size / 1024 / 1024).toFixed(2)} MB)
                          </span>
                        </div>
                <button
                          type="button"
                          onClick={() => removeAttachment(index)}
                          className="text-red-500 hover:text-red-700"
                >
                          <XMarkIcon className="h-4 w-4" />
                </button>
                      </div>
                    ))}
              </div>
            </div>
          )}
        </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Notas Adicionales
              </label>
              <textarea
                name="additional_notes"
                value={formData.additional_notes}
                onChange={handleChange}
                rows={4}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Cualquier información adicional relevante..."
              />
      </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[95vh] overflow-hidden">
        {/* Header */}
        <div className="px-8 py-6 bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
              <div className="flex items-center justify-between">
            <div>
              <h3 className="text-2xl font-bold flex items-center">
                <PlusIcon className="h-6 w-6 mr-3" />
                {getTitle()}
                </h3>
              <p className="text-blue-100 mt-1">
                {getDescription()}
              </p>
            </div>
                <button
              onClick={onClose}
              className="text-white hover:text-gray-200 transition-colors duration-200 p-2"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
          
          {/* Progress Bar */}
          <div className="mt-4">
            <div className="flex items-center justify-between text-sm text-blue-100 mb-2">
              <span>Paso {currentStep} de {totalSteps}</span>
              <span>{Math.round((currentStep / totalSteps) * 100)}%</span>
            </div>
            <div className="w-full bg-blue-200 rounded-full h-2">
              <div 
                className="bg-white h-2 rounded-full transition-all duration-300"
                style={{ width: `${(currentStep / totalSteps) * 100}%` }}
              ></div>
            </div>
          </div>
              </div>

        {/* Content */}
        <div className="p-8 max-h-[70vh] overflow-y-auto">
          <form onSubmit={handleSubmit}>
            {renderStepContent()}
          </form>
        </div>
        
        {/* Footer */}
        <div className="px-8 py-6 bg-gray-50 border-t border-gray-200">
          <div className="flex justify-between">
                <button
              type="button"
              onClick={handlePrevious}
              disabled={currentStep === 1}
              className="px-6 py-3 text-sm font-semibold text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            >
              Anterior
            </button>
            
            <div className="flex space-x-3">
              <button
                type="button"
                onClick={onClose}
                className="px-6 py-3 text-sm font-semibold text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 transition-colors duration-200"
                >
                  Cancelar
                </button>
              
              {currentStep < totalSteps ? (
                <button
                  type="button"
                  onClick={handleNext}
                  className="px-6 py-3 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors duration-200"
                >
                  Siguiente
                </button>
              ) : (
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-8 py-3 text-sm font-semibold text-white bg-green-600 hover:bg-green-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
                >
                  {isSubmitting ? 'Creando...' : 'Crear Reporte'}
                </button>
              )}
              </div>
            </div>
          </div>
        </div>
    </div>
  );
};

// Componente para modal de escalamiento
const EscalateReportModal = ({ report, onSubmit, onClose }) => {
  const [escalationData, setEscalationData] = useState({
    reason: '',
    priority: 'high',
    assignedTo: '',
    notes: '',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setEscalationData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(escalationData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Escalar Reporte
                </h3>
              </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Razón del Escalamiento
            </label>
            <textarea
              name="reason"
              value={escalationData.reason}
              onChange={handleChange}
              required
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Asignar a
                </label>
            <input
              type="text"
              name="assignedTo"
              value={escalationData.assignedTo}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Nombre del responsable"
            />
              </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Notas Adicionales
            </label>
            <textarea
              name="notes"
              value={escalationData.notes}
              onChange={handleChange}
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
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
              className="px-4 py-2 text-sm font-medium text-white bg-orange-600 border border-transparent rounded-lg hover:bg-orange-700"
            >
              Escalar Reporte
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
            isLoading={false}
          />
      )}
    </div>
  );
};

// Modal para adjuntar documento
const UploadDocumentModal = ({ incidents, onSubmit, onClose }) => {
  const [formData, setFormData] = useState({
    incidentId: '',
    file: null,
    description: '',
  });

  const handleChange = (e) => {
    const { name, value, files } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: files ? files[0] : value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.incidentId || !formData.file) {
      alert('Por favor selecciona una incidencia y un archivo');
      return;
    }

    const submitData = new FormData();
    submitData.append('incident_id', formData.incidentId);
    submitData.append('file', formData.file);
    submitData.append('description', formData.description);
    submitData.append('document_type', 'quality_report');

    onSubmit(submitData);
  };

  return (
        <div className="fixed inset-0 bg-black bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
          <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-md">
        <div className="px-6 py-4 bg-gradient-to-r from-green-600 to-emerald-600 rounded-t-2xl">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white flex items-center">
                  <DocumentArrowUpIcon className="h-5 w-5 mr-2" />
              Adjuntar Documento
                </h3>
                <button
              onClick={onClose}
                  className="text-white hover:text-gray-200 transition-colors duration-200"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
            </div>
        
        <form onSubmit={handleSubmit} className="p-6">
          <div className="space-y-4">
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                Incidencia
                </label>
                <select
                name="incidentId"
                value={formData.incidentId}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
                required
              >
                <option value="">Selecciona una incidencia</option>
                {incidents
                  .filter(incident => incident.escalated_to_quality === true)
                  .map(incident => (
                    <option key={incident.id} value={incident.id}>
                      {incident.code} - {incident.title}
                    </option>
                  ))}
                </select>
              </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Archivo
              </label>
              <input
                type="file"
                name="file"
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
                required
                accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
              />
              </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Descripción
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
                placeholder="Descripción del documento..."
              />
            </div>
              </div>

          <div className="flex justify-end space-x-3 mt-6">
                <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors duration-200"
                >
                  Cancelar
                </button>
            <button
              type="submit"
              className="px-6 py-2 text-sm font-semibold text-white bg-green-600 hover:bg-green-700 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Adjuntar Documento
                </button>
              </div>
        </form>
            </div>
    </div>
  );
};

export default InternalQualityReportsPage;