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
  WrenchScrewdriverIcon,
  EyeIcon,
} from '@heroicons/react/24/outline';

const PolifusionVisitReport = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const [formData, setFormData] = useState({
    // Información del reporte
    orden_number: '',
    fecha_visita: new Date().toISOString().split('T')[0],
    
    // Información general de la obra
    obra: '',
    cliente: '',
    direccion: '',
    administrador: '',
    constructor: '',
    motivo_visita: '01-Visita Técnica',
    
    // Información del personal
    vendedor: '',
    comuna: '',
    ciudad: '',
    instalador: '',
    fono_instalador: '',
    tecnico: '',
    
    // Roles y contactos
    encargado_calidad: '',
    profesional_obra: '',
    inspector_tecnico: '',
    otro_contacto: '',
    
    // Uso de maquinaria
    maquinaria: [
      { maquina: '', inicio: '', corte: '' }
    ],
    retiro_maq: 'No',
    numero_reporte: '',
    
    // Observaciones
    obs_muro_tabique: '',
    obs_matriz: '',
    obs_loza: '',
    obs_almacenaje: '',
    obs_pre_armados: '',
    obs_exteriores: '',
    obs_generales: '',
    
    // Firmas
    firma_tecnico: '',
    firma_instalador: '',
    
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
      const response = await fetch(getEndpoint('generatePolifusionVisitReportPDF'), {
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
      alert('✅ Reporte de visita PDF generado exitosamente\n\nEl documento PDF ha sido creado y guardado en la carpeta compartida de la empresa.');
      navigate('/documents', { 
        state: { 
          message: 'Reporte de visita generado exitosamente',
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

  const handleMaquinariaChange = (index, field, value) => {
    const newMaquinaria = [...formData.maquinaria];
    newMaquinaria[index][field] = value;
    setFormData(prev => ({
      ...prev,
      maquinaria: newMaquinaria
    }));
  };

  const addMaquinariaRow = () => {
    setFormData(prev => ({
      ...prev,
      maquinaria: [...prev.maquinaria, { maquina: '', inicio: '', corte: '' }]
    }));
  };

  const removeMaquinariaRow = (index) => {
    if (formData.maquinaria.length > 1) {
      const newMaquinaria = formData.maquinaria.filter((_, i) => i !== index);
      setFormData(prev => ({
        ...prev,
        maquinaria: newMaquinaria
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.obra.trim()) {
      newErrors.obra = 'La obra es requerida';
    }
    
    if (!formData.cliente.trim()) {
      newErrors.cliente = 'El cliente es requerido';
    }
    
    if (!formData.vendedor.trim()) {
      newErrors.vendedor = 'El vendedor es requerido';
    }
    
    if (!formData.tecnico.trim()) {
      newErrors.tecnico = 'El técnico es requerido';
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
          <title>Vista Previa - Reporte de Visita Polifusión</title>
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
            .two-column { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>${brandConfig.company.name}</h1>
            <p>${brandConfig.company.tagline}</p>
            <h2>REPORTE VISITA</h2>
            <p>Orden N°: ${formData.orden_number || 'Pendiente'}</p>
            <p>Fecha Visita: ${formData.fecha_visita}</p>
          </div>
          
          <div class="section">
            <h3>INFORMACIÓN GENERAL DE LA OBRA</h3>
            <div class="two-column">
              <div>
                <p><strong>Obra:</strong> ${formData.obra}</p>
                <p><strong>Cliente:</strong> ${formData.cliente}</p>
                <p><strong>Dirección:</strong> ${formData.direccion}</p>
                <p><strong>Administrador:</strong> ${formData.administrador}</p>
                <p><strong>Constructor:</strong> ${formData.constructor}</p>
                <p><strong>Motivo Visita:</strong> ${formData.motivo_visita}</p>
              </div>
              <div>
                <p><strong>Vendedor:</strong> ${formData.vendedor}</p>
                <p><strong>Comuna:</strong> ${formData.comuna}</p>
                <p><strong>Ciudad:</strong> ${formData.ciudad}</p>
                <p><strong>Instalador:</strong> ${formData.instalador}</p>
                <p><strong>Teléfono Instalador:</strong> ${formData.fono_instalador}</p>
                <p><strong>Técnico:</strong> ${formData.tecnico}</p>
              </div>
            </div>
          </div>
          
          <div class="section">
            <h3>ROLES Y CONTACTOS</h3>
            <div class="two-column">
              <div>
                <p><strong>Enc. de Calidad:</strong> ${formData.encargado_calidad}</p>
                <p><strong>Profesional de Obra:</strong> ${formData.profesional_obra}</p>
              </div>
              <div>
                <p><strong>Inspector Técnico:</strong> ${formData.inspector_tecnico}</p>
                <p><strong>Otro Contacto:</strong> ${formData.otro_contacto}</p>
              </div>
            </div>
          </div>
          
          <div class="section">
            <h3>USO DE MAQUINARIA</h3>
            <table class="table">
              <thead>
                <tr><th>Máquina</th><th>Inicio</th><th>Corte</th></tr>
              </thead>
              <tbody>
                ${formData.maquinaria.map(item => 
                  `<tr><td>${item.maquina}</td><td>${item.inicio}</td><td>${item.corte}</td></tr>`
                ).join('')}
              </tbody>
            </table>
            <p><strong>Retiro Maq:</strong> ${formData.retiro_maq}</p>
            <p><strong>N° Rep:</strong> ${formData.numero_reporte}</p>
          </div>
          
          <div class="section">
            <h3>OBSERVACIONES</h3>
            <p><strong>Obs Muro/Tabique:</strong> ${formData.obs_muro_tabique}</p>
            <p><strong>Obs Matriz:</strong> ${formData.obs_matriz}</p>
            <p><strong>Obs Loza:</strong> ${formData.obs_loza}</p>
            <p><strong>Obs Almacenaje:</strong> ${formData.obs_almacenaje}</p>
            <p><strong>Obs Pre Armados:</strong> ${formData.obs_pre_armados}</p>
            <p><strong>Obs Exteriores:</strong> ${formData.obs_exteriores}</p>
            <p><strong>Obs Generales:</strong> ${formData.obs_generales}</p>
          </div>
          
          <div class="section">
            <h3>FIRMAS</h3>
            <div class="two-column">
              <div>
                <p><strong>Firma Técnico:</strong> ${formData.firma_tecnico}</p>
              </div>
              <div>
                <p><strong>Firma Instalador:</strong> ${formData.firma_instalador}</p>
              </div>
            </div>
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
              <div className="p-3 bg-green-500/10 rounded-xl">
                <EyeIcon className="h-8 w-8 text-green-600" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  Reporte de Visita Polifusión
                </h1>
                <p className="mt-2 text-lg text-gray-600">
                  Generar reporte de visita técnica con formato oficial
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Información del Reporte */}
          <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-blue-500/10 rounded-xl">
                <DocumentTextIcon className="h-6 w-6 text-blue-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Información del Reporte</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Número de Orden
                </label>
                <input
                  type="text"
                  name="orden_number"
                  value={formData.orden_number}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ej: 26136"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Fecha de Visita
                </label>
                <input
                  type="date"
                  name="fecha_visita"
                  value={formData.fecha_visita}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Información General de la Obra */}
          <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-green-500/10 rounded-xl">
                <BuildingOffice2Icon className="h-6 w-6 text-green-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Información General de la Obra</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Obra *
                </label>
                <input
                  type="text"
                  name="obra"
                  value={formData.obra}
                  onChange={handleInputChange}
                  className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.obra ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="Ej: DEL INCA"
                />
                {errors.obra && (
                  <p className="mt-1 text-sm text-red-600">{errors.obra}</p>
                )}
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
                  Administrador
                </label>
                <input
                  type="text"
                  name="administrador"
                  value={formData.administrador}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Nombre del administrador"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Constructor
                </label>
                <input
                  type="text"
                  name="constructor"
                  value={formData.constructor}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ej: INGETASCO"
                />
              </div>
              
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Motivo de Visita
                </label>
                <select
                  name="motivo_visita"
                  value={formData.motivo_visita}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="01-Visita Técnica">01-Visita Técnica</option>
                  <option value="02-Inspección">02-Inspección</option>
                  <option value="03-Supervisión">03-Supervisión</option>
                  <option value="04-Otro">04-Otro</option>
                </select>
              </div>
            </div>
          </div>

          {/* Información del Personal */}
          <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-purple-500/10 rounded-xl">
                <UserIcon className="h-6 w-6 text-purple-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Información del Personal</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Vendedor *
                </label>
                <input
                  type="text"
                  name="vendedor"
                  value={formData.vendedor}
                  onChange={handleInputChange}
                  className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.vendedor ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="Ej: HECTOR GALVEZ"
                />
                {errors.vendedor && (
                  <p className="mt-1 text-sm text-red-600">{errors.vendedor}</p>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Comuna
                </label>
                <input
                  type="text"
                  name="comuna"
                  value={formData.comuna}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ej: Las Condes"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Ciudad
                </label>
                <input
                  type="text"
                  name="ciudad"
                  value={formData.ciudad}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ej: SANTIAGO"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Instalador
                </label>
                <input
                  type="text"
                  name="instalador"
                  value={formData.instalador}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ej: MOISES MONTOYA"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Teléfono Instalador
                </label>
                <input
                  type="text"
                  name="fono_instalador"
                  value={formData.fono_instalador}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ej: 960477568"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Técnico *
                </label>
                <input
                  type="text"
                  name="tecnico"
                  value={formData.tecnico}
                  onChange={handleInputChange}
                  className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.tecnico ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="Ej: Patricio Morales"
                />
                {errors.tecnico && (
                  <p className="mt-1 text-sm text-red-600">{errors.tecnico}</p>
                )}
              </div>
            </div>
          </div>

          {/* Roles y Contactos */}
          <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-yellow-500/10 rounded-xl">
                <TagIcon className="h-6 w-6 text-yellow-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Roles y Contactos</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Encargado de Calidad
                </label>
                <input
                  type="text"
                  name="encargado_calidad"
                  value={formData.encargado_calidad}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Nombre del encargado de calidad"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Profesional de Obra
                </label>
                <input
                  type="text"
                  name="profesional_obra"
                  value={formData.profesional_obra}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Nombre del profesional de obra"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Inspector Técnico de Obra
                </label>
                <input
                  type="text"
                  name="inspector_tecnico"
                  value={formData.inspector_tecnico}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Nombre del inspector técnico"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Otro Contacto
                </label>
                <input
                  type="text"
                  name="otro_contacto"
                  value={formData.otro_contacto}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Otro contacto relevante"
                />
              </div>
            </div>
          </div>

          {/* Uso de Maquinaria */}
          <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <div className="p-3 bg-orange-500/10 rounded-xl">
                  <WrenchScrewdriverIcon className="h-6 w-6 text-orange-600" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900">Uso de Maquinaria</h2>
              </div>
              <button
                type="button"
                onClick={addMaquinariaRow}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Agregar Máquina
              </button>
            </div>
            
            <div className="space-y-4">
              {formData.maquinaria.map((item, index) => (
                <div key={index} className="flex gap-4 items-start">
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Máquina
                    </label>
                    <input
                      type="text"
                      value={item.maquina}
                      onChange={(e) => handleMaquinariaChange(index, 'maquina', e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Ej: FC 15413"
                    />
                  </div>
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Inicio
                    </label>
                    <input
                      type="text"
                      value={item.inicio}
                      onChange={(e) => handleMaquinariaChange(index, 'inicio', e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Ej: 282"
                    />
                  </div>
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Corte
                    </label>
                    <input
                      type="text"
                      value={item.corte}
                      onChange={(e) => handleMaquinariaChange(index, 'corte', e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Ej: 230"
                    />
                  </div>
                  {formData.maquinaria.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeMaquinariaRow(index)}
                      className="mt-6 px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                    >
                      Eliminar
                    </button>
                  )}
                </div>
              ))}
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Retiro de Maquinaria
                </label>
                <select
                  name="retiro_maq"
                  value={formData.retiro_maq}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="No">No</option>
                  <option value="Sí">Sí</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Número de Reporte
                </label>
                <input
                  type="text"
                  name="numero_reporte"
                  value={formData.numero_reporte}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Número de reporte"
                />
              </div>
            </div>
          </div>

          {/* Observaciones */}
          <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-indigo-500/10 rounded-xl">
                <ClipboardDocumentListIcon className="h-6 w-6 text-indigo-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Observaciones</h2>
            </div>
            
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Obs Muro/Tabique
                </label>
                <textarea
                  name="obs_muro_tabique"
                  value={formData.obs_muro_tabique}
                  onChange={handleInputChange}
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Observaciones sobre muro/tabique"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Obs Matriz
                </label>
                <textarea
                  name="obs_matriz"
                  value={formData.obs_matriz}
                  onChange={handleInputChange}
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Observaciones sobre matriz"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Obs Loza
                </label>
                <textarea
                  name="obs_loza"
                  value={formData.obs_loza}
                  onChange={handleInputChange}
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Observaciones sobre loza"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Obs Almacenaje
                </label>
                <textarea
                  name="obs_almacenaje"
                  value={formData.obs_almacenaje}
                  onChange={handleInputChange}
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Observaciones sobre almacenaje"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Obs Pre Armados
                </label>
                <textarea
                  name="obs_pre_armados"
                  value={formData.obs_pre_armados}
                  onChange={handleInputChange}
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Observaciones sobre pre armados"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Obs Exteriores
                </label>
                <textarea
                  name="obs_exteriores"
                  value={formData.obs_exteriores}
                  onChange={handleInputChange}
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Observaciones exteriores"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Obs Generales
                </label>
                <textarea
                  name="obs_generales"
                  value={formData.obs_generales}
                  onChange={handleInputChange}
                  rows={4}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Observaciones generales"
                />
              </div>
            </div>
          </div>

          {/* Firmas */}
          <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-gray-500/10 rounded-xl">
                <UserIcon className="h-6 w-6 text-gray-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Firmas</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Firma Técnico
                </label>
                <input
                  type="text"
                  name="firma_tecnico"
                  value={formData.firma_tecnico}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Nombre del técnico"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Firma Instalador
                </label>
                <input
                  type="text"
                  name="firma_instalador"
                  value={formData.firma_instalador}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Nombre del instalador"
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
                  <span>Generar Reporte</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PolifusionVisitReport;
