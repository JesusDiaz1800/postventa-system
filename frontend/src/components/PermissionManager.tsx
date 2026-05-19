import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import { useNotifications } from '../hooks/useNotifications';
import {
    ShieldCheckIcon,
    ComputerDesktopIcon,
    CheckCircleIcon,
    XCircleIcon,
    ArrowPathIcon
} from '@heroicons/react/24/outline';

import { PERMISSION_LABELS, PAGE_LABELS } from '../utils/permissionUtils';

const PermissionManager = () => {
    const { showSuccess, showError } = useNotifications();
    const queryClient = useQueryClient();
    const [selectedRole, setSelectedRole] = useState(null);

    // Fetch Permissions
    const { data: rolesData, isLoading } = useQuery({
        queryKey: ['role-permissions'],
        queryFn: async () => {
            const response = await api.get('/users/permissions/roles/');
            return response.data; // Array of objects from serializer
        }
    });

    // Update Permission Mutation
    const updateMutation = useMutation({
        mutationFn: async ({ role, permissions, accessible_pages }) => {
            await api.patch(`/users/permissions/roles/${role}/`, {
                permissions,
                accessible_pages
            });
        },
        onSuccess: () => {
            queryClient.invalidateQueries(['role-permissions']);
            showSuccess('Permisos actualizados correctamente');
        },
        onError: (error) => {
            showError('Error al actualizar permisos: ' + (error.response?.data?.message || error.message));
        }
    });

    if (isLoading) {
        return (
            <div className="flex justify-center p-12">
                <ArrowPathIcon className="h-8 w-8 animate-spin text-blue-500" />
            </div>
        );
    }

    // Set initial selected role
    if (!selectedRole && rolesData && rolesData.length > 0) {
        const adminRole = rolesData.find(r => r.role === 'admin');
        setSelectedRole(adminRole || rolesData[0]);
    }

    const handleRoleSelect = (roleObj) => {
        setSelectedRole(roleObj);
    };

    const togglePermission = (permKey) => {
        if (!selectedRole) return;

        const currentPerms = { ...selectedRole.permissions };
        currentPerms[permKey] = !currentPerms[permKey];

        // Optimistic update local state for UI responsiveness
        const updatedRole = { ...selectedRole, permissions: currentPerms };
        setSelectedRole(updatedRole);

        // Trigger mutation
        updateMutation.mutate({
            role: selectedRole.role,
            permissions: currentPerms,
            accessible_pages: selectedRole.accessible_pages
        });
    };

    const togglePage = (pageKey) => {
        if (!selectedRole) return;

        let currentPages = [...selectedRole.accessible_pages];
        if (currentPages.includes(pageKey)) {
            currentPages = currentPages.filter(p => p !== pageKey);
        } else {
            currentPages.push(pageKey);
        }

        // Optimistic update
        const updatedRole = { ...selectedRole, accessible_pages: currentPages };
        setSelectedRole(updatedRole);

        // Trigger mutation
        updateMutation.mutate({
            role: selectedRole.role,
            permissions: selectedRole.permissions,
            accessible_pages: currentPages
        });
    };

    return (
        <div className="bg-white/50 backdrop-blur-xl rounded-3xl shadow-xl border border-white/60 overflow-hidden">
            <div className="p-6 border-b border-gray-100 flex items-center gap-3">
                <ShieldCheckIcon className="h-6 w-6 text-indigo-600" />
                <h2 className="text-lg font-bold text-gray-800">Matriz de Permisos y Roles</h2>
            </div>

            <div className="flex flex-col md:flex-row h-[600px]">
                {/* Sidebar: Roles List */}
                <div className="w-full md:w-64 bg-gray-50/50 border-r border-gray-100 p-4 space-y-2 overflow-y-auto">
                    <h3 className="text-xs font-black text-gray-400 uppercase tracking-wider mb-4 px-2">Roles del Sistema</h3>
                    {rolesData?.map((roleObj) => (
                        <button
                            key={roleObj.id}
                            onClick={() => handleRoleSelect(roleObj)}
                            className={`w-full text-left px-4 py-3 rounded-xl text-sm font-bold transition-all ${selectedRole?.role === roleObj.role
                                    ? 'bg-white shadow-md text-indigo-700 ring-1 ring-indigo-200'
                                    : 'text-slate-700 hover:bg-white/60 hover:text-indigo-600'
                                }`}
                        >
                            <div className="flex items-center justify-between">
                                <span className="truncate">{roleObj.role_display || roleObj.role}</span>
                                {selectedRole?.role === roleObj.role && (
                                    <div className="h-2 w-2 rounded-full bg-indigo-500" />
                                )}
                            </div>
                        </button>
                    ))}
                </div>

                {/* Content: Permissions & Pages */}
                <div className="flex-1 overflow-y-auto p-6 bg-white/40">
                    {selectedRole && (
                        <div className="space-y-8 animate-fadeIn">

                            {/* Header */}
                            <div className="flex items-center justify-between mb-6">
                                <div>
                                    <h3 className="text-2xl font-bold text-gray-800">{selectedRole.role_display}</h3>
                                    <p className="text-sm text-gray-500">Configuración de acceso y capacidades</p>
                                </div>
                                <div className="text-xs font-mono bg-gray-100 px-3 py-1 rounded-lg text-gray-500">
                                    ID: {selectedRole.role}
                                </div>
                            </div>

                            {/* Permissions Section */}
                            <section>
                                <h4 className="flex items-center gap-2 text-sm font-black text-indigo-900 uppercase tracking-wide mb-4 border-b border-indigo-100 pb-2">
                                    <ShieldCheckIcon className="h-4 w-4" />
                                    Permisos de Acción
                                </h4>
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                    {Object.entries(PERMISSION_LABELS).map(([key, label]) => {
                                        const isEnabled = selectedRole.permissions[key] || false;
                                        return (
                                            <div
                                                key={key}
                                                onClick={() => togglePermission(key)}
                                                className={`
                          group relative flex items-center justify-between p-4 rounded-xl border cursor-pointer transition-all duration-200
                          ${isEnabled
                                                        ? 'bg-indigo-50/50 border-indigo-200 shadow-sm'
                                                        : 'bg-white border-gray-100 hover:border-gray-300'
                                                    }
                        `}
                                            >
                                                <span className={`text-sm font-medium ${isEnabled ? 'text-indigo-900' : 'text-gray-600'}`}>
                                                    {label}
                                                </span>

                                                <div className={`
                          w-11 h-6 flex items-center rounded-full p-1 transition-colors duration-200 ease-in-out
                          ${isEnabled ? 'bg-indigo-600' : 'bg-gray-200'}
                        `}>
                                                    <div className={`
                            bg-white w-4 h-4 rounded-full shadow-md transform transition-transform duration-200 ease-in-out
                            ${isEnabled ? 'translate-x-5' : 'translate-x-0'}
                          `} />
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </section>

                            {/* Pages Section */}
                            <section>
                                <h4 className="flex items-center gap-2 text-sm font-black text-emerald-900 uppercase tracking-wide mb-4 border-b border-emerald-100 pb-2 mt-8">
                                    <ComputerDesktopIcon className="h-4 w-4" />
                                    Acceso a Páginas
                                </h4>
                                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                                    {Object.entries(PAGE_LABELS).map(([key, label]) => {
                                        const isEnabled = selectedRole.accessible_pages?.includes(key);
                                        return (
                                            <button
                                                key={key}
                                                onClick={() => togglePage(key)}
                                                className={`
                          flex items-center gap-3 p-3 rounded-xl border text-left transition-all
                          ${isEnabled
                                                        ? 'bg-emerald-50/50 border-emerald-200 text-emerald-900 shadow-sm'
                                                        : 'bg-white border-gray-100 text-gray-500 hover:border-gray-300'
                                                    }
                        `}
                                            >
                                                <div className={`
                          flex-shrink-0 h-5 w-5 rounded-md border flex items-center justify-center transition-colors
                          ${isEnabled ? 'bg-emerald-500 border-emerald-600' : 'border-gray-300'}
                        `}>
                                                    {isEnabled && <CheckCircleIcon className="h-4 w-4 text-white" />}
                                                </div>
                                                <span className="text-xs font-bold uppercase tracking-tight">{label}</span>
                                            </button>
                                        );
                                    })}
                                </div>
                            </section>

                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default PermissionManager;
