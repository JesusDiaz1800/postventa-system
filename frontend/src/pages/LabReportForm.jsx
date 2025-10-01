import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { api } from '../services/api';
import {
  DocumentTextIcon,
  PhotoIcon,
  ArrowLeftIcon,
  CheckIcon,
  XMarkIcon,
  BeakerIcon
} from '@heroicons/react/24/outline';

const LabReportForm = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();
  const incidentId = searchParams.get('incident_id');
  const reportType = searchParams.get('report_type') || 'cliente';

  // Estados del formulario
  const [formData, setFormData] = useState({
    // Información básica
    report_number: '',
    report_date: new Date().toISOString().split('T')[0],
    
    // Información del proyecto/cliente
    project_name: '',
    client_name: '',
    client_rut: '',
    address: '',
    
    // Personal involucrado
    technician: '',
    supervisor: '',
    lab_analyst: '',
    
    // Ubicación
    commune: '',
    city: '',
    
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
    incident_detection_time: '',
    
    // Tipo de análisis
    analysis_type: '',
    sample_description: '',
    sample_quantity: '',
    sample_condition: '',
    
    // Parámetros de análisis
    analysis_parameters: {
      temperature: '',
      pressure: '',
      humidity: '',
      ph_level: '',
      conductivity: '',
      other_parameters: ''
    },
    
    // Resultados del análisis
    test_results: {
      visual_inspection: '',
      dimensional_analysis: '',
      mechanical_tests: '',
      chemical_analysis: '',
      other_tests: ''
    },
    
    // Conclusiones y recomendaciones
    conclusions: '',
    recommendations: '',
    compliance_status: '',
    
    // Estado
    status: 'draft'
  });

  const [images, setImages] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Query para obtener datos de la incidencia
  const { data: incident, isLoading: incidentLoading } = useQuery({
    queryKey: ['incident', incidentId],
    queryFn: () => api.get(`/incidents/${incidentId}/`).then(res => res.data),
    enabled: !!incidentId
  });

  // Cargar datos de la incidencia al formulario
  useEffect(() => {
    if (incident) {
      setFormData(prev => ({
        ...prev,
        // Información del proyecto/cliente
        project_name: incident.obra || '',
        client_name: incident.cliente || '',
        address: incident.address || '',
        commune: incident.commune || '',
        city: incident.city || '',
        
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
        incident_detection_time: incident.hora_deteccion || '',
        
        // Información del técnico
        technician: incident.responsable || '',
        supervisor: incident.responsable || ''
      }));
    }
  }, [incident]);

  // Mutación para crear reporte
  const createReportMutation = useMutation({
    mutationFn: async (data) => {
      // Primero crear el reporte
      const reportResponse = await api.post('/documents/lab-reports/', data);
      
      // Luego generar el PDF
      const pdfResponse = await api.post('/documents/pdf/lab-report/', data, {
        responseType: 'blob'
      });
      
      return {
        report: reportResponse.data,
        pdf: pdfResponse.data
      };
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries(['labReports']);
      
      // Crear URL para el PDF y abrirlo
      const pdfUrl = URL.createObjectURL(data.pdf);
      window.open(pdfUrl, '_blank');
      
      navigate('/lab-reports');
    },
    onError: (error) => {
      console.error('Error creating report:', error);
      alert('Error al crear el reporte');
    }
  });

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleAnalysisParametersChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      analysis_parameters: {
        ...prev.analysis_parameters,
        [field]: value
      }
    }));
  };

  const handleTestResultsChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      test_results: {
        ...prev.test_results,
        [field]: value
      }
    }));
  };

  const handleImageUpload = (event) => {
    const files = Array.from(event.target.files);
    setImages(prev => [...prev, ...files]);
  };

  const handleRemoveImage = (index) => {
    setImages(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      // Crear FormData para enviar datos y archivos
      const formDataToSend = new FormData();
      
      // Agregar datos del formulario
      Object.keys(formData).forEach(key => {
        if (key === 'analysis_parameters' || key === 'test_results') {
          formDataToSend.append(key, JSON.stringify(formData[key]));
        } else {
          formDataToSend.append(key, formData[key]);
        }
      });

      // Agregar imágenes
      images.forEach((image, index) => {
        formDataToSend.append(`images`, image);
      });

      // Agregar ID de incidencia y tipo de reporte
      formDataToSend.append('related_incident_id', incidentId);
      formDataToSend.append('report_type', reportType);

      await createReportMutation.mutateAsync(formDataToSend);
    } catch (error) {
      console.error('Error submitting form:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (incidentLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/lab-reports')}
          className="flex items-center text-blue-600 hover:text-blue-800 mb-4"
        >
          <ArrowLeftIcon className="h-5 w-5 mr-2" />
          Volver a Reportes de Laboratorio
        </button>
        
        <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-lg p-6 text-white">
          <h1 className="text-2xl font-bold mb-2 flex items-center">
            <BeakerIcon className="h-6 w-6 mr-3" />
            Reporte de Laboratorio - {reportType === 'cliente' ? 'Para Cliente' : 'Interno'}
          </h1>
          <p className="text-purple-100">
            {incident ? `Incidencia: ${incident.code} - ${incident.cliente}` : 'Cargando...'}
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Información Básica */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <DocumentTextIcon className="h-5 w-5 mr-2" />
            Información Básica
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Número de Reporte
              </label>
              <input
                type="text"
                value={formData.report_number}
                onChange={(e) => handleInputChange('report_number', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Fecha del Reporte
              </label>
              <input
                type="date"
                value={formData.report_date}
                onChange={(e) => handleInputChange('report_date', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
            </div>
          </div>
        </div>

        {/* Información del Proyecto/Cliente */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Información del Proyecto y Cliente
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nombre del Proyecto
              </label>
              <input
                type="text"
                value={formData.project_name}
                onChange={(e) => handleInputChange('project_name', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Cliente
              </label>
              <input
                type="text"
                value={formData.client_name}
                onChange={(e) => handleInputChange('client_name', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                RUT del Cliente
              </label>
              <input
                type="text"
                value={formData.client_rut}
                onChange={(e) => handleInputChange('client_rut', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Dirección
              </label>
              <input
                type="text"
                value={formData.address}
                onChange={(e) => handleInputChange('address', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Comuna
              </label>
              <input
                type="text"
                value={formData.commune}
                onChange={(e) => handleInputChange('commune', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Ciudad
              </label>
              <input
                type="text"
                value={formData.city}
                onChange={(e) => handleInputChange('city', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
            </div>
          </div>
        </div>

        {/* Información del Producto */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Información del Producto
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Categoría del Producto
              </label>
              <input
                type="text"
                value={formData.product_category}
                onChange={(e) => handleInputChange('product_category', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                readOnly
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Subcategoría del Producto
              </label>
              <input
                type="text"
                value={formData.product_subcategory}
                onChange={(e) => handleInputChange('product_subcategory', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                readOnly
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                SKU del Producto
              </label>
              <input
                type="text"
                value={formData.product_sku}
                onChange={(e) => handleInputChange('product_sku', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                readOnly
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Lote del Producto
              </label>
              <input
                type="text"
                value={formData.product_lot}
                onChange={(e) => handleInputChange('product_lot', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                readOnly
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Proveedor
              </label>
              <input
                type="text"
                value={formData.product_provider}
                onChange={(e) => handleInputChange('product_provider', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                readOnly
              />
            </div>
          </div>
        </div>

        {/* Información de la Incidencia */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Información de la Incidencia
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Descripción del Problema
              </label>
              <textarea
                value={formData.incident_description}
                onChange={(e) => handleInputChange('incident_description', e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                readOnly
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Prioridad
              </label>
              <input
                type="text"
                value={formData.incident_priority}
                onChange={(e) => handleInputChange('incident_priority', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                readOnly
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Responsable Técnico
              </label>
              <input
                type="text"
                value={formData.incident_responsible}
                onChange={(e) => handleInputChange('incident_responsible', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                readOnly
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Fecha de Detección
              </label>
              <input
                type="date"
                value={formData.incident_detection_date}
                onChange={(e) => handleInputChange('incident_detection_date', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                readOnly
              />
            </div>
          </div>
        </div>

        {/* Personal Involucrado */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Personal Involucrado
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Técnico Responsable
              </label>
              <input
                type="text"
                value={formData.technician}
                onChange={(e) => handleInputChange('technician', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Supervisor
              </label>
              <input
                type="text"
                value={formData.supervisor}
                onChange={(e) => handleInputChange('supervisor', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Analista de Laboratorio
              </label>
              <input
                type="text"
                value={formData.lab_analyst}
                onChange={(e) => handleInputChange('lab_analyst', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
            </div>
          </div>
        </div>

        {/* Información de la Muestra */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Información de la Muestra
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tipo de Análisis
              </label>
              <select
                value={formData.analysis_type}
                onChange={(e) => handleInputChange('analysis_type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              >
                <option value="">Seleccionar tipo de análisis...</option>
                <option value="quimico">Análisis Químico</option>
                <option value="fisico">Análisis Físico</option>
                <option value="mecanico">Análisis Mecánico</option>
                <option value="microbiologico">Análisis Microbiológico</option>
                <option value="otro">Otro</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Cantidad de Muestra
              </label>
              <input
                type="text"
                value={formData.sample_quantity}
                onChange={(e) => handleInputChange('sample_quantity', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Ej: 500ml, 1kg, etc."
              />
            </div>
            
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Descripción de la Muestra
              </label>
              <textarea
                value={formData.sample_description}
                onChange={(e) => handleInputChange('sample_description', e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Describa la muestra analizada..."
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Condición de la Muestra
              </label>
              <select
                value={formData.sample_condition}
                onChange={(e) => handleInputChange('sample_condition', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="">Seleccionar condición...</option>
                <option value="excelente">Excelente</option>
                <option value="buena">Buena</option>
                <option value="regular">Regular</option>
                <option value="deficiente">Deficiente</option>
              </select>
            </div>
          </div>
        </div>

        {/* Parámetros de Análisis */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Parámetros de Análisis
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Temperatura (°C)
              </label>
              <input
                type="number"
                step="0.1"
                value={formData.analysis_parameters.temperature}
                onChange={(e) => handleAnalysisParametersChange('temperature', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Presión (atm)
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.analysis_parameters.pressure}
                onChange={(e) => handleAnalysisParametersChange('pressure', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Humedad (%)
              </label>
              <input
                type="number"
                step="0.1"
                value={formData.analysis_parameters.humidity}
                onChange={(e) => handleAnalysisParametersChange('humidity', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nivel de pH
              </label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="14"
                value={formData.analysis_parameters.ph_level}
                onChange={(e) => handleAnalysisParametersChange('ph_level', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Conductividad (μS/cm)
              </label>
              <input
                type="number"
                step="0.1"
                value={formData.analysis_parameters.conductivity}
                onChange={(e) => handleAnalysisParametersChange('conductivity', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Otros Parámetros
              </label>
              <input
                type="text"
                value={formData.analysis_parameters.other_parameters}
                onChange={(e) => handleAnalysisParametersChange('other_parameters', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Especificar otros parámetros..."
              />
            </div>
          </div>
        </div>

        {/* Resultados de Pruebas */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Resultados de Pruebas
          </h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Inspección Visual
              </label>
              <textarea
                value={formData.test_results.visual_inspection}
                onChange={(e) => handleTestResultsChange('visual_inspection', e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Describa los resultados de la inspección visual..."
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Análisis Dimensional
              </label>
              <textarea
                value={formData.test_results.dimensional_analysis}
                onChange={(e) => handleTestResultsChange('dimensional_analysis', e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Describa los resultados del análisis dimensional..."
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Pruebas Mecánicas
              </label>
              <textarea
                value={formData.test_results.mechanical_tests}
                onChange={(e) => handleTestResultsChange('mechanical_tests', e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Describa los resultados de las pruebas mecánicas..."
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Análisis Químico
              </label>
              <textarea
                value={formData.test_results.chemical_analysis}
                onChange={(e) => handleTestResultsChange('chemical_analysis', e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Describa los resultados del análisis químico..."
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Otras Pruebas
              </label>
              <textarea
                value={formData.test_results.other_tests}
                onChange={(e) => handleTestResultsChange('other_tests', e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Describa otras pruebas realizadas..."
              />
            </div>
          </div>
        </div>

        {/* Conclusiones y Recomendaciones */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Conclusiones y Recomendaciones
          </h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Conclusiones
              </label>
              <textarea
                value={formData.conclusions}
                onChange={(e) => handleInputChange('conclusions', e.target.value)}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Describa las conclusiones del análisis..."
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Recomendaciones
              </label>
              <textarea
                value={formData.recommendations}
                onChange={(e) => handleInputChange('recommendations', e.target.value)}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Describa las recomendaciones basadas en los resultados..."
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Estado de Cumplimiento
              </label>
              <select
                value={formData.compliance_status}
                onChange={(e) => handleInputChange('compliance_status', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              >
                <option value="">Seleccionar estado...</option>
                <option value="cumple">Cumple con especificaciones</option>
                <option value="no_cumple">No cumple con especificaciones</option>
                <option value="parcial">Cumplimiento parcial</option>
                <option value="requiere_analisis">Requiere análisis adicional</option>
              </select>
            </div>
          </div>
        </div>

        {/* Subida de Imágenes */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <PhotoIcon className="h-5 w-5 mr-2" />
            Imágenes del Reporte
          </h2>
          
          <div className="space-y-4">
            <div>
              <input
                type="file"
                multiple
                accept="image/*"
                onChange={handleImageUpload}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
              <p className="text-sm text-gray-500 mt-1">
                Puede seleccionar múltiples imágenes
              </p>
            </div>
            
            {images.length > 0 && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {images.map((image, index) => (
                  <div key={index} className="relative">
                    <img
                      src={URL.createObjectURL(image)}
                      alt={`Imagen ${index + 1}`}
                      className="w-full h-32 object-cover rounded-lg"
                    />
                    <button
                      type="button"
                      onClick={() => handleRemoveImage(index)}
                      className="absolute top-2 right-2 bg-red-600 text-white rounded-full p-1 hover:bg-red-700"
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
            onClick={() => navigate('/lab-reports')}
            className="px-6 py-3 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            Cancelar
          </button>
          
          <button
            type="submit"
            disabled={isSubmitting}
            className="px-6 py-3 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 flex items-center"
          >
            {isSubmitting ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Guardando...
              </>
            ) : (
              <>
                <CheckIcon className="h-4 w-4 mr-2" />
                Guardar y Generar PDF
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default LabReportForm;
