import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { api } from '../services/api';
import {
  DocumentTextIcon,
  PhotoIcon,
  ArrowLeftIcon,
  CheckIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import IncidentImagesViewer from '../components/IncidentImagesViewer';

const VisitReportForm = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();
  const incidentId = searchParams.get('incident_id');
  const reportType = searchParams.get('report_type') || 'cliente';

  // Estados del formulario
  const [formData, setFormData] = useState({
    // Información básica
    order_number: '',
    visit_date: new Date().toISOString().split('T')[0],
    
    // Información del proyecto/cliente
    project_name: '',
    project_id: '',
    client_name: '',
    client_rut: '',
    address: '',
    construction_company: '',
    
    // Personal involucrado
    salesperson: '',
    technician: '',
    installer: '',
    installer_phone: '',
    
    // Ubicación
    commune: '',
    city: '',
    
    // Motivo de la visita
    visit_reason: '',
    
    // Información del producto (precargada)
    product_category: '',
    product_subcategory: '',
    product_sku: '',
    product_lot: '',
    product_provider: '',
    incident_description: '',
    incident_priority: '',
    incident_responsible: '',
    incident_detection_date: '',
    incident_detection_time: '',
    
    // Datos de máquinas
    machine_data: {
      machines: [],
      machine_removal: false,
      report_number: ''
    },
    
    // Observaciones por sección
    wall_observations: '',
    matrix_observations: '',
    slab_observations: '',
    storage_observations: '',
    pre_assembled_observations: '',
    exterior_observations: '',
    general_observations: '',
    
    // Estado
    status: 'draft'
  });

  const [images, setImages] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [documentStatus, setDocumentStatus] = useState(null);

  // Query para obtener datos de la incidencia
  const { data: incident, isLoading: incidentLoading } = useQuery({
    queryKey: ['incident', incidentId],
    queryFn: () => api.get(`/incidents/${incidentId}/`).then(res => res.data),
    enabled: !!incidentId
  });

  // Query para obtener imágenes de la incidencia
  const { data: incidentImages, isLoading: imagesLoading } = useQuery({
    queryKey: ['incidentImages', incidentId],
    queryFn: () => api.get(`/incidents/${incidentId}/images/list/`).then(res => res.data),
    enabled: !!incidentId
  });

  // Cargar datos de la incidencia al formulario
  useEffect(() => {
    if (incident) {
      // Generar número de orden automáticamente
      const generateOrderNumber = async () => {
        try {
          const response = await api.get('/documents/generate-order-number/');
          const orderNumber = response.data.order_number;
          
          setFormData(prev => ({
            ...prev,
            // Información del proyecto/cliente
            project_name: incident.obra || '',
            client_name: incident.cliente || '',
            address: incident.address || '',
            commune: incident.commune || '',
            city: incident.city || '',
            visit_reason: incident.visit_reason || '01-Visita Técnica',
            
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
            
            // Número de orden generado automáticamente
            order_number: orderNumber
          }));
        } catch (error) {
          console.error('Error generando número de orden:', error);
          // Continuar sin el número de orden si hay error
          setFormData(prev => ({
            ...prev,
            // Información del proyecto/cliente
            project_name: incident.obra || '',
            client_name: incident.cliente || '',
            address: incident.address || '',
            commune: incident.commune || '',
            city: incident.city || '',
            visit_reason: incident.visit_reason || '01-Visita Técnica',
            
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
      };
      
      generateOrderNumber();
      
      // Cargar estado de documentos
      checkDocumentStatus();
    }
  }, [incident]);

  // Mutación para crear reporte
  const createReportMutation = useMutation({
    mutationFn: async (data) => {
      // Crear el reporte (el PDF se genera automáticamente en el backend)
      const reportResponse = await api.post('/documents/visit-reports/', data);
      
      return {
        report: reportResponse.data
      };
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries(['visitReports']);
      
      // Mostrar mensaje de éxito
      alert('✅ Reporte de visita creado exitosamente. El PDF se ha generado automáticamente.');
      
      navigate('/visit-reports');
    },
    onError: (error) => {
      console.error('Error creating report:', error);
      
      // Mostrar mensaje de error específico
      if (error.response?.data?.error) {
        const errorMessage = error.response.data.error;
        if (errorMessage.includes('Ya existe un reporte de visita')) {
          alert(`⚠️ ${errorMessage}\n\nEsta incidencia ya tiene un reporte de visita. No se puede crear otro.`);
        } else {
          alert(`Error: ${errorMessage}`);
        }
      } else if (error.response?.data?.related_incident) {
        alert(`Error: ${error.response.data.related_incident}`);
      } else {
        alert('Error al crear el reporte. Por favor, inténtalo de nuevo.');
      }
    }
  });

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleMachineDataChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      machine_data: {
        ...prev.machine_data,
        [field]: value
      }
    }));
  };

  const handleAddMachine = () => {
    setFormData(prev => ({
      ...prev,
      machine_data: {
        ...prev.machine_data,
        machines: [...prev.machine_data.machines, { machine: '', start: '', cut: '' }]
      }
    }));
  };

  const handleMachineChange = (index, field, value) => {
    setFormData(prev => ({
      ...prev,
      machine_data: {
        ...prev.machine_data,
        machines: prev.machine_data.machines.map((machine, i) => 
          i === index ? { ...machine, [field]: value } : machine
        )
      }
    }));
  };

  const handleRemoveMachine = (index) => {
    setFormData(prev => ({
      ...prev,
      machine_data: {
        ...prev.machine_data,
        machines: prev.machine_data.machines.filter((_, i) => i !== index)
      }
    }));
  };

  const checkDocumentStatus = async () => {
    try {
      const response = await api.get(`/documents/incident/${incidentId}/documents-status/`);
      setDocumentStatus(response.data);
      
      if (response.data.visit_report) {
        alert('⚠️ Esta incidencia ya tiene un reporte de visita. No se puede crear otro.');
        return false;
      }
      return true;
    } catch (error) {
      console.error('Error checking document status:', error);
      return true; // Continuar si no se puede verificar
    }
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
      // Verificar estado de documentos antes de enviar
      const canProceed = await checkDocumentStatus();
      if (!canProceed) {
        setIsSubmitting(false);
        return;
      }
      // Crear FormData para enviar datos y archivos
      const formDataToSend = new FormData();
      
      // Agregar datos del formulario
      Object.keys(formData).forEach(key => {
        if (key === 'machine_data') {
          formDataToSend.append(key, JSON.stringify(formData[key]));
        } else if (key === 'order_number' && !formData[key]) {
          // No enviar order_number si está vacío, se generará automáticamente
          return;
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
          onClick={() => navigate('/visit-reports')}
          className="flex items-center text-blue-600 hover:text-blue-800 mb-4"
        >
          <ArrowLeftIcon className="h-5 w-5 mr-2" />
          Volver a Reportes de Visita
        </button>
        
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg p-6 text-white">
          <h1 className="text-2xl font-bold mb-2">
            📋 Reporte de Visita - {reportType === 'cliente' ? 'Para Cliente' : 'Interno'}
          </h1>
          <p className="text-blue-100">
            {incident ? `Incidencia: ${incident.code} - ${incident.cliente}` : 'Cargando...'}
          </p>
        </div>
        
        {/* Estado de documentos */}
        {documentStatus && (
          <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h3 className="text-sm font-medium text-blue-900 mb-2">Estado de Documentos de la Incidencia</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
              <div className={`px-2 py-1 rounded ${documentStatus.visit_report ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
                Reporte de Visita: {documentStatus.visit_report ? 'Existe' : 'No existe'}
              </div>
              <div className={`px-2 py-1 rounded ${documentStatus.supplier_report ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
                Reporte de Proveedor: {documentStatus.supplier_report ? 'Existe' : 'No existe'}
              </div>
              <div className={`px-2 py-1 rounded ${documentStatus.lab_report ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
                Reporte de Laboratorio: {documentStatus.lab_report ? 'Existe' : 'No existe'}
              </div>
              <div className={`px-2 py-1 rounded ${documentStatus.quality_report_cliente ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
                Reporte de Calidad: {documentStatus.quality_report_cliente ? 'Existe' : 'No existe'}
              </div>
            </div>
            {documentStatus.visit_report && reportType === 'visit' && (
              <div className="mt-2 p-2 bg-red-100 border border-red-300 rounded text-red-800 text-sm">
                ⚠️ Esta incidencia ya tiene un reporte de visita. No se puede crear otro.
              </div>
            )}
          </div>
        )}
        
        {/* Visualizador de imágenes adjuntas */}
        {incidentImages && incidentImages.length > 0 && (
          <div className="mt-4">
            <IncidentImagesViewer 
              incidentId={incidentId} 
              images={incidentImages} 
            />
          </div>
        )}
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
                Número de Orden
              </label>
              <input
                type="text"
                value={formData.order_number}
                onChange={(e) => handleInputChange('order_number', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Fecha de Visita
              </label>
              <input
                type="date"
                value={formData.visit_date}
                onChange={(e) => handleInputChange('visit_date', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
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
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                ID del Proyecto
              </label>
              <input
                type="text"
                value={formData.project_id}
                onChange={(e) => handleInputChange('project_id', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
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
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
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
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
              />
            </div>
            
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Dirección
              </label>
              <input
                type="text"
                value={formData.address}
                onChange={(e) => handleInputChange('address', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Empresa Constructora
              </label>
              <input
                type="text"
                value={formData.construction_company}
                onChange={(e) => handleInputChange('construction_company', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
              />
            </div>
          </div>
        </div>

        {/* Información del Producto */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg shadow-md p-6 border-l-4 border-blue-500">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <svg className="w-6 h-6 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
            Información del Producto
            <span className="ml-2 text-sm text-blue-600 bg-blue-100 px-2 py-1 rounded-full">Precargada</span>
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Categoría
              </label>
              <input
                type="text"
                value={formData.product_category}
                onChange={(e) => handleInputChange('product_category', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
                placeholder="Categoría del producto"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Subcategoría
              </label>
              <input
                type="text"
                value={formData.product_subcategory}
                onChange={(e) => handleInputChange('product_subcategory', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                SKU
              </label>
              <input
                type="text"
                value={formData.product_sku}
                onChange={(e) => handleInputChange('product_sku', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Lote
              </label>
              <input
                type="text"
                value={formData.product_lot}
                onChange={(e) => handleInputChange('product_lot', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
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
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Responsable
              </label>
              <input
                type="text"
                value={formData.incident_responsible}
                onChange={(e) => handleInputChange('incident_responsible', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
              />
            </div>
          </div>
          
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Descripción de la Incidencia
            </label>
            <textarea
              value={formData.incident_description}
              onChange={(e) => handleInputChange('incident_description', e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              readOnly
            />
          </div>
        </div>

        {/* Personal Involucrado */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Personal Involucrado
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Vendedor
              </label>
              <input
                type="text"
                value={formData.salesperson}
                onChange={(e) => handleInputChange('salesperson', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Técnico
              </label>
              <input
                type="text"
                value={formData.technician}
                onChange={(e) => handleInputChange('technician', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Instalador
              </label>
              <input
                type="text"
                value={formData.installer}
                onChange={(e) => handleInputChange('installer', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Teléfono del Instalador
              </label>
              <input
                type="text"
                value={formData.installer_phone}
                onChange={(e) => handleInputChange('installer_phone', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
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
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
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
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Motivo de la Visita
              </label>
              <select
                value={formData.visit_reason}
                onChange={(e) => handleInputChange('visit_reason', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
                required
              >
                <option value="01-Visita Técnica">01-Visita Técnica</option>
                <option value="02-Instalación">02-Instalación</option>
                <option value="03-Mantenimiento">03-Mantenimiento</option>
                <option value="04-Inspección">04-Inspección</option>
                <option value="05-Otro">05-Otro</option>
              </select>
            </div>
          </div>
        </div>

        {/* Datos de Máquinas */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Datos de Máquinas
          </h2>
          
          <div className="space-y-4">
            {formData.machine_data.machines.map((machine, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-center mb-3">
                  <h3 className="font-medium text-gray-700">Máquina {index + 1}</h3>
                  <button
                    type="button"
                    onClick={() => handleRemoveMachine(index)}
                    className="text-red-600 hover:text-red-800"
                  >
                    <XMarkIcon className="h-5 w-5" />
                  </button>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Máquina
                    </label>
                    <input
                      type="text"
                      value={machine.machine}
                      onChange={(e) => handleMachineChange(index, 'machine', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Inicio
                    </label>
                    <input
                      type="text"
                      value={machine.start}
                      onChange={(e) => handleMachineChange(index, 'start', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Corte
                    </label>
                    <input
                      type="text"
                      value={machine.cut}
                      onChange={(e) => handleMachineChange(index, 'cut', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
                    />
                  </div>
                </div>
              </div>
            ))}
            
            <button
              type="button"
              onClick={handleAddMachine}
              className="w-full flex items-center justify-center px-4 py-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-gray-400 hover:text-gray-700"
            >
              <DocumentTextIcon className="h-5 w-5 mr-2" />
              Agregar Máquina
            </button>
          </div>
          
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Retiro de Máquina
              </label>
              <select
                value={formData.machine_data.machine_removal ? 'Si' : 'No'}
                onChange={(e) => handleMachineDataChange('machine_removal', e.target.value === 'Si')}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
              >
                <option value="No">No</option>
                <option value="Si">Si</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Número de Reporte
              </label>
              <input
                type="text"
                value={formData.machine_data.report_number}
                onChange={(e) => handleMachineDataChange('report_number', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
              />
            </div>
          </div>
        </div>

        {/* Observaciones */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Observaciones
          </h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Observaciones Muro/Tabique
              </label>
              <textarea
                value={formData.wall_observations}
                onChange={(e) => handleInputChange('wall_observations', e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
                placeholder="Describa las observaciones sobre muros y tabiques..."
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Observaciones Matriz
              </label>
              <textarea
                value={formData.matrix_observations}
                onChange={(e) => handleInputChange('matrix_observations', e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
                placeholder="Describa las observaciones sobre la matriz principal..."
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Observaciones Losa
              </label>
              <textarea
                value={formData.slab_observations}
                onChange={(e) => handleInputChange('slab_observations', e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
                placeholder="Describa las observaciones sobre la losa..."
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Observaciones Almacenaje
              </label>
              <textarea
                value={formData.storage_observations}
                onChange={(e) => handleInputChange('storage_observations', e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
                placeholder="Describa las observaciones sobre el almacenaje..."
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Observaciones Pre Armados
              </label>
              <textarea
                value={formData.pre_assembled_observations}
                onChange={(e) => handleInputChange('pre_assembled_observations', e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
                placeholder="Describa las observaciones sobre pre armados..."
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Observaciones Exteriores
              </label>
              <textarea
                value={formData.exterior_observations}
                onChange={(e) => handleInputChange('exterior_observations', e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
                placeholder="Describa las observaciones exteriores..."
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Observaciones Generales
              </label>
              <textarea
                value={formData.general_observations}
                onChange={(e) => handleInputChange('general_observations', e.target.value)}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
                placeholder="Describa las observaciones generales..."
                required
              />
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
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
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
            onClick={() => navigate('/visit-reports')}
            className="px-6 py-3 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            Cancelar
          </button>
          
          <button
            type="submit"
            disabled={isSubmitting}
            className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center"
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

export default VisitReportForm;
