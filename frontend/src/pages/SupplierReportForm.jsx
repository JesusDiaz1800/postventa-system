import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import {
  ArrowLeftIcon,
  DocumentTextIcon,
  BuildingOfficeIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  PhotoIcon,
  XMarkIcon,
  PaperAirplaneIcon,
  ChevronDownIcon,
  BeakerIcon,
  WrenchScrewdriverIcon,
  ClipboardIcon,
  CalendarDaysIcon,
  TrashIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

// Componente de sección premium/wow (Reutilizado para consistencia)
const PremiumSection = ({ title, icon: Icon, children, defaultOpen = true, color = 'teal' }) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  const colorClasses = {
    blue: 'from-blue-600 to-indigo-700',
    teal: 'from-teal-600 to-emerald-700',
    amber: 'from-amber-600 to-orange-700',
    purple: 'from-purple-600 to-violet-700',
    rose: 'from-rose-600 to-pink-700'
  };

  return (
    <div className="bg-white/60 backdrop-blur-2xl rounded-3xl border border-white/60 shadow-xl shadow-slate-200/50 overflow-hidden transition-all duration-300 mb-6 group hover:shadow-2xl hover:shadow-slate-300/50">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={`w-full px-6 py-5 flex items-center justify-between bg-gradient-to-r ${colorClasses[color] || colorClasses.teal} text-white transition-all relative overflow-hidden`}
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
        <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-teal-600 transition-colors">
          <Icon className="h-5 w-5" />
        </div>
      )}
      <input
        {...props}
        className={`w-full ${Icon ? 'pl-12' : 'px-4'} py-3.5 bg-slate-50/50 border border-slate-200 rounded-xl focus:bg-white focus:border-teal-500 focus:ring-4 focus:ring-teal-500/10 transition-all duration-300 placeholder:text-slate-400 font-medium text-sm text-slate-700 shadow-sm`}
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
        <div className="absolute left-4 top-4 text-slate-400 group-focus-within:text-teal-600 transition-colors">
          <Icon className="h-5 w-5" />
        </div>
      )}
      <textarea
        {...props}
        rows={rows}
        className={`w-full ${Icon ? 'pl-12' : 'px-4'} py-3.5 bg-slate-50/50 border border-slate-200 rounded-xl focus:bg-white focus:border-teal-500 focus:ring-4 focus:ring-teal-500/10 transition-all duration-300 placeholder:text-slate-400 font-medium text-sm text-slate-700 resize-none shadow-sm`}
      />
    </div>
  </div>
);

const SupplierReportForm = () => {
  const { incidentId: paramIncidentId } = useParams();
  const [searchParams] = useSearchParams();
  const incidentId = paramIncidentId || searchParams.get('incident_id');
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    // Datos Generales Proveedor
    supplier_name: '',
    supplier_email: '',
    supplier_contact: '',
    contact_phone: '',

    // Descripción del Problema
    subject: '',
    problem_description: '',
    recommendations: '', // Acción Esperada
    deadline_days: '5',
    additional_notes: '',

    // Datos Técnicos (Para JSON technical_details)
    // Producto
    product_diameter: '',
    product_pn: '',
    product_sdr: '',
    product_material: 'PP-R',
    product_lot: '',

    // Condiciones
    joining_method: 'Termofusión',
    ambient_temperature: '',
    machine_id: '',

    // Ensayos y Pruebas
    visual_inspection: 'No Conforme',
    melt_index: '',
    density: '',
    test_result_summary: ''
  });

  const [images, setImages] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false);

  // Obtener datos de la incidencia
  const { data: incident, isLoading } = useQuery({
    queryKey: ['incident', incidentId],
    queryFn: async () => {
      const response = await api.get(`/incidents/${incidentId}/`);
      return response.data;
    },
    enabled: !!incidentId
  });

  // Pre-cargar datos
  useEffect(() => {
    if (incident) {
      setFormData(prev => ({
        ...prev,
        supplier_name: incident.provider || '',
        subject: `Reclamo de Calidad - ${incident.code} - ${incident.sku || ''}`,
        problem_description: incident.descripcion || '',
        product_lot: incident.lote || ''
      }));
    }
  }, [incident]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleImageUpload = (e) => {
    const files = Array.from(e.target.files);
    const newImages = files.map(file => ({
      file,
      id: Date.now() + Math.random(),
      preview: URL.createObjectURL(file)
    }));
    setImages(prev => [...prev, ...newImages]);
  };

  const removeImage = (imageId) => {
    setImages(prev => {
      const img = prev.find(i => i.id === imageId);
      if (img) URL.revokeObjectURL(img.preview);
      return prev.filter(i => i.id !== imageId);
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.supplier_name || !formData.problem_description) {
      toast.error('Por favor completa los campos requeridos');
      return;
    }

    setIsSubmitting(true);

    try {
      // 1. Construir objeto technical_details con la estructura esperada por backend
      const technical_details = {
        product: {
          diameter: formData.product_diameter,
          pn: formData.product_pn,
          sdr: formData.product_sdr,
          material: formData.product_material,
          lot: formData.product_lot
        },
        site_conditions: {
          method: formData.joining_method,
          temperature: formData.ambient_temperature,
          machine_id: formData.machine_id
        },
        lab_tests: {
          melt_index: formData.melt_index,
          density: formData.density,
          visual_inspection: formData.visual_inspection
        },
        deadline_days: formData.deadline_days,
        additional_notes: formData.additional_notes
      };

      const submitData = new FormData();
      submitData.append('related_incident_id', parseInt(incidentId));
      submitData.append('supplier_name', formData.supplier_name);
      submitData.append('supplier_email', formData.supplier_email);
      submitData.append('supplier_contact', formData.supplier_contact);
      submitData.append('subject', formData.subject);
      submitData.append('problem_description', formData.problem_description);
      submitData.append('recommendations', formData.recommendations); // Acción esperada
      submitData.append('technical_details', JSON.stringify(technical_details));

      // Adjuntar imágenes
      images.forEach(img => {
        submitData.append('images', img.file);
      });

      // 2. Enviar reporte
      const response = await api.post('/documents/supplier-reports/', submitData);
      const newReportId = response.data.id;

      // 3. Generar PDF
      setIsGeneratingPDF(true);
      try {
        await api.post(`/documents/supplier-reports/${newReportId}/generate/`);
        toast.success('Reporte y PDF generados exitosamente');
      } catch (pdfError) {
        console.error("Error generando PDF:", pdfError);
        toast.error('Reporte guardado, pero falló la generación del PDF');
      }

      setTimeout(() => {
        navigate('/supplier-reports');
      }, 1500);

    } catch (error) {
      console.error('Error:', error);
      toast.error('Error al crear el reporte');
    } finally {
      setIsSubmitting(false);
      setIsGeneratingPDF(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-16 h-16 border-4 border-teal-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-gray-500 font-medium animate-pulse">Cargando datos...</p>
        </div>
      </div>
    );
  }

  if (!incidentId) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <ExclamationTriangleIcon className="h-16 w-16 text-amber-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-gray-900 mb-2">Incidencia no especificada</h2>
          <button onClick={() => navigate('/supplier-reports')} className="mt-4 px-4 py-2 bg-teal-600 text-white rounded-lg">Volver</button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC] p-4 md:p-8">
      <div className="max-w-5xl mx-auto">
        {/* Header Superior - Industrial Premium */}
        <div className="relative mb-8 pt-6">
          <div className="absolute inset-0 bg-gradient-to-r from-teal-600/5 via-emerald-600/5 to-cyan-600/5 rounded-3xl blur-3xl -z-10"></div>
          <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
            <div>
              <button
                onClick={() => navigate(-1)}
                className="group flex items-center gap-2 px-4 py-2 rounded-xl bg-white/50 hover:bg-white text-slate-500 hover:text-teal-600 border border-transparent hover:border-teal-100 transition-all duration-300 mb-4 shadow-sm"
              >
                <ArrowLeftIcon className="w-4 h-4 transition-transform group-hover:-translate-x-1" />
                <span className="text-xs font-bold uppercase tracking-wider">Volver</span>
              </button>

              <div className="flex items-center gap-4">
                <div className="p-3 bg-gradient-to-br from-teal-600 to-emerald-600 rounded-2xl shadow-lg shadow-teal-500/30">
                  <BuildingOfficeIcon className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-black text-slate-800 tracking-tight uppercase">
                    Reporte a Proveedor
                    <span className="ml-3 px-3 py-1 bg-teal-50 text-teal-600 text-[10px] rounded-lg border border-teal-100 align-middle">
                      Reclamo
                    </span>
                  </h1>
                  <p className="text-slate-500 font-medium text-sm mt-1 flex items-center gap-2">
                    <span className="w-2 h-2 bg-teal-500 rounded-full animate-pulse shadow-sm shadow-teal-500/50"></span>
                    Incidencia Vinculada: <span className="font-mono text-slate-700 bg-slate-100 px-1.5 py-0.5 rounded ml-1">{incident?.code}</span>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          {/* SECCIÓN 1: DATOS DEL PROVEEDOR */}
          <PremiumSection title="Información del Proveedor" icon={BuildingOfficeIcon} color="teal">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <GlassInput
                label="Nombre del Proveedor"
                value={formData.supplier_name}
                onChange={handleChange}
                name="supplier_name"
                required
                icon={BuildingOfficeIcon}
              />
              <GlassInput
                label="Email Corporativo"
                value={formData.supplier_email}
                onChange={handleChange}
                name="supplier_email"
                type="email"
              />
              <GlassInput
                label="Persona de Contacto"
                value={formData.supplier_contact}
                onChange={handleChange}
                name="supplier_contact"
              />
              <GlassInput
                label="Teléfono"
                value={formData.contact_phone}
                onChange={handleChange}
                name="contact_phone"
              />
            </div>
          </PremiumSection>

          {/* SECCIÓN 2: DETALLES TÉCNICOS DEL PRODUCTO */}
          <PremiumSection title="Especificaciones Técnicas del Producto" icon={ClipboardIcon} color="blue">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <GlassInput
                label="Diámetro (mm)"
                placeholder="Ej: 32"
                value={formData.product_diameter}
                onChange={handleChange}
                name="product_diameter"
              />
              <GlassInput
                label="PN (Presión)"
                placeholder="Ej: 16"
                value={formData.product_pn}
                onChange={handleChange}
                name="product_pn"
              />
              <GlassInput
                label="SDR"
                placeholder="Ej: 7.4"
                value={formData.product_sdr}
                onChange={handleChange}
                name="product_sdr"
              />
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-gray-500 uppercase tracking-wider px-1">Material</label>
                <select
                  name="product_material"
                  value={formData.product_material}
                  onChange={handleChange}
                  className="w-full px-4 py-2.5 bg-gray-50/50 border border-gray-200 rounded-xl focus:ring-4 focus:ring-blue-500/5 transition-all text-sm font-medium"
                >
                  <option value="PP-R">PP-R</option>
                  <option value="PP-RCT">PP-RCT</option>
                  <option value="PE-AD">PE-AD</option>
                  <option value="PEX">PEX</option>
                  <option value="PVC">PVC</option>
                </select>
              </div>
            </div>
            <div className="mt-4">
              <GlassInput
                label="Lote de Fabricación / Trazabilidad"
                value={formData.product_lot}
                onChange={handleChange}
                name="product_lot"
                placeholder="Lote impreso en el tubo o accesorio"
              />
            </div>
          </PremiumSection>

          {/* SECCIÓN 3: ANÁLISIS DEL PROBLEMA */}
          <PremiumSection title="Detalle del Reclamo y Evidencia" icon={ExclamationTriangleIcon} color="amber">
            <GlassInput
              label="Asunto del Reclamo"
              value={formData.subject}
              onChange={handleChange}
              name="subject"
              required
              className="mb-4"
            />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
              <GlassTextarea
                label="Descripción Detallada de la No Conformidad"
                value={formData.problem_description}
                onChange={handleChange}
                name="problem_description"
                rows={6}
                required
                icon={DocumentTextIcon}
              />
              <div className="space-y-4">
                <GlassTextarea
                  label="Acción Correctiva Esperada"
                  value={formData.recommendations}
                  onChange={handleChange}
                  name="recommendations"
                  rows={3}
                  placeholder="¿Qué solución solicita al proveedor?"
                />
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-xs font-bold text-gray-500 uppercase tracking-wider px-1">Plazo Respuesta</label>
                    <select
                      name="deadline_days"
                      value={formData.deadline_days}
                      onChange={handleChange}
                      className="w-full px-4 py-2.5 bg-gray-50/50 border border-gray-200 rounded-xl"
                    >
                      <option value="3">3 días hábiles</option>
                      <option value="5">5 días hábiles</option>
                      <option value="7">7 días hábiles</option>
                      <option value="15">15 días hábiles</option>
                    </select>
                  </div>
                  <GlassInput
                    label="Normativa Ref."
                    value={formData.additional_notes}
                    onChange={handleChange}
                    name="additional_notes"
                    placeholder="Ej: ISO 15874"
                  />
                </div>
              </div>
            </div>

            {/* Subida de Imágenes */}
            <div className="mt-6 p-4 bg-gray-50 rounded-xl border border-dashed border-gray-300">
              <div className="flex items-center gap-2 mb-3">
                <PhotoIcon className="h-5 w-5 text-gray-400" />
                <span className="text-sm font-bold text-gray-600">Evidencia Fotográfica</span>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {/* Botón Upload */}
                <label className="aspect-square flex flex-col items-center justify-center bg-white border-2 border-dashed border-teal-200 rounded-xl cursor-pointer hover:bg-teal-50 transition-colors">
                  <PhotoIcon className="h-8 w-8 text-teal-400 mb-1" />
                  <span className="text-xs font-bold text-teal-600">Agregar</span>
                  <input type="file" multiple accept="image/*" onChange={handleImageUpload} className="hidden" />
                </label>

                {/* Lista Imágenes */}
                {images.map(img => (
                  <div key={img.id} className="relative group aspect-square rounded-xl overflow-hidden shadow-sm">
                    <img src={img.preview} alt="preview" className="w-full h-full object-cover" />
                    <button
                      type="button"
                      onClick={() => removeImage(img.id)}
                      className="absolute top-1 right-1 p-1 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <XMarkIcon className="h-3 w-3" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </PremiumSection>

          {/* DATOS DE LABORATORIO (OPCIONAL) */}
          <PremiumSection title="Datos Adicionales de Laboratorio (Opcional)" icon={BeakerIcon} color="purple" defaultOpen={false}>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <GlassInput
                label="Melt Index"
                value={formData.melt_index}
                onChange={handleChange}
                name="melt_index"
              />
              <GlassInput
                label="Densidad"
                value={formData.density}
                onChange={handleChange}
                name="density"
              />
              <div className="space-y-1.5 col-span-2">
                <label className="text-xs font-bold text-gray-500 uppercase tracking-wider px-1">Inspección Visual</label>
                <select
                  name="visual_inspection"
                  value={formData.visual_inspection}
                  onChange={handleChange}
                  className="w-full px-4 py-2.5 bg-gray-50/50 border border-gray-200 rounded-xl"
                >
                  <option value="Conforme">Conforme</option>
                  <option value="No Conforme">No Conforme (Defectos visibles)</option>
                  <option value="Dudoso">Requiere Análisis Profundo</option>
                </select>
              </div>
            </div>
          </PremiumSection>


          {/* Botones Finales */}
          <div className="flex justify-end gap-4 mt-8 pb-12">
            <button
              type="button"
              onClick={() => navigate('/supplier-reports')}
              className="px-6 py-4 rounded-2xl border border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-50 text-[10px] font-black uppercase tracking-widest transition-all"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isSubmitting || isGeneratingPDF}
              className="px-8 py-4 bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-700 hover:to-emerald-700 text-white rounded-2xl shadow-xl shadow-teal-500/20 text-[10px] font-black uppercase tracking-widest transition-all hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {(isSubmitting || isGeneratingPDF) && <div className="animate-spin h-3 w-3 border-2 border-white border-t-transparent rounded-full" />}
              {isGeneratingPDF ? 'Generando PDF...' : 'Crear Reporte Oficial'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SupplierReportForm;