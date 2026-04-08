import React from 'react';
import {
    CheckCircleIcon,
    UserIcon,
    DocumentTextIcon,
    PhotoIcon,
    ClockIcon,
    ArrowPathIcon,
    ExclamationCircleIcon
} from '@heroicons/react/24/outline';

const IncidentTimeline = ({ timeline = [] }) => {

    if (!timeline || timeline.length === 0) {
        return (
            <div className="p-8 text-center text-slate-400 text-xs font-bold uppercase tracking-widest bg-slate-50 rounded-3xl border border-slate-100">
                No hay actividad registrada
            </div>
        );
    }

    const translateAction = (action) => {
        const map = {
            'created': 'CREADO',
            'updated': 'ACTUALIZADO',
            'closed': 'CERRADO',
            'status_changed': 'ESCALADO',
            'reopened': 'REABIERTO',
            'image_uploaded': 'IMAGEN ADJUNTA',
            'comment_added': 'COMENTARIO',
        };
        return map[action] || action.replace(/_/g, ' ').toUpperCase();
    };

    const getStageName = (stage) => {
        const stages = {
            'incidencia': 'INCIDENCIA',
            'reporte_visita': 'REPORTE DE VISITA',
            'calidad': 'CALIDAD',
            'proveedor': 'PROVEEDOR',
            'en_calidad': 'CALIDAD',
            'en_proveedor': 'PROVEEDOR'
        };
        return stages[stage] || stage?.toUpperCase() || 'INCIDENCIA';
    };

    const formatDescription = (event) => {
        if (event.action === 'closed') {
            const stage = event.metadata?.stage || 'incidencia';
            const userName = event.user ?
                (event.user.first_name ? `${event.user.first_name} ${event.user.last_name}` : event.user.username)
                : 'SISTEMA';
            return `CERRADO EN ${getStageName(stage)} POR ${userName.toUpperCase()}`;
        }

        if (!event.description) return '';
        // Remove [Motivo: ...] pattern for other events just in case
        return event.description.replace(/\[Motivo:.*?\]/g, '').trim();
    };

    const getIcon = (action) => {
        switch (action) {
            case 'created': return <CheckCircleIcon className="w-4 h-4 text-white" />;
            case 'updated': return <ArrowPathIcon className="w-4 h-4 text-white" />;
            case 'closed': return <CheckCircleIcon className="w-4 h-4 text-white" />;
            case 'image_uploaded': return <PhotoIcon className="w-4 h-4 text-white" />;
            default: return <ClockIcon className="w-4 h-4 text-white" />;
        }
    };

    const getColor = (action) => {
        switch (action) {
            case 'created': return 'bg-emerald-500 shadow-emerald-200';
            case 'closed': return 'bg-slate-900 shadow-slate-300';
            case 'escalated': return 'bg-rose-500 shadow-rose-200';
            default: return 'bg-indigo-500 shadow-indigo-200';
        }
    };

    return (
        <div className="relative pl-4 border-l border-slate-200 space-y-8 py-2">
            {timeline.map((event, index) => (
                <div key={event.id || index} className="relative group">
                    {/* Dot */}
                    <div className={`absolute -left-[21px] top-1 w-8 h-8 rounded-full flex items-center justify-center shadow-lg border-2 border-white transition-transform group-hover:scale-110 ${getColor(event.action)}`}>
                        {getIcon(event.action)}
                    </div>

                    <div className="pl-6">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-1">
                            <span className="text-[10px] font-black uppercase tracking-widest text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-md self-start">
                                {translateAction(event.action)}
                            </span>
                            <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider mt-1 sm:mt-0">
                                {new Date(event.created_at).toLocaleString()}
                            </span>
                        </div>


                        <p className="text-sm font-medium text-slate-700 leading-snug mb-2">
                            {formatDescription(event)}
                        </p>
                    </div>
                </div>
            ))}
        </div>
    );
};

export default IncidentTimeline;
