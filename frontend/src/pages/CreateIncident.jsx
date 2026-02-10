import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { incidentsAPI } from '../services/api';
import { useNotifications } from '../hooks/useNotifications';
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
  XMarkIcon,
  MagnifyingGlassIcon,
  CloudArrowDownIcon
} from '@heroicons/react/24/outline';
import { useSAPServiceCall, useSAPCustomerSearch } from '../hooks/useSAPData';
import { useDebounce } from '../hooks/useDebounce';

const CreateIncident = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { showSuccess, showError } = useNotifications();
  const isEditMode = !!id;

  const [formData, setFormData] = useState({
    cliente: '',
    customer_code: '',
    provider: '',
    obra: '',
    proyecto: '',
    project_code: '',
    descripcion: '',
    salesperson: '',
    sap_call_id: null,
    categoria: 'tuberia_beta',
    subcategoria: '',
    responsable: 'Patricio Morales',
    prioridad: 'media',
    fecha_deteccion: new Date().toISOString().split('T')[0],
    hora_deteccion: new Date().toTimeString().split(' ')[0].substring(0, 5),
  });

  const { data: existingIncident, isLoading: loadingIncident } = useQuery({
    queryKey: ['incident', id],
    queryFn: async () => {
      const response = await incidentsAPI.get(id);
      return response.data || response;
    },
    enabled: isEditMode,
  });

  React.useEffect(() => {
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
        fecha_deteccion: existingIncident.fecha_deteccion || existingIncident.fecha_reporte || new Date().toISOString().split('T')[0],
        hora_deteccion: existingIncident.hora_deteccion || new Date().toTimeString().split(' ')[0].substring(0, 5),
      });
      if (existingIncident.sap_call_id) setSearchSapCallId(existingIncident.sap_call_id);
    }
  }, [existingIncident]);

  const [sapCallIdInput, setSapCallIdInput] = useState('');
  const [searchSapCallId, setSearchSapCallId] = useState('');
  const [customerSearchInput, setCustomerSearchInput] = useState('');
  const debouncedCustomerSearch = useDebounce(customerSearchInput, 500);

  const { data: sapCallData, isLoading: sapCallLoading, error: sapCallError } = useSAPServiceCall(searchSapCallId);
  const { data: sapCustomers, isLoading: sapCustomersLoading } = useSAPCustomerSearch(debouncedCustomerSearch);

  React.useEffect(() => {
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
      setFormData(prev => ({
        ...prev,
        sap_call_id: sapCallData.call_id,
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
      }));
      showSuccess(`BRIDGE_CONNECTED: Data synced from SAP Call ${sapCallData.call_id}`);
    }
  }, [sapCallData]);

  const createIncidentMutation = useMutation({
    mutationFn: (data) => {
      const cleanData = { ...data };
      if (!cleanData.obra) cleanData.obra = 'Default Location';
      if (!cleanData.descripcion) cleanData.descripcion = 'System Generated Description';
      return isEditMode ? incidentsAPI.update(id, cleanData) : incidentsAPI.create(cleanData);
    },
    onSuccess: () => {
      showSuccess(isEditMode ? 'Protocol Updated Successfully' : 'New Protocol Initiated');
      queryClient.invalidateQueries(['incidents']);
      navigate('/incidents');
    },
    onError: (error) => showError(`ERROR: Protocol failure - ${error.message}`),
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    createIncidentMutation.mutate(formData);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  if (loadingIncident) return (
    <div className="flex flex-col items-center justify-center p-20 space-y-4">
      <div className="w-12 h-12 border-2 border-purple-500/20 border-t-purple-500 animate-spin rounded-full"></div>
      <p className="data-font text-[10px] text-purple-400 uppercase tracking-widest animate-pulse">Syncing Central Archive...</p>
    </div>
  );

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-fade-in pb-20">
      {/* HUD Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div>
          <button onClick={() => navigate('/incidents')} className="flex items-center gap-2 group mb-4">
            <ArrowLeftIcon className="w-4 h-4 text-gray-500 group-hover:text-purple-400 transition-colors" />
            <span className="data-font text-[10px] text-gray-500 group-hover:text-white uppercase tracking-widest transition-colors font-black">Return_to_Matrix</span>
          </button>
          <div className="flex items-center gap-3">
            <div className="w-1.5 h-8 bg-purple-500 shadow-[0_0_10px_#b026ff]"></div>
            <h1 className="text-4xl font-black italic tracking-tighter uppercase text-white">
              {isEditMode ? 'Update_Protocol' : 'Initiate_Process'}
            </h1>
          </div>
          <p className="data-font text-[10px] text-gray-500 uppercase tracking-[0.4em] font-bold mt-2">Data Input Deck // Security Level 03</p>
        </div>

        <div className="flex items-center gap-2">
          <div className="px-4 py-2 bg-purple-600/10 border border-purple-500/30 rounded-xs">
            <p className="data-font text-[9px] text-purple-400 uppercase tracking-tighter font-black">Stage_01: Input</p>
          </div>
          <div className="w-10 h-[1px] bg-white/10"></div>
          <div className="px-4 py-2 bg-white/5 border border-white/5 rounded-xs opacity-40">
            <p className="data-font text-[9px] text-gray-500 uppercase tracking-tighter">Stage_02: Review</p>
          </div>
        </div>
      </div>

      {/* SAP Bridge - External Connection */}
      <div className="glass-panel p-6 border border-emerald-500/20 relative overflow-hidden group">
        <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-emerald-500/50 to-transparent opacity-40 transition-opacity group-hover:opacity-100"></div>
        <div className="flex items-center gap-4 mb-6">
          <CloudArrowDownIcon className="w-6 h-6 text-emerald-500" />
          <h3 className="text-white data-font text-xs font-black uppercase tracking-widest italic">External_Data_Bridge (SAP_ERP)</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="space-y-3">
            <p className="data-font text-[9px] text-gray-600 uppercase tracking-widest pl-1">Direct_Call_Sync</p>
            <div className="flex gap-2">
              <input
                type="number"
                value={sapCallIdInput}
                onChange={(e) => setSapCallIdInput(e.target.value)}
                placeholder="CALL_ID_NUM"
                className="flex-1 bg-white/5 border border-white/5 focus:border-emerald-500/30 focus:ring-1 focus:ring-emerald-500/10 rounded-xs px-4 py-3 data-font text-xs text-white placeholder-gray-800"
              />
              <button
                type="button"
                onClick={() => setSearchSapCallId(sapCallIdInput)}
                className="tactical-btn py-3 px-6 bg-emerald-500/10 border-emerald-500/20 text-emerald-500 hover:bg-emerald-500 hover:text-black hover:shadow-[0_0_15px_#10b981]"
                disabled={sapCallLoading}
              >
                {sapCallLoading ? 'SYNC...' : 'CONNECT'}
              </button>
            </div>
            {sapCallError && <p className="data-font text-[9px] text-rose-500 uppercase tracking-widest pl-1">Link_Fail: Call not found</p>}
          </div>

          <div className="space-y-3 relative">
            <p className="data-font text-[9px] text-gray-600 uppercase tracking-widest pl-1">Global_Entity_Search</p>
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-600" />
              <input
                type="text"
                value={customerSearchInput}
                onChange={(e) => setCustomerSearchInput(e.target.value)}
                placeholder="CLIENT_NAME_OR_RUT..."
                className="w-full bg-white/5 border border-white/5 focus:border-emerald-500/30 focus:ring-1 focus:ring-emerald-500/10 rounded-xs pl-10 pr-4 py-3 data-font text-xs text-white placeholder-gray-800"
              />
            </div>
            {sapCustomers && sapCustomers.length > 0 && (
              <div className="absolute z-20 w-full mt-2 bg-[#0a0f1d] border border-white/10 shadow-2xl overflow-hidden animate-scale-in">
                {sapCustomers.map(c => (
                  <button
                    key={c.card_code}
                    type="button"
                    className="w-full text-left px-5 py-3 hover:bg-white/5 border-b border-white/5 last:border-0 group"
                    onClick={() => { setFormData(prev => ({ ...prev, cliente: c.card_name, customer_code: c.card_code })); setCustomerSearchInput(''); showSuccess('Bridge: Client Linked'); }}
                  >
                    <p className="data-font text-[11px] font-black text-white group-hover:text-emerald-400 transition-colors uppercase">{c.card_name}</p>
                    <p className="data-font text-[8px] text-gray-600 uppercase mt-1">{c.card_code}</p>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Protocol Form */}
      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Segment: Identity Data */}
        <div className="glass-panel p-8 border border-white/5 space-y-8">
          <div className="flex items-center gap-4">
            <UserIcon className="w-5 h-5 text-purple-500" />
            <h3 className="text-white data-font text-xs font-black uppercase tracking-[0.3em]">Identity_Vectors</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="md:col-span-2 space-y-3">
              <label className="data-font text-[9px] text-gray-600 uppercase tracking-widest pl-1">Primary_Entity (Client)</label>
              <input
                type="text"
                name="cliente"
                value={formData.cliente}
                onChange={handleChange}
                required
                placeholder="LEGAL_ENTITY_NAME"
                className="w-full bg-white/5 border border-white/10 rounded-xs px-4 py-4 data-font text-xs text-white focus:border-purple-500/50 focus:ring-1 focus:ring-purple-500/10"
              />
            </div>
            <div className="space-y-3">
              <label className="data-font text-[9px] text-gray-600 uppercase tracking-widest pl-1">SAP_Entity_ID</label>
              <input
                type="text"
                name="customer_code"
                value={formData.customer_code}
                readOnly
                placeholder="BP_CODE"
                className="w-full bg-white/[0.02] border border-white/5 rounded-xs px-4 py-4 data-font text-xs text-gray-500 font-black cursor-not-allowed"
              />
            </div>
            <div className="md:col-span-2 space-y-3">
              <label className="data-font text-[9px] text-gray-600 uppercase tracking-widest pl-1">Location / Site (Obra)</label>
              <input
                type="text"
                name="obra"
                value={formData.obra}
                onChange={handleChange}
                placeholder="OPERATIONAL_ZONE_IDENTIFIER"
                className="w-full bg-white/5 border border-white/10 rounded-xs px-4 py-4 data-font text-xs text-white focus:border-purple-500/50 focus:ring-1 focus:ring-purple-500/10"
              />
            </div>
            <div className="space-y-3">
              <label className="data-font text-[9px] text-gray-600 uppercase tracking-widest pl-1">Internal_Project_ID</label>
              <input
                type="text"
                name="proyecto"
                value={formData.proyecto}
                onChange={handleChange}
                placeholder="PROJ_REF"
                className="w-full bg-white/5 border border-white/10 rounded-xs px-4 py-4 data-font text-xs text-white focus:border-purple-500/50 focus:ring-1 focus:ring-purple-500/10"
              />
            </div>
            <div className="space-y-3">
              <label className="data-font text-[9px] text-gray-600 uppercase tracking-widest pl-1">Origin_Provider</label>
              <input
                type="text"
                name="provider"
                value={formData.provider}
                onChange={handleChange}
                placeholder="SOURCE_PROVIDER"
                className="w-full bg-white/5 border border-white/10 rounded-xs px-4 py-4 data-font text-xs text-white focus:border-purple-500/50 focus:ring-1 focus:ring-purple-500/10"
              />
            </div>
            <div className="space-y-3">
              <label className="data-font text-[9px] text-gray-600 uppercase tracking-widest pl-1">Assigned_Agent (Sales)</label>
              <input
                type="text"
                name="salesperson"
                value={formData.salesperson}
                readOnly
                className="w-full bg-white/[0.02] border border-white/5 rounded-xs px-4 py-4 data-font text-xs text-gray-500 font-black cursor-not-allowed"
              />
            </div>
            <div className="space-y-3">
              <label className="data-font text-[9px] text-gray-500 uppercase tracking-widest pl-1">Protocol_Code</label>
              <div className="relative">
                <input
                  type="text"
                  value={isEditMode ? existingIncident?.code : "SYSTEM_GENERATED_ID"}
                  disabled
                  className="w-full bg-purple-500/5 border border-purple-500/20 rounded-xs px-4 py-4 data-font text-xs text-purple-400 font-black"
                />
                <div className="absolute inset-y-0 right-4 flex items-center"><BoltIcon className="w-4 h-4 text-purple-500/50" /></div>
              </div>
            </div>
          </div>
        </div>

        {/* Segment: Technical Details */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="glass-panel p-8 border border-white/5 space-y-8">
            <div className="flex items-center gap-4">
              <TagIcon className="w-5 h-5 text-cyan-400" />
              <h3 className="text-white data-font text-xs font-black uppercase tracking-[0.3em]">Technical_Vector</h3>
            </div>
            <div className="space-y-6">
              <div className="space-y-3">
                <label className="data-font text-[9px] text-gray-600 uppercase tracking-widest pl-1">Vector_Class (Category)</label>
                <select
                  name="categoria"
                  value={formData.categoria}
                  onChange={handleChange}
                  className="w-full bg-white/5 border border-white/10 rounded-xs px-4 py-4 data-font text-[11px] font-black text-white focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/10 uppercase"
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
              <div className="space-y-3">
                <label className="data-font text-[9px] text-gray-600 uppercase tracking-widest pl-1">Sub_Vector_Detail</label>
                <input
                  type="text"
                  name="subcategoria"
                  value={formData.subcategoria}
                  onChange={handleChange}
                  placeholder="SPECIFIC_FAILURE_TYPE"
                  className="w-full bg-white/5 border border-white/10 rounded-xs px-4 py-4 data-font text-xs text-white"
                />
              </div>
            </div>
          </div>

          <div className="glass-panel p-8 border border-white/5 space-y-8">
            <div className="flex items-center gap-4">
              <ExclamationCircleIcon className="w-5 h-5 text-rose-500" />
              <h3 className="text-white data-font text-xs font-black uppercase tracking-[0.3em]">Priority_&_Logistics</h3>
            </div>
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-3">
                  <label className="data-font text-[9px] text-gray-600 uppercase tracking-widest pl-1">Custodian_Official</label>
                  <select
                    name="responsable"
                    value={formData.responsable}
                    onChange={handleChange}
                    className="w-full bg-white/5 border border-white/10 rounded-xs px-4 py-4 data-font text-[10px] text-white focus:border-rose-500/50 uppercase"
                  >
                    <option value="Patricio Morales">Patricio Morales</option>
                    <option value="Marco Montenegro">Marco Montenegro</option>
                    <option value="Andrea Soto">Andrea Soto</option>
                    <option value="Carlos Mendoza">Carlos Mendoza</option>
                  </select>
                </div>
                <div className="space-y-3">
                  <label className="data-font text-[9px] text-gray-600 uppercase tracking-widest pl-1">Severity_Level</label>
                  <select
                    name="prioridad"
                    value={formData.prioridad}
                    onChange={handleChange}
                    className="w-full bg-white/5 border border-white/10 rounded-xs px-4 py-4 data-font text-[10px] text-white focus:border-rose-500/50 uppercase"
                  >
                    <option value="baja">Level_01 (Baja)</option>
                    <option value="media">Level_02 (Media)</option>
                    <option value="alta">Level_03 (Alta)</option>
                    <option value="critica">CRITICAL (Red Alert)</option>
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-3">
                  <label className="data-font text-[9px] text-gray-600 uppercase tracking-widest pl-1">Detection_Date</label>
                  <input
                    type="date"
                    name="fecha_deteccion"
                    value={formData.fecha_deteccion}
                    onChange={handleChange}
                    className="w-full bg-white/5 border border-white/10 rounded-xs px-4 py-4 data-font text-xs text-white"
                  />
                </div>
                <div className="space-y-3">
                  <label className="data-font text-[9px] text-gray-600 uppercase tracking-widest pl-1">Detection_Time</label>
                  <input
                    type="time"
                    name="hora_deteccion"
                    value={formData.hora_deteccion}
                    onChange={handleChange}
                    className="w-full bg-white/5 border border-white/10 rounded-xs px-4 py-4 data-font text-xs text-white"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Segment: Manifest (Description) */}
        <div className="glass-panel p-8 border border-white/5 space-y-8">
          <div className="flex items-center gap-4">
            <DocumentTextIcon className="w-5 h-5 text-purple-400" />
            <h3 className="text-white data-font text-xs font-black uppercase tracking-[0.3em]">Incident_Manifest (Full_Description)</h3>
          </div>
          <div className="space-y-3">
            <textarea
              name="descripcion"
              value={formData.descripcion}
              onChange={handleChange}
              required
              rows={6}
              placeholder="INPUT_DETAILED_MANIFEST_LOG_HERE..."
              className="w-full bg-[#0a0f1d] border border-white/5 focus:border-purple-500/50 focus:ring-1 focus:ring-purple-500/10 rounded-xs p-6 data-font text-sm text-white placeholder-gray-800 leading-relaxed custom-scrollbar-purple"
            />
            <p className="data-font text-[8px] text-gray-700 uppercase tracking-widest">Min 10 Characters Required // Data persistent in central archive</p>
          </div>
        </div>

        {/* Terminal Actions */}
        <div className="flex gap-4 pt-10 border-t border-white/5">
          <button
            type="button"
            onClick={() => navigate('/incidents')}
            className="tactical-btn py-5 px-10 data-font text-[11px] font-black uppercase tracking-widest"
          >
            Abort_Process
          </button>
          <button
            type="submit"
            disabled={createIncidentMutation.isPending}
            className="tactical-btn-active py-5 px-16 data-font text-[11px] font-black uppercase tracking-widest ml-auto shadow-[0_0_25px_#b026ff]"
          >
            {createIncidentMutation.isPending ? 'TRANSMITTING...' : (isEditMode ? 'COMMIT_CHANGES' : 'EXECUTE_PROTOCOL')}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CreateIncident;
