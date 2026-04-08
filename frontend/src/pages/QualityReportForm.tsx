import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api, aiAPI } from '../services/api';
import {
  ArrowLeftIcon,
  DocumentArrowUpIcon,
  PhotoIcon,
  XMarkIcon,
  CheckCircleIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  ClipboardDocumentCheckIcon,
  DocumentTextIcon,
  UserIcon,
  MagnifyingGlassIcon,
  WrenchScrewdriverIcon,
  ClipboardDocumentListIcon,
  CalendarDaysIcon,
  ChatBubbleBottomCenterTextIcon,
  CameraIcon,
  ExclamationTriangleIcon,
  SparklesIcon,
  BuildingOfficeIcon,
  ClipboardIcon,
  BeakerIcon,
  ArrowPathIcon,
  ArrowDownTrayIcon,
  CubeIcon
} from '@heroicons/react/24/outline';
import { useNotifications } from '../hooks/useNotifications';
import IncidentImagesViewer from '../components/IncidentImagesViewer';

// Componente de sección premium/wow
const PremiumSection = ({ title, icon: Icon, children, defaultOpen = true, color = 'blue' }) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  const colorClasses = {
    blue: 'from-blue-600 to-indigo-700',
    indigo: 'from-indigo-600 to-violet-700',
    emerald: 'from-emerald-600 to-teal-700',
    amber: 'from-amber-500 to-orange-600',
    rose: 'from-rose-500 to-pink-600',
    slate: 'from-slate-700 to-slate-800'
  };

  return (
    <div className="bg-white/60 backdrop-blur-2xl rounded-3xl border border-white/60 shadow-xl shadow-slate-200/50 overflow-hidden transition-all duration-300 mb-6 group hover:shadow-2xl hover:shadow-slate-300/50">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={`w-full px-6 py-5 flex items-center justify-between bg-gradient-to-r ${colorClasses[color]} text-white transition-all relative overflow-hidden`}
      >
        <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <div className="flex items-center gap-4 relative z-10">
          <div className="p-1.5 bg-white/20 rounded-lg backdrop-blur-sm">
            <Icon className="h-6 w-6 text-white" />
          </div>
          <span className="text-lg font-black tracking-wide uppercase">{title}</span>
        </div>
        <div className={`transition-transform duration-300 bg-white/20 p-1.5 rounded-full backdrop-blur-sm ${isOpen ? 'rotate-180' : ''}`}>
          <ChevronDownIcon className="h-4 w-4 text-white" />
        </div>
      </button>
      <div className={`transition-all duration-500 ease-in-out ${isOpen ? 'max-h-[5000px] opacity-100' : 'max-h-0 opacity-0 overflow-hidden'}`}>
        <div className="p-8 space-y-8">
          {children}
        </div>
      </div>
    </div>
  );
};

// Input con diseño ultra-moderno
const GlassInput = ({ label, icon: Icon, required, ...props }) => (
  <div className="space-y-2 group">
    <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest flex items-center gap-2 px-1">
      {label}
      {required && <span className="text-rose-500">*</span>}
    </label>
    <div className="relative">
      {Icon && (
        <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-blue-600 transition-colors">
          <Icon className="h-5 w-5" />
        </div>
      )}
      <input
        {...props}
        className={`w-full ${Icon ? 'pl-12' : 'px-4'} py-3.5 bg-slate-50/50 border border-slate-200 rounded-xl focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all duration-300 placeholder:text-slate-400 font-medium text-sm text-slate-700 shadow-sm`}
      />
    </div>
  </div>
);

// Textarea con diseño ultra-moderno
const GlassTextarea = ({ label, icon: Icon, required, rows = 3, ...props }) => (
  <div className="space-y-2 group">
    <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest flex items-center gap-2 px-1">
      {label}
      {required && <span className="text-rose-500">*</span>}
    </label>
    <div className="relative">
      {Icon && (
        <div className="absolute left-4 top-4 text-slate-400 group-focus-within:text-blue-600 transition-colors">
          <Icon className="h-5 w-5" />
        </div>
      )}
      <textarea
        {...props}
        rows={rows}
        className={`w-full ${Icon ? 'pl-12' : 'px-4'} py-3.5 bg-slate-50/50 border border-slate-200 rounded-xl focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all duration-300 placeholder:text-slate-400 font-medium text-sm text-slate-700 resize-none shadow-sm`}
      />
    </div>
  </div>
);

const QualityReportForm = () => {
  const { incidentId } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { showSuccess, showError } = useNotifications();
  const queryClient = useQueryClient();

  const isInternal = searchParams.get('internal') === 'true' || window.location.pathname.includes('/internal/');
  const reportType = isInternal ? 'interno' : 'cliente';

  const [formData, setFormData] = useState({
    // Datos Generales (Inicializar vacío para evitar uncontrolled inputs)
    title: '',
    incident_code: '',
    client_name: '',
    project_name: '',
    sap_call_id: '',
    salesperson: '',
    technician: '',

    // Contenido del Reporte
    executive_summary: '',
    problem_description: '',
    technical_analysis: '',
    root_cause_analysis: '',
    corrective_actions: '',
    preventive_measures: '',
    recommendations: '',
    conclusions: '',
    internal_notes: '',

    // Datos del Producto
    product_diameter: '',
    product_pn: '',
    product_sdr: '',
    product_material: 'PP-R',
    product_lot: '',

    // Condiciones de Terreno
    joining_method: 'Termofusión',
    ambient_temperature: '',
    tools_status: 'OK',
    machine_id: '',
    applicable_normative: 'ISO 15874 / NCh 3151',

    // Ensayos de Laboratorio (NUEVO)
    melt_index: '',
    density: '',
    tio: '',
    dsc: '',
    carbon_black_dispersion: '',
    carbon_black_percentage: '',
    ash_percentage: '',
    moisture_percentage: '',

    // Protocolo de Pruebas
    visual_inspection: 'Conforme',
    pressure_test: 'No Realizada',
    test_pressure_bar: '',
    test_duration_min: '',
    test_result: 'N/A',

    // Imágenes por sección (IDs de adjuntos o base64)
    section_images: {
      product: null,
      site_conditions: null,
      test_protocol: null,
      lab_tests: null,
      conclusions: null
    },

    // Estado
    status: 'draft'
  });

  const [images, setImages] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [createdReportId, setCreatedReportId] = useState(null);
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false);

  // 1. Obtener datos de la incidencia real
  const { data: incident, isLoading: incidentLoading } = useQuery({
    queryKey: ['incident-for-quality', incidentId],
    queryFn: () => api.get(`/incidents/${incidentId}/`).then(res => res.data),
    enabled: !!incidentId
  });

  // 2. Obtener imágenes de la incidencia
  const { data: incidentImages } = useQuery({
    queryKey: ['incidentImages-for-quality', incidentId],
    queryFn: () => api.get(`/incidents/${incidentId}/images/list/`).then(res => res.data),
    enabled: !!incidentId
  });

  // 3. Precargar datos AUTOMÁTICAMENTE (Feedback Usuario)
  useEffect(() => {
    if (incident) {
      setFormData(prev => ({
        ...prev,
        title: `Informe de Calidad - ${incident.code}`,
        incident_code: incident.code,
        client_name: incident.cliente || '',
        project_name: incident.obra || incident.proyecto || '',
        sap_call_id: incident.sap_call_id || 'Sin llamada SAP vinculada',
        salesperson: incident.vendedor || incident.salesperson || 'No asignado',
        technician: (typeof incident.responsable === 'object' ? incident.responsable?.full_name : incident.responsable) || 'No asignado',
        problem_description: incident.descripcion || '',
      }));
    }
  }, [incident]);

  // Componente para seleccionar imagen de una sección
  const SectionImageSlot = ({ section, label }) => {
    const selectedImageId = formData.section_images[section];
    const selectedImage = images.find(img => img.id === selectedImageId);

    return (
      <div className="space-y-2">
        <label className="text-[10px] font-bold text-gray-500 uppercase tracking-wider px-1">{label}</label>
        <div
          className={`relative h-40 rounded-xl border-2 border-dashed transition-all flex flex-col items-center justify-center p-4 text-center cursor-pointer overflow-hidden ${selectedImage
            ? 'border-blue-500 bg-blue-50/20'
            : 'border-gray-200 bg-gray-50/50 hover:bg-gray-100/50'
            }`}
          onClick={() => {
            // Aquí podríamos abrir un modal para seleccionar de las imágenes subidas
            // Por simplicidad en este paso, permitiremos subir/seleccionar directamente
          }}
        >
          {selectedImage ? (
            <>
              <img
                src={URL.createObjectURL(selectedImage)}
                alt={label}
                className="absolute inset-0 w-full h-full object-cover opacity-80"
              />
              <div className="relative z-10 bg-white/90 px-3 py-1 rounded-full text-[10px] font-bold text-blue-600 shadow-sm">
                Cambiar Imagen
              </div>
              <button
                className="absolute top-2 right-2 z-20 bg-red-500 text-white p-1 rounded-full hover:bg-red-600 shadow-lg"
                onClick={(e) => {
                  e.stopPropagation();
                  handleInputChange('section_images', { ...formData.section_images, [section]: null });
                }}
              >
                <XMarkIcon className="h-3 w-3" />
              </button>
            </>
          ) : (
            <>
              <PhotoIcon className="h-8 w-8 text-gray-300 mb-2" />
              <p className="text-[10px] text-gray-400 font-medium">Click para asignar imagen de referencia ({label})</p>
              <input
                type="file"
                accept="image/*"
                className="absolute inset-0 opacity-0 cursor-pointer"
                onChange={(e) => {
                  const file = e.target.files[0];
                  if (file) {
                    const newId = Date.now();
                    const fileWithId = Object.assign(file, { id: newId });
                    setImages(prev => [...prev, fileWithId]);
                    handleInputChange('section_images', { ...formData.section_images, [section]: newId });
                  }
                }}
              />
            </>
          )}
        </div>
      </div>
    );
  };

  const handleInputChange = (name, value) => {
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleImportClientData = async () => {
    try {
      const { data } = await api.get(`/documents/quality-reports/by-incident/${incidentId}/`);
      if (data.success && data.reports && data.reports.length > 0) {
        // Find latest client report or just latest report
        const clientReport = data.reports.find(r => r.report_type === 'cliente') || data.reports[0];

        if (clientReport) {
          if (!confirm(`Se encontró un reporte previo del ${new Date(clientReport.created_at).toLocaleDateString()}. ¿Desea sobrescribir los datos actuales con la información de ese reporte?`)) return;

          let techDetails = {};
          try {
            techDetails = typeof clientReport.technical_details === 'string'
              ? JSON.parse(clientReport.technical_details)
              : clientReport.technical_details || {};
          } catch (e) { console.error("Error parsing technical details", e); }

          setFormData(prev => ({
            ...prev,
            // Campos de texto directo
            problem_description: clientReport.problem_description || prev.problem_description,
            executive_summary: clientReport.executive_summary || prev.executive_summary,
            root_cause_analysis: clientReport.root_cause_analysis || prev.root_cause_analysis,
            corrective_actions: clientReport.corrective_actions || prev.corrective_actions,
            preventive_measures: clientReport.preventive_measures || prev.preventive_measures,
            recommendations: clientReport.recommendations || prev.recommendations,
            conclusions: clientReport.conclusions || prev.conclusions,

            // Campos técnicos (flatten object)
            // Product
            product_diameter: techDetails.product?.diameter || prev.product_diameter || '',
            product_pn: techDetails.product?.pn || prev.product_pn || '',
            product_sdr: techDetails.product?.sdr || prev.product_sdr || '',
            product_material: techDetails.product?.material || prev.product_material || 'PP-R',
            product_lot: techDetails.product?.lot || prev.product_lot || '',

            // Site
            joining_method: techDetails.site_conditions?.method || prev.joining_method || 'Termofusión',
            ambient_temperature: techDetails.site_conditions?.temperature || prev.ambient_temperature || '',
            tools_status: techDetails.site_conditions?.tools || prev.tools_status || 'OK',
            machine_id: techDetails.site_conditions?.machine_id || prev.machine_id || '',
            applicable_normative: techDetails.site_conditions?.normative || prev.applicable_normative || 'ISO 15874 / NCh 3151',

            // Tests
            visual_inspection: techDetails.test_protocol?.visual || prev.visual_inspection || 'Conforme',
            pressure_test: techDetails.test_protocol?.pressure_test || prev.pressure_test || 'No Realizada',
            test_pressure_bar: techDetails.test_protocol?.pressure_bar || prev.test_pressure_bar || '',
            test_duration_min: techDetails.test_protocol?.duration_min || prev.test_duration_min || '',
            test_result: techDetails.test_protocol?.result || prev.test_result || 'N/A',

            // Lab
            melt_index: techDetails.lab_tests?.melt_index || prev.melt_index || '',
            density: techDetails.lab_tests?.density || prev.density || '',
            tio: techDetails.lab_tests?.tio || prev.tio || '',
            dsc: techDetails.lab_tests?.dsc || prev.dsc || '',
            carbon_black_dispersion: techDetails.lab_tests?.carbon_black_dispersion || prev.carbon_black_dispersion || '',
            carbon_black_percentage: techDetails.lab_tests?.carbon_black_percentage || prev.carbon_black_percentage || '',
            ash_percentage: techDetails.lab_tests?.ash_percentage || prev.ash_percentage || '',
            moisture_percentage: techDetails.lab_tests?.moisture_percentage || prev.moisture_percentage || '',
          }));
          showSuccess("Datos importados del reporte previo exitosamente");
        } else {
          showError("No se encontraron reportes previos para importar");
        }
      } else {
        showError("No hay reportes previos asociados a esta incidencia");
      }
    } catch (error) {
      console.error(error);
      showError("Error al consultar reportes previos");
    }
  };

  const handleAIAnalysis = async () => {
    if (!formData.problem_description) {
      showError("Se requiere una descripción del problema para analizar.");
      return;
    }

    setIsAnalyzing(true);
    try {
      const response = await aiAPI.analyzeCause(formData.problem_description);
      const analysis = response.data;

      setFormData(prev => ({
        ...prev,
        technical_analysis: analysis.analysis || prev.technical_analysis,
        root_cause_analysis: analysis.root_cause || prev.root_cause_analysis,
        recommendations: analysis.recommendations || prev.recommendations,
        conclusions: "Análisis generado mediante inteligencia artificial basado en la evidencia recolectada."
      }));
      showSuccess("Análisis de IA completado exitosamente");
    } catch (error) {
      console.error("AI Analysis error:", error);
      showError("Error al generar análisis con IA");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    if (!incidentId || isNaN(parseInt(incidentId))) {
      showError("ID de incidencia inválido");
      setIsSubmitting(false);
      return;
    }

    try {
      const dataToSend = new FormData();

      // Construcción del objeto técnico limpio (sin nulls/undefined)
      const technicalDetailsObj = {
        client: formData.client_name || '',
        project: formData.project_name || '',
        sap_call_id: formData.sap_call_id || '',
        salesperson: formData.salesperson || '',
        technician: formData.technician || '',
        incident_code: formData.incident_code || '',
        sku: incident?.sku || '-',
        provider: incident?.provider || '-',
        // Campos técnicos avanzados
        product: {
          diameter: formData.product_diameter || '',
          pn: formData.product_pn || '',
          sdr: formData.product_sdr || '',
          material: formData.product_material || 'PP-R',
          lot: formData.product_lot || ''
        },
        site_conditions: {
          method: formData.joining_method || 'Termofusión',
          temperature: formData.ambient_temperature || '',
          tools: formData.tools_status || 'OK',
          machine_id: formData.machine_id || '',
          normative: formData.applicable_normative || 'ISO 15874 / NCh 3151'
        },
        test_protocol: {
          visual: formData.visual_inspection || 'Conforme',
          pressure_test: formData.pressure_test || 'No Realizada',
          pressure_bar: formData.test_pressure_bar || '',
          duration_min: formData.test_duration_min || '',
          result: formData.test_result || 'N/A'
        },
        lab_tests: {
          melt_index: formData.melt_index || '',
          density: formData.density || '',
          tio: formData.tio || '',
          dsc: formData.dsc || '',
          carbon_black_dispersion: formData.carbon_black_dispersion || '',
          carbon_black_percentage: formData.carbon_black_percentage || '',
          ash_percentage: formData.ash_percentage || '',
          moisture_percentage: formData.moisture_percentage || ''
        },
        section_images: formData.section_images
      };

      const payload = {
        related_incident_id: parseInt(incidentId),
        report_type: reportType,
        title: formData.title || `Reporte - ${formData.incident_code}`,
        executive_summary: formData.executive_summary || '',
        problem_description: formData.problem_description || '',
        technical_analysis: formData.technical_analysis || '',
        root_cause_analysis: formData.root_cause_analysis || '',
        corrective_actions: formData.corrective_actions || '',
        preventive_measures: formData.preventive_measures || '',
        recommendations: formData.recommendations || '',
        conclusions: formData.conclusions || '',
        status: formData.status || 'draft',
        internal_notes: formData.internal_notes || '',
        technical_details: JSON.stringify(technicalDetailsObj)
      };

      Object.keys(payload).forEach(key => {
        const value = payload[key];
        if (value !== null && value !== undefined) {
          dataToSend.append(key, value);
        }
      });

      images.forEach(img => {
        // Encontrar si esta imagen está asignada a alguna sección específica
        const sectionKey = Object.keys(formData.section_images).find(key => formData.section_images[key] === img.id);
        if (sectionKey) {
          dataToSend.append(`image_${sectionKey}`, img);
        } else {
          dataToSend.append('images', img);
        }
      });

      const response = await api.post('/documents/quality-reports/', dataToSend);
      const newReport = response.data;
      setCreatedReportId(newReport.id);

      showSuccess('Reporte de calidad guardado. Generando PDF profesional...');

      // AUTO GENERAR PDF PROFESIONAL
      try {
        setIsGeneratingPDF(true);
        await api.post(`/documents/quality-reports/${newReport.id}/generate/`);
        showSuccess('PDF Profesional generado con éxito');
      } catch (pdfErr) {
        console.error('PDF Generation error:', pdfErr);
        showError('Reporte guardado pero hubo un error al generar el PDF');
      } finally {
        setIsGeneratingPDF(false);
      }

      navigate(isInternal ? '/quality-reports/internal' : '/quality-reports/client');
    } catch (error) {
      console.error('Submit error details:', error.response?.data || error.message);
      showError(`Error al crear el reporte: ${error.response?.data?.message || error.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handlePreviewPDF = async () => {
    if (!createdReportId) {
      showError("Debe guardar el reporte antes de previsualizar el PDF");
      return;
    }

    try {
      window.open(`${api.defaults.baseURL}/documents/quality-reports/${createdReportId}/download/`, '_blank');
    } catch (error) {
      showError("Error al abrir el PDF");
    }
  };

  if (incidentLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-gray-500 font-medium animate-pulse">Sincronizando con incidencia...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC] p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header Superior - Industrial Premium */}
        <div className="relative mb-12 pt-6">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600/5 via-indigo-600/5 to-purple-600/5 rounded-3xl blur-3xl -z-10"></div>
          <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
            <div>
              <button
                onClick={() => navigate(-1)}
                className="group flex items-center gap-2 px-4 py-2 rounded-xl bg-white/50 hover:bg-white text-slate-500 hover:text-blue-600 border border-transparent hover:border-blue-100 transition-all duration-300 mb-4 shadow-sm"
              >
                <ArrowLeftIcon className="w-4 h-4 transition-transform group-hover:-translate-x-1" />
                <span className="text-xs font-bold uppercase tracking-wider">Volver</span>
              </button>

              <div className="flex items-center gap-4">
                <div className="p-3 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl shadow-lg shadow-blue-500/30">
                  <ClipboardDocumentCheckIcon className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-black text-slate-800 tracking-tight uppercase">
                    {isInternal ? 'Informe de Calidad Interno' : 'Reporte de Calidad'}
                    <span className="ml-3 px-3 py-1 bg-indigo-50 text-indigo-600 text-[10px] rounded-lg border border-indigo-100 align-middle">
                      {isInternal ? 'Uso Interno' : 'Cliente Final'}
                    </span>
                  </h1>
                  <p className="text-slate-500 font-medium text-sm mt-1 flex items-center gap-2">
                    <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse shadow-sm shadow-blue-500/50"></span>
                    Trazabilidad Activa: <span className="font-mono text-slate-700 bg-slate-100 px-1.5 py-0.5 rounded ml-1">{incident?.code}</span>
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {isInternal && (
                <button
                  onClick={handleImportClientData}
                  type="button"
                  className="flex items-center gap-2 px-4 py-3 bg-white/80 backdrop-blur-sm border border-emerald-100 text-emerald-600 rounded-xl font-bold shadow-sm hover:bg-emerald-50 transition-all text-xs uppercase tracking-wide"
                  title="Precargar datos del reporte de cliente si existe"
                >
                  <ArrowDownTrayIcon className="h-4 w-4" />
                  <span className="hidden sm:inline">Importar Datos</span>
                </button>
              )}
              <button
                onClick={handleAIAnalysis}
                disabled={isAnalyzing}
                className="flex items-center gap-2 px-5 py-3 bg-white/80 backdrop-blur-sm border border-indigo-100 text-indigo-600 rounded-xl font-bold shadow-sm hover:bg-indigo-50 transition-all disabled:opacity-50 text-xs uppercase tracking-wide group"
              >
                {isAnalyzing ? (
                  <ArrowPathIcon className="h-4 w-4 animate-spin" />
                ) : (
                  <SparklesIcon className="h-4 w-4 group-hover:scale-110 transition-transform" />
                )}
                Asistente IA
              </button>
              <button
                form="quality-form"
                type="submit"
                disabled={isSubmitting || isGeneratingPDF}
                className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-bold shadow-lg shadow-blue-500/30 hover:shadow-blue-500/40 hover:scale-[1.02] transition-all disabled:opacity-50 text-xs uppercase tracking-wide"
              >
                {isSubmitting || isGeneratingPDF ? (
                  <ArrowPathIcon className="h-4 w-4 animate-spin" />
                ) : (
                  <CheckCircleIcon className="h-4 w-4" />
                )}
                {isGeneratingPDF ? 'Generando PDF...' : 'Finalizar Reporte'}
              </button>
            </div>
          </div>
        </div>

        <form id="quality-form" onSubmit={handleSubmit}>
          {/* FASE 2: SECCIÓN DE TRAZABILIDAD (WOW Factor con datos reales) */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="md:col-span-2 bg-slate-900/95 backdrop-blur-xl rounded-3xl p-8 text-white shadow-2xl shadow-slate-900/20 relative overflow-hidden group border border-white/10 transition-all hover:scale-[1.01]">
              <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 group-hover:bg-blue-500/20 transition-all duration-700"></div>
              <div className="relative z-10 grid grid-cols-2 gap-8">
                <div className="space-y-6">
                  <div>
                    <p className="text-blue-400 text-[10px] font-black uppercase tracking-widest mb-2 flex items-center gap-2">
                      <BuildingOfficeIcon className="w-3 h-3" />
                      Cliente / Proyecto
                    </p>
                    <p className="text-xl font-bold leading-tight line-clamp-1 text-white">{formData.client_name || '-'}</p>
                    <p className="text-sm text-slate-400 mt-1 line-clamp-1 font-medium">{formData.project_name || '-'}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-white/5 rounded-xl p-3 border border-white/5">
                      <p className="text-slate-400 text-[9px] font-bold uppercase tracking-wider mb-1">ID SAP</p>
                      <p className="text-sm font-mono font-bold text-white tracking-wide">#{formData.sap_doc_num || formData.sap_call_id}</p>
                    </div>
                    <div className="bg-white/5 rounded-xl p-3 border border-white/5">
                      <p className="text-slate-400 text-[9px] font-bold uppercase tracking-wider mb-1">Cód. Incidencia</p>
                      <p className="text-sm font-mono font-bold text-blue-300">{formData.incident_code}</p>
                    </div>
                  </div>
                </div>
                <div className="space-y-6 border-l border-white/10 pl-8">
                  <div>
                    <p className="text-slate-400 text-[9px] font-bold uppercase tracking-wider mb-2">Personal Responsable</p>
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center border border-blue-500/20">
                        <UserIcon className="h-4 w-4 text-blue-400" />
                      </div>
                      <div>
                        <p className="text-xs font-bold text-white">{formData.technician}</p>
                        <p className="text-[10px] text-slate-400 uppercase tracking-wide">Técnico</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-emerald-500/20 rounded-lg flex items-center justify-center border border-emerald-500/20">
                        <BuildingOfficeIcon className="h-4 w-4 text-emerald-400" />
                      </div>
                      <div>
                        <p className="text-xs font-bold text-white">{formData.salesperson}</p>
                        <p className="text-[10px] text-slate-400 uppercase tracking-wide">Vendedor</p>
                      </div>
                    </div>
                  </div>
                  <div className="bg-white/5 rounded-xl p-3 inline-block border border-white/5">
                    <p className="text-slate-400 text-[9px] font-bold uppercase tracking-wider mb-1">Fecha Emisión</p>
                    <p className="text-xs font-bold text-white">{new Date().toLocaleDateString('es-CL', { day: '2-digit', month: 'long', year: 'numeric' })}</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white/60 backdrop-blur-2xl rounded-3xl p-8 shadow-xl shadow-slate-200/50 border border-white/60 flex flex-col justify-center relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-white/40 to-white/0 z-0"></div>
              <div className="relative z-10 space-y-4">
                <GlassInput
                  label="Título Técnico del Informe"
                  value={formData.title}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                  placeholder="Ej: Análisis de Calidad - Tubería PP"
                  required
                />
                <div className="flex gap-3">
                  <div className="flex-1 bg-slate-50/50 rounded-xl px-4 py-3 border border-slate-200/50">
                    <p className="text-[9px] text-slate-400 font-black uppercase mb-1 tracking-wider">Tipo</p>
                    <p className="text-xs font-bold text-slate-700 capitalize">{reportType}</p>
                  </div>
                  <div className="flex-1 bg-blue-50/50 rounded-xl px-4 py-3 border border-blue-100/50">
                    <p className="text-[9px] text-blue-400 font-black uppercase mb-1 tracking-wider">Nivel</p>
                    <p className="text-xs font-bold text-blue-600">Profesional V2</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* NUEVA SECCIÓN: Especificaciones Técnicas del Producto */}
          {/* NUEVA SECCIÓN: Especificaciones Técnicas del Producto */}
          <PremiumSection title="Especificaciones del Producto y Trazabilidad" icon={CubeIcon} color="indigo">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <GlassInput
                label="Diámetro (mm)"
                placeholder="Ej: 32"
                value={formData.product_diameter}
                onChange={(e) => handleInputChange('product_diameter', e.target.value)}
              />
              <GlassInput
                label="PN (Presión)"
                placeholder="Ej: 16"
                value={formData.product_pn}
                onChange={(e) => handleInputChange('product_pn', e.target.value)}
              />
              <GlassInput
                label="SDR"
                placeholder="Ej: 7.4"
                value={formData.product_sdr}
                onChange={(e) => handleInputChange('product_sdr', e.target.value)}
              />
              <div className="space-y-2 group">
                <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest px-1">Material</label>
                <div className="relative">
                  <select
                    value={formData.product_material}
                    onChange={(e) => handleInputChange('product_material', e.target.value)}
                    className="w-full px-4 py-3.5 bg-slate-50/50 border border-slate-200 rounded-xl focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 transition-all text-sm font-medium text-slate-700 appearance-none shadow-sm cursor-pointer hover:bg-white"
                  >
                    <option value="PP-R">PP-R</option>
                    <option value="PP-RCT">PP-RCT</option>
                    <option value="PE-AD">PE-AD</option>
                    <option value="PEX">PEX</option>
                  </select>
                  <ChevronDownIcon className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
                </div>
              </div>
            </div>
            <div className="mt-6">
              <GlassInput
                label="Lote de Fabricación / Código de Trazabilidad"
                icon={ClipboardIcon}
                placeholder="Ingrese el lote impreso en la tubería..."
                value={formData.product_lot}
                onChange={(e) => handleInputChange('product_lot', e.target.value)}
              />
            </div>
          </PremiumSection>

          <PremiumSection title="Condiciones de Instalación" icon={WrenchScrewdriverIcon} color="emerald">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="space-y-2 group">
                <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest px-1">Método de Unión</label>
                <div className="relative">
                  <select
                    value={formData.joining_method}
                    onChange={(e) => handleInputChange('joining_method', e.target.value)}
                    className="w-full px-4 py-3.5 bg-slate-50/50 border border-slate-200 rounded-xl text-sm font-medium text-slate-700 appearance-none shadow-sm cursor-pointer hover:bg-white focus:ring-4 focus:ring-emerald-500/10 focus:border-emerald-500 transition-all"
                  >
                    <option value="Termofusión">Termofusión</option>
                    <option value="Electrofusión">Electrofusión</option>
                    <option value="Mecánico">Mecánico / Roscado</option>
                    <option value="Compresión">Compresión</option>
                  </select>
                  <ChevronDownIcon className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
                </div>
              </div>
              <GlassInput
                label="Temp. Ambiente (°C)"
                placeholder="Ej: 22"
                value={formData.ambient_temperature}
                onChange={(e) => handleInputChange('ambient_temperature', e.target.value)}
              />
              <GlassInput
                label="ID Máquina / Herramienta"
                placeholder="Ej: TF-2025-042"
                value={formData.machine_id}
                onChange={(e) => handleInputChange('machine_id', e.target.value)}
              />
              <GlassInput
                label="Normativa Aplicable"
                placeholder="Ej: ISO 15874"
                value={formData.applicable_normative}
                onChange={(e) => handleInputChange('applicable_normative', e.target.value)}
              />
              <div className="space-y-2 md:col-span-2 lg:col-span-4">
                <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest px-1">Estado Herramientas</label>
                <div className="flex gap-2 bg-slate-50/50 p-1 rounded-xl border border-slate-200/50">
                  {['OK', 'Revisión', 'Falla'].map(status => (
                    <button
                      key={status}
                      type="button"
                      onClick={() => handleInputChange('tools_status', status)}
                      className={`flex-1 py-2 rounded-lg text-[10px] font-black uppercase tracking-wide transition-all ${formData.tools_status === status
                        ? 'bg-white shadow-sm text-emerald-600 border border-emerald-100'
                        : 'text-slate-400 hover:text-slate-600 hover:bg-slate-100/50'
                        }`}
                    >
                      {status}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </PremiumSection>

          {/* NUEVA SECCIÓN: Protocolo de Pruebas y Resultados */}
          {/* NUEVA SECCIÓN: Protocolo de Pruebas y Resultados */}
          <PremiumSection title="Protocolo de Inspección y Pruebas de Terreno" icon={ClipboardDocumentCheckIcon} color="amber">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="space-y-2 group">
                <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest px-1">Inspección Visual</label>
                <div className="relative">
                  <select
                    value={formData.visual_inspection}
                    onChange={(e) => handleInputChange('visual_inspection', e.target.value)}
                    className={`w-full px-4 py-3.5 border rounded-xl text-sm font-bold appearance-none shadow-sm cursor-pointer transition-all ${formData.visual_inspection === 'Conforme' ? 'bg-emerald-50/50 border-emerald-200 text-emerald-700 shadow-emerald-500/10' : 'bg-rose-50/50 border-rose-200 text-rose-700 shadow-rose-500/10'
                      }`}
                  >
                    <option value="Conforme">Conforme</option>
                    <option value="No Conforme">No Conforme</option>
                    <option value="No Aplica">No Aplica</option>
                  </select>
                  <ChevronDownIcon className={`absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 pointer-events-none ${formData.visual_inspection === 'Conforme' ? 'text-emerald-500' : 'text-rose-500'}`} />
                </div>
              </div>
              <div className="space-y-2 group">
                <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest px-1">Prueba de Presión</label>
                <div className="relative">
                  <select
                    value={formData.pressure_test}
                    onChange={(e) => handleInputChange('pressure_test', e.target.value)}
                    className="w-full px-4 py-3.5 bg-slate-50/50 border border-slate-200 rounded-xl text-sm font-medium text-slate-700 appearance-none shadow-sm cursor-pointer hover:bg-white focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 transition-all"
                  >
                    <option value="Realizada">Realizada</option>
                    <option value="No Realizada">No Realizada</option>
                    <option value="Pendiente">Pendiente</option>
                  </select>
                  <ChevronDownIcon className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
                </div>
              </div>
              <GlassInput
                label="Presión de Prueba (Bar)"
                placeholder="Ej: 10"
                value={formData.test_pressure_bar}
                onChange={(e) => handleInputChange('test_pressure_bar', e.target.value)}
              />
              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-gray-500 uppercase tracking-wider px-1">Veredicto de Prueba</label>
                <div className="flex gap-2">
                  {['Aprobado', 'Rechazado', 'N/A'].map(res => (
                    <button
                      key={res}
                      type="button"
                      onClick={() => handleInputChange('test_result', res)}
                      className={`flex-1 py-2 rounded-xl text-xs font-bold transition-all border ${formData.test_result === res
                        ? (res === 'Aprobado' ? 'bg-emerald-600 border-emerald-600 text-white shadow-lg' : res === 'Rechazado' ? 'bg-red-600 border-red-600 text-white shadow-lg' : 'bg-slate-600 border-slate-600 text-white shadow-lg')
                        : 'bg-white border-gray-200 text-gray-400 hover:border-gray-300'
                        }`}
                    >
                      {res}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </PremiumSection>

          {/* NUEVA SECCIÓN: Ensayos de Laboratorio */}
          <PremiumSection title="Ensayos de Laboratorio y Análisis de Polímeros" icon={BeakerIcon} color="purple">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <GlassInput
                label="Melt Index (g/10 min)"
                placeholder="Ej: 0.35"
                value={formData.melt_index}
                onChange={(e) => handleInputChange('melt_index', e.target.value)}
              />
              <GlassInput
                label="Densidad (g/cm³)"
                placeholder="Ej: 0.905"
                value={formData.density}
                onChange={(e) => handleInputChange('density', e.target.value)}
              />
              <GlassInput
                label="TIO (min)"
                placeholder="Ej: > 20"
                value={formData.tio}
                onChange={(e) => handleInputChange('tio', e.target.value)}
              />
              <GlassInput
                label="DSC (°C)"
                placeholder="Ej: 145"
                value={formData.dsc}
                onChange={(e) => handleInputChange('dsc', e.target.value)}
              />
              <GlassInput
                label="Dispersión Negro Humo"
                placeholder="Ej: Grado 1-2"
                value={formData.carbon_black_dispersion}
                onChange={(e) => handleInputChange('carbon_black_dispersion', e.target.value)}
              />
              <GlassInput
                label="% Negro de Humo"
                placeholder="Ej: 2.2%"
                value={formData.carbon_black_percentage}
                onChange={(e) => handleInputChange('carbon_black_percentage', e.target.value)}
              />
              <GlassInput
                label="% Cenizas"
                placeholder="Ej: 0.05%"
                value={formData.ash_percentage}
                onChange={(e) => handleInputChange('ash_percentage', e.target.value)}
              />
              <GlassInput
                label="% Humedad"
                placeholder="Ej: < 0.02%"
                value={formData.moisture_percentage}
                onChange={(e) => handleInputChange('moisture_percentage', e.target.value)}
              />
            </div>
            <div className="mt-8 border-t border-gray-50 pt-6">
              <SectionImageSlot section="lab_tests" label="Captura/Gráfico de Ensayos" />
            </div>
          </PremiumSection>

          {/* NUEVA SECCIÓN: Documentación Visual Intercalada */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            <SectionImageSlot section="product" label="Img. Producto / Lote" />
            <SectionImageSlot section="site_conditions" label="Img. Instalación" />
            <SectionImageSlot section="test_protocol" label="Img. Prueba Presión" />
            <SectionImageSlot section="conclusions" label="Img. Conclusiones" />
          </div>

          {/* Sección: Análisis Técnico */}
          <PremiumSection title="Análisis y Hallazgos Técnicos" icon={WrenchScrewdriverIcon} color="blue">
            <div className="grid grid-cols-1 gap-6">
              <GlassTextarea
                label="Resumen Ejecutivo"
                icon={DocumentTextIcon}
                placeholder="Breve descripción del problema y la conclusión principal para gerencia..."
                value={formData.executive_summary}
                onChange={(e) => handleInputChange('executive_summary', e.target.value)}
                rows={2}
              />
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <GlassTextarea
                  label="Descripción Detallada del Problema"
                  icon={ClipboardDocumentListIcon}
                  value={formData.problem_description}
                  onChange={(e) => handleInputChange('problem_description', e.target.value)}
                  required
                />
                <GlassTextarea
                  label="Análisis Técnico"
                  icon={BeakerIcon}
                  placeholder="Detalle de las pruebas realizadas, mediciones y observaciones técnicas..."
                  value={formData.technical_analysis}
                  onChange={(e) => handleInputChange('technical_analysis', e.target.value)}
                />
              </div>
              <GlassTextarea
                label="Análisis de Causa Raíz (Root Cause)"
                icon={MagnifyingGlassIcon}
                placeholder="Identificación del origen del problema tras la investigación..."
                value={formData.root_cause_analysis}
                onChange={(e) => handleInputChange('root_cause_analysis', e.target.value)}
                rows={2}
              />
            </div>
          </PremiumSection>

          {/* Sección: Acciones y Mejoras */}
          <PremiumSection title="Acciones y Recomendaciones" icon={CheckCircleIcon} color="indigo">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <GlassTextarea
                label="Acciones Correctivas Tomadas"
                placeholder="¿Qué se hizo para solucionar el problema inmediato?"
                value={formData.corrective_actions}
                onChange={(e) => handleInputChange('corrective_actions', e.target.value)}
              />
              <GlassTextarea
                label="Medidas Preventivas Sugeridas"
                placeholder="¿Cómo evitamos que vuelva a suceder?"
                value={formData.preventive_measures}
                onChange={(e) => handleInputChange('preventive_measures', e.target.value)}
              />
              <GlassTextarea
                label="Recomendaciones Técnicas"
                placeholder="Sugerencias adicionales para el cliente/proveedor..."
                value={formData.recommendations}
                onChange={(e) => handleInputChange('recommendations', e.target.value)}
              />
              <GlassTextarea
                label="Conclusiones Finales"
                placeholder="Cierre y veredicto final del departamento de Calidad..."
                value={formData.conclusions}
                onChange={(e) => handleInputChange('conclusions', e.target.value)}
              />
              {isInternal && (
                <div className="md:col-span-2">
                  <GlassTextarea
                    label="Notas Internas Confidenciales"
                    icon={ExclamationTriangleIcon}
                    placeholder="Observaciones privadas que NO aparecerán en el reporte del cliente..."
                    value={formData.internal_notes}
                    onChange={(e) => handleInputChange('internal_notes', e.target.value)}
                    rows={2}
                  />
                </div>
              )}
            </div>
          </PremiumSection>

          {/* Sección: Evidencia Fotográfica (Sincronizada con Incidencia) */}
          <PremiumSection title="Evidencia Fotográfica" icon={CameraIcon} color="slate">
            {incidentImages && incidentImages.length > 0 && (
              <div className="mb-10">
                <h4 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-6 px-1">Imágenes de la Incidencia (Referencia)</h4>
                <IncidentImagesViewer incidentId={incidentId} images={incidentImages} />
              </div>
            )}

            <div className="space-y-6">
              <label className="block text-sm font-bold text-gray-700 px-1">Adjuntar Nuevas Imágenes de Calidad</label>
              <div className="border-4 border-dashed border-gray-100 rounded-[2rem] p-12 text-center group hover:border-blue-200 hover:bg-blue-50/50 transition-all duration-500 cursor-pointer relative">
                <input
                  type="file"
                  multiple
                  accept="image/*"
                  onChange={(e) => setImages(prev => [...prev, ...Array.from(e.target.files)])}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                <div className="flex flex-col items-center">
                  <div className="p-5 bg-blue-50 rounded-2xl mb-6 group-hover:scale-110 transition-transform duration-500">
                    <PhotoIcon className="h-10 w-10 text-blue-600" />
                  </div>
                  <p className="text-xl font-bold text-gray-900 mb-2">Subir nuevas fotos para el informe</p>
                  <p className="text-gray-400 font-medium tracking-tight">Formatos: JPG, PNG • Máx 10MB por archivo</p>
                </div>
              </div>

              {images.length > 0 && (
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6 pt-6">
                  {images.map((img, idx) => (
                    <div key={idx} className="relative aspect-square group rounded-[1.5rem] overflow-hidden shadow-lg">
                      <img
                        src={URL.createObjectURL(img)}
                        alt={`New ${idx}`}
                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                      />
                      <button
                        type="button"
                        onClick={() => setImages(prev => prev.filter((_, i) => i !== idx))}
                        className="absolute top-2 right-2 p-2 bg-red-500 text-white rounded-xl shadow-lg opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <XMarkIcon className="h-4 w-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </PremiumSection>

          {/* Botones de Acción Inferiores */}
          <div className="flex items-center justify-between py-8 border-t border-gray-100 mt-8">
            <div className="flex gap-3">
              {createdReportId && (
                <button
                  type="button"
                  onClick={handlePreviewPDF}
                  className="px-6 py-3 bg-slate-100 text-slate-700 rounded-xl font-bold hover:bg-slate-200 transition-all flex items-center gap-2 text-sm border border-slate-200"
                >
                  <DocumentTextIcon className="h-4 w-4" />
                  Ver PDF Generado
                </button>
              )}
            </div>

            <div className="flex gap-4">
              <button
                type="button"
                onClick={() => navigate(-1)}
                className="px-6 py-3 bg-white text-gray-500 rounded-xl font-bold hover:bg-gray-50 transition-all text-sm"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={isSubmitting || isGeneratingPDF}
                className="px-10 py-3 bg-blue-600 text-white rounded-xl font-bold shadow-lg shadow-blue-200/50 hover:bg-blue-700 transition-all disabled:opacity-50 text-sm flex items-center gap-2"
              >
                {isSubmitting || isGeneratingPDF ? (
                  <ArrowPathIcon className="h-4 w-4 animate-spin" />
                ) : (
                  <CheckCircleIcon className="h-4 w-4" />
                )}
                {isSubmitting ? 'Guardando...' : isGeneratingPDF ? 'Generando PDF...' : 'Finalizar y Guardar'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default QualityReportForm;