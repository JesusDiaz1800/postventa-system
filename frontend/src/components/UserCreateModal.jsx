import React, { useState } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';

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
    is_active: true,
  });

  const [errors, setErrors] = useState({});

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
    
    // Real-time validation for username
    if (name === 'username') {
      if (value.toLowerCase() === 'admin') {
        setErrors(prev => ({ 
          ...prev, 
          username: 'El nombre de usuario "admin" ya existe. Por favor, elige otro nombre.' 
        }));
      } else if (value.includes(' ')) {
        setErrors(prev => ({ 
          ...prev, 
          username: 'El nombre de usuario no puede contener espacios. Usa puntos, guiones o números.' 
        }));
      } else if (value.length > 0 && value.length < 3) {
        setErrors(prev => ({ 
          ...prev, 
          username: 'El nombre de usuario debe tener al menos 3 caracteres.' 
        }));
      }
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.username.trim()) newErrors.username = 'El nombre de usuario es requerido';
    if (!formData.email.trim()) newErrors.email = 'El email es requerido';
    if (!formData.first_name.trim()) newErrors.first_name = 'El nombre es requerido';
    if (!formData.last_name.trim()) newErrors.last_name = 'El apellido es requerido';
    if (!formData.password.trim()) newErrors.password = 'La contraseña es requerida';
    if (formData.password.length < 8) newErrors.password = 'La contraseña debe tener al menos 8 caracteres';
    if (formData.password !== formData.password_confirm) newErrors.password_confirm = 'Las contraseñas no coinciden';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit(formData);
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
      is_active: true,
    });
    setErrors({});
    onClose();
  };

  const generateUniqueUsername = () => {
    const firstName = formData.first_name.toLowerCase().replace(/\s+/g, '');
    const lastName = formData.last_name.toLowerCase().replace(/\s+/g, '');
    const timestamp = Date.now().toString().slice(-4);
    
    // Generate username without spaces, using dots or underscores
    let suggestedUsername;
    if (firstName && lastName) {
      suggestedUsername = `${firstName}.${lastName}${timestamp}`;
    } else if (firstName) {
      suggestedUsername = `${firstName}${timestamp}`;
    } else {
      suggestedUsername = `user${timestamp}`;
    }
    
    setFormData(prev => ({
      ...prev,
      username: suggestedUsername
    }));
    
    // Clear any existing username error
    if (errors.username) {
      setErrors(prev => ({ ...prev, username: '' }));
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={handleClose}></div>
        
        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div className="sm:flex sm:items-start">
              <div className="mt-3 text-center sm:mt-0 sm:text-left w-full">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">
                    Crear Nuevo Usuario
                  </h3>
                  <button
                    onClick={handleClose}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <XMarkIcon className="h-6 w-6" />
                  </button>
                </div>
                
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div>
                      <label htmlFor="first_name" className="block text-sm font-medium text-gray-700">
                        Nombre *
                      </label>
                      <input
                        type="text"
                        name="first_name"
                        id="first_name"
                        value={formData.first_name}
                        onChange={handleInputChange}
                        className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                          errors.first_name ? 'border-red-300' : 'border-gray-300'
                        }`}
                        placeholder="Nombre del usuario"
                      />
                      {errors.first_name && (
                        <p className="mt-1 text-sm text-red-600">{errors.first_name}</p>
                      )}
                    </div>
                    
                    <div>
                      <label htmlFor="last_name" className="block text-sm font-medium text-gray-700">
                        Apellido *
                      </label>
                      <input
                        type="text"
                        name="last_name"
                        id="last_name"
                        value={formData.last_name}
                        onChange={handleInputChange}
                        className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                          errors.last_name ? 'border-red-300' : 'border-gray-300'
                        }`}
                        placeholder="Apellido del usuario"
                      />
                      {errors.last_name && (
                        <p className="mt-1 text-sm text-red-600">{errors.last_name}</p>
                      )}
                    </div>
                  </div>

                  <div>
                    <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                      Nombre de Usuario *
                    </label>
                    <div className="mt-1 flex rounded-md shadow-sm">
                      <input
                        type="text"
                        name="username"
                        id="username"
                        value={formData.username}
                        onChange={handleInputChange}
                        className={`flex-1 block w-full px-3 py-2 border rounded-l-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                          errors.username ? 'border-red-300' : 'border-gray-300'
                        }`}
                        placeholder="usuario"
                      />
                      <button
                        type="button"
                        onClick={generateUniqueUsername}
                        className="inline-flex items-center px-3 py-2 border border-l-0 border-gray-300 rounded-r-md bg-gray-50 text-gray-500 text-sm hover:bg-gray-100"
                      >
                        Generar
                      </button>
                    </div>
                    {errors.username && (
                      <p className="mt-1 text-sm text-red-600">{errors.username}</p>
                    )}
                  </div>

                  <div>
                    <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                      Email *
                    </label>
                    <input
                      type="email"
                      name="email"
                      id="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                        errors.email ? 'border-red-300' : 'border-gray-300'
                      }`}
                      placeholder="usuario@empresa.com"
                    />
                    {errors.email && (
                      <p className="mt-1 text-sm text-red-600">{errors.email}</p>
                    )}
                  </div>

                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div>
                      <label htmlFor="role" className="block text-sm font-medium text-gray-700">
                        Rol *
                      </label>
                      <select
                        name="role"
                        id="role"
                        value={formData.role}
                        onChange={handleInputChange}
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
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
                      <label htmlFor="department" className="block text-sm font-medium text-gray-700">
                        Departamento
                      </label>
                      <input
                        type="text"
                        name="department"
                        id="department"
                        value={formData.department}
                        onChange={handleInputChange}
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                        placeholder="Departamento"
                      />
                    </div>
                  </div>

                  <div>
                    <label htmlFor="phone" className="block text-sm font-medium text-gray-700">
                      Teléfono
                    </label>
                    <input
                      type="tel"
                      name="phone"
                      id="phone"
                      value={formData.phone}
                      onChange={handleInputChange}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      placeholder="+56 9 1234 5678"
                    />
                  </div>

                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div>
                      <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                        Contraseña *
                      </label>
                      <input
                        type="password"
                        name="password"
                        id="password"
                        value={formData.password}
                        onChange={handleInputChange}
                        className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                          errors.password ? 'border-red-300' : 'border-gray-300'
                        }`}
                        placeholder="Mínimo 8 caracteres"
                      />
                      {errors.password && (
                        <p className="mt-1 text-sm text-red-600">{errors.password}</p>
                      )}
                    </div>
                    
                    <div>
                      <label htmlFor="password_confirm" className="block text-sm font-medium text-gray-700">
                        Confirmar Contraseña *
                      </label>
                      <input
                        type="password"
                        name="password_confirm"
                        id="password_confirm"
                        value={formData.password_confirm}
                        onChange={handleInputChange}
                        className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                          errors.password_confirm ? 'border-red-300' : 'border-gray-300'
                        }`}
                        placeholder="Repetir contraseña"
                      />
                      {errors.password_confirm && (
                        <p className="mt-1 text-sm text-red-600">{errors.password_confirm}</p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      name="is_active"
                      id="is_active"
                      checked={formData.is_active}
                      onChange={handleInputChange}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">
                      Usuario activo
                    </label>
                  </div>
                </form>
              </div>
            </div>
          </div>
          
          <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button
              type="button"
              onClick={handleSubmit}
              disabled={isLoading}
              className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Creando...' : 'Crear Usuario'}
            </button>
            <button
              type="button"
              onClick={handleClose}
              className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
            >
              Cancelar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserCreateModal;