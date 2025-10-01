import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { documentsAPI, incidentsAPI } from '../services/api';
import { brandConfig } from '../config/brand';
import {
  DocumentTextIcon,
  ArrowLeftIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  UserIcon,
  BuildingOffice2Icon,
  TagIcon,
  DocumentDuplicateIcon,
} from '@heroicons/react/24/outline';

const CreateDocument = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    template_type: '',
    incident_id: '',
    title: '',
    content: '',
    status: 'draft',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { data: incidents } = useQuery({
    queryKey: ['incidents', 'open'],
    queryFn: () => incidentsAPI.list({ estado: 'abierto' }),
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Si es plantilla de Polifusión, redirigir al formulario especial
    if (formData.template_type === 'polifusion_lab') {
      navigate('/documents/polifusion-lab-report');
      return;
    }
    
    if (formData.template_type === 'polifusion_incident') {
      navigate('/documents/polifusion-incident-report');
      return;
    }
    
    if (formData.template_type === 'polifusion_visit') {
      navigate('/documents/polifusion-visit-report');
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      await documentsAPI.create(formData);
      navigate('/documents');
    } catch (error) {
      console.error('Error creating document:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getTemplateInfo = (templateType) => {
    const templates = {
      polifusion_lab: {
        name: 'Informe de Laboratorio',
        description: 'Análisis técnico de muestras y ensayos de laboratorio',
        icon: DocumentTextIcon,
        color: 'blue',
      },
      polifusion_incident: {
        name: 'Informe de Incidencia',
        description: 'Registro de problemas y acciones correctivas',
        icon: ExclamationTriangleIcon,
        color: 'orange',
      },
      polifusion_visit: {
        name: 'Reporte de Visita',
        description: 'Evaluación de instalación y servicio técnico',
        icon: DocumentDuplicateIcon,
        color: 'purple',
      },
    };
    
    return templates[templateType] || {
      name: 'Plantilla',
      description: 'Selecciona una plantilla',
      icon: DocumentTextIcon,
      color: 'gray',
    };
  };

  const selectedTemplate = getTemplateInfo(formData.template_type);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="relative">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 via-purple-600/10 to-indigo-600/10 rounded-3xl blur-3xl"></div>
        <div className="relative bg-white/80 backdrop-blur-sm rounded-2xl p-8 border border-white/20 shadow-xl">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/documents')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-white/60 rounded-lg transition-all duration-200"
            >
              <ArrowLeftIcon className="h-6 w-6" />
            </button>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
                Nuevo Documento
              </h1>
              <p className="mt-2 text-lg text-gray-600">
                Crear un nuevo documento usando plantillas
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Template Selection */}
        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600/5 via-purple-600/5 to-indigo-600/5 rounded-3xl blur-3xl"></div>
          <div className="relative bg-white/90 backdrop-blur-sm rounded-2xl p-8 border border-white/20 shadow-xl">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-blue-500/10 rounded-xl">
                <TagIcon className="h-6 w-6 text-blue-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Selección de Plantilla</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[
                { value: 'polifusion_lab', name: 'Informe de Laboratorio', description: 'Análisis técnico de muestras y ensayos', special: true },
                { value: 'polifusion_incident', name: 'Informe de Incidencia', description: 'Registro de problemas y acciones correctivas', special: true },
                { value: 'polifusion_visit', name: 'Reporte de Visita', description: 'Evaluación de instalación y servicio técnico', special: true },
              ].map((template) => (
                <div
                  key={template.value}
                  className={`p-6 rounded-xl border-2 cursor-pointer transition-all duration-200 hover:scale-105 ${
                    formData.template_type === template.value
                      ? 'border-blue-500 bg-blue-50 shadow-lg'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setFormData(prev => ({ ...prev, template_type: template.value }))}
                >
                  <div className="flex items-center space-x-3 mb-3">
                    <div className={`p-2 rounded-lg ${
                      formData.template_type === template.value ? 'bg-blue-500' : 'bg-gray-500'
                    }`}>
                      <DocumentTextIcon className="h-5 w-5 text-white" />
                    </div>
                    <h3 className="font-semibold text-gray-900">{template.name}</h3>
                  </div>
                  <p className="text-sm text-gray-600">{template.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Document Details */}
        {formData.template_type && (
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-green-600/5 via-emerald-600/5 to-teal-600/5 rounded-3xl blur-3xl"></div>
            <div className="relative bg-white/90 backdrop-blur-sm rounded-2xl p-8 border border-white/20 shadow-xl">
              <div className="flex items-center space-x-3 mb-6">
                <div className="p-3 bg-green-500/10 rounded-xl">
                  <DocumentTextIcon className="h-6 w-6 text-green-600" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900">Detalles del Documento</h2>
              </div>
              
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Título del Documento *
                    </label>
                    <input
                      type="text"
                      name="title"
                      value={formData.title}
                      onChange={handleInputChange}
                      required
                      className="w-full px-4 py-3 border border-gray-200 rounded-xl bg-white/60 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200"
                      placeholder="Ingrese el título del documento"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Incidente Relacionado
                    </label>
                    <select
                      name="incident_id"
                      value={formData.incident_id}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 border border-gray-200 rounded-xl bg-white/60 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200"
                    >
                      <option value="">Sin incidente relacionado</option>
                      {incidents?.results?.map(incident => (
                        <option key={incident.id} value={incident.id}>
                          {incident.code} - {incident.cliente} ({incident.obra}) - {incident.categoria}
                        </option>
                      ))}
                    </select>
                    {incidents?.results?.length === 0 && (
                      <p className="text-sm text-gray-500 mt-2">
                        No hay incidencias abiertas disponibles
                      </p>
                    )}
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Contenido del Documento *
                  </label>
                  <textarea
                    name="content"
                    value={formData.content}
                    onChange={handleInputChange}
                    required
                    rows={12}
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl bg-white/60 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200 resize-none"
                    placeholder="Escriba el contenido del documento aquí..."
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Estado
                  </label>
                  <select
                    name="status"
                    value={formData.status}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl bg-white/60 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200"
                  >
                    <option value="draft">Borrador</option>
                    <option value="generated">Generado</option>
                    <option value="sent">Enviado</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Template Preview */}
        {formData.template_type && (
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-purple-600/5 via-violet-600/5 to-indigo-600/5 rounded-3xl blur-3xl"></div>
            <div className="relative bg-white/90 backdrop-blur-sm rounded-2xl p-8 border border-white/20 shadow-xl">
              <div className="flex items-center space-x-3 mb-6">
                <div className="p-3 bg-purple-500/10 rounded-xl">
                  <selectedTemplate.icon className={`h-6 w-6 text-${selectedTemplate.color}-600`} />
                </div>
                <h2 className="text-2xl font-bold text-gray-900">Vista Previa de Plantilla</h2>
              </div>
              
              <div className="bg-gray-50 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {selectedTemplate.name}
                </h3>
                <p className="text-gray-600 mb-4">
                  {selectedTemplate.description}
                </p>
                <div className="text-sm text-gray-500">
                  <p>Esta plantilla incluirá:</p>
                  <ul className="list-disc list-inside mt-2 space-y-1">
                    <li>Encabezado con información de la empresa</li>
                    <li>Contenido personalizado según el tipo</li>
                    <li>Pie de página con datos de contacto</li>
                    <li>Formato profesional para impresión</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Submit Button */}
        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => navigate('/documents')}
            className="px-6 py-3 text-gray-700 bg-white/60 hover:bg-white/80 border border-gray-200 rounded-xl font-medium transition-all duration-200 hover:scale-105"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={isSubmitting || !formData.template_type}
            className="px-8 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-medium hover:shadow-lg transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {isSubmitting ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Creando...</span>
              </>
            ) : (
              <>
                <CheckCircleIcon className="h-5 w-5" />
                <span>Crear Documento</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CreateDocument;
