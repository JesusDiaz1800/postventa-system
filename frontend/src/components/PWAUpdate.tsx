import React, { useState } from 'react';
import { usePWA } from '../hooks/usePWA';
import { 
  ArrowPathIcon, 
  XMarkIcon, 
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

const PWAUpdate = () => {
  const { updateAvailable, updateApp } = usePWA();
  const [isUpdating, setIsUpdating] = useState(false);
  const [showBanner, setShowBanner] = useState(updateAvailable);

  const handleUpdate = async () => {
    setIsUpdating(true);
    try {
      await updateApp();
    } catch (error) {
      console.error('Error actualizando la app:', error);
      setIsUpdating(false);
    }
  };

  const handleDismiss = () => {
    setShowBanner(false);
  };

  if (!showBanner || !updateAvailable) {
    return null;
  }

  return (
    <div className="fixed top-0 left-0 right-0 z-50 bg-gradient-to-r from-green-600 to-blue-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between py-3">
          <div className="flex items-center space-x-3">
            <div className="flex-shrink-0">
              <ArrowPathIcon className="h-8 w-8 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-sm font-medium">
                Nueva versión disponible
              </h3>
              <p className="text-xs opacity-90 mt-1">
                Actualiza para obtener las últimas mejoras y correcciones
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={handleUpdate}
              disabled={isUpdating}
              className="inline-flex items-center px-3 py-2 border border-transparent text-xs font-medium rounded-md text-green-600 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            >
              {isUpdating ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-green-600 mr-1"></div>
                  Actualizando...
                </>
              ) : (
                <>
                  <ArrowPathIcon className="h-4 w-4 mr-1" />
                  Actualizar
                </>
              )}
            </button>
            
            <button
              onClick={handleDismiss}
              className="inline-flex items-center p-1 border border-transparent text-white hover:bg-white hover:bg-opacity-20 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-white transition-colors duration-200"
            >
              <XMarkIcon className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PWAUpdate;
