import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useSearchParams, useParams } from 'react-router-dom';
import { api } from '../services/api';
import {
  DocumentTextIcon,
  PhotoIcon,
  ArrowLeftIcon,
  CheckIcon,
  XMarkIcon,
  SparklesIcon,
  BuildingOfficeIcon,
} from '@heroicons/react/24/outline';
import RichTextEditor from '../components/RichTextEditor';
import { useSAPServiceCall, useSAPCustomerSearch, useSAPTechnicians } from '../hooks/useSAPData';
import { useDebounce } from '../hooks/useDebounce';
import { MagnifyingGlassIcon, CloudArrowDownIcon } from '@heroicons/react/24/outline';



const VisitReportForm = () => {
  const { id } = useParams();
  const isEditMode = !!id;
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();
  const incidentIdFromQuery = searchParams.get('incident_id');
  const [incidentId, setIncidentId] = useState(incidentIdFromQuery);

  // Flag para evitar recargas infinitas si detectamos incidentId desde el reporte cargado
  const [hasSetIncidentIdFromReport, setHasSetIncidentIdFromReport] = useState(false);
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
    technician_id: '',
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

    // Datos de máquinas y Metadata SAP
    machine_data: {
      machines: [],
      machine_removal: false,
      report_number: '',
      sap_metadata: {
        is_mixed_material: false,
        is_rescued_project: false,
        patent_number: '',
        is_project_finished: false,
        critical_observation: '',
        project_with_other_provider: '',
        installation_level: 'NORMAL',
        other_provider: ''
      }
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

  // Query para obtener datos del reporte existente (si es edición)
  const { data: existingReport, isLoading: reportLoading } = useQuery({
    queryKey: ['visitReport', id],
    queryFn: () => api.get(`/documents/visit-reports/${id}/`).then(res => res.data),
    enabled: isEditMode
  });

  // SAP Queries
  const { data: sapCallData, isLoading: sapCallLoading, error: sapCallError } = useSAPServiceCall(searchSapCallId);
  const { data: sapCustomers, isLoading: sapCustomersLoading } = useSAPCustomerSearch(debouncedCustomerSearch);
  const { data: sapTechnicians, isLoading: sapTechniciansLoading } = useSAPTechnicians('technician');

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
        // CORRECCIÓN: No sobrescribir técnico en edición si ya tiene valor
        technician: (isEditMode && prev.technician) ? prev.technician : (sapCallData.technician || prev.technician),
        technician_id: (isEditMode && prev.technician_id) ? prev.technician_id : (sapCallData.technician_code || prev.technician_id),
        address: sapCallData.address || prev.address,
        commune: sapCallData.commune || prev.commune,
        city: sapCallData.city || prev.city,

        // 4. Contacto (Usar datos del instalador si están disponibles, sino contacto)
        installer: sapCallData.installer_name || sapCallData.contact_name || prev.installer,
        installer_phone: sapCallData.installer_phone || sapCallData.telephone || prev.installer_phone,

        // 5. Observaciones (Mapeo directo desde campos personalizados de SAP)
        // Eliminado sapCallData.description para evitar pre-cargar la descripción de la incidencia en observaciones generales
        general_observations: sapCallData.general_observations || prev.general_observations,
        wall_observations: sapCallData.obs_muro || prev.wall_observations,
        matrix_observations: sapCallData.obs_matriz || prev.matrix_observations,
        slab_observations: sapCallData.obs_losa || prev.slab_observations,
        storage_observations: sapCallData.obs_almac || prev.storage_observations,
        pre_assembled_observations: sapCallData.obs_pre_arm || prev.pre_assembled_observations,
        exterior_observations: sapCallData.obs_exter || prev.exterior_observations,

        // 6. Responsable (desde técnico de SAP)
        incident_responsible: sapCallData.technician || sapCallData.assignee || prev.incident_responsible,

        // 7. Máquinas Vectoriales (Reverse Mapping de UDFs)
        machine_data: (() => {
          const machinesFromSap = [];
          for (let i = 1; i <= 6; i++) {
            const maq = sapCallData[`maq${i}`];
            const ini = sapCallData[`ini${i}`];
            const cor = sapCallData[`cor${i}`];
            if (maq || ini || cor) {
              machinesFromSap.push({ machine: maq || '', start: ini || '', cut: cor || '' });
            }
          }
          return {
            ...prev.machine_data,
            machines: machinesFromSap.length > 0 ? machinesFromSap : prev.machine_data.machines,
            machine_removal: sapCallData.retiro_maq === 'Si' ? true : (sapCallData.retiro_maq === 'No' ? false : prev.machine_data.machine_removal)
          };
        })(),

        // Mantener otros campos
      }));

      //alert(`✅ Datos cargados desde SAP: Llamada ${sapCallData.call_id}`);
    }
  }, [sapCallData]);


  // Efecto para cargar datos del reporte existente (Modo Edición)
  useEffect(() => {
    if (existingReport) {
      setFormData(prev => ({
        ...prev,
        ...existingReport,
        // Asegurar que las fechas estén en formato YYYY-MM-DD
        visit_date: existingReport.visit_date ? existingReport.visit_date.split('T')[0] : prev.visit_date,
      }));
      // Si no teníamos incidentId (modo edición directo desde URL), recuperarlo del reporte
      if (!incidentId && existingReport?.related_incident?.id && !hasSetIncidentIdFromReport) {
        setIncidentId(existingReport.related_incident.id);
        setHasSetIncidentIdFromReport(true);
      }
      // Si el reporte tiene un SAP Call ID, disparar la búsqueda
      if (existingReport.sap_call_id) {
        setSearchSapCallId(existingReport.sap_call_id);
      }
    }
  }, [existingReport, incidentId, hasSetIncidentIdFromReport]);




  // Cargar datos de la incidencia al formulario (Optimizado para NUEVOS y EDICIÓN)
  useEffect(() => {
    if (incident) {
      // MAGIA SILENCIOSA: Disparar la sincronización SAP en background automáticamente
      // si la incidencia ya vino enlazada a un SAP DocNum desde el Backend (solo si no tenemos ya uno).
      if (!isEditMode) {
        if (incident.sap_doc_num) {
          setSapCallIdInput(incident.sap_doc_num.toString());
          setSearchSapCallId(incident.sap_doc_num);
        } else if (incident.sap_call_id) {
          setSapCallIdInput(incident.sap_call_id.toString());
          setSearchSapCallId(incident.sap_call_id);
        }
      }

      // Generar número de orden automáticamente vinculado a la incidencia (solo si no es edición)
      const generateOrderNumber = async () => {
        if (isEditMode) return;
        try {
          // Pasar incident_id para vincular el código del reporte al de la incidencia
          const response = await api.get(`/documents/generate-order-number/?incident_id=${incident.id}`);
          const orderNumber = response.data.order_number;

          setFormData(prev => ({
            ...prev,
            // Información del proyecto/cliente (del incidente si están vacíos)
            project_name: prev.project_name || incident.obra || '',
            client_name: prev.client_name || incident.cliente || '',
            client_rut: prev.client_rut || incident.cliente_rut || '',
            address: prev.address || incident.direccion_cliente || '',
            commune: prev.commune || incident.comuna || '',
            city: prev.city || incident.ciudad || '',
            visit_reason: prev.visit_reason || '01-Visita Técnica',

            // Personal (del incidente si están vacíos)
            salesperson: prev.salesperson || incident.salesperson || '',
            technician: prev.technician || (
              typeof incident.responsable === 'object'
                ? (incident.responsable?.full_name || incident.responsable?.name || '')
                : (incident.responsable || '')
            ),
            technician_id: prev.technician_id || incident.technician_id || '',
            installer: prev.installer || incident.installer_name || incident.contact_name || '',
            installer_phone: prev.installer_phone || incident.installer_phone || incident.contact_phone || '',

            // Información del producto (del incidente si están vacíos)
            product_category: prev.product_category || incident.categoria?.name || incident.categoria || '',
            product_subcategory: prev.product_subcategory || incident.subcategoria || '',
            product_sku: prev.product_sku || incident.sku || '',
            product_lot: prev.product_lot || incident.lote || '',
            product_provider: prev.product_provider || incident.provider || '',

            // Información de la incidencia (SIEMPRE del incidente)
            incident_code: incident.code || '',
            incident_description: incident.descripcion || '',
            incident_priority: incident.prioridad || '',
            incident_responsible: typeof incident.responsable === 'object'
              ? (incident.responsable?.full_name || incident.responsable?.name || '')
              : (incident.responsable || ''),
            incident_detection_date: incident.fecha_deteccion || '',
            incident_detection_time: incident.hora_deteccion || '',
            incident_immediate_actions: incident.acciones_inmediatas || '',

            // Número de orden generado si es nuevo
            order_number: isEditMode ? prev.order_number : (orderNumber || prev.order_number)
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

            // Personal
            salesperson: incident.salesperson || '',
            technician: typeof incident.responsable === 'object'
              ? (incident.responsable?.full_name || incident.responsable?.name || '')
              : (incident.responsable || ''),

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
    }
    
    // Independiente del modo edición, siempre queremos el estado de documentos si hay incidencia
    if (incident) {
      checkDocumentStatus();
    }
  }, [incident, isEditMode]);

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

      window.scrollTo(0, 0);
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

      if (isEditMode) {
        await api.patch(`/documents/visit-reports/${id}/`, formDataToSend);
        alert('✅ Reporte de visita actualizado exitosamente. El PDF se ha regenerado.');
        window.scrollTo(0, 0);
        navigate('/visit-reports');
      } else {
        await createReportMutation.mutateAsync(formDataToSend);
      }
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
    <div className="max-w-6xl mx-auto p-6">
      {/* Header - Industrial Premium */}
      <div className="relative mb-8 pt-6">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/5 via-indigo-600/5 to-purple-600/5 rounded-3xl blur-3xl -z-10"></div>
        <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
          <div>
            <button
              onClick={() => navigate('/visit-reports')}
              className="group flex items-center gap-2 px-4 py-2 rounded-xl bg-white/50 hover:bg-white text-slate-500 hover:text-blue-600 border border-transparent hover:border-blue-100 transition-all duration-300 mb-4 shadow-sm"
            >
              <ArrowLeftIcon className="w-4 h-4 transition-transform group-hover:-translate-x-1" />
              <span className="text-xs font-bold uppercase tracking-wider">Volver a Reportes</span>
            </button>

            <div className="flex items-center gap-4">
              <div className="p-3 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl shadow-lg shadow-blue-500/30">
                <DocumentTextIcon className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-black text-slate-800 tracking-tight uppercase flex items-center">
                  Reporte de Visita
                  <span className="ml-3 px-3 py-1 bg-indigo-50 text-indigo-600 text-[10px] rounded-lg border border-indigo-100 align-middle">
                    {reportType === 'cliente' ? 'Cliente' : 'Interno'}
                  </span>
                  {(incident?.sap_doc_num || incident?.sap_call_id) && (
                    <button
                      type="button"
                      onClick={() => {
                        const sapId = incident?.sap_doc_num || incident?.sap_call_id;
                        setSearchSapCallId(null);
                        setTimeout(() => setSearchSapCallId(sapId), 100);
                      }}
                      className="ml-4 flex items-center gap-1 px-3 py-1 text-xs font-bold bg-green-50 text-green-700 hover:bg-green-100 border border-green-200 rounded-lg transition-colors"
                      title="Forzar actualización desde SAP"
                    >
                      <CloudArrowDownIcon className={`w-4 h-4 ${sapCallLoading ? 'animate-bounce' : ''}`} />
                      Sync SAP
                    </button>
                  )}
                </h1>
                <p className="text-slate-500 font-medium text-sm mt-1">
                  {incident ? `Incidencia: ${incident.code} - ${incident.cliente}` : 'Cargando datos de incidencia...'}
                </p>
              </div>
            </div>
          </div>
        </div>
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




      {/* Formulario Principal */}
      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Información Básica - Glass Card */}
        <div className="bg-white/60 backdrop-blur-2xl border border-white/60 rounded-3xl p-6 md:p-8 space-y-6 shadow-xl shadow-slate-200/50">
          <div className="flex items-center gap-4 border-b border-slate-200/50 pb-4">
            <div className="p-2 bg-blue-50 rounded-xl border border-blue-100">
              <DocumentTextIcon className="w-5 h-5 text-blue-600" />
            </div>
            <h2 className="text-slate-800 font-black text-sm uppercase tracking-widest">Información Básica</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-wide mb-2">
                Número de Orden
              </label>
              <input
                type="text"
                value={formData.order_number}
                onChange={(e) => handleInputChange('order_number', e.target.value)}
                className="w-full bg-slate-50/50 border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-800 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all font-medium"
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

        {/* Información del Proyecto/Cliente - Glass Card */}
        <div className="bg-white/60 backdrop-blur-2xl border border-white/60 rounded-3xl p-6 md:p-8 space-y-6 shadow-xl shadow-slate-200/50">
          <div className="flex items-center gap-4 border-b border-slate-200/50 pb-4">
            <div className="p-2 bg-indigo-50 rounded-xl border border-indigo-100">
              <BuildingOfficeIcon className="w-5 h-5 text-indigo-600" />
            </div>
            <h2 className="text-slate-800 font-black text-sm uppercase tracking-widest">Ubicación y Detalles del Proyecto</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
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
                    value={incident?.sap_doc_num || searchSapCallId || formData.sap_call_id}
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

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
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

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
                Técnico (SAP)
              </label>
              <select
                value={formData.technician_id || ''}
                onChange={(e) => {
                  const techId = e.target.value;
                  const techName = sapTechnicians?.find(t => t.id.toString() === techId)?.name || '';
                  setFormData(prev => ({
                    ...prev,
                    technician_id: techId,
                    technician: techName
                  }));
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
                required
              >
                <option value="">Seleccione Técnico...</option>
                {sapTechnicians?.map(tech => (
                  <option key={tech.id} value={tech.id}>
                    {tech.name} (id: {tech.id})
                  </option>
                ))}
              </select>
              {sapTechniciansLoading && <p className="text-[10px] text-blue-500 animate-pulse mt-1">Cargando técnicos de SAP...</p>}
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

        {/* Métricas e Información de Obra */}
        <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg shadow-md p-6 border-l-4 border-purple-500">
          <h2 className="text-xl font-semibold text-purple-900 mb-4 flex items-center">
            <SparklesIcon className="h-6 w-6 mr-2 text-purple-600" />
            Desempeño Técnico y Métricas
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="flex flex-col space-y-4 bg-white p-4 rounded-xl border border-purple-100 shadow-sm">
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.machine_data.sap_metadata?.is_mixed_material || false}
                  onChange={(e) => {
                    setFormData(prev => ({
                      ...prev,
                      machine_data: {
                        ...prev.machine_data,
                        sap_metadata: { ...prev.machine_data.sap_metadata, is_mixed_material: e.target.checked }
                      }
                    }));
                  }}
                  className="w-5 h-5 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                />
                <span className="text-sm font-medium text-gray-700">Material Mezclado</span>
              </label>

              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.machine_data.sap_metadata?.is_rescued_project || false}
                  onChange={(e) => {
                    setFormData(prev => ({
                      ...prev,
                      machine_data: {
                        ...prev.machine_data,
                        sap_metadata: { ...prev.machine_data.sap_metadata, is_rescued_project: e.target.checked }
                      }
                    }));
                  }}
                  className="w-5 h-5 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                />
                <span className="text-sm font-medium text-gray-700">Obra Rescatada (No Nueva)</span>
              </label>

              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.machine_data.sap_metadata?.is_project_finished || false}
                  onChange={(e) => {
                    setFormData(prev => ({
                      ...prev,
                      machine_data: {
                        ...prev.machine_data,
                        sap_metadata: { ...prev.machine_data.sap_metadata, is_project_finished: e.target.checked }
                      }
                    }));
                  }}
                  className="w-5 h-5 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                />
                <span className="text-sm font-medium text-gray-700">Obra Finalizada</span>
              </label>
            </div>

            <div className="space-y-4 md:col-span-2">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nivel de Instalación
                  </label>
                  <select
                    value={formData.machine_data.sap_metadata?.installation_level || 'NORMAL'}
                    onChange={(e) => {
                      setFormData(prev => ({
                        ...prev,
                        machine_data: {
                          ...prev.machine_data,
                          sap_metadata: { ...prev.machine_data.sap_metadata, installation_level: e.target.value }
                        }
                      }));
                    }}
                    className="w-full px-3 py-2 border border-purple-200 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="NORMAL">Normal</option>
                    <option value="DEFICIENTE">Deficiente</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    N° Patente Vehículo
                  </label>
                  <input
                    type="text"
                    value={formData.machine_data.sap_metadata?.patent_number || ''}
                    onChange={(e) => {
                      setFormData(prev => ({
                        ...prev,
                        machine_data: {
                          ...prev.machine_data,
                          sap_metadata: { ...prev.machine_data.sap_metadata, patent_number: e.target.value.toUpperCase() }
                        }
                      }));
                    }}
                    className="w-full px-3 py-2 border border-purple-200 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 uppercase"
                    placeholder="XXYY12"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Obra c/ Otro Proveedor
                  </label>
                  <select
                    value={formData.machine_data.sap_metadata?.project_with_other_provider || ''}
                    onChange={(e) => {
                      setFormData(prev => ({
                        ...prev,
                        machine_data: {
                          ...prev.machine_data,
                          sap_metadata: { ...prev.machine_data.sap_metadata, project_with_other_provider: e.target.value }
                        }
                      }));
                    }}
                    className="w-full px-3 py-2 border border-purple-200 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="">Seleccione...</option>
                    <option value="SI">Sí</option>
                    <option value="NO">No</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nombre Otro Proveedor
                  </label>
                  <input
                    type="text"
                    value={formData.machine_data.sap_metadata?.other_provider || ''}
                    onChange={(e) => {
                      setFormData(prev => ({
                        ...prev,
                        machine_data: {
                          ...prev.machine_data,
                          sap_metadata: { ...prev.machine_data.sap_metadata, other_provider: e.target.value }
                        }
                      }));
                    }}
                    disabled={formData.machine_data.sap_metadata?.project_with_other_provider !== 'SI'}
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 ${formData.machine_data.sap_metadata?.project_with_other_provider !== 'SI' ? 'bg-gray-100 border-gray-200 text-gray-400' : 'border-purple-200 bg-white'}`}
                    placeholder="Ej. TIGRE, TUPEMESA..."
                  />
                </div>
            </div>
          </div>
      </div>
    </div>

    {/* Observaciones */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Observaciones
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Observaciones Muro/Tabique
              </label>
              <textarea
                value={formData.wall_observations}
                onChange={(e) => handleInputChange('wall_observations', e.target.value)}
                rows={4}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50/50 shadow-inner"
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
                rows={4}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50/50 shadow-inner"
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
                rows={4}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50/50 shadow-inner"
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
                rows={4}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50/50 shadow-inner"
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
                rows={4}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50/50 shadow-inner"
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
                rows={4}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50/50 shadow-inner"
                placeholder="Describa las observaciones exteriores..."
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Observaciones Generales
              </label>
              <textarea
                value={formData.general_observations}
                onChange={(e) => handleInputChange('general_observations', e.target.value)}
                rows={5}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50/50 shadow-inner"
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
