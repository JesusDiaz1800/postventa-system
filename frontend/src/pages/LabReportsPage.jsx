import React, { useState, useEffect, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useLocation } from 'react-router-dom';
import { api } from '../services/api';
import { 
  PlusIcon, 
  DocumentArrowUpIcon, 
  EyeIcon, 
  TrashIcon,
  XMarkIcon,
  CheckCircleIcon,
  MagnifyingGlassIcon,
  DocumentTextIcon,
  CalendarIcon,
  UserIcon,
  BuildingOfficeIcon,
  BeakerIcon
} from '@heroicons/react/24/outline';

const LabReportsPage = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const location = useLocation();
  
  // Estados principales
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  
  const [selectedIncidentId, setSelectedIncidentId] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [uploadedDocuments, setUploadedDocuments] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [selectedReportType, setSelectedReportType] = useState('');
  const [attachReportType, setAttachReportType] = useState('cliente');

  // Formulario de creación
  const [formData, setFormData] = useState({
    related_incident_id: '',
    report_type: '',
    sample_id: '',
    test_date: new Date().toISOString().split('T')[0],
    technician: '',
    test_parameters: '',
    test_results: '',
    conclusion: '',
    recommendations: '',
    status: 'draft'
  });

  // Query para obtener reportes de laboratorio
  const { data: reports, isLoading: reportsLoading } = useQuery({
    queryKey: ['labReports'],
    queryFn: () => api.get('/documents/lab-reports/').then(res => res.data)
  });

  // Query para obtener incidencias abiertas
  const { data: openIncidents, isLoading: incidentsLoading } = useQuery({
    queryKey: ['openIncidents'],
    queryFn: () => api.get('/incidents/?estado=abierto').then(res => res.data)
  });

  // Función para cargar documentos subidos
  const loadUploadedDocuments = async (incidentId) => {
    try {
      const response = await api.get(`/documents/uploaded/lab-report/${incidentId}/`);
      if (response.data && response.data.documents) {
        return response.data.documents;
      }
      return [];
    } catch (error) {
      console.error(`Error cargando documentos subidos para incidencia ${incidentId}:`, error);
      return [];
    }
  };

  // Cargar documentos subidos cuando cambian los reportes
  useEffect(() => {
    const loadDocuments = async () => {
      if (reports?.results || reports?.data) {
        const reportsArray = reports?.results || reports?.data || reports || [];
        
        for (const report of reportsArray) {
          if (report.related_incident?.id) {
            try {
              const documents = await loadUploadedDocuments(report.related_incident.id);
              setUploadedDocuments(prev => ({
                ...prev,
                [report.related_incident.id]: documents
              }));
            } catch (error) {
              console.error('Error cargando documentos para incidencia', report.related_incident.id, ':', error);
            }
          }
        }
      }
    };

    loadDocuments().catch(error => {
      console.error('Error general cargando documentos:', error);
    });
  }, [reports?.results, reports?.data]);

  // Prellenar datos de la incidencia cuando se selecciona
  useEffect(() => {
    if (selectedIncidentId && openIncidents) {
      const incidentsArray = openIncidents?.data?.results || openIncidents?.results || [];
      const incident = incidentsArray.find(inc => inc.id === parseInt(selectedIncidentId));
      
      if (incident) {
        setSelectedIncident(incident);
        setFormData(prev => ({
          ...prev,
          related_incident_id: selectedIncidentId,
          // Prellenar con datos de la incidencia
          test_date: new Date().toISOString().split('T')[0],
        }));
      }
    }
  }, [selectedIncidentId, openIncidents]);

  // Mutation para crear reporte de laboratorio
  const createLabReportMutation = useMutation({
    mutationFn: (data) => api.post('/documents/lab-reports/', data),
    onSuccess: (response) => {
      queryClient.invalidateQueries(['labReports']);
      setShowCreateModal(false);
      setSelectedIncidentId('');
      setSelectedIncident(null);
      setSelectedReportType('');
      resetForm();
      alert('Reporte de laboratorio creado exitosamente');
    },
    onError: (error) => {
      console.error('Error creando reporte de laboratorio:', error);
      alert('Error al crear el reporte de laboratorio');
    }
  });

  // Mutation para subir documento
  const uploadDocumentMutation = useMutation({
    mutationFn: (formData) => api.post('/documents/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
    onSuccess: (response) => {
      console.log('Document uploaded successfully:', response.data);
      queryClient.invalidateQueries(['labReports']);
      setShowUploadModal(false);
      setSelectedIncidentId('');
      
      // Recargar documentos subidos para la incidencia
      if (response.data?.incident_id) {
        loadUploadedDocuments(response.data.incident_id).then(documents => {
          setUploadedDocuments(prev => ({
            ...prev,
            [response.data.incident_id]: documents
          }));
        }).catch(error => {
          console.error('Error recargando documentos:', error);
        });
      }
      
      alert('Documento subido exitosamente');
    },
    onError: (error) => {
      console.error('Error subiendo documento:', error);
      alert('Error al subir el documento');
    }
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const resetForm = () => {
    setFormData({
      related_incident_id: '',
      report_type: '',
      sample_id: '',
      test_date: new Date().toISOString().split('T')[0],
      technician: '',
      test_parameters: '',
      test_results: '',
      conclusion: '',
      recommendations: '',
      status: 'draft'
    });
    setSelectedIncident(null);
    setSelectedReportType('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      await createLabReportMutation.mutateAsync(formData);
    } catch (error) {
      console.error('Error submitting form:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUploadDocument = () => {
    if (!selectedIncidentId) {
      alert('Por favor selecciona una incidencia');
      return;
    }

    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.pdf,.doc,.docx';
    input.onchange = (e) => {
      const file = e.target.files[0];
      if (file) {
        const uploadData = new FormData();
        uploadData.append('file', file);
        uploadData.append('incident_id', selectedIncidentId);
        uploadData.append('document_type', 'lab-report');
        uploadData.append('report_type', attachReportType);
        
        uploadDocumentMutation.mutate(uploadData);
      }
    };
    input.click();
  };

  const handleOpenDocument = (report) => {
    const incidentId = report.related_incident?.id || report.related_incident;
    // Si hay documentos subidos, abrir el primero a través del servidor
    if (uploadedDocuments[incidentId] && uploadedDocuments[incidentId].length > 0) {
      const firstDoc = uploadedDocuments[incidentId][0];
      const apiUrl = `http://localhost:8000/api/documents/open/lab-report/${incidentId}/${firstDoc.filename}`;
      window.open(apiUrl, '_blank');
    } else {
      // Si no hay documentos subidos, intentar abrir el reporte generado
      const apiUrl = `http://localhost:8000/api/documents/open/lab-report/${incidentId}/${report.report_number || report.id}.pdf`;
      window.open(apiUrl, '_blank');
    }
  };

  const handleDeleteReport = async (reportId) => {
    if (window.confirm('¿Estás seguro de que deseas eliminar este reporte?')) {
      try {
        await api.delete(`/documents/lab-reports/${reportId}/`);
        queryClient.invalidateQueries(['labReports']);
        alert('Reporte eliminado exitosamente');
      } catch (error) {
        console.error('Error eliminando reporte:', error);
        alert('Error al eliminar el reporte');
      }
    }
  };

  const handleDeleteDocument = async (incidentId, filename) => {
    if (window.confirm('¿Estás seguro de que deseas eliminar este documento? Esta acción no se puede deshacer.')) {
      try {
        await api.delete(`/documents/delete/lab-report/${incidentId}/${filename}`);
        
        // Recargar documentos para esta incidencia
        const documents = await loadUploadedDocuments(incidentId);
        setUploadedDocuments(prev => ({
          ...prev,
          [incidentId]: documents
        }));
        
        alert('Documento eliminado exitosamente');
      } catch (error) {
        console.error('Error eliminando documento:', error);
        alert('Error al eliminar el documento');
      }
    }
  };

  // Filtrar reportes por término de búsqueda
  const filteredReports = useMemo(() => {
    if (!reports?.results && !reports?.data) return [];
    
    const reportsArray = reports?.results || reports?.data || reports || [];
    
    if (searchTerm) {
      return reportsArray.filter(report => 
        report.report_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        report.related_incident?.code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        report.related_incident?.cliente?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        report.sample_id?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    return reportsArray;
  }, [reports, searchTerm]);

  if (reportsLoading || incidentsLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-violet-50 to-indigo-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-purple-600 mx-auto mb-6"></div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Cargando Reportes</h3>
          <p className="text-gray-600">Preparando la información...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-violet-50 to-indigo-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header Principal */}
        <div className="mb-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
            <div className="mb-6 lg:mb-0">
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                🧪 Reportes de Laboratorio
              </h1>
              <p className="text-lg text-gray-600">
                Gestiona y crea reportes de laboratorio profesionales
              </p>
            </div>
            <div className="flex flex-col sm:flex-row gap-4">
              <button
                onClick={() => setShowCreateModal(true)}
                className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-xl text-white bg-gradient-to-r from-purple-600 to-violet-600 hover:from-purple-700 hover:to-violet-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 shadow-lg hover:shadow-xl transition-all duration-200"
              >
                <PlusIcon className="h-5 w-5 mr-2" />
                Nuevo Reporte
              </button>
              <button
                onClick={() => setShowUploadModal(true)}
                className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-xl text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 shadow-lg hover:shadow-xl transition-all duration-200"
              >
                <DocumentArrowUpIcon className="h-5 w-5 mr-2" />
                Adjuntar Documento
              </button>
            </div>
          </div>
        </div>

        {/* Panel de Búsqueda Avanzada */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-200 mb-8 overflow-hidden">
          <div className="bg-gradient-to-r from-purple-600 to-violet-600 px-6 py-4">
            <div className="flex items-center">
              <MagnifyingGlassIcon className="h-6 w-6 text-white mr-3" />
              <h3 className="text-lg font-semibold text-white">Búsqueda Avanzada</h3>
            </div>
          </div>
          <div className="p-6">
            <div className="flex flex-col lg:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <input
                    type="text"
                    placeholder="🔍 Buscar por número de reporte, código de incidencia, muestra..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full px-4 py-3 pl-12 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200 text-lg"
                  />
                  <MagnifyingGlassIcon className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-gray-700">
                    {filteredReports.length} reporte{filteredReports.length !== 1 ? 's' : ''}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Tabla de Reportes */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden">
          <div className="bg-gradient-to-r from-purple-50 to-violet-50 px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <BeakerIcon className="h-6 w-6 text-purple-600 mr-3" />
                <h3 className="text-xl font-semibold text-gray-900">
                  Reportes de Laboratorio ({filteredReports.length})
                </h3>
              </div>
            </div>
          </div>
          
        <div className="table-container">
          <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">
                    📋 Número de Reporte
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">
                    🔗 Código de Incidencia
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">
                    🧪 Tipo de Reporte
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">
                    📊 Estado
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">
                    📅 Fecha de Creación
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">
                    📄 Documentos
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">
                    ⚙️ Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredReports.map((report) => (
                  <tr key={report.id} className="hover:bg-purple-50 transition-colors duration-200">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10">
                          <div className="h-10 w-10 rounded-full bg-purple-100 flex items-center justify-center">
                            <BeakerIcon className="h-5 w-5 text-purple-600" />
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {report.report_number || `LR-${report.id}`}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-violet-100 text-violet-800">
                        {report.related_incident?.code || 'N/A'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <DocumentTextIcon className="h-4 w-4 text-gray-400 mr-2" />
                        <span className="text-sm text-gray-900">
                          {report.report_type === 'cliente' ? '👤 Cliente' : 
                           report.report_type === 'interno' ? '🏢 Interno' : 
                           report.report_type === 'Cliente' ? '👤 Cliente' :
                           report.report_type === 'Interno' ? '🏢 Interno' : 'N/A'}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${
                        report.status === 'completed' 
                          ? 'bg-green-100 text-green-800' 
                          : report.status === 'draft'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {report.status === 'completed' ? '✅ Completado' : 
                         report.status === 'draft' ? '📝 Borrador' : '⏳ Pendiente'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <CalendarIcon className="h-4 w-4 text-gray-400 mr-2" />
                        <span className="text-sm text-gray-500">
                          {new Date(report.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {uploadedDocuments[report.related_incident?.id]?.length > 0 ? (
                        <div className="flex flex-col space-y-1">
                          {uploadedDocuments[report.related_incident?.id]?.slice(0, 2).map((doc, index) => (
                            <div key={index} className="flex items-center space-x-1">
                              <button
                                onClick={() => {
                                  const apiUrl = `http://localhost:8000/api/documents/open/lab-report/${report.related_incident?.id}/${doc.filename}`;
                                  window.open(apiUrl, '_blank');
                                }}
                                className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-purple-100 text-purple-800 hover:bg-purple-200 cursor-pointer transition-colors flex-1"
                                title={`Abrir ${doc.filename}`}
                              >
                                📄 {doc.filename.length > 15 ? doc.filename.substring(0, 15) + '...' : doc.filename}
                              </button>
                              <button
                                onClick={() => handleDeleteDocument(report.related_incident?.id, doc.filename)}
                                className="inline-flex items-center px-1 py-1 rounded-full text-xs bg-red-100 text-red-800 hover:bg-red-200 cursor-pointer transition-colors"
                                title={`Eliminar ${doc.filename}`}
                              >
                                🗑️
                              </button>
                            </div>
                          ))}
                          {uploadedDocuments[report.related_incident?.id]?.length > 2 && (
                            <span className="text-xs text-gray-500">
                              +{uploadedDocuments[report.related_incident?.id]?.length - 2} más
                            </span>
                          )}
                        </div>
                      ) : (
                        <span className="text-gray-400 text-sm">Sin documentos</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleOpenDocument(report)}
                          className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-lg text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition-colors duration-200 shadow-sm hover:shadow-md"
                          title="Ver documento"
                        >
                          <EyeIcon className="h-4 w-4 mr-1" />
                          Ver
                        </button>
                        <button
                          onClick={() => handleDeleteReport(report.id)}
                          className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-lg text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors duration-200 shadow-sm hover:shadow-md"
                          title="Eliminar reporte"
                        >
                          <TrashIcon className="h-4 w-4 mr-1" />
                          Eliminar
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Modal de Creación de Reporte */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
            <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
              <div className="px-6 py-4 bg-gradient-to-r from-purple-600 to-violet-600 rounded-t-2xl">
                <div className="flex items-center justify-between">
                  <h3 className="text-xl font-semibold text-white flex items-center">
                    <PlusIcon className="h-6 w-6 mr-3" />
                    Crear Reporte de Laboratorio
                  </h3>
                  <button
                    onClick={() => {
                      setShowCreateModal(false);
                      resetForm();
                    }}
                    className="text-white hover:text-gray-200 transition-colors duration-200"
                  >
                    <XMarkIcon className="h-6 w-6" />
                  </button>
                </div>
              </div>
              <div className="p-6">
                <form onSubmit={handleSubmit} className="space-y-8">
                  {/* Selección de Incidencia */}
                  <div className="bg-gradient-to-r from-purple-50 to-violet-50 p-6 rounded-xl border border-purple-200">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                      <BuildingOfficeIcon className="h-5 w-5 text-purple-600 mr-2" />
                      Seleccionar Incidencia
                    </h4>
                    <select
                      name="related_incident_id"
                      value={formData.related_incident_id}
                      onChange={(e) => {
                        setSelectedIncidentId(e.target.value);
                        handleInputChange(e);
                      }}
                      className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 text-lg"
                      required
                    >
                      <option value="">Seleccionar incidencia...</option>
                      {(openIncidents?.data?.results || openIncidents?.results || []).map((incident) => (
                        <option key={incident.id} value={incident.id}>
                          {incident.code} - {incident.cliente} - {incident.provider}
                        </option>
                      ))}
                    </select>
                    
                    {/* Mostrar datos de la incidencia seleccionada */}
                    {selectedIncident && (
                      <div className="mt-4 p-4 bg-white rounded-lg border border-purple-200">
                        <h5 className="font-semibold text-gray-900 mb-2">📋 Datos de la Incidencia:</h5>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                          <div><strong>Cliente:</strong> {selectedIncident.cliente}</div>
                          <div><strong>Obra:</strong> {selectedIncident.obra}</div>
                          <div><strong>SKU:</strong> {selectedIncident.sku}</div>
                          <div><strong>Lote:</strong> {selectedIncident.lote}</div>
                          <div className="md:col-span-2"><strong>Descripción:</strong> {selectedIncident.descripcion}</div>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Tipo de Reporte */}
                  <div className="border-b border-gray-200 pb-6">
                    <h4 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
                      🧪 Tipo de Reporte
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Tipo de Reporte
                        </label>
                        <select
                          name="report_type"
                          value={formData.report_type}
                          onChange={(e) => {
                            setSelectedReportType(e.target.value);
                            handleInputChange(e);
                          }}
                          className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 text-lg"
                          required
                        >
                          <option value="">Seleccionar tipo...</option>
                          <option value="cliente">👤 Reporte para Cliente</option>
                          <option value="interno">🏢 Reporte Interno</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          ID de Muestra
                        </label>
                        <input
                          type="text"
                          name="sample_id"
                          value={formData.sample_id}
                          onChange={handleInputChange}
                          className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 text-lg"
                          placeholder="Ej: MUESTRA-001"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Fecha de Prueba
                        </label>
                        <input
                          type="date"
                          name="test_date"
                          value={formData.test_date}
                          onChange={handleInputChange}
                          className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 text-lg"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Técnico Responsable
                        </label>
                        <input
                          type="text"
                          name="technician"
                          value={formData.technician}
                          onChange={handleInputChange}
                          className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 text-lg"
                          required
                        />
                      </div>
                    </div>
                  </div>

                  {/* Parámetros de Prueba */}
                  <div className="border-b border-gray-200 pb-6">
                    <h4 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
                      🔬 Parámetros de Prueba
                    </h4>
                    <div className="space-y-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Parámetros Evaluados
                        </label>
                        <textarea
                          name="test_parameters"
                          value={formData.test_parameters}
                          onChange={handleInputChange}
                          rows={4}
                          className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 text-lg"
                          placeholder="Describa los parámetros que se evaluarán en la muestra..."
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Resultados de Prueba
                        </label>
                        <textarea
                          name="test_results"
                          value={formData.test_results}
                          onChange={handleInputChange}
                          rows={4}
                          className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 text-lg"
                          placeholder="Ingrese los resultados obtenidos en las pruebas..."
                          required
                        />
                      </div>
                    </div>
                  </div>

                  {/* Conclusiones y Recomendaciones */}
                  <div className="pb-6">
                    <h4 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
                      📊 Conclusiones y Recomendaciones
                    </h4>
                    <div className="space-y-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Conclusión
                        </label>
                        <textarea
                          name="conclusion"
                          value={formData.conclusion}
                          onChange={handleInputChange}
                          rows={4}
                          className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 text-lg"
                          placeholder="Conclusión basada en los resultados obtenidos..."
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Recomendaciones
                        </label>
                        <textarea
                          name="recommendations"
                          value={formData.recommendations}
                          onChange={handleInputChange}
                          rows={4}
                          className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 text-lg"
                          placeholder="Recomendaciones basadas en los resultados..."
                        />
                      </div>
                    </div>
                  </div>

                  {/* Botones de Acción */}
                  <div className="flex justify-end space-x-4 pt-6 border-t border-gray-200">
                    <button
                      type="button"
                      onClick={() => {
                        setShowCreateModal(false);
                        resetForm();
                      }}
                      className="px-6 py-3 text-sm font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-xl transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
                    >
                      Cancelar
                    </button>
                    <button
                      type="submit"
                      disabled={isSubmitting}
                      className="inline-flex items-center px-6 py-3 border border-transparent text-sm font-semibold rounded-xl text-white bg-gradient-to-r from-purple-600 to-violet-600 hover:from-purple-700 hover:to-violet-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50 transition-all duration-200 shadow-lg hover:shadow-xl"
                    >
                      <CheckCircleIcon className="h-5 w-5 mr-2" />
                      {isSubmitting ? 'Creando...' : 'Crear Reporte'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}

        {/* Modal de Subida de Documento */}
        {showUploadModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
            <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-md">
              <div className="px-6 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-t-2xl">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-white flex items-center">
                    <DocumentArrowUpIcon className="h-5 w-5 mr-2" />
                    Adjuntar Documento
                  </h3>
                  <button
                    onClick={() => setShowUploadModal(false)}
                    className="text-white hover:text-gray-200 transition-colors duration-200"
                  >
                    <XMarkIcon className="h-6 w-6" />
                  </button>
                </div>
              </div>
              <div className="p-6">
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tipo de Reporte
                  </label>
                  <select
                    value={attachReportType}
                    onChange={(e) => setAttachReportType(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="cliente">📋 Reporte para Cliente</option>
                    <option value="interno">🔍 Reporte Interno</option>
                  </select>
                  <p className="text-sm text-gray-500 mt-1">
                    {attachReportType === 'cliente' 
                      ? 'Documento que se compartirá con el cliente'
                      : 'Documento interno para análisis técnico'
                    }
                  </p>
                </div>

                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Seleccionar Incidencia
                  </label>
                  <select
                    value={selectedIncidentId}
                    onChange={(e) => setSelectedIncidentId(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Seleccionar incidencia...</option>
                    {(openIncidents?.data?.results || openIncidents?.results || []).map((incident) => (
                      <option key={incident.id} value={incident.id}>
                        {incident.code} - {incident.cliente} - {incident.provider}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="mb-6">
                  <button
                    onClick={handleUploadDocument}
                    className="w-full flex items-center justify-center px-6 py-4 border-2 border-dashed border-gray-300 text-sm font-semibold rounded-xl text-gray-700 bg-white hover:bg-gray-50 hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 shadow-md hover:shadow-lg"
                  >
                    <DocumentArrowUpIcon className="h-5 w-5 mr-3" />
                    📎 Seleccionar Archivo
                  </button>
                </div>

                <div className="flex justify-end pt-4 border-t border-gray-200">
                  <button
                    onClick={() => setShowUploadModal(false)}
                    className="px-6 py-2 text-sm font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
                  >
                    Cancelar
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LabReportsPage;
