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
  ClipboardDocumentListIcon,
  CalendarIcon,
  MapPinIcon,
  PhoneIcon,
  EnvelopeIcon,
} from '@heroicons/react/24/outline';

const PolifusionIncidentReport = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const [formData, setFormData] = useState({
    // Información del informe
    report_number: '',
    report_date: new Date().toISOString().split('T')[0],
    
    // Registro de información
    proveedor: '',
    obra: '',
    produccion: '',
    cliente: '',
    servicio: '',
    rut: '',
    direccion: '',
    otros: '',
    contactos: '',
    fecha_deteccion: '',
    hora: '',
    
    // Descripción del problema
    descripcion_problema: '',
    
    // Acciones inmediatas
    acciones_inmediatas: '',
    
    // Evolución/Acciones posteriores
    evolucion_acciones: [
      { fecha: '', descripcion: '' }
    ],
    
    // Observaciones y cierre
    observaciones: '',
    fecha_cierre: '',
    
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
      const response = await fetch(getEndpoint('generatePolifusionIncidentReportPDF'), {
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
      alert('✅ Informe de incidencia PDF generado exitosamente\n\nEl documento PDF ha sido creado y guardado en la carpeta compartida de la empresa.');
      navigate('/documents', { 
        state: { 
          message: 'Informe de incidencia generado exitosamente',
          document: data 
        }
      });
    },
    onError: (error) => {
      console.error('Error generating document:', error);
      setErrors({ submit: 'Error al generar el documento' });
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

  const handleEvolucionChange = (index, field, value) => {
    const newEvolucion = [...formData.evolucion_acciones];
    newEvolucion[index][field] = value;
    setFormData(prev => ({
      ...prev,
      evolucion_acciones: newEvolucion
    }));
  };

  const addEvolucionRow = () => {
    setFormData(prev => ({
      ...prev,
      evolucion_acciones: [...prev.evolucion_acciones, { fecha: '', descripcion: '' }]
    }));
  };

  const removeEvolucionRow = (index) => {
    if (formData.evolucion_acciones.length > 1) {
      const newEvolucion = formData.evolucion_acciones.filter((_, i) => i !== index);
      setFormData(prev => ({
        ...prev,
        evolucion_acciones: newEvolucion
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.proveedor.trim()) {
      newErrors.proveedor = 'El proveedor es requerido';
    }
    
    if (!formData.cliente.trim()) {
      newErrors.cliente = 'El cliente es requerido';
    }
    
    if (!formData.descripcion_problema.trim()) {
      newErrors.descripcion_problema = 'La descripción del problema es requerida';
    }
    
    if (!formData.acciones_inmediatas.trim()) {
      newErrors.acciones_inmediatas = 'Las acciones inmediatas son requeridas';
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
    const previewWindow = window.open('', '_blank');
    previewWindow.document.write(`
      <html>
        <head>
          <title>Vista Previa - Informe de Incidencia Polifusión</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 30px; }
            .section { margin-bottom: 25px; }
            .section h3 { color: #2563eb; border-bottom: 1px solid #e5e7eb; padding-bottom: 5px; }
            .field { margin-bottom: 10px; }
            .label { font-weight: bold; }
            .value { margin-left: 10px; }
            .table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            .table th, .table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            .table th { background-color: #f2f2f2; }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>${brandConfig.company.name}</h1>
            <p>${brandConfig.company.tagline}</p>
            <h2>INFORME DE INCIDENCIA</h2>
            <p>N° ${formData.report_number || 'Pendiente'}</p>
          </div>
          
          <div class="section">
            <h3>REGISTRO DE INFORMACIÓN</h3>
            <table class="table">
              <tr><td><strong>Proveedor:</strong></td><td>${formData.proveedor}</td></tr>
              <tr><td><strong>Obra:</strong></td><td>${formData.obra}</td></tr>
              <tr><td><strong>Producción:</strong></td><td>${formData.produccion}</td></tr>
              <tr><td><strong>Cliente:</strong></td><td>${formData.cliente}</td></tr>
              <tr><td><strong>Servicio:</strong></td><td>${formData.servicio}</td></tr>
              <tr><td><strong>RUT:</strong></td><td>${formData.rut}</td></tr>
              <tr><td><strong>Dirección:</strong></td><td>${formData.direccion}</td></tr>
              <tr><td><strong>Contactos:</strong></td><td>${formData.contactos}</td></tr>
              <tr><td><strong>Fecha Detección:</strong></td><td>${formData.fecha_deteccion}</td></tr>
              <tr><td><strong>Hora:</strong></td><td>${formData.hora}</td></tr>
            </table>
          </div>
          
          <div class="section">
            <h3>DESCRIPCIÓN DEL PROBLEMA</h3>
            <p>${formData.descripcion_problema}</p>
          </div>
          
          <div class="section">
            <h3>ACCIONES INMEDIATAS ADOPTADAS</h3>
            <p>${formData.acciones_inmediatas}</p>
          </div>
          
          <div class="section">
            <h3>EVOLUCIÓN/ACCIONES POSTERIORMENTE ADOPTADAS</h3>
            <table class="table">
              <thead>
                <tr><th>FECHA</th><th>DESCRIPCIÓN</th></tr>
              </thead>
              <tbody>
                ${formData.evolucion_acciones.map(item => 
                  `<tr><td>${item.fecha}</td><td>${item.descripcion}</td></tr>`
                ).join('')}
              </tbody>
            </table>
          </div>
          
          <div class="section">
            <h3>OBSERVACIONES</h3>
            <p>${formData.observaciones}</p>
          </div>
          
          <div class="section">
            <h3>FECHA CIERRE</h3>
            <p>${formData.fecha_cierre || 'Pendiente'}</p>
          </div>
        </body>
      </html>
    `);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
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
              <div className="p-3 bg-red-500/10 rounded-xl">
                <ExclamationTriangleIcon className="h-8 w-8 text-red-600" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  Informe de Incidencia Polifusión
                </h1>
                <p className="mt-2 text-lg text-gray-600">
                  Generar informe de incidencia con formato oficial
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Información del Informe */}
          <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-blue-500/10 rounded-xl">
                <DocumentTextIcon className="h-6 w-6 text-blue-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Información del Informe</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Número de Informe
                </label>
                <input
                  type="text"
                  name="report_number"
                  value={formData.report_number}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ej: 20"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Fecha del Informe
                </label>
                <input
                  type="date"
                  name="report_date"
                  value={formData.report_date}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Registro de Información */}
          <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-green-500/10 rounded-xl">
                <BuildingOffice2Icon className="h-6 w-6 text-green-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Registro de Información</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Proveedor *
                </label>
                <input
                  type="text"
                  name="proveedor"
                  value={formData.proveedor}
                  onChange={handleInputChange}
                  className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.proveedor ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="Ej: Hotel Hilton Curico"
                />
                {errors.proveedor && (
                  <p className="mt-1 text-sm text-red-600">{errors.proveedor}</p>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Obra
                </label>
                <input
                  type="text"
                  name="obra"
                  value={formData.obra}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Nombre de la obra"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Producción
                </label>
                <input
                  type="text"
                  name="produccion"
                  value={formData.produccion}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ej: Amsovi"
                />
              </div>
              
              <div>
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
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Servicio
                </label>
                <input
                  type="text"
                  name="servicio"
                  value={formData.servicio}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Tipo de servicio"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  RUT
                </label>
                <input
                  type="text"
                  name="rut"
                  value={formData.rut}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ej: 76.495.275-8"
                />
              </div>
              
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Dirección
                </label>
                <input
                  type="text"
                  name="direccion"
                  value={formData.direccion}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Dirección completa"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Otros
                </label>
                <input
                  type="text"
                  name="otros"
                  value={formData.otros}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Información adicional"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Contactos
                </label>
                <input
                  type="text"
                  name="contactos"
                  value={formData.contactos}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Persona de contacto"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Fecha Detección
                </label>
                <input
                  type="date"
                  name="fecha_deteccion"
                  value={formData.fecha_deteccion}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Hora
                </label>
                <input
                  type="time"
                  name="hora"
                  value={formData.hora}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Descripción del Problema */}
          <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-red-500/10 rounded-xl">
                <ExclamationTriangleIcon className="h-6 w-6 text-red-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Descripción del Problema</h2>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Descripción Detallada *
              </label>
              <textarea
                name="descripcion_problema"
                value={formData.descripcion_problema}
                onChange={handleInputChange}
                rows={4}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.descripcion_problema ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Describa detalladamente el problema encontrado"
              />
              {errors.descripcion_problema && (
                <p className="mt-1 text-sm text-red-600">{errors.descripcion_problema}</p>
              )}
            </div>
          </div>

          {/* Acciones Inmediatas */}
          <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-yellow-500/10 rounded-xl">
                <CheckCircleIcon className="h-6 w-6 text-yellow-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Acciones Inmediatas Adoptadas</h2>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Acciones Tomadas *
              </label>
              <textarea
                name="acciones_inmediatas"
                value={formData.acciones_inmediatas}
                onChange={handleInputChange}
                rows={4}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.acciones_inmediatas ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Describa las acciones inmediatas que se adoptaron"
              />
              {errors.acciones_inmediatas && (
                <p className="mt-1 text-sm text-red-600">{errors.acciones_inmediatas}</p>
              )}
            </div>
          </div>

          {/* Evolución/Acciones Posteriores */}
          <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <div className="p-3 bg-purple-500/10 rounded-xl">
                  <ClipboardDocumentListIcon className="h-6 w-6 text-purple-600" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900">Evolución/Acciones Posteriores</h2>
              </div>
              <button
                type="button"
                onClick={addEvolucionRow}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Agregar Fila
              </button>
            </div>
            
            <div className="space-y-4">
              {formData.evolucion_acciones.map((item, index) => (
                <div key={index} className="flex gap-4 items-start">
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Fecha
                    </label>
                    <input
                      type="date"
                      value={item.fecha}
                      onChange={(e) => handleEvolucionChange(index, 'fecha', e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div className="flex-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Descripción
                    </label>
                    <textarea
                      value={item.descripcion}
                      onChange={(e) => handleEvolucionChange(index, 'descripcion', e.target.value)}
                      rows={2}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Descripción de la evolución o acción adoptada"
                    />
                  </div>
                  {formData.evolucion_acciones.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeEvolucionRow(index)}
                      className="mt-6 px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                    >
                      Eliminar
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Observaciones y Cierre */}
          <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-gray-500/10 rounded-xl">
                <TagIcon className="h-6 w-6 text-gray-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Observaciones y Cierre</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Observaciones
                </label>
                <textarea
                  name="observaciones"
                  value={formData.observaciones}
                  onChange={handleInputChange}
                  rows={4}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Observaciones adicionales"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Fecha de Cierre
                </label>
                <input
                  type="date"
                  name="fecha_cierre"
                  value={formData.fecha_cierre}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
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

export default PolifusionIncidentReport;
