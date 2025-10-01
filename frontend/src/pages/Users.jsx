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
import {
  PlusIcon,
  MagnifyingGlassIcon,
  UserPlusIcon,
  ShieldCheckIcon,
  UserIcon,
  EnvelopeIcon,
  PhoneIcon,
  CalendarIcon,
  PencilIcon,
  TrashIcon,
  EyeIcon,
  KeyIcon,
  CheckCircleIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline';

const Users = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRole, setSelectedRole] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  
  // Hook de permisos
  const { canManageUsers, canAccessAdmin, user: currentUser } = usePermissions();
  
  
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
  
  const { showSuccess, showError, showWarning } = useNotifications();
  const queryClient = useQueryClient();

  // Query para obtener usuarios
  const { data: usersData, isLoading, error } = useQuery({
    queryKey: ['users', { search: searchTerm, role: selectedRole }],
    queryFn: () => usersAPI.list({ search: searchTerm, role: selectedRole }),
  });

  // Handle paginated response from Django REST Framework
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
    mutationFn: ({ id, ...data }) => usersAPI.update(id, data),
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
    updateUserMutation.mutate({ id: selectedUser.id, ...userData });
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

  // Filter users based on search and role
  const filteredUsers = users.filter(user => {
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
      'admin': 'bg-red-100 text-red-800',
      'management': 'bg-purple-100 text-purple-800',
      'technical_service': 'bg-blue-100 text-blue-800',
      'quality': 'bg-green-100 text-green-800',
      'supervisor': 'bg-yellow-100 text-yellow-800',
      'analyst': 'bg-indigo-100 text-indigo-800',
      'customer_service': 'bg-pink-100 text-pink-800',
      'provider': 'bg-gray-100 text-gray-800'
    };

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${roleColors[role] || 'bg-gray-100 text-gray-800'}`}>
        {getRoleDisplay(role)}
      </span>
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Error al cargar los usuarios</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <PageHeader
        title="Gestión de Usuarios"
        subtitle="Administra usuarios, roles y permisos del sistema"
        icon={UserIcon}
        showLogo={true}
      >
        <div className="flex space-x-3">
          {canManageUsers() && (
            <button 
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-xl shadow-lg text-white bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 transform hover:scale-105"
            >
              <UserPlusIcon className="h-5 w-5 mr-2" />
              Nuevo Usuario
            </button>
          )}
        </div>
      </PageHeader>

      {/* Filters */}
      <div className="bg-white shadow-lg rounded-xl border border-gray-100">
        <div className="p-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-2">
                Buscar usuarios
              </label>
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  id="search"
                  placeholder="Buscar por nombre, email o usuario..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            <div className="sm:w-48">
              <label htmlFor="role" className="block text-sm font-medium text-gray-700 mb-2">
                Filtrar por rol
              </label>
              <select
                id="role"
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white shadow-lg rounded-xl border border-gray-100">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">
            Usuarios ({filteredUsers.length})
          </h3>
        </div>
        
        <div className="table-container">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Usuario
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rol
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Departamento
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Último acceso
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredUsers.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-6 py-12 text-center text-gray-500">
                    No se encontraron usuarios
                  </td>
                </tr>
              ) : (
                filteredUsers.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10">
                          <div className="h-10 w-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center">
                            <span className="text-white font-medium text-sm">
                              {user.first_name?.[0] || user.username[0].toUpperCase()}
                            </span>
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {user.full_name || user.username}
                          </div>
                          <div className="text-sm text-gray-500">{user.email}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <RoleBadge role={user.role} />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {user.department || 'No asignado'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        user.is_active 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {user.is_active ? 'Activo' : 'Inactivo'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {user.last_login 
                        ? new Date(user.last_login).toLocaleDateString('es-ES')
                        : 'Nunca'
                      }
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end space-x-2">
                        {canEditUser(user) && (
                          <button 
                            onClick={() => handleEditUser(user)}
                            className="p-2 rounded-lg text-blue-600 hover:text-blue-900 hover:bg-blue-50 transition-colors"
                            title="Editar usuario"
                          >
                            <PencilIcon className="h-4 w-4" />
                          </button>
                        )}
                        {canResetPassword(user) && (
                          <button 
                            onClick={() => handleChangePassword(user)}
                            className="p-2 rounded-lg text-yellow-600 hover:text-yellow-900 hover:bg-yellow-50 transition-colors"
                            title="Cambiar contraseña"
                          >
                            <KeyIcon className="h-4 w-4" />
                          </button>
                        )}
                        {canDeleteUser(user) && (
                          <button 
                            onClick={() => handleDeleteUser(user)}
                            className="p-2 rounded-lg text-red-600 hover:text-red-900 hover:bg-red-50 transition-colors"
                            title="Eliminar usuario"
                          >
                            <TrashIcon className="h-4 w-4" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

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