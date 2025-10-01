import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { 
  ArrowLeftIcon,
  DocumentArrowDownIcon,
  PhotoIcon,
  XMarkIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';

const QualityReportForm = () => {
  const { incidentId } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  // Detectar tipo de reporte basado en la URL
  const isInternalReport = window.location.pathname.includes('/internal/');
  const reportType = isInternalReport ? 'interno' : 'cliente';
  const [formData, setFormData] = useState({
    incident_id: incidentId,
    report_type: reportType, // Se determina automáticamente por la URL
    report_date: '',
    report_number: '',
    quality_manager: '',
    inspector_name: '',
    inspector_phone: '',
    inspector_email: '',
    product_sku: '',
    product_lot: '',
    product_description: '',
    supplier_name: '',
    inspection_date: '',
    inspection_location: '',
    inspection_type: 'rutinaria', // rutinaria, especial, reclamacion
    inspection_scope: '',
    inspection_criteria: '',
    sampling_method: '',
    sample_size: '',
    sample_condition: '',
    test_parameters: '',
    visual_inspection: '',
    dimensional_analysis: '',
    mechanical_tests: '',
    chemical_analysis: '',
    other_tests: '',
    test_results: '',
    non_conformities: '',
    corrective_actions: '',
    preventive_actions: '',
    conclusions: '',
    recommendations: '',
    compliance_status: 'pendiente', // pendiente, cumplido, no_cumplido
    follow_up_required: false,
    follow_up_date: '',
    follow_up_responsible: '',
    additional_notes: ''
  });
  
  const [images, setImages] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  // Obtener datos de la incidencia
  const { data: incident, isLoading: incidentLoading } = useQuery({
    queryKey: ['incident', incidentId],
    queryFn: async () => {
      const response = await api.get(`/incidents/${incidentId}/`);
      return response.data;
    },
    enabled: !!incidentId
  });

  // Pre-llenar datos cuando se carga la incidencia
  useEffect(() => {
    if (incident) {
      setFormData(prev => ({
        ...prev,
        report_date: new Date().toISOString().split('T')[0],
        report_number: `QR-${new Date().getFullYear()}-${String(new Date().getMonth() + 1).padStart(2, '0')}-${String(Math.floor(Math.random() * 1000)).padStart(3, '0')}`,
        product_sku: incident.sku || '',
        product_lot: incident.lote || '',
        product_category: incident.categoria || '',
        product_subcategory: incident.subcategoria || '',
        product_description: incident.descripcion || '',
        supplier_name: incident.provider || '',
        inspection_date: new Date().toISOString().split('T')[0],
        inspection_location: incident.obra || '',
        inspection_scope: `Análisis de calidad del producto ${incident.sku} del lote ${incident.lote || 'N/A'} reportado en la incidencia ${incident.code}`,
        inspection_criteria: 'Normas ISO 9001, especificaciones técnicas del producto y requisitos del cliente',
        sampling_method: 'Muestreo aleatorio según ISO 2859-1',
        sample_size: '10 unidades del lote reportado',
        sample_condition: 'Producto en condiciones de almacenamiento normal',
        test_parameters: 'Análisis dimensional, pruebas mecánicas, análisis químico y evaluación visual',
        visual_inspection: 'Inspección visual detallada del producto para identificar defectos superficiales',
        dimensional_analysis: 'Medición de dimensiones críticas según especificaciones técnicas',
        mechanical_tests: 'Pruebas de resistencia y durabilidad según normativas aplicables',
        chemical_analysis: 'Análisis de composición química y propiedades del material',
        other_tests: 'Pruebas adicionales según requerimientos específicos del producto',
        test_results: 'Resultados detallados de todas las pruebas realizadas',
        non_conformities: 'Identificación de no conformidades encontradas durante la inspección',
        corrective_actions: 'Acciones correctivas implementadas para resolver no conformidades',
        preventive_actions: 'Acciones preventivas para evitar recurrencia de problemas',
        conclusions: 'Conclusiones basadas en los resultados de las pruebas realizadas',
        recommendations: 'Recomendaciones para mejorar la calidad del producto',
        follow_up_responsible: 'Equipo de Control de Calidad'
      }));
    }
  }, [incident]);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
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
      const imageToRemove = prev.find(img => img.id === imageId);
      if (imageToRemove) {
        URL.revokeObjectURL(imageToRemove.preview);
      }
      return prev.filter(img => img.id !== imageId);
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const formDataToSend = new FormData();
      
      // Agregar datos del formulario
      Object.keys(formData).forEach(key => {
        if (formData[key] !== null && formData[key] !== undefined) {
          formDataToSend.append(key, formData[key]);
        }
      });

      // Agregar imágenes
      images.forEach((image, index) => {
        formDataToSend.append(`images`, image.file);
      });

      // Enviar formulario
      const response = await api.post('/documents/quality-reports/', formDataToSend, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setSubmitSuccess(true);
        setTimeout(() => {
          navigate(isInternalReport ? '/quality-reports/internal' : '/quality-reports/client');
        }, 2000);
      }
    } catch (error) {
      console.error('Error al enviar formulario:', error);
      alert('Error al enviar el formulario. Por favor, inténtalo de nuevo.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (incidentLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando datos de la incidencia...</p>
        </div>
      </div>
    );
  }

  if (submitSuccess) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <CheckCircleIcon className="h-16 w-16 text-green-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            {isInternalReport ? '¡Informe Enviado!' : '¡Reporte Enviado!'}
          </h2>
          <p className="text-gray-600">
            {isInternalReport ? 'El informe interno de calidad se ha generado exitosamente.' : 'El reporte de calidad se ha generado exitosamente.'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
        {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <button
                onClick={() => navigate(isInternalReport ? '/quality-reports/internal' : '/quality-reports/client')}
                className="mr-4 p-2 text-gray-400 hover:text-gray-600"
              >
                <ArrowLeftIcon className="h-5 w-5" />
              </button>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">
                  {isInternalReport ? 'Nuevo Informe Interno de Calidad' : 'Nuevo Reporte de Calidad para Cliente'}
                </h1>
                <p className="text-sm text-gray-500">
                  Incidencia: {incident?.code} - {incident?.provider}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                {incident?.prioridad?.toUpperCase()}
              </span>
            </div>
            </div>
          </div>
        </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Información de la Incidencia */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Información de la Incidencia
              </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Código de Incidencia</label>
                <p className="mt-1 text-sm text-gray-900">{incident?.code}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Proveedor</label>
                <p className="mt-1 text-sm text-gray-900">{incident?.provider}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Cliente</label>
                <p className="mt-1 text-sm text-gray-900">{incident?.cliente}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Obra</label>
                <p className="mt-1 text-sm text-gray-900">{incident?.obra}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">SKU</label>
                <p className="mt-1 text-sm text-gray-900">{incident?.sku}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Lote</label>
                <p className="mt-1 text-sm text-gray-900">{incident?.lote || 'N/A'}</p>
              </div>
            </div>
                </div>

          {/* Información del Reporte */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Información del Reporte
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Fecha del Reporte</label>
                <input
                  type="date"
                  name="report_date"
                  value={formData.report_date}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Número de Reporte</label>
                <input
                  type="text"
                  name="report_number"
                  value={formData.report_number}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Gerente de Calidad</label>
                <input
                  type="text"
                  name="quality_manager"
                  value={formData.quality_manager}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
            </div>
          </div>

          {/* Información del Inspector */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Información del Inspector
              </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Nombre del Inspector</label>
                <input
                  type="text"
                  name="inspector_name"
                  value={formData.inspector_name}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Teléfono del Inspector</label>
                <input
                  type="tel"
                  name="inspector_phone"
                  value={formData.inspector_phone}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Email del Inspector</label>
                <input
                  type="email"
                  name="inspector_email"
                  value={formData.inspector_email}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Información del Producto */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Información del Producto
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">SKU del Producto</label>
                <input
                  type="text"
                  name="product_sku"
                  value={formData.product_sku}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Lote del Producto</label>
                <input
                  type="text"
                  name="product_lot"
                  value={formData.product_lot}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Categoría</label>
                <input
                  type="text"
                  name="product_category"
                  value={formData.product_category}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  readOnly
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Subcategoría</label>
                <input
                  type="text"
                  name="product_subcategory"
                  value={formData.product_subcategory}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  readOnly
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700">Descripción del Producto</label>
                <textarea
                  name="product_description"
                  value={formData.product_description}
                  onChange={handleInputChange}
                  rows={3}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
            </div>
          </div>

          {/* Información de la Inspección */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Información de la Inspección
              </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Fecha de Inspección</label>
                <input
                  type="date"
                  name="inspection_date"
                  value={formData.inspection_date}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Ubicación de Inspección</label>
                <input
                  type="text"
                  name="inspection_location"
                  value={formData.inspection_location}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Tipo de Inspección</label>
                <select
                  name="inspection_type"
                  value={formData.inspection_type}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  <option value="rutinaria">Rutinaria</option>
                  <option value="especial">Especial</option>
                  <option value="reclamacion">Reclamación</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Alcance de Inspección</label>
                <input
                  type="text"
                  name="inspection_scope"
                  value={formData.inspection_scope}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
            </div>
          </div>

          {/* Criterios y Métodos de Inspección */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Criterios y Métodos de Inspección
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Criterios de Inspección</label>
                <textarea
                  name="inspection_criteria"
                  value={formData.inspection_criteria}
                  onChange={handleInputChange}
                  rows={3}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Método de Muestreo</label>
                  <input
                    type="text"
                    name="sampling_method"
                    value={formData.sampling_method}
                    onChange={handleInputChange}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Tamaño de Muestra</label>
                  <input
                    type="text"
                    name="sample_size"
                    value={formData.sample_size}
                    onChange={handleInputChange}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Condición de la Muestra</label>
                <input
                  type="text"
                  name="sample_condition"
                  value={formData.sample_condition}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
            </div>
          </div>

          {/* Parámetros de Prueba */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Parámetros de Prueba
              </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Parámetros de Prueba</label>
                <textarea
                  name="test_parameters"
                  value={formData.test_parameters}
                  onChange={handleInputChange}
                  rows={3}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Inspección Visual</label>
                  <textarea
                    name="visual_inspection"
                    value={formData.visual_inspection}
                    onChange={handleInputChange}
                    rows={3}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Análisis Dimensional</label>
                  <textarea
                    name="dimensional_analysis"
                    value={formData.dimensional_analysis}
                    onChange={handleInputChange}
                    rows={3}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Pruebas Mecánicas</label>
                  <textarea
                    name="mechanical_tests"
                    value={formData.mechanical_tests}
                    onChange={handleInputChange}
                    rows={3}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Análisis Químico</label>
                  <textarea
                    name="chemical_analysis"
                    value={formData.chemical_analysis}
                    onChange={handleInputChange}
                    rows={3}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Otras Pruebas</label>
                <textarea
                  name="other_tests"
                  value={formData.other_tests}
                  onChange={handleInputChange}
                  rows={3}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Resultados y No Conformidades */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Resultados y No Conformidades
              </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Resultados de Pruebas</label>
                <textarea
                  name="test_results"
                  value={formData.test_results}
                  onChange={handleInputChange}
                  rows={4}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">No Conformidades</label>
                <textarea
                  name="non_conformities"
                  value={formData.non_conformities}
                  onChange={handleInputChange}
                  rows={4}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Acciones Correctivas y Preventivas */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Acciones Correctivas y Preventivas
              </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Acciones Correctivas</label>
                <textarea
                  name="corrective_actions"
                  value={formData.corrective_actions}
                  onChange={handleInputChange}
                  rows={4}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
            </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Acciones Preventivas</label>
                <textarea
                  name="preventive_actions"
                  value={formData.preventive_actions}
                  onChange={handleInputChange}
                  rows={4}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Conclusiones y Recomendaciones */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Conclusiones y Recomendaciones
              </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Conclusiones</label>
                <textarea
                  name="conclusions"
                  value={formData.conclusions}
                  onChange={handleInputChange}
                  rows={4}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  required
                />
            </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Recomendaciones</label>
                <textarea
                  name="recommendations"
                  value={formData.recommendations}
                  onChange={handleInputChange}
                  rows={4}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
            </div>
          </div>

          {/* Seguimiento */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Seguimiento
            </h3>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Estado de Cumplimiento</label>
                  <select
                    name="compliance_status"
                    value={formData.compliance_status}
                    onChange={handleInputChange}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    required
                  >
                    <option value="pendiente">Pendiente</option>
                    <option value="cumplido">Cumplido</option>
                    <option value="no_cumplido">No Cumplido</option>
                  </select>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    name="follow_up_required"
                    checked={formData.follow_up_required}
                    onChange={handleInputChange}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label className="ml-2 block text-sm text-gray-900">
                    Seguimiento Requerido
                  </label>
                </div>
              </div>
              {formData.follow_up_required && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Fecha de Seguimiento</label>
                    <input
                      type="date"
                      name="follow_up_date"
                      value={formData.follow_up_date}
                      onChange={handleInputChange}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Responsable del Seguimiento</label>
                    <input
                      type="text"
                      name="follow_up_responsible"
                      value={formData.follow_up_responsible}
                      onChange={handleInputChange}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Notas Adicionales */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Notas Adicionales
              </h3>
            <div>
              <label className="block text-sm font-medium text-gray-700">Notas Adicionales</label>
              <textarea
                name="additional_notes"
                value={formData.additional_notes}
                onChange={handleInputChange}
                rows={4}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                placeholder="Cualquier información adicional relevante"
              />
            </div>
          </div>

          {/* Subida de Imágenes */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Imágenes del Reporte
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Subir Imágenes</label>
                <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
                  <div className="space-y-1 text-center">
                    <PhotoIcon className="mx-auto h-12 w-12 text-gray-400" />
                    <div className="flex text-sm text-gray-600">
                      <label htmlFor="image-upload" className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500">
                        <span>Subir imágenes</span>
                <input
                          id="image-upload"
                          name="image-upload"
                  type="file"
                  multiple
                  accept="image/*"
                          onChange={handleImageUpload}
                          className="sr-only"
                        />
                      </label>
                      <p className="pl-1">o arrastra y suelta</p>
                    </div>
                    <p className="text-xs text-gray-500">PNG, JPG, GIF hasta 10MB cada una</p>
                  </div>
                </div>
              </div>

              {/* Vista previa de imágenes */}
              {images.length > 0 && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {images.map((image) => (
                    <div key={image.id} className="relative">
                      <img
                        src={image.preview}
                        alt="Preview"
                        className="w-full h-32 object-cover rounded-lg"
                      />
                        <button
                          type="button"
                        onClick={() => removeImage(image.id)}
                        className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                        >
                        <XMarkIcon className="h-4 w-4" />
                        </button>
                      </div>
                    ))}
                </div>
              )}
            </div>
          </div>

          {/* Botones de Acción */}
          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={() => navigate(isInternalReport ? '/quality-reports/internal' : '/quality-reports/client')}
              className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              {isSubmitting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Generando PDF...
                </>
              ) : (
                <>
                  <DocumentArrowDownIcon className="h-4 w-4 mr-2" />
                  Generar Reporte PDF
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default QualityReportForm;