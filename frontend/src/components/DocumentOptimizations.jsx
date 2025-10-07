import React, { useState, useCallback, useMemo } from 'react';
import {
  ArrowPathIcon,
  ChartBarIcon,
  CpuChipIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';

/**
 * Componente de optimizaciones de rendimiento para el sistema de documentos
 * Proporciona herramientas para mejorar la carga y rendimiento
 */
const DocumentOptimizations = ({ 
  documents, 
  onOptimize, 
  onClearCache, 
  onRefreshData,
  isLoading = false 
}) => {
  const [showOptimizations, setShowOptimizations] = useState(false);
  const [optimizationStatus, setOptimizationStatus] = useState('idle'); // 'idle', 'optimizing', 'success', 'error'

  // Estadísticas de rendimiento
  const performanceStats = useMemo(() => {
    if (!documents) return null;
    
    const totalSize = documents.reduce((sum, doc) => sum + (doc.file_size || 0), 0);
    const avgSize = totalSize / documents.length || 0;
    const largeFiles = documents.filter(doc => (doc.file_size || 0) > 10 * 1024 * 1024).length; // > 10MB
    
    return {
      totalDocuments: documents.length,
      totalSize: totalSize,
      averageSize: avgSize,
      largeFiles: largeFiles,
      memoryUsage: Math.round((totalSize / 1024 / 1024) * 0.1), // Estimación aproximada
    };
  }, [documents]);

  // Optimizaciones disponibles
  const optimizations = [
    {
      id: 'lazy-loading',
      title: 'Carga Diferida',
      description: 'Carga documentos solo cuando son visibles',
      impact: 'Alto',
      status: 'available',
      icon: ClockIcon,
      benefits: ['Reducción del tiempo de carga inicial', 'Menor uso de memoria', 'Mejor experiencia de usuario']
    },
    {
      id: 'image-compression',
      title: 'Compresión de Imágenes',
      description: 'Optimiza automáticamente las imágenes',
      impact: 'Medio',
      status: 'available',
      icon: CpuChipIcon,
      benefits: ['Reducción del tamaño de archivos', 'Carga más rápida', 'Menor uso de ancho de banda']
    },
    {
      id: 'cache-optimization',
      title: 'Optimización de Caché',
      description: 'Mejora el almacenamiento en caché',
      impact: 'Alto',
      status: 'available',
      icon: ArrowPathIcon,
      benefits: ['Acceso más rápido a documentos', 'Menor carga del servidor', 'Mejor rendimiento offline']
    },
    {
      id: 'virtual-scrolling',
      title: 'Desplazamiento Virtual',
      description: 'Renderiza solo elementos visibles',
      impact: 'Alto',
      status: 'available',
      icon: ChartBarIcon,
      benefits: ['Manejo de grandes listas', 'Rendimiento constante', 'Menor uso de DOM']
    },
    {
      id: 'prefetch-documents',
      title: 'Precarga Inteligente',
      description: 'Precarga documentos basado en patrones de uso',
      impact: 'Medio',
      status: 'available',
      icon: InformationCircleIcon,
      benefits: ['Navegación más fluida', 'Predicción de uso', 'Experiencia más rápida']
    },
    {
      id: 'document-indexing',
      title: 'Indexación de Documentos',
      description: 'Crea índices para búsquedas más rápidas',
      impact: 'Alto',
      status: 'available',
      icon: CheckCircleIcon,
      benefits: ['Búsquedas instantáneas', 'Filtrado eficiente', 'Mejor organización']
    }
  ];

  const handleOptimize = useCallback(async (optimizationId) => {
    setOptimizationStatus('optimizing');
    
    try {
      // Simular proceso de optimización
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      if (onOptimize) {
        await onOptimize(optimizationId);
      }
      
      setOptimizationStatus('success');
      setTimeout(() => setOptimizationStatus('idle'), 3000);
    } catch (error) {
      setOptimizationStatus('error');
      setTimeout(() => setOptimizationStatus('idle'), 3000);
    }
  }, [onOptimize]);

  const handleClearCache = useCallback(async () => {
    setOptimizationStatus('optimizing');
    
    try {
      if (onClearCache) {
        await onClearCache();
      }
      
      setOptimizationStatus('success');
      setTimeout(() => setOptimizationStatus('idle'), 3000);
    } catch (error) {
      setOptimizationStatus('error');
      setTimeout(() => setOptimizationStatus('idle'), 3000);
    }
  }, [onClearCache]);

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getImpactColor = (impact) => {
    switch (impact) {
      case 'Alto': return 'text-red-600 bg-red-100';
      case 'Medio': return 'text-yellow-600 bg-yellow-100';
      case 'Bajo': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'optimizing':
        return <ArrowPathIcon className="h-5 w-5 text-blue-600 animate-spin" />;
      case 'success':
        return <CheckCircleIcon className="h-5 w-5 text-green-600" />;
      case 'error':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-600" />;
      default:
        return <CpuChipIcon className="h-5 w-5 text-gray-600" />;
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 bg-gradient-to-r from-purple-600 to-indigo-600">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-white/20 rounded-lg">
              <CpuChipIcon className="h-6 w-6 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">Optimizaciones de Rendimiento</h3>
              <p className="text-purple-100 text-sm">Mejora la velocidad y eficiencia del sistema</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {performanceStats && (
              <div className="text-right text-purple-100 text-sm">
                <div>{performanceStats.totalDocuments} documentos</div>
                <div>{formatFileSize(performanceStats.totalSize)} total</div>
              </div>
            )}
            <button
              onClick={() => setShowOptimizations(!showOptimizations)}
              className="p-2 text-white/80 hover:text-white hover:bg-white/20 rounded-lg transition-colors"
            >
              <InformationCircleIcon className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Estadísticas de rendimiento */}
      {performanceStats && (
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">{performanceStats.totalDocuments}</p>
              <p className="text-sm text-gray-500">Documentos</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">{formatFileSize(performanceStats.totalSize)}</p>
              <p className="text-sm text-gray-500">Tamaño Total</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">{formatFileSize(performanceStats.averageSize)}</p>
              <p className="text-sm text-gray-500">Tamaño Promedio</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">{performanceStats.largeFiles}</p>
              <p className="text-sm text-gray-500">Archivos Grandes</p>
            </div>
          </div>
        </div>
      )}

      {/* Optimizaciones */}
      {showOptimizations && (
        <div className="p-6 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {optimizations.map((optimization) => {
              const IconComponent = optimization.icon || CpuChipIcon;
              return (
                <div
                  key={optimization.id}
                  className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-all duration-200 hover:border-blue-300"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-start space-x-3">
                      <div className="p-2 bg-blue-50 rounded-lg">
                        <IconComponent className="h-5 w-5 text-blue-600" />
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-900">{optimization.title}</h4>
                        <p className="text-sm text-gray-600 mt-1">{optimization.description}</p>
                        {optimization.benefits && (
                          <ul className="text-xs text-gray-500 mt-2 space-y-1">
                            {optimization.benefits.slice(0, 2).map((benefit, index) => (
                              <li key={index} className="flex items-center">
                                <CheckCircleIcon className="h-3 w-3 text-green-500 mr-1" />
                                {benefit}
                              </li>
                            ))}
                          </ul>
                        )}
                      </div>
                    </div>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getImpactColor(optimization.impact)}`}>
                      {optimization.impact}
                    </span>
                  </div>
                  
                  <button
                    onClick={() => handleOptimize(optimization.id)}
                    disabled={optimizationStatus === 'optimizing'}
                    className="w-full flex items-center justify-center px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {getStatusIcon(optimizationStatus)}
                    <span className="ml-2">
                      {optimizationStatus === 'optimizing' ? 'Optimizando...' : 'Aplicar Optimización'}
                    </span>
                  </button>
                </div>
              );
            })}
          </div>

          {/* Acciones adicionales */}
          <div className="pt-4 border-t border-gray-200">
            <div className="flex flex-col sm:flex-row gap-3">
              <button
                onClick={handleClearCache}
                disabled={optimizationStatus === 'optimizing'}
                className="flex items-center justify-center px-4 py-2 text-sm font-medium text-orange-600 bg-orange-50 hover:bg-orange-100 rounded-lg transition-colors disabled:opacity-50"
              >
                <ArrowPathIcon className="h-4 w-4 mr-2" />
                Limpiar Caché
              </button>
              
              <button
                onClick={onRefreshData}
                disabled={isLoading}
                className="flex items-center justify-center px-4 py-2 text-sm font-medium text-green-600 bg-green-50 hover:bg-green-100 rounded-lg transition-colors disabled:opacity-50"
              >
                <ArrowPathIcon className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                Actualizar Datos
              </button>
            </div>
          </div>

          {/* Estado de optimización */}
          {optimizationStatus !== 'idle' && (
            <div className={`p-4 rounded-lg border ${
              optimizationStatus === 'success' 
                ? 'bg-green-50 border-green-200 text-green-800'
                : optimizationStatus === 'error'
                ? 'bg-red-50 border-red-200 text-red-800'
                : 'bg-blue-50 border-blue-200 text-blue-800'
            }`}>
              <div className="flex items-center space-x-2">
                {getStatusIcon(optimizationStatus)}
                <span className="font-medium">
                  {optimizationStatus === 'success' && 'Optimización completada exitosamente'}
                  {optimizationStatus === 'error' && 'Error en la optimización'}
                  {optimizationStatus === 'optimizing' && 'Aplicando optimizaciones...'}
                </span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DocumentOptimizations;
