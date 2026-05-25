import React, { useState, useMemo, useEffect } from 'react';
import ReactDOM from 'react-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { visitReportsAPI, sapAPI } from '../services/api';
import { useAuth } from '../hooks/useAuth';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import {
  PlusIcon,
  EyeIcon,
  TrashIcon,
  XMarkIcon,
  MagnifyingGlassIcon,
  ClipboardDocumentListIcon,
  ArrowPathIcon,
  FolderOpenIcon,
  CalendarIcon,
  BuildingOfficeIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  PencilSquareIcon,
  BoltIcon,
  CheckCircleIcon,
  DocumentTextIcon,
  SparklesIcon,
  DocumentArrowDownIcon,
  EnvelopeIcon,
} from '@heroicons/react/24/outline';
import { PDFViewer } from '../components/PDFViewer';
import SignatureCanvas from '../components/SignatureCanvas';
import { Modal, ModalHeader, ModalBody, ModalFooter, ModalTitle, ModalCloseButton } from '../components/ui/Modal';

const STATUS_BADGES: Record<string, { label: string; cls: string }> = {
  draft: { label: 'Abierto', cls: 'bg-emerald-100 text-emerald-700 border border-emerald-200' },
  pending_review: { label: 'Falta firma', cls: 'bg-amber-100 text-amber-700 border border-amber-200' },
  approved: { label: 'Falta enviar', cls: 'bg-blue-100 text-blue-700 border border-blue-200' },
  sent: { label: 'Cerrada', cls: 'bg-slate-100 text-slate-700 border border-slate-200' },
  waiting_response: { label: 'Esperando', cls: 'bg-orange-100 text-orange-700 border border-orange-200' },
  closed: { label: 'Cerrada', cls: 'bg-slate-100 text-slate-700 border border-slate-200' },
};

const hasDraftContent = (report: any) => {
  return !!(
    report.installer ||
    report.incident_description ||
    report.general_observations ||
    report.wall_observations ||
    report.matrix_observations ||
    report.slab_observations ||
    report.storage_observations ||
    report.pre_assembled_observations ||
    report.exterior_observations ||
    (report.machine_data?.machines && report.machine_data.machines.some((m: any) => m.machine || m.start || m.cut)) ||
    (report.materials_data && report.materials_data.length > 0)
  );
};

const VisitReportsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(20);

  const { user, getUserDisplayName } = useAuth();
  const userDisplayName = getUserDisplayName();

  const isTechnician = useMemo(() => {
    if (!user) return false;
    const roleLower = user.role?.toLowerCase() || '';
    return roleLower === 'technical_service' || roleLower === 'tecnico' || roleLower === 'technician';
  }, [user]);
  
  const isJefe = useMemo(() => {
    if (!user) return false;
    const roleLower = user.role?.toLowerCase() || '';
    const usernameLower = user.username?.toLowerCase() || '';
    const nameLower = userDisplayName?.toLowerCase() || '';
    
    // Roles administrativos / gerencia / supervisión / calidad de Sertec que gestionan reportes
    const isSertecStaff = [
      'admin', 'administrador', 'jefe', 'supervisor', 'quality', 'calidad', 
      'analyst', 'analista', 'management', 'gerencia', 'customer_service'
    ].some(role => roleLower.includes(role));
    
    return isSertecStaff || usernameLower.includes('patricio') || nameLower.includes('patricio');
  }, [user, userDisplayName]);

  // Initially always pre-loads with their own name (via 'me')
  const [technicianFilter, setTechnicianFilter] = useState<string>('me');

  // Load technicians for Jefe dropdown selection
  const { data: sapTechs } = useQuery({
    queryKey: ['sap-technicians-list'],
    queryFn: () => sapAPI.getTechnicians('technician').then(res => res.data),
    enabled: isJefe,
  });
  
  // Manual Debounce to avoid useDebounce hook issues
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchTerm);
      setCurrentPage(1);
    }, 100);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  const [showPDFPreviewModal, setShowPDFPreviewModal] = useState(false);
  const [showSignatureModal, setShowSignatureModal] = useState(false);
  const [selectedReport, setSelectedReport] = useState<any>(null);
  const [previewURL, setPreviewURL] = useState<string | null>(null);
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false);
  
  // Email Modal State
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [emailToSend, setEmailToSend] = useState('');
  const [reportForEmail, setReportForEmail] = useState<any>(null);
  const [isFetchingEmail, setIsFetchingEmail] = useState(false);

  // Fetch visit reports from new /api/visits/ endpoint
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['visit-reports', currentPage, pageSize, debouncedSearch],
    queryFn: () => visitReportsAPI.list({ page: currentPage, page_size: pageSize, search: debouncedSearch }).then(res => res.data),
    staleTime: 30_000,        // 30s — don't refetch on every focus
    refetchOnWindowFocus: false,
  });


  const reports = useMemo(() => {
    if (!data) return [];
    let fetchedReports = data.results || (Array.isArray(data) ? data : []);
    
    // Sort logic
    fetchedReports = fetchedReports.sort((a: any, b: any) => {
      const isDraftA = a.status === 'draft';
      const isDraftB = b.status === 'draft';
      
      if (isDraftA && !isDraftB) return -1;
      if (!isDraftA && isDraftB) return 1;
      
      // If both are drafts, sort by visit_date ascending (closest first)
      if (isDraftA && isDraftB) {
        const dateA = a.visit_date ? new Date(a.visit_date).getTime() : 0;
        const dateB = b.visit_date ? new Date(b.visit_date).getTime() : 0;
        return dateA - dateB;
      }
      
      // Otherwise sort by visit_date descending (newest first)
      const dateA = a.visit_date ? new Date(a.visit_date).getTime() : 0;
      const dateB = b.visit_date ? new Date(b.visit_date).getTime() : 0;
      return dateB - dateA;
    });

    // Apply technician permissions and slicing filters
    const matchName = (reportTech: string, userDispName: string) => {
      if (!reportTech || !userDispName) return false;
      const techLower = reportTech.toLowerCase();
      const userLower = userDispName.toLowerCase();
      return techLower.includes(userLower) || userLower.includes(techLower);
    };

    if (isJefe) {
      if (technicianFilter === 'all') return fetchedReports;
      if (technicianFilter === 'me') {
        return fetchedReports.filter((r: any) => matchName(r.technician, userDisplayName));
      }
      return fetchedReports.filter((r: any) => matchName(r.technician, technicianFilter));
    } else {
      // Normal technician (like Marco Montenegro): ONLY see their own reports
      return fetchedReports.filter((r: any) => matchName(r.technician, userDisplayName));
    }
  }, [data, isJefe, technicianFilter, userDisplayName]);

  const totalCount = data?.count || reports.length;
  const totalPages = Math.ceil(totalCount / pageSize);

  // AUTO-SIGN LOGIC: Detect ?sign=ID in URL and open signature modal
  useEffect(() => {
    const signId = searchParams.get('sign');
    if (signId && reports.length > 0) {
      const reportToSign = reports.find((r: any) => r.id.toString() === signId);
      if (reportToSign) {
        setSelectedReport(reportToSign);
        setShowSignatureModal(true);
        // Clean URL after opening
        const newParams = new URLSearchParams(searchParams);
        newParams.delete('sign');
        setSearchParams(newParams, { replace: true });
      }
    }
  }, [searchParams, reports, setSearchParams]);

  const deleteMutation = useMutation({
    mutationFn: (id: number) => visitReportsAPI.delete(id),
    onSuccess: () => {
      toast.success('Reporte eliminado');
      queryClient.invalidateQueries({ queryKey: ['visit-reports'] });
    },
    onError: () => toast.error('Error al eliminar'),
  });

  const handleDelete = (id: number) => {
    if (window.confirm('¿Eliminar este reporte de visita?')) {
      deleteMutation.mutate(id);
    }
  };

  const syncMutation = useMutation({
    mutationFn: (id: number) => visitReportsAPI.generatePDF(id, { final: true }),
    onSuccess: () => {
      toast.success('Sincronización con SAP iniciada');
      queryClient.invalidateQueries({ queryKey: ['visit-reports'] });
    },
    onError: (err: any) => {
      const msg = err.response?.data?.error || "Error al sincronizar con SAP";
      toast.error(msg);
    },
  });

  const handleSync = (id: number) => {
    if (window.confirm('¿Sincronizar este reporte con SAP ahora?')) {
      syncMutation.mutate(id);
    }
  };

  const getStatusBadge = (status: string) => {
    const cfg = STATUS_BADGES[status] || STATUS_BADGES.draft;
    return <span className={`px-2.5 py-1 text-[10px] font-black uppercase tracking-wider rounded-full ${cfg.cls}`}>{cfg.label}</span>;
  };

  const handlePreviewPDF = async (reportId: number) => {
    setIsGeneratingPDF(true);
    try {
      const res = await visitReportsAPI.generatePDF(reportId, { final: false });
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

  const handleOpenEmailModal = async (report: any) => {
    setReportForEmail(report);
    setShowEmailModal(true);
    
    if (report.client_email) {
      setEmailToSend(report.client_email);
    } else if (report.client_rut) {
      setIsFetchingEmail(true);
      setEmailToSend('Cargando correo desde SAP...');
      try {
        const detailRes = await sapAPI.getCustomerDetails(report.client_rut);
        if (detailRes.data && detailRes.data.salesperson_email) {
          setEmailToSend(detailRes.data.salesperson_email);
        } else {
          setEmailToSend('');
        }
      } catch (err) {
        console.error("Error cargando correo del vendedor desde SAP:", err);
        setEmailToSend('');
      } finally {
        setIsFetchingEmail(false);
      }
    } else {
      setEmailToSend('');
    }
  };

  const handleSendEmail = async () => {
    if (!reportForEmail || !emailToSend) {
      toast.error("Debe ingresar un correo válido");
      return;
    }

    const loadingToast = toast.loading('Enviando reporte por correo...');
    try {
      await visitReportsAPI.sendEmail(reportForEmail.id, [emailToSend]);
      toast.success('Reporte enviado correctamente', { id: loadingToast });
      setShowEmailModal(false);
      setReportForEmail(null);
    } catch (err: any) {
      toast.error(err?.response?.data?.error || 'Error al enviar correo', { id: loadingToast });
    }
  };


  return (
    <div className="space-y-4 px-2 pb-6">

      {/* HEADER — compact */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 bg-white/80 backdrop-blur-xl p-4 rounded-2xl border border-white/60 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="bg-blue-600 p-2.5 rounded-xl shadow-lg shadow-blue-200">
            <ClipboardDocumentListIcon className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-black text-slate-900 tracking-tight leading-none flex items-center gap-2">
              Reportes de <span className="text-blue-600">Visita</span>
              <BoltIcon className="w-4 h-4 text-cyan-500" />
            </h1>
            <p className="text-[9px] font-bold text-slate-400 uppercase tracking-[0.2em] mt-0.5">
              Historial · Sincronizado SAP
            </p>
          </div>
        </div>

        <div className="flex flex-row gap-2 w-full sm:w-auto items-center">
          {isJefe && (
            <div className="flex items-center gap-1.5 bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 shadow-sm flex-1 sm:flex-none">
              <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest whitespace-nowrap">Tec:</span>
              <select
                value={technicianFilter}
                onChange={(e) => setTechnicianFilter(e.target.value)}
                className="bg-transparent border-none p-0 text-xs font-black text-blue-600 focus:ring-0 cursor-pointer outline-none"
              >
                <option value="me">{userDisplayName}</option>
                <option value="all">— Todos —</option>
                {sapTechs?.map((t: any) => (
                  <option key={t.id} value={t.name}>{t.name}</option>
                ))}
              </select>
            </div>
          )}
          <button
            onClick={() => refetch()}
            className="w-10 h-10 flex items-center justify-center text-slate-400 hover:text-blue-600 bg-white border border-slate-100 rounded-xl shadow-sm transition-all flex-shrink-0"
            title="Refrescar"
          >
            <ArrowPathIcon className="w-4 h-4" />
          </button>
          {!isTechnician && (
            <button
              onClick={() => navigate('/visit-report-form')}
              className="flex-1 sm:flex-none px-5 py-2.5 bg-gradient-to-r from-blue-600 to-cyan-500 text-white rounded-xl text-xs font-black uppercase tracking-widest shadow-xl shadow-blue-200 hover:shadow-blue-300 transition-all flex items-center justify-center gap-2 hover:scale-[1.02] whitespace-nowrap"
            >
              <PlusIcon className="h-4 w-4" />
              Nuevo
            </button>
          )}
        </div>
      </div>

      {/* SEARCH */}
      <div className="bg-white/70 backdrop-blur-xl rounded-xl shadow-sm p-3 border border-white/60">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Buscar por número, cliente, proyecto..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            className="block w-full pl-10 pr-10 py-2.5 bg-slate-50 border border-transparent rounded-lg text-sm font-bold text-slate-700 placeholder-slate-400 focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all outline-none"
          />
          {searchTerm && (
            <button onClick={() => setSearchTerm('')} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-300 hover:text-rose-500">
              <XMarkIcon className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>

      {/* TABLE */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xl overflow-hidden">
        <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <h2 className="text-xs font-black text-slate-700 uppercase tracking-widest">Reportes</h2>
          <span className="bg-blue-500/10 text-blue-600 px-3 py-1 rounded-full text-[10px] font-black uppercase">{totalCount} registros</span>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-24">
            <div className="relative w-16 h-16">
              <div className="absolute inset-0 border-4 border-blue-500/10 rounded-full"></div>
              <div className="absolute inset-0 border-4 border-blue-600 rounded-full border-t-transparent animate-spin"></div>
            </div>
          </div>
        ) : reports.length > 0 ? (
          <div className="flex flex-col">
            {/* Table Header (Desktop only) */}
            <div className="hidden md:grid grid-cols-12 gap-4 px-8 py-4 bg-slate-50/80 border-b border-slate-100">
              <div className="col-span-3 text-[10px] font-black text-slate-400 uppercase tracking-widest">Identificación</div>
              <div className="col-span-5 text-[10px] font-black text-slate-400 uppercase tracking-widest">Cliente y Proyecto</div>
              <div className="col-span-2 text-[10px] font-black text-slate-400 uppercase tracking-widest text-center">Fecha</div>
              <div className="col-span-2 text-[10px] font-black text-slate-400 uppercase tracking-widest text-right">Acciones</div>
            </div>

            <div className="divide-y divide-slate-100">
              {reports.map((report: any) => (
                <motion.div 
                  key={report.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  onClick={() => handlePreviewPDF(report.id)}
                  className="hover:bg-blue-50/40 transition-all cursor-pointer group relative"
                >
                  {/* VERSION DESKTOP: Tabla clásica y organizada */}
                  <div className="hidden md:grid grid-cols-12 gap-4 px-8 py-5 items-center">
                    <div className="col-span-3 flex flex-col gap-1.5 items-start">
                      <span className="text-sm font-black text-slate-900 group-hover:text-blue-600">
                        {report.report_number || `RV-${report.id}`}
                      </span>
                      <div className="flex items-center gap-1.5">
                        {getStatusBadge(report.status)}
                        {report.sap_doc_num && (
                          <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 border border-emerald-500/20 text-[9px] font-black whitespace-nowrap">
                            SAP #{report.sap_doc_num}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="col-span-5 flex flex-col">
                      <span className="text-sm font-bold text-slate-800 truncate">{report.client_name || 'Sin Cliente'}</span>
                      <div className="flex items-center gap-1.5 text-[10px] text-slate-400 font-medium truncate">
                        <span className="italic">{report.project_name || 'Obra no especificada'}</span>
                        {report.commune && (
                          <>
                            <span className="text-slate-300">•</span>
                            <span className="font-bold text-blue-600/80">{report.commune}</span>
                          </>
                        )}
                      </div>
                    </div>
                    <div className="col-span-2 text-center">
                      <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-slate-100 text-[11px] font-bold text-slate-600">
                        {report.visit_date ? new Date(report.visit_date).toLocaleDateString('es-CL') : '—'}
                      </div>
                    </div>
                    <div className="col-span-2 flex items-center justify-end gap-2" onClick={(e) => e.stopPropagation()}>
                      {report.status === 'approved' && (
                        <button 
                          onClick={() => handleOpenEmailModal(report)} 
                          className="p-2.5 rounded-xl bg-blue-50 text-blue-600 border border-blue-100 hover:bg-blue-600 hover:text-white transition-all shadow-sm"
                          title="Enviar por Correo"
                        >
                          <EnvelopeIcon className="w-4 h-4"/>
                        </button>
                      )}
                      {report.status !== 'closed' && report.status !== 'sent' && (
                        <button 
                          onClick={() => navigate(`/visit-report-form/${report.id}`)} 
                          className="p-2.5 rounded-xl bg-slate-800 text-white shadow-sm hover:bg-black transition-all"
                          title="Editar"
                        >
                          <DocumentTextIcon className="w-4 h-4"/>
                        </button>
                      )}
                      {report.status === 'draft' && hasDraftContent(report) && (
                        <button 
                          onClick={() => { setSelectedReport(report); setShowSignatureModal(true); }} 
                          className="p-2.5 rounded-xl bg-emerald-500 text-white shadow-sm hover:bg-emerald-600 transition-all"
                          title="Firmar"
                        >
                          <PencilSquareIcon className="w-4 h-4"/>
                        </button>
                      )}
                      {!isTechnician && (
                        <button 
                          onClick={() => handleDelete(report.id)} 
                          className="p-2.5 rounded-xl bg-rose-50 text-rose-500 border border-rose-100 hover:bg-rose-500 hover:text-white transition-all"
                          title="Eliminar"
                        >
                          <TrashIcon className="w-4 h-4"/>
                        </button>
                      )}
                    </div>
                  </div>

                  {/* VERSION MOBILE: Tarjetas con aire y legibilidad */}
                  <div className="md:hidden p-5 flex flex-col gap-3">
                    <div className="flex justify-between items-start">
                      <div className="flex flex-col gap-0.5">
                        <span className="text-sm font-black text-slate-900">{report.report_number || `RV-${report.id}`}</span>
                        {report.sap_doc_num && (
                          <span className="w-fit px-2 py-0.5 rounded-md bg-emerald-500/10 text-emerald-600 border border-emerald-500/20 text-[9px] font-black uppercase">
                            SINCRONIZADO SAP #{report.sap_doc_num}
                          </span>
                        )}
                      </div>
                      <div className="text-[10px] font-black text-slate-400 bg-slate-50 px-2.5 py-1.5 rounded-lg border border-slate-100">
                        {report.visit_date ? new Date(report.visit_date).toLocaleDateString('es-CL') : '—'}
                      </div>
                    </div>

                    <div className="flex flex-col gap-1">
                      <span className="text-[15px] font-bold text-slate-800 leading-tight pr-10">{report.client_name || 'Sin Cliente'}</span>
                      <div className="text-xs text-slate-400 font-medium truncate flex items-center gap-1.5 flex-wrap">
                        <span className="flex items-center gap-1">
                          <BuildingOfficeIcon className="w-3 h-3"/> {report.project_name || 'Obra no especificada'}
                        </span>
                        {report.commune && (
                          <>
                            <span className="text-slate-300">•</span>
                            <span className="font-bold text-blue-600">{report.commune}</span>
                          </>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center justify-end gap-3 mt-2" onClick={(e) => e.stopPropagation()}>
                      {report.status === 'approved' && (
                        <button 
                          onClick={() => handleOpenEmailModal(report)}
                          className="flex-1 flex items-center justify-center gap-2 py-3 bg-blue-600 text-white rounded-xl text-[10px] font-black uppercase tracking-widest shadow-lg shadow-blue-900/20"
                        >
                          <EnvelopeIcon className="w-4 h-4"/> Enviar Email
                        </button>
                      )}
                      {report.status !== 'closed' && report.status !== 'sent' && (
                        <button 
                          onClick={() => navigate(`/visit-report-form/${report.id}`)} 
                          className="flex-1 flex items-center justify-center gap-2 py-3 bg-slate-800 text-white rounded-xl text-[10px] font-black uppercase tracking-widest shadow-lg shadow-slate-200"
                        >
                          <DocumentTextIcon className="w-4 h-4"/> Editar
                        </button>
                      )}
                      {report.status === 'draft' && hasDraftContent(report) && (
                        <button 
                          onClick={() => { setSelectedReport(report); setShowSignatureModal(true); }} 
                          className="flex-1 flex items-center justify-center gap-2 py-3 bg-emerald-500 text-white rounded-xl text-[10px] font-black uppercase tracking-widest shadow-lg shadow-emerald-200"
                        >
                          <PencilSquareIcon className="w-4 h-4"/> Firmar
                        </button>
                      )}
                      {!isTechnician && (
                        <button 
                          onClick={() => handleDelete(report.id)} 
                          className="p-3 bg-rose-50 text-rose-500 border border-rose-100 rounded-xl"
                        >
                          <TrashIcon className="w-5 h-5"/>
                        </button>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        ) : (
          <div className="text-center py-20">
            <FolderOpenIcon className="mx-auto h-16 w-16 text-slate-200" />
            <h3 className="mt-4 text-lg font-bold text-slate-700">Sin reportes</h3>
            <p className="mt-2 text-sm text-slate-400">Crea tu primer reporte de visita desde el botón superior.</p>
            <button
              onClick={() => navigate('/visit-report-form')}
              className="mt-6 inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-xl text-xs font-black uppercase tracking-widest hover:bg-blue-700 transition-all"
            >
              <PlusIcon className="h-4 w-4 mr-2" /> Crear Reporte
            </button>
          </div>
        )}
      </div>

      {/* PAGINATION */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between bg-white px-6 py-4 rounded-2xl shadow-md border border-slate-100">
          <p className="text-xs font-bold text-slate-400">
            Página <span className="text-slate-800">{currentPage}</span> de <span className="text-slate-800">{totalPages}</span> · {totalCount} resultados
          </p>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setCurrentPage(p => Math.max(p - 1, 1))}
              disabled={currentPage === 1}
              className="p-2 rounded-lg bg-slate-50 border border-slate-200 text-slate-500 hover:bg-blue-50 hover:text-blue-600 disabled:opacity-30 transition-all"
            >
              <ChevronLeftIcon className="w-4 h-4" />
            </button>
            {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
              let pageNum: number;
              if (totalPages <= 7) {
                pageNum = i + 1;
              } else if (currentPage <= 4) {
                pageNum = i + 1;
              } else if (currentPage >= totalPages - 3) {
                pageNum = totalPages - 6 + i;
              } else {
                pageNum = currentPage - 3 + i;
              }
              return (
                <button
                  key={pageNum}
                  onClick={() => setCurrentPage(pageNum)}
                  className={`w-9 h-9 rounded-lg text-xs font-black transition-all
                    ${pageNum === currentPage
                      ? 'bg-blue-600 text-white shadow-lg shadow-blue-200'
                      : 'bg-slate-50 text-slate-600 hover:bg-blue-50 border border-slate-200'
                    }`}
                >
                  {pageNum}
                </button>
              );
            })}
            <button
              onClick={() => setCurrentPage(p => Math.min(p + 1, totalPages))}
              disabled={currentPage === totalPages}
              className="p-2 rounded-lg bg-slate-50 border border-slate-200 text-slate-500 hover:bg-blue-50 hover:text-blue-600 disabled:opacity-30 transition-all"
            >
              <ChevronRightIcon className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Modal de Previsualización PDF FULL SCREEN */}
      {showPDFPreviewModal && previewURL && ReactDOM.createPortal(
        <div className="fixed inset-0 z-[9999] flex flex-col bg-slate-950 animate-in fade-in zoom-in duration-300">
          <div className="flex items-center justify-between p-4 bg-slate-900 border-b border-white/10 shadow-2xl">
            <div className="flex items-center gap-4">
              <div className="bg-blue-600 p-2 rounded-lg">
                <DocumentTextIcon className="w-5 h-5 text-white"/>
              </div>
              <div>
                <h3 className="text-white font-black uppercase tracking-widest text-sm">Vista Completa del Reporte</h3>
                <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Documento Técnico Polifusión</p>
              </div>
            </div>
            <button 
              onClick={() => setShowPDFPreviewModal(false)}
              className="px-6 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all"
            >
              Cerrar Vista
            </button>
          </div>
          <div className="flex-1 bg-slate-800 relative flex flex-col overflow-hidden">
            <object
              data={previewURL}
              type="application/pdf"
              className="w-full h-full border-none"
            >
              <div className="flex flex-col items-center justify-center h-full p-8 text-center bg-slate-900">
                <div className="p-8 bg-slate-800 rounded-3xl border border-white/10 shadow-2xl flex flex-col items-center gap-6 max-w-sm">
                  <div className="p-4 bg-blue-500/10 rounded-2xl">
                    <DocumentArrowDownIcon className="w-12 h-12 text-blue-500" />
                  </div>
                  <h3 className="text-white font-black uppercase tracking-tighter text-lg">Documento Listo</h3>
                  <p className="text-slate-400 text-xs">Para visualizar en móvil, abre el archivo directamente.</p>
                  <a 
                    href={previewURL} 
                    target="_blank" 
                    rel="noreferrer"
                    className="w-full py-4 bg-blue-600 text-white rounded-2xl text-xs font-black uppercase tracking-widest shadow-lg shadow-blue-900/40"
                  >
                    Ver Reporte Completo
                  </a>
                </div>
              </div>
            </object>
          </div>
        </div>,
        document.body
      )}

      {/* Modal de Firma FULL SCREEN */}
      {showSignatureModal && selectedReport && (
        <SignatureCanvas
          title="Firma de Recepción (Cliente)"
          signerName={selectedReport.client_name || 'Representante de Obra'}
          onSave={async (dataUrl) => {
            setShowSignatureModal(false);
            toast.loading("Procesando firma y sincronizando con SAP...", { id: 'sap-sync' });
            try {
              // 1. Guardar firma y marcar como final
              await visitReportsAPI.update(selectedReport.id, { 
                client_signature: dataUrl,
                is_final: true 
              });
              // 2. Generar PDF final y disparar SAP Sync
              await visitReportsAPI.generatePDF(selectedReport.id, { final: true });
              
              toast.success("Reporte firmado y sincronizado exitosamente", { id: 'sap-sync' });
              queryClient.invalidateQueries({ queryKey: ['visit-reports'] });
            } catch (err: any) {
              console.error("Error en flujo de firma:", err);
              toast.error("Error al procesar la firma: " + (err.response?.data?.error || err.message), { id: 'sap-sync' });
            }
          }}
          onClose={() => {
            setShowSignatureModal(false);
            setSelectedReport(null);
          }}
        />
      )}

      {/* Modal de Correo Dinámico */}
      <Modal isOpen={showEmailModal} onClose={() => setShowEmailModal(false)} size="sm">
        <ModalHeader className="!border-none !pb-0">
          <div className="flex items-center gap-3">
            <div className="bg-blue-500/10 p-2 rounded-lg">
              <EnvelopeIcon className="w-5 h-5 text-blue-600"/>
            </div>
            <ModalTitle className="text-sm font-black uppercase tracking-tight">Enviar Reporte</ModalTitle>
          </div>
          <ModalCloseButton onClick={() => setShowEmailModal(false)} />
        </ModalHeader>
        <ModalBody className="!pt-4">
          <div className="space-y-4">
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">
              El reporte se enviará exclusivamente al vendedor de SAP asociado y a sus superiores (NUNCA directamente al cliente). Puede ingresar múltiples correos separados por coma (,) o punto y coma (;):
            </p>
            <div className="relative">
              <input
                type="text"
                placeholder="vendedor@sertec.cl (use ',' o ';' para múltiples correos)"
                value={emailToSend}
                disabled={isFetchingEmail}
                onChange={(e) => {
                  e.stopPropagation();
                  setEmailToSend(e.target.value);
                }}
                className={`w-full px-4 py-3 border border-slate-200 rounded-xl text-sm font-bold text-slate-700 placeholder-slate-400 focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all outline-none ${isFetchingEmail ? 'bg-slate-100 opacity-70' : 'bg-slate-50'}`}
              />
              {isFetchingEmail && (
                <div className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
              )}
            </div>
          </div>
        </ModalBody>
        <ModalFooter className="!border-none !pt-2">
          <button
            onClick={() => setShowEmailModal(false)}
            className="px-5 py-2.5 text-[10px] font-black uppercase tracking-widest text-slate-400 hover:text-slate-600 transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={handleSendEmail}
            className="px-6 py-2.5 bg-blue-600 text-white rounded-xl text-[10px] font-black uppercase tracking-widest shadow-lg shadow-blue-200 hover:bg-blue-700 transition-all active:scale-95"
          >
            Enviar Ahora
          </button>
        </ModalFooter>
      </Modal>
    </div>
  );
};

export default VisitReportsPage;