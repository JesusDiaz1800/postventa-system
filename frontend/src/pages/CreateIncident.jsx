import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { incidentsAPI } from '../services/api';
import { useNotifications } from '../hooks/useNotifications';
import {
  ArrowLeftIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';

const CreateIncident = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { showSuccess, showError } = useNotifications();
  
  const [formData, setFormData] = useState({
    code: '',
    cliente: '',
    provider: '',
    obra: '',
    sku: '',
    descripcion: '',
    categoria: 'tuberia_beta',
    responsable: 'patricio_morales',
    prioridad: 'media',
    fecha_deteccion: new Date().toISOString().split('T')[0],
    hora_deteccion: new Date().toTimeString().split(' ')[0].substring(0, 5),
  });

  const createIncidentMutation = useMutation({
    mutationFn: incidentsAPI.create,
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
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* Header */}
        <div className="mb-8">
            <button
              onClick={() => navigate('/incidents')}
            className="inline-flex items-center text-sm font-medium text-gray-500 hover:text-gray-700 mb-4"
            >
            <ArrowLeftIcon className="h-4 w-4 mr-2" />
            Volver a Incidencias
            </button>
          <h1 className="text-3xl font-bold text-gray-900">Crear Nueva Incidencia</h1>
          <p className="mt-2 text-gray-600">Complete la información de la nueva incidencia</p>
      </div>

      {/* Form */}
        <div className="bg-white shadow-xl rounded-xl border border-gray-100">
          <form onSubmit={handleSubmit} className="p-8">
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              {/* Código */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Código de Incidencia *
                </label>
                <input
                  type="text"
                  name="code"
                  value={formData.code}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Ej: INC-2025-0001"
                />
              </div>

              {/* Cliente */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cliente *
                </label>
                <input
                  type="text"
                  name="cliente"
                  value={formData.cliente}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Nombre del cliente"
                />
              </div>

              {/* Proveedor */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Proveedor *
                </label>
                <input
                  type="text"
                  name="provider"
                  value={formData.provider}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Nombre del proveedor"
                />
              </div>

              {/* Obra */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Obra/Proyecto *
                </label>
                <input
                  type="text"
                  name="obra"
                  value={formData.obra}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Nombre de la obra o proyecto"
                />
              </div>

              {/* SKU */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  SKU *
                </label>
                <input
                  type="text"
                  name="sku"
                  value={formData.sku}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Código del producto"
                />
              </div>

              {/* Categoría */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Categoría *
                </label>
                <select
                  name="categoria"
                  value={formData.categoria}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
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

              {/* Responsable */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Responsable *
                </label>
                <select
                  name="responsable"
                  value={formData.responsable}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="patricio_morales">Patricio Morales</option>
                  <option value="marco_montenegro">Marco Montenegro</option>
                </select>
              </div>

              {/* Prioridad */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Prioridad
                </label>
                <select
                  name="prioridad"
                  value={formData.prioridad}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="baja">Baja</option>
                  <option value="media">Media</option>
                  <option value="alta">Alta</option>
                  <option value="critica">Crítica</option>
                </select>
              </div>

              {/* Fecha de Detección */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Fecha de Detección *
                </label>
                <input
                  type="date"
                  name="fecha_deteccion"
                  value={formData.fecha_deteccion}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Hora de Detección */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Hora de Detección *
                </label>
                <input
                  type="time"
                  name="hora_deteccion"
                  value={formData.hora_deteccion}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Descripción */}
            <div className="mt-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Descripción del Problema *
              </label>
              <textarea
                name="descripcion"
                value={formData.descripcion}
                onChange={handleChange}
                required
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Describe detalladamente el problema encontrado..."
              />
            </div>
                
            {/* Botones */}
            <div className="mt-8 flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => navigate('/incidents')}
                className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500"
          >
            Cancelar
          </button>
          <button
            type="submit"
                disabled={createIncidentMutation.isPending}
                className="inline-flex items-center px-6 py-2 border border-transparent text-sm font-medium rounded-lg shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
                {createIncidentMutation.isPending ? (
              <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Creando...
              </>
            ) : (
              <>
                    <CheckCircleIcon className="h-4 w-4 mr-2" />
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
