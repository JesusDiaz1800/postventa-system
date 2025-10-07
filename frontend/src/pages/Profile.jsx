import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useNotifications } from '../hooks/useNotifications';
import ChangePasswordModal from '../components/ChangePasswordModal';
import {
  UserIcon,
  EnvelopeIcon,
  PhoneIcon,
  BuildingOffice2Icon,
  ShieldCheckIcon,
  CalendarIcon,
  PencilIcon,
  KeyIcon,
  BellIcon,
  CogIcon,
} from '@heroicons/react/24/outline';

const Profile = () => {
  const { user } = useAuth();
  const { showSuccess, showError } = useNotifications();
  const [activeTab, setActiveTab] = useState('personal');
  const [isEditing, setIsEditing] = useState(false);
  const [showChangePasswordModal, setShowChangePasswordModal] = useState(false);

  const profileTabs = [
    { id: 'personal', name: 'Información Personal', icon: UserIcon },
    { id: 'security', name: 'Seguridad', icon: ShieldCheckIcon },
    { id: 'notifications', name: 'Notificaciones', icon: BellIcon },
    { id: 'preferences', name: 'Preferencias', icon: CogIcon },
  ];

  const getRoleBadge = (role) => {
    const roleClasses = {
      admin: 'bg-red-100 text-red-800 border-red-200',
      supervisor: 'bg-blue-100 text-blue-800 border-blue-200',
      analyst: 'bg-green-100 text-green-800 border-green-200',
      customer_service: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    };
    
    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold border ${roleClasses[role] || 'bg-gray-100 text-gray-800 border-gray-200'}`}>
        {role}
      </span>
    );
  };

  const handleChangePassword = async (passwordData) => {
    try {
  const { usersAPI } = await import('../services/api');
      await usersAPI.changeOwnPassword(passwordData);
      showSuccess('Contraseña cambiada exitosamente');
      setShowChangePasswordModal(false);
    } catch (error) {
      console.error('Error changing password:', error);
      showError('Error al cambiar la contraseña: ' + (error.response?.data?.error || error.message));
    }
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'personal':
        return (
          <div className="space-y-6">
            <div className="bg-white shadow-xl rounded-xl border border-gray-100 p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900">Información Personal</h3>
                <button
                  onClick={() => setIsEditing(!isEditing)}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
                >
                  <PencilIcon className="h-4 w-4 mr-2" />
                  {isEditing ? 'Cancelar' : 'Editar'}
                </button>
              </div>
              
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Usuario</label>
                  {isEditing ? (
                    <input
                      type="text"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      defaultValue={user?.username}
                    />
                  ) : (
                    <p className="text-sm text-gray-900 bg-gray-50 px-4 py-3 rounded-lg">{user?.username}</p>
                  )}
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                  {isEditing ? (
                    <input
                      type="email"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      defaultValue={user?.email}
                    />
                  ) : (
                    <p className="text-sm text-gray-900 bg-gray-50 px-4 py-3 rounded-lg">{user?.email}</p>
                  )}
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Nombre</label>
                  {isEditing ? (
                    <input
                      type="text"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      defaultValue={`${user?.first_name} ${user?.last_name}`}
                    />
                  ) : (
                    <p className="text-sm text-gray-900 bg-gray-50 px-4 py-3 rounded-lg">{user?.first_name} {user?.last_name}</p>
                  )}
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Teléfono</label>
                  {isEditing ? (
                    <input
                      type="tel"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      defaultValue={user?.phone || ''}
                    />
                  ) : (
                    <p className="text-sm text-gray-900 bg-gray-50 px-4 py-3 rounded-lg">{user?.phone || 'No especificado'}</p>
                  )}
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Departamento</label>
                  {isEditing ? (
                    <input
                      type="text"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      defaultValue={user?.department || ''}
                    />
                  ) : (
                    <p className="text-sm text-gray-900 bg-gray-50 px-4 py-3 rounded-lg">{user?.department || 'No especificado'}</p>
                  )}
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Rol</label>
                  <div className="bg-gray-50 px-4 py-3 rounded-lg">
                    {getRoleBadge(user?.role)}
                  </div>
                </div>
              </div>
              
              {isEditing && (
                <div className="mt-6 flex justify-end space-x-3">
                  <button className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors">
                    Cancelar
                  </button>
                  <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
                    Guardar Cambios
                  </button>
                </div>
              )}
            </div>
          </div>
        );
      
      case 'security':
        return (
          <div className="space-y-6">
            <div className="bg-white shadow-xl rounded-xl border border-gray-100 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Seguridad</h3>
              
              <div className="space-y-6">
                <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center">
                    <KeyIcon className="h-8 w-8 text-gray-400 mr-4" />
                    <div>
                      <h4 className="font-medium text-gray-900">Cambiar Contraseña</h4>
                      <p className="text-sm text-gray-500">Actualiza tu contraseña regularmente</p>
                    </div>
                  </div>
                  <button 
                    onClick={() => setShowChangePasswordModal(true)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Cambiar
                  </button>
                </div>
                
                <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center">
                    <ShieldCheckIcon className="h-8 w-8 text-gray-400 mr-4" />
                    <div>
                      <h4 className="font-medium text-gray-900">Autenticación de Dos Factores</h4>
                      <p className="text-sm text-gray-500">Añade una capa extra de seguridad</p>
                    </div>
                  </div>
                  <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
                    Activar
                  </button>
                </div>
                
                <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center">
                    <CalendarIcon className="h-8 w-8 text-gray-400 mr-4" />
                    <div>
                      <h4 className="font-medium text-gray-900">Último Acceso</h4>
                      <p className="text-sm text-gray-500">{new Date(user?.last_login).toLocaleString('es-ES')}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
      
      default:
        return (
          <div className="bg-white shadow-xl rounded-xl border border-gray-100 p-6">
            <div className="text-center py-12">
              <CogIcon className="mx-auto h-16 w-16 text-gray-400" />
              <h3 className="mt-4 text-lg font-medium text-gray-900">Sección en Desarrollo</h3>
              <p className="mt-2 text-sm text-gray-500">
                Esta sección estará disponible próximamente.
              </p>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-4">
            <div className="h-16 w-16 rounded-full bg-gradient-to-r from-blue-500 to-blue-600 flex items-center justify-center">
              <span className="text-2xl font-bold text-white">
                {user?.first_name?.[0]}{user?.last_name?.[0]}
              </span>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Mi Perfil</h1>
              <p className="mt-2 text-lg text-gray-600">
                {user?.first_name} {user?.last_name} • {user?.role}
              </p>
            </div>
          </div>
        </div>

        <div className="flex flex-col lg:flex-row gap-8">
          {/* Sidebar */}
          <div className="lg:w-64 flex-shrink-0">
            <nav className="space-y-1">
              {profileTabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200 ${
                      activeTab === tab.id
                        ? 'bg-gradient-to-r from-blue-50 to-purple-50 text-blue-700 border-r-2 border-blue-500 shadow-sm'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900 hover:shadow-sm'
                    }`}
                  >
                    <Icon className={`mr-3 h-5 w-5 ${
                      activeTab === tab.id ? 'text-blue-500' : 'text-gray-400'
                    }`} />
                    {tab.name}
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Content */}
          <div className="flex-1">
            {renderTabContent()}
          </div>
        </div>
      </div>

      {/* Modal de cambio de contraseña */}
      <ChangePasswordModal
        isOpen={showChangePasswordModal}
        onClose={() => setShowChangePasswordModal(false)}
        onSave={handleChangePassword}
        user={user}
        isOwnPassword={true}
      />
    </div>
  );
};

export default Profile;
