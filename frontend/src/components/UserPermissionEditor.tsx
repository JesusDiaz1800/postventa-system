import React, { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import {
    ShieldCheckIcon,
    ComputerDesktopIcon,
    ArrowPathIcon,
    ArrowPathRoundedSquareIcon,
    LockClosedIcon,
    LockOpenIcon,
    InformationCircleIcon,
} from '@heroicons/react/24/outline';
import {
    PERMISSION_LABELS,
    PERMISSION_DESCRIPTIONS,
    PERMISSION_CATEGORIES,
    PAGE_LABELS,
    getEffectivePermission,
    isPermissionOverridden,
} from '../utils/permissionUtils';

const Toggle = ({ enabled, overridden, onClick }) => (
    <button
        type="button"
        onClick={(e) => { e.stopPropagation(); onClick(); }}
        className={`relative flex-shrink-0 w-12 h-6 rounded-full transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-1
            ${enabled
                ? overridden
                    ? 'bg-amber-500 focus:ring-amber-400'
                    : 'bg-blue-600 focus:ring-blue-500'
                : 'bg-slate-200 focus:ring-slate-300'
            }`}
    >
        <span className={`
            absolute top-1 left-1 w-4 h-4 bg-white rounded-full shadow-md transform transition-transform duration-300
            ${enabled ? 'translate-x-6' : 'translate-x-0'}
        `} />
    </button>
);

const PermissionRow = ({ permKey, label, description, effectiveValue, isOverridden, onToggle }) => (
    <div
        className={`group flex items-center justify-between gap-4 p-3.5 rounded-xl border transition-all duration-200 cursor-pointer
            ${isOverridden
                ? 'bg-amber-50/60 border-amber-200 shadow-sm'
                : effectiveValue
                    ? 'bg-blue-50/40 border-blue-100'
                    : 'bg-white border-slate-100 hover:border-slate-200 hover:bg-slate-50/50'
            }`}
        onClick={onToggle}
    >
        <div className="flex flex-col min-w-0">
            <span className={`text-sm font-bold truncate ${effectiveValue ? 'text-slate-900' : 'text-slate-400'}`}>
                {label}
            </span>
            <span className="text-[10px] text-slate-400 font-medium truncate mt-0.5">{description}</span>
            {isOverridden && (
                <span className="text-[9px] font-black text-amber-600 uppercase tracking-wider mt-0.5">
                    ● Personalizado (sobrescribe el rol)
                </span>
            )}
            {!isOverridden && effectiveValue && (
                <span className="text-[9px] font-medium text-blue-400 mt-0.5">Heredado del rol</span>
            )}
        </div>
        <Toggle enabled={effectiveValue} overridden={isOverridden} onClick={onToggle} />
    </div>
);

const UserPermissionEditor = ({
    user,
    permissions_override = {},
    pages_override = [],
    onPermissionsChange,
    onPagesChange,
}) => {
    const { data: rolesData, isLoading } = useQuery({
        queryKey: ['role-permissions'],
        queryFn: async () => {
            const response = await api.get('/users/permissions/roles/');
            return response.data;
        },
        staleTime: 60000,
    });

    const userRoleData = useMemo(() => {
        if (!rolesData || !user?.role) return null;
        return rolesData.find(r => r.role === user.role);
    }, [rolesData, user?.role]);

    const hasOverrides = Object.keys(permissions_override).length > 0 || pages_override.length > 0;

    if (isLoading) {
        return (
            <div className="flex justify-center items-center p-10">
                <ArrowPathIcon className="h-6 w-6 animate-spin text-blue-500" />
            </div>
        );
    }

    const togglePermission = (key) => {
        const currentEffective = getEffectivePermission(userRoleData?.permissions, permissions_override, key);
        onPermissionsChange({ ...permissions_override, [key]: !currentEffective });
    };

    const resetAll = () => {
        onPermissionsChange({});
        onPagesChange([]);
    };

    const togglePage = (key) => {
        const rolePages = userRoleData?.accessible_pages || [];
        // If no override yet, start from role pages
        let currentPages = pages_override.length > 0 ? [...pages_override] : [...rolePages];
        if (currentPages.includes(key)) {
            currentPages = currentPages.filter(p => p !== key);
        } else {
            currentPages.push(key);
        }
        onPagesChange(currentPages);
    };

    return (
        <div className="space-y-5 max-h-[520px] overflow-y-auto pr-1 -mr-1">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                    <div className={`p-1.5 rounded-lg ${hasOverrides ? 'bg-amber-100' : 'bg-blue-50'}`}>
                        {hasOverrides
                            ? <LockOpenIcon className="h-4 w-4 text-amber-600" />
                            : <LockClosedIcon className="h-4 w-4 text-blue-500" />
                        }
                    </div>
                    <div>
                        <p className="text-xs font-black text-slate-800">
                            {hasOverrides ? 'Configuración Personalizada' : 'Usando permisos del rol'}
                        </p>
                        <p className="text-[10px] text-slate-400">
                            Rol base: <span className="font-bold text-blue-600">{userRoleData?.role_display || user?.role || '—'}</span>
                        </p>
                    </div>
                </div>
                {hasOverrides && (
                    <button
                        type="button"
                        onClick={resetAll}
                        className="flex items-center gap-1.5 text-[10px] uppercase font-black text-red-500 hover:text-red-700 bg-red-50 hover:bg-red-100 px-3 py-1.5 rounded-lg transition-all"
                    >
                        <ArrowPathRoundedSquareIcon className="h-3.5 w-3.5" />
                        Restablecer todo
                    </button>
                )}
            </div>

            {/* Permissions by category */}
            {Object.entries(PERMISSION_CATEGORIES).map(([categoryName, keys]) => (
                <section key={categoryName}>
                    <div className="flex items-center gap-2 mb-2.5">
                        <ShieldCheckIcon className="h-3.5 w-3.5 text-slate-400" />
                        <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{categoryName}</span>
                    </div>
                    <div className="space-y-1.5">
                        {keys.map(key => {
                            const label = PERMISSION_LABELS[key];
                            const description = PERMISSION_DESCRIPTIONS[key];
                            if (!label) return null;
                            const effectiveValue = getEffectivePermission(userRoleData?.permissions, permissions_override, key);
                            const overridden = isPermissionOverridden(permissions_override, key);
                            return (
                                <PermissionRow
                                    key={key}
                                    permKey={key}
                                    label={label}
                                    description={description}
                                    effectiveValue={effectiveValue}
                                    isOverridden={overridden}
                                    onToggle={() => togglePermission(key)}
                                />
                            );
                        })}
                    </div>
                </section>
            ))}

            {/* Pages Section */}
            <section>
                <div className="flex items-center gap-2 mb-2.5 pt-3 border-t border-slate-100">
                    <ComputerDesktopIcon className="h-3.5 w-3.5 text-slate-400" />
                    <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Páginas del Sistema</span>
                </div>

                {pages_override.length === 0 && (
                    <div className="flex items-start gap-2 p-3 bg-blue-50 rounded-xl mb-3 border border-blue-100">
                        <InformationCircleIcon className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
                        <p className="text-[10px] text-blue-600 leading-relaxed">
                            Este usuario accede a las páginas estándar de su rol. Al modificar una, se crea una lista personalizada exclusiva.
                        </p>
                    </div>
                )}

                <div className="grid grid-cols-2 gap-2">
                    {Object.entries(PAGE_LABELS).map(([key, label]) => {
                        const roleHasAccess = userRoleData?.accessible_pages?.includes(key);
                        const userHasAccess = pages_override.length > 0
                            ? pages_override.includes(key)
                            : roleHasAccess;
                        const isCustom = pages_override.length > 0 && (pages_override.includes(key) !== roleHasAccess);

                        return (
                            <button
                                key={key}
                                type="button"
                                onClick={() => togglePage(key)}
                                className={`flex items-center gap-2.5 p-3 rounded-xl border text-left transition-all
                                    ${userHasAccess
                                        ? isCustom
                                            ? 'bg-amber-50 border-amber-200 text-amber-900 shadow-sm'
                                            : 'bg-emerald-50 border-emerald-200 text-emerald-900 shadow-sm'
                                        : 'bg-white border-slate-100 text-slate-300 hover:border-slate-200'
                                    }`}
                            >
                                <div className={`flex-shrink-0 w-5 h-5 rounded-lg border flex items-center justify-center transition-all
                                    ${userHasAccess
                                        ? isCustom ? 'bg-amber-500 border-amber-600' : 'bg-emerald-500 border-emerald-600'
                                        : 'border-slate-200'
                                    }`}>
                                    {userHasAccess && (
                                        <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                        </svg>
                                    )}
                                </div>
                                <div className="flex flex-col min-w-0">
                                    <span className="text-[11px] font-black uppercase tracking-tight truncate">{label}</span>
                                    {isCustom && (
                                        <span className="text-[8px] font-bold text-amber-600 uppercase">Personalizado</span>
                                    )}
                                </div>
                            </button>
                        );
                    })}
                </div>
            </section>
        </div>
    );
};

export default UserPermissionEditor;
