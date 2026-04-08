import React, { useState, useCallback } from 'react';
import {
  XMarkIcon,
  CheckCircleIcon,
  PaperClipIcon
} from '@heroicons/react/24/outline';
import { Incident } from '../types';

interface IncidentClosureFormProps {
  incident: number | Incident | undefined;
  onSubmit: (data: any) => void;
  onCancel: () => void;
  isClosing?: boolean;
  defaultStage?: string;
}

/**
 * Standardized Incident Closure Form
 */
const IncidentClosureForm: React.FC<IncidentClosureFormProps> = ({
  incident,
  onSubmit,
  onCancel,
  isClosing = false,
  defaultStage = 'incidencia'
}) => {
  const [formData, setFormData] = useState({
    stage: defaultStage,
    reason: '',
    closure_summary: '',
    closure_attachment: null as File | null
  });

  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const target = e.target as HTMLInputElement;
    const { name, value } = target;
    
    if (name === 'closure_attachment') {
      setFormData(prev => ({ ...prev, closure_attachment: target.files?.[0] || null }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
    
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  }, [errors]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const newErrors: { [key: string]: string } = {};
    if (!formData.reason) newErrors.reason = 'El motivo de cierre es obligatorio';
    if (formData.closure_summary.length < 10) newErrors.closure_summary = 'El resumen debe tener al menos 10 caracteres';
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    // Combine Reason + Summary for traceability
    const finalSummary = `[Motivo: ${formData.reason}] ${formData.closure_summary}`;

    onSubmit({
      ...formData,
      closure_summary: finalSummary,
      raw_summary: formData.closure_summary
    });
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm transition-opacity" aria-hidden="true" onClick={onCancel}></div>

        <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

        <div className="inline-block align-bottom bg-white rounded-3xl text-left overflow-hidden shadow-2xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full border border-white/20">
          <div className="bg-white px-6 pt-6 pb-6 sm:p-8">
            <div className="sm:flex sm:items-start mb-6">
              <div className="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-2xl bg-emerald-50 text-emerald-600 sm:mx-0 sm:h-12 sm:w-12 shadow-sm border border-emerald-100">
                <CheckCircleIcon className="h-7 w-7" aria-hidden="true" />
              </div>
              <div className="mt-4 text-center sm:mt-0 sm:ml-5 sm:text-left w-full">
                <h3 className="text-xl font-black text-slate-800 uppercase tracking-tight" id="modal-title">
                  Cerrar Incidencia Asociada
                </h3>
                <div className="mt-1">
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                    Expediente: <span className="text-indigo-600">
                      {typeof incident === 'object' ? incident?.code : (incident ? `INC-${incident}` : 'S/N')}
                    </span>
                  </p>
                </div>
              </div>
              <button onClick={onCancel} className="absolute top-6 right-6 text-slate-400 hover:text-slate-600 transition-colors">
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>

            <div className="space-y-6">
              <div className="bg-amber-50 border border-amber-100 rounded-2xl p-4 text-sm text-amber-800 flex items-start gap-3">
                <div className="mt-0.5">⚠️</div>
                <p className="font-bold leading-relaxed italic">
                  Esta acción es definitiva y cerrará formalmente el caso en el sistema y SAP.
                </p>
              </div>

              {/* Etapa de Cierre */}
              <div>
                <label className="block text-[11px] font-black text-slate-400 uppercase tracking-widest mb-2">
                  Etapa de Cierre <span className="text-rose-500">*</span>
                </label>
                <select
                  name="stage"
                  value={formData.stage}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-4 focus:ring-emerald-500/10 focus:border-emerald-500 transition-all font-bold text-slate-700 outline-none"
                >
                  <option value="incidencia">Cerrada en Incidencia</option>
                  <option value="reporte_visita">Cerrada en Reporte de Visita</option>
                  <option value="calidad">Cerrada en Calidad</option>
                  <option value="proveedor">Cerrada en Proveedor</option>
                </select>
              </div>

              {/* Motivo de Cierre */}
              <div>
                <label className="block text-[11px] font-black text-slate-400 uppercase tracking-widest mb-2">
                  Motivo de Cierre <span className="text-rose-500">*</span>
                </label>
                <select
                  name="reason"
                  value={formData.reason}
                  onChange={handleChange}
                  className={`w-full px-4 py-3 bg-slate-50 border rounded-xl focus:ring-4 transition-all font-bold text-slate-700 outline-none ${errors.reason ? 'border-rose-300 focus:ring-rose-500/10 focus:border-rose-500' : 'border-slate-200 focus:ring-emerald-500/10 focus:border-emerald-500'}`}
                >
                  <option value="">-- Seleccionar motivo --</option>
                  <option value="Resuelto satisfactoriamente">Resuelto satisfactoriamente</option>
                  <option value="Sin garantía aplicable">Sin garantía aplicable</option>
                  <option value="Producto reemplazado">Producto reemplazado</option>
                  <option value="Crédito emitido">Crédito emitido</option>
                  <option value="Problema no reproducible">Problema no reproducible</option>
                  <option value="Solicitud del cliente">Solicitud del cliente</option>
                  <option value="Otro">Otro</option>
                </select>
                {errors.reason && <p className="mt-1.5 text-[10px] font-black text-rose-500 uppercase tracking-widest">{errors.reason}</p>}
              </div>

              {/* Resumen */}
              <div>
                <label className="block text-[11px] font-black text-slate-400 uppercase tracking-widest mb-2">
                  Resumen de Acciones y Conclusiones <span className="text-rose-500">*</span>
                </label>
                <textarea
                  name="closure_summary"
                  value={formData.closure_summary}
                  onChange={handleChange}
                  rows={4}
                  className={`w-full px-4 py-3 bg-slate-50 border rounded-xl focus:ring-4 transition-all font-bold text-slate-700 outline-none resize-none ${errors.closure_summary ? 'border-rose-300 focus:ring-rose-500/10 focus:border-rose-500' : 'border-slate-200 focus:ring-emerald-500/10 focus:border-emerald-500'}`}
                  placeholder="Describa las acciones tomadas..."
                />
                <div className="flex justify-between mt-1.5">
                  <p className={`text-[10px] font-black uppercase tracking-widest ${formData.closure_summary.length < 10 ? 'text-rose-500' : 'text-emerald-600'}`}>
                    {formData.closure_summary.length}/10 caracteres mínimos
                  </p>
                  {errors.closure_summary && <p className="text-[10px] font-black text-rose-500 uppercase tracking-widest">{errors.closure_summary}</p>}
                </div>
              </div>

              {/* Archivo Adjunto */}
              <div>
                <label className="block text-[11px] font-black text-slate-400 uppercase tracking-widest mb-2">
                  Archivo Adjunto (opcional)
                </label>
                <div className="flex items-center gap-3">
                  <input
                    type="file"
                    id="closure-file-standard"
                    name="closure_attachment"
                    className="hidden"
                    onChange={handleChange}
                    accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.txt"
                  />
                  <label
                    htmlFor="closure-file-standard"
                    className="px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-600 border border-slate-200 rounded-xl cursor-pointer transition-all text-[10px] font-black uppercase tracking-widest shadow-sm"
                  >
                    Seleccionar Archivo
                  </label>
                  {formData.closure_attachment && (
                    <div className="flex items-center gap-2 text-xs font-bold text-slate-500 bg-slate-50 px-3 py-2 rounded-lg border border-slate-100 animate-in fade-in slide-in-from-left-2">
                      <PaperClipIcon className="w-4 h-4 text-slate-400" />
                      <span className="truncate max-w-[150px]">{formData.closure_attachment.name}</span>
                      <button
                        type="button"
                        onClick={() => setFormData(prev => ({ ...prev, closure_attachment: null }))}
                        className="ml-1 text-rose-500 hover:text-rose-700"
                      >
                        ✕
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="mt-10 flex gap-4">
              <button
                type="button"
                onClick={onCancel}
                className="flex-1 py-4 bg-slate-100 text-slate-600 rounded-2xl font-black text-[10px] uppercase tracking-widest hover:bg-slate-200 transition-all"
                disabled={isClosing}
              >
                CANCELAR
              </button>
              <button
                type="button"
                onClick={handleSubmit}
                disabled={isClosing || formData.closure_summary.length < 10 || !formData.reason}
                className={`flex-1 py-4 text-white rounded-2xl font-black text-[10px] uppercase tracking-widest border-b-4 transition-all shadow-lg ${
                  formData.closure_summary.length < 10 || !formData.reason
                    ? 'bg-slate-300 border-slate-400 cursor-not-allowed opacity-50'
                    : 'bg-emerald-600 border-emerald-800 hover:bg-emerald-700 active:border-b-0 shadow-emerald-600/20'
                }`}
              >
                {isClosing ? (
                  <div className="flex items-center justify-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white/30 border-t-white"></div>
                    <span>CERRANDO...</span>
                  </div>
                ) : (
                  <div className="flex items-center justify-center gap-2">
                    <CheckCircleIcon className="h-4 w-4" />
                    <span>CONFIRMAR CIERRE</span>
                  </div>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IncidentClosureForm;