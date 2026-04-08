import React, { useState } from 'react';
import {
    useMonitoringStatistics,
    useAlerts,
    useMonitoringRules,
    useHealthCheckStatistics,
    useAcknowledgeAlert,
    useExecuteMonitoringRule
} from '../hooks/useMonitoring';
import {
    ShieldCheckIcon,
    ExclamationTriangleIcon,
    BellIcon,
    CpuChipIcon,
    PlayIcon,
    CheckCircleIcon,
    ClockIcon
} from '@heroicons/react/24/outline';

const MonitoringTab = () => {
    const { data: stats, isLoading: statsLoading } = useMonitoringStatistics();
    const { data: healthStats } = useHealthCheckStatistics();
    const { data: rulesData } = useMonitoringRules();
    const { data: alertsData } = useAlerts({ page_size: 10 });

    const acknowledgeMutation = useAcknowledgeAlert();
    const executeRuleMutation = useExecuteMonitoringRule();

    const rules = rulesData?.results || [];
    const alerts = alertsData?.results || [];

    const getStatusColor = (status) => {
        switch (status?.toLowerCase()) {
            case 'healthy': return 'text-emerald-500 bg-emerald-50 border-emerald-100';
            case 'unhealthy': return 'text-rose-500 bg-rose-50 border-rose-100';
            case 'warning': return 'text-amber-500 bg-amber-50 border-amber-100';
            default: return 'text-slate-500 bg-slate-50 border-slate-100';
        }
    };

    const getSeverityColor = (severity) => {
        switch (severity?.toLowerCase()) {
            case 'critical': return 'text-rose-600 bg-rose-50';
            case 'warning': return 'text-amber-600 bg-amber-50';
            case 'info': return 'text-blue-600 bg-blue-50';
            default: return 'text-slate-600 bg-slate-50';
        }
    };

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            {/* Overview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-white p-5 rounded-3xl border border-slate-100 shadow-sm flex items-center gap-4">
                    <div className="p-3 bg-indigo-50 rounded-2xl text-indigo-600">
                        <ShieldCheckIcon className="w-6 h-6" />
                    </div>
                    <div>
                        <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Estado Sistema</p>
                        <p className="text-lg font-black text-slate-800 tracking-tight">
                            {healthStats?.overall_status || 'Estable'}
                        </p>
                    </div>
                </div>

                <div className="bg-white p-5 rounded-3xl border border-slate-100 shadow-sm flex items-center gap-4">
                    <div className="p-3 bg-rose-50 rounded-2xl text-rose-600">
                        <ExclamationTriangleIcon className="w-6 h-6" />
                    </div>
                    <div>
                        <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Alertas Activas</p>
                        <p className="text-lg font-black text-slate-800 tracking-tight">
                            {stats?.active_alerts || 0}
                        </p>
                    </div>
                </div>

                <div className="bg-white p-5 rounded-3xl border border-slate-100 shadow-sm flex items-center gap-4">
                    <div className="p-3 bg-blue-50 rounded-2xl text-blue-600">
                        <BellIcon className="w-6 h-6" />
                    </div>
                    <div>
                        <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Reglas Activas</p>
                        <p className="text-lg font-black text-slate-800 tracking-tight">
                            {stats?.total_rules || 0}
                        </p>
                    </div>
                </div>

                <div className="bg-white p-5 rounded-3xl border border-slate-100 shadow-sm flex items-center gap-4">
                    <div className="p-3 bg-emerald-50 rounded-2xl text-emerald-600">
                        <CpuChipIcon className="w-6 h-6" />
                    </div>
                    <div>
                        <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Chequeos Salud</p>
                        <p className="text-lg font-black text-slate-800 tracking-tight">
                            {healthStats?.total_checks || 0}
                        </p>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                {/* Monitoring Rules */}
                <div className="bg-white rounded-3xl border border-slate-100 shadow-sm overflow-hidden flex flex-col">
                    <div className="px-6 py-4 border-b border-slate-50 bg-slate-50/30 flex justify-between items-center">
                        <h3 className="text-[11px] font-black text-slate-500 uppercase tracking-widest flex items-center gap-2">
                            <PlayIcon className="w-4 h-4" />
                            Reglas de Monitoreo
                        </h3>
                    </div>
                    <div className="divide-y divide-slate-50 max-h-[400px] overflow-y-auto custom-scrollbar">
                        {rules.length === 0 ? (
                            <p className="p-8 text-center text-slate-400 text-sm italic">No hay reglas configuradas</p>
                        ) : (
                            rules.map(rule => (
                                <div key={rule.id} className="p-4 hover:bg-slate-50 transition-colors flex justify-between items-center group">
                                    <div className="space-y-1">
                                        <p className="text-sm font-bold text-slate-800">{rule.name}</p>
                                        <div className="flex items-center gap-3">
                                            <span className={`px-2 py-0.5 rounded-lg text-[10px] font-black uppercase tracking-wider border ${getStatusColor(rule.last_execution_status)}`}>
                                                {rule.last_execution_status || 'Pendiente'}
                                            </span>
                                            <span className="text-[10px] font-bold text-slate-400 flex items-center gap-1">
                                                <ClockIcon className="w-3 h-3" />
                                                Cada {rule.interval_minutes} min
                                            </span>
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => executeRuleMutation.mutate(rule.id)}
                                        className="p-2 bg-indigo-50 text-indigo-600 rounded-xl opacity-0 group-hover:opacity-100 transition-all hover:bg-indigo-600 hover:text-white"
                                        title="Ejecutar ahora"
                                    >
                                        <PlayIcon className="w-4 h-4" />
                                    </button>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                {/* Recent Alerts */}
                <div className="bg-white rounded-3xl border border-slate-100 shadow-sm overflow-hidden flex flex-col">
                    <div className="px-6 py-4 border-b border-slate-50 bg-slate-50/30 flex justify-between items-center">
                        <h3 className="text-[11px] font-black text-slate-500 uppercase tracking-widest flex items-center gap-2">
                            <BellIcon className="w-4 h-4" />
                            Últimas Alertas
                        </h3>
                    </div>
                    <div className="divide-y divide-slate-50 max-h-[400px] overflow-y-auto custom-scrollbar">
                        {alerts.length === 0 ? (
                            <p className="p-8 text-center text-slate-400 text-sm italic">Sistema sin alertas recientes</p>
                        ) : (
                            alerts.map(alert => (
                                <div key={alert.id} className="p-4 hover:bg-slate-50 transition-colors flex justify-between items-start gap-4">
                                    <div className="space-y-1 flex-1">
                                        <div className="flex items-center gap-2">
                                            <span className={`px-2 py-0.5 rounded-lg text-[9px] font-black uppercase tracking-wider ${getSeverityColor(alert.severity)}`}>
                                                {alert.severity}
                                            </span>
                                            <p className="text-sm font-bold text-slate-800">{alert.title}</p>
                                        </div>
                                        <p className="text-xs text-slate-500 line-clamp-1">{alert.message}</p>
                                        <p className="text-[9px] font-bold text-slate-400 uppercase">
                                            {new Date(alert.created_at).toLocaleString('es-CL')}
                                        </p>
                                    </div>
                                    {!alert.acknowledged_at && (
                                        <button
                                            onClick={() => acknowledgeMutation.mutate(alert.id)}
                                            className="px-3 py-1.5 bg-slate-100 text-slate-600 rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-emerald-600 hover:text-white transition-all shrink-0"
                                        >
                                            OK
                                        </button>
                                    )}
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MonitoringTab;
