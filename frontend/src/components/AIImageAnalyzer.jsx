import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import {
  PhotoIcon,
  CpuChipIcon,
  DocumentTextIcon,
  ArrowDownTrayIcon,
  XMarkIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  LightBulbIcon,
  WrenchScrewdriverIcon,
  EyeIcon,
  ClockIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';
import { useNotifications } from '../hooks/useNotifications';

const AIImageAnalyzer = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const { showSuccess, showError, showWarning } = useNotifications();

  const analyzeImageMutation = useMutation({
    mutationFn: async (imageFile) => {
      const formData = new FormData();
      formData.append('image', imageFile);
      formData.append('analysis_type', 'comprehensive_technical_analysis');
      formData.append('description', 'Análisis técnico completo de imagen para diagnóstico de fallas');
      formData.append('context', 'Sistema de postventa - Análisis de fallas en tuberías, accesorios y componentes');

      try {
        // Importar api dinámicamente para evitar problemas de circularidad
        const { api } = await import('../services/api');

        const response = await api.post('/ai/analyze-image/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        return response.data;
      } catch (error) {
        console.error('Error in image analysis:', error);
        if (error.response) {
          const errorMessage = error.response.data?.error || error.response.data?.message || `Error del servidor: ${error.response.status}`;
          throw new Error(errorMessage);
        }
        throw error;
      }
    },
    onSuccess: (data) => {
      if (data.success) {
        setAnalysisResult({
          analysis: data.analysis,
          confidence_score: data.confidence_score,
          processing_time: data.processing_time,
          tokens_used: data.tokens_used,
          model_used: data.model_used,
          analysis_id: data.analysis_id
        });
      } else {
        throw new Error(data.error || 'Error en el análisis');
      }
    },
    onError: (error) => {
      console.error('Error analyzing image:', error);
      let errorMessage = 'Error al analizar la imagen';

      const response = error.response?.data;
      if (error.response?.status === 429 || error.message.includes('429')) {
        const nextReset = response?.next_reset;
        const timeStr = nextReset ? new Date(nextReset).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'mañana';

        errorMessage = (
          <div className="flex flex-col gap-1">
            <span className="font-bold">Límite de cuota de IA alcanzado</span>
            <span className="text-xs">Se restablecerá aproximadamente a las {timeStr}.</span>
            <span className="text-xs italic">Mientras tanto, el sistema usará el motor local básico.</span>
          </div>
        );
        showWarning(errorMessage);
        return;
      }

      if (error.message.includes('401')) {
        errorMessage = 'Error de autenticación. Por favor, inicia sesión nuevamente.';
      } else if (error.message.includes('500')) {
        errorMessage = 'Error del servidor. Verifica que los proveedores de IA estén configurados.';
      } else if (error.message.includes('413')) {
        errorMessage = 'La imagen es demasiado grande. Máximo 10MB.';
      } else if (error.message) {
        errorMessage = error.message;
      }

      showError(errorMessage);
    },
  });



  const handleImageSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validar tipo de archivo
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'image/bmp'];
      if (!allowedTypes.includes(file.type)) {
        showError('Tipo de archivo no soportado. Use JPG, PNG, GIF, WebP o BMP.');
        return;
      }

      // Validar tamaño (máximo 10MB)
      const maxSize = 10 * 1024 * 1024; // 10MB
      if (file.size > maxSize) {
        showError('El archivo es demasiado grande. Máximo 10MB.');
        return;
      }

      setSelectedImage(file);

      // Crear preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleAnalyze = () => {
    if (selectedImage) {
      analyzeImageMutation.mutate(selectedImage);
    }
  };



  const clearAll = () => {
    setSelectedImage(null);
    setImagePreview(null);
    setAnalysisResult(null);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-2 bg-blue-100 rounded-lg">
            <CpuChipIcon className="h-6 w-6 text-blue-600" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Análisis de Imágenes con IA</h2>
            <p className="text-sm text-gray-600">Analiza muestras e imágenes técnicas para generar informes</p>
          </div>
        </div>
      </div>

      {/* Selección de imagen */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">1. Seleccionar Imagen</h3>

        <div
          className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 hover:bg-blue-50 transition-colors"
          onDrop={(e) => {
            e.preventDefault();
            const files = e.dataTransfer.files;
            if (files.length > 0) {
              handleImageSelect({ target: { files: [files[0]] } });
            }
          }}
          onDragOver={(e) => e.preventDefault()}
          onDragEnter={(e) => e.preventDefault()}
        >
          <input
            type="file"
            accept="image/*"
            onChange={handleImageSelect}
            className="hidden"
            id="image-upload"
          />
          <label
            htmlFor="image-upload"
            className="cursor-pointer flex flex-col items-center space-y-3"
          >
            <PhotoIcon className="h-16 w-16 text-gray-400" />
            <div className="space-y-2">
              <p className="text-lg font-medium text-gray-700">
                {selectedImage ? 'Imagen seleccionada:' : 'Adjuntar imagen para análisis'}
              </p>
              <p className="text-sm text-gray-600">
                {selectedImage ? selectedImage.name : 'Haz clic aquí o arrastra una imagen'}
              </p>
              <p className="text-xs text-gray-500">
                Formatos soportados: JPG, PNG, GIF, WebP, BMP (máx. 10MB)
              </p>
            </div>
          </label>
        </div>

        {imagePreview && (
          <div className="mt-4">
            <img
              src={imagePreview}
              alt="Preview"
              className="max-w-full h-64 object-contain mx-auto rounded-lg border border-gray-200"
            />
          </div>
        )}
      </div>

      {/* Análisis */}
      {selectedImage && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">2. Análisis con IA</h3>

          <div className="flex space-x-4">
            <button
              onClick={handleAnalyze}
              disabled={analyzeImageMutation.isPending}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <CpuChipIcon className="h-5 w-5" />
              <span>
                {analyzeImageMutation.isPending ? 'Analizando...' : 'Analizar Imagen'}
              </span>
            </button>

            <button
              onClick={clearAll}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
            >
              <XMarkIcon className="h-5 w-5" />
              <span>Limpiar</span>
            </button>
          </div>
        </div>
      )}

      {/* Resultados del análisis */}
      {analysisResult && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-medium text-gray-900">3. Resultados del Análisis</h3>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <ClockIcon className="h-4 w-4" />
              <span>Procesado en {analysisResult.processing_time || 'N/A'}s</span>
            </div>
          </div>

          {/* Métricas del análisis */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <ChartBarIcon className="h-5 w-5 text-blue-600" />
                <span className="text-sm font-medium text-blue-900">Confianza</span>
              </div>
              <p className="text-2xl font-bold text-blue-600 mt-1">
                {analysisResult.confidence_score ? `${Math.round(analysisResult.confidence_score * 100)}%` : 'N/A'}
              </p>
            </div>
            <div className="bg-green-50 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <CpuChipIcon className="h-5 w-5 text-green-600" />
                <span className="text-sm font-medium text-green-900">Modelo</span>
              </div>
              <p className="text-sm font-bold text-green-600 mt-1">
                {analysisResult.model_used || 'Gemini Pro'}
              </p>
            </div>
            <div className="bg-purple-50 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <DocumentTextIcon className="h-5 w-5 text-purple-600" />
                <span className="text-sm font-medium text-purple-900">Tokens</span>
              </div>
              <p className="text-sm font-bold text-purple-600 mt-1">
                {analysisResult.tokens_used || 'N/A'}
              </p>
            </div>
          </div>

          {/* Análisis estructurado */}
          <div className="space-y-6">
            {/* Observaciones */}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-3">
                <EyeIcon className="h-5 w-5 text-gray-600" />
                <h4 className="font-medium text-gray-900">Observaciones Técnicas</h4>
              </div>
              <div className="text-sm text-gray-700 whitespace-pre-wrap">
                {analysisResult.analysis?.observations || analysisResult.analysis || 'Análisis no disponible'}
              </div>
            </div>

            {/* Posibles Causas */}
            <div className="bg-red-50 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-3">
                <ExclamationTriangleIcon className="h-5 w-5 text-red-600" />
                <h4 className="font-medium text-red-900">Posibles Causas de Falla</h4>
              </div>
              <div className="text-sm text-red-800 whitespace-pre-wrap">
                {analysisResult.analysis?.possible_causes || 'Análisis de causas no disponible'}
              </div>
            </div>

            {/* Recomendaciones */}
            <div className="bg-green-50 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-3">
                <LightBulbIcon className="h-5 w-5 text-green-600" />
                <h4 className="font-medium text-green-900">Recomendaciones</h4>
              </div>
              <div className="text-sm text-green-800 whitespace-pre-wrap">
                {analysisResult.analysis?.recommendations || 'Recomendaciones no disponibles'}
              </div>
            </div>

            {/* Acciones Correctivas */}
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-3">
                <WrenchScrewdriverIcon className="h-5 w-5 text-blue-600" />
                <h4 className="font-medium text-blue-900">Acciones Correctivas Sugeridas</h4>
              </div>
              <div className="text-sm text-blue-800 whitespace-pre-wrap">
                {analysisResult.analysis?.corrective_actions || 'Acciones correctivas no disponibles'}
              </div>
            </div>
          </div>

          <div className="flex space-x-4 mt-6">
            <button
              onClick={() => {
                const text = `INFORME TÉCNICO DE ANÁLISIS - IA
FECHA: ${new Date().toLocaleString()}
MODELO: ${analysisResult.model_used || 'Gemini 1.5 Flash'}
CONFIANZA: ${analysisResult.confidence_score ? Math.round(analysisResult.confidence_score * 100) + '%' : 'N/A'}

1. OBSERVACIONES TÉCNICAS
${analysisResult.analysis?.observations || 'N/A'}

2. POSIBLES CAUSAS
${Array.isArray(analysisResult.analysis?.possible_causes)
                    ? analysisResult.analysis.possible_causes.map(c => `- ${c}`).join('\n')
                    : analysisResult.analysis?.possible_causes || 'N/A'}

3. RECOMENDACIONES
${Array.isArray(analysisResult.analysis?.recommendations)
                    ? analysisResult.analysis.recommendations.map(r => `- ${r}`).join('\n')
                    : analysisResult.analysis?.recommendations || 'N/A'}

4. ACCIONES CORRECTIVAS
${Array.isArray(analysisResult.analysis?.corrective_actions)
                    ? analysisResult.analysis.corrective_actions.map(a => `- ${a}`).join('\n')
                    : analysisResult.analysis?.corrective_actions || 'N/A'}
`;
                navigator.clipboard.writeText(text);
                showSuccess('Análisis copiado al portapapeles');
              }}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <DocumentTextIcon className="h-5 w-5" />
              <span>Copiar Información</span>
            </button>

            <button
              onClick={() => {
                const text = `INFORME TÉCNICO DE ANÁLISIS - IA
----------------------------------------
FECHA: ${new Date().toLocaleString()}
ID ANÁLISIS: ${analysisResult.analysis_id || 'N/A'}
MODELO: ${analysisResult.model_used || 'Gemini 1.5 Flash'}
CONFIANZA: ${analysisResult.confidence_score ? Math.round(analysisResult.confidence_score * 100) + '%' : 'N/A'}
----------------------------------------

1. OBSERVACIONES TÉCNICAS
----------------------------------------
${analysisResult.analysis?.observations || 'N/A'}

2. POSIBLES CAUSAS
----------------------------------------
${Array.isArray(analysisResult.analysis?.possible_causes)
                    ? analysisResult.analysis.possible_causes.map(c => `- ${c}`).join('\n')
                    : analysisResult.analysis?.possible_causes || 'N/A'}

3. RECOMENDACIONES
----------------------------------------
${Array.isArray(analysisResult.analysis?.recommendations)
                    ? analysisResult.analysis.recommendations.map(r => `- ${r}`).join('\n')
                    : analysisResult.analysis?.recommendations || 'N/A'}

4. ACCIONES CORRECTIVAS
----------------------------------------
${Array.isArray(analysisResult.analysis?.corrective_actions)
                    ? analysisResult.analysis.corrective_actions.map(a => `- ${a}`).join('\n')
                    : analysisResult.analysis?.corrective_actions || 'N/A'}
  
----------------------------------------
Generado por Sistema PostVenta - Módulo IA
`;
                const blob = new Blob([text], { type: 'text/plain' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `Informe_Tecnico_${new Date().toISOString().split('T')[0]}.txt`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                showSuccess('Informe técnico descargado');
              }}
              className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              <ArrowDownTrayIcon className="h-5 w-5" />
              <span>Descargar Informe .TXT</span>
            </button>
          </div>
        </div>
      )}

      {/* Información de uso */}
      <div className="bg-blue-50 rounded-lg p-4">
        <h4 className="font-medium text-blue-900 mb-2">Análisis Técnico con IA - Guía de Uso:</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h5 className="font-medium text-blue-800 mb-2">Tipos de Imágenes Recomendadas:</h5>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• Tuberías con fisuras o corrosión</li>
              <li>• Accesorios con fallas de soldadura</li>
              <li>• Componentes con desgaste anormal</li>
              <li>• Fugas o problemas de presión</li>
              <li>• Defectos de fabricación</li>
            </ul>
          </div>
          <div>
            <h5 className="font-medium text-blue-800 mb-2">Análisis Incluye:</h5>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• Observaciones técnicas detalladas</li>
              <li>• Identificación de posibles causas</li>
              <li>• Recomendaciones de reparación</li>
              <li>• Acciones correctivas sugeridas</li>
              <li>• Nivel de confianza del análisis</li>
            </ul>
          </div>
        </div>
        <div className="mt-3 p-3 bg-blue-100 rounded-lg">
          <p className="text-sm text-blue-800">
            <strong>Nota:</strong> El análisis de IA es una herramienta de apoyo técnico.
            Siempre consulte con especialistas para validar los hallazgos antes de tomar decisiones críticas.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AIImageAnalyzer;
