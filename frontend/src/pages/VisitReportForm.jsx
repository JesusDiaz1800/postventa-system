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
  SparklesIcon
} from '@heroicons/react/24/outline';
import IncidentImagesViewer from '../components/IncidentImagesViewer';
import RichTextEditor from '../components/RichTextEditor';
import { useSAPServiceCall, useSAPCustomerSearch } from '../hooks/useSAPData';
import { useDebounce } from '../hooks/useDebounce';
import { MagnifyingGlassIcon, CloudArrowDownIcon } from '@heroicons/react/24/outline';
import { SAPAttachmentImage, SAPAttachmentFile } from '../components/SAPAttachment';

const VisitReportForm = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();
  const incidentId = searchParams.get('incident_id');
  const reportType = searchParams.get('report_type') || 'cliente';

  // SAP Integration States
  const [sapCallIdInput, setSapCallIdInput] = useState('');
  const [searchSapCallId, setSearchSapCallId] = useState(''); // ID para ejecutar la búsqueda
  const [customerSearchInput, setCustomerSearchInput] = useState('');
  const debouncedCustomerSearch = useDebounce(customerSearchInput, 500);

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
    commune: '',
    city: '',
    construction_company: '',

    // Personal involucrado
    salesperson: '',
    technician: '',
    installer: '',
    installer_phone: '',


    // Motivo de la visita
    visit_reason: '',

    // Información del producto (precargada desde incidencia)
    product_category: '',
    product_subcategory: '',
    product_provider: '',

    // Información de la incidencia (precargada)
    incident_code: '',
    incident_description: '',
    incident_priority: '',
    incident_responsible: '',
    incident_detection_date: '',
    incident_detection_time: '',
    incident_immediate_actions: '',

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
  const [imageDescriptions, setImageDescriptions] = useState({}); // {filename: description}
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [documentStatus, setDocumentStatus] = useState(null);

  // Query para obtener datos de la incidencia
  const { data: incident, isLoading: incidentLoading } = useQuery({
    queryKey: ['incident', incidentId],
    queryFn: () => api.get(`/incidents/${incidentId}/`).then(res => res.data),
    enabled: !!incidentId
  });

  // SAP Queries
  const { data: sapCallData, isLoading: sapCallLoading, error: sapCallError } = useSAPServiceCall(searchSapCallId);
  const { data: sapCustomers, isLoading: sapCustomersLoading } = useSAPCustomerSearch(debouncedCustomerSearch);

  // Efecto para cargar datos desde SAP
  useEffect(() => {
    if (sapCallData) {
      setFormData(prev => ({
        ...prev,
        sap_call_id: sapCallData.call_id,
        // Autocompletar con datos de SAP (Deep Integration)
        // 1. Cliente
        client_name: sapCallData.customer_name || prev.client_name,
        client_rut: sapCallData.customer_code || prev.client_rut,

        // 2. Proyecto y Vendedor
        project_name: sapCallData.project_name || prev.project_name,
        project_id: sapCallData.project_code || prev.project_id,
        salesperson: sapCallData.salesperson || prev.salesperson,

        // 3. Detalles Visita
        visit_reason: sapCallData.problem_type || sapCallData.subject || prev.visit_reason,  // problemTyp
        visit_date: sapCallData.create_date ? sapCallData.create_date.split('T')[0] : prev.visit_date,
        technician: sapCallData.technician || prev.technician,
        address: sapCallData.address || prev.address,
        commune: sapCallData.commune || prev.commune,
        city: sapCallData.city || prev.city,

        // 4. Contacto (Usar datos del instalador si están disponibles, sino contacto)
        installer: sapCallData.installer_name || sapCallData.contact_name || prev.installer,
        installer_phone: sapCallData.installer_phone || sapCallData.telephone || prev.installer_phone,

        // 5. Observaciones (Mapeo directo desde campos personalizados de SAP)
        general_observations: sapCallData.general_observations || sapCallData.description || prev.general_observations,
        wall_observations: sapCallData.obs_muro || prev.wall_observations,
        matrix_observations: sapCallData.obs_matriz || prev.matrix_observations,
        slab_observations: sapCallData.obs_losa || prev.slab_observations,
        storage_observations: sapCallData.obs_almac || prev.storage_observations,
        pre_assembled_observations: sapCallData.obs_pre_arm || prev.pre_assembled_observations,
        exterior_observations: sapCallData.obs_exter || prev.exterior_observations,

        // 6. Responsable (desde técnico de SAP)
        incident_responsible: sapCallData.technician || sapCallData.assignee || prev.incident_responsible,

        // Mantener otros campos
      }));

      // Precargar descripciones de imágenes con nombres de archivo limpios
      if (sapCallData.attachments && sapCallData.attachments.length > 0) {
        const descriptions = {};
        sapCallData.attachments.forEach(att => {
          if (att.is_image) {
            // Limpiar nombre del archivo: remover extensión, guiones bajos, números de versión
            const cleanName = att.filename
              .replace(/\.[^/.]+$/, '')  // Remover extensión
              .replace(/_/g, ' ')          // Reemplazar _ con espacios
              .replace(/-/g, ' ')          // Reemplazar - con espacios
              .replace(/\s*\(\d+\)\s*$/, '') // Remover sufijos como (1), (2)
              .trim();
            descriptions[att.filename] = cleanName;
          }
        });
        setImageDescriptions(descriptions);
      }
      //alert(`✅ Datos cargados desde SAP: Llamada ${sapCallData.call_id}`);
    }
  }, [sapCallData]);

  // Query para obtener imágenes de la incidencia
  const { data: incidentImages, isLoading: imagesLoading } = useQuery({
    queryKey: ['incidentImages', incidentId],
    queryFn: () => api.get(`/incidents/${incidentId}/images/list/`).then(res => res.data),
    enabled: !!incidentId
  });

  // Cargar datos de la incidencia al formulario
  useEffect(() => {
    if (incident) {
      // Generar número de orden automáticamente vinculado a la incidencia
      const generateOrderNumber = async () => {
        try {
          // Pasar incident_id para vincular el código del reporte al de la incidencia
          const response = await api.get(`/documents/generate-order-number/?incident_id=${incident.id}`);
          const orderNumber = response.data.order_number;

          // Si la incidencia tiene un ID de llamada SAP, cargarlo automáticamente
          if (incident.sap_call_id) {
            setSearchSapCallId(incident.sap_call_id);
          }

          setFormData(prev => ({
            ...prev,
            // Información del proyecto/cliente (from incident)
            project_name: incident.obra || '',
            client_name: incident.cliente || '',
            client_rut: incident.cliente_rut || '',
            address: incident.direccion_cliente || '',
            commune: incident.comuna || '',
            city: incident.ciudad || '',
            visit_reason: '01-Visita Técnica',

            // Personal
            installer: incident.installer_name || incident.contact_name || '',
            installer_phone: incident.installer_phone || incident.contact_phone || '',

            // Información del producto (from incident)
            product_category: incident.categoria?.name || incident.categoria || '',
            product_subcategory: incident.subcategoria || '',
            product_sku: incident.sku || '',
            product_lot: incident.lote || '',
            product_provider: incident.provider || '',

            // Información de la incidencia (from incident)
            incident_code: incident.code || '',
            incident_description: incident.descripcion || '',
            incident_priority: incident.prioridad || '',
            incident_responsible: typeof incident.responsable === 'object'
              ? (incident.responsable?.full_name || incident.responsable?.name || '')
              : (incident.responsable || ''),
            incident_detection_date: incident.fecha_deteccion || '',
            incident_detection_time: incident.hora_deteccion || '',
            incident_immediate_actions: incident.acciones_inmediatas || '',

            // Número de orden generado automáticamente
            order_number: orderNumber
          }));
        } catch (error) {
          console.error('Error generando número de orden:', error);
          // Continuar sin el número de orden si hay error
          setFormData(prev => ({
            ...prev,
            // Información del proyecto/cliente (from incident)
            project_name: incident.obra || '',
            client_name: incident.cliente || '',
            client_rut: incident.cliente_rut || '',
            address: incident.direccion_cliente || '',
            visit_reason: '01-Visita Técnica',

            // Información del producto (from incident)
            product_category: incident.categoria?.name || incident.categoria || '',
            product_subcategory: incident.subcategoria || '',
            product_sku: incident.sku || '',
            product_lot: incident.lote || '',
            product_provider: incident.provider || '',

            // Información de la incidencia (from incident)
            incident_code: incident.code || '',
            incident_description: incident.descripcion || '',
            incident_priority: incident.prioridad || '',
            incident_responsible: typeof incident.responsable === 'object'
              ? (incident.responsable?.full_name || incident.responsable?.name || '')
              : (incident.responsable || ''),
            incident_detection_date: incident.fecha_deteccion || '',
            incident_detection_time: incident.hora_deteccion || '',
            incident_immediate_actions: incident.acciones_inmediatas || ''
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

  // Simplified - just allow creation (endpoint doesn't exist)
  const checkDocumentStatus = async () => {
    return true;
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
        if (key === 'machine_data' || key === 'materials_data') {
          formDataToSend.append(key, JSON.stringify(formData[key]));
        } else if (key === 'order_number' && !formData[key]) {
          // No enviar order_number si está vacío, se generará automáticamente
          return;
        } else if (key === 'sap_call_id') {
          // No agregar sap_call_id aquí, se agrega explícitamente después si existe
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
      if (incidentId && incidentId !== 'null' && incidentId !== 'undefined') {
        formDataToSend.append('related_incident_id', incidentId);
      }
      formDataToSend.append('report_type', reportType);

      // Agregar SAP Call ID si existe
      if (searchSapCallId && searchSapCallId !== 'null' && searchSapCallId !== 'undefined') {
        formDataToSend.append('sap_call_id', searchSapCallId);
      }

      // Agregar descripciones de imágenes personalizadas
      if (Object.keys(imageDescriptions).length > 0) {
        formDataToSend.append('image_descriptions', JSON.stringify(imageDescriptions));
      }

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

      {/* SAP Integration Section */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8 border-l-4 border-green-500">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <CloudArrowDownIcon className="h-6 w-6 mr-2 text-green-600" />
          Integración SAP (Opcional)
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Búsqueda por ID de Llamada */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Buscar por ID Llamada de Servicio
            </label>
            <div className="flex">
              <input
                type="number"
                value={sapCallIdInput}
                onChange={(e) => setSapCallIdInput(e.target.value)}
                placeholder="Ej: 26533"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-green-500"
              />
              <button
                type="button"
                onClick={() => setSearchSapCallId(sapCallIdInput)}
                className="px-4 py-2 bg-green-600 text-white rounded-r-md hover:bg-green-700 flex items-center"
                disabled={!sapCallIdInput || sapCallLoading}
              >
                {sapCallLoading ? '...' : <MagnifyingGlassIcon className="h-5 w-5" />}
              </button>
            </div>
            {sapCallError && (
              <p className="text-sm text-red-600 mt-1">No se encontró la llamada en SAP.</p>
            )}
            {sapCallData && (
              <div className="mt-2 text-sm text-green-700 bg-green-50 p-2 rounded">
                ✓ Llamada encontrada: {sapCallData.subject} ({sapCallData.status === -3 ? 'Cerrada' : 'Abierta'})
              </div>
            )}
          </div>

          {/* Búsqueda de Cliente */}
          <div className="relative">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Buscar Cliente en SAP
            </label>
            <div className="relative">
              <input
                type="text"
                value={customerSearchInput}
                onChange={(e) => setCustomerSearchInput(e.target.value)}
                placeholder="Escribe nombre o RUT (mín. 3 caracteres)..."
                className="w-full px-3 py-2 pl-10 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              />
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400 absolute left-3 top-2.5" />
            </div>

            {/* Resultados de búsqueda cliente */}
            {sapCustomers && sapCustomers.length > 0 && (
              <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-md shadow-lg max-h-60 overflow-auto">
                {sapCustomers.map((customer) => (
                  <button
                    key={customer.card_code}
                    type="button"
                    className="w-full text-left px-4 py-2 hover:bg-gray-50 border-b border-gray-100 last:border-0"
                    onClick={() => {
                      setFormData(prev => ({
                        ...prev,
                        client_name: customer.card_name,
                        client_rut: customer.card_code,
                      }));
                      setCustomerSearchInput(''); // Limpiar búsqueda
                    }}
                  >
                    <div className="font-medium text-gray-900">{customer.card_name}</div>
                    <div className="text-xs text-gray-500">{customer.card_code}</div>
                  </button>
                ))}
              </div>
            )}
            {debouncedCustomerSearch.length >= 3 && sapCustomersLoading && (
              <p className="text-sm text-gray-500 mt-1">Buscando...</p>
            )}
          </div>
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

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-2">
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

            {/* Campo ID SAP solo lectura */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                ID Llamada SAP
              </label>
              {(searchSapCallId || formData.sap_call_id) ? (
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <CloudArrowDownIcon className="h-5 w-5 text-green-500" />
                  </div>
                  <input
                    type="text"
                    value={searchSapCallId || formData.sap_call_id}
                    readOnly
                    className="w-full pl-10 px-3 py-2 border border-gray-300 rounded-md bg-gray-100 text-gray-700 font-medium focus:outline-none"
                  />
                </div>
              ) : (
                <input
                  type="text"
                  value="N/A"
                  readOnly
                  className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-400"
                />
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Código de la Obra
              </label>
              <input
                type="text"
                value={formData.project_id}
                onChange={(e) => handleInputChange('project_id', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
              />
            </div>

            <div className="md:col-span-2">
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

            <div className="md:col-span-3">
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

            {/* Nuevos Campos: Comuna y Ciudad */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Comuna
              </label>
              <input
                type="text"
                value={formData.commune || ''}
                onChange={(e) => handleInputChange('commune', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
                placeholder="Comuna"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Ciudad
              </label>
              <input
                type="text"
                value={formData.city || ''}
                onChange={(e) => handleInputChange('city', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
                placeholder="Ciudad"
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
                Contacto
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
                Teléfono del Contacto
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
                placeholder="Observaciones generales de la visita (U_NX_GENE en SAP)..."
              />
            </div>

          </div>
        </div>

        {/* Sección Unificada de Imágenes */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <PhotoIcon className="h-5 w-5 mr-2" />
            Imágenes del Reporte
          </h2>

          <div className="space-y-6">
            {/* Imágenes Precargadas de SAP */}
            {sapCallData && sapCallData.attachments && sapCallData.attachments.filter(a => a.is_image).length > 0 && (
              <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg p-4 border border-purple-200">
                <h3 className="text-lg font-semibold text-purple-900 mb-3 flex items-center">
                  <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
                  </svg>
                  Imágenes Precargadas de SAP ({sapCallData.attachments.filter(a => a.is_image).length})
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {sapCallData.attachments.filter(att => att.is_image).map((att) => (
                    <div key={att.id} className="bg-white rounded-lg p-3 shadow-sm border border-purple-100">
                      <div className="mb-2">
                        <SAPAttachmentImage
                          atcEntry={att.atc_entry}
                          line={att.line}
                          filename={att.filename}
                          className="w-full h-32 object-cover rounded-md border border-gray-200"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">
                          Descripción para el PDF:
                        </label>
                        <input
                          type="text"
                          value={imageDescriptions[att.filename] || ''}
                          onChange={(e) => setImageDescriptions(prev => ({
                            ...prev,
                            [att.filename]: e.target.value
                          }))}
                          placeholder="Descripción de la imagen..."
                          className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-purple-500"
                        />
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-3 text-xs text-purple-700 bg-purple-100 p-2 rounded">
                  💡 Estas imágenes se importarán automáticamente al generar el reporte.
                </div>
              </div>
            )}

            {/* Subida Manual de Imágenes Adicionales */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200">
              <h3 className="text-lg font-semibold text-blue-900 mb-3 flex items-center">
                <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                Agregar Imágenes Adicionales
              </h3>

              <div className="mb-4">
                <input
                  type="file"
                  multiple
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="w-full px-3 py-2 border border-blue-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                />
                <p className="text-sm text-blue-600 mt-1">
                  Puede seleccionar múltiples imágenes (JPG, PNG, etc.)
                </p>
              </div>

              {/* Preview de imágenes subidas con descripciones */}
              {images.length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {images.map((image, index) => (
                    <div key={index} className="bg-white rounded-lg p-3 shadow-sm border border-blue-100">
                      <div className="relative mb-2">
                        <img
                          src={URL.createObjectURL(image)}
                          alt={`Imagen ${index + 1}`}
                          className="w-full h-32 object-cover rounded-md border border-gray-200"
                        />
                        <button
                          type="button"
                          onClick={() => handleRemoveImage(index)}
                          className="absolute top-2 right-2 bg-red-600 text-white rounded-full p-1 hover:bg-red-700 shadow-md"
                        >
                          <XMarkIcon className="h-4 w-4" />
                        </button>
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">
                          Descripción para el PDF:
                        </label>
                        <input
                          type="text"
                          value={imageDescriptions[image.name] || ''}
                          onChange={(e) => setImageDescriptions(prev => ({
                            ...prev,
                            [image.name]: e.target.value
                          }))}
                          placeholder="Descripción de la imagen..."
                          className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {images.length === 0 && (
                <div className="text-center py-6 text-gray-500">
                  <PhotoIcon className="h-12 w-12 mx-auto text-gray-300 mb-2" />
                  <p className="text-sm">No hay imágenes adicionales seleccionadas</p>
                </div>
              )}
            </div>

            {/* Resumen de imágenes */}
            {((sapCallData?.attachments?.filter(a => a.is_image).length || 0) + images.length) > 0 && (
              <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
                📊 <strong>Total de imágenes:</strong>{' '}
                {sapCallData?.attachments?.filter(a => a.is_image).length || 0} de SAP + {images.length} adicionales
                = <strong>{(sapCallData?.attachments?.filter(a => a.is_image).length || 0) + images.length}</strong> imágenes para el PDF
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
      </form >
    </div >
  );
};

export default VisitReportForm;
