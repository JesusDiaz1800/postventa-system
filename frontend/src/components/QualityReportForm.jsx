import React, { useState, useEffect } from 'react';
import { 
  PlusIcon, 
  XMarkIcon,
  CloudArrowUpIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';

// Modal unificado para crear reportes - FORMULARIO SIMPLIFICADO CON PRECARGA
const QualityReportForm = ({ incidents, onSubmit, onClose, reportType = "cliente" }) => {
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

  const [selectedIncident, setSelectedIncident] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState({});

  // Precargar datos de la incidencia cuando se selecciona
  useEffect(() => {
    if (formData.incidentId && incidents) {
      const incidentsArray = incidents?.data?.results || incidents?.results || incidents || [];
      const incident = incidentsArray.find(inc => inc.id === parseInt(formData.incidentId));
      
      if (incident) {
        setSelectedIncident(incident);
        setFormData(prev => ({
          ...prev,
          // Precargar con datos de la incidencia
          title: `Reporte de Calidad - ${incident.code}`,
          description: `Reporte de calidad relacionado con la incidencia ${incident.code}: ${incident.title || incident.cliente}`,
          client_contact: incident.cliente || '',
          location: incident.obra || incident.proyecto || '',
          responsible_person: incident.responsible_person || '',
          department: incident.department || 'Control de Calidad',
          follow_up_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 7 días después
          estimated_completion: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 14 días después
        }));
      }
    }
  }, [formData.incidentId, incidents]);

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

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.incidentId) newErrors.incidentId = 'Debe seleccionar una incidencia';
    if (!formData.title.trim()) newErrors.title = 'El título es obligatorio';
    if (!formData.description.trim()) newErrors.description = 'La descripción es obligatoria';
    if (!formData.findings.trim()) newErrors.findings = 'Los hallazgos son obligatorios';
    if (!formData.recommendations.trim()) newErrors.recommendations = 'Las recomendaciones son obligatorias';
    if (!formData.category) newErrors.category = 'La categoría es obligatoria';
    if (!formData.severity) newErrors.severity = 'La severidad es obligatoria';
    if (!formData.responsible_person.trim()) newErrors.responsible_person = 'La persona responsable es obligatoria';
    if (!formData.department.trim()) newErrors.department = 'El departamento es obligatorio';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
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

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-6xl w-full max-h-[95vh] overflow-hidden">
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
        </div>
        
        {/* Content */}
        <div className="p-8 max-h-[70vh] overflow-y-auto">
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Información Básica */}
            <div className="bg-blue-50 p-6 rounded-lg">
              <h4 className="text-lg font-semibold text-blue-900 mb-4">Información Básica</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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
              </div>

              <div className="mt-4">
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

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
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

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Categoría
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
              </div>
            </div>

            {/* Análisis Técnico */}
            <div className="bg-green-50 p-6 rounded-lg">
              <h4 className="text-lg font-semibold text-green-900 mb-4">Análisis Técnico</h4>
              <div className="space-y-4">
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
            </div>

            {/* Clasificación y Evaluación */}
            <div className="bg-yellow-50 p-6 rounded-lg">
              <h4 className="text-lg font-semibold text-yellow-900 mb-4">Clasificación y Evaluación</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
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
              </div>

              <div className="mt-4">
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

            {/* Responsabilidades y Recursos */}
            <div className="bg-purple-50 p-6 rounded-lg">
              <h4 className="text-lg font-semibold text-purple-900 mb-4">Responsabilidades y Recursos</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
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

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
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

            {/* Acciones y Documentación */}
            <div className="bg-indigo-50 p-6 rounded-lg">
              <h4 className="text-lg font-semibold text-indigo-900 mb-4">Acciones y Documentación</h4>
              <div className="space-y-4">
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
            </div>

            {/* Footer */}
            <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
              <button
                type="button"
                onClick={onClose}
                className="px-6 py-3 text-sm font-semibold text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 transition-colors duration-200"
              >
                Cancelar
              </button>
              
              <button
                type="submit"
                disabled={isSubmitting}
                className="px-8 py-3 text-sm font-semibold text-white bg-green-600 hover:bg-green-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
              >
                {isSubmitting ? 'Creando...' : 'Crear Reporte'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default QualityReportForm;
