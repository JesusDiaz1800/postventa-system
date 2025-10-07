import React, { useState, useEffect } from 'react';
import { usePWA } from '../hooks/usePWA';
import { 
  DevicePhoneMobileIcon, 
  XMarkIcon, 
  ArrowDownTrayIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

const PWAInstaller = () => {
  const { 
    isInstalled, 
    canInstall, 
    installApp, 
    isMobile, 
    isIOS, 
    isAndroid 
  } = usePWA();
  
  const [showBanner, setShowBanner] = useState(false);
  const [isInstalling, setIsInstalling] = useState(false);
  const [installSuccess, setInstallSuccess] = useState(false);

  useEffect(() => {
    // Mostrar banner si se puede instalar y no está instalado
    if (canInstall && !isInstalled && !localStorage.getItem('pwa-install-dismissed')) {
      setShowBanner(true);
    }
  }, [canInstall, isInstalled]);

  const handleInstall = async () => {
    setIsInstalling(true);
    try {
      const success = await installApp();
      if (success) {
        setInstallSuccess(true);
        setTimeout(() => {
          setShowBanner(false);
        }, 3000);
      }
    } catch (error) {
      console.error('Error instalando la app:', error);
    } finally {
      setIsInstalling(false);
    }
  };

  const handleDismiss = () => {
    setShowBanner(false);
    localStorage.setItem('pwa-install-dismissed', 'true');
  };

  const handleIOSInstall = () => {
    // Mostrar instrucciones para iOS
    alert(`
Para instalar esta app en iOS:
1. Toca el botón de compartir (📤) en Safari
2. Desplázate hacia abajo y toca "Agregar a pantalla de inicio"
3. Toca "Agregar" para confirmar
    `);
  };

  if (!showBanner || isInstalled) {
    return null;
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between py-3">
          <div className="flex items-center space-x-3">
            <div className="flex-shrink-0">
              <DevicePhoneMobileIcon className="h-8 w-8 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-sm font-medium">
                Instala la app para una mejor experiencia
              </h3>
              <p className="text-xs opacity-90 mt-1">
                Acceso rápido, notificaciones y funcionamiento offline
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {isIOS() ? (
              <button
                onClick={handleIOSInstall}
                className="inline-flex items-center px-3 py-2 border border-transparent text-xs font-medium rounded-md text-blue-600 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
              >
                <ArrowDownTrayIcon className="h-4 w-4 mr-1" />
                Instalar
              </button>
            ) : canInstall ? (
              <button
                onClick={handleInstall}
                disabled={isInstalling}
                className="inline-flex items-center px-3 py-2 border border-transparent text-xs font-medium rounded-md text-blue-600 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
              >
                {isInstalling ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-1"></div>
                    Instalando...
                  </>
                ) : installSuccess ? (
                  <>
                    <CheckCircleIcon className="h-4 w-4 mr-1" />
                    ¡Instalado!
                  </>
                ) : (
                  <>
                    <ArrowDownTrayIcon className="h-4 w-4 mr-1" />
                    Instalar
                  </>
                )}
              </button>
            ) : (
              <div className="text-xs opacity-75">
                {isAndroid() ? 'Usa Chrome para instalar' : 'Usa un navegador compatible'}
              </div>
            )}
            
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

export default PWAInstaller;
