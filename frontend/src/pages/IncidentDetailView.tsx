import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { incidentsAPI } from '../services/api';
import IncidentAttachments from '../components/IncidentAttachments';
import IncidentTimeline from '../components/IncidentTimeline';
import {
  ArrowLeftIcon,
  UserIcon,
  BuildingOfficeIcon,
  TagIcon,
  ClockIcon,
  CalendarIcon,
  ExclamationTriangleIcon,
  DocumentTextIcon,
  MapPinIcon,
  BriefcaseIcon,
  PencilSquareIcon,
  XMarkIcon,
  CheckBadgeIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';

const IncidentDetail = ({ incidentId, isModal, onClose }) => {
  const { id: paramId } = useParams();
  const navigate = useNavigate();

  const id = incidentId || paramId;

  const { data: incidentResponse, isLoading, error, refetch } = useQuery({
    queryKey: ['incident', id],
    queryFn: async () => {
      const response = await incidentsAPI.get(id);
      return response.data || response;
    },
    enabled: !!id,
  });

  const incident = incidentResponse;

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-24 space-y-4">
        <div className="w-14 h-14 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
        <p className="text-slate-400 font-black uppercase tracking-[0.3em] text-[10px]">Sincronizando Expediente...</p>
      </div>
    );
  }

  if (error || !incident) {
    return (
      <div className="text-center py-20 bg-white m-10 rounded-[3rem] border border-slate-100 shadow-xl">
        <div className="w-20 h-20 bg-rose-50 text-rose-500 rounded-full flex items-center justify-center mx-auto mb-6">
          <ExclamationTriangleIcon className="w-10 h-10" />
        </div>
        <h3 className="text-2xl font-black text-slate-900 mb-2 uppercase">Error de Lectura</h3>
        <p className="text-slate-500 text-sm mb-10 max-w-xs mx-auto">No se pudo establecer conexión con el registro remoto de esta incidencia.</p>
        <button
          onClick={() => isModal ? onClose() : navigate('/incidents')}
          className="px-10 py-4 bg-slate-900 text-white rounded-2xl text-[10px] font-black uppercase tracking-widest hover:bg-indigo-600 transition-all shadow-lg"
        >
          {isModal ? 'Cerrar Ventana' : 'Regresar al Tablero'}
        </button>
      </div>
    );
  }

  const getPriorityBadge = (prio) => {
    const styles = {
      'alta': 'bg-rose-50 text-rose-600 border-rose-100',
      'critica': 'bg-rose-600 text-white border-rose-600 shadow-lg shadow-rose-200',
      'media': 'bg-amber-50 text-amber-600 border-amber-100',
      'baja': 'bg-emerald-50 text-emerald-600 border-emerald-100',
    }[prio?.toLowerCase()] || 'bg-slate-50 text-slate-400 border-slate-100';

    return (
      <span className={`px-4 py-1.5 rounded-full border text-[10px] font-black uppercase tracking-widest ${styles}`}>
        Prioridad {prio || 'No Definida'}
      </span>
    );
  };

  const StatusChip = ({ status }) => {
    const isCancelled = status?.toLowerCase() === 'cancelada';
    return (
      <div className={`flex items-center gap-2 px-4 py-2 ${isCancelled ? 'bg-slate-100 border-slate-200' : 'bg-indigo-50/50 border-indigo-100'} border rounded-2xl`}>
        <div className={`w-2 h-2 ${isCancelled ? 'bg-slate-400' : 'bg-indigo-500 animate-pulse shadow-sm shadow-indigo-400'} rounded-full`}></div>
        <span className={`text-[12px] font-black ${isCancelled ? 'text-slate-500' : 'text-indigo-700'} uppercase tracking-widest leading-none`}>{status || 'PENDIENTE'}</span>
      </div>
    );
  };

  return (
    <div className={`bg-white animate-fade-in ${isModal ? 'h-full flex flex-col' : 'min-h-screen p-10 pb-24 bg-slate-50'}`}>

      {/* HEADER SECTION */}
      <div className={`p-6 lg:p-8 border-b border-slate-100 flex flex-col md:flex-row justify-between items-start md:items-center gap-6 ${isModal ? 'bg-slate-50/30' : 'bg-white rounded-[3rem] shadow-xl border-white mb-6 relative overflow-hidden'}`}>
        {!isModal && <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500"></div>}
        <div className="flex items-center gap-6 relative z-10">
          <div className="w-20 h-20 bg-white rounded-2xl shadow-xl shadow-indigo-100 border border-slate-100 flex items-center justify-center relative group overflow-hidden transition-transform hover:scale-105 active:scale-95 cursor-default">
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/10 to-purple-500/10"></div>
            <DocumentTextIcon className="w-8 h-8 text-indigo-600 relative z-10" />
          </div>
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              <StatusChip status={incident.estado} />
              {getPriorityBadge(incident.prioridad)}
            </div>
            <h1 className="text-4xl font-black text-slate-900 tracking-tighter uppercase italic leading-none pr-4">
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">{incident.code}</span>
            </h1>
            <div className="flex items-center gap-2 text-slate-400">
              <CalendarIcon className="w-3.5 h-3.5" />
              <span className="text-[10px] font-bold uppercase tracking-[0.2em]">
                REGISTRO EFECTUADO EL {new Date(incident.created_at).toLocaleDateString('es-ES', { day: '2-digit', month: 'long', year: 'numeric' })}
              </span>
            </div>
          </div>
        </div>

        <div className="flex gap-3 relative z-10">
          {incident.estado?.toLowerCase() !== 'cancelada' && (
            <button
              onClick={() => navigate(`/incidents/${incident.id}/edit`)}
              className="px-6 py-3 bg-white border border-slate-200 rounded-xl text-slate-600 hover:text-indigo-600 hover:border-indigo-200 transition-all flex items-center gap-2 shadow-sm group hover:shadow-md"
            >
              <PencilSquareIcon className="w-4 h-4 group-hover:rotate-12 transition-transform" />
              <span className="text-[10px] font-black uppercase tracking-widest">Editar Caso</span>
            </button>
          )}
          {isModal ? (
            <button
              onClick={onClose}
              className="px-6 py-3 bg-slate-900 text-white rounded-xl shadow-lg shadow-slate-200 hover:bg-rose-500 transition-all flex items-center gap-2"
            >
              <XMarkIcon className="w-4 h-4" />
              <span className="text-[10px] font-black uppercase tracking-widest">Cerrar</span>
            </button>
          ) : (
            <button
              onClick={() => navigate('/incidents')}
              className="px-6 py-3 bg-slate-900 text-white rounded-xl shadow-lg shadow-slate-200 hover:bg-indigo-600 transition-all flex items-center gap-2"
            >
              <ArrowLeftIcon className="w-4 h-4" />
              <span className="text-[10px] font-black uppercase tracking-widest">Regresar</span>
            </button>
          )}
        </div>
      </div>

      {/* CONTENT LAYOUT */}
      <div className={`flex-1 ${isModal ? 'overflow-y-auto p-6 lg:p-12' : 'max-w-7xl mx-auto space-y-12'}`}>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">

          {/* PRIMARY DATA COLUMN */}
          <div className="lg:col-span-2 space-y-12">

            {/* DESCRIPTION CARD */}
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <div className="w-10 h-1 bg-indigo-600 rounded-full"></div>
                <h4 className="text-[11px] font-black text-slate-400 uppercase tracking-[0.4em]">Reporte de Situación</h4>
              </div>
              <div className="bg-slate-50 border border-slate-100 rounded-[2.5rem] p-8 relative group">
                <div className="absolute top-6 right-8 opacity-10 group-hover:opacity-20 transition-opacity">
                  <ShieldCheckIcon className="w-16 h-16 text-slate-900" />
                </div>
                <p className="text-lg font-medium text-slate-800 leading-relaxed italic pr-10">
                  "{incident.descripcion || 'El informante no ha ingresado una descripción detallada del evento.'}"
                </p>
              </div>
            </div>

            {/* RESOLUTION SECTION (IF CLOSED OR CANCELLED) */}
            {(incident.estado?.toLowerCase() === 'cerrado' || incident.estado?.toLowerCase() === 'cancelada') && (
              <div className="space-y-4">
                <div className="flex items-center gap-4">
                  <div className={`w-10 h-1 ${incident.estado?.toLowerCase() === 'cancelada' ? 'bg-slate-400' : 'bg-emerald-500'} rounded-full`}></div>
                  <h4 className="text-[11px] font-black text-slate-400 uppercase tracking-[0.4em]">Resolución del Caso</h4>
                </div>
                <div className={`${incident.estado?.toLowerCase() === 'cancelada' ? 'bg-slate-100 border-slate-200' : 'bg-emerald-50 border-emerald-100'} border rounded-[2.5rem] p-8`}>
                  <p className={`text-md font-bold ${incident.estado?.toLowerCase() === 'cancelada' ? 'text-slate-600' : 'text-emerald-800'} leading-relaxed`}>
                    {incident.closure_summary || 'No se registró un resumen de cierre.'}
                  </p>
                  {incident.closed_at && (
                    <p className="mt-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">
                      Finalizado el {new Date(incident.closed_at).toLocaleDateString('es-ES', { day: '2-digit', month: 'long', year: 'numeric' })} por {incident.closed_by?.full_name || incident.closed_by?.username || 'Sistema'}
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* PRODUCT/TECH INFO */}
            <div className="space-y-6">
              <h4 className="text-[11px] font-black text-slate-400 uppercase tracking-[0.4em] flex items-center gap-3 px-2">
                <ShieldCheckIcon className="w-5 h-5 text-indigo-500" /> DETALLES DE PRODUCTO
              </h4>
              <div className="bg-white border border-slate-100 rounded-[2.5rem] p-8 shadow-xl shadow-slate-100/50 space-y-6">
                <div>
                  <p className="text-[10px] font-black text-slate-300 uppercase tracking-widest mb-1.5 ml-1">CATEGORÍA ASIGNADA</p>
                  <div className="flex flex-wrap items-center gap-3">
                    <div className="px-4 py-2 bg-indigo-600 text-white rounded-xl text-[10px] font-black uppercase tracking-widest">
                      {incident.categoria?.replace(/_/g, ' ') || 'GENERAL'}
                    </div>
                    {incident.subcategoria && (
                      <div className="px-4 py-2 bg-indigo-50 text-indigo-600 border border-indigo-100 rounded-xl text-[10px] font-black uppercase tracking-widest">
                        {incident.subcategoria}
                      </div>
                    )}
                  </div>
                </div>
                <div>
                  <p className="text-[10px] font-black text-slate-300 uppercase tracking-widest mb-2.5 ml-1">ORIGEN Y RESPONSABLE</p>
                  <div className="flex items-center gap-3 bg-slate-50 p-4 rounded-2xl border border-slate-100">
                    <BriefcaseIcon className="w-6 h-6 text-slate-400" />
                    <div>
                      <p className="text-xs font-black text-slate-800 uppercase leading-none mb-1">{incident.provider || 'POLIFUSION'}</p>
                      <p className="text-[10px] font-bold text-indigo-600 uppercase tracking-widest">RESP: {incident.responsable}</p>
                    </div>
                  </div>
                </div>
                <div className="grid grid-cols-1 gap-4 pt-4 border-t border-slate-50">
                  <div className="flex justify-between items-center">
                    <p className="text-[10px] font-black text-slate-300 uppercase tracking-widest">ASISTENCIA COMERCIAL</p>
                    <p className="text-xs font-bold text-slate-600 uppercase">{incident.salesperson || 'ASIGNACIÓN PENDIENTE'}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* EVIDENCIAS SECTION */}
            <div className="space-y-8 pb-12">
              <div className="flex items-center justify-between px-2">
                <h4 className="text-[11px] font-black text-slate-400 uppercase tracking-[0.4em]">EVIDENCIAS Y ADJUNTOS</h4>
                <div className="h-px flex-1 mx-8 bg-slate-100"></div>
              </div>
              <div className="bg-white border border-slate-100 rounded-[2.5rem] p-4 lg:p-8 shadow-sm">
                <IncidentAttachments incidentId={parseInt(id)} />
              </div>
            </div>
          </div>

          {/* SIDEBAR METADATA COLUMN */}
          <div className="space-y-8">
            {/* PROJECT CARD (BLUE BOX) */}
            <div className="bg-gradient-to-br from-slate-900 to-indigo-950 rounded-3xl p-8 text-white shadow-2xl shadow-indigo-200">
              <div className="flex items-center gap-3 mb-8 opacity-60">
                <BuildingOfficeIcon className="w-4 h-4" />
                <h5 className="text-[10px] font-black uppercase tracking-[0.4em]">FICHA DE PROYECTO</h5>
              </div>

              <div className="space-y-6">
                <div>
                  <p className="text-[10px] font-black text-indigo-300 uppercase tracking-widest mb-1.5">ENTIDAD PRINCIPAL</p>
                  <p className="text-lg font-black text-white uppercase tracking-tight leading-tight">{incident.cliente}</p>
                </div>

                <div>
                  <p className="text-[10px] font-black text-indigo-300 uppercase tracking-widest mb-2.5">LOCALIZACIÓN / PROYECTO</p>
                  <div className="flex items-start gap-3 bg-white/5 p-4 rounded-2xl border border-white/5">
                    <MapPinIcon className="w-5 h-5 text-indigo-300 mt-1" />
                    <div>
                      <p className="text-sm font-bold text-white uppercase leading-none mb-1.5">{incident.obra}</p>
                      <p className="text-xs font-semibold text-indigo-200/80 uppercase tracking-widest">{incident.project_code ? `Proyecto SAP: ${incident.project_code}` : 'Proyecto no especificado'}</p>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 pt-4 border-t border-white/10">
                  <div>
                    <p className="text-[10px] font-black text-indigo-300 uppercase tracking-widest mb-1">ID ERP (SAP)</p>
                    <p className="text-xs font-mono font-black text-white">{incident.customer_code || '---'}</p>
                  </div>
                  <div>
                    <p className="text-[10px] font-black text-indigo-300 uppercase tracking-widest mb-1">FOLIO SAP</p>
                    <p className="text-xs font-mono font-black text-slate-400">{incident.sap_doc_num || incident.sap_call_id || 'SIN VÍNCULO'}</p>
                  </div>
                </div>
              </div>

              <div className="mt-8 pt-6 border-t border-white/10 grid grid-cols-2 gap-4">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <CalendarIcon className="w-4 h-4 text-indigo-300" />
                    <p className="text-[10px] font-black text-indigo-300 uppercase tracking-widest">Fecha Reporte</p>
                  </div>
                  <p className="text-sm font-black text-white uppercase tracking-tight">{incident.fecha_deteccion || 'S.F.'}</p>
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <ClockIcon className="w-4 h-4 text-indigo-300" />
                    <p className="text-[10px] font-black text-indigo-300 uppercase tracking-widest">Hora</p>
                  </div>
                  <p className="text-sm font-black text-white uppercase tracking-tight">{incident.hora_deteccion || '---'}</p>
                </div>
              </div>
            </div>



            {/* TIMELINE */}
            <div className="bg-white border border-slate-100 rounded-[2.5rem] p-8 shadow-sm">
              <div className="flex items-center gap-3 mb-6">
                <TagIcon className="w-5 h-5 text-slate-400" />
                <h5 className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Actividad Reciente</h5>
              </div>
              <IncidentTimeline timeline={incident.timeline} />
            </div>


          </div>
        </div>
      </div>
    </div>
  );
};

export default IncidentDetail;
