import React, { useState, useEffect } from 'react';
import { usePWA } from '../context/PWAContext';
import {
  DevicePhoneMobileIcon,
  XMarkIcon,
  ArrowDownTrayIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';

const PWAInstaller = () => {
  const { deferredPrompt, isStandalone, install } = usePWA();

  const [showBanner, setShowBanner] = useState(false);
  const [isInstalling, setIsInstalling] = useState(false);
  const [installSuccess, setInstallSuccess] = useState(false);

  // Derive state from context
  const canInstall = !!deferredPrompt;
  const isInstalled = isStandalone;

  useEffect(() => {
    // Show banner if installable and not in standalone mode
    // Also check if previously dismissed? Let's show it anyway if the user asked for it to be visible.
    // User said: "no me da la opcion ... o que me llegue una notificacion".
    // So let's respect dismissal but maybe reset it after some time?
    // For now, simple check.
    // Force show banner if installable (Debugging/User Preference)
    if (canInstall && !isInstalled) {
      setShowBanner(true);
    }
  }, [canInstall, isInstalled]);

  const handleInstall = async () => {
    setIsInstalling(true);
    try {
      await install(); // This triggers the prompt
      // We don't get success callback easily from the prompt() promise in the context 
      // but if deferredPrompt becomes null, it likely worked.
      setInstallSuccess(true);
      setTimeout(() => {
        setShowBanner(false);
      }, 3000);
    } catch (error) {
      console.error('Error initiating install:', error);
    } finally {
      setIsInstalling(false);
    }
  };

  const handleDismiss = () => {
    setShowBanner(false);
    localStorage.setItem('pwa-install-dismissed', 'true');
  };

  if (!showBanner || isInstalled) {
    return null;
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg animate-slide-up">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between py-3">
          <div className="flex items-center space-x-3">
            <div className="flex-shrink-0">
              <DevicePhoneMobileIcon className="h-8 w-8 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-sm font-medium">
                Instala la App Postventa
              </h3>
              <p className="text-xs opacity-90 mt-1">
                Acceso directo y mejor rendimiento.
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handleInstall}
              disabled={isInstalling}
              className="inline-flex items-center px-3 py-2 border border-transparent text-xs font-medium rounded-md text-blue-600 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 transition-colors duration-200"
            >
              {isInstalling ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-1"></div>
                  ...
                </>
              ) : (
                <>
                  <ArrowDownTrayIcon className="h-4 w-4 mr-1" />
                  Instalar
                </>
              )}
            </button>

            <button
              onClick={handleDismiss}
              className="inline-flex items-center p-1 hover:bg-white hover:bg-opacity-20 rounded-md transition-colors"
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
