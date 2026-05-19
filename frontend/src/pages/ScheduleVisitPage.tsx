import React, { useState, useMemo, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { sapAPI, visitReportsAPI } from '../services/api';
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
  TrashIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { motion } from 'framer-motion';

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
    <div className="bg-slate-50 rounded-2xl p-6 border border-slate-200">
      <div className="flex items-center justify-between mb-6">
        <h4 className="text-sm font-black text-slate-800 uppercase tracking-widest">
          {monthNames[currentMonth.getMonth()]} {currentMonth.getFullYear()}
        </h4>
        <div className="flex gap-1">
          <button type="button" onClick={prevMonth} className="p-1.5 hover:bg-slate-200 rounded-md transition-colors"><ChevronLeftIcon className="w-5 h-5 text-slate-600"/></button>
          <button type="button" onClick={nextMonth} className="p-1.5 hover:bg-slate-200 rounded-md transition-colors"><ChevronRightIcon className="w-5 h-5 text-slate-600"/></button>
        </div>
      </div>
      <div className="grid grid-cols-7 gap-1 text-center mb-3">
        {['Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sá', 'Do'].map(d => <div key={d} className="text-[11px] font-bold text-slate-400">{d}</div>)}
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
              className={`h-10 w-full rounded-xl text-sm font-bold transition-all relative flex items-center justify-center
                ${isSelected ? 'bg-blue-600 text-white shadow-md shadow-blue-200' : 
                  isToday ? 'bg-blue-50 text-blue-600 border border-blue-200' : 
                  'hover:bg-slate-200 text-slate-700'}`}
            >
              {i + 1}
              {visitsThisDay.length > 0 && (
                <span className={`absolute -top-1 -right-1 min-w-[16px] h-4 px-1 rounded-full bg-orange-500 text-white flex items-center justify-center text-[9px] font-black shadow-md border border-white`}>
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
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [isEditing, setIsEditing] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<'form' | 'calendar'>('form');
  const [selectedTechnicianFilter, setSelectedTechnicianFilter] = useState<string>('all');

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
  });
  
  const selectedTechnicianFilterStr = selectedTechnicianFilter.toString();
  const pendingVisits = useMemo(() => {
    const raw = allVisitsData?.results || (Array.isArray(allVisitsData) ? allVisitsData : []);
    if (selectedTechnicianFilterStr === 'all') return raw;
    return raw.filter((v: any) => v.technician_id?.toString() === selectedTechnicianFilterStr);
  }, [allVisitsData, selectedTechnicianFilterStr]);

  const visitsForSelectedDate = useMemo(() => {
    return pendingVisits.filter(v => {
      if (!v.visit_date) return false;
      const vDate = new Date(v.visit_date);
      return vDate.toDateString() === selectedDate.toDateString();
    });
  }, [pendingVisits, selectedDate]);

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
    }));
    setCustomerSearch(customer.card_name);
    setCustomers([]);

    try {
      const detailRes = await sapAPI.getCustomerDetails(customer.card_code);
      if (detailRes.data) {
        setFormData(prev => ({
          ...prev,
          salesperson: detailRes.data.salesperson_name || '',
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
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        project_id: '',
        project_name: '',
      }));
    }
  };

  const resetForm = () => {
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
      visit_date: new Date().toLocaleDateString('en-CA'),
      visit_time: '09:00',
    });
    setCustomerSearch('');
    setIsEditing(null);
    setSelectedDate(new Date());
  };

  const deleteVisitMutation = useMutation({
    mutationFn: (id: number) => visitReportsAPI.delete(id),
    onSuccess: () => {
      toast.success('Programación eliminada con éxito');
      queryClient.invalidateQueries({ queryKey: ['visit-reports'] });
      resetForm();
    },
    onError: () => {
      toast.error('Error al eliminar la programación');
    }
  });

  const handleDeleteVisit = (e: React.MouseEvent, id: number) => {
    e.stopPropagation();
    if (window.confirm('¿Está seguro de que desea eliminar esta programación? Se eliminará de la agenda y de los reportes.')) {
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
    });
    setCustomerSearch(visit.client_name || '');
    setIsEditing(visit.id);
    setSelectedDate(vDate);
    setActiveTab('form');
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
      toast.success(isEditing ? 'Visita reprogramada' : 'Visita programada exitosamente');
      queryClient.invalidateQueries({ queryKey: ['visit-reports'] });
      resetForm();
      setActiveTab('calendar');
    },
    onError: (err: any) => {
      toast.error('Error al guardar: ' + (err.response?.data?.error || err.message));
    }
  });

  return (
    <div className="max-w-[1400px] mx-auto pb-12 pt-2 px-4">
      {/* HEADER COMPACTO */}
      <motion.div 
        initial={{ y: -10, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="sticky top-2 z-40 flex items-center justify-between mb-4 p-3 rounded-2xl bg-white border border-slate-200 shadow-sm"
      >
        <div className="flex items-center gap-3">
           <button onClick={() => navigate('/quick-actions')} className="p-2.5 hover:bg-slate-100 rounded-xl transition-colors text-slate-600">
             <ArrowLeftIcon className="w-5 h-5"/>
           </button>
           <div className="flex items-center gap-3">
             <div className="bg-blue-600 p-2 rounded-lg shadow-md shadow-blue-200">
               <CalendarIcon className="w-5 h-5 text-white"/>
             </div>
             <div>
               <h1 className="text-lg font-black text-slate-900 flex items-center gap-2 uppercase tracking-tight">
                 Programar Visita
               </h1>
               <p className="text-[10px] text-slate-500 font-bold uppercase tracking-[0.2em]">Asignación proactiva de tareas a técnicos</p>
             </div>
           </div>
        </div>
      </motion.div>

      {/* Selector de pestañas para móviles */}
      <div className="flex lg:hidden bg-slate-100 p-1 rounded-xl mb-4 border border-slate-200">
        <button
          onClick={() => setActiveTab('form')}
          className={`flex-1 py-2 text-xs font-black uppercase tracking-wider rounded-lg transition-all ${activeTab === 'form' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-800'}`}
        >
          Programar
        </button>
        <button
          onClick={() => setActiveTab('calendar')}
          className={`flex-1 py-2 text-xs font-black uppercase tracking-wider rounded-lg transition-all ${activeTab === 'calendar' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-800'}`}
        >
          Ver Agenda ({visitsForSelectedDate.length})
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 lg:gap-8">
        
        {/* PANEL IZQUIERDO: Calendario y Visitas del Día (4 Columnas) */}
        <div className={`lg:col-span-4 flex flex-col gap-6 ${activeTab === 'calendar' ? 'flex' : 'hidden lg:flex'}`}>
          <div className="flex flex-col gap-2 bg-slate-50 border border-slate-200 rounded-2xl p-4">
            <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest flex items-center gap-1.5">
              <UserIcon className="w-3.5 h-3.5 text-blue-600"/>
              Filtrar por Técnico:
            </label>
            <select
              value={selectedTechnicianFilter}
              onChange={(e) => setSelectedTechnicianFilter(e.target.value)}
              className="w-full px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-xs font-bold text-slate-700 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all outline-none appearance-none cursor-pointer"
            >
              <option value="all">-- Todos los Técnicos --</option>
              {technicians?.map((t: any) => (
                <option key={t.id} value={t.id.toString()}>{t.name}</option>
              ))}
            </select>
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
          
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm flex-1 flex flex-col min-h-[400px]">
            <div className="flex items-center justify-between mb-6">
              <h5 className="text-xs font-black text-slate-800 uppercase tracking-widest flex items-center gap-2">
                <ClockIcon className="w-4 h-4 text-blue-600"/>
                Visitas del Día
              </h5>
              <span className="text-[10px] font-bold text-blue-600 bg-blue-50 border border-blue-100 px-3 py-1 rounded-full">
                {visitsForSelectedDate.length}
              </span>
            </div>
            
            <div className="flex flex-col gap-3 overflow-y-auto pr-2 custom-scrollbar flex-1">
              {visitsForSelectedDate.length > 0 ? (
                visitsForSelectedDate.map(v => (
                  <div 
                    key={v.id} 
                    onClick={() => handleEditVisit(v)}
                    className={`p-4 rounded-xl border-2 transition-all cursor-pointer ${isEditing === v.id ? 'bg-blue-50 border-blue-400 shadow-md shadow-blue-100' : 'bg-white border-slate-100 hover:border-blue-300 hover:shadow-md'}`}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-[11px] font-black text-blue-700 bg-blue-100 px-2 py-0.5 rounded-md border border-blue-200">
                          Programada
                        </span>
                        <button 
                          onClick={(e) => handleDeleteVisit(e, v.id)} 
                          className="p-1 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-all"
                          title="Eliminar Programación"
                        >
                          <TrashIcon className="w-3.5 h-3.5"/>
                        </button>
                      </div>
                      <span className="text-[10px] font-bold text-slate-400 uppercase bg-slate-50 px-2 py-0.5 rounded">{v.report_number || `RV-${v.id}`}</span>
                    </div>
                    <p className="text-sm font-bold text-slate-800 line-clamp-1">{v.client_name}</p>
                    <p className="text-[11px] font-medium text-slate-500 truncate flex items-center gap-1.5 mt-1">
                      <BuildingOfficeIcon className="w-3.5 h-3.5"/> {v.project_name || 'Sin obra'}
                    </p>
                    <div className="mt-3 pt-3 border-t border-slate-100 flex items-center gap-2">
                      <div className="w-6 h-6 rounded-full bg-slate-100 flex items-center justify-center border border-slate-200"><UserIcon className="w-3.5 h-3.5 text-slate-600"/></div>
                      <span className="text-[11px] font-bold text-slate-700">{v.technician || 'Sin asignar'}</span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-slate-400 gap-3">
                  <div className="w-12 h-12 rounded-full bg-slate-50 flex items-center justify-center border border-slate-100">
                    <CalendarIcon className="w-6 h-6 text-slate-300" />
                  </div>
                  <p className="text-xs font-bold text-slate-500">No hay visitas programadas</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* PANEL DERECHO: Formulario (8 Columnas) */}
        <div className={`lg:col-span-8 bg-white p-5 lg:p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col h-fit ${activeTab === 'form' ? 'block' : 'hidden lg:block'}`}>
          <div className="flex items-center justify-between mb-5 pb-3 border-b border-slate-100">
            <h4 className="text-sm font-black text-blue-600 uppercase tracking-widest flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-blue-600"></span>
              {isEditing ? 'Reprogramar Visita' : 'Nueva Programación'}
            </h4>
            {isEditing && (
              <button 
                onClick={resetForm}
                className="text-[10px] font-black text-rose-600 hover:text-white hover:bg-rose-500 px-4 py-2 rounded-xl border border-rose-200 transition-all uppercase tracking-widest bg-rose-50"
              >
                Cancelar Edición
              </button>
            )}
          </div>

          <div className="space-y-5">
            {/* Cliente */}
            <div className="relative z-50">
              <label className="text-[11px] font-black text-slate-500 uppercase tracking-widest mb-2 block">1. Seleccionar Cliente (SAP)</label>
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  type="text"
                  value={customerSearch}
                  onChange={(e) => handleCustomerSearch(e.target.value)}
                  placeholder="Buscar por RUT o Nombre..."
                  className="w-full pl-12 pr-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-bold text-slate-800 focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all outline-none"
                />
                {isSearchingCustomers && (
                  <div className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                )}
              </div>
              
              {/* Dropdown de búsqueda */}
              {customers.length > 0 && (
                <div className="absolute z-50 w-full mt-2 bg-white rounded-xl shadow-[0_10px_40px_-10px_rgba(0,0,0,0.1)] border border-slate-200 max-h-64 overflow-y-auto">
                  {customers.map((c, idx) => (
                    <button
                      key={idx}
                      onClick={() => selectCustomer(c)}
                      className="w-full text-left px-5 py-4 hover:bg-blue-50 border-b border-slate-100 last:border-0 transition-colors group"
                    >
                      <div className="text-sm font-bold text-slate-800 group-hover:text-blue-700">{c.card_name}</div>
                      <div className="text-[11px] font-bold text-slate-500 font-mono mt-1">{c.card_code}</div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Obra */}
            <div className="relative z-40">
              <label className="text-[11px] font-black text-slate-500 uppercase tracking-widest mb-2 flex items-center justify-between">
                <span>2. Seleccionar Obra</span>
                {loadingProjects && <span className="text-blue-500 flex items-center gap-1"><div className="w-3 h-3 border border-blue-500 border-t-transparent rounded-full animate-spin"></div> Cargando...</span>}
              </label>
              <select
                value={formData.project_id}
                onChange={selectProject}
                disabled={!formData.client_rut || loadingProjects}
                className="w-full px-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-bold text-slate-800 focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all outline-none disabled:opacity-50 disabled:cursor-not-allowed appearance-none"
              >
                <option value="">-- Seleccionar Obra --</option>
                {projects?.map((p: any) => (
                  <option key={p.proyecto} value={p.proyecto}>{p.obra} ({p.proyecto})</option>
                ))}
              </select>
            </div>

            {/* Técnico y Fecha Visita en la misma línea */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 relative z-30">
              <div>
                <label className="text-[11px] font-black text-slate-500 uppercase tracking-widest mb-2 block">3. Asignar Técnico</label>
                <select
                  value={formData.technician_id}
                  onChange={(e) => setFormData(prev => ({...prev, technician_id: e.target.value}))}
                  className="w-full px-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-bold text-slate-800 focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all outline-none appearance-none"
                >
                  <option value="">-- Seleccionar Técnico --</option>
                  {technicians?.map((t: any) => (
                    <option key={t.id} value={t.id}>{t.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-[11px] font-black text-slate-500 uppercase tracking-widest mb-2 block">4. Fecha Visita</label>
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
                  className="w-full px-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-bold text-slate-800 focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all outline-none"
                />
              </div>
            </div>

            {/* Datos autocompletados (Info) */}
            {formData.project_id && (
              <div className="bg-slate-50/50 p-5 rounded-xl border border-slate-200 grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
                <div>
                  <span className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1.5">Dirección / Comuna</span>
                  <span className="text-sm font-bold text-slate-700 flex items-center gap-1.5">
                    <MapPinIcon className="w-4 h-4 text-blue-500"/>
                    <span className="truncate">{formData.address || 'Sin dirección'} {formData.commune ? `- ${formData.commune}` : ''}</span>
                  </span>
                </div>
                <div>
                  <span className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1.5">Vendedor Asignado</span>
                  <span className="text-sm font-bold text-slate-700 flex items-center gap-1.5">
                    <UserIcon className="w-4 h-4 text-emerald-500"/>
                    <span className="truncate">{formData.salesperson || 'Sin vendedor'}</span>
                  </span>
                </div>
              </div>
            )}

            <div className="pt-6 mt-6 border-t border-slate-100">
              <button
                onClick={() => saveMutation.mutate(formData)}
                disabled={!formData.client_rut || !formData.technician_id || saveMutation.isPending}
                className="w-full py-4 bg-blue-600 text-white rounded-xl text-sm font-black uppercase tracking-widest shadow-lg shadow-blue-600/30 hover:bg-blue-700 hover:shadow-blue-600/40 hover:-translate-y-0.5 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0 flex items-center justify-center gap-2"
              >
                {saveMutation.isPending ? (
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                ) : isEditing ? (
                  <>Guardar Reprogramación</>
                ) : (
                  <><PlusIcon className="w-5 h-5"/> Confirmar Programación</>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScheduleVisitPage;
