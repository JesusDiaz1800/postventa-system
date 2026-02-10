import React, { useState, useCallback } from 'react';
import {
  CheckCircleIcon,
  XMarkIcon,
  DocumentTextIcon,
  UserIcon,
  CalendarIcon,
  ExclamationTriangleIcon,
  CheckIcon,
  ListBulletIcon,
  FlagIcon,
  ChatBubbleBottomCenterTextIcon,
  PaperClipIcon
} from '@heroicons/react/24/outline';

/**
 * Formulario optimizado para cierre de incidencias
 * Incluye campos detallados: Motivo, Resultado, Conclusión
 */
const IncidentClosureForm = ({
  incident,
  onSubmit,
  onCancel,
  isLoading = false
}) => {
  // Determinar etapa inicial basada en el estado de la incidencia
  const getInitialStage = () => {
    if (!incident?.estado) return 'incidencia';
    const status = incident.estado;
    if (status === 'escalado_proveedor' || status === 'en_proveedor' || status === 'proveedor') return 'proveedor';
    if (status === 'escalado_calidad' || status === 'en_calidad' || status === 'laboratorio') return 'calidad';
    if (status === 'en_proceso' || status === 'reporte_visita') return 'reporte_visita';
    return 'incidencia';
  };

  const [formData, setFormData] = useState({
    stage: getInitialStage(), // Inicializar correctamente
    closure_reason: '',
    closure_result: '',
    conclusions: '',
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

    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  }, [errors]);

  // Validar formulario
  const validateForm = useCallback(() => {
    const newErrors = {};

    if (!formData.closure_reason) newErrors.closure_reason = 'El motivo de cierre es obligatorio';
    if (!formData.closure_result) newErrors.closure_result = 'El resultado es obligatorio';
    if (!formData.conclusions.trim()) newErrors.conclusions = 'La conclusión es obligatoria';
    if (!formData.resolution.trim()) newErrors.resolution = 'La resolución es obligatoria';
    if (!formData.actions_taken.trim()) newErrors.actions_taken = 'Las acciones tomadas son obligatorias';
    if (!formData.responsible_person.trim()) newErrors.responsible_person = 'La persona responsable es obligatoria';

    if (formData.requires_follow_up) {
      if (!formData.follow_up_date) newErrors.follow_up_date = 'La fecha de seguimiento es obligatoria';
      if (!formData.follow_up_responsible.trim()) newErrors.follow_up_responsible = 'El responsable es obligatorio';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [formData]);

  // Manejar envío del formulario
  const handleSubmit = useCallback((e) => {
    e.preventDefault();
    if (!validateForm()) return;

    // Formatear el resumen completo para el backend
    const structuredSummary = `
[CIERRE DETALLADO]
Motivo: ${formData.closure_reason}
Resultado: ${formData.closure_result}

--- CONCLUSIONES ---
${formData.conclusions}

--- RESOLUCIÓN ---
${formData.resolution}

--- ACCIONES TOMADAS ---
${formData.actions_taken}

--- MEDIDAS PREVENTIVAS ---
${formData.preventive_measures}

--- NOTAS ADICIONALES ---
${formData.closure_notes}
    `.trim();

    onSubmit({
      incident_id: incident?.id,
      stage: formData.stage, // Usar la etapa seleccionada por el usuario
      closure_summary: structuredSummary,
      // Pasamos los datos crudos por si el componente padre quiere usarlos individualmente
      raw_data: formData,
      closure_date: formData.closure_date
    });
  }, [formData, validateForm, onSubmit, incident]);

  return (
    <div className="fixed inset-0 bg-gray-900/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white/95 backdrop-blur-xl rounded-2xl shadow-[0_25px_60px_-15px_rgba(0,0,0,0.25)] w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col border border-white/40 animate-in fade-in zoom-in-95 duration-200">
        {/* Header - Premium Green Gradient */}
        <div className="px-6 py-4 bg-gradient-to-r from-emerald-600 to-green-600 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/20 backdrop-blur-md rounded-xl shadow-inner">
              <CheckCircleIcon className="h-6 w-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-white">Cerrar Incidencia</h3>
              <p className="text-sm text-emerald-100 font-medium">{incident?.code} - {incident?.cliente}</p>
            </div>
          </div>
          <button onClick={onCancel} className="text-white/70 hover:text-white p-1 rounded-lg hover:bg-white/10 transition-colors">
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        {/* Formulario - Scrollable Body */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto px-6 py-6 space-y-5">

          {/* Etapa de Cierre (Selector) */}
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-100">
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Etapa de Cierre <span className="text-red-500">*</span>
            </label>
            <select
              name="stage"
              value={formData.stage}
              onChange={handleChange}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white"
            >
              <option value="incidencia">Incidencia (Interna)</option>
              <option value="reporte_visita">Reporte de Visita</option>
              <option value="calidad">Calidad (Laboratorio)</option>
              <option value="proveedor">Proveedor</option>
            </select>
            <p className="mt-1 text-xs text-blue-600">
              Confirma en qué etapa se está cerrando el caso.
            </p>
          </div>

          {/* Archivo Adjunto */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              <PaperClipIcon className="h-4 w-4 inline mr-1.5 text-gray-500" />
              Adjuntar Archivo de Cierre (Opcional)
            </label>
            <div className="flex items-center gap-3">
              <input
                type="file"
                name="closure_attachment"
                id="closure_attachment"
                onChange={handleChange}
                className="hidden"
              />
              <label
                htmlFor="closure_attachment"
                className="px-4 py-2 bg-gray-100 text-gray-700 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-200 transition-colors text-sm font-medium"
              >
                Elegir Archivo...
              </label>
              {formData.closure_attachment ? (
                <span className="text-sm text-green-600 font-medium truncate max-w-xs block">
                  {formData.closure_attachment.name}
                </span>
              ) : (
                <span className="text-sm text-gray-400 italic">Ningún archivo seleccionado</span>
              )}
            </div>
          </div>


          {/* Fila 1: Motivo y Resultado */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                <ListBulletIcon className="h-4 w-4 inline mr-1.5 text-blue-500" />
                Motivo de Cierre *
              </label>
              <select
                name="closure_reason"
                value={formData.closure_reason}
                onChange={handleChange}
                className={`w-full px-4 py-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 transition-all ${errors.closure_reason ? 'border-red-300' : 'border-gray-300'}`}
              >
                <option value="">Seleccione un motivo...</option>
                <option value="Solucionado Definitivamente">Solucionado Definitivamente</option>
                <option value="Solucion Palliata">Solución Paliativa</option>
                <option value="Rechazado por Cliente">Rechazado por Cliente</option>
                <option value="No Procede (Falsa Alarma)">No Procede (Falsa Alarma)</option>
                <option value="Duplicado">Duplicado</option>
                <option value="Otro">Otro</option>
              </select>
              {errors.closure_reason && <p className="mt-1 text-sm text-red-600 animate-pulse">{errors.closure_reason}</p>}
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                <FlagIcon className="h-4 w-4 inline mr-1.5 text-blue-500" />
                Resultado Final *
              </label>
              <select
                name="closure_result"
                value={formData.closure_result}
                onChange={handleChange}
                className={`w-full px-4 py-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 transition-all ${errors.closure_result ? 'border-red-300' : 'border-gray-300'}`}
              >
                <option value="">Seleccione un resultado...</option>
                <option value="Exitoso">Exitoso</option>
                <option value="Satisfactorio con Observaciones">Satisfactorio con Observaciones</option>
                <option value="No Satisfactorio">No Satisfactorio</option>
                <option value="Cancelado">Cancelado</option>
              </select>
              {errors.closure_result && <p className="mt-1 text-sm text-red-600 animate-pulse">{errors.closure_result}</p>}
            </div>
          </div>

          {/* Conclusiones */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              <ChatBubbleBottomCenterTextIcon className="h-4 w-4 inline mr-1.5 text-blue-500" />
              Conclusiones *
            </label>
            <textarea
              name="conclusions"
              value={formData.conclusions}
              onChange={handleChange}
              rows={3}
              className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 transition-all ${errors.conclusions ? 'border-red-300' : 'border-gray-300'}`}
              placeholder="¿A qué conclusión se llegó tras el análisis?"
            />
            {errors.conclusions && <p className="mt-1 text-sm text-red-600">{errors.conclusions}</p>}
          </div>

          {/* Resolución */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              <DocumentTextIcon className="h-4 w-4 inline mr-1.5 text-blue-500" />
              Resolución Técnica *
            </label>
            <textarea
              name="resolution"
              value={formData.resolution}
              onChange={handleChange}
              rows={3}
              className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 transition-all ${errors.resolution ? 'border-red-300' : 'border-gray-300'}`}
              placeholder="Detalle técnico de la solución aplicada..."
            />
            {errors.resolution && <p className="mt-1 text-sm text-red-600">{errors.resolution}</p>}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Acciones tomadas */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                <CheckIcon className="h-4 w-4 inline mr-1.5 text-blue-500" />
                Acciones Tomadas *
              </label>
              <textarea
                name="actions_taken"
                value={formData.actions_taken}
                onChange={handleChange}
                rows={4}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 transition-all ${errors.actions_taken ? 'border-red-300' : 'border-gray-300'}`}
                placeholder="- Acción 1..."
              />
              {errors.actions_taken && <p className="mt-1 text-sm text-red-600">{errors.actions_taken}</p>}
            </div>

            {/* Medidas preventivas */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                <ExclamationTriangleIcon className="h-4 w-4 inline mr-1.5 text-blue-500" />
                Medidas Preventivas
              </label>
              <textarea
                name="preventive_measures"
                value={formData.preventive_measures}
                onChange={handleChange}
                rows={4}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 transition-all"
                placeholder="- Medida 1..."
              />
            </div>
          </div>

          {/* Responsable y Fecha */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 bg-gray-50 p-4 rounded-xl">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                <UserIcon className="h-4 w-4 inline mr-1.5 text-gray-500" />
                Responsable del Cierre *
              </label>
              <input
                type="text"
                name="responsible_person"
                value={formData.responsible_person}
                onChange={handleChange}
                className={`w-full px-4 py-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 bg-white ${errors.responsible_person ? 'border-red-300' : 'border-gray-300'}`}
                placeholder="Nombre del responsable"
              />
              {errors.responsible_person && <p className="mt-1 text-sm text-red-600">{errors.responsible_person}</p>}
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                <CalendarIcon className="h-4 w-4 inline mr-1.5 text-gray-500" />
                Fecha de Cierre
              </label>
              <input
                type="date"
                name="closure_date"
                value={formData.closure_date}
                onChange={handleChange}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white"
              />
            </div>
          </div>

          {/* Seguimiento */}
          <div className="border border-gray-200 rounded-xl p-4">
            <div className="flex items-center mb-3">
              <input
                type="checkbox"
                id="requires_follow_up"
                name="requires_follow_up"
                checked={formData.requires_follow_up}
                onChange={handleChange}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded cursor-pointer"
              />
              <label htmlFor="requires_follow_up" className="ml-2 text-sm font-semibold text-gray-700 cursor-pointer select-none">
                Requiere seguimiento posterior
              </label>
            </div>

            {formData.requires_follow_up && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3 animate-fadeIn">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Fecha de Seguimiento *</label>
                  <input
                    type="date"
                    name="follow_up_date"
                    value={formData.follow_up_date}
                    onChange={handleChange}
                    className={`w-full px-3 py-2 border rounded-lg ${errors.follow_up_date ? 'border-red-300' : 'border-gray-300'}`}
                  />
                  {errors.follow_up_date && <p className="mt-1 text-xs text-red-600">{errors.follow_up_date}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Responsable Seguimiento *</label>
                  <input
                    type="text"
                    name="follow_up_responsible"
                    value={formData.follow_up_responsible}
                    onChange={handleChange}
                    className={`w-full px-3 py-2 border rounded-lg ${errors.follow_up_responsible ? 'border-red-300' : 'border-gray-300'}`}
                  />
                  {errors.follow_up_responsible && <p className="mt-1 text-xs text-red-600">{errors.follow_up_responsible}</p>}
                </div>
              </div>
            )}
          </div>

        </form>

        {/* Footer - Premium Sticky */}
        <div className="px-6 py-4 bg-gray-50/80 backdrop-blur-sm border-t border-gray-100 flex justify-end gap-3">
          <button
            type="button"
            onClick={onCancel}
            className="px-5 py-2.5 text-sm font-bold text-gray-700 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 hover:shadow-md transition-all shadow-sm"
          >
            Cancelar
          </button>
          <button
            onClick={handleSubmit}
            disabled={isLoading}
            className="px-6 py-2.5 text-sm font-bold text-white bg-gradient-to-r from-emerald-600 to-green-600 rounded-xl hover:from-emerald-700 hover:to-green-700 transition-all shadow-lg shadow-green-500/30 hover:shadow-green-500/40 disabled:opacity-50 disabled:cursor-not-allowed flex items-center hover:-translate-y-0.5"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white/30 border-t-white mr-2"></div>
                Cerrando...
              </>
            ) : (
              <>
                <CheckCircleIcon className="h-5 w-5 mr-2" />
                Confirmar Cierre
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default IncidentClosureForm;