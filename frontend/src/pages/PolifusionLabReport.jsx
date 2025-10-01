import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { incidentsAPI } from '../services/api';
import { brandConfig } from '../config/brand';
import { getEndpoint, getHeaders } from '../config/endpoints';
import {
  DocumentTextIcon,
  ArrowLeftIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  UserIcon,
  BuildingOffice2Icon,
  TagIcon,
  DocumentDuplicateIcon,
  BeakerIcon,
  CameraIcon,
  ClipboardDocumentListIcon,
} from '@heroicons/react/24/outline';

const PolifusionLabReport = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const [formData, setFormData] = useState({
    // Información del solicitante
    solicitante: 'POLIFUSION',
    fecha_solicitud: new Date().toISOString().split('T')[0],
    cliente: 'POLIFUSION',
    incident_code: '', // Add incident code field
    
    // Información técnica
    diametro: '160',
    proyecto: 'Proyecto Alameda Park',
    ubicacion: 'Av. Libertador Bernardo O\'Higgins 4687',
    presion: '11.8-12',
    temperatura: 'No registrada',
    informante: 'Yenny Valdivia Sazo',
    
    // Ensayos
    ensayos_adicionales: 'Análisis de fractura y cristalización',
    
    // Comentarios detallados
    comentarios_detallados: 'Se recibió una muestra compuesta por un codo de 90° PP-RCT de 160mm, fusionado en ambos extremos a una tubería PP-RCT/FIBERGLASS S-3.2 de 160mm. La muestra presenta una grieta longitudinal tipo corte en la sección transversal de la tubería en uno de los extremos del codo, con un inserto de tapón, posiblemente para detener una fuga.',
    
    // Conclusiones
    conclusiones_detalladas: 'El análisis de la muestra reveló que los extremos de la tubería no fueron reducidos, y el cordón de fusión externo era irregular, mostrando fusión excesiva y evidencia clara de sobre-fusión de la pared del fitting. También se observó una fisura tipo corte o grieta longitudinal, en la cual se insertó un tapón de reparación, presumiblemente como intento de contener la fuga.',
    
    // Experto
    experto_nombre: 'CÉSAR MUNIZAGA GARRIDO',
    
    // Análisis detallado
    analisis_detallado: 'Se realizó un corte longitudinal del fitting, revelando cordones de fusión internos corrugados, lo cual es una indicación clara de presencia de agua durante el proceso de fusión. La inspección de la grieta, encontrada en el punto donde se inserta una sección de tubería, justo detrás del cordón de fusión, reveló una separación de 1-2 mm de la pared del fitting. Al aplicar una fuerza de flexión se reveló una fractura frágil característica, típica de material cristalizado debido al calentamiento excesivo.',
    
    // Relación con incidencia
    incident_id: '',
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState({});

  // Obtener incidencias disponibles
  const { data: incidents } = useQuery({
    queryKey: ['incidents'],
    queryFn: () => incidentsAPI.list({}),
  });

  // Mutación para generar el documento
  const generateDocumentMutation = useMutation({
    mutationFn: async (data) => {
      const response = await fetch(getEndpoint('generatePolifusionLabReportPDF'), {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(data),
      });
      
      if (!response.ok) {
        throw new Error('Error al generar el documento');
      }
      
      return response.json();
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries(['documents']);
      // Mostrar confirmación
      alert('✅ Informe de laboratorio PDF generado exitosamente\n\nEl documento PDF ha sido creado y guardado en la carpeta compartida de la empresa.');
      navigate('/documents', { 
        state: { 
          message: 'Informe de laboratorio PDF generado exitosamente',
          document: data 
        }
      });
    },
    onError: (error) => {
      console.error('Error generating document:', error);
      let errorMessage = 'Error al generar el documento';
      
      if (error.message.includes('401')) {
        errorMessage = 'Error de autenticación. Por favor, inicia sesión nuevamente.';
      } else if (error.message.includes('500')) {
        errorMessage = 'Error del servidor. Verifica la configuración.';
      } else if (error.message.includes('400')) {
        errorMessage = 'Datos inválidos. Verifica que todos los campos requeridos estén completos.';
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setErrors({ submit: errorMessage });
      alert(`❌ ${errorMessage}`);
    },
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Limpiar error del campo
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.solicitante.trim()) {
      newErrors.solicitante = 'El solicitante es requerido';
    }
    
    if (!formData.cliente.trim()) {
      newErrors.cliente = 'El cliente es requerido';
    }
    
    if (!formData.proyecto.trim()) {
      newErrors.proyecto = 'El proyecto es requerido';
    }
    
    if (!formData.experto_nombre.trim()) {
      newErrors.experto_nombre = 'El nombre del experto es requerido';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsSubmitting(true);
    setErrors({});
    
    try {
      await generateDocumentMutation.mutateAsync(formData);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handlePreview = () => {
    // Abrir preview en nueva ventana
    const previewData = {
      ...formData,
      preview: true
    };
    
    const previewWindow = window.open('', '_blank');
    previewWindow.document.write(`
      <html>
        <head>
          <title>Vista Previa - Informe de Laboratorio Polifusión</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 30px; }
            .section { margin-bottom: 25px; }
            .section h3 { color: #2563eb; border-bottom: 1px solid #e5e7eb; padding-bottom: 5px; }
            .field { margin-bottom: 10px; }
            .label { font-weight: bold; }
            .value { margin-left: 10px; }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>${brandConfig.company.name}</h1>
            <p>${brandConfig.company.tagline}</p>
            <h2>INFORME DE LABORATORIO</h2>
          </div>
          
          <div class="section">
            <h3>INFORMACIÓN DEL SOLICITANTE</h3>
            <div class="field">
              <span class="label">Solicitante:</span>
              <span class="value">${formData.solicitante}</span>
            </div>
            <div class="field">
              <span class="label">Fecha de solicitud:</span>
              <span class="value">${formData.fecha_solicitud}</span>
            </div>
            <div class="field">
              <span class="label">Cliente:</span>
              <span class="value">${formData.cliente}</span>
            </div>
          </div>
          
          <div class="section">
            <h3>INFORMACIÓN TÉCNICA</h3>
            <div class="field">
              <span class="label">Diámetro:</span>
              <span class="value">${formData.diametro}mm</span>
            </div>
            <div class="field">
              <span class="label">Proyecto:</span>
              <span class="value">${formData.proyecto}</span>
            </div>
            <div class="field">
              <span class="label">Ubicación:</span>
              <span class="value">${formData.ubicacion}</span>
            </div>
            <div class="field">
              <span class="label">Presión:</span>
              <span class="value">${formData.presion} bar</span>
            </div>
            <div class="field">
              <span class="label">Temperatura:</span>
              <span class="value">${formData.temperatura}</span>
            </div>
            <div class="field">
              <span class="label">Informante:</span>
              <span class="value">${formData.informante}</span>
            </div>
          </div>
          
          <div class="section">
            <h3>CONCLUSIONES</h3>
            <p>${formData.conclusiones_detalladas}</p>
          </div>
          
          <div class="section">
            <h3>FIRMA</h3>
            <p><strong>${formData.experto_nombre}</strong><br>
            Experto técnico<br>
            Control de Calidad Polifusión S.A.</p>
          </div>
        </body>
      </html>
    `);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-4 mb-4">
            <button
              onClick={() => navigate('/documents')}
              className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <ArrowLeftIcon className="h-6 w-6" />
            </button>
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-blue-500/10 rounded-xl">
                <BeakerIcon className="h-8 w-8 text-blue-600" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  Informe de Laboratorio Polifusión
                </h1>
                <p className="mt-2 text-lg text-gray-600">
                  Generar informe técnico de laboratorio con plantilla oficial
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Información del Solicitante */}
          <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-blue-500/10 rounded-xl">
                <UserIcon className="h-6 w-6 text-blue-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Información del Solicitante</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Solicitante *
                </label>
                <input
                  type="text"
                  name="solicitante"
                  value={formData.solicitante}
                  onChange={handleInputChange}
                  className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.solicitante ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="Nombre del solicitante"
                />
                {errors.solicitante && (
                  <p className="mt-1 text-sm text-red-600">{errors.solicitante}</p>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Fecha de Solicitud
                </label>
                <input
                  type="date"
                  name="fecha_solicitud"
                  value={formData.fecha_solicitud}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cliente *
                </label>
                <input
                  type="text"
                  name="cliente"
                  value={formData.cliente}
                  onChange={handleInputChange}
                  className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.cliente ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="Nombre del cliente"
                />
                {errors.cliente && (
                  <p className="mt-1 text-sm text-red-600">{errors.cliente}</p>
                )}
              </div>
            </div>
          </div>

          {/* Información Técnica */}
          <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-green-500/10 rounded-xl">
                <BuildingOffice2Icon className="h-6 w-6 text-green-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Información Técnica</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Diámetro (mm)
                </label>
                <input
                  type="text"
                  name="diametro"
                  value={formData.diametro}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="160"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Proyecto *
                </label>
                <input
                  type="text"
                  name="proyecto"
                  value={formData.proyecto}
                  onChange={handleInputChange}
                  className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.proyecto ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="Nombre del proyecto"
                />
                {errors.proyecto && (
                  <p className="mt-1 text-sm text-red-600">{errors.proyecto}</p>
                )}
              </div>
              
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Ubicación
                </label>
                <input
                  type="text"
                  name="ubicacion"
                  value={formData.ubicacion}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Dirección del proyecto"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Presión (bar)
                </label>
                <input
                  type="text"
                  name="presion"
                  value={formData.presion}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="11.8-12"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Temperatura
                </label>
                <input
                  type="text"
                  name="temperatura"
                  value={formData.temperatura}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="No registrada"
                />
              </div>
              
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Informante
                </label>
                <input
                  type="text"
                  name="informante"
                  value={formData.informante}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Nombre del informante"
                />
              </div>
            </div>
          </div>

          {/* Ensayos */}
          <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-purple-500/10 rounded-xl">
                <ClipboardDocumentListIcon className="h-6 w-6 text-purple-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Ensayos Realizados</h2>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ensayos Adicionales
              </label>
              <textarea
                name="ensayos_adicionales"
                value={formData.ensayos_adicionales}
                onChange={handleInputChange}
                rows={3}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Descripción de ensayos adicionales realizados"
              />
            </div>
          </div>

          {/* Comentarios Detallados */}
          <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-yellow-500/10 rounded-xl">
                <DocumentTextIcon className="h-6 w-6 text-yellow-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Comentarios Detallados</h2>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Descripción Detallada
              </label>
              <textarea
                name="comentarios_detallados"
                value={formData.comentarios_detallados}
                onChange={handleInputChange}
                rows={6}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Descripción detallada de la muestra y observaciones"
              />
            </div>
          </div>

          {/* Conclusiones */}
          <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-red-500/10 rounded-xl">
                <CheckCircleIcon className="h-6 w-6 text-red-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Conclusiones</h2>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Conclusiones Detalladas
              </label>
              <textarea
                name="conclusiones_detalladas"
                value={formData.conclusiones_detalladas}
                onChange={handleInputChange}
                rows={6}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Conclusiones técnicas del análisis"
              />
            </div>
          </div>

          {/* Análisis Detallado */}
          <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-indigo-500/10 rounded-xl">
                <CameraIcon className="h-6 w-6 text-indigo-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Análisis Detallado</h2>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Análisis Técnico
              </label>
              <textarea
                name="analisis_detallado"
                value={formData.analisis_detallado}
                onChange={handleInputChange}
                rows={6}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Análisis técnico detallado de la muestra"
              />
            </div>
          </div>

          {/* Experto */}
          <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-gray-500/10 rounded-xl">
                <UserIcon className="h-6 w-6 text-gray-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Firma del Experto</h2>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nombre del Experto *
              </label>
              <input
                type="text"
                name="experto_nombre"
                value={formData.experto_nombre}
                onChange={handleInputChange}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.experto_nombre ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Nombre completo del experto técnico"
              />
              {errors.experto_nombre && (
                <p className="mt-1 text-sm text-red-600">{errors.experto_nombre}</p>
              )}
            </div>
          </div>

          {/* Relación con Incidencia */}
          <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-orange-500/10 rounded-xl">
                <TagIcon className="h-6 w-6 text-orange-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Relación con Incidencia</h2>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Incidencia Relacionada (Opcional)
              </label>
              <select
                name="incident_id"
                value={formData.incident_id}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Seleccionar incidencia (opcional)</option>
                {incidents?.results?.map((incident) => (
                  <option key={incident.id} value={incident.id}>
                    #{incident.id} - {incident.title} - {incident.client}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Error de envío */}
          {errors.submit && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <ExclamationTriangleIcon className="h-5 w-5 text-red-600" />
                <p className="text-red-800">{errors.submit}</p>
              </div>
            </div>
          )}

          {/* Botones de Acción */}
          <div className="flex flex-col sm:flex-row gap-4 justify-end">
            <button
              type="button"
              onClick={handlePreview}
              className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors flex items-center justify-center space-x-2"
            >
              <DocumentDuplicateIcon className="h-5 w-5" />
              <span>Vista Previa</span>
            </button>
            
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
            >
              {isSubmitting ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Generando...</span>
                </>
              ) : (
                <>
                  <DocumentTextIcon className="h-5 w-5" />
                  <span>Generar Informe</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PolifusionLabReport;
