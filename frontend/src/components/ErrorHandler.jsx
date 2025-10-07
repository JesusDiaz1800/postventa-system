import React, { useState, useEffect, useCallback } from 'react';
import {
  ExclamationTriangleIcon,
  XMarkIcon,
  ArrowPathIcon,
  InformationCircleIcon,
  BugAntIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';

/**
 * Componente de manejo de errores robusto
 * Proporciona una interfaz unificada para mostrar y manejar errores
 */
const ErrorHandler = ({ 
  error, 
  onRetry, 
  onDismiss, 
  showDetails = false,
  context = 'general',
  severity = 'error' // 'error', 'warning', 'info'
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [errorDetails, setErrorDetails] = useState(null);

  // Procesar información del error
  useEffect(() => {
    if (error) {
      const details = {
        message: error.message || 'Error desconocido',
        code: error.code || error.status || 'UNKNOWN',
        timestamp: new Date().toISOString(),
        context: context,
        severity: severity,
        stack: error.stack,
        response: error.response?.data,
        request: error.config
      };
      setErrorDetails(details);
    }
  }, [error, context, severity]);

  const handleRetry = useCallback(() => {
    if (onRetry) {
      onRetry();
    }
  }, [onRetry]);

  const handleDismiss = useCallback(() => {
    if (onDismiss) {
      onDismiss();
    }
  }, [onDismiss]);

  const getSeverityConfig = (severity) => {
    switch (severity) {
      case 'error':
        return {
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
          textColor: 'text-red-800',
          iconColor: 'text-red-600',
          icon: ExclamationTriangleIcon,
          title: 'Error'
        };
      case 'warning':
        return {
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-200',
          textColor: 'text-yellow-800',
          iconColor: 'text-yellow-600',
          icon: ExclamationTriangleIcon,
          title: 'Advertencia'
        };
      case 'info':
        return {
          bgColor: 'bg-blue-50',
          borderColor: 'border-blue-200',
          textColor: 'text-blue-800',
          iconColor: 'text-blue-600',
          icon: InformationCircleIcon,
          title: 'Información'
        };
      default:
        return {
          bgColor: 'bg-gray-50',
          borderColor: 'border-gray-200',
          textColor: 'text-gray-800',
          iconColor: 'text-gray-600',
          icon: InformationCircleIcon,
          title: 'Notificación'
        };
    }
  };

  const getContextMessage = (context) => {
    const contextMessages = {
      'documents': 'Error al cargar documentos',
      'incidents': 'Error al cargar incidencias',
      'upload': 'Error al subir archivo',
      'download': 'Error al descargar archivo',
      'delete': 'Error al eliminar elemento',
      'network': 'Error de conexión',
      'auth': 'Error de autenticación',
      'general': 'Error en la aplicación'
    };
    return contextMessages[context] || 'Error en la aplicación';
  };

  const getSuggestedActions = (error) => {
    const actions = [];
    
    if (error?.response?.status === 401) {
      actions.push('Verificar credenciales de acceso');
      actions.push('Cerrar sesión y volver a iniciar');
    } else if (error?.response?.status === 403) {
      actions.push('Verificar permisos de usuario');
      actions.push('Contactar al administrador');
    } else if (error?.response?.status === 404) {
      actions.push('Verificar que el recurso existe');
      actions.push('Actualizar la página');
    } else if (error?.response?.status >= 500) {
      actions.push('El servidor está experimentando problemas');
      actions.push('Intentar nuevamente en unos minutos');
    } else if (error?.code === 'NETWORK_ERROR') {
      actions.push('Verificar conexión a internet');
      actions.push('Revisar configuración de red');
    } else {
      actions.push('Intentar la operación nuevamente');
      actions.push('Contactar al soporte técnico si persiste');
    }
    
    return actions;
  };

  if (!error || !errorDetails) return null;

  const config = getSeverityConfig(severity);
  const Icon = config.icon;
  const suggestedActions = getSuggestedActions(error);

  return (
    <div className={`rounded-lg border ${config.borderColor} ${config.bgColor} p-4`}>
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <Icon className={`h-5 w-5 ${config.iconColor}`} />
        </div>
        
        <div className="ml-3 flex-1">
          <div className="flex items-center justify-between">
            <h3 className={`text-sm font-medium ${config.textColor}`}>
              {config.title}: {getContextMessage(context)}
            </h3>
            <div className="flex items-center space-x-2">
              {onRetry && (
                <button
                  onClick={handleRetry}
                  className="inline-flex items-center px-2 py-1 text-xs font-medium text-gray-700 bg-white border border-gray-300 rounded hover:bg-gray-50 transition-colors"
                >
                  <ArrowPathIcon className="h-3 w-3 mr-1" />
                  Reintentar
                </button>
              )}
              {onDismiss && (
                <button
                  onClick={handleDismiss}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <XMarkIcon className="h-4 w-4" />
                </button>
              )}
            </div>
          </div>
          
          <div className="mt-2">
            <p className={`text-sm ${config.textColor}`}>
              {errorDetails.message}
            </p>
            
            {/* Acciones sugeridas */}
            {suggestedActions.length > 0 && (
              <div className="mt-3">
                <p className="text-xs font-medium text-gray-600 mb-2">Acciones sugeridas:</p>
                <ul className="text-xs text-gray-600 space-y-1">
                  {suggestedActions.map((action, index) => (
                    <li key={index} className="flex items-start">
                      <span className="mr-2">•</span>
                      <span>{action}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {/* Detalles técnicos */}
            {showDetails && (
              <div className="mt-4">
                <button
                  onClick={() => setIsExpanded(!isExpanded)}
                  className="flex items-center text-xs font-medium text-gray-600 hover:text-gray-800 transition-colors"
                >
                  <BugAntIcon className="h-3 w-3 mr-1" />
                  {isExpanded ? 'Ocultar detalles' : 'Mostrar detalles técnicos'}
                </button>
                
                {isExpanded && (
                  <div className="mt-3 p-3 bg-gray-100 rounded border text-xs">
                    <div className="space-y-2">
                      <div>
                        <span className="font-medium">Código:</span> {errorDetails.code}
                      </div>
                      <div>
                        <span className="font-medium">Contexto:</span> {errorDetails.context}
                      </div>
                      <div>
                        <span className="font-medium">Timestamp:</span> {errorDetails.timestamp}
                      </div>
                      {errorDetails.response && (
                        <div>
                          <span className="font-medium">Respuesta del servidor:</span>
                          <pre className="mt-1 text-xs bg-white p-2 rounded border overflow-x-auto">
                            {JSON.stringify(errorDetails.response, null, 2)}
                          </pre>
                        </div>
                      )}
                      {errorDetails.stack && (
                        <div>
                          <span className="font-medium">Stack trace:</span>
                          <pre className="mt-1 text-xs bg-white p-2 rounded border overflow-x-auto">
                            {errorDetails.stack}
                          </pre>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Hook para manejo de errores
 */
export const useErrorHandler = () => {
  const [errors, setErrors] = useState([]);
  const [globalError, setGlobalError] = useState(null);

  const addError = useCallback((error, context = 'general', severity = 'error') => {
    const errorId = Date.now().toString();
    const newError = {
      id: errorId,
      error,
      context,
      severity,
      timestamp: new Date()
    };
    
    setErrors(prev => [...prev, newError]);
    
    // Auto-dismiss después de 10 segundos para errores no críticos
    if (severity !== 'error') {
      setTimeout(() => {
        removeError(errorId);
      }, 10000);
    }
    
    return errorId;
  }, []);

  const removeError = useCallback((errorId) => {
    setErrors(prev => prev.filter(err => err.id !== errorId));
  }, []);

  const clearErrors = useCallback(() => {
    setErrors([]);
  }, []);

  const setGlobalErrorHandler = useCallback((error) => {
    setGlobalError(error);
  }, []);

  const clearGlobalError = useCallback(() => {
    setGlobalError(null);
  }, []);

  return {
    errors,
    globalError,
    addError,
    removeError,
    clearErrors,
    setGlobalErrorHandler,
    clearGlobalError
  };
};

export default ErrorHandler;
