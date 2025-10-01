import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { 
  ArrowLeftIcon,
  DocumentArrowDownIcon,
  PhotoIcon,
  XMarkIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';

const SupplierReportForm = () => {
  const { incidentId } = useParams();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    incident_id: incidentId,
    supplier_name: '',
    contact_person: '',
    contact_phone: '',
    contact_email: '',
    report_type: 'cliente', // cliente o interno
    visit_date: '',
    visit_time: '',
    visit_duration: '',
    participants: '',
    objectives: '',
    findings: '',
    recommendations: '',
    next_steps: '',
    supplier_response: '',
    compliance_status: 'pendiente', // pendiente, cumplido, no_cumplido
    follow_up_date: '',
    follow_up_responsible: '',
    additional_notes: '',
    
    // Información del producto (precargada desde incidencia)
    product_category: '',
    product_subcategory: '',
    product_sku: '',
    product_lot: '',
    product_provider: '',
    
    // Información de la incidencia (precargada)
    incident_description: '',
    incident_priority: '',
    incident_responsible: '',
    incident_detection_date: '',
    incident_detection_time: ''
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

  // Cargar datos de la incidencia al formulario
  useEffect(() => {
    if (incident) {
      setFormData(prev => ({
        ...prev,
        // Información del producto (importante para reportes)
        product_category: incident.categoria || '',
        product_subcategory: incident.subcategoria || '',
        product_sku: incident.sku || '',
        product_lot: incident.lote || '',
        product_provider: incident.provider || '',
        
        // Información de la incidencia
        incident_description: incident.descripcion || '',
        incident_priority: incident.prioridad || '',
        incident_responsible: incident.responsable || '',
        incident_detection_date: incident.fecha_deteccion || '',
        incident_detection_time: incident.hora_deteccion || ''
      }));
    }
  }, [incident]);


  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
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
      const response = await api.post('/documents/supplier-reports/', formDataToSend, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setSubmitSuccess(true);
        setTimeout(() => {
          navigate('/supplier-reports');
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
          <h2 className="text-2xl font-bold text-gray-900 mb-2">¡Reporte Enviado!</h2>
          <p className="text-gray-600">El reporte de proveedor se ha generado exitosamente.</p>
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
                onClick={() => navigate('/supplier-reports')}
                className="mr-4 p-2 text-gray-400 hover:text-gray-600"
              >
                <ArrowLeftIcon className="h-5 w-5" />
              </button>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">
                  Nuevo Reporte de Proveedor
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

          {/* Información del Producto */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Información del Producto
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Categoría del Producto</label>
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
                <label className="block text-sm font-medium text-gray-700">Subcategoría del Producto</label>
                <input
                  type="text"
                  name="product_subcategory"
                  value={formData.product_subcategory}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  readOnly
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">SKU del Producto</label>
                <input
                  type="text"
                  name="product_sku"
                  value={formData.product_sku}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  readOnly
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
                  readOnly
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Proveedor</label>
                <input
                  type="text"
                  name="product_provider"
                  value={formData.product_provider}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  readOnly
                />
              </div>
            </div>
          </div>

          {/* Información de la Incidencia */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Información de la Incidencia
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700">Descripción del Problema</label>
                <textarea
                  name="incident_description"
                  value={formData.incident_description}
                  onChange={handleInputChange}
                  rows={3}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  readOnly
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Prioridad</label>
                <input
                  type="text"
                  name="incident_priority"
                  value={formData.incident_priority}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  readOnly
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Responsable Técnico</label>
                <input
                  type="text"
                  name="incident_responsible"
                  value={formData.incident_responsible}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  readOnly
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Fecha de Detección</label>
                <input
                  type="date"
                  name="incident_detection_date"
                  value={formData.incident_detection_date}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  readOnly
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Hora de Detección</label>
                <input
                  type="time"
                  name="incident_detection_time"
                  value={formData.incident_detection_time}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  readOnly
                />
              </div>
            </div>
          </div>

          {/* Información del Proveedor */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Información del Proveedor
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Nombre del Proveedor</label>
                <input
                  type="text"
                  name="supplier_name"
                  value={formData.supplier_name}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Persona de Contacto</label>
                <input
                  type="text"
                  name="contact_person"
                  value={formData.contact_person}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Teléfono de Contacto</label>
                <input
                  type="tel"
                  name="contact_phone"
                  value={formData.contact_phone}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Email de Contacto</label>
                <input
                  type="email"
                  name="contact_email"
                  value={formData.contact_email}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Tipo de Reporte */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Tipo de Reporte
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Tipo de Reporte</label>
                <select
                  name="report_type"
                  value={formData.report_type}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  <option value="cliente">Para Cliente</option>
                  <option value="interno">Interno</option>
                </select>
              </div>
            </div>
          </div>

          {/* Información de la Visita */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Información de la Visita
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Fecha de Visita</label>
                <input
                  type="date"
                  name="visit_date"
                  value={formData.visit_date}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Hora de Visita</label>
                <input
                  type="time"
                  name="visit_time"
                  value={formData.visit_time}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Duración (minutos)</label>
                <input
                  type="number"
                  name="visit_duration"
                  value={formData.visit_duration}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  min="1"
                />
              </div>
            </div>
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700">Participantes</label>
              <textarea
                name="participants"
                value={formData.participants}
                onChange={handleInputChange}
                rows={3}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                placeholder="Lista de participantes en la visita"
              />
            </div>
          </div>

          {/* Objetivos y Hallazgos */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Objetivos y Hallazgos
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Objetivos de la Visita</label>
                <textarea
                  name="objectives"
                  value={formData.objectives}
                  onChange={handleInputChange}
                  rows={4}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Hallazgos</label>
                <textarea
                  name="findings"
                  value={formData.findings}
                  onChange={handleInputChange}
                  rows={4}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
            </div>
          </div>

          {/* Recomendaciones y Próximos Pasos */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Recomendaciones y Próximos Pasos
            </h3>
            <div className="space-y-4">
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
              <div>
                <label className="block text-sm font-medium text-gray-700">Próximos Pasos</label>
                <textarea
                  name="next_steps"
                  value={formData.next_steps}
                  onChange={handleInputChange}
                  rows={4}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
            </div>
          </div>

          {/* Respuesta del Proveedor */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Respuesta del Proveedor
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Respuesta del Proveedor</label>
                <textarea
                  name="supplier_response"
                  value={formData.supplier_response}
                  onChange={handleInputChange}
                  rows={4}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Respuesta del proveedor a los hallazgos"
                />
              </div>
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
              onClick={() => navigate('/supplier-reports')}
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

export default SupplierReportForm;