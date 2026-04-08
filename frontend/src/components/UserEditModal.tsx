import React, { useState, useEffect } from 'react';
import { XMarkIcon, UserIcon, ShieldCheckIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import UserPermissionEditor from './UserPermissionEditor';

const UserEditModal = ({ isOpen, onClose, onSubmit, user, isLoading }) => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    role: '',
    phone: '',
    department: '',
    is_active: true,
    sap_user: '',
    sap_password: '',
    digital_signature: null,
    permissions_override: {},
    pages_override: [],
  });

  const [activeTab, setActiveTab] = useState('general');
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (user) {
      setFormData({
        username: user.username || '',
        email: user.email || '',
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        role: user.role || '',
        phone: user.phone || '',
        department: user.department || '',
        is_active: user.is_active ?? true,
        sap_user: user.sap_user || '',
        sap_password: '', // Always reset for security, only send if changed
        digital_signature: user.digital_signature || null,
        permissions_override: user.permissions_override || {},
        pages_override: user.pages_override || [],
      });
      setErrors({});
    }
  }, [user, isOpen]);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));

    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.username.trim()) newErrors.username = 'El usuario es requerido';
    if (!formData.email.trim()) newErrors.email = 'El email es requerido';
    else if (!/\S+@\S+\.\S+/.test(formData.email)) newErrors.email = 'Email inválido';
    if (!formData.first_name.trim()) newErrors.first_name = 'El nombre es requerido';
    if (!formData.last_name.trim()) newErrors.last_name = 'El apellido es requerido';
    if (!formData.role) newErrors.role = 'El rol es requerido';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      const submitData = new FormData();

      Object.keys(formData).forEach(key => {
        if (key === 'digital_signature') {
          if (formData[key] instanceof File) {
            submitData.append(key, formData[key]);
          }
        } else if (key === 'sap_password') {
          if (formData[key]) submitData.append(key, formData[key]); // Solo enviar si cambió explícitamente y no está vacío
        } else if (key === 'permissions_override' || key === 'pages_override') {
          submitData.append(key, JSON.stringify(formData[key]));
        } else {
          submitData.append(key, formData[key] !== null ? formData[key] : '');
        }
      });

      onSubmit(submitData);
    }
  };

  const handleClose = () => {
    setErrors({});
    onClose();
  };

  if (!isOpen || !user) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={handleClose}></div>

        <div className="inline-block align-bottom bg-white rounded-3xl text-left overflow-hidden shadow-2xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full border border-white/20">
          <form onSubmit={handleSubmit}>
            <div className="bg-white px-6 pt-6 pb-4 sm:p-8 sm:pb-6">
              <div className="flex items-center justify-between mb-6 border-b border-gray-100 pb-4">
                <div>
                    <h3 className="text-xl font-black text-gray-900 leading-tight">Perfil de Usuario</h3>
                    <p className="text-xs text-gray-500 font-medium">Gestión de datos y capacidades</p>
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

              <div className="space-y-5">
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
                          className={`w-full px-4 py-2.5 bg-gray-50 border rounded-xl text-sm font-medium focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all ${errors.first_name ? 'border-red-300 bg-red-50/30' : 'border-gray-200'}`}
                        />
                        {errors.first_name && <p className="text-red-500 text-[10px] font-bold mt-1 ml-1">{errors.first_name}</p>}
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
                          className={`w-full px-4 py-2.5 bg-gray-50 border rounded-xl text-sm font-medium focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all ${errors.last_name ? 'border-red-300 bg-red-50/30' : 'border-gray-200'}`}
                        />
                        {errors.last_name && <p className="text-red-500 text-[10px] font-bold mt-1 ml-1">{errors.last_name}</p>}
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-[10px] font-black text-gray-400 uppercase tracking-wider mb-1.5 ml-1">
                                Usuario
                            </label>
                            <input
                                type="text"
                                name="username"
                                value={formData.username}
                                onChange={handleInputChange}
                                className={`w-full px-4 py-2.5 bg-gray-50 border rounded-xl text-sm font-medium focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all ${errors.username ? 'border-red-300 bg-red-50/30' : 'border-gray-200'}`}
                            />
                            {errors.username && <p className="text-red-500 text-[10px] font-bold mt-1 ml-1">{errors.username}</p>}
                        </div>
                        <div>
                            <label className="block text-[10px] font-black text-gray-400 uppercase tracking-wider mb-1.5 ml-1">
                                Rol
                            </label>
                            <select
                                name="role"
                                value={formData.role}
                                onChange={handleInputChange}
                                className={`w-full px-4 py-2.5 bg-gray-50 border rounded-xl text-sm font-bold text-gray-700 focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all ${errors.role ? 'border-red-300 bg-red-50/30' : 'border-gray-200'}`}
                            >
                                <option value="">Seleccionar Rol</option>
                                <option value="admin">Administrador</option>
                                <option value="management">Gerencia</option>
                                <option value="technical_service">Servicio Técnico</option>
                                <option value="quality">Calidad</option>
                                <option value="supervisor">Supervisor</option>
                                <option value="analyst">Analista</option>
                                <option value="customer_service">Atención al Cliente</option>
                                <option value="provider">Proveedor</option>
                            </select>
                            {errors.role && <p className="text-red-500 text-[10px] font-bold mt-1 ml-1">{errors.role}</p>}
                        </div>
                    </div>

                    <div>
                      <label className="block text-[10px] font-black text-gray-400 uppercase tracking-wider mb-1.5 ml-1">
                        Email Coorporativo
                      </label>
                      <input
                        type="email"
                        name="email"
                        value={formData.email}
                        onChange={handleInputChange}
                        className={`w-full px-4 py-2.5 bg-gray-50 border rounded-xl text-sm font-medium focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all ${errors.email ? 'border-red-300 bg-red-50/30' : 'border-gray-200'}`}
                      />
                      {errors.email && <p className="text-red-500 text-[10px] font-bold mt-1 ml-1">{errors.email}</p>}
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-[10px] font-black text-gray-400 uppercase tracking-wider mb-1.5 ml-1">
                          Teléfono
                        </label>
                        <input
                          type="tel"
                          name="phone"
                          value={formData.phone}
                          onChange={handleInputChange}
                          className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm font-medium focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all"
                        />
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
                          className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm font-medium focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all"
                        />
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-100">
                      <div>
                        <label className="block text-[10px] font-black text-indigo-400 uppercase tracking-wider mb-1.5 ml-1">
                          Usuario SAP SL
                        </label>
                        <input
                          type="text"
                          name="sap_user"
                          value={formData.sap_user}
                          onChange={handleInputChange}
                          className="w-full px-4 py-2.5 bg-indigo-50/30 border border-indigo-100 rounded-xl text-sm font-bold text-indigo-900 focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all"
                        />
                      </div>

                      <div>
                        <label className="block text-[10px] font-black text-indigo-400 uppercase tracking-wider mb-1.5 ml-1">
                          Password SAP SL
                        </label>
                        <input
                          type="password"
                          name="sap_password"
                          value={formData.sap_password}
                          onChange={handleInputChange}
                          className="w-full px-4 py-2.5 bg-indigo-50/30 border border-indigo-100 rounded-xl text-sm font-bold text-indigo-900 focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all"
                        />
                      </div>
                    </div>

                    <div className="flex items-center p-4 bg-gray-50 rounded-2xl border border-gray-100">
                      <input
                        type="checkbox"
                        id="is_active_check"
                        name="is_active"
                        checked={formData.is_active}
                        onChange={handleInputChange}
                        className="h-5 w-5 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded-lg transition-all"
                      />
                      <label htmlFor="is_active_check" className="ml-3 block text-sm font-bold text-gray-700 cursor-pointer">
                        Estado Activo del Usuario
                      </label>
                    </div>

                    <div className="pt-4">
                      <label className="block text-[10px] font-black text-gray-400 uppercase tracking-wider mb-3 ml-1">
                        Certificación Digital / Firma
                      </label>
                      <div className="flex items-center gap-6 p-4 bg-gray-50 rounded-2xl border border-dashed border-gray-300">
                        {user.digital_signature && (
                          <div className="flex-shrink-0">
                            <img
                              src={user.digital_signature}
                              alt="Firma"
                              className="h-14 w-auto object-contain rounded-lg shadow-sm bg-white"
                            />
                          </div>
                        )}
                        <div className="flex-1">
                            <input
                            type="file"
                            id="file-upload"
                            name="digital_signature"
                            accept="image/*"
                            onChange={(e) => {
                                const file = e.target.files[0];
                                if (file) setFormData(prev => ({ ...prev, digital_signature: file }));
                            }}
                            className="hidden"
                            />
                            <label 
                                htmlFor="file-upload"
                                className="inline-flex items-center px-4 py-2 bg-white border border-gray-200 rounded-xl text-xs font-black text-indigo-600 shadow-sm hover:shadow-md hover:bg-indigo-50 transition-all cursor-pointer"
                            >
                                Seleccionar Archivo
                            </label>
                            <p className="mt-2 text-[10px] text-gray-400 font-medium">Recomendado: Fondo transparente (PNG)</p>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="animate-fadeIn">
                    <UserPermissionEditor 
                        user={user}
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
                className="flex-1 sm:flex-none inline-flex justify-center items-center px-8 py-3 bg-indigo-600 text-xs font-black uppercase tracking-widest text-white rounded-2xl shadow-lg shadow-indigo-200 hover:bg-indigo-700 hover:shadow-xl focus:ring-4 focus:ring-indigo-500/20 transition-all disabled:opacity-50"
              >
                {isLoading ? (
                    <>
                        <ArrowPathIcon className="h-4 w-4 animate-spin mr-2" />
                        Guardando...
                    </>
                ) : 'Guardar Cambios'}
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

export default UserEditModal;
