import React, { useState, useEffect } from 'react';
import {
  SparklesIcon,
  LightBulbIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  EyeIcon,
  CpuChipIcon,
  DocumentTextIcon,
  UserGroupIcon
} from '@heroicons/react/24/outline';

/**
 * Componente de insights de IA para análisis inteligente de datos
 */
const AIInsights = ({ documents, incidents, users }) => {
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');

  const categories = [
    { id: 'all', name: 'Todos', icon: SparklesIcon },
    { id: 'performance', name: 'Rendimiento', icon: ChartBarIcon },
    { id: 'trends', name: 'Tendencias', icon: ArrowTrendingUpIcon },
    { id: 'recommendations', name: 'Recomendaciones', icon: LightBulbIcon },
    { id: 'alerts', name: 'Alertas', icon: ExclamationTriangleIcon }
  ];

  // Simular análisis de IA
  useEffect(() => {
    const generateInsights = () => {
      const mockInsights = [
        {
          id: 1,
          category: 'performance',
          type: 'optimization',
          title: 'Optimización de Carga de Documentos',
          description: 'El sistema detectó que los documentos se cargan 23% más lento durante las horas pico (9:00-11:00 AM).',
          impact: 'high',
          confidence: 94,
          recommendation: 'Implementar caché inteligente durante horas pico',
          metrics: {
            current: '4.2s',
            optimized: '2.8s',
            improvement: '33%'
          },
          icon: CpuChipIcon,
          color: 'blue'
        },
        {
          id: 2,
          category: 'trends',
          type: 'pattern',
          title: 'Patrón de Incidencias Detectado',
          description: 'Las incidencias relacionadas con "Tubería PPR" aumentan un 45% los viernes.',
          impact: 'medium',
          confidence: 87,
          recommendation: 'Preparar recursos adicionales los viernes',
          metrics: {
            pattern: 'Viernes',
            increase: '+45%',
            frequency: 'Semanal'
          },
          icon: ChartBarIcon,
          color: 'orange'
        },
        {
          id: 3,
          category: 'recommendations',
          type: 'suggestion',
          title: 'Automatización Recomendada',
          description: 'El 78% de las incidencias de "Baja" prioridad siguen el mismo flujo de resolución.',
          impact: 'high',
          confidence: 91,
          recommendation: 'Crear workflow automatizado para incidencias de baja prioridad',
          metrics: {
            automation: '78%',
            time_saved: '2.5h',
            efficiency: '+40%'
          },
          icon: LightBulbIcon,
          color: 'green'
        },
        {
          id: 4,
          category: 'alerts',
          type: 'warning',
          title: 'Alerta de Rendimiento',
          description: 'El tiempo de respuesta del sistema ha aumentado un 15% en la última semana.',
          impact: 'high',
          confidence: 96,
          recommendation: 'Revisar configuración del servidor y optimizar consultas',
          metrics: {
            current: '1.8s',
            previous: '1.5s',
            increase: '+15%'
          },
          icon: ExclamationTriangleIcon,
          color: 'red'
        },
        {
          id: 5,
          category: 'trends',
          type: 'prediction',
          title: 'Predicción de Carga',
          description: 'Basado en patrones históricos, se espera un aumento del 30% en documentos la próxima semana.',
          impact: 'medium',
          confidence: 82,
          recommendation: 'Aumentar capacidad de almacenamiento y preparar recursos',
          metrics: {
            prediction: '+30%',
            timeframe: '7 días',
            accuracy: '82%'
          },
          icon: ArrowTrendingUpIcon,
          color: 'purple'
        },
        {
          id: 6,
          category: 'recommendations',
          type: 'optimization',
          title: 'Optimización de Usuarios',
          description: 'Los usuarios que usan filtros avanzados resuelven incidencias 60% más rápido.',
          impact: 'medium',
          confidence: 89,
          recommendation: 'Promover el uso de filtros avanzados con tutoriales',
          metrics: {
            improvement: '+60%',
            users: '23%',
            potential: 'Alto'
          },
          icon: UserGroupIcon,
          color: 'indigo'
        }
      ];

      setInsights(mockInsights);
      setLoading(false);
    };

    const timer = setTimeout(generateInsights, 2000);
    return () => clearTimeout(timer);
  }, [documents, incidents, users]);

  const filteredInsights = selectedCategory === 'all' 
    ? insights 
    : insights.filter(insight => insight.category === selectedCategory);

  const getImpactColor = (impact) => {
    switch (impact) {
      case 'high': return 'text-red-600 bg-red-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 90) return 'text-green-600';
    if (confidence >= 75) return 'text-yellow-600';
    return 'text-red-600';
  };

  const InsightCard = ({ insight }) => {
    const IconComponent = insight.icon;
    
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-all duration-200">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-start space-x-3">
            <div className={`p-2 rounded-lg bg-${insight.color}-50`}>
              <IconComponent className={`h-5 w-5 text-${insight.color}-600`} />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900 mb-1">{insight.title}</h3>
              <p className="text-sm text-gray-600 mb-3">{insight.description}</p>
              <div className="flex items-center space-x-4 text-xs">
                <span className={`px-2 py-1 rounded-full font-medium ${getImpactColor(insight.impact)}`}>
                  Impacto {insight.impact}
                </span>
                <span className={`font-medium ${getConfidenceColor(insight.confidence)}`}>
                  {insight.confidence}% confianza
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Métricas */}
        {insight.metrics && (
          <div className="mb-4 p-3 bg-gray-50 rounded-lg">
            <div className="grid grid-cols-3 gap-4 text-center">
              {Object.entries(insight.metrics).map(([key, value]) => (
                <div key={key}>
                  <div className="text-lg font-semibold text-gray-900">{value}</div>
                  <div className="text-xs text-gray-500 capitalize">{key.replace('_', ' ')}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recomendación */}
        <div className="border-t border-gray-200 pt-4">
          <div className="flex items-start space-x-2">
            <CheckCircleIcon className="h-4 w-4 text-green-500 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-gray-900">Recomendación:</p>
              <p className="text-sm text-gray-600">{insight.recommendation}</p>
            </div>
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
        <div className="flex items-center justify-center space-x-3">
          <CpuChipIcon className="h-6 w-6 text-indigo-600 animate-pulse" />
          <span className="text-gray-600">Analizando datos con IA...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-indigo-100 rounded-lg">
              <SparklesIcon className="h-6 w-6 text-indigo-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">Insights de IA</h2>
              <p className="text-sm text-gray-600">Análisis inteligente y recomendaciones automáticas</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-indigo-600">{insights.length}</div>
            <div className="text-sm text-gray-500">Insights encontrados</div>
          </div>
        </div>
      </div>

      {/* Filtros */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <div className="flex flex-wrap gap-2">
          {categories.map((category) => {
            const Icon = category.icon;
            const count = category.id === 'all' 
              ? insights.length 
              : insights.filter(i => i.category === category.id).length;
            
            return (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedCategory === category.id
                    ? 'bg-indigo-100 text-indigo-700 border border-indigo-200'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{category.name}</span>
                <span className="bg-white/50 px-2 py-0.5 rounded-full text-xs">{count}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredInsights.map((insight) => (
          <InsightCard key={insight.id} insight={insight} />
        ))}
      </div>

      {filteredInsights.length === 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
          <EyeIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No hay insights disponibles</h3>
          <p className="text-gray-600">No se encontraron insights para la categoría seleccionada.</p>
        </div>
      )}
    </div>
  );
};

export default AIInsights;
