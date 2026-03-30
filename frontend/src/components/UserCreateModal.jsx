import React, { useState } from 'react';
import { XMarkIcon, UserIcon, ShieldCheckIcon, ArrowPathRoundedSquareIcon } from '@heroicons/react/24/outline';
import UserPermissionEditor from './UserPermissionEditor';

const UserCreateModal = ({ isOpen, onClose, onSubmit, isLoading }) => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    role: 'quality',
    phone: '',
    department: '',
    password: '',
    password_confirm: '',
    sap_user: '',
    sap_password: '',
    is_active: true,
    permissions_override: {},
    pages_override: [],
  });

  const [activeTab, setActiveTab] = useState('general');
  const [errors, setErrors] = useState({});

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
    
    if (name === 'username') {
      if (value.toLowerCase() === 'admin') {
        setErrors(prev => ({ ...prev, username: 'El usuario "admin" está reservado.' }));
      } else if (value.includes(' ')) {
        setErrors(prev => ({ ...prev, username: 'Sin espacios, por favor.' }));
      }
    }
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.username.trim()) newErrors.username = 'Requerido';
    if (!formData.email.trim()) newErrors.email = 'Requerido';
    if (!formData.first_name.trim()) newErrors.first_name = 'Requerido';
    if (!formData.last_name.trim()) newErrors.last_name = 'Requerido';
    if (!formData.password.trim()) newErrors.password = 'Requerido';
    if (formData.password.length < 8) newErrors.password = 'Mínimo 8 caracteres';
    if (formData.password !== formData.password_confirm) newErrors.password_confirm = 'No coinciden';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit({
        ...formData,
        password_confirm: formData.password_confirm || formData.password
      });
    }
  };

  const handleClose = () => {
    setFormData({
      username: '',
      email: '',
      first_name: '',
      last_name: '',
      role: 'quality',
      phone: '',
      department: '',
      password: '',
      password_confirm: '',
      sap_user: '',
      sap_password: '',
      is_active: true,
      permissions_override: {},
      pages_override: [],
    });
    setErrors({});
    setActiveTab('general');
    onClose();
  };

  const generateUniqueUsername = () => {
    const firstName = formData.first_name.toLowerCase().replace(/\s+/g, '');
    const lastName = formData.last_name.toLowerCase().replace(/\s+/g, '');
    const timestamp = Date.now().toString().slice(-4);
    
    if (firstName && lastName) {
        setFormData(prev => ({ ...prev, username: `${firstName}.${lastName}${timestamp}` }));
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={handleClose}></div>
        
        <div className="inline-block align-bottom bg-white rounded-3xl text-left overflow-hidden shadow-2xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full border border-white/20">
          <form onSubmit={handleSubmit}>
            <div className="bg-white px-6 pt-6 pb-4 sm:p-8 sm:pb-6">
              <div className="flex items-center justify-between mb-6 border-b border-gray-100 pb-4">
                <div>
                    <h3 className="text-xl font-black text-gray-900 leading-tight tracking-tight">Nuevo Colaborador</h3>
                    <p className="text-xs text-indigo-500 font-bold uppercase tracking-widest">Postventa System</p>
                </div>
                <button
                  type="button"
                  onClick={handleClose}
                  className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-all"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>

              {/* Tabs Navigation */}
              <div className="flex bg-gray-100/80 p-1 rounded-2xl mb-8">
                <button
                  type="button"
                  onClick={() => setActiveTab('general')}
                  className={`flex-1 flex items-center justify-center gap-2 py-2.5 text-[10px] font-black uppercase tracking-[0.2em] rounded-xl transition-all ${
                    activeTab === 'general' 
                      ? 'bg-white text-indigo-600 shadow-md ring-1 ring-black/5' 
                      : 'text-gray-400 hover:text-gray-600'
                  }`}
                >
                  <UserIcon className="h-4 w-4" />
                  Información
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab('permissions')}
                  className={`flex-1 flex items-center justify-center gap-2 py-2.5 text-[10px] font-black uppercase tracking-[0.2em] rounded-xl transition-all ${
                    activeTab === 'permissions' 
                      ? 'bg-white text-indigo-600 shadow-md ring-1 ring-black/5' 
                      : 'text-gray-400 hover:text-gray-600'
                  }`}
                >
                  <ShieldCheckIcon className="h-4 w-4" />
                  Accesos
                </button>
              </div>

              <div className="space-y-4">
                {activeTab === 'general' ? (
                  <div className="space-y-4 animate-fadeIn">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-[10px] font-black text-gray-400 uppercase tracking-wider mb-1.5 ml-1">
                          Nombre
                        </label>
                        <input
                          type="text"
                          name="first_name"
                          value={formData.first_name}
                          onChange={handleInputChange}
                          className={`w-full px-4 py-2.5 bg-gray-50 border rounded-xl text-sm font-medium transition-all ${errors.first_name ? 'border-red-300 ring-1 ring-red-100' : 'border-gray-200'}`}
                        />
                      </div>
                      <div>
                        <label className="block text-[10px] font-black text-gray-400 uppercase tracking-wider mb-1.5 ml-1">
                          Apellido
                        </label>
                        <input
                          type="text"
                          name="last_name"
                          value={formData.last_name}
                          onChange={handleInputChange}
                          className={`w-full px-4 py-2.5 bg-gray-50 border rounded-xl text-sm font-medium transition-all ${errors.last_name ? 'border-red-300 ring-1 ring-red-100' : 'border-gray-200'}`}
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-[10px] font-black text-gray-400 uppercase tracking-wider mb-1.5 ml-1">
                        Nombre de Usuario
                      </label>
                      <div className="flex gap-2">
                        <input
                          type="text"
                          name="username"
                          value={formData.username}
                          onChange={handleInputChange}
                          className={`flex-1 px-4 py-2.5 bg-gray-50 border rounded-xl text-sm font-bold transition-all ${errors.username ? 'border-red-300' : 'border-gray-200'}`}
                        />
                        <button
                          type="button"
                          onClick={generateUniqueUsername}
                          className="px-3 bg-white border border-gray-200 rounded-xl text-[10px] font-black text-indigo-600 hover:bg-indigo-50 transition-colors shadow-sm"
                        >
                          AUTO
                        </button>
                      </div>
                    </div>

                    <div>
                      <label className="block text-[10px] font-black text-gray-400 uppercase tracking-wider mb-1.5 ml-1">
                        Email Corporativo
                      </label>
                      <input
                        type="email"
                        name="email"
                        value={formData.email}
                        onChange={handleInputChange}
                        className={`w-full px-4 py-2.5 bg-gray-50 border rounded-xl text-sm font-medium transition-all ${errors.email ? 'border-red-300' : 'border-gray-200'}`}
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-[10px] font-black text-gray-400 uppercase tracking-wider mb-1.5 ml-1">
                          Rol Inicial
                        </label>
                        <select
                          name="role"
                          value={formData.role}
                          onChange={handleInputChange}
                          className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm font-bold text-gray-700"
                        >
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
                      <div>
                        <label className="block text-[10px] font-black text-gray-400 uppercase tracking-wider mb-1.5 ml-1">
                          Departamento
                        </label>
                        <input
                          type="text"
                          name="department"
                          value={formData.department}
                          onChange={handleInputChange}
                          className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm font-medium"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-[10px] font-black text-gray-400 uppercase tracking-wider mb-1.5 ml-1">
                          Contraseña
                        </label>
                        <input
                          type="password"
                          name="password"
                          value={formData.password}
                          onChange={handleInputChange}
                          className={`w-full px-4 py-2.5 bg-gray-50 border rounded-xl text-sm transition-all ${errors.password ? 'border-red-300' : 'border-gray-200'}`}
                        />
                      </div>
                      <div>
                        <label className="block text-[10px] font-black text-gray-400 uppercase tracking-wider mb-1.5 ml-1">
                          Confirmar
                        </label>
                        <input
                          type="password"
                          name="password_confirm"
                          value={formData.password_confirm}
                          onChange={handleInputChange}
                          className={`w-full px-4 py-2.5 bg-gray-50 border rounded-xl text-sm transition-all ${errors.password_confirm ? 'border-red-300' : 'border-gray-200'}`}
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-100">
                      <div>
                        <label className="block text-[10px] font-black text-indigo-400 uppercase tracking-wider mb-1.5 ml-1">
                          Usuario SAP
                        </label>
                        <input
                          type="text"
                          name="sap_user"
                          value={formData.sap_user}
                          onChange={handleInputChange}
                          className="w-full px-4 py-2.5 bg-indigo-50/30 border border-indigo-100 rounded-xl text-sm font-bold text-indigo-900"
                        />
                      </div>
                      <div>
                        <label className="block text-[10px] font-black text-indigo-400 uppercase tracking-wider mb-1.5 ml-1">
                          Password SAP
                        </label>
                        <input
                          type="password"
                          name="sap_password"
                          value={formData.sap_password}
                          onChange={handleInputChange}
                          className="w-full px-4 py-2.5 bg-indigo-50/30 border border-indigo-100 rounded-xl text-sm font-bold text-indigo-900"
                        />
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="animate-fadeIn">
                    <UserPermissionEditor 
                        user={{ role: formData.role }} // Mock user with selected role
                        permissions_override={formData.permissions_override}
                        pages_override={formData.pages_override}
                        onPermissionsChange={(newPerms) => setFormData(p => ({ ...p, permissions_override: newPerms }))}
                        onPagesChange={(newPages) => setFormData(p => ({ ...p, pages_override: newPages }))}
                    />
                  </div>
                )}
              </div>
            </div>
            
            <div className="bg-gray-50/50 px-8 py-6 flex flex-col sm:flex-row-reverse gap-3 border-t border-gray-100">
              <button
                type="submit"
                disabled={isLoading}
                className="flex-1 sm:flex-none inline-flex justify-center items-center px-8 py-3 bg-indigo-600 text-xs font-black uppercase tracking-widest text-white rounded-2xl shadow-lg shadow-indigo-200 hover:bg-indigo-700 hover:shadow-xl transition-all disabled:opacity-50"
              >
                {isLoading ? 'Creando...' : 'Crear Colaborador'}
              </button>
              <button
                type="button"
                onClick={handleClose}
                className="flex-1 sm:flex-none inline-flex justify-center items-center px-8 py-3 bg-white border border-gray-200 text-xs font-black uppercase tracking-widest text-gray-500 rounded-2xl hover:bg-gray-50 transition-all"
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default UserCreateModal;