import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { visitReportsAPI, sapAPI, documentsAPI, api } from '../services/api';
import SignatureCanvas from '../components/SignatureCanvas';
import {
  ChevronLeftIcon,
  CheckCircleIcon,
  BuildingOffice2Icon,
  UserGroupIcon,
  ClipboardDocumentListIcon,
  WrenchScrewdriverIcon,
  PaperAirplaneIcon,
  ArrowLeftIcon,
  SparklesIcon,
  BoltIcon,
  MagnifyingGlassIcon,
  EyeIcon,
  PencilSquareIcon,
  CloudArrowDownIcon,
  XMarkIcon,
  DocumentTextIcon,
  FolderArrowDownIcon,
  PlusIcon,
  CameraIcon,
  PhotoIcon,
  TrashIcon,
  BuildingOfficeIcon,
} from '@heroicons/react/24/outline';
import ReportAttachments from '../components/ReportAttachments';
import { useSearchParams } from 'react-router-dom';

// Helpers and components for secure image loading
const isImageFile = (filename: string) => {
  const ext = filename?.split('.').pop()?.toLowerCase();
  return ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(ext || '');
};

interface SecureReportImageProps {
  reportId: string | number;
  attachmentId: number;
  alt?: string;
  className?: string;
}

const SecureReportImage: React.FC<SecureReportImageProps> = ({ reportId, attachmentId, alt = "evidence", className = "" }) => {
  const [src, setSrc] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<boolean>(false);

  useEffect(() => {
    let active = true;
    let url = '';

    const fetchImage = async () => {
      try {
        setLoading(true);
        setError(false);
        const response = await api.get(`/documents/report-attachments/${reportId}/visit/${attachmentId}/view/`, {
          responseType: 'blob'
        });
        if (active) {
          url = URL.createObjectURL(response.data);
          setSrc(url);
        }
      } catch (err) {
        console.error("Error loading secure image:", err);
        if (active) {
          setError(true);
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    fetchImage();

    return () => {
      active = false;
      if (url) {
        URL.revokeObjectURL(url);
      }
    };
  }, [reportId, attachmentId]);

  if (loading) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-slate-900/50 min-h-[100px]">
        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-emerald-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center bg-slate-950 text-slate-500 text-[9px] p-2 text-center min-h-[100px]">
        <span className="text-lg">⚠️</span>
        <span>Error de carga</span>
      </div>
    );
  }

  return <img src={src} alt={alt} className={`${className} object-cover`} />;
};

// =============================================================================
// FIELD COMPONENT (High Contrast Dashboard)
// =============================================================================
const GlassField = ({ label, children, className = '' }: { label: string; children: React.ReactNode; className?: string }) => (
  <div className={`flex flex-col gap-1.5 ${className}`}>
    <label className="text-[11px] font-black text-cyan-300 uppercase tracking-[0.25em] drop-shadow-md">{label}</label>
    {children}
  </div>
);

const inputClass = "w-full px-4 py-3 rounded-xl bg-slate-800 border border-white/30 text-white placeholder-slate-500 outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/30 transition-all text-sm font-black shadow-lg";
const textareaClass = `${inputClass} resize-none min-h-[90px]`;

// =============================================================================
// MAIN COMPONENT
// =============================================================================
const VisitReportForm = () => {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const isEditing = !!id;
  const incidentIdFromQuery = searchParams.get('incident_id');

  const [form, setForm] = useState<any>({
    // Identificación
    order_number: '',
    visit_date: (() => {
      const d = new Date();
      return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}T${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
    })(),
    
    // Proyecto/Cliente
    project_name: '',
    project_id: '',
    client_name: '',
    client_rut: '',
    address: '',
    commune: '',
    city: 'Santiago',
    construction_company: '',
    
    // Personal (Simplificado)
    salesperson: '',
    technician: '',
    technician_id: null,
    installer: '',
    client_contact: '',
    client_email: '',
    telephone: '',
    fax: '',
    contact_observations: '',
    visit_reason: '',

    // Máquinas (Dinámicas, se paddearán a 6 para SAP al enviar)
    machine_data: {
      machines: [], // Iniciar vacío para no mostrar filas en blanco innecesarias
      machine_removal: false,
      report_number: '',
    },
    
    // Observaciones (Compacto)
    wall_observations: '',
    matrix_observations: '',
    slab_observations: '',
    storage_observations: '',
    pre_assembled_observations: '',
    exterior_observations: '',
    general_observations: '',
    
    status: 'draft',
    client_signature: null,
    technician_signature: null,
    sap_call_id: null,
    
    // Metadatos Técnicos SAP (Top-level en el modelo)
    is_mixed_material: false,
    is_rescued_project: false,
    patent_number: '',
    is_project_finished: false,
    installation_level: '0',
    is_other_provider: false,
    other_provider_name: '',
    critical_observations: '',
  });

  // SAP Cascading Search State
  const [customerSearch, setCustomerSearch] = useState('');
  const [customers, setCustomers] = useState<any[]>([]);
  const [projects, setProjects] = useState<any[]>([]);
  const [isSearchingCustomers, setIsSearchingCustomers] = useState(false);
  const [projectSearch, setProjectSearch] = useState('');
  const [showProjectDropdown, setShowProjectDropdown] = useState(false);

  const [showSignatureModal, setShowSignatureModal] = useState(false);
  const [showPDFPreviewModal, setShowPDFPreviewModal] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false);
  const [previewURL, setPreviewURL] = useState<string | null>(null);
  const [showPhotoOptions, setShowPhotoOptions] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);
  const justSaved = useRef(false);
  const [createdReportId, setCreatedReportId] = useState<number | null>(null);

  // Load Technicians from SAP
  const { data: technicians } = useQuery({
    queryKey: ['sap-technicians'],
    queryFn: () => sapAPI.getTechnicians('technician').then(res => res.data),
  });

  // Load existing report
  const { data: existingReport, isLoading: isLoadingReport } = useQuery({
    queryKey: ['visit-report', id],
    queryFn: () => visitReportsAPI.get(id!).then(res => res.data),
    enabled: isEditing,
  });

  // Load existing report attachments if editing
  const { data: existingAttachments = [], refetch: refetchAttachments } = useQuery({
    queryKey: ['report-attachments', id, 'visit'],
    queryFn: () => documentsAPI.listAttachments(id!, 'visit').then(res => res.data || []),
    enabled: isEditing,
  });

  // Mutation to delete an existing attachment
  const deleteAttachmentMutation = useMutation({
    mutationFn: (attachmentId: number) => documentsAPI.deleteAttachment(id!, 'visit', attachmentId),
    onSuccess: () => {
      toast.success("Evidencia eliminada correctamente");
      refetchAttachments();
      queryClient.invalidateQueries({ queryKey: ['report-attachments', id, 'visit'] });
    },
    onError: (err) => {
      console.error("Error al eliminar evidencia:", err);
      toast.error("Error al eliminar la evidencia");
    }
  });

  useEffect(() => {
    if (existingReport && !justSaved.current) {
      setForm((prev: any) => {
        const machines = existingReport.machine_data?.machines || [];
        // Asegurar 6 slots
        const paddedMachines = [...machines];
        while(paddedMachines.length < 6) paddedMachines.push({ machine: '', start: '', cut: '' });
        
        const city = existingReport.city || 'Santiago';
        
        return { 
          ...prev, 
          ...existingReport,
          city,
          visit_date: existingReport.visit_date ? existingReport.visit_date.slice(0, 16) : prev.visit_date,
          machine_data: {
            ...prev.machine_data,
            ...existingReport.machine_data,
            machines: (existingReport.machine_data?.machines || []).filter((m: any) => m.machine || m.start || m.cut)
          }
        };
      });
      if (existingReport.client_name) setCustomerSearch(existingReport.client_name);
    }
  }, [existingReport, isEditing]); // Removed id from dependencies to avoid reset on navigate

  const [pendingPhotos, setPendingPhotos] = useState<{ file: File; description: string }[]>([]);
  const [showLocalCamera, setShowLocalCamera] = useState(false);
  const [saveAction, setSaveAction] = useState<'draft' | 'preview' | 'final' | 'sign'>('preview');

  const updateField = (field: string, value: any) => setForm((prev: any) => ({ ...prev, [field]: value }));

  const updateMachine = (index: number, field: string, value: any) => {
    const newMachines = [...form.machine_data.machines];
    newMachines[index] = { ...newMachines[index], [field]: value };
    updateField('machine_data', { ...form.machine_data, machines: newMachines });
  };

  const addMachineRow = () => {
    if (form.machine_data.machines.length >= 6) {
      toast.error("Máximo 6 máquinas permitidas por reporte (Límite SAP)");
      return;
    }
    const newMachines = [...form.machine_data.machines, { machine: '', start: '', cut: '' }];
    updateField('machine_data', { ...form.machine_data, machines: newMachines });
  };

  const removeMachineRow = (index: number) => {
    if (form.machine_data.machines.length <= 1) return;
    const newMachines = form.machine_data.machines.filter((_: any, i: number) => i !== index);
    updateField('machine_data', { ...form.machine_data, machines: newMachines });
  };

  const mutation = useMutation({
    mutationFn: (data: any) => {
      justSaved.current = true;
      // Padding a 6 slots para SAP antes de enviar
      const finalData = { ...data };
      const padded = [...(data.machine_data?.machines || [])];
      while(padded.length < 6) padded.push({ machine: '', start: '', cut: '' });
      finalData.machine_data = { 
        ...(data.machine_data || {}), 
        machines: padded.slice(0, 6) 
      };
      
      return isEditing ? visitReportsAPI.update(id!, finalData) : visitReportsAPI.create(finalData);
    },
    onSuccess: async (res) => {
      const newId = res.data.id;
      
      // SUBIR FOTOS PENDIENTES SI EXISTEN
      if (pendingPhotos.length > 0) {
        toast.loading(`Subiendo ${pendingPhotos.length} fotos...`, { id: 'photo-upload' });
        try {
          for (const photo of pendingPhotos) {
            const formData = new FormData();
            formData.append('file', photo.file);
            formData.append('description', photo.description || 'Evidencia de visita');
            await documentsAPI.uploadAttachment(newId, 'visit', formData);
          }
          setPendingPhotos([]);
          toast.success("Fotos subidas correctamente", { id: 'photo-upload' });
        } catch (uploadErr) {
          console.error("Error subiendo fotos:", uploadErr);
          toast.error("Error al subir algunas fotos", { id: 'photo-upload' });
        }
      }

      toast.success(isEditing ? 'Reporte Actualizado' : 'Reporte Creado con Éxito');
      queryClient.invalidateQueries({ queryKey: ['visit-reports'] });
      
      setCreatedReportId(newId);

      // Si la acción era firmar, abrimos el modal directamente
      if (saveAction === 'sign') {
        setShowSignatureModal(true);
      } else {
        // Redirección suave si no es para firmar
        setTimeout(() => navigate(`/visit-reports/${newId}/preview`), 500);
      }
      
      setTimeout(() => { justSaved.current = false; }, 3000);
    },
    onError: (err: any) => {
      justSaved.current = false;
      toast.error(err?.response?.data?.error || 'Error al guardar');
    },
  });
  // --- SAP LOGIC (debounce auto-search) ---
  const handleCustomerSearch = useCallback(async (query: string) => {
    if (query.length < 3) { setCustomers([]); return; }
    setIsSearchingCustomers(true);
    try {
      const res = await sapAPI.searchCustomers(query);
      setCustomers(res.data.results || []);
      if (res.data.results?.length === 0) toast('Sin resultados en SAP', { icon: '🔍' });
    } catch (e) {
      toast.error('Error buscando clientes en SAP');
    } finally {
      setIsSearchingCustomers(false);
    }
  }, []);

  const handleSearchChange = (val: string) => {
    setCustomerSearch(val);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => handleCustomerSearch(val), 500);
  };

  const selectCustomer = async (cust: any) => {
    updateField('client_name', cust.card_name);
    updateField('client_rut', cust.card_code);
    setCustomers([]);
    setCustomerSearch(cust.card_name);
    
    // Load Projects/Details
    try {
      const [projRes, detailRes] = await Promise.all([
        sapAPI.getCustomerProjects(cust.card_code),
        sapAPI.getCustomerDetails(cust.card_code)
      ]);
      setProjects(projRes.data.projects || []);
      const details = detailRes.data;
      if (details) {
        setForm((prev: any) => ({
          ...prev,
          salesperson: details.salesperson_name || '',
          client_contact: details.contact_person || '', 
          client_email: details.salesperson_email || '', // Exclusivamente correo de vendedor SAP
          telephone: details.phone1 || '',
          installer: details.installer || prev.installer,
          installer_phone: details.phone1 || prev.installer_phone,
        }));

        if (projRes.data.projects?.length === 1) {
          selectProject(projRes.data.projects[0]);
        }
      }
    } catch (e) {
      toast.error("Error cargando detalles de SAP");
    }


  };

  const selectProject = (proj: any) => {
    if (!proj) return;
    setForm((prev: any) => ({
      ...prev,
      project_name:         proj.obra                 || prev.project_name,
      project_id:           proj.proyecto             || prev.project_id,
      address:              proj.direccion            || prev.address,
      commune:              proj.comuna               || prev.commune,
      city:                 proj.ciudad               || prev.city || 'Santiago',
      construction_company: proj.construction_company || prev.construction_company,
      installer:            proj.installer            || prev.installer,
      installer_phone:      proj.installer_phone      || prev.installer_phone,
    }));
  };

  const handlePreviewPDF = async (reportId?: number) => {
    const targetId = reportId || id;
    if (!targetId) {
      toast.error("ID de reporte no encontrado");
      return;
    }
    setIsGeneratingPDF(true);
    try {
      const res = await visitReportsAPI.generatePDF(targetId, { final: false });
      // El response de axios viene en res.data cuando se usa responseType: 'blob'
      const pdfBlob = res.data instanceof Blob ? res.data : new Blob([res.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(pdfBlob);
      setPreviewURL(url);
      setShowPDFPreviewModal(true);
    } catch (e: any) {
      console.error("Error previsualizando PDF:", e);
      toast.error("Error al generar vista previa del PDF");
    } finally {
      setIsGeneratingPDF(false);
    }
  };



  if (isEditing && isLoadingReport) return <div className="flex h-screen items-center justify-center text-white">Cargando reporte...</div>;

  return (
    <div className="max-w-[1200px] mx-auto pb-20 pt-6 px-4">
      {/* HEADER COMPACTO */}
      <motion.div 
        initial={{ y: -10, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="sticky top-4 z-40 flex items-center justify-between mb-6 p-4 rounded-2xl bg-slate-900 border-2 border-white/20 shadow-2xl"
      >
        <div className="flex items-center gap-3">
           <button onClick={() => navigate('/visit-reports')} className="p-2.5 hover:bg-white/10 rounded-xl transition-colors text-white">
             <ArrowLeftIcon className="w-5 h-5"/>
           </button>
           <div>
             <h1 className="text-lg font-black text-white flex items-center gap-2 uppercase tracking-tight">
               {isEditing ? `Reporte ${form.report_number}` : 'Nueva Visita Técnica'}
               {form.sap_call_id && <span className="px-1.5 py-0.5 bg-cyan-500/10 border border-cyan-500/20 rounded text-[9px] text-cyan-400 font-black">SAP: {form.sap_call_id}</span>}
             </h1>
             <p className="text-[10px] text-cyan-400 font-bold uppercase tracking-[0.3em]">Polifusión Sertec System</p>
           </div>
        </div>
        <div className="flex gap-2">
            <button 
              onClick={() => {
                setSaveAction('preview');
                mutation.mutate(form);
              }} 
              disabled={mutation.isPending} 
              className="px-6 py-2.5 bg-slate-800 hover:bg-slate-700 rounded-xl text-white text-[10px] font-black uppercase tracking-wider flex items-center gap-2 border border-white/10 transition-all"
            >
              <FolderArrowDownIcon className="w-3 h-3"/>
              Guardar Borrador
            </button>

        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* COLUMNA IZQUIERDA: DATOS Y MÉTRICAS (8 cols) */}
        <div className="lg:col-span-8 space-y-6">
          
          {/* SECCIÓN 1: CLIENTE Y OBRA */}
          <div className="p-6 rounded-2xl bg-slate-900/95 border border-white/10 shadow-xl">
            <h2 className="text-[11px] font-black text-cyan-400 uppercase tracking-[0.25em] mb-6 flex items-center gap-2">
              <BuildingOffice2Icon className="w-4 h-4"/> DATOS DEL CLIENTE Y PROYECTO
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <GlassField label="Buscar Cliente (RUT o Nombre)" className="md:col-span-2">
                <div className="relative group">
                  <input 
                    className={`${inputClass} !py-2.5 !pl-10 ${isEditing && form.client_rut ? 'opacity-50 cursor-not-allowed' : ''}`} 
                    placeholder="Mínimo 3 caracteres..." 
                    value={customerSearch} 
                    onChange={e => handleSearchChange(e.target.value)}
                    readOnly={isEditing && !!form.client_rut}
                  />
                  <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500"/>
                  {isSearchingCustomers && <div className="absolute right-3 top-1/2 -translate-y-1/2"><SparklesIcon className="w-3 h-3 text-cyan-500 animate-spin"/></div>}
                  <AnimatePresence>
                    {customers.length > 0 && (
                      <motion.div initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="absolute left-0 right-0 mt-1 bg-slate-900 border border-white/10 rounded-xl z-50 max-h-60 overflow-y-auto shadow-2xl">
                        {customers.map(c => (
                          <button key={c.card_code} onClick={() => selectCustomer(c)} className="w-full p-3 text-left hover:bg-cyan-500/10 border-b border-white/5 last:border-0 group transition-all">
                            <p className="text-xs font-bold text-white group-hover:text-cyan-400">{c.card_name}</p>
                            <span className="text-[9px] text-slate-500 font-black tracking-widest uppercase">{c.card_code}</span>
                          </button>
                        ))}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </GlassField>

              {projects.length > 0 && (
                <GlassField label="Seleccionar Obra (Busque por nombre o ID)" className="md:col-span-2">
                  <div className="relative group">
                    <input 
                      className={`${inputClass} !py-2.5 !pl-10 ${isEditing && form.project_id ? 'opacity-50 cursor-not-allowed' : ''}`} 
                      placeholder="Escriba para filtrar obras..." 
                      value={projectSearch} 
                      onFocus={() => !isEditing && setShowProjectDropdown(true)}
                      onChange={e => setProjectSearch(e.target.value)}
                      readOnly={isEditing && !!form.project_id}
                    />
                    <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500"/>
                    <AnimatePresence>
                      {showProjectDropdown && (
                        <motion.div 
                          initial={{ opacity: 0, y: 5 }} 
                          animate={{ opacity: 1, y: 0 }} 
                          exit={{ opacity: 0 }} 
                          className="absolute left-0 right-0 mt-1 bg-slate-900 border border-white/10 rounded-xl z-50 max-h-60 overflow-y-auto shadow-2xl"
                        >
                          {projects
                            .filter(p => 
                              p.obra.toLowerCase().includes(projectSearch.toLowerCase()) || 
                              p.proyecto.toLowerCase().includes(projectSearch.toLowerCase()) ||
                              (p.direccion || '').toLowerCase().includes(projectSearch.toLowerCase())
                            )
                            .map(p => (
                              <button 
                                key={p.proyecto} 
                                onClick={() => {
                                  selectProject(p);
                                  setProjectSearch(p.obra);
                                  setShowProjectDropdown(false);
                                }} 
                                className="w-full p-3 text-left hover:bg-cyan-500/10 border-b border-white/5 last:border-0 group transition-all"
                              >
                                <div className="flex justify-between items-start">
                                  <p className="text-xs font-bold text-white group-hover:text-cyan-400">{p.obra}</p>
                                  <span className="text-[8px] bg-white/5 px-1.5 py-0.5 rounded text-slate-400 font-black">{p.proyecto}</span>
                                </div>
                                {p.direccion && <p className="text-[9px] text-slate-500 mt-0.5 italic">{p.direccion}</p>}
                              </button>
                            ))
                          }
                          {projects.filter(p => p.obra.toLowerCase().includes(projectSearch.toLowerCase())).length === 0 && (
                            <div className="p-4 text-center text-slate-500 text-[10px] font-bold uppercase tracking-widest">No se encontraron coincidencias</div>
                          )}
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                </GlassField>
              )}
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <GlassField label="RUT Cliente"><input className={`${inputClass} !bg-transparent`} value={form.client_rut} readOnly/></GlassField>
              <GlassField label="ID Obra"><input className={`${inputClass} !bg-transparent`} value={form.project_id} readOnly/></GlassField>
              <GlassField label="Comuna"><input className={inputClass} value={form.commune} onChange={e => updateField('commune', e.target.value)}/></GlassField>
              <GlassField label="Ciudad"><input className={inputClass} value={form.city} onChange={e => updateField('city', e.target.value)}/></GlassField>
              <GlassField label="Dirección Obra" className="md:col-span-2"><input className={inputClass} value={form.address} onChange={e => updateField('address', e.target.value)}/></GlassField>
              <GlassField label="Persona Contacto SAP"><input className={inputClass} value={form.client_contact} onChange={e => updateField('client_contact', e.target.value)} placeholder="Nombre del contacto"/></GlassField>
              <GlassField label="Teléfono SAP"><input className={inputClass} value={form.telephone} onChange={e => updateField('telephone', e.target.value)} placeholder="Número de contacto"/></GlassField>
              <GlassField label="Email Vendedor SAP (Envío)"><input className={inputClass} value={form.client_email} onChange={e => updateField('client_email', e.target.value)} placeholder="vendedor@sertec.cl (separe por ',' o ';' para incluir superiores)"/></GlassField>
              <GlassField label="Empresa Constructora" className="md:col-span-3"><input className={inputClass} value={form.construction_company} onChange={e => updateField('construction_company', e.target.value)}/></GlassField>
            </div>
          </div>

          {/* SECCIÓN 2: CONTROL DE MÁQUINAS (6 Slots) */}
          <div className="p-6 rounded-2xl bg-slate-900/95 border border-white/10 shadow-xl">
            <h2 className="text-[11px] font-black text-amber-400 uppercase tracking-[0.25em] mb-6 flex items-center gap-2">
              <WrenchScrewdriverIcon className="w-4 h-4"/> CONTROL DE MÁQUINAS (SAP UDF)
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div className="flex items-center gap-3 p-3 bg-white/5 rounded-xl border border-white/5">
                 <input type="checkbox" id="rem" className="w-4 h-4 rounded border-white/20 bg-slate-800 text-amber-500" checked={form.machine_data.machine_removal} onChange={e => updateField('machine_data', { ...form.machine_data, machine_removal: e.target.checked })}/>
                 <label htmlFor="rem" className="text-xs font-bold text-slate-300">Se retira máquina de obra</label>
              </div>
              <GlassField label="Nº Reporte Retiro">
                <input className={inputClass} value={form.machine_data.report_number || ''} onChange={e => updateField('machine_data', { ...form.machine_data, report_number: e.target.value })} placeholder="Ej: 450123"/>
              </GlassField>
            </div>

            <div className="overflow-hidden rounded-xl border border-white/10 bg-black/40">
              <table className="w-full text-xs">
                <thead className="bg-white/10 text-slate-200 font-black uppercase tracking-widest">
                  <tr>
                    <th className="px-3 py-3 text-center w-8 border-b border-white/10">#</th>
                    <th className="px-3 py-3 text-left border-b border-white/10">Máquina / Modelo</th>
                    <th className="px-3 py-3 text-center w-24 border-b border-white/10">Inicio</th>
                    <th className="px-3 py-3 text-center w-24 border-b border-white/10">Cortes</th>
                    <th className="px-3 py-3 text-center w-8 border-b border-white/10"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {form.machine_data.machines.map((m: any, idx: number) => (
                    <tr key={idx} className="group hover:bg-white/[0.02]">
                      <td className="px-3 py-1.5 text-center text-slate-400 font-black">{idx + 1}</td>
                      <td className="px-1 py-1"><input className="w-full bg-transparent border-none focus:ring-0 px-2 py-1 text-white placeholder-slate-700 font-bold" placeholder="Escriba el modelo..." value={m?.machine || m?.modelo || ''} onChange={e => updateMachine(idx, 'machine', e.target.value)}/></td>
                      <td className="px-1 py-1"><input type="number" className="w-full bg-transparent border-none focus:ring-0 px-2 py-1 text-center text-amber-400 font-mono font-black" value={m?.start || m?.inicio || ''} onChange={e => updateMachine(idx, 'start', e.target.value)}/></td>
                      <td className="px-1 py-1"><input type="number" className="w-full bg-transparent border-none focus:ring-0 px-2 py-1 text-center text-cyan-400 font-mono font-black" value={m?.cut || m?.cortes || ''} onChange={e => updateMachine(idx, 'cut', e.target.value)}/></td>
                      <td className="px-1 py-1 text-center">
                        <button onClick={() => removeMachineRow(idx)} className="p-1 hover:text-red-500 text-slate-600 transition-colors opacity-0 group-hover:opacity-100">✕</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <button 
              onClick={addMachineRow}
              className="mt-4 w-full py-3 bg-white/5 hover:bg-white/10 border border-white/10 border-dashed rounded-xl text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] transition-all flex items-center justify-center gap-2"
            >
              <PlusIcon className="w-3 h-3"/> Agregar otra máquina
            </button>
          </div>
        </div>

        {/* COLUMNA DERECHA: PERSONAL Y MÉTRICAS SAP (4 cols) */}
        <div className="lg:col-span-4 space-y-6">
          <div className="p-6 rounded-2xl bg-slate-900/95 border border-white/10 shadow-xl h-full">
            <h2 className="text-[11px] font-black text-emerald-400 uppercase tracking-[0.25em] mb-6 flex items-center gap-2">
              <UserGroupIcon className="w-4 h-4"/> PERSONAL Y MÉTRICAS SAP
            </h2>
            
            <div className="space-y-4">
              <GlassField label="Fecha Visita"><input type="datetime-local" className={inputClass} value={form.visit_date} onChange={e => updateField('visit_date', e.target.value)}/></GlassField>
              <GlassField label="Técnico SAP">
                <select className={inputClass} value={form.technician_id || ''} onChange={e => { const id = e.target.value; const name = technicians?.find((t: any) => t.id.toString() === id)?.name || ''; setForm((prev: any) => ({ ...prev, technician_id: id, technician: name })); }}>
                  <option value="" className="bg-slate-900">Seleccione Técnico...</option>
                  {technicians?.map((t: any) => <option key={t.id} value={t.id} className="bg-slate-900">{t.name}</option>)}
                </select>
              </GlassField>
              <GlassField label="Vendedor"><input className={inputClass} value={form.salesperson} readOnly/></GlassField>
              <GlassField label="Ciudad"><input className={inputClass} value={form.city} onChange={e => updateField('city', e.target.value)} placeholder="Ej: Santiago"/></GlassField>
              
              <div className="pt-4 border-t border-white/5 space-y-4">
                <div className="flex items-center justify-between p-3 bg-white/5 rounded-xl border border-white/5">
                  <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Obra con otro proveedor</span>
                  <input type="checkbox" className="w-4 h-4 rounded border-white/20 bg-slate-800 text-cyan-500" checked={form.is_other_provider} onChange={e => updateField('is_other_provider', e.target.checked)}/>
                </div>
                {form.is_other_provider && (
                  <GlassField label="Nombre del otro proveedor">
                    <input className={inputClass} value={form.other_provider_name} onChange={e => updateField('other_provider_name', e.target.value)} placeholder="Ej: Proveedor X"/>
                  </GlassField>
                )}

                <div className="flex items-center justify-between p-3 bg-white/5 rounded-xl border border-white/5">
                  <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Obra Terminada</span>
                  <input type="checkbox" className="w-4 h-4 rounded border-white/20 bg-slate-800 text-emerald-500" checked={form.is_project_finished} onChange={e => updateField('is_project_finished', e.target.checked)}/>
                </div>

                <div className="space-y-2">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1">
                    <SparklesIcon className="w-3 h-3 text-indigo-500" />
                    Nivel de Instalación
                  </label>
                  <select
                    value={form.installation_level}
                    onChange={(e) => setForm({ ...form, installation_level: e.target.value })}
                    className={inputClass}
                  >
                    <option value="0" className="bg-slate-900">Normal</option>
                    <option value="1" className="bg-slate-900">Deficiente</option>
                    <option value="2" className="bg-slate-900">Crítico</option>
                    <option value="3" className="bg-slate-900">Inexistente</option>
                    <option value="4" className="bg-slate-900">No Aplica</option>
                  </select>
                </div>

                <div className="flex items-center justify-between p-3 bg-white/5 rounded-xl border border-white/5">
                  <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Material Mixto</span>
                  <input type="checkbox" className="w-4 h-4 rounded border-white/20 bg-slate-800 text-amber-500" checked={form.is_mixed_material} onChange={e => updateField('is_mixed_material', e.target.checked)}/>
                </div>

                <div className="space-y-2">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Obra Nueva / Rescatada</label>
                  <select
                    className={inputClass}
                    value={form.is_rescued_project ? 'RESCATADA' : 'NUEVA'}
                    onChange={e => updateField('is_rescued_project', e.target.value === 'RESCATADA')}
                  >
                    <option value="NUEVA" className="bg-slate-900">Nueva</option>
                    <option value="RESCATADA" className="bg-slate-900">Rescatada</option>
                  </select>
                </div>
              </div>

              <div className="pt-4 border-t border-white/5 space-y-4">
                <GlassField label="Nombre Instalador / Prof. Obra"><input className={inputClass} value={form.installer} onChange={e => updateField('installer', e.target.value)}/></GlassField>
                <GlassField label="Telf. Inst. (Contacto Proyecto)"><input className={inputClass} value={form.installer_phone} onChange={e => updateField('installer_phone', e.target.value)}/></GlassField>
              </div>
            </div>
          </div>
        </div>

        {/* SECCIÓN 3: OBSERVACIONES TÉCNICAS (12 cols) */}
        <div className="lg:col-span-12">
          <div className="p-6 rounded-2xl bg-slate-900/95 border border-white/10 shadow-xl">
            <h2 className="text-[11px] font-black text-indigo-400 uppercase tracking-[0.25em] mb-6 flex items-center gap-2">
              <ClipboardDocumentListIcon className="w-4 h-4"/> OBSERVACIONES TÉCNICAS POR ÁREA
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[
                { label: 'Muros / Tabiques', key: 'wall_observations' },
                { label: 'Matriz', key: 'matrix_observations' },
                { label: 'Losa', key: 'slab_observations' },
                { label: 'Almacenaje', key: 'storage_observations' },
                { label: 'Pre-Armados', key: 'pre_assembled_observations' },
                { label: 'Exteriores', key: 'exterior_observations' },
              ].map(s => (
                <GlassField key={s.key} label={s.label}>
                  <textarea className={`${textareaClass} !min-h-[80px] !py-2`} value={form[s.key]} onChange={e => updateField(s.key, e.target.value)}/>
                </GlassField>
              ))}
              <GlassField label="Observaciones Generales" className="md:col-span-3">
                <textarea className={`${textareaClass} !min-h-[100px] !bg-cyan-500/5 !border-cyan-500/20`} value={form.general_observations} onChange={e => updateField('general_observations', e.target.value)}/>
              </GlassField>
              <div className="md:col-span-3">
                <div className="p-4 rounded-2xl bg-red-950/30 border border-red-500/20">
                  <label className="text-[10px] font-black text-red-400 uppercase tracking-widest flex items-center gap-2 mb-2">
                    <span>🔒</span> Observación Crítica — Solo Interno (SAP)
                  </label>
                  <textarea
                    className={`${textareaClass} !min-h-[80px] !bg-red-500/5 !border-red-500/20 !text-red-300`}
                    placeholder="Información crítica interna. NO aparece en el PDF del cliente..."
                    value={form.critical_observations}
                    onChange={e => updateField('critical_observations', e.target.value)}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* SECCIÓN 4: FOTOS DE EVIDENCIA (12 cols) */}
        <div className="lg:col-span-12">
          <div className="p-6 rounded-2xl bg-slate-900/95 border border-white/10 shadow-xl relative group">
            <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent pointer-events-none" />
            
            <div className="relative z-10">
              <h2 className="text-[11px] font-black text-emerald-400 uppercase tracking-[0.25em] mb-6 flex items-center gap-2">
                <CameraIcon className="w-4 h-4"/> REGISTRO FOTOGRÁFICO Y EVIDENCIAS
              </h2>
              
              {!showLocalCamera && !isEditing && existingAttachments.length === 0 ? (
                <div className="p-12 text-center border-2 border-dashed border-white/10 rounded-2xl bg-white/5 flex flex-col items-center gap-4">
                  <div className="p-4 bg-emerald-500/10 rounded-full">
                    <CameraIcon className="w-10 h-10 text-emerald-500/50" />
                  </div>
                  <p className="text-slate-400 text-[10px] font-bold">Las fotos se guardarán localmente hasta que guarde el reporte.</p>
                  <button 
                    onClick={() => setShowLocalCamera(true)}
                    className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-[10px] font-black uppercase tracking-widest transition-all"
                  >
                    HABILITAR CÁMARA
                  </button>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Controles y Carga superior */}
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-black text-emerald-400 uppercase tracking-widest">
                      Gestión de Fotos y Evidencias
                    </span>
                    
                    {/* Hidden Inputs */}
                    <input 
                      type="file" 
                      accept="image/*" 
                      multiple
                      ref={fileInputRef}
                      className="hidden" 
                      onChange={async (e) => {
                        if (e.target.files?.length) {
                          const files = Array.from(e.target.files);
                          toast.loading(`Optimizando ${files.length} imágenes...`, { id: 'compressing' });
                          for (const file of files) {
                            try {
                              const compressed = await compressImage(file);
                              setPendingPhotos(prev => [...prev, { file: compressed, description: '' }]);
                            } catch (err) { console.error("Error optimizando imagen:", err); }
                          }
                          toast.success('Imágenes optimizadas', { id: 'compressing' });
                          e.target.value = '';
                        }
                      }}
                    />
                    <input 
                      type="file" 
                      accept="image/*" 
                      capture="environment"
                      ref={cameraInputRef}
                      className="hidden" 
                      onChange={async (e) => {
                        if (e.target.files?.length) {
                          const file = e.target.files[0];
                          toast.loading(`Procesando foto...`, { id: 'compressing' });
                          try {
                            const compressed = await compressImage(file);
                            setPendingPhotos(prev => [...prev, { file: compressed, description: '' }]);
                            toast.success('Foto capturada', { id: 'compressing' });
                          } catch (err) { toast.error('Error al procesar foto', { id: 'compressing' }); }
                          e.target.value = '';
                        }
                      }}
                    />

                    <div className="relative">
                      <button 
                        onClick={() => setShowPhotoOptions(!showPhotoOptions)}
                        className="px-6 py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-[10px] font-black shadow-lg shadow-emerald-900/20 active:scale-95 transition-all flex items-center gap-2"
                      >
                        <CameraIcon className="w-4 h-4"/>
                        AÑADIR EVIDENCIA
                      </button>

                      <AnimatePresence>
                        {showPhotoOptions && (
                          <motion.div 
                            initial={{ opacity: 0, scale: 0.95, y: -5 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95, y: -5 }}
                            className="absolute right-0 top-full mt-2 w-44 bg-slate-900/95 backdrop-blur-xl border border-white/20 rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] overflow-hidden z-[110]"
                          >
                            <button 
                              onClick={() => { cameraInputRef.current?.click(); setShowPhotoOptions(false); }}
                              className="w-full p-4 flex items-center gap-3 hover:bg-emerald-500/10 text-white transition-colors border-b border-white/5"
                            >
                              <div className="p-2 bg-emerald-500/10 rounded-lg">
                                <CameraIcon className="w-4 h-4 text-emerald-400"/>
                              </div>
                              <span className="text-[10px] font-bold uppercase tracking-wider">Usar Cámara</span>
                            </button>
                            <button 
                              onClick={() => { fileInputRef.current?.click(); setShowPhotoOptions(false); }}
                              className="w-full p-4 flex items-center gap-3 hover:bg-cyan-500/10 text-white transition-colors"
                            >
                              <div className="p-2 bg-cyan-500/10 rounded-lg">
                                <PhotoIcon className="w-4 h-4 text-cyan-400"/>
                              </div>
                              <span className="text-[10px] font-bold uppercase tracking-wider">De Galería</span>
                            </button>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  </div>

                  {/* 1. SECCIÓN DE IMÁGENES GUARDADAS PREVIAMENTE */}
                  {isEditing && existingAttachments.length > 0 && (
                    <div className="space-y-3 pt-2">
                      <span className="text-[10px] font-black text-emerald-400 uppercase tracking-widest block">
                        Fotos Cargadas en Servidor ({existingAttachments.length})
                      </span>
                      
                      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
                        {existingAttachments.map((att: any) => {
                          const isImg = isImageFile(att.filename);
                          return (
                            <div key={att.id} className="relative aspect-square rounded-2xl overflow-hidden border border-white/10 bg-slate-950 flex flex-col group/item shadow-lg hover:border-emerald-500/30 transition-all duration-300">
                              <div className="flex-1 relative overflow-hidden bg-slate-900 flex items-center justify-center">
                                {isImg ? (
                                  <SecureReportImage 
                                    reportId={id!} 
                                    attachmentId={att.id} 
                                    alt={att.description || att.filename}
                                    className="w-full h-full object-cover transition-transform duration-500 group-hover/item:scale-105"
                                  />
                                ) : (
                                  <div className="flex flex-col items-center gap-2 text-slate-400 p-4 text-center">
                                    <DocumentTextIcon className="w-10 h-10 text-slate-600 animate-pulse" />
                                    <span className="text-[9px] font-medium truncate max-w-full">{att.filename}</span>
                                  </div>
                                )}
                                
                                {/* Overlay de hover interactivo */}
                                <div className="absolute inset-0 bg-slate-950/60 opacity-0 group-hover/item:opacity-100 transition-opacity duration-300 flex items-center justify-center gap-2 backdrop-blur-[2px]">
                                  <button
                                    type="button"
                                    onClick={async () => {
                                      try {
                                        toast.loading("Cargando vista previa...", { id: 'viewing-file' });
                                        const response = await api.get(`/documents/report-attachments/${id}/visit/${att.id}/view/`, {
                                          responseType: 'blob'
                                        });
                                        const blob = new Blob([response.data], { type: response.headers['content-type'] });
                                        const url = window.URL.createObjectURL(blob);
                                        window.open(url, '_blank');
                                        toast.success("Vista previa abierta", { id: 'viewing-file' });
                                      } catch (err) {
                                        console.error("Error viewing image:", err);
                                        toast.error("Error al abrir la imagen", { id: 'viewing-file' });
                                      }
                                    }}
                                    className="p-2 bg-slate-850 hover:bg-slate-700 text-emerald-400 rounded-xl transition-all hover:scale-110"
                                    title="Ver a pantalla completa"
                                  >
                                    <EyeIcon className="w-4 h-4" />
                                  </button>
                                  <button
                                    type="button"
                                    onClick={async () => {
                                      try {
                                        toast.loading("Descargando...", { id: 'downloading-file' });
                                        const response = await api.get(`/documents/report-attachments/${id}/visit/${att.id}/download/`, {
                                          responseType: 'blob'
                                        });
                                        const blob = new Blob([response.data]);
                                        const url = window.URL.createObjectURL(blob);
                                        const link = document.createElement('a');
                                        link.href = url;
                                        link.download = att.filename;
                                        document.body.appendChild(link);
                                        link.click();
                                        document.body.removeChild(link);
                                        window.URL.revokeObjectURL(url);
                                        toast.success("Archivo descargado", { id: 'downloading-file' });
                                      } catch (err) {
                                        console.error("Error downloading file:", err);
                                        toast.error("Error al descargar el archivo", { id: 'downloading-file' });
                                      }
                                    }}
                                    className="p-2 bg-slate-850 hover:bg-slate-700 text-cyan-400 rounded-xl transition-all hover:scale-110"
                                    title="Descargar archivo"
                                  >
                                    <CloudArrowDownIcon className="w-4 h-4" />
                                  </button>
                                  <button
                                    type="button"
                                    onClick={() => {
                                      if (confirm("¿Está seguro de eliminar esta evidencia permanentemente?")) {
                                        deleteAttachmentMutation.mutate(att.id);
                                      }
                                    }}
                                    className="p-2 bg-red-500/20 hover:bg-red-500 text-red-400 hover:text-white rounded-xl transition-all hover:scale-110"
                                    title="Eliminar evidencia"
                                  >
                                    <TrashIcon className="w-4 h-4" />
                                  </button>
                                </div>
                              </div>
                              
                              {/* Footer de Descripción */}
                              <div className="bg-slate-900/90 border-t border-white/5 p-2 min-h-[36px] flex flex-col justify-center">
                                <p className="text-[9px] text-slate-300 font-medium line-clamp-2 leading-tight">
                                  {att.description || "Evidencia de visita"}
                                </p>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}

                  {/* 2. SECCIÓN DE FOTOS NUEVAS EN MEMORIA (PENDIENTES DE GUARDAR) */}
                  <div className="space-y-3 pt-2">
                    <span className="text-[10px] font-black text-emerald-400 uppercase tracking-widest block">
                      Fotos Nuevas a Guardar ({pendingPhotos.length})
                    </span>
                    
                    {pendingPhotos.length === 0 ? (
                      <p className="text-slate-500 text-[10px] font-medium italic">No hay fotos nuevas añadidas aún.</p>
                    ) : (
                      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
                        {pendingPhotos.map((photo, idx) => (
                          <div key={idx} className="relative aspect-square rounded-2xl overflow-hidden border border-white/10 bg-slate-950 flex flex-col shadow-lg">
                            <div className="flex-1 relative overflow-hidden bg-slate-900">
                              <img 
                                src={URL.createObjectURL(photo.file)} 
                                className="w-full h-full object-cover" 
                                alt="preview"
                              />
                              <button 
                                type="button"
                                onClick={() => setPendingPhotos(prev => prev.filter((_, i) => i !== idx))}
                                className="absolute top-2 right-2 p-1.5 bg-red-500/80 hover:bg-red-500 text-white rounded-full transition-colors active:scale-95 shadow-md"
                              >
                                <XMarkIcon className="w-3 h-3"/>
                              </button>
                            </div>
                            <input 
                              type="text" 
                              placeholder="Descripción..." 
                              value={photo.description}
                              onChange={(e) => {
                                const newPhotos = [...pendingPhotos];
                                newPhotos[idx].description = e.target.value;
                                setPendingPhotos(newPhotos);
                              }}
                              className="w-full text-[10px] bg-slate-900 text-white placeholder-slate-500 p-2 outline-none border-t border-white/5 font-semibold text-center"
                            />
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

      </div>

      {/* Modal de Procesamiento / Generando PDF */}
      {(mutation.isLoading || isGeneratingPDF) && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-[100] flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl p-8 max-w-sm w-full shadow-2xl border border-white/20 flex flex-col items-center text-center">
            <div className="relative w-20 h-20 mb-6">
              <div className="absolute inset-0 border-4 border-indigo-100 rounded-full"></div>
              <div className="absolute inset-0 border-4 border-indigo-600 rounded-full border-t-transparent animate-spin"></div>
              <div className="absolute inset-0 flex items-center justify-center">
                <DocumentTextIcon className="w-8 h-8 text-indigo-600" />
              </div>
            </div>
            <h3 className="text-xl font-black text-slate-800 mb-2 uppercase tracking-tight">Procesando Reporte</h3>
            <p className="text-slate-500 text-sm leading-relaxed">
              Estamos generando el documento profesional y sincronizando con SAP. Por favor, no cierres esta ventana.
            </p>
          </div>
        </div>
      )}

      {/* Modal de Previsualización PDF FULL SCREEN */}
      {showPDFPreviewModal && previewURL && (
        <div className="fixed inset-0 z-[200] flex flex-col bg-slate-950 animate-in fade-in zoom-in duration-300">
          <div className="flex items-center justify-between p-4 bg-slate-900 border-b border-white/10 shadow-2xl">
            <div className="flex items-center gap-4">
              <div className="bg-blue-600 p-2 rounded-lg">
                <DocumentTextIcon className="w-5 h-5 text-white"/>
              </div>
              <div>
                <h3 className="text-white font-black uppercase tracking-widest text-sm">Previsualización del Reporte</h3>
                <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Revisión antes de firmar</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button 
                onClick={() => setShowPDFPreviewModal(false)}
                className="px-6 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all"
              >
                Volver a editar
              </button>
              <button 
                onClick={() => {
                  setShowPDFPreviewModal(false);
                  navigate('/visit-reports');
                }}
                className="px-8 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-500 text-white rounded-xl text-[10px] font-black uppercase tracking-widest shadow-lg shadow-emerald-900/20 hover:scale-105 transition-all flex items-center gap-2"
              >
                <CheckCircleIcon className="w-4 h-4"/>
                Ir al Listado para Firmar
              </button>
            </div>
          </div>
          <div className="flex-1 bg-slate-800 relative">
            <iframe src={previewURL} className="w-full h-full border-none" title="PDF Preview"/>
          </div>
        </div>
      )}

      {/* Modal de Firma Directa (Cliente) */}
      {showSignatureModal && (createdReportId || id) && (
        <SignatureCanvas
          onClose={() => setShowSignatureModal(false)}
          onSave={async (signatureDataUrl) => {
            toast.loading('Guardando firma del cliente...', { id: 'signing' });
            try {
              const targetId = createdReportId || Number(id);
              // 1. Guardar firma del cliente y marcar como final
              await visitReportsAPI.update(targetId, {
                client_signature: signatureDataUrl,
                is_final: true
              });
              // 2. Generar PDF final y disparar SAP Sync
              await visitReportsAPI.generatePDF(targetId, { final: true });
              
              toast.success('Reporte firmado y finalizado con éxito', { id: 'signing' });
              setShowSignatureModal(false);
              navigate('/visit-reports');
            } catch (err: any) {
              console.error("Error al guardar firma de cliente:", err);
              toast.error('Error al guardar firma: ' + (err.response?.data?.error || err.message), { id: 'signing' });
            }
          }}
          title="Firma de Recepción (Cliente)"
          signerName={form.client_name || 'Representante de Obra'}
        />
      )}
    </div>
  );
};

// =============================================================================
// HELPERS
// =============================================================================
const compressImage = (file: File): Promise<File> => {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = (event) => {
      const img = new Image();
      img.src = event.target?.result as string;
      img.onload = () => {
        const canvas = document.createElement('canvas');
        const MAX_WIDTH = 1200;
        const scale = Math.min(1, MAX_WIDTH / img.width);
        canvas.width = img.width * scale;
        canvas.height = img.height * scale;
        const ctx = canvas.getContext('2d');
        ctx?.drawImage(img, 0, 0, canvas.width, canvas.height);
        canvas.toBlob((blob) => {
          resolve(new File([blob!], file.name, { type: 'image/jpeg', lastModified: Date.now() }));
        }, 'image/jpeg', 0.7);
      };
    };
  });
};

export default VisitReportForm;
