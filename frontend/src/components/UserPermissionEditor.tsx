import React, { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { 
    ShieldCheckIcon, 
    ComputerDesktopIcon,
    CheckCircleIcon,
    ArrowPathIcon,
    InformationCircleIcon,
    ArrowPathRoundedSquareIcon
} from '@heroicons/react/24/outline';
import { PERMISSION_LABELS, PAGE_LABELS, getEffectivePermission, isPermissionOverridden } from '../utils/permissionUtils';

const UserPermissionEditor = ({ 
    user, 
    permissions_override = {}, 
    pages_override = [], 
    onPermissionsChange, 
    onPagesChange 
}) => {
    // Fetch all role permissions to find the baseline for this user's role
    const { data: rolesData, isLoading } = useQuery({
        queryKey: ['role-permissions'],
        queryFn: async () => {
            const response = await api.get('/users/permissions/roles/');
            return response.data;
        }
    });

    const userRoleData = useMemo(() => {
        if (!rolesData || !user?.role) return null;
        return rolesData.find(r => r.role === user.role);
    }, [rolesData, user?.role]);

    if (isLoading) {
        return (
            <div className="flex justify-center p-8">
                <ArrowPathIcon className="h-6 w-6 animate-spin text-indigo-500" />
            </div>
        );
    }

    const togglePermission = (key) => {
        const newOverrides = { ...permissions_override };
        
        // If it's already an override, we might want to toggle its value
        // or clear it if it matches the role default (optional refinement)
        const roleValue = userRoleData?.permissions?.[key] || false;
        const currentEffective = getEffectivePermission(userRoleData?.permissions, permissions_override, key);
        
        const newValue = !currentEffective;
        
        // Save as override
        newOverrides[key] = newValue;
        
        onPermissionsChange(newOverrides);
    };

    const resetPermissions = () => {
        onPermissionsChange({});
        onPagesChange([]);
    };

    const togglePage = (key) => {
        // Pages are slightly different: if pages_override is empty, we use role baseline.
        // If it's NOT empty, it's a full override of the list.
        let currentPages = pages_override.length > 0 ? [...pages_override] : [...(userRoleData?.accessible_pages || [])];
        
        if (currentPages.includes(key)) {
            currentPages = currentPages.filter(p => p !== key);
        } else {
            currentPages.push(key);
        }
        
        onPagesChange(currentPages);
    };

    return (
        <div className="space-y-6 max-h-[500px] overflow-y-auto px-1">
            <div className="flex items-center justify-between border-b border-indigo-50 pb-3">
                <div>
                    <h4 className="text-sm font-bold text-indigo-900">Configuración Personalizada</h4>
                    <p className="text-xs text-indigo-400">
                        Los cambios aquí sobrescriben los permisos del rol <span className="font-bold underline">{userRoleData?.role_display || user?.role}</span>.
                    </p>
                </div>
                <button 
                    type="button"
                    onClick={resetPermissions}
                    className="flex items-center gap-1 text-[10px] uppercase font-bold text-red-500 hover:text-red-700 transition-colors"
                >
                    <ArrowPathRoundedSquareIcon className="h-3 w-3" />
                    Restablecer
                </button>
            </div>

            {/* Permissions Section */}
            <section>
                <div className="flex items-center gap-2 mb-3">
                    <ShieldCheckIcon className="h-4 w-4 text-indigo-600" />
                    <span className="text-xs font-black uppercase tracking-widest text-gray-400">Capacidades de Acción</span>
                </div>
                <div className="grid grid-cols-1 gap-2">
                    {Object.entries(PERMISSION_LABELS).map(([key, label]) => {
                        const isOverridden = isPermissionOverridden(permissions_override, key);
                        const effectiveValue = getEffectivePermission(userRoleData?.permissions, permissions_override, key);
                        
                        return (
                            <div 
                                key={key}
                                onClick={() => togglePermission(key)}
                                className={`
                                    flex items-center justify-between p-3 rounded-xl border cursor-pointer transition-all duration-200
                                    ${isOverridden 
                                        ? 'bg-amber-50/30 border-amber-200 shadow-sm' 
                                        : 'bg-white border-gray-100 hover:border-indigo-100'
                                    }
                                `}
                            >
                                <div className="flex flex-col">
                                    <span className={`text-sm font-semibold ${effectiveValue ? 'text-gray-900' : 'text-gray-400'}`}>
                                        {label}
                                    </span>
                                    {isOverridden && (
                                        <span className="text-[10px] text-amber-600 font-bold uppercase tracking-tighter">Personalizado</span>
                                    )}
                                    {!isOverridden && effectiveValue && (
                                        <span className="text-[10px] text-indigo-400 font-medium">Heredado del rol</span>
                                    )}
                                </div>

                                <div className={`
                                    w-10 h-5 flex items-center rounded-full p-1 transition-colors duration-200
                                    ${effectiveValue ? (isOverridden ? 'bg-amber-500' : 'bg-indigo-600') : 'bg-gray-200'}
                                `}>
                                    <div className={`
                                        bg-white w-3 h-3 rounded-full shadow-sm transform transition-transform duration-200
                                        ${effectiveValue ? 'translate-x-5' : 'translate-x-0'}
                                    `} />
                                </div>
                            </div>
                        );
                    })}
                </div>
            </section>

            {/* Pages Section */}
            <section>
                <div className="flex items-center gap-2 mb-3 pt-4 border-t border-gray-50">
                    <ComputerDesktopIcon className="h-4 w-4 text-emerald-600" />
                    <span className="text-xs font-black uppercase tracking-widest text-gray-400">Acceso a Páginas</span>
                </div>
                {pages_override.length === 0 && (
                    <div className="flex items-start gap-2 p-3 bg-indigo-50 rounded-xl mb-4 border border-indigo-100">
                        <InformationCircleIcon className="h-4 w-4 text-indigo-500 mt-0.5" />
                        <p className="text-[11px] text-indigo-600 leading-tight">
                            Este usuario usa los accesos estándar del rol. Al seleccionar una página, se creará una lista personalizada exclusiva.
                        </p>
                    </div>
                )}
                <div className="grid grid-cols-2 gap-2">
                    {Object.entries(PAGE_LABELS).map(([key, label]) => {
                        const roleHasAccess = userRoleData?.accessible_pages?.includes(key);
                        const userHasAccess = pages_override.length > 0 
                            ? pages_override.includes(key)
                            : roleHasAccess;
                        
                        const isIndividual = pages_override.length > 0 && pages_override.includes(key) !== roleHasAccess;
                        const isOverrideActive = pages_override.length > 0;

                        return (
                            <button
                                key={key}
                                type="button"
                                onClick={() => togglePage(key)}
                                className={`
                                    flex items-center gap-2 p-2.5 rounded-xl border text-left transition-all
                                    ${userHasAccess
                                        ? (isOverrideActive ? 'bg-amber-50/50 border-amber-200 text-amber-900 shadow-sm' : 'bg-emerald-50/50 border-emerald-100 text-emerald-900')
                                        : 'bg-white border-gray-50 text-gray-300'
                                    }
                                `}
                            >
                                <div className={`
                                    flex-shrink-0 h-4 w-4 rounded border flex items-center justify-center
                                    ${userHasAccess 
                                        ? (isOverrideActive ? 'bg-amber-500 border-amber-600' : 'bg-emerald-500 border-emerald-600') 
                                        : 'border-gray-200'
                                    }
                                `}>
                                    {userHasAccess && <CheckCircleIcon className="h-3.5 w-3.5 text-white" />}
                                </div>
                                <span className="text-[10px] font-black uppercase truncate">{label}</span>
                            </button>
                        );
                    })}
                </div>
            </section>
        </div>
    );
};

export default UserPermissionEditor;
