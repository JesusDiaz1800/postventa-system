import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  CpuChipIcon, 
  PhotoIcon,
  DocumentTextIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';
import PageHeader from '../components/PageHeader';
import AIImageAnalyzer from '../components/AIImageAnalyzer';
import { useNotifications } from '../hooks/useNotifications';

interface ImageAnalysisResult {
  tipo_falla: string;
  descripcion_visual: string;
  posibles_causas: string[];
  severidad: string;
  recomendaciones_inmediatas: string[];
  recomendaciones_preventivas: string[];
  material_afectado: string;
  condiciones_ambientales: string;
}

interface ProblemRedactionResult {
  titulo_profesional: string;
  descripcion_redactada: string;
  justificacion_tecnica: string;
  contexto_operacional: string;
  terminologia_utilizada: string[];
  nivel_urgencia: string;
  recomendacion_redaccion: string;
}

export function AIPage() {
  const [activeTab, setActiveTab] = useState('image-analysis');
  const { showSuccess, showError } = useNotifications();

  // Estados para análisis de imagen (manejados por AIImageAnalyzer)

  // Estados para redacción de problemas
  const [problemDescription, setProblemDescription] = useState('');
  const [problemRedactionResult, setProblemRedactionResult] = useState<ProblemRedactionResult | null>(null);
  const [isRedactingProblem, setIsRedactingProblem] = useState(false);

  const tabs = [
    { id: 'image-analysis', name: 'Análisis de Imágenes', icon: PhotoIcon },
    { id: 'problem-redaction', name: 'Redacción Profesional', icon: DocumentTextIcon },
  ];

  // Función para analizar imagen (manejada por AIImageAnalyzer)

  // Función para redactar problema
  const handleProblemRedaction = async () => {
    if (!problemDescription.trim()) {
      showError('Por favor, describe el problema que deseas redactar');
      return;
    }

    setIsRedactingProblem(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/ai/professionalize-description/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          problem_description: problemDescription
        }),
      });

      if (!response.ok) {
        let errorMessage = 'Error al redactar el problema';
        try {
          const errorData = await response.json();
          errorMessage = errorData.error || errorMessage;
        } catch (e) {
          errorMessage = `Error del servidor: ${response.status}`;
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();
      
      if (data.success) {
        setProblemRedactionResult(data.redaction);
        showSuccess('Redacción profesional completada exitosamente');
      } else {
        showError(data.error || 'Error al redactar el problema');
      }
    } catch (error) {
      console.error('Error redacting problem:', error);
      showError(error.message || 'Error de conexión al redactar el problema');
    } finally {
      setIsRedactingProblem(false);
    }
  };

  return (
    <div className="p-6">
      {/* Header */}
      <PageHeader
        title="Análisis con Inteligencia Artificial"
        subtitle="Herramientas especializadas para análisis de fallas y redacción profesional"
        icon={CpuChipIcon}
        showLogo={true}
      >
        <div className="flex items-center text-sm text-gray-600">
          <CpuChipIcon className="h-4 w-4 mr-1" />
          Servicio Gemini AI Operativo
        </div>
      </PageHeader>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-4 w-4 mr-2" />
                {tab.name}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Content */}
      {activeTab === 'image-analysis' && (
        <div className="space-y-6">
          {/* Análisis de Imágenes */}
          <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
            <div className="flex items-center mb-6">
              <PhotoIcon className="h-8 w-8 text-blue-600 mr-3" />
              <div>
                <h3 className="text-xl font-semibold text-gray-900">Análisis de Imágenes de Fallas</h3>
                <p className="text-gray-600">Sube una imagen de la tubería, accesorio o falla para obtener un análisis técnico detallado con IA</p>
              </div>
            </div>

            <AIImageAnalyzer />
          </div>
        </div>
      )}

      {activeTab === 'problem-redaction' && (
        <div className="space-y-6">
          {/* Redacción Profesional */}
          <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
            <div className="flex items-center mb-6">
              <DocumentTextIcon className="h-8 w-8 text-green-600 mr-3" />
              <div>
                <h3 className="text-xl font-semibold text-gray-900">Redacción Profesional de Problemas</h3>
                <p className="text-gray-600">Describe el problema y obtén una redacción profesional que justifique la situación sin atribuir culpa</p>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Descripción del Problema
                </label>
                <textarea
                  value={problemDescription}
                  onChange={(e) => setProblemDescription(e.target.value)}
                  placeholder="Describe el problema tal como lo observaste, sin preocuparte por la redacción. La IA lo reformulará de manera profesional."
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 resize-none"
                  rows={4}
                />
              </div>

              <button
                onClick={handleProblemRedaction}
                disabled={isRedactingProblem || !problemDescription.trim()}
                className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isRedactingProblem ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Redactando...
                  </>
                ) : (
                  <>
                    <DocumentTextIcon className="h-4 w-4 mr-2" />
                    Redactar Profesionalmente
                  </>
                )}
              </button>
            </div>

            {/* Resultado de la Redacción */}
            {problemRedactionResult && (
              <div className="mt-8 p-6 bg-gray-50 rounded-lg">
                <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <CheckCircleIcon className="h-5 w-5 text-green-600 mr-2" />
                  Redacción Profesional
                </h4>
                
                <div className="space-y-4">
                  <div>
                    <h5 className="font-medium text-gray-900 mb-2">Título Profesional</h5>
                    <p className="text-gray-700 bg-white p-3 rounded border font-medium">{problemRedactionResult.titulo_profesional}</p>
                  </div>
                  
                  <div>
                    <h5 className="font-medium text-gray-900 mb-2">Descripción Redactada</h5>
                    <p className="text-gray-700 bg-white p-3 rounded border">{problemRedactionResult.descripcion_redactada}</p>
                  </div>
                  
                  <div>
                    <h5 className="font-medium text-gray-900 mb-2">Justificación Técnica</h5>
                    <p className="text-gray-700 bg-white p-3 rounded border">{problemRedactionResult.justificacion_tecnica}</p>
                  </div>
                  
                  <div>
                    <h5 className="font-medium text-gray-900 mb-2">Contexto Operacional</h5>
                    <p className="text-gray-700 bg-white p-3 rounded border">{problemRedactionResult.contexto_operacional}</p>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h5 className="font-medium text-gray-900 mb-2">Nivel de Urgencia</h5>
                      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                        problemRedactionResult.nivel_urgencia === 'Alto' ? 'bg-red-100 text-red-800' :
                        problemRedactionResult.nivel_urgencia === 'Medio' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {problemRedactionResult.nivel_urgencia}
                      </span>
                    </div>
                    
                    <div>
                      <h5 className="font-medium text-gray-900 mb-2">Terminología Utilizada</h5>
                      <div className="flex flex-wrap gap-1">
                        {problemRedactionResult.terminologia_utilizada.map((term, index) => (
                          <span key={index} className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800">
                            {term}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h5 className="font-medium text-gray-900 mb-2">Recomendación de Redacción</h5>
                    <p className="text-gray-700 bg-white p-3 rounded border">{problemRedactionResult.recomendacion_redaccion}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default AIPage;