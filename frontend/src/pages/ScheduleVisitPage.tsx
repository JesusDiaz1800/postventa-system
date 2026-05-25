import React, { useState, useMemo, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { sapAPI, visitReportsAPI } from '../services/api';
import { usePermissions } from '../hooks/usePermissions';
import {
  CalendarIcon,
  UserIcon,
  BuildingOfficeIcon,
  ClockIcon,
  MapPinIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  PlusIcon,
  MagnifyingGlassIcon,
  ArrowLeftIcon,
  TrashIcon,
  PencilIcon,
  EnvelopeIcon,
  PhoneIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';
import { Modal, ModalHeader, ModalBody, ModalTitle, ModalCloseButton } from '../components/ui/Modal';

// Simple Calendar Component
const MiniCalendar = ({ selectedDate, onSelectDate, pendingVisits }: { selectedDate: Date, onSelectDate: (d: Date) => void, pendingVisits: any[] }) => {
  const [currentMonth, setCurrentMonth] = useState(new Date(selectedDate.getFullYear(), selectedDate.getMonth(), 1));

  const daysInMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 0).getDate();
  const firstDayOfMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), 1).getDay();
  const adjustedFirstDay = firstDayOfMonth === 0 ? 6 : firstDayOfMonth - 1;

  const prevMonth = () => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1));
  const nextMonth = () => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1));

  const monthNames = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];

  return (
    <div className="bg-slate-50/80 backdrop-blur-md rounded-3xl p-6 border border-slate-200 shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <h4 className="text-xs font-black text-slate-800 uppercase tracking-widest">
          {monthNames[currentMonth.getMonth()]} {currentMonth.getFullYear()}
        </h4>
        <div className="flex gap-1">
          <button type="button" onClick={prevMonth} className="p-1.5 hover:bg-slate-200 rounded-lg transition-all"><ChevronLeftIcon className="w-4 h-4 text-slate-600"/></button>
          <button type="button" onClick={nextMonth} className="p-1.5 hover:bg-slate-200 rounded-lg transition-all"><ChevronRightIcon className="w-4 h-4 text-slate-600"/></button>
        </div>
      </div>
      <div className="grid grid-cols-7 gap-1 text-center mb-3">
        {['Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sá', 'Do'].map(d => <div key={d} className="text-[10px] font-black text-slate-400 uppercase tracking-wider">{d}</div>)}
      </div>
      <div className="grid grid-cols-7 gap-1">
        {Array.from({ length: adjustedFirstDay }).map((_, i) => <div key={`empty-${i}`} className="h-10"></div>)}
        {Array.from({ length: daysInMonth }).map((_, i) => {
          const date = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), i + 1);
          const isSelected = date.toDateString() === selectedDate.toDateString();
          const isToday = date.toDateString() === new Date().toDateString();
          
          const visitsThisDay = pendingVisits.filter(v => {
            if (!v.visit_date) return false;
            const vDate = new Date(v.visit_date);
            return vDate.toDateString() === date.toDateString();
          });

          return (
            <button
              key={i}
              type="button"
              onClick={() => onSelectDate(date)}
              className={`h-10 w-full rounded-2xl text-xs font-black transition-all relative flex items-center justify-center
                ${isSelected ? 'bg-blue-600 text-white shadow-lg shadow-blue-200' : 
                  isToday ? 'bg-blue-50 text-blue-600 border border-blue-200' : 
                  'hover:bg-slate-200 text-slate-700'}`}
            >
              {i + 1}
              {visitsThisDay.length > 0 && (
                <span className="absolute -top-1 -right-1 min-w-[18px] h-4.5 px-1 rounded-full bg-orange-500 text-white flex items-center justify-center text-[9px] font-black shadow-md border border-white">
                  {visitsThisDay.length}
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};

export const ScheduleVisitPage = () => {
  const { user } = usePermissions();
  const isTechnician = user?.role === 'technical_service' || user?.role === 'tecnico' || user?.role === 'technician';

  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [isEditing, setIsEditing] = useState<number | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [selectedTechnicianFilter, setSelectedTechnicianFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  const [formData, setFormData] = useState({
    client_name: '',
    client_rut: '',
    project_name: '',
    project_id: '',
    address: '',
    commune: '',
    salesperson: '',
    technician_id: '',
    technician: '',
    visit_date: new Date().toLocaleDateString('en-CA'),
    visit_time: '09:00',
    city: '',
    installer: '',
    installer_phone: '',
    client_contact: '',
    client_email: '',
    telephone: '',
    construction_company: '',
  });

  const [customerSearch, setCustomerSearch] = useState('');
  const [customers, setCustomers] = useState<any[]>([]);
  const [isSearchingCustomers, setIsSearchingCustomers] = useState(false);
  const searchTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);

  const { data: technicians } = useQuery({
    queryKey: ['sap-technicians'],
    queryFn: () => sapAPI.getTechnicians('technician').then(res => res.data),
  });

  const { data: projects, isLoading: loadingProjects } = useQuery({
    queryKey: ['sap-customer-projects', formData.client_rut],
    queryFn: () => sapAPI.getCustomerProjects(formData.client_rut).then(res => res.data.projects),
    enabled: !!formData.client_rut,
  });

  const { data: allVisitsData } = useQuery({
    queryKey: ['visit-reports', 'draft-all'],
    queryFn: () => visitReportsAPI.list({ status: 'draft', page_size: 100 }).then(res => res.data),
    staleTime: 30_000,
    refetchOnWindowFocus: false,
  });

  // Intentar mapear el ID del técnico en SAP con el usuario autenticado
  const myTechnicianId = useMemo(() => {
    if (!isTechnician || !user || !technicians) return null;
    
    const uName = `${user.first_name || ''} ${user.last_name || ''}`.trim().toLowerCase();
    const uUsername = user.username?.toLowerCase() || '';
    
    const normalizeStr = (str: string) => 
      str ? str.normalize("NFD").replace(/[\u0300-\u036f]/g, "").trim().toLowerCase() : '';
    
    const normUName = normalizeStr(uName);
    const normUsername = normalizeStr(uUsername);
    
    for (const t of technicians) {
      const tName = normalizeStr(t.name || t.fullName || `${t.firstName || ''} ${t.lastName || ''}`);
      const tId = t.id?.toString() || t.empID?.toString() || '';
      
      if (tName && (tName.includes(normUName) || normUName.includes(tName))) {
        return tId;
      }
      if (tName && (tName.includes(normUsername) || normUsername.includes(tName))) {
        return tId;
      }
    }
    return null;
  }, [isTechnician, user, technicians]);
  
  const selectedTechnicianFilterStr = selectedTechnicianFilter.toString();
  const pendingVisits = useMemo(() => {
    const raw = allVisitsData?.results || (Array.isArray(allVisitsData) ? allVisitsData : []);
    
    if (isTechnician && user) {
      const uName = `${user.first_name || ''} ${user.last_name || ''}`.trim().toLowerCase();
      const uUsername = user.username?.toLowerCase() || '';
      
      const normalizeStr = (str: string) => 
        str ? str.normalize("NFD").replace(/[\u0300-\u036f]/g, "").trim().toLowerCase() : '';
      
      const normUName = normalizeStr(uName);
      const normUsername = normalizeStr(uUsername);
      
      return raw.filter((v: any) => {
        // 1. Filtrar por ID de SAP emparejado
        if (myTechnicianId && v.technician_id?.toString() === myTechnicianId.toString()) {
          return true;
        }
        
        // 2. Fallback por coincidencia textual del nombre del técnico
        const vTechName = normalizeStr(v.technician);
        if (normUName && vTechName && (vTechName.includes(normUName) || normUName.includes(vTechName))) {
          return true;
        }
        if (normUsername && vTechName && (vTechName.includes(normUsername) || normUsername.includes(vTechName))) {
          return true;
        }
        
        // 3. Fallback por creador
        if (v.created_by?.toString() === user.id?.toString()) {
          return true;
        }
        
        return false;
      });
    }
    
    if (selectedTechnicianFilterStr === 'all') return raw;
    return raw.filter((v: any) => v.technician_id?.toString() === selectedTechnicianFilterStr);
  }, [allVisitsData, selectedTechnicianFilterStr, isTechnician, user, myTechnicianId]);

  const visitsForSelectedDate = useMemo(() => {
    return pendingVisits.filter(v => {
      if (!v.visit_date) return false;
      const vDate = new Date(v.visit_date);
      return vDate.toDateString() === selectedDate.toDateString();
    });
  }, [pendingVisits, selectedDate]);

  const filteredVisits = useMemo(() => {
    if (!searchTerm.trim()) return visitsForSelectedDate;
    const q = searchTerm.toLowerCase();
    return visitsForSelectedDate.filter(v => 
      v.client_name?.toLowerCase().includes(q) ||
      v.project_name?.toLowerCase().includes(q) ||
      v.technician?.toLowerCase().includes(q) ||
      v.commune?.toLowerCase().includes(q)
    );
  }, [visitsForSelectedDate, searchTerm]);

  // Group visits by commune for smart organization
  const visitsByCommune = useMemo(() => {
    const groups: Record<string, any[]> = {};
    for (const v of filteredVisits) {
      const key = (v.commune || 'Sin Comuna').trim().toUpperCase();
      if (!groups[key]) groups[key] = [];
      groups[key].push(v);
    }
    // Sort groups: communes with more visits first, then alphabetically
    return Object.entries(groups).sort(([aKey, aList], [bKey, bList]) => {
      if (bList.length !== aList.length) return bList.length - aList.length;
      return aKey.localeCompare(bKey);
    });
  }, [filteredVisits]);

  const handleCustomerSearch = (query: string) => {
    setCustomerSearch(query);
    if (query.length < 3) {
      setCustomers([]);
      return;
    }
    
    if (searchTimeout.current) clearTimeout(searchTimeout.current);
    setIsSearchingCustomers(true);
    
    searchTimeout.current = setTimeout(async () => {
      try {
        const response = await sapAPI.searchCustomers(query);
        setCustomers(response.data.results || []);
      } catch (error) {
        console.error("Error buscando clientes:", error);
      } finally {
        setIsSearchingCustomers(false);
      }
    }, 500);
  };

  const selectCustomer = async (customer: any) => {
    setFormData(prev => ({
      ...prev,
      client_name: customer.card_name,
      client_rut: customer.card_code,
      project_name: '',
      project_id: '',
      address: '',
      commune: '',
      salesperson: '',
      city: '',
      installer: '',
      installer_phone: '',
      client_contact: '',
      client_email: '',
      telephone: '',
      construction_company: '',
    }));
    setCustomerSearch(customer.card_name);
    setCustomers([]);

    try {
      const detailRes = await sapAPI.getCustomerDetails(customer.card_code);
      if (detailRes.data) {
        const details = detailRes.data;
        setFormData(prev => ({
          ...prev,
          salesperson: details.salesperson_name || '',
          client_contact: details.contact_person || '',
          client_email: details.salesperson_email || '', // Exclusivamente correo de vendedor SAP
          telephone: details.phone || '',
          installer: details.installer || prev.installer,
          installer_phone: details.installer_phone || prev.installer_phone,
        }));
      }
    } catch (e) {
      console.error("Error al cargar detalles del cliente", e);
    }
  };

  const selectProject = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const projId = e.target.value;
    const project = projects?.find(p => p.proyecto === projId);
    
    if (project) {
      setFormData(prev => ({
        ...prev,
        project_id: project.proyecto,
        project_name: project.obra,
        address: project.direccion || '',
        commune: project.comuna || '', 
        city: project.ciudad || prev.city || 'Santiago',
        construction_company: project.construction_company || prev.construction_company,
        installer: project.installer || prev.installer,
        installer_phone: project.installer_phone || prev.installer_phone,
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        project_id: '',
        project_name: '',
        city: '',
        construction_company: '',
        installer: '',
        installer_phone: '',
      }));
    }
  };

  const resetForm = (dateToKeep?: Date) => {
    const defaultDate = dateToKeep || selectedDate || new Date();
    setFormData({
      client_name: '',
      client_rut: '',
      project_name: '',
      project_id: '',
      address: '',
      commune: '',
      salesperson: '',
      technician_id: '',
      technician: '',
      visit_date: defaultDate.toLocaleDateString('en-CA'),
      visit_time: '09:00',
      city: '',
      installer: '',
      installer_phone: '',
      client_contact: '',
      client_email: '',
      telephone: '',
      construction_company: '',
    });
    setCustomerSearch('');
    setIsEditing(null);
  };

  const deleteVisitMutation = useMutation({
    mutationFn: (id: number) => visitReportsAPI.delete(id),
    onSuccess: () => {
      toast.success('Programación cancelada con éxito');
      queryClient.invalidateQueries({ queryKey: ['visit-reports'] });
      resetForm();
    },
    onError: () => {
      toast.error('Error al cancelar la programación');
    }
  });

  const handleDeleteVisit = (e: React.MouseEvent, id: number) => {
    e.stopPropagation();
    if (window.confirm('¿Está seguro de que desea cancelar y eliminar esta programación de visita? Esta acción no se puede deshacer.')) {
      deleteVisitMutation.mutate(id);
    }
  };

  const handleEditVisit = (visit: any) => {
    const vDate = new Date(visit.visit_date);
    const timeStr = `${String(vDate.getHours()).padStart(2, '0')}:${String(vDate.getMinutes()).padStart(2, '0')}`;
    const dateStr = vDate.toLocaleDateString('en-CA');
    
    setFormData({
      client_name: visit.client_name || '',
      client_rut: visit.client_rut || '',
      project_name: visit.project_name || '',
      project_id: visit.project_id || '',
      address: visit.address || '',
      commune: visit.commune || '',
      salesperson: visit.salesperson || '',
      technician_id: visit.technician_id?.toString() || '',
      technician: visit.technician || '',
      visit_date: dateStr,
      visit_time: timeStr,
      city: visit.city || '',
      installer: visit.installer || '',
      installer_phone: visit.installer_phone || '',
      client_contact: visit.client_contact || '',
      client_email: visit.client_email || '',
      telephone: visit.telephone || '',
      construction_company: visit.construction_company || '',
    });
    setCustomerSearch(visit.client_name || '');
    setIsEditing(visit.id);
    setSelectedDate(vDate);
    setShowModal(true);
  };

  const saveMutation = useMutation({
    mutationFn: async (data: any) => {
      const [year, month, day] = formData.visit_date.split('-').map(Number);
      const visitDate = new Date(year, month - 1, day, 9, 0, 0, 0);
      
      const tech = technicians?.find((t: any) => t.id.toString() === formData.technician_id);
      
      const payload = {
        ...formData,
        visit_date: visitDate.toISOString(),
        technician: tech?.name || formData.technician,
        status: 'draft',
      };

      if (isEditing) {
        return visitReportsAPI.update(isEditing, payload);
      } else {
        return visitReportsAPI.create(payload);
      }
    },
    onSuccess: () => {
      toast.success(isEditing ? 'Visita reprogramada con éxito' : 'Visita programada exitosamente');
      queryClient.invalidateQueries({ queryKey: ['visit-reports'] });
      resetForm();
      setShowModal(false);
    },
    onError: (err: any) => {
      toast.error('Error al guardar: ' + (err.response?.data?.error || err.message));
    }
  });

  const handleOpenNewScheduling = () => {
    resetForm(selectedDate);
    setShowModal(true);
  };

  return (
    <div className="max-w-[1400px] mx-auto pb-12 pt-2 px-4">
      {/* HEADER COMPACTO */}
      <motion.div 
        initial={{ y: -10, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="sticky top-2 z-40 flex items-center justify-between mb-6 p-4 rounded-3xl bg-white/90 backdrop-blur-xl border border-slate-200 shadow-sm"
      >
        <div className="flex items-center gap-3">
           <button onClick={() => navigate(isTechnician ? '/visit-reports' : '/quick-actions')} className="p-2.5 hover:bg-slate-100 rounded-xl transition-all text-slate-600">
             <ArrowLeftIcon className="w-5 h-5"/>
           </button>
           <div className="flex items-center gap-3">
             <div className="bg-blue-600 p-2.5 rounded-2xl shadow-lg shadow-blue-200">
               <CalendarIcon className="w-5 h-5 text-white"/>
             </div>
             <div>
               <h1 className="text-base font-black text-slate-900 flex items-center gap-2 uppercase tracking-tight">
                 Agenda y Programación de Visitas
               </h1>
               <p className="text-[10px] text-slate-400 font-bold uppercase tracking-[0.2em]">Vista Principal de la Planificación Operativa</p>
             </div>
           </div>
        </div>

        {!isTechnician && (
          <button
            onClick={handleOpenNewScheduling}
            className="flex items-center gap-2 px-5 py-3 bg-blue-600 text-white rounded-2xl text-[10px] font-black uppercase tracking-widest shadow-lg shadow-blue-200 hover:bg-blue-700 hover:shadow-blue-300 hover:-translate-y-0.5 active:scale-95 transition-all"
          >
            <PlusIcon className="w-4 h-4"/> Nueva Programación
          </button>
        )}
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* PANEL IZQUIERDO: Calendario y Filtros (4 Columnas) */}
        <div className="lg:col-span-4 flex flex-col gap-6">
          <div className="flex flex-col gap-2 bg-white rounded-3xl border border-slate-200 p-5 shadow-sm">
            <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-1.5">
              <UserIcon className="w-3.5 h-3.5 text-blue-600"/>
              {isTechnician ? 'Técnico Asignado:' : 'Filtrar por Técnico:'}
            </label>
            {isTechnician ? (
              <div className="w-full px-4 py-3.5 bg-blue-50/50 border border-blue-200/60 rounded-2xl text-xs font-extrabold text-blue-700 flex items-center gap-2 shadow-sm">
                <div className="w-2.5 h-2.5 rounded-full bg-blue-500 animate-pulse shrink-0" />
                <span>{user ? (user.first_name ? `${user.first_name} ${user.last_name || ''}`.trim() : user.username) : ''}</span>
              </div>
            ) : (
              <select
                value={selectedTechnicianFilter}
                onChange={(e) => setSelectedTechnicianFilter(e.target.value)}
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-bold text-slate-700 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all outline-none appearance-none cursor-pointer"
              >
                <option value="all">-- Todos los Técnicos --</option>
                {technicians?.map((t: any) => (
                  <option key={t.id} value={t.id.toString()}>{t.name}</option>
                ))}
              </select>
            )}
          </div>

          <MiniCalendar 
            selectedDate={selectedDate} 
            onSelectDate={(d) => {
              setSelectedDate(d);
              setFormData(prev => ({
                ...prev,
                visit_date: d.toLocaleDateString('en-CA')
              }));
            }} 
            pendingVisits={pendingVisits} 
          />
        </div>

        {/* PANEL DERECHO: Lista Principal de Visitas Programadas (8 Columnas) */}
        <div className="lg:col-span-8 flex flex-col gap-4">
          <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm flex flex-col min-h-[500px]">
            {/* Header del panel derecho */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 pb-5 border-b border-slate-100">
              <div>
                <h5 className="text-sm font-black text-slate-800 uppercase tracking-widest flex items-center gap-2">
                  <ClockIcon className="w-5 h-5 text-blue-600"/>
                  Agenda del Día: {selectedDate.toLocaleDateString('es-CL', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
                </h5>
                <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider mt-1">
                  Se muestran las visitas programadas para la fecha seleccionada
                </p>
              </div>
              <span className="self-start sm:self-auto text-[11px] font-black text-blue-600 bg-blue-50 border border-blue-100 px-4 py-1.5 rounded-full">
                {visitsForSelectedDate.length} Visitas
              </span>
            </div>

            {/* Buscador de visitas del día */}
            {visitsForSelectedDate.length > 0 && (
              <div className="relative mb-4">
                <MagnifyingGlassIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Filtrar visitas de hoy por cliente, obra o técnico..."
                  className="w-full pl-11 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-700 focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all outline-none"
                />
              </div>
            )}
            
            {/* Listado agrupado por comuna */}
            <div className="flex flex-col gap-5 overflow-y-auto pr-1 flex-1 max-h-[600px] custom-scrollbar">
              {filteredVisits.length > 0 ? (
                visitsByCommune.map(([commune, visits]) => (
                  <div key={commune}>
                    {/* Commune group header */}
                    <div className="flex items-center gap-2 mb-2.5">
                      <MapPinIcon className="w-3.5 h-3.5 text-blue-500 flex-shrink-0" />
                      <span className="text-[10px] font-black text-blue-700 uppercase tracking-widest">{commune}</span>
                      <span className="flex-shrink-0 text-[9px] font-black bg-blue-100 text-blue-600 px-1.5 py-0.5 rounded-full">{visits.length}</span>
                      <div className="flex-1 h-px bg-blue-100" />
                    </div>

                    <div className="flex flex-col gap-3">
                      {visits.map(v => (
                        <div
                          key={v.id}
                          onClick={() => !isTechnician && handleEditVisit(v)}
                          className={`p-5 rounded-2xl border border-slate-200 hover:border-blue-300 hover:shadow-lg hover:shadow-blue-50/40 transition-all bg-white relative group ${!isTechnician ? 'cursor-pointer' : ''}`}
                        >
                          <div className="flex flex-col sm:flex-row justify-between items-start gap-2 mb-3">
                            <div className="flex items-center gap-2">
                              <span className="text-[9px] font-black text-blue-700 bg-blue-50 border border-blue-200/50 px-2 py-0.5 rounded-md uppercase tracking-wider">
                                Programada
                              </span>
                              <span className="text-[9px] font-bold text-slate-400 bg-slate-50 px-2 py-0.5 rounded border border-slate-100 font-mono">
                                {v.report_number || `RV-${v.id}`}
                              </span>
                            </div>
                            {!isTechnician && (
                              <span className="opacity-0 group-hover:opacity-100 transition-opacity text-[9px] font-bold text-blue-400 flex items-center gap-1 ml-auto">
                                <PencilIcon className="w-3 h-3"/> Click para editar
                              </span>
                            )}
                          </div>

                          <h4 className="text-base font-extrabold text-slate-800 mb-3 leading-snug group-hover:text-blue-700 transition-colors">
                            {v.client_name}
                          </h4>

                          {/* Información Técnica y de Obra Grid */}
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-3 text-xs">
                            <div className="flex items-center gap-2 text-slate-600 bg-slate-50/50 px-3 py-1.5 rounded-xl border border-slate-100">
                              <BuildingOfficeIcon className="w-4 h-4 text-slate-400 shrink-0"/>
                              <span className="truncate"><strong>Obra:</strong> {v.project_name || 'Sin obra'}</span>
                            </div>
                            <div className="flex items-center gap-2 text-slate-600 bg-slate-50/50 px-3 py-1.5 rounded-xl border border-slate-100">
                              <UserIcon className="w-4 h-4 text-slate-400 shrink-0"/>
                              <span className="truncate"><strong>Técnico:</strong> {v.technician || 'Sin asignar'}</span>
                            </div>
                            {v.address && (
                              <div className="flex items-center gap-2 text-slate-600 bg-slate-50/50 px-3 py-1.5 rounded-xl border border-slate-100 sm:col-span-2">
                                <MapPinIcon className="w-4 h-4 text-blue-400 shrink-0"/>
                                <span className="truncate font-medium text-slate-700">{v.address}{v.commune ? `, ${v.commune}` : ''}{v.city ? `, ${v.city}` : ''}</span>
                              </div>
                            )}
                            {!v.address && (v.commune || v.city) && (
                              <div className="flex items-center gap-2 text-slate-600 bg-slate-50/50 px-3 py-1.5 rounded-xl border border-slate-100 sm:col-span-2">
                                <MapPinIcon className="w-4 h-4 text-slate-400 shrink-0"/>
                                <span className="truncate"><strong>Ubicación:</strong> {v.commune ? `${v.commune}, ` : ''}{v.city || 'Santiago'}</span>
                              </div>
                            )}
                          </div>

                          {/* Datos de contacto del reporte pre-cargados (si existen) */}
                          {(v.salesperson || v.client_contact) && (
                            <div className="mb-3 p-3 bg-blue-50/30 rounded-xl border border-blue-100/40 grid grid-cols-1 sm:grid-cols-2 gap-3 text-[11px] text-slate-500 font-medium">
                              {v.salesperson && (
                                <div className="flex items-center gap-1.5 truncate">
                                  <UserIcon className="w-3.5 h-3.5 text-blue-500 shrink-0"/>
                                  <span><strong>Vendedor SAP:</strong> {v.salesperson}</span>
                                </div>
                              )}
                              {v.client_contact && (
                                <div className="flex items-center gap-1.5 truncate">
                                  <UserIcon className="w-3.5 h-3.5 text-emerald-500 shrink-0"/>
                                  <span><strong>Contacto:</strong> {v.client_contact}</span>
                                </div>
                              )}
                            </div>
                          )}

                          {/* Footer: fecha creación + botón eliminar */}
                          <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-3">
                            <span className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">
                              Creado: {v.created_at ? new Date(v.created_at).toLocaleDateString('es-CL') : 'N/A'}
                            </span>
                            {!isTechnician && (
                              <button
                                onClick={(e) => { e.stopPropagation(); handleDeleteVisit(e, v.id); }}
                                className="flex items-center gap-1.5 px-3 py-1.5 text-[10px] font-black text-rose-500 bg-rose-50 hover:bg-rose-500 hover:text-white border border-rose-100 rounded-lg transition-all uppercase tracking-widest active:scale-95"
                                title="Cancelar y Eliminar Visita"
                              >
                                <TrashIcon className="w-3 h-3"/> Cancelar
                              </button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))
              ) : (

                <div className="flex flex-col items-center justify-center py-24 text-slate-400 gap-4">
                  <div className="w-16 h-16 rounded-full bg-slate-50 flex items-center justify-center border border-slate-100 shadow-inner">
                    <CalendarIcon className="w-8 h-8 text-slate-300" />
                  </div>
                  <div className="text-center">
                    <p className="text-sm font-bold text-slate-600">No hay visitas programadas</p>
                    <p className="text-xs text-slate-400 mt-1">
                      {searchTerm ? 'No se encontraron resultados para la búsqueda' : 'Selecciona otro día en el calendario o crea una nueva visita'}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

      </div>

      {/* MODAL DE NUEVA / EDICIÓN DE PROGRAMACIÓN */}
      <Modal isOpen={showModal} onClose={() => setShowModal(false)} size="lg">
        <ModalHeader className="!border-none !pb-2">
          <div className="flex items-center gap-3">
            <div className="bg-blue-500/10 p-2.5 rounded-xl">
              <CalendarIcon className="w-5 h-5 text-blue-600"/>
            </div>
            <div>
              <ModalTitle className="text-sm font-black uppercase tracking-wider text-slate-800">
                {isEditing ? 'Reprogramar Visita Técnica' : 'Programar Nueva Visita'}
              </ModalTitle>
              <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mt-0.5">SAP Integration & Technician Assignment</p>
            </div>
          </div>
          <ModalCloseButton onClick={() => setShowModal(false)} />
        </ModalHeader>
        <ModalBody className="!pt-4 max-h-[80vh] overflow-y-auto custom-scrollbar">
          <div className="space-y-5">
            {/* Cliente */}
            <div className="relative z-50">
              <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1.5 block">1. Buscar y Seleccionar Cliente (SAP)</label>
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  type="text"
                  value={customerSearch}
                  onChange={(e) => handleCustomerSearch(e.target.value)}
                  placeholder="Escriba RUT o Nombre del cliente (mín. 3 letras)..."
                  className="w-full pl-12 pr-4 py-3.5 bg-slate-50 border border-slate-200 rounded-2xl text-sm font-bold text-slate-800 focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all outline-none"
                />
                {isSearchingCustomers && (
                  <div className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                )}
              </div>
              
              {/* Dropdown de búsqueda autocomplete */}
              {customers.length > 0 && (
                <div className="absolute z-50 w-full mt-2 bg-white rounded-2xl shadow-[0_15px_50px_-15px_rgba(0,0,0,0.15)] border border-slate-200 max-h-60 overflow-y-auto">
                  {customers.map((c, idx) => (
                    <button
                      key={idx}
                      onClick={() => selectCustomer(c)}
                      className="w-full text-left px-5 py-3.5 hover:bg-blue-50 border-b border-slate-100 last:border-0 transition-colors group flex flex-col gap-0.5"
                    >
                      <div className="text-xs font-black text-slate-800 group-hover:text-blue-700">{c.card_name}</div>
                      <div className="text-[10px] font-bold text-slate-400 font-mono">{c.card_code}</div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Obra */}
            <div className="relative z-40">
              <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1.5 flex items-center justify-between">
                <span>2. Seleccionar Obra del Cliente</span>
                {loadingProjects && <span className="text-blue-500 flex items-center gap-1 text-[9px]"><div className="w-2.5 h-2.5 border border-blue-500 border-t-transparent rounded-full animate-spin"></div> Cargando proyectos...</span>}
              </label>
              <select
                value={formData.project_id}
                onChange={selectProject}
                disabled={!formData.client_rut || loadingProjects}
                className="w-full px-4 py-3.5 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-bold text-slate-700 focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all outline-none disabled:opacity-50 disabled:cursor-not-allowed appearance-none"
              >
                <option value="">-- Seleccionar Obra --</option>
                {projects?.map((p: any) => (
                  <option key={p.proyecto} value={p.proyecto}>{p.obra} ({p.proyecto})</option>
                ))}
              </select>
            </div>

            {/* Técnico y Fecha Visita */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 relative z-30">
              <div>
                <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1.5 block">3. Asignar Técnico de Visita</label>
                <select
                  value={formData.technician_id}
                  onChange={(e) => setFormData(prev => ({...prev, technician_id: e.target.value}))}
                  className="w-full px-4 py-3.5 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-bold text-slate-700 focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all outline-none appearance-none"
                >
                  <option value="">-- Seleccionar Técnico --</option>
                  {technicians?.map((t: any) => (
                    <option key={t.id} value={t.id}>{t.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1.5 block">4. Fecha Programada</label>
                <input
                  type="date"
                  value={formData.visit_date}
                  onChange={(e) => {
                    const newDateStr = e.target.value;
                    setFormData(prev => ({...prev, visit_date: newDateStr}));
                    if (newDateStr) {
                      const [year, month, day] = newDateStr.split('-').map(Number);
                      setSelectedDate(new Date(year, month - 1, day));
                    }
                  }}
                  className="w-full px-4 py-3.5 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-bold text-slate-700 focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all outline-none"
                />
              </div>
            </div>

            {/* Datos autocompletados (Info SAP) */}
            <AnimatePresence>
              {formData.client_rut && (
                <motion.div 
                  key="sap-info-panel"
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="bg-slate-50 rounded-2xl border border-slate-200 p-4 grid grid-cols-1 sm:grid-cols-2 gap-4 mt-3"
                >
                  <div className="col-span-1 sm:col-span-2 border-b border-slate-200/60 pb-2">
                    <span className="text-[10px] font-black text-blue-600 uppercase tracking-widest">Información SAP Pre-cargada</span>
                  </div>
                  <div>
                    <span className="block text-[9px] font-black text-slate-400 uppercase tracking-widest mb-0.5">Dirección Obra</span>
                    <span className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                      <MapPinIcon className="w-3.5 h-3.5 text-blue-500 shrink-0"/>
                      <span className="truncate">{formData.address || 'Sin dirección'} {formData.commune ? `- ${formData.commune}` : ''}</span>
                    </span>
                  </div>
                  <div>
                    <span className="block text-[9px] font-black text-slate-400 uppercase tracking-widest mb-0.5">Vendedor Asignado (SAP OSLP)</span>
                    <span className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                      <UserIcon className="w-3.5 h-3.5 text-slate-500 shrink-0"/>
                      <span className="truncate">{formData.salesperson || 'Sin vendedor'}</span>
                    </span>
                  </div>
                  {formData.client_email && (
                    <div>
                      <span className="block text-[9px] font-black text-slate-400 uppercase tracking-widest mb-0.5">Email de Envío Vendedor SAP (OSLP)</span>
                      <span className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                        <EnvelopeIcon className="w-3.5 h-3.5 text-emerald-500 shrink-0"/>
                        <span className="truncate">{formData.client_email}</span>
                      </span>
                    </div>
                  )}
                  {formData.client_contact && (
                    <div>
                      <span className="block text-[9px] font-black text-slate-400 uppercase tracking-widest mb-0.5">Contacto Principal Obra</span>
                      <span className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                        <UserIcon className="w-3.5 h-3.5 text-blue-500 shrink-0"/>
                        <span className="truncate">{formData.client_contact} {formData.telephone ? `(T: ${formData.telephone})` : ''}</span>
                      </span>
                    </div>
                  )}
                  {formData.installer && (
                    <div className="col-span-1 sm:col-span-2">
                      <span className="block text-[9px] font-black text-slate-400 uppercase tracking-widest mb-0.5">Instalador & Teléfono</span>
                      <span className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                        <UserIcon className="w-3.5 h-3.5 text-amber-500 shrink-0"/>
                        <span className="truncate">{formData.installer} {formData.installer_phone ? `- T: ${formData.installer_phone}` : ''}</span>
                      </span>
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>

            <div className="pt-4 border-t border-slate-100 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowModal(false)}
                className="px-5 py-3 text-[10px] font-black uppercase tracking-widest text-slate-400 hover:text-slate-600 transition-colors"
              >
                Cerrar
              </button>
              <button
                onClick={() => saveMutation.mutate(formData)}
                disabled={!formData.client_rut || !formData.technician_id || saveMutation.isPending}
                className="px-6 py-3 bg-blue-600 text-white rounded-2xl text-[10px] font-black uppercase tracking-widest shadow-lg shadow-blue-200 hover:bg-blue-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {saveMutation.isPending ? (
                  <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                ) : isEditing ? (
                  <>Guardar Cambios</>
                ) : (
                  <>Confirmar Programación</>
                )}
              </button>
            </div>
          </div>
        </ModalBody>
      </Modal>
    </div>
  );
};

export default ScheduleVisitPage;
