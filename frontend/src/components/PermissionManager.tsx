import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import { useNotifications } from '../hooks/useNotifications';
import {
    ShieldCheckIcon,
    ComputerDesktopIcon,
    ArrowPathIcon,
    CheckIcon,
    ClipboardDocumentListIcon,
    CalendarDaysIcon,
    UsersIcon,
    ClipboardDocumentCheckIcon,
    DocumentArrowDownIcon,
    EnvelopeIcon,
    PencilSquareIcon,
    TrashIcon,
    Cog6ToothIcon,
    MagnifyingGlassCircleIcon,
    UserGroupIcon,
} from '@heroicons/react/24/outline';
import {
    PERMISSION_LABELS,
    PERMISSION_DESCRIPTIONS,
    PERMISSION_CATEGORIES,
    PAGE_LABELS,
} from '../utils/permissionUtils';

// Icon map for each permission key
const PERMISSION_ICONS = {
    'can_manage_users':           UsersIcon,
    'can_manage_visits':          PencilSquareIcon,
    'can_view_reports':           ClipboardDocumentListIcon,
    'can_delete_visits':          TrashIcon,
    'can_sign_reports':           ClipboardDocumentCheckIcon,
    'can_send_reports':           EnvelopeIcon,
    'can_export_pdf':             DocumentArrowDownIcon,
    'can_schedule_visits':        CalendarDaysIcon,
    'can_view_all_technicians':   UserGroupIcon,
    'can_access_admin':           ShieldCheckIcon,
    'can_view_audit_logs':        MagnifyingGlassCircleIcon,
    'can_manage_system_settings': Cog6ToothIcon,
};

// Icon map for pages
const PAGE_ICONS = {
    'dashboard':      ClipboardDocumentListIcon,
    'visit-reports':  ClipboardDocumentListIcon,
    'schedule-visit': CalendarDaysIcon,
    'users':          UsersIcon,
    'audit':          MagnifyingGlassCircleIcon,
};

const ROLE_COLORS = {
    admin:            'from-rose-500 to-rose-700',
    management:       'from-purple-500 to-purple-700',
    technical_service:'from-blue-500 to-blue-700',
    quality:          'from-emerald-500 to-emerald-700',
    supervisor:       'from-amber-500 to-amber-700',
    analyst:          'from-indigo-500 to-indigo-700',
    customer_service: 'from-pink-500 to-pink-700',
    provider:         'from-slate-500 to-slate-700',
};

const ROLE_BG = {
    admin:            'bg-rose-50 text-rose-700 border-rose-200',
    management:       'bg-purple-50 text-purple-700 border-purple-200',
    technical_service:'bg-blue-50 text-blue-700 border-blue-200',
    quality:          'bg-emerald-50 text-emerald-700 border-emerald-200',
    supervisor:       'bg-amber-50 text-amber-700 border-amber-200',
    analyst:          'bg-indigo-50 text-indigo-700 border-indigo-200',
    customer_service: 'bg-pink-50 text-pink-700 border-pink-200',
    provider:         'bg-slate-50 text-slate-700 border-slate-200',
};

const PermissionToggle = ({ enabled, saving, onClick }) => (
    <button
        type="button"
        onClick={onClick}
        disabled={saving}
        className={`relative flex-shrink-0 w-12 h-6 rounded-full transition-all duration-300 focus:outline-none
            ${enabled ? 'bg-blue-600 shadow-md shadow-blue-200' : 'bg-slate-200'}
            ${saving ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
    >
        {saving ? (
            <span className="absolute inset-0 flex items-center justify-center">
                <ArrowPathIcon className="w-3 h-3 text-white animate-spin" />
            </span>
        ) : (
            <span className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full shadow-sm transform transition-transform duration-300
                ${enabled ? 'translate-x-6' : 'translate-x-0'}`}
            />
        )}
    </button>
);

const PermissionManager = () => {
    const { showSuccess, showError } = useNotifications();
    const queryClient = useQueryClient();
    const [selectedRole, setSelectedRole] = useState(null);
    const [savingKey, setSavingKey] = useState(null);

    const { data: rolesData, isLoading } = useQuery({
        queryKey: ['role-permissions'],
        queryFn: async () => {
            const response = await api.get('/users/permissions/roles/');
            return response.data;
        },
        staleTime: 30000,
    });

    React.useEffect(() => {
        if (rolesData && rolesData.length > 0 && !selectedRole) {
            const adminRole = rolesData.find(r => r.role === 'admin');
            setSelectedRole(adminRole || rolesData[0]);
        }
    }, [rolesData]); // eslint-disable-line react-hooks/exhaustive-deps

    const updateMutation = useMutation({
        mutationFn: async ({ role, permissions, accessible_pages }) => {
            await api.patch(`/users/permissions/roles/${role}/`, { permissions, accessible_pages });
        },
        onSuccess: () => {
            queryClient.invalidateQueries(['role-permissions']);
            showSuccess('Permisos actualizados');
            setSavingKey(null);
        },
        onError: (error) => {
            showError('Error al actualizar: ' + (error.response?.data?.message || error.message));
            setSavingKey(null);
        },
    });

    const togglePermission = (permKey) => {
        if (!selectedRole) return;
        setSavingKey(permKey);
        const currentPerms = { ...selectedRole.permissions, [permKey]: !selectedRole.permissions[permKey] };
        const updatedRole = { ...selectedRole, permissions: currentPerms };
        setSelectedRole(updatedRole);
        updateMutation.mutate({ role: selectedRole.role, permissions: currentPerms, accessible_pages: selectedRole.accessible_pages });
    };

    const togglePage = (pageKey) => {
        if (!selectedRole) return;
        setSavingKey('page_' + pageKey);
        const currentPages = selectedRole.accessible_pages.includes(pageKey)
            ? selectedRole.accessible_pages.filter(p => p !== pageKey)
            : [...selectedRole.accessible_pages, pageKey];
        const updatedRole = { ...selectedRole, accessible_pages: currentPages };
        setSelectedRole(updatedRole);
        updateMutation.mutate({ role: selectedRole.role, permissions: selectedRole.permissions, accessible_pages: currentPages });
    };

    // Sync selected role with fresh data from server
    React.useEffect(() => {
        if (rolesData && selectedRole) {
            const fresh = rolesData.find(r => r.role === selectedRole.role);
            if (fresh && savingKey === null) setSelectedRole(fresh);
        }
    }, [rolesData]); // eslint-disable-line react-hooks/exhaustive-deps

    if (isLoading) {
        return (
            <div className="flex flex-col items-center justify-center h-64 gap-4">
                <ArrowPathIcon className="h-8 w-8 animate-spin text-blue-500" />
                <p className="text-sm font-medium text-slate-400">Cargando configuración de permisos...</p>
            </div>
        );
    }

    const enabledCount = selectedRole ? Object.values(selectedRole.permissions).filter(Boolean).length : 0;
    const totalPerms = Object.keys(PERMISSION_LABELS).length;

    return (
        <div className="bg-white/50 backdrop-blur-xl rounded-3xl shadow-xl border border-white/60 overflow-hidden">

            {/* Header */}
            <div className="px-6 py-5 border-b border-slate-100 flex items-center justify-between bg-gradient-to-r from-slate-50 to-white">
                <div className="flex items-center gap-3">
                    <div className="p-2.5 bg-blue-600 rounded-xl shadow-lg shadow-blue-200">
                        <ShieldCheckIcon className="h-5 w-5 text-white" />
                    </div>
                    <div>
                        <h2 className="text-base font-black text-slate-900">Matriz de Permisos y Roles</h2>
                        <p className="text-xs text-slate-400 font-medium">Configura qué puede hacer cada rol en el sistema SERTEC</p>
                    </div>
                </div>
                {selectedRole && (
                    <div className={`hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl border text-xs font-black uppercase tracking-wider ${ROLE_BG[selectedRole.role] || 'bg-slate-50 text-slate-700 border-slate-200'}`}>
                        <span>{enabledCount}/{totalPerms}</span>
                        <span className="font-medium opacity-60">permisos activos</span>
                    </div>
                )}
            </div>

            <div className="flex flex-col md:flex-row" style={{ minHeight: '580px' }}>

                {/* SIDEBAR: Role list */}
                <div className="w-full md:w-60 border-r border-slate-100 bg-slate-50/60 p-4 space-y-1.5 overflow-y-auto flex-shrink-0">
                    <p className="text-[9px] font-black text-slate-400 uppercase tracking-[0.2em] px-2 mb-3">Roles del Sistema</p>
                    {rolesData?.map((roleObj) => {
                        const isSelected = selectedRole?.role === roleObj.role;
                        const colorClass = ROLE_COLORS[roleObj.role] || 'from-slate-500 to-slate-700';
                        const active = Object.values(roleObj.permissions || {}).filter(Boolean).length;
                        const total = Object.keys(PERMISSION_LABELS).length;

                        return (
                            <button
                                key={roleObj.role}
                                onClick={() => setSelectedRole(roleObj)}
                                className={`w-full text-left px-3.5 py-3 rounded-2xl transition-all group
                                    ${isSelected
                                        ? 'bg-white shadow-md ring-1 ring-black/5'
                                        : 'hover:bg-white/70 hover:shadow-sm'
                                    }`}
                            >
                                <div className="flex items-center gap-3">
                                    <div className={`w-2.5 h-2.5 rounded-full bg-gradient-to-br ${colorClass} flex-shrink-0 ${isSelected ? 'shadow-md' : ''}`} />
                                    <div className="flex-1 min-w-0">
                                        <p className={`text-sm font-black truncate ${isSelected ? 'text-slate-900' : 'text-slate-600 group-hover:text-slate-800'}`}>
                                            {roleObj.role_display || roleObj.role}
                                        </p>
                                        <p className="text-[9px] font-bold text-slate-400 mt-0.5">{active}/{total} permisos</p>
                                    </div>
                                    {isSelected && (
                                        <div className="w-1.5 h-5 rounded-full bg-blue-600 flex-shrink-0" />
                                    )}
                                </div>
                            </button>
                        );
                    })}
                </div>

                {/* CONTENT: Permission matrix */}
                <div className="flex-1 overflow-y-auto p-6 space-y-8">
                    {selectedRole ? (
                        <>
                            {/* Role header */}
                            <div className="flex items-center justify-between">
                                <div>
                                    <h3 className="text-xl font-black text-slate-900">{selectedRole.role_display}</h3>
                                    <p className="text-xs text-slate-400 font-medium mt-0.5">
                                        Configura los permisos para este rol · Los cambios se aplican a todos los usuarios con este rol (salvo overrides individuales)
                                    </p>
                                </div>
                                <span className="hidden lg:block text-[10px] font-mono bg-slate-100 text-slate-500 px-2.5 py-1 rounded-lg">
                                    {selectedRole.role}
                                </span>
                            </div>

                            {/* Permissions by category */}
                            {Object.entries(PERMISSION_CATEGORIES).map(([categoryName, keys]) => (
                                <section key={categoryName}>
                                    <div className="flex items-center gap-2 mb-3 pb-2 border-b border-slate-100">
                                        <ShieldCheckIcon className="h-4 w-4 text-slate-400" />
                                        <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-widest">{categoryName}</h4>
                                    </div>
                                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-2.5">
                                        {keys.map((key) => {
                                            const label = PERMISSION_LABELS[key];
                                            const description = PERMISSION_DESCRIPTIONS[key];
                                            if (!label) return null;
                                            const IconComponent = PERMISSION_ICONS[key] || ShieldCheckIcon;
                                            const isEnabled = selectedRole.permissions[key] || false;
                                            const isSaving = savingKey === key;

                                            return (
                                                <div
                                                    key={key}
                                                    onClick={() => !isSaving && togglePermission(key)}
                                                    className={`group flex items-center gap-3.5 p-4 rounded-xl border cursor-pointer transition-all duration-200
                                                        ${isEnabled
                                                            ? 'bg-blue-50/60 border-blue-200 shadow-sm'
                                                            : 'bg-white border-slate-100 hover:border-slate-200 hover:bg-slate-50/50'
                                                        }
                                                        ${isSaving ? 'opacity-60 cursor-not-allowed' : ''}
                                                    `}
                                                >
                                                    <div className={`flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center transition-all
                                                        ${isEnabled ? 'bg-blue-600 shadow-md shadow-blue-200' : 'bg-slate-100'}`}>
                                                        <IconComponent className={`h-4.5 w-4.5 ${isEnabled ? 'text-white' : 'text-slate-400'}`} />
                                                    </div>
                                                    <div className="flex-1 min-w-0">
                                                        <p className={`text-sm font-bold truncate ${isEnabled ? 'text-slate-900' : 'text-slate-500'}`}>{label}</p>
                                                        <p className="text-[10px] text-slate-400 truncate">{description}</p>
                                                    </div>
                                                    <PermissionToggle
                                                        enabled={isEnabled}
                                                        saving={isSaving}
                                                        onClick={(e) => { e?.stopPropagation(); togglePermission(key); }}
                                                    />
                                                </div>
                                            );
                                        })}
                                    </div>
                                </section>
                            ))}

                            {/* Pages Section */}
                            <section>
                                <div className="flex items-center gap-2 mb-3 pb-2 border-b border-slate-100">
                                    <ComputerDesktopIcon className="h-4 w-4 text-slate-400" />
                                    <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Páginas del Sistema con Acceso</h4>
                                </div>
                                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2.5">
                                    {Object.entries(PAGE_LABELS).map(([key, label]) => {
                                        const PageIcon = PAGE_ICONS[key] || ComputerDesktopIcon;
                                        const isEnabled = selectedRole.accessible_pages?.includes(key);
                                        const isSaving = savingKey === 'page_' + key;

                                        return (
                                            <button
                                                key={key}
                                                type="button"
                                                onClick={() => !isSaving && togglePage(key)}
                                                disabled={isSaving}
                                                className={`flex flex-col items-center gap-2 p-4 rounded-xl border text-center transition-all
                                                    ${isEnabled
                                                        ? 'bg-emerald-50 border-emerald-200 shadow-sm text-emerald-900'
                                                        : 'bg-white border-slate-100 text-slate-400 hover:border-slate-200 hover:bg-slate-50/50'
                                                    }
                                                    ${isSaving ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'}`}
                                            >
                                                <div className={`w-10 h-10 rounded-xl flex items-center justify-center transition-all
                                                    ${isEnabled ? 'bg-emerald-600 shadow-md shadow-emerald-200' : 'bg-slate-100'}`}>
                                                    {isSaving
                                                        ? <ArrowPathIcon className="h-5 w-5 text-emerald-600 animate-spin" />
                                                        : isEnabled
                                                            ? <CheckIcon className="h-5 w-5 text-white" />
                                                            : <PageIcon className="h-5 w-5 text-slate-400" />
                                                    }
                                                </div>
                                                <span className="text-[10px] font-black uppercase tracking-tight leading-tight">{label}</span>
                                            </button>
                                        );
                                    })}
                                </div>
                            </section>
                        </>
                    ) : (
                        <div className="flex flex-col items-center justify-center h-full gap-4 text-center py-24">
                            <ShieldCheckIcon className="h-16 w-16 text-slate-200" />
                            <p className="text-slate-400 text-sm font-medium">Selecciona un rol para configurar sus permisos</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default PermissionManager;
