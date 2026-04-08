import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { incidentsAPI } from '../services/api';
import api from '../services/api';
import { useNotifications } from '../hooks/useNotifications';
import { useAuth } from '../contexts/AuthContext';
import {
  ArrowLeftIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  UserIcon,
  BuildingOfficeIcon,
  DocumentTextIcon,
  TagIcon,
  CalendarIcon,
  ClockIcon,
  ExclamationCircleIcon,
  PlusIcon,
  MagnifyingGlassIcon,
  CloudArrowDownIcon,
  BoltIcon,
  PaperClipIcon,
  XMarkIcon,
  TrashIcon
} from '@heroicons/react/24/outline';
import { useSAPServiceCall, useSAPCustomerSearch, useSAPCustomerDetails, useSAPSalesEmployees, useSAPTechnicians } from '../hooks/useSAPData';
import { useDebounce } from '../hooks/useDebounce';

const CreateIncident = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { showSuccess, showError } = useNotifications();
  const { user } = useAuth();
  const isEditMode = !!id;
  
  const countryCode = localStorage.getItem('country_code') || 'CL';
  const isChile = countryCode === 'CL';
  console.log('[CreateIncident] Loaded countryCode:', countryCode, 'isChile:', isChile);

  const [formData, setFormData] = useState({
    cliente: '',
    customer_code: '',
    provider: 'PoliFusion',
    obra: '',
    proyecto: '',
    project_code: '',
    descripcion: '',
    salesperson: '',
    salesperson_code: null,
    sap_call_id: null,
    categoria: 'tuberia_beta',
    subcategoria: '',
    responsable: 'Patricio Morales',
    technician_code: null,
    prioridad: 'media',
    direccion_cliente: '',
    comuna: '',
    ciudad: '',
    fecha_deteccion: new Date().toISOString().split('T')[0],
    hora_deteccion: new Date().toTimeString().split(' ')[0].substring(0, 5),
  });

  // Limpiar valor por defecto quemado para países distintos a Chile
  useEffect(() => {
    if (!isChile && formData.responsable === 'Patricio Morales') {
      setFormData(prev => ({ ...prev, responsable: '' }));
    }
  }, [isChile]);

  const { data: existingIncident, isLoading: loadingIncident } = useQuery({
    queryKey: ['incident', id],
    queryFn: async () => {
      const response = await incidentsAPI.get(id);
      return response.data || response;
    },
    enabled: isEditMode,
  });

  useEffect(() => {
    if (existingIncident) {
      setFormData({
        cliente: existingIncident.cliente || '',
        customer_code: existingIncident.customer_code || '',
        provider: existingIncident.provider || '',
        obra: existingIncident.obra || '',
        proyecto: existingIncident.proyecto || '',
        project_code: existingIncident.project_code || '',
        descripcion: existingIncident.descripcion || '',
        salesperson: existingIncident.salesperson || '',
        sap_call_id: existingIncident.sap_call_id || null,
        categoria: existingIncident.categoria || 'tuberia_beta',
        subcategoria: existingIncident.subcategoria || '',
        responsable: existingIncident.responsable || 'Patricio Morales',
        prioridad: existingIncident.prioridad || 'media',
        direccion_cliente: existingIncident.direccion_cliente || '',
        comuna: existingIncident.comuna || '',
        ciudad: existingIncident.ciudad || '',
        fecha_deteccion: existingIncident.fecha_deteccion || existingIncident.fecha_reporte || new Date().toISOString().split('T')[0],
        hora_deteccion: existingIncident.hora_deteccion || new Date().toTimeString().split(' ')[0].substring(0, 5),
      });
      if (existingIncident.sap_doc_num) {
        setSearchSapCallId(existingIncident.sap_doc_num);
        setSapCallIdInput(existingIncident.sap_doc_num);
      } else {
        // Fallback visual vacío para evitar cruces
        setSapCallIdInput('');
      }
    }
  }, [existingIncident]);

  const [sapCallIdInput, setSapCallIdInput] = useState('');
  const [searchSapCallId, setSearchSapCallId] = useState('');

  // Autocomplete para Cliente en el campo principal
  const debouncedClientInput = useDebounce(formData.cliente, 500);
  const [selectedCustomerCode, setSelectedCustomerCode] = useState(null);
  const [showSuggestions, setShowSuggestions] = useState(false);

  // Autocomplete para Vendedor
  const [salespersonInput, setSalespersonInput] = useState('');
  const [showSalespersonDropdown, setShowSalespersonDropdown] = useState(false);

  // Dropdown para Obras
  const [showObraDropdown, setShowObraDropdown] = useState(false);

  // File Upload State
  const [selectedFiles, setSelectedFiles] = useState([]);

  const handleFileSelect = (e) => {
    if (e.target.files) {
      const filesArray = Array.from(e.target.files);
      setSelectedFiles(prev => [...prev, ...filesArray]);
    }
  };

  const removeFile = (index) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const { data: sapCallData, isLoading: sapCallLoading, error: sapCallError } = useSAPServiceCall(searchSapCallId);
  const { data: sapCustomersForClient } = useSAPCustomerSearch(debouncedClientInput);
  const { data: sapSalesEmployees } = useSAPSalesEmployees();
  const { data: customerDetails } = useSAPCustomerDetails(selectedCustomerCode);
  const { data: sapTechnicians, isLoading: sapTechniciansLoading } = useSAPTechnicians();

  // Auto-popular campos al seleccionar cliente
  useEffect(() => {
    if (customerDetails) {
      console.log('🔄 Auto-populating customer data:', customerDetails);
      setFormData(prev => ({
        ...prev,
        salesperson: customerDetails.salesperson_name || '',
        salesperson_code: customerDetails.salesperson_code || null,
      }));

      // Autoselección de obra si hay solo una
      if (customerDetails.projects?.length === 1 && !formData.project_code) {
        const p = customerDetails.projects[0];
        console.log('🏗️ Auto-selecting single project:', p);
        setFormData(prev => ({
          ...prev,
          obra: p.obra,
          proyecto: p.proyecto,
          project_code: p.proyecto,
          direccion_cliente: p.direccion || prev.direccion_cliente,
          comuna: p.comuna || prev.comuna,
          ciudad: p.ciudad || prev.ciudad
        }));
      }
    }
  }, [customerDetails, formData.project_code]);

  // Limpiar selección cuando usuario escribe algo DISTINTO al cliente seleccionado
  useEffect(() => {
    // Solo limpiar si el usuario realmente cambió el texto (el debouncer terminó y no coincide con el cliente seleccionado)
    if (selectedCustomerCode && customerDetails &&
      debouncedClientInput !== customerDetails.card_name &&
      debouncedClientInput === formData.cliente) {
      console.log('🧹 Clearing selection because input no longer matches:', debouncedClientInput);
      setSelectedCustomerCode(null);

        // ¡CRÍTICO! Limpiar el customer_code oculto devuelto por SAP si el input se ensucia
        setFormData(prev => ({
          ...prev,
          customer_code: '',
          salesperson: '',
          salesperson_code: null,
          proyecto: '',
          project_code: ''
        }));
    }
  }, [debouncedClientInput, customerDetails, selectedCustomerCode, formData.cliente]);

  useEffect(() => {
    if (sapCallData) {
      let sapDate = null;
      let sapTime = null;
      if (sapCallData.create_date) {
        try {
          const d = new Date(sapCallData.create_date);
          if (!isNaN(d.getTime())) {
            sapDate = d.toISOString().split('T')[0];
            sapTime = d.toTimeString().split(' ')[0].substring(0, 5);
          }
        } catch (e) { }
      }
      // SAP create_time viene como "HH:MM" (convertido en backend)
      if (sapCallData.create_time) {
        sapTime = sapCallData.create_time;
      }

      // Mapeo de prioridad SAP → App (SAP devuelve 'L','M','H' o 0,1,2)
      let mappedPriority = null;
      if (sapCallData.sap_priority !== null && sapCallData.sap_priority !== undefined) {
        const priorityMap = { 0: 'baja', 1: 'media', 2: 'alta', 'L': 'baja', 'M': 'media', 'H': 'alta' };
        mappedPriority = priorityMap[sapCallData.sap_priority] || null;
      }

      setFormData(prev => ({
        ...prev,
        sap_call_id: sapCallData.call_id,
        sap_doc_num: sapCallData.doc_num,
        cliente: sapCallData.customer_name || prev.cliente,
        customer_code: sapCallData.customer_code || prev.customer_code,
        obra: sapCallData.project_name || prev.obra,
        proyecto: sapCallData.project_code || prev.proyecto,
        project_code: sapCallData.project_code || prev.project_code,
        salesperson: sapCallData.salesperson || prev.salesperson,
        responsable: sapCallData.technician || sapCallData.assignee || prev.responsable,
        provider: 'PoliFusion',
        fecha_deteccion: sapDate || prev.fecha_deteccion,
        hora_deteccion: sapTime || prev.hora_deteccion,
        direccion_cliente: sapCallData.address || prev.direccion_cliente,
        comuna: sapCallData.commune || prev.comuna,
        ciudad: sapCallData.city || prev.ciudad,
        descripcion: sapCallData.description || prev.descripcion,
        prioridad: mappedPriority || prev.prioridad,
      }));
      showSuccess(`Conectado: Datos sincronizados desde Folio SAP ${sapCallData.doc_num || sapCallData.call_id}`);
    }
  }, [sapCallData]);

  const createIncidentMutation = useMutation({
    mutationFn: async (data) => {
      // Preparar datos para el backend
      const cleanData = {
        ...data,
        cliente_rut: data.customer_code || '', // Asegurar que el RUT viaje en el campo correcto
      };

      let response;
      if (isEditMode) {
        response = await incidentsAPI.update(id, cleanData);
      } else {
        response = await incidentsAPI.create(cleanData);
      }

      // Upload files if any after a small delay to prevent race condition with Database sync
      const incidentId = isEditMode ? id : (response.data?.id || response.id);

      if (incidentId && selectedFiles.length > 0) {
        // Pausar 3 Segundos intencionalmente para la estabilidad de la transacción asíncrona SAP en el Backend
        await new Promise(resolve => setTimeout(resolve, 3000));

        const uploadPromises = selectedFiles.map(file => {
          const isImage = file.type.startsWith('image/');
          const formData = new FormData();

          if (isImage) {
            formData.append('image', file);
            return api.post(`/incidents/${incidentId}/images/`, formData);
          } else {
            formData.append('file', file);
            formData.append('incident_id', incidentId);
            formData.append('document_type', 'incident_attachment');
            formData.append('description', file.name);
            return api.post(`/documents/attachments/incident/${incidentId}/upload/`, formData);
          }
        });

        await Promise.all(uploadPromises);
      }

      return response;
    },
    onSuccess: (data) => {
      const sapDocNum = data?.data?.sap_doc_num || data?.data?.sap_call_id;
      const msg = isEditMode ? 'Incidencia Actualizada' : 'Incidencia Creada';
      showSuccess(sapDocNum ? `${msg} y Sincronizada (Folio SAP: ${sapDocNum})` : `${msg} (Solo Local)`);
      queryClient.invalidateQueries(['incidents']);
      queryClient.invalidateQueries(['incidents-search']);
      window.scrollTo(0, 0);
      navigate('/incidents');
    },
    onError: (error) => showError(`ERROR: No se pudo guardar - ${error.message}`),
  });

  const handleSubmit = (e) => {
    e.preventDefault();

    // Buscar coincidencia exacta o case-insensitive por nombre
    let finalCode = formData.salesperson_code;
    if (formData.salesperson && !finalCode && sapSalesEmployees) {
      const matchedEmp = sapSalesEmployees.find(emp =>
        emp.name.toLowerCase() === formData.salesperson.trim().toLowerCase()
      );
      if (matchedEmp) {
        finalCode = matchedEmp.code;
      }
    }

    // Auto-mapear el código del proyecto (Obra) de forma estricta
    let finalProjectCode = formData.project_code || formData.proyecto;
    if (formData.obra && !finalProjectCode && customerDetails?.projects) {
      const matchedProject = customerDetails.projects.find(p =>
        p.obra.toLowerCase() === formData.obra.trim().toLowerCase()
      );
      if (matchedProject) {
        finalProjectCode = matchedProject.proyecto; // El código de SAP
      }
    }

    const payloadToSubmit = {
      ...formData,
      salesperson_code: finalCode,
      project_code: finalProjectCode
    };

    createIncidentMutation.mutate(payloadToSubmit);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  if (loadingIncident) return (
    <div className="flex flex-col items-center justify-center p-20 space-y-4">
      <div className="w-12 h-12 border-2 border-purple-500 border-t-transparent animate-spin rounded-full"></div>
      <p className="text-gray-400 text-sm">Cargando datos...</p>
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 p-6 pb-20 transition-colors duration-300">
      <div className="max-w-6xl mx-auto space-y-8 animate-fade-in">

        {/* Header - Industrial Premium */}
        <div className="relative mb-8 pt-6">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600/5 via-indigo-600/5 to-purple-600/5 rounded-3xl blur-3xl -z-10"></div>
          <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
            <div>
              <button
                onClick={() => navigate('/incidents')}
                className="group flex items-center gap-2 px-4 py-2 rounded-xl bg-white/50 hover:bg-white text-slate-500 hover:text-blue-600 border border-transparent hover:border-blue-100 transition-all duration-300 mb-4 shadow-sm"
              >
                <ArrowLeftIcon className="w-4 h-4 transition-transform group-hover:-translate-x-1" />
                <span className="text-xs font-bold uppercase tracking-wider">Volver a Incidencias</span>
              </button>

              <div className="flex items-center gap-4">
                <div className="p-3 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl shadow-lg shadow-blue-500/30">
                  <DocumentTextIcon className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-black text-slate-800 tracking-tight uppercase">
                    {isEditMode ? 'Editar Incidencia' : 'Nueva Incidencia'}
                  </h1>
                  <p className="text-slate-500 font-medium text-sm mt-1">
                    Complete el formulario técnico para registrar el caso
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>



        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Identificación - Glass Card */}
          <div className="bg-white/60 backdrop-blur-2xl border border-white/60 rounded-3xl p-6 md:p-8 space-y-6 shadow-xl shadow-slate-200/50">
            <div className="flex items-center gap-4 border-b border-slate-200/50 pb-4">
              <div className="p-2 bg-blue-50 rounded-xl border border-blue-100">
                <UserIcon className="w-5 h-5 text-blue-600" />
              </div>
              <h3 className="text-slate-800 font-black text-sm uppercase tracking-widest">Información Principal</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="md:col-span-2 space-y-2 relative">
                <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide ml-1">Cliente / RUT</label>
                <input
                  type="text"
                  name="cliente"
                  value={formData.cliente}
                  onChange={(e) => {
                    handleChange(e);
                    setShowSuggestions(true);
                  }}
                  onFocus={() => setShowSuggestions(true)}
                  required
                  autoComplete="off"
                  placeholder="Nombre o RUT del Cliente"
                  className="w-full bg-slate-50/50 border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-800 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 outline-none transition-all placeholder-slate-400 font-medium"
                />
                {!selectedCustomerCode && showSuggestions && sapCustomersForClient && sapCustomersForClient.length > 0 && formData.cliente.length >= 3 && (
                  <div className="absolute z-50 w-full mt-1 bg-white border border-slate-200 rounded-lg shadow-xl max-h-48 overflow-y-auto ring-1 ring-black ring-opacity-5">
                    {sapCustomersForClient.map(c => (
                      <button
                        key={c.card_code}
                        type="button"
                        className="w-full text-left px-4 py-2.5 hover:bg-blue-50 border-b border-slate-100 last:border-0 group transition-colors"
                        onMouseDown={(e) => {
                          e.preventDefault(); // Evita que onBlur cierre el dropdown antes del click
                          setFormData(prev => ({ ...prev, cliente: c.card_name, customer_code: c.card_code }));
                          setSelectedCustomerCode(c.card_code); // Fetch details
                          setShowSuggestions(false); // Hide dropdown immediately
                          showSuccess('Cliente seleccionado desde SAP');
                        }}
                      >
                        <div className="flex flex-col">
                          <span className="text-sm font-bold text-slate-900 group-hover:text-blue-600">
                            {c.card_name}
                          </span>
                          <span className="text-xs text-slate-500 font-mono mt-0.5">
                            {c.card_code}
                          </span>
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide ml-1">Código Cliente SAP</label>
                <input
                  type="text"
                  name="customer_code"
                  value={formData.customer_code}
                  onChange={(e) => {
                    handleChange(e);
                    // Opcional: si el usuario escribe el código, también buscar sugerencias
                    if (e.target.value.length >= 3) {
                      setShowSuggestions(true);
                    }
                  }}
                  onFocus={() => setShowSuggestions(true)}
                  placeholder="Ej: C76000000-0"
                  className="w-full bg-slate-50/50 border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-800 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 outline-none transition-all placeholder-slate-400 font-mono"
                />
              </div>

              <div className="md:col-span-2 space-y-2 relative">
                <div className="flex justify-between items-center">
                  <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide ml-1">
                    Obra Principal {(countryCode === 'PE' || countryCode === 'CO') && <span className="text-red-500 font-bold ml-1">* (REQUERIDO SAP)</span>}
                  </label>
                  {customerDetails?.projects?.length > 0 && (
                    <span className="text-[10px] text-blue-500 font-medium animate-pulse">Sugerencias SAP</span>
                  )}
                </div>
                <div className="relative group">
                  <input
                    type="text"
                    name="obra"
                    value={formData.obra}
                    onChange={handleChange}
                    onFocus={() => setShowObraDropdown(true)}
                    onBlur={() => setTimeout(() => setShowObraDropdown(false), 200)}
                    autoComplete="off"
                    placeholder="Nombre de la Obra o Edificio"
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 text-sm text-slate-900 focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 outline-none transition-all placeholder-gray-400"
                  />
                  <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none opacity-40 group-hover:opacity-100 transition-opacity">
                    <BuildingOfficeIcon className="w-4 h-4 text-slate-400" />
                  </div>
                </div>
                {showObraDropdown && customerDetails?.projects && (
                  <div className="absolute z-50 w-full mt-1 bg-white border border-slate-200 rounded-lg shadow-2xl max-h-60 overflow-y-auto overscroll-contain ring-1 ring-black ring-opacity-5">
                    {customerDetails.projects.length === 0 ? (
                      <div className="px-4 py-3 text-xs text-slate-500 italic">No se encontraron obras para este cliente</div>
                    ) : (
                      customerDetails.projects
                        .filter(p => {
                          const obraInput = formData.obra?.toLowerCase() || '';
                          const proyInput = formData.proyecto?.toLowerCase() || '';
                          return (!obraInput || p.obra.toLowerCase().includes(obraInput) || p.proyecto.toLowerCase().includes(obraInput)) &&
                            (!proyInput || p.proyecto.toLowerCase().includes(proyInput) || p.obra.toLowerCase().includes(proyInput));
                        })
                        .map((p, idx) => (
                          <button
                            key={idx}
                            type="button"
                            onMouseDown={(e) => {
                              e.preventDefault();
                              setFormData(prev => ({
                                ...prev,
                                obra: p.obra,
                                proyecto: p.proyecto,
                                project_code: p.proyecto, // Sincronizar campo esperado por backend
                                direccion_cliente: p.direccion || prev.direccion_cliente,
                                comuna: p.comuna || prev.comuna,
                                ciudad: p.ciudad || prev.ciudad
                              }));
                              setShowObraDropdown(false);
                            }}
                            className="w-full text-left px-4 py-2.5 hover:bg-blue-50 border-b border-slate-100 last:border-0 group/item transition-colors"
                          >
                            <div className="flex flex-col">
                              <span className="text-sm font-bold text-slate-900 group-hover/item:text-blue-600">{p.obra}</span>
                              <div className="flex items-center gap-2 mt-0.5">
                                <span className="text-[10px] px-1.5 py-0.5 bg-slate-100 text-slate-500 rounded-md font-medium">{p.proyecto}</span>
                                {p.direccion && (
                                  <span className="text-[10px] text-slate-400 truncate italic">/ {p.direccion}</span>
                                )}
                              </div>
                            </div>
                          </button>
                        ))
                    )}
                  </div>
                )}
              </div>
              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide ml-1">Código de Obra SAP</label>
                <div className="relative group">
                  <input
                    type="text"
                    name="proyecto"
                    value={formData.proyecto}
                    onChange={handleChange}
                    onFocus={() => setShowObraDropdown(true)}
                    onBlur={() => setTimeout(() => setShowObraDropdown(false), 200)}
                    autoComplete="off"
                    placeholder="Código manual o clic para buscar..."
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 text-sm text-slate-900 focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 outline-none transition-all font-mono placeholder-gray-400"
                  />
                  <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none opacity-40">
                    <DocumentTextIcon className="w-4 h-4 text-slate-400" />
                  </div>
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide ml-1">Dirección</label>
                <div className="relative group">
                  <input
                    type="text"
                    name="direccion_cliente"
                    value={formData.direccion_cliente}
                    onChange={handleChange}
                    autoComplete="off"
                    placeholder="Calle y número"
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 text-sm text-slate-900 focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 outline-none transition-all placeholder-gray-400"
                  />
                  <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none opacity-40">
                    <UserIcon className="w-4 h-4 text-slate-400" />
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide ml-1">Comuna</label>
                <input
                  type="text"
                  name="comuna"
                  value={formData.comuna}
                  onChange={handleChange}
                  placeholder="Ej: Las Condes"
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 text-sm text-slate-900 focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 outline-none transition-all placeholder-gray-400"
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide ml-1">Ciudad</label>
                <input
                  type="text"
                  name="ciudad"
                  value={formData.ciudad}
                  onChange={handleChange}
                  placeholder="Ej: Santiago"
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 text-sm text-slate-900 focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 outline-none transition-all placeholder-gray-400"
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide ml-1">Proveedor de Origen</label>
                <input
                  type="text"
                  name="provider"
                  value={formData.provider}
                  onChange={handleChange}
                  placeholder="Nombre Proveedor"
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 text-sm text-slate-900 focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 outline-none transition-all placeholder-gray-400"
                />
              </div>
              <div className="space-y-2 relative">
                <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide ml-1">Vendedor Asignado</label>
                <input
                  type="text"
                  name="salesperson"
                  value={formData.salesperson}
                  onChange={handleChange}
                  onFocus={() => setShowSalespersonDropdown(true)}
                  onBlur={() => setTimeout(() => setShowSalespersonDropdown(false), 200)}
                  autoComplete="off"
                  placeholder="Seleccione o escriba..."
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 text-sm text-slate-900 focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 outline-none transition-all placeholder-gray-400"
                />
                {showSalespersonDropdown && sapSalesEmployees && sapSalesEmployees.length > 0 && (
                  <div className="absolute z-50 w-full mt-1 bg-white border border-slate-200 rounded-lg shadow-xl max-h-48 overflow-y-auto">
                    {sapSalesEmployees
                      .filter(emp => formData.salesperson === '' || emp.name.toLowerCase().includes(formData.salesperson.toLowerCase()))
                      .map(emp => (
                        <button
                          key={emp.code}
                          type="button"
                          onMouseDown={(e) => {
                            e.preventDefault();
                            setFormData(prev => ({ ...prev, salesperson: emp.name, salesperson_code: emp.code }));
                            setShowSalespersonDropdown(false);
                            showSuccess('Vendedor seleccionado');
                          }}
                          className="w-full text-left px-4 py-2 hover:bg-blue-50 border-b border-slate-100 last:border-0"
                        >
                          <p className="text-sm font-bold text-slate-900">{emp.name}</p>
                          <p className="text-xs text-slate-500">{emp.email || `Código: ${emp.code}`}</p>
                        </button>
                      ))
                    }
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Detalles Técnicos */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white/60 backdrop-blur-2xl border border-white/60 rounded-3xl p-6 md:p-8 space-y-6 shadow-xl shadow-slate-200/50">
              <div className="flex items-center gap-4 border-b border-slate-200/50 pb-4">
                <div className="p-2 bg-cyan-50 rounded-xl border border-cyan-100">
                  <TagIcon className="w-5 h-5 text-cyan-600" />
                </div>
                <h3 className="text-slate-800 font-black text-sm uppercase tracking-widest">Clasificación</h3>
              </div>

              <div className="space-y-4">
                <div className="space-y-2">
                  <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide ml-1">Categoría</label>
                  <select
                    name="categoria"
                    value={formData.categoria}
                    onChange={handleChange}
                    required
                    className="w-full bg-slate-50/50 border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-800 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 outline-none appearance-none font-medium transition-all"
                  >
                    <option value="tuberia_beta">Tubería BETA</option>
                    <option value="tuberia_ppr">Tubería PPR</option>
                    <option value="tuberia_hdpe">Tubería HDPE</option>
                    <option value="fitting_inserto_metalico">Fitting Metálico</option>
                    <option value="fitting_ppr">Fitting PPR</option>
                    <option value="fitting_hdpe_electrofusion">Fitting HDPE Electrofusión</option>
                    <option value="otro">Otro / Desconocido</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide ml-1">Subcategoría / Detalle</label>
                  <input
                    type="text"
                    name="subcategoria"
                    value={formData.subcategoria}
                    onChange={handleChange}
                    placeholder="Especificar detalle..."
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 text-sm text-slate-900 focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/20 outline-none transition-all placeholder-gray-400"
                  />
                </div>
              </div>
            </div>

            <div className="bg-white border border-slate-200 rounded-2xl p-6 md:p-8 space-y-6 shadow-lg transition-colors">
              <div className="flex items-center gap-3 border-b border-slate-100 pb-4">
                <ExclamationCircleIcon className="w-5 h-5 text-rose-600" />
                <h3 className="text-slate-900 font-bold text-sm uppercase tracking-wide">Prioridad y Tiempos</h3>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide ml-1">Responsable</label>
                  {isChile ? (
                    <select
                      name="responsable"
                      value={formData.responsable}
                      onChange={handleChange}
                      className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 text-sm text-slate-900 focus:border-rose-500/50 outline-none appearance-none"
                    >
                      <option value="Patricio Morales">Patricio Morales</option>
                      <option value="Marco Montenegro">Marco Montenegro</option>
                      <option value="Andrea Soto">Andrea Soto</option>
                      <option value="Carlos Mendoza">Carlos Mendoza</option>
                    </select>
                  ) : (
                    <select
                      name="responsable"
                      value={formData.responsable}
                      onChange={(e) => {
                        const val = e.target.value;
                        const tech = sapTechnicians?.find(t => t.name === val);
                        setFormData(prev => ({
                          ...prev,
                          responsable: val,
                          technician_code: tech ? tech.id : prev.technician_code
                        }));
                      }}
                      className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 text-sm text-slate-900 focus:border-rose-500/50 outline-none appearance-none"
                    >
                      {sapTechniciansLoading ? (
                        <option value={formData.responsable}>Cargando técnicos...</option>
                      ) : (sapTechnicians && sapTechnicians.length > 0) ? (
                        <>
                          <option value="">Seleccione un técnico...</option>
                          {sapTechnicians.map(tech => (
                            <option key={tech.id} value={tech.name}>
                              {tech.name}
                            </option>
                          ))}
                          {/* Fallback option showing the current one if not in list */}
                          {formData.responsable && !sapTechnicians.find(t => t.name === formData.responsable) && (
                            <option value={formData.responsable}>{formData.responsable}</option>
                          )}
                        </>
                      ) : (
                        <option value={formData.responsable}>{formData.responsable || 'No hay técnicos disponibles'}</option>
                      )}
                    </select>
                  )}
                </div>
                <div className="space-y-2">
                  <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide ml-1">Prioridad</label>
                  <select
                    name="prioridad"
                    value={formData.prioridad}
                    onChange={handleChange}
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 text-sm text-slate-900 focus:border-rose-500/50 outline-none appearance-none"
                  >
                    <option value="baja">Baja</option>
                    <option value="media">Media</option>
                    <option value="alta">Alta</option>
                    <option value="critica">CRÍTICA</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide ml-1">Fecha Detección</label>
                  <input
                    type="date"
                    name="fecha_deteccion"
                    value={formData.fecha_deteccion}
                    onChange={handleChange}
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 text-sm text-slate-900 focus:border-rose-500/50 outline-none"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide ml-1">Hora</label>
                  <input
                    type="time"
                    name="hora_deteccion"
                    value={formData.hora_deteccion}
                    onChange={handleChange}
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 text-sm text-slate-900 focus:border-rose-500/50 outline-none"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Descripción */}
          <div className="bg-white/60 backdrop-blur-2xl border border-white/60 rounded-3xl p-6 md:p-8 space-y-6 shadow-xl shadow-slate-200/50">
            <div className="flex items-center gap-4 border-b border-slate-200/50 pb-4">
              <div className="p-2 bg-indigo-50 rounded-xl border border-indigo-100">
                <DocumentTextIcon className="w-5 h-5 text-indigo-600" />
              </div>
              <h3 className="text-slate-800 font-black text-sm uppercase tracking-widest">Descripción Detallada</h3>
            </div>
            <div className="space-y-2">
              <textarea
                name="descripcion"
                value={formData.descripcion}
                onChange={handleChange}
                required
                rows={6}
                placeholder="Describa el problema, situación o hallazgo..."
                className="w-full bg-slate-50 border border-slate-200 focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 rounded-lg p-4 text-sm text-slate-900 placeholder-gray-400 outline-none resize-y"
              />
              <p className="text-xs text-slate-500 ml-1">Describa el problema o situación detectada.</p>
            </div>
          </div>



          {/* Evidencias y Adjuntos */}
          <div className="bg-white/60 backdrop-blur-2xl border border-white/60 rounded-3xl p-6 md:p-8 space-y-6 shadow-xl shadow-slate-200/50">
            <div className="flex items-center gap-4 border-b border-slate-200/50 pb-4">
              <div className="p-2 bg-purple-50 rounded-xl border border-purple-100">
                <PaperClipIcon className="w-5 h-5 text-purple-600" />
              </div>
              <h3 className="text-slate-800 font-black text-sm uppercase tracking-widest">Evidencias y Adjuntos (Opcional)</h3>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-center w-full">
                <label htmlFor="dropzone-file" className="flex flex-col items-center justify-center w-full h-32 border-2 border-slate-300 border-dashed rounded-2xl cursor-pointer bg-slate-50/50 hover:bg-white border-slate-300 hover:border-indigo-400 transition-all group">
                  <div className="flex flex-col items-center justify-center pt-5 pb-6">
                    <CloudArrowDownIcon className="w-8 h-8 mb-3 text-slate-400 group-hover:text-indigo-500 transition-colors" />
                    <p className="mb-2 text-sm text-slate-500"><span className="font-semibold text-indigo-600">Haga clic para subir</span> o arrastre archivos</p>
                    <p className="text-xs text-slate-400">Imágenes, PDF, Documentos (MAX. 10MB)</p>
                  </div>
                  <input id="dropzone-file" type="file" multiple className="hidden" onChange={handleFileSelect} />
                </label>
              </div>

              {selectedFiles.length > 0 && (
                <div className="space-y-2 animate-fade-in">
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Archivos Seleccionados ({selectedFiles.length})</p>
                  {selectedFiles.map((file, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg border border-slate-100">
                      <div className="flex items-center gap-3 overflow-hidden">
                        <div className="p-2 bg-indigo-50 rounded-lg">
                          <DocumentTextIcon className="w-4 h-4 text-indigo-600" />
                        </div>
                        <div className="min-w-0">
                          <p className="text-sm font-medium text-slate-700 truncate">{file.name}</p>
                          <p className="text-xs text-slate-400">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={() => removeFile(index)}
                        className="p-1 hover:bg-rose-50 text-slate-400 hover:text-rose-500 rounded-full transition-colors"
                      >
                        <XMarkIcon className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Acciones */}
          <div className="flex justify-end gap-4 pt-4">
            <button
              type="button"
              onClick={() => navigate('/incidents')}
              className="px-6 py-4 rounded-2xl border border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-50 text-[10px] font-black uppercase tracking-widest transition-all"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={createIncidentMutation.isPending}
              className="px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-2xl shadow-xl shadow-blue-500/20 text-[10px] font-black uppercase tracking-widest transition-all hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {createIncidentMutation.isPending ? 'Guardando...' : (isEditMode ? 'Guardar Cambios' : 'Registrar Incidencia')}
            </button>
          </div>
        </form>
      </div >
    </div >
  );
};

export default CreateIncident;
