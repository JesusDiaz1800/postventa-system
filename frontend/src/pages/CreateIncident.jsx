import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { incidentsAPI } from '../services/api';
import { useNotifications } from '../hooks/useNotifications';
import {
  ArrowLeftIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  UserIcon,
  BuildingOfficeIcon,
  DocumentTextIcon,
  TagIcon,
  CalendarIcon,
  ClockIcon,
  ExclamationCircleIcon,
  PlusIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';

const CreateIncident = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { showSuccess, showError } = useNotifications();
  
  const [formData, setFormData] = useState({
    cliente: '',
    provider: '',
    obra: '',
    proyecto: '',
    descripcion: '',
    categoria: 'tuberia_beta',
    subcategoria: '',
    responsable: 'patricio_morales',
    prioridad: 'media',
    fecha_deteccion: new Date().toISOString().split('T')[0],
    hora_deteccion: new Date().toTimeString().split(' ')[0].substring(0, 5),
  });

  // Estados para el formulario mejorado
  const [showAdvancedFields, setShowAdvancedFields] = useState(false);

  // Generar código automático
  const generateCode = () => {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
    return `INC-${year}${month}${day}-${random}`;
  };

  const createIncidentMutation = useMutation({
    mutationFn: (data) => {
      // Limpiar datos antes de enviar
      const cleanData = { ...data };
      
      // Remover campos que pueden causar problemas
      delete cleanData.categoria; // El backend maneja esto internamente
      delete cleanData.responsable; // El backend maneja esto internamente
      
      // Asegurar que los campos requeridos estén presentes
      if (!cleanData.obra) {
        cleanData.obra = 'Obra por defecto';
      }
      if (!cleanData.descripcion) {
        cleanData.descripcion = 'Descripción por defecto';
      }
      
      return incidentsAPI.create(cleanData);
    },
    onSuccess: () => {
      showSuccess('Incidencia creada exitosamente');
      queryClient.invalidateQueries(['incidents']);
      navigate('/incidents');
    },
    onError: (error) => {
      showError('Error al crear la incidencia: ' + (error.message || 'Error desconocido'));
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    createIncidentMutation.mutate(formData);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header Mejorado */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/incidents')}
            className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:text-gray-900 transition-all duration-200 mb-6"
          >
            <ArrowLeftIcon className="h-4 w-4 mr-2" />
            Volver a Incidencias
          </button>
          
          <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-8">
            <div className="flex items-center mb-6">
              <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg mr-4">
                <PlusIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Nueva Incidencia</h1>
                <p className="text-gray-600 mt-1">
                  Complete la información para crear una nueva incidencia en el sistema
                </p>
              </div>
            </div>
            
            {/* Indicador de progreso */}
            <div className="flex items-center space-x-4 mb-6">
              <div className="flex items-center">
                <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                  1
                </div>
                <span className="ml-2 text-sm font-medium text-gray-900">Información Básica</span>
              </div>
              <div className="flex-1 h-px bg-gray-200"></div>
              <div className="flex items-center">
                <div className="w-8 h-8 bg-gray-200 text-gray-500 rounded-full flex items-center justify-center text-sm font-medium">
                  2
                </div>
                <span className="ml-2 text-sm font-medium text-gray-500">Detalles Adicionales</span>
              </div>
            </div>
          </div>
        </div>

        {/* Formulario Mejorado */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
          <form onSubmit={handleSubmit} className="p-8">
            {/* Sección 1: Información Básica */}
            <div className="mb-8">
              <div className="flex items-center mb-6">
                <div className="flex items-center justify-center w-8 h-8 bg-blue-100 rounded-lg mr-3">
                  <UserIcon className="h-4 w-4 text-blue-600" />
                </div>
                <h2 className="text-xl font-semibold text-gray-900">Información Básica</h2>
              </div>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Código */}
                <div className="lg:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <TagIcon className="h-4 w-4 inline mr-1" />
                    Código de Incidencia
                  </label>
                  <div className="relative">
                    <input
                      type="text"
                      value="Se generará automáticamente"
                      disabled
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50 text-gray-600 font-mono"
                      placeholder="Ej: INC-2025-0001"
                    />
                    <div className="absolute inset-y-0 right-0 flex items-center pr-3">
                      <CheckCircleIcon className="h-5 w-5 text-green-500" />
                    </div>
                  </div>
                  <p className="text-xs text-gray-500 mt-2 flex items-center">
                    <ExclamationCircleIcon className="h-3 w-3 mr-1" />
                    El código se genera automáticamente al crear la incidencia
                  </p>
                </div>

                {/* Cliente */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <UserIcon className="h-4 w-4 inline mr-1" />
                    Cliente *
                  </label>
                  <input
                    type="text"
                    name="cliente"
                    value={formData.cliente}
                    onChange={handleChange}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                    placeholder="Nombre del cliente"
                  />
                </div>

                {/* Proveedor */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <BuildingOfficeIcon className="h-4 w-4 inline mr-1" />
                    Proveedor
                  </label>
                  <input
                    type="text"
                    name="provider"
                    value={formData.provider}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                    placeholder="Nombre del proveedor"
                  />
                </div>

                {/* Obra y Proyecto */}
                <div className="lg:col-span-2">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        <BuildingOfficeIcon className="h-4 w-4 inline mr-1" />
                        Obra
                      </label>
                      <input
                        type="text"
                        name="obra"
                        value={formData.obra}
                        onChange={handleChange}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                        placeholder="Nombre de la obra"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        <DocumentTextIcon className="h-4 w-4 inline mr-1" />
                        Proyecto
                      </label>
                      <input
                        type="text"
                        name="proyecto"
                        value={formData.proyecto}
                        onChange={handleChange}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                        placeholder="Nombre del proyecto"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Sección 2: Categorización */}
            <div className="mb-8">
              <div className="flex items-center mb-6">
                <div className="flex items-center justify-center w-8 h-8 bg-green-100 rounded-lg mr-3">
                  <TagIcon className="h-4 w-4 text-green-600" />
                </div>
                <h2 className="text-xl font-semibold text-gray-900">Categorización</h2>
              </div>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">


                {/* Categoría */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <TagIcon className="h-4 w-4 inline mr-1" />
                    Categoría *
                  </label>
                  <select
                    name="categoria"
                    value={formData.categoria}
                    onChange={handleChange}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                  >
                    <option value="tuberia_beta">Tubería BETA</option>
                    <option value="tuberia_ppr">Tubería PPR</option>
                    <option value="tuberia_hdpe">Tubería HDPE</option>
                    <option value="fitting_inserto_metalico">Fitting con inserto metálico</option>
                    <option value="fitting_ppr">Fitting PPR</option>
                    <option value="fitting_hdpe_electrofusion">Fitting HDPE Electrofusión</option>
                    <option value="fitting_hdpe_fusion_tope">Fitting HDPE Fusión Tope</option>
                    <option value="llave">LLave</option>
                    <option value="flange">Flange</option>
                    <option value="inserto_metalico">Inserto metálico</option>
                    <option value="otro">Otro</option>
                  </select>
                </div>

                {/* Subcategoría - Campo Manual */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <DocumentTextIcon className="h-4 w-4 inline mr-1" />
                    Subcategoría
                  </label>
                  <input
                    type="text"
                    name="subcategoria"
                    value={formData.subcategoria}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                    placeholder="Describa el tipo específico de problema"
                  />
                </div>
              </div>
            </div>

            {/* Sección 3: Detalles de la Incidencia */}
            <div className="mb-8">
              <div className="flex items-center mb-6">
                <div className="flex items-center justify-center w-8 h-8 bg-purple-100 rounded-lg mr-3">
                  <ExclamationCircleIcon className="h-4 w-4 text-purple-600" />
                </div>
                <h2 className="text-xl font-semibold text-gray-900">Detalles de la Incidencia</h2>
              </div>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                {/* Responsable */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <UserIcon className="h-4 w-4 inline mr-1" />
                    Responsable *
                  </label>
                  <select
                    name="responsable"
                    value={formData.responsable}
                    onChange={handleChange}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                  >
                    <option value="patricio_morales">Patricio Morales</option>
                    <option value="marco_montenegro">Marco Montenegro</option>
                  </select>
                </div>

                {/* Prioridad */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <ExclamationTriangleIcon className="h-4 w-4 inline mr-1" />
                    Prioridad
                  </label>
                  <select
                    name="prioridad"
                    value={formData.prioridad}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                  >
                    <option value="baja">🟢 Baja</option>
                    <option value="media">🟡 Media</option>
                    <option value="alta">🟠 Alta</option>
                    <option value="critica">🔴 Crítica</option>
                  </select>
                </div>

                {/* Fecha de Detección */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <CalendarIcon className="h-4 w-4 inline mr-1" />
                    Fecha de Detección *
                  </label>
                  <input
                    type="date"
                    name="fecha_deteccion"
                    value={formData.fecha_deteccion}
                    onChange={handleChange}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                  />
                </div>

                {/* Hora de Detección */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <ClockIcon className="h-4 w-4 inline mr-1" />
                    Hora de Detección *
                  </label>
                  <input
                    type="time"
                    name="hora_deteccion"
                    value={formData.hora_deteccion}
                    onChange={handleChange}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                  />
                </div>
              </div>
            </div>

            {/* Sección 4: Descripción */}
            <div className="mb-8">
              <div className="flex items-center mb-6">
                <div className="flex items-center justify-center w-8 h-8 bg-orange-100 rounded-lg mr-3">
                  <DocumentTextIcon className="h-4 w-4 text-orange-600" />
                </div>
                <h2 className="text-xl font-semibold text-gray-900">Descripción de la Incidencia</h2>
              </div>
              
              <div>
            </div>

                {/* Descripción */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <DocumentTextIcon className="h-4 w-4 inline mr-1" />
                    Descripción del Problema *
                  </label>
                  <textarea
                    name="descripcion"
                    value={formData.descripcion}
                    onChange={handleChange}
                    required
                    rows={5}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors resize-none"
                    placeholder="Describa detalladamente la incidencia, incluyendo síntomas, ubicación, y cualquier información relevante..."
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Mínimo 10 caracteres. Sea específico y detallado para facilitar la resolución.
                  </p>
                </div>
              </div>

            {/* Botones de Acción Mejorados */}
            <div className="flex flex-col sm:flex-row gap-4 pt-6 border-t border-gray-200">
              <button
                type="button"
                onClick={() => navigate('/incidents')}
                className="flex-1 sm:flex-none px-6 py-3 border border-gray-300 text-gray-700 bg-white rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 transition-all duration-200 font-medium"
              >
                <XMarkIcon className="h-4 w-4 inline mr-2" />
                Cancelar
              </button>
              <button
                type="submit"
                disabled={createIncidentMutation.isPending}
                className="flex-1 sm:flex-none px-8 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200 font-medium shadow-lg hover:shadow-xl transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
              >
                {createIncidentMutation.isPending ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Creando...
                  </>
                ) : (
                  <>
                    <CheckCircleIcon className="h-4 w-4 inline mr-2" />
                    Crear Incidencia
                  </>
                )}
              </button>
            </div>
      </form>
        </div>
      </div>
    </div>
  );
};

export default CreateIncident;

