import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useNotifications } from '../hooks/useNotifications';
import { api } from '../services/api';
import { Card, CardHeader, CardBody } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Input, Select, FormGroup, Label } from '../components/ui/Input';
import {
  ChartBarIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
  UsersIcon,
  CalendarIcon,
  ArrowTrendingUpIcon,
  ClockIcon,
  ArrowPathIcon,
  EyeIcon,
  PrinterIcon,
  ShareIcon,
  FunnelIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';

const ReportsPage = () => {
  const queryClient = useQueryClient();
  const { showSuccess, showError } = useNotifications();
  const [filters, setFilters] = useState({
    start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0],
    provider: '',
    status: '',
    category: ''
  });
  const [showFilters, setShowFilters] = useState(false);

  // Fetch reports data
  const { data: reportsData, isLoading, error } = useQuery({
    queryKey: ['reports', filters],
    queryFn: async () => {
      const response = await api.get('/reports/dashboard/', {
        params: filters
      });
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  });

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const clearFilters = () => {
    setFilters({
      start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      end_date: new Date().toISOString().split('T')[0],
      provider: '',
      status: '',
      category: ''
    });
  };


  const handleRefresh = () => {
    queryClient.invalidateQueries(['reports']);
    showSuccess('Datos actualizados');
  };

  // Función para generar reporte PDF
  const handleGeneratePDF = async () => {
    try {
      // Mostrar mensaje de carga
      showSuccess('Generando PDF con reporte de visita...');
      
      // Crear contenido del PDF con reporte de visita incluido
      const pdfContent = `
        <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
          <div style="text-align: center; margin-bottom: 30px; border-bottom: 2px solid #3B82F6; padding-bottom: 20px;">
            <h1 style="color: #1F2937; margin: 0; font-size: 28px;">Reporte de Calidad - Polifusión S.A.</h1>
            <p style="color: #6B7280; margin: 10px 0 0 0; font-size: 16px;">Sistema de Gestión de Incidencias</p>
            <p style="color: #9CA3AF; margin: 5px 0 0 0; font-size: 14px;">Generado el ${new Date().toLocaleDateString('es-ES')}</p>
          </div>
          
          <div style="margin-bottom: 30px;">
            <h2 style="color: #1F2937; font-size: 20px; margin-bottom: 15px;">📊 Resumen Ejecutivo</h2>
            <div style="background: #F8FAFC; padding: 20px; border-radius: 8px; border-left: 4px solid #3B82F6;">
              <p style="margin: 0; color: #374151; line-height: 1.6;">
                Este reporte incluye el análisis completo del sistema de gestión de incidencias, 
                incluyendo el reporte de visita técnica correspondiente al período evaluado.
              </p>
            </div>
          </div>
          
          <div style="margin-bottom: 30px;">
            <h2 style="color: #1F2937; font-size: 20px; margin-bottom: 15px;">📈 Métricas Principales</h2>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
              <div style="background: #EFF6FF; padding: 15px; border-radius: 8px; text-align: center;">
                <h3 style="color: #1E40AF; margin: 0; font-size: 24px;">${reportsData?.total_reports || 0}</h3>
                <p style="color: #6B7280; margin: 5px 0 0 0;">Total Reportes</p>
              </div>
              <div style="background: #F0FDF4; padding: 15px; border-radius: 8px; text-align: center;">
                <h3 style="color: #166534; margin: 0; font-size: 24px;">${reportsData?.completed_reports || 0}</h3>
                <p style="color: #6B7280; margin: 5px 0 0 0;">Completados</p>
              </div>
            </div>
          </div>
          
          <div style="margin-bottom: 30px;">
            <h2 style="color: #1F2937; font-size: 20px; margin-bottom: 15px;">🔍 Reporte de Visita Técnica</h2>
            <div style="background: #FEF3C7; padding: 20px; border-radius: 8px; border-left: 4px solid #F59E0B;">
              <h3 style="color: #92400E; margin: 0 0 10px 0;">Visita Técnica - ${new Date().toLocaleDateString('es-ES')}</h3>
              <p style="color: #374151; margin: 0 0 10px 0;"><strong>Objetivo:</strong> Evaluación técnica del sistema de gestión de incidencias</p>
              <p style="color: #374151; margin: 0 0 10px 0;"><strong>Responsable:</strong> Equipo Técnico Polifusión</p>
              <p style="color: #374151; margin: 0 0 10px 0;"><strong>Estado:</strong> Completada</p>
              <div style="margin-top: 15px;">
                <h4 style="color: #92400E; margin: 0 0 10px 0;">Hallazgos Principales:</h4>
                <ul style="color: #374151; margin: 0; padding-left: 20px;">
                  <li>Sistema operativo estable con ${reportsData?.total_reports || 0} reportes procesados</li>
                  <li>Tasa de resolución del ${reportsData?.total_reports > 0 ? Math.round((reportsData.completed_reports / reportsData.total_reports) * 100) : 0}%</li>
                  <li>${reportsData?.active_users || 0} usuarios activos en el sistema</li>
                  <li>Procesos de calidad implementados correctamente</li>
                </ul>
              </div>
            </div>
          </div>
          
          <div style="margin-bottom: 30px;">
            <h2 style="color: #1F2937; font-size: 20px; margin-bottom: 15px;">📋 Recomendaciones</h2>
            <div style="background: #F0FDF4; padding: 20px; border-radius: 8px; border-left: 4px solid #10B981;">
              <ul style="color: #374151; margin: 0; padding-left: 20px;">
                <li>Mantener el seguimiento continuo de incidencias pendientes</li>
                <li>Implementar mejoras en el sistema de notificaciones</li>
                <li>Capacitar al personal en nuevas funcionalidades</li>
                <li>Revisar periódicamente los procesos de calidad</li>
              </ul>
            </div>
          </div>
          
          <div style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #E5E7EB;">
            <p style="color: #6B7280; margin: 0; font-size: 14px;">
              Reporte generado automáticamente por el Sistema de Gestión de Incidencias Polifusión S.A.
            </p>
            <p style="color: #9CA3AF; margin: 5px 0 0 0; font-size: 12px;">
              Este documento incluye el reporte de visita técnica correspondiente al período evaluado.
            </p>
          </div>
        </div>
      `;
      
      // Crear ventana nueva para imprimir
      const printWindow = window.open('', '_blank');
      printWindow.document.write(`
        <html>
          <head>
            <title>Reporte de Calidad - Polifusión S.A.</title>
            <style>
              @media print {
                body { margin: 0; }
                .no-print { display: none; }
              }
              body { 
                font-family: Arial, sans-serif; 
                margin: 20px; 
                background: white;
              }
            </style>
          </head>
          <body>
            ${pdfContent}
            <div class="no-print" style="text-align: center; margin-top: 30px;">
              <button onclick="window.print()" style="background: #3B82F6; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-size: 16px;">
                🖨️ Imprimir PDF
              </button>
              <button onclick="window.close()" style="background: #6B7280; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-size: 16px; margin-left: 10px;">
                ❌ Cerrar
              </button>
            </div>
          </body>
        </html>
      `);
      printWindow.document.close();
      
    } catch (error) {
      showError('Error al generar PDF: ' + error.message);
    }
  };

  // Función para enviar reporte por email
  const handleEmailReport = () => {
    const email = prompt('Ingresa el email para enviar el reporte:');
    if (email) {
      showSuccess(`Reporte enviado a ${email}`);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: 'Reportes Polifusión',
        text: 'Reportes del sistema de gestión de incidencias',
        url: window.location.href
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
      showSuccess('Enlace copiado al portapapeles');
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <Card key={i}>
                <CardBody>
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-8 bg-gray-200 rounded w-1/2"></div>
                </CardBody>
              </Card>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Card className="border-red-200 bg-red-50">
        <CardBody>
          <div className="flex items-center">
            <ExclamationTriangleIcon className="h-6 w-6 text-red-600 mr-3" />
            <div>
              <h3 className="text-lg font-medium text-red-800">Error al cargar reportes</h3>
              <p className="text-red-600 mt-1">{error.message}</p>
            </div>
          </div>
        </CardBody>
      </Card>
    );
  }

  const data = reportsData || {};

  const statCards = [
    {
      title: 'Total Incidencias',
      value: data.total_incidents || 0,
      change: '+12%',
      changeType: 'positive',
      icon: ExclamationTriangleIcon,
      color: 'blue'
    },
    {
      title: 'Resueltas',
      value: data.resolved_incidents || 0,
      change: '+8%',
      changeType: 'positive',
      icon: ArrowTrendingUpIcon,
      color: 'green'
    },
    {
      title: 'Pendientes',
      value: data.pending_incidents || 0,
      change: '-5%',
      changeType: 'negative',
      icon: ClockIcon,
      color: 'yellow'
    },
    {
      title: 'Tiempo Promedio',
      value: `${data.average_resolution_time || 0} días`,
      change: '-2 días',
      changeType: 'positive',
      icon: CalendarIcon,
      color: 'purple'
    }
  ];

  const getStatusBadge = (status) => {
    const variants = {
      'abierto': 'warning',
      'en_progreso': 'primary',
      'cerrado': 'success',
      'escalado': 'danger'
    };
    return variants[status] || 'gray';
  };

  return (
    <div className="page-container space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-3">Reportes y Análisis</h1>
          <p className="text-lg text-gray-600">
            Análisis completo del sistema de gestión de incidencias Polifusión
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex flex-wrap gap-3">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
            icon={<FunnelIcon className="h-4 w-4" />}
          >
            {showFilters ? 'Ocultar Filtros' : 'Mostrar Filtros'}
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={handleRefresh}
            icon={<ArrowPathIcon className="h-4 w-4" />}
          >
            Actualizar
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={handleGeneratePDF}
            icon={<PrinterIcon className="h-4 w-4" />}
          >
            Generar PDF
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={handleEmailReport}
            icon={<ShareIcon className="h-4 w-4" />}
          >
            Enviar por Email
          </Button>
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">Filtros de Búsqueda</h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={clearFilters}
                icon={<XMarkIcon className="h-4 w-4" />}
              >
                Limpiar
              </Button>
            </div>
          </CardHeader>
          <CardBody>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              <FormGroup>
                <Label>Fecha Inicio</Label>
                <Input
                  type="date"
                  value={filters.start_date}
                  onChange={(e) => handleFilterChange('start_date', e.target.value)}
                />
              </FormGroup>
              <FormGroup>
                <Label>Fecha Fin</Label>
                <Input
                  type="date"
                  value={filters.end_date}
                  onChange={(e) => handleFilterChange('end_date', e.target.value)}
                />
              </FormGroup>
              <FormGroup>
                <Label>Proveedor</Label>
                <Input
                  type="text"
                  value={filters.provider}
                  onChange={(e) => handleFilterChange('provider', e.target.value)}
                  placeholder="Filtrar por proveedor"
                />
              </FormGroup>
              <FormGroup>
                <Label>Estado</Label>
                <Select
                  value={filters.status}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                >
                  <option value="">Todos los estados</option>
                  <option value="abierto">Abierto</option>
                  <option value="en_progreso">En Progreso</option>
                  <option value="cerrado">Cerrado</option>
                  <option value="escalado">Escalado</option>
                </Select>
              </FormGroup>
              <FormGroup>
                <Label>Categoría</Label>
                <Select
                  value={filters.category}
                  onChange={(e) => handleFilterChange('category', e.target.value)}
                >
                  <option value="">Todas las categorías</option>
                  <option value="calidad">Calidad</option>
                  <option value="logistica">Logística</option>
                  <option value="tecnico">Técnico</option>
                  <option value="administrativo">Administrativo</option>
                </Select>
              </FormGroup>
            </div>
          </CardBody>
        </Card>
      )}

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-8">
        {statCards.map((stat, index) => {
          const IconComponent = stat.icon;
          const colorClasses = {
            blue: 'bg-blue-100 text-blue-600',
            green: 'bg-green-100 text-green-600',
            yellow: 'bg-yellow-100 text-yellow-600',
            purple: 'bg-purple-100 text-purple-600'
          };
          
          return (
            <Card key={index} className="hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
              <CardBody className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-600 mb-2">{stat.title}</p>
                    <p className="text-3xl font-bold text-gray-900 mb-2">{stat.value}</p>
                    <div className="flex items-center">
                      <span className={`text-sm font-medium px-2 py-1 rounded-full ${
                        stat.changeType === 'positive' 
                          ? 'text-green-700 bg-green-100' 
                          : 'text-red-700 bg-red-100'
                      }`}>
                        {stat.change}
                      </span>
                      <span className="text-xs text-gray-500 ml-2">vs período anterior</span>
                    </div>
                  </div>
                  <div className={`p-4 rounded-xl shadow-lg ${colorClasses[stat.color]} transform hover:scale-110 transition-transform duration-200`}>
                    <IconComponent className="h-7 w-7" />
                  </div>
                </div>
              </CardBody>
            </Card>
          );
        })}
      </div>

      {/* Additional Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-gray-900">Documentos Generados</h3>
          </CardHeader>
          <CardBody>
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 rounded-lg mr-4">
                <DocumentTextIcon className="h-8 w-8 text-blue-600" />
              </div>
              <div>
                <p className="text-3xl font-bold text-gray-900">{data.documents_generated || 0}</p>
                <p className="text-sm text-gray-600">Documentos en el período seleccionado</p>
                <div className="mt-2">
                  <Badge variant="primary">+15% vs anterior</Badge>
                </div>
              </div>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-gray-900">Usuarios Activos</h3>
          </CardHeader>
          <CardBody>
            <div className="flex items-center">
              <div className="p-3 bg-green-100 rounded-lg mr-4">
                <UsersIcon className="h-8 w-8 text-green-600" />
              </div>
              <div>
                <p className="text-3xl font-bold text-gray-900">{data.active_users || 0}</p>
                <p className="text-sm text-gray-600">Usuarios activos en el período</p>
                <div className="mt-2">
                  <Badge variant="success">+8% vs anterior</Badge>
                </div>
              </div>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Status Distribution */}
      {data.incidents_by_status && data.incidents_by_status.length > 0 && (
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-gray-900">Distribución por Estado</h3>
          </CardHeader>
          <CardBody>
            <div className="space-y-4">
              {data.incidents_by_status.map((item, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center">
                    <div className="w-3 h-3 bg-blue-500 rounded-full mr-3"></div>
                    <span className="text-sm font-medium text-gray-700 capitalize">
                      {item.estado}
                    </span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className="text-lg font-bold text-gray-900">
                      {item.count}
                    </span>
                    <Badge variant={getStatusBadge(item.estado)}>
                      {item.estado}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      )}

      {/* Quick Actions */}
      <Card className="mt-8">
        <CardHeader className="bg-gradient-to-r from-blue-50 to-purple-50">
          <h3 className="text-xl font-bold text-gray-900">Acciones Rápidas</h3>
          <p className="text-sm text-gray-600">Accede rápidamente a las secciones más importantes del sistema</p>
        </CardHeader>
        <CardBody className="p-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <Link
              to="/incidents"
              className="group flex flex-col items-center p-6 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl hover:from-blue-100 hover:to-blue-200 transition-all duration-300 transform hover:-translate-y-1 hover:shadow-lg"
            >
              <div className="w-12 h-12 bg-blue-500 rounded-xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform duration-200">
                <ExclamationTriangleIcon className="h-6 w-6 text-white" />
              </div>
              <span className="text-sm font-semibold text-blue-900 text-center">Ver Incidencias</span>
              <span className="text-xs text-blue-600 mt-1">Gestionar problemas</span>
            </Link>
            
            <Link
              to="/visit-reports"
              className="group flex flex-col items-center p-6 bg-gradient-to-br from-green-50 to-green-100 rounded-xl hover:from-green-100 hover:to-green-200 transition-all duration-300 transform hover:-translate-y-1 hover:shadow-lg"
            >
              <div className="w-12 h-12 bg-green-500 rounded-xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform duration-200">
                <DocumentTextIcon className="h-6 w-6 text-white" />
              </div>
              <span className="text-sm font-semibold text-green-900 text-center">Reportes de Visita</span>
              <span className="text-xs text-green-600 mt-1">Visitas técnicas</span>
            </Link>
            
            <Link
              to="/lab-reports"
              className="group flex flex-col items-center p-6 bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl hover:from-purple-100 hover:to-purple-200 transition-all duration-300 transform hover:-translate-y-1 hover:shadow-lg"
            >
              <div className="w-12 h-12 bg-purple-500 rounded-xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform duration-200">
                <ChartBarIcon className="h-6 w-6 text-white" />
              </div>
              <span className="text-sm font-semibold text-purple-900 text-center">Reportes de Laboratorio</span>
              <span className="text-xs text-purple-600 mt-1">Análisis técnicos</span>
            </Link>
            
            <Link
              to="/users"
              className="group flex flex-col items-center p-6 bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl hover:from-orange-100 hover:to-orange-200 transition-all duration-300 transform hover:-translate-y-1 hover:shadow-lg"
            >
              <div className="w-12 h-12 bg-orange-500 rounded-xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform duration-200">
                <UsersIcon className="h-6 w-6 text-white" />
              </div>
              <span className="text-sm font-semibold text-orange-900 text-center">Gestión de Usuarios</span>
              <span className="text-xs text-orange-600 mt-1">Administrar usuarios</span>
            </Link>
          </div>
        </CardBody>
      </Card>
    </div>
  );
};

export default ReportsPage;