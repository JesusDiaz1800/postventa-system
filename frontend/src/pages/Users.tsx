import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { usersAPI } from '../services/api';
import { useNotifications } from '../hooks/useNotifications';
import { usePermissions } from '../hooks/usePermissions';
import PageHeader from '../components/PageHeader';
import UserCreateModal from '../components/UserCreateModal';
import UserEditModal from '../components/UserEditModal';
import UserDeleteModal from '../components/UserDeleteModal';
import ChangePasswordModal from '../components/ChangePasswordModal';
import PermissionManager from '../components/PermissionManager';
import {
  MagnifyingGlassIcon,
  UserPlusIcon,
  UserIcon,
  KeyIcon,
  TrashIcon,
  PencilIcon,
  ShieldCheckIcon,
  UsersIcon,
  AdjustmentsHorizontalIcon
} from '@heroicons/react/24/outline';

const Users = () => {
  const [activeTab, setActiveTab] = useState('users'); // 'users' or 'permissions'
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRole, setSelectedRole] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);

  // Hook de permisos
  const { canManageUsers, user: currentUser } = usePermissions();

  // Funciones auxiliares para determinar permisos
  const canEditUser = (user) => {
    return canManageUsers() || (currentUser && currentUser.id === user.id);
  };

  const canDeleteUser = (user) => {
    return canManageUsers() && currentUser && currentUser.id !== user.id;
  };

  const canResetPassword = (user) => {
    return canManageUsers() || (currentUser && currentUser.id === user.id);
  };

  const [selectedUser, setSelectedUser] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [userToDelete, setUserToDelete] = useState(null);
  const [showChangePasswordModal, setShowChangePasswordModal] = useState(false);
  const [userToChangePassword, setUserToChangePassword] = useState(null);

  const { showSuccess, showError } = useNotifications();
  const queryClient = useQueryClient();

  // Query para obtener usuarios
  const { data: usersData, isLoading, error } = useQuery({
    queryKey: ['users', { search: searchTerm, role: selectedRole }],
    queryFn: () => usersAPI.list({ search: searchTerm, role: selectedRole }),
    enabled: activeTab === 'users' // Only fetch if on users tab
  });

  // Handle paginated response
  let users = [];
  if (usersData) {
    if (Array.isArray(usersData)) {
      users = usersData;
    } else if (usersData.data && usersData.data.results) {
      users = usersData.data.results;
    } else if (usersData.results) {
      users = usersData.results;
    } else if (usersData.data && Array.isArray(usersData.data)) {
      users = usersData.data;
    }
  }

  // Mutations
  const createUserMutation = useMutation({
    mutationFn: usersAPI.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['users']);
      showSuccess('Usuario creado exitosamente');
      setShowCreateModal(false);
    },
    onError: (error) => {
      showError('Error al crear usuario: ' + (error.response?.data?.message || error.message));
    },
  });

  const updateUserMutation = useMutation({
    mutationFn: ({ id, data }) => usersAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['users']);
      showSuccess('Usuario actualizado exitosamente');
      setShowEditModal(false);
      setSelectedUser(null);
    },
    onError: (error) => {
      showError('Error al actualizar usuario: ' + (error.response?.data?.message || error.message));
    },
  });

  const deleteUserMutation = useMutation({
    mutationFn: usersAPI.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['users']);
      showSuccess('Usuario eliminado exitosamente');
      setShowDeleteModal(false);
      setUserToDelete(null);
    },
    onError: (error) => {
      showError('Error al eliminar usuario: ' + (error.response?.data?.message || error.message));
    },
  });

  const changePasswordMutation = useMutation({
    mutationFn: ({ id, ...data }) => usersAPI.changePassword(id, data),
    onSuccess: () => {
      showSuccess('Contraseña actualizada exitosamente');
      setShowChangePasswordModal(false);
      setUserToChangePassword(null);
    },
    onError: (error) => {
      showError('Error al cambiar contraseña: ' + (error.response?.data?.message || error.message));
    },
  });

  // Handlers
  const handleCreateUser = (userData) => {
    createUserMutation.mutate(userData);
  };

  const handleEditUser = (user) => {
    setSelectedUser(user);
    setShowEditModal(true);
  };

  const handleUpdateUser = (userData) => {
    updateUserMutation.mutate({ id: selectedUser.id, data: userData });
  };

  const handleDeleteUser = (user) => {
    setUserToDelete(user);
    setShowDeleteModal(true);
  };

  const confirmDeleteUser = () => {
    if (userToDelete) {
      deleteUserMutation.mutate(userToDelete.id);
    }
  };

  const handleChangePassword = (user) => {
    setUserToChangePassword(user);
    setShowChangePasswordModal(true);
  };

  const handlePasswordChange = (passwordData) => {
    changePasswordMutation.mutate({ id: userToChangePassword.id, ...passwordData });
  };

  // Filter users logic (client-side fallback if needed)
  const filteredUsers = users.filter(user => {
    // If backend handles filtering, this might be redundant but safe
    const matchesSearch = !searchTerm ||
      user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.last_name.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesRole = !selectedRole || user.role === selectedRole;

    return matchesSearch && matchesRole;
  });

  // Role display function
  const getRoleDisplay = (role) => {
    const roleMap = {
      'admin': 'Administrador',
      'management': 'Gerencia',
      'technical_service': 'Servicio Técnico',
      'quality': 'Calidad',
      'supervisor': 'Supervisor',
      'analyst': 'Analista',
      'customer_service': 'Atención al Cliente',
      'provider': 'Proveedor'
    };
    return roleMap[role] || role;
  };

  // Role badge component
  const RoleBadge = ({ role }) => {
    const roleColors = {
      'admin': 'bg-rose-100 text-rose-800 border-rose-200',
      'management': 'bg-purple-100 text-purple-800 border-purple-200',
      'technical_service': 'bg-blue-100 text-blue-800 border-blue-200',
      'quality': 'bg-emerald-100 text-emerald-800 border-emerald-200',
      'supervisor': 'bg-amber-100 text-amber-800 border-amber-200',
      'analyst': 'bg-indigo-100 text-indigo-800 border-indigo-200',
      'customer_service': 'bg-pink-100 text-pink-800 border-pink-200',
      'provider': 'bg-slate-100 text-slate-800 border-slate-200'
    };

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-lg text-xs font-bold uppercase tracking-wider border ${roleColors[role] || 'bg-gray-100 text-gray-800'}`}>
        {getRoleDisplay(role)}
      </span>
    );
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <PageHeader
          title="Gestión de Accesos"
          subtitle="Administración centralizada de usuarios y roles"
          icon={UsersIcon}
          showLogo={true}
        />

        {/* Toggle View */}
        <div className="flex bg-white/50 backdrop-blur rounded-xl p-1 border border-white/60 shadow-sm self-start md:self-auto">
          <button
            onClick={() => setActiveTab('users')}
            className={`
              flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-bold transition-all
              ${activeTab === 'users'
                ? 'bg-white text-indigo-600 shadow-md ring-1 ring-black/5'
                : 'text-gray-500 hover:text-gray-900 hover:bg-white/40'}
            `}
          >
            <UserIcon className="h-4 w-4" />
            Usuarios
          </button>
          {currentUser?.role === 'admin' && (
            <button
              onClick={() => setActiveTab('permissions')}
              className={`
                flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-bold transition-all
                ${activeTab === 'permissions'
                  ? 'bg-white text-indigo-600 shadow-md ring-1 ring-black/5'
                  : 'text-gray-500 hover:text-gray-900 hover:bg-white/40'}
              `}
            >
              <ShieldCheckIcon className="h-4 w-4" />
              Roles y Permisos
            </button>
          )}
        </div>
      </div>

      {activeTab === 'users' ? (
        <>
          {/* Controls Bar */}
          <div className="flex flex-col md:flex-row gap-4 items-center justify-between bg-white/40 backdrop-blur-md p-4 rounded-2xl border border-white/50 shadow-sm">

            {/* Search & Filter */}
            <div className="flex flex-col sm:flex-row gap-3 w-full md:w-auto flex-1">
              <div className="relative group flex-1 max-w-md">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400 group-focus-within:text-indigo-500 transition-colors" />
                <input
                  type="text"
                  placeholder="Buscar usuario..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 w-full px-4 py-2.5 bg-white/80 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-sm font-medium"
                />
              </div>

              <div className="w-full sm:w-48 relative">
                <AdjustmentsHorizontalIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <select
                  value={selectedRole}
                  onChange={(e) => setSelectedRole(e.target.value)}
                  className="pl-10 w-full px-4 py-2.5 bg-white/80 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-sm font-medium appearance-none"
                >
                  <option value="">Todos los roles</option>
                  <option value="admin">Administrador</option>
                  <option value="management">Gerencia</option>
                  <option value="technical_service">Servicio Técnico</option>
                  <option value="quality">Calidad</option>
                  <option value="supervisor">Supervisor</option>
                  <option value="analyst">Analista</option>
                  <option value="customer_service">Atención al Cliente</option>
                  <option value="provider">Proveedor</option>
                </select>
              </div>
            </div>

            {/* Action Button */}
            {canManageUsers() && (
              <button
                onClick={() => setShowCreateModal(true)}
                className="w-full md:w-auto px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-sm font-bold shadow-lg shadow-indigo-500/30 transition-all flex items-center justify-center gap-2 hover:scale-[1.02]"
              >
                <UserPlusIcon className="h-5 w-5" />
                Nuevo Usuario
              </button>
            )}
          </div>

          {/* Users Table */}
          <div className="bg-white/60 backdrop-blur-xl rounded-3xl shadow-xl border border-white/60 overflow-hidden">
            {isLoading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600"></div>
              </div>
            ) : filteredUsers.length === 0 ? (
              <div className="text-center py-20">
                <div className="bg-gray-50 rounded-full h-20 w-20 flex items-center justify-center mx-auto mb-4">
                  <UserIcon className="h-10 w-10 text-gray-300" />
                </div>
                <h3 className="text-lg font-medium text-gray-900">No se encontraron usuarios</h3>
                <p className="text-gray-500">Intenta ajustar los filtros de búsqueda</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-100">
                  <thead>
                    <tr className="bg-gray-50/50">
                      <th className="px-6 py-4 text-left text-xs font-black text-gray-400 uppercase tracking-wider pl-8">Usuario</th>
                      <th className="px-6 py-4 text-left text-xs font-black text-gray-400 uppercase tracking-wider">Rol</th>
                      <th className="px-6 py-4 text-left text-xs font-black text-gray-400 uppercase tracking-wider">Departamento</th>
                      <th className="px-6 py-4 text-left text-xs font-black text-gray-400 uppercase tracking-wider">Estado</th>
                      <th className="px-6 py-4 text-left text-xs font-black text-gray-400 uppercase tracking-wider">Último Acceso</th>
                      <th className="px-6 py-4 text-right text-xs font-black text-gray-400 uppercase tracking-wider pr-8">Acciones</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100 bg-transparent">
                    {filteredUsers.map((user) => (
                      <tr key={user.id} className="hover:bg-indigo-50/30 transition-colors group">
                        <td className="px-6 py-4 whitespace-nowrap pl-8">
                          <div className="flex items-center">
                            <div className="flex-shrink-0 h-10 w-10">
                              <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-md">
                                <span className="text-white font-bold text-sm">
                                  {user.first_name?.[0] || user.username[0].toUpperCase()}
                                </span>
                              </div>
                            </div>
                            <div className="ml-4">
                              <div className="text-sm font-bold text-gray-900">
                                {user.full_name || user.username}
                              </div>
                              <div className="text-xs text-gray-500 font-mono">{user.email}</div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <RoleBadge role={user.role} />
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 font-medium">
                          {user.department || <span className="text-gray-400 italic">No asignado</span>}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${user.is_active
                              ? 'bg-emerald-100 text-emerald-800'
                              : 'bg-rose-100 text-rose-800'
                            }`}>
                            <span className={`w-1.5 h-1.5 mr-1.5 rounded-full ${user.is_active ? 'bg-emerald-500' : 'bg-rose-500'}`}></span>
                            {user.is_active ? 'Activo' : 'Inactivo'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {user.last_login
                            ? new Date(user.last_login).toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric' })
                            : <span className="text-gray-300">Nunca</span>
                          }
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium pr-8">
                          <div className="flex items-center justify-end gap-2 opacity-60 group-hover:opacity-100 transition-all duration-200">
                            {canEditUser(user) && (
                              <button
                                onClick={() => handleEditUser(user)}
                                className="p-2 rounded-lg text-indigo-600 hover:bg-indigo-50 hover:shadow-sm transition-all"
                                title="Editar"
                              >
                                <PencilIcon className="h-5 w-5" />
                              </button>
                            )}
                            {canResetPassword(user) && (
                              <button
                                onClick={() => handleChangePassword(user)}
                                className="p-2 rounded-lg text-amber-600 hover:bg-amber-50 hover:shadow-sm transition-all"
                                title="Cambiar contraseña"
                              >
                                <KeyIcon className="h-5 w-5" />
                              </button>
                            )}
                            {canDeleteUser(user) && (
                              <button
                                onClick={() => handleDeleteUser(user)}
                                className="p-2 rounded-lg text-rose-600 hover:bg-rose-50 hover:shadow-sm transition-all"
                                title="Eliminar"
                              >
                                <TrashIcon className="h-5 w-5" />
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      ) : (
        /* Permission Manager Tab */
        <PermissionManager />
      )}

      {/* Modales */}
      <UserCreateModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSubmit={handleCreateUser}
        isLoading={createUserMutation.isPending}
      />

      <UserEditModal
        isOpen={showEditModal}
        onClose={() => {
          setShowEditModal(false);
          setSelectedUser(null);
        }}
        onSubmit={handleUpdateUser}
        user={selectedUser}
        isLoading={updateUserMutation.isPending}
      />

      <UserDeleteModal
        isOpen={showDeleteModal}
        onClose={() => {
          setShowDeleteModal(false);
          setUserToDelete(null);
        }}
        onConfirm={confirmDeleteUser}
        user={userToDelete}
        isLoading={deleteUserMutation.isPending}
      />

      <ChangePasswordModal
        isOpen={showChangePasswordModal}
        onClose={() => {
          setShowChangePasswordModal(false);
          setUserToChangePassword(null);
        }}
        onSave={handlePasswordChange}
        user={userToChangePassword}
        isOwnPassword={currentUser && userToChangePassword && currentUser.id === userToChangePassword.id}
      />
    </div>
  );
};

export default Users;