import React, { useState, useCallback } from 'react';
import {
  CheckCircleIcon,
  XMarkIcon,
  DocumentTextIcon,
  UserIcon,
  CalendarIcon,
  ExclamationTriangleIcon,
  CheckIcon,
} from '@heroicons/react/24/outline';

/**
 * Formulario optimizado para cierre de incidencias
 * Captura la resolución final y acciones tomadas
 */
const IncidentClosureForm = ({ 
  incident, 
  onSubmit, 
  onCancel, 
  isLoading = false 
}) => {
  const [formData, setFormData] = useState({
    resolution: '',
    actions_taken: '',
    preventive_measures: '',
    responsible_person: '',
    closure_date: new Date().toISOString().split('T')[0],
    closure_notes: '',
    requires_follow_up: false,
    follow_up_date: '',
    follow_up_responsible: '',
  });

  const [errors, setErrors] = useState({});

  // Manejar cambios en el formulario
  const handleChange = useCallback((e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    
    // Limpiar error del campo
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  }, [errors]);

  // Validar formulario
  const validateForm = useCallback(() => {
    const newErrors = {};
    
    if (!formData.resolution.trim()) {
      newErrors.resolution = 'La resolución es obligatoria';
    }
    
    if (!formData.actions_taken.trim()) {
      newErrors.actions_taken = 'Las acciones tomadas son obligatorias';
    }
    
    if (!formData.responsible_person.trim()) {
      newErrors.responsible_person = 'La persona responsable es obligatoria';
    }
    
    if (formData.requires_follow_up && !formData.follow_up_date) {
      newErrors.follow_up_date = 'La fecha de seguimiento es obligatoria si se requiere seguimiento';
    }
    
    if (formData.requires_follow_up && !formData.follow_up_responsible.trim()) {
      newErrors.follow_up_responsible = 'El responsable del seguimiento es obligatorio';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [formData]);

  // Manejar envío del formulario
  const handleSubmit = useCallback((e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    onSubmit({
      ...formData,
      incident_id: incident?.id,
      incident_code: incident?.code,
    });
  }, [formData, validateForm, onSubmit, incident]);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <CheckCircleIcon className="h-6 w-6 text-green-600 mr-3" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Cerrar Incidencia
                </h3>
                <p className="text-sm text-gray-500">
                  {incident?.code} - {incident?.title}
                </p>
              </div>
            </div>
            <button
              onClick={onCancel}
              className="text-gray-400 hover:text-gray-600"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Formulario */}
        <form onSubmit={handleSubmit} className="px-6 py-4 space-y-6">
          {/* Resolución */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <DocumentTextIcon className="h-4 w-4 inline mr-1" />
              Resolución Final *
            </label>
            <textarea
              name="resolution"
              value={formData.resolution}
              onChange={handleChange}
              rows={4}
              className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.resolution ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="Describe la resolución final del problema..."
            />
            {errors.resolution && (
              <p className="mt-1 text-sm text-red-600">{errors.resolution}</p>
            )}
          </div>

          {/* Acciones tomadas */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <CheckIcon className="h-4 w-4 inline mr-1" />
              Acciones Tomadas *
            </label>
            <textarea
              name="actions_taken"
              value={formData.actions_taken}
              onChange={handleChange}
              rows={4}
              className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.actions_taken ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="Detalla las acciones específicas que se tomaron para resolver el problema..."
            />
            {errors.actions_taken && (
              <p className="mt-1 text-sm text-red-600">{errors.actions_taken}</p>
            )}
          </div>

          {/* Medidas preventivas */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <ExclamationTriangleIcon className="h-4 w-4 inline mr-1" />
              Medidas Preventivas
            </label>
            <textarea
              name="preventive_measures"
              value={formData.preventive_measures}
              onChange={handleChange}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Describe las medidas implementadas para prevenir que el problema se repita..."
            />
          </div>

          {/* Persona responsable */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <UserIcon className="h-4 w-4 inline mr-1" />
              Persona Responsable del Cierre *
            </label>
            <input
              type="text"
              name="responsible_person"
              value={formData.responsible_person}
              onChange={handleChange}
              className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.responsible_person ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="Nombre de la persona responsable del cierre"
            />
            {errors.responsible_person && (
              <p className="mt-1 text-sm text-red-600">{errors.responsible_person}</p>
            )}
          </div>

          {/* Fecha de cierre */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <CalendarIcon className="h-4 w-4 inline mr-1" />
              Fecha de Cierre
            </label>
            <input
              type="date"
              name="closure_date"
              value={formData.closure_date}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Notas adicionales */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Notas Adicionales
            </label>
            <textarea
              name="closure_notes"
              value={formData.closure_notes}
              onChange={handleChange}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Cualquier información adicional relevante..."
            />
          </div>

          {/* Seguimiento requerido */}
          <div className="border-t pt-4">
            <div className="flex items-center mb-4">
              <input
                type="checkbox"
                name="requires_follow_up"
                checked={formData.requires_follow_up}
                onChange={handleChange}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label className="ml-2 text-sm font-medium text-gray-700">
                Requiere seguimiento posterior
              </label>
            </div>

            {formData.requires_follow_up && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Fecha de Seguimiento *
                  </label>
                  <input
                    type="date"
                    name="follow_up_date"
                    value={formData.follow_up_date}
                    onChange={handleChange}
                    className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                      errors.follow_up_date ? 'border-red-300' : 'border-gray-300'
                    }`}
                  />
                  {errors.follow_up_date && (
                    <p className="mt-1 text-sm text-red-600">{errors.follow_up_date}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Responsable del Seguimiento *
                  </label>
                  <input
                    type="text"
                    name="follow_up_responsible"
                    value={formData.follow_up_responsible}
                    onChange={handleChange}
                    className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                      errors.follow_up_responsible ? 'border-red-300' : 'border-gray-300'
                    }`}
                    placeholder="Nombre del responsable del seguimiento"
                  />
                  {errors.follow_up_responsible && (
                    <p className="mt-1 text-sm text-red-600">{errors.follow_up_responsible}</p>
                  )}
                </div>
              </div>
            )}
          </div>
        </form>

        {/* Botones */}
        <div className="px-6 py-4 bg-gray-50 rounded-b-lg flex justify-end space-x-3">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Cancelar
          </button>
          <button
            type="submit"
            onClick={handleSubmit}
            disabled={isLoading}
            className="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Cerrando...' : 'Cerrar Incidencia'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default IncidentClosureForm;