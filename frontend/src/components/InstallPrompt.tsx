
import React, { useState, useEffect } from 'react';
import { ArrowDownTrayIcon, XMarkIcon } from '@heroicons/react/24/outline';

const InstallPrompt = () => {
    const [deferredPrompt, setDeferredPrompt] = useState(null);
    const [showPrompt, setShowPrompt] = useState(false);

    useEffect(() => {
        // 1. Check if app is already installed/running in standalone
        const isStandalone = window.matchMedia('(display-mode: standalone)').matches;
        if (isStandalone) return;

        // 2. Listen for 'beforeinstallprompt'
        const handler = (e) => {
            e.preventDefault();
            setDeferredPrompt(e);
            // Wait a bit to show prompt after login/load to be less intrusive
            setTimeout(() => setShowPrompt(true), 2000);
        };

        window.addEventListener('beforeinstallprompt', handler);

        return () => window.removeEventListener('beforeinstallprompt', handler);
    }, []);

    const handleInstallClick = async () => {
        if (!deferredPrompt) return;

        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;

        if (outcome === 'accepted') {
            console.log('User accepted the install prompt');
        } else {
            console.log('User dismissed the install prompt');
        }

        setDeferredPrompt(null);
        setShowPrompt(false);
    };

    if (!showPrompt) return null;

    return (
        <div className="fixed bottom-4 right-4 z-50 animate-fade-in-up">
            <div className="bg-gradient-to-r from-indigo-600 to-blue-600 rounded-lg shadow-xl p-4 max-w-sm text-white flex items-center space-x-4 pr-10 relative overflow-hidden">

                {/* Background Decoration */}
                <div className="absolute -right-4 -top-4 bg-white opacity-10 rounded-full h-24 w-24"></div>

                {/* Icon */}
                <div className="bg-white bg-opacity-20 p-2 rounded-lg">
                    <ArrowDownTrayIcon className="h-6 w-6 text-white" />
                </div>

                {/* Text */}
                <div className="flex-1">
                    <h3 className="font-bold text-sm">Instalar Aplicación</h3>
                    <p className="text-xs text-indigo-100 mt-1">
                        Instala Postventa en tu escritorio para una experiencia mejorada.
                    </p>
                </div>

                {/* Close Button */}
                <button
                    onClick={() => setShowPrompt(false)}
                    className="absolute top-2 right-2 p-1 hover:bg-white hover:bg-opacity-20 rounded-full transition-colors"
                >
                    <XMarkIcon className="h-4 w-4 text-white" />
                </button>

                {/* Install Button (Invisible overlay for better UX or actual button?) 
            Let's make the whole card clickable EXCEPT close button, OR add a dedicated button.
            I'll add a dedicated button for clarity.
        */}
            </div>

            {/* Action Button positioned outside/below or inside? Inside is better for compact. 
          Refactoring layout slightly.
       */}
            <div className="absolute bottom-4 right-4 w-full h-full flex items-center justify-end pointer-events-none">
                {/* Re-doing the return structure for better click handling */}
            </div>
        </div>
    );
};

// Re-write component for better structure
const InstallPromptRefined = () => {
    const [deferredPrompt, setDeferredPrompt] = useState(null);
    const [showPrompt, setShowPrompt] = useState(false);
    const [isDismissed, setIsDismissed] = useState(false);

    useEffect(() => {
        const isStandalone = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone;
        if (isStandalone) return;

        // Check if user previously dismissed in this session (optional, using state)
        // For "always offer if not installed", we skip persistent storage dismissal for now, 
        // relying on component lifecycle (per session/refresh).

        const handler = (e) => {
            e.preventDefault();
            setDeferredPrompt(e);
            // Small delay for animation entry
            setTimeout(() => setShowPrompt(true), 3000);
        };

        window.addEventListener('beforeinstallprompt', handler);

        return () => window.removeEventListener('beforeinstallprompt', handler);
    }, []);

    const handleInstallClick = async () => {
        if (!deferredPrompt) return;
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        setDeferredPrompt(null);
        setShowPrompt(false);
    };

    const handleDismiss = () => {
        setShowPrompt(false);
        setIsDismissed(true);
    };

    if (!showPrompt || isDismissed) return null;

    return (
        <div className="fixed bottom-6 right-6 z-50 animate-slide-in-right">
            <div className="bg-white border-l-4 border-indigo-600 rounded-lg shadow-2xl p-4 max-w-md flex items-start space-x-4">
                <div className="flex-shrink-0">
                    <div className="bg-indigo-100 p-2 rounded-full">
                        <ArrowDownTrayIcon className="h-6 w-6 text-indigo-600" />
                    </div>
                </div>
                <div className="flex-1 pt-1">
                    <p className="text-sm font-medium text-gray-900">
                        Instalar App de Escritorio
                    </p>
                    <p className="mt-1 text-sm text-gray-500">
                        Obtén acceso rápido y modo pantalla completa instalando la aplicación.
                    </p>
                    <div className="mt-4 flex space-x-3">
                        <button
                            onClick={handleInstallClick}
                            className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                        >
                            Instalar Ahora
                        </button>
                        <button
                            onClick={handleDismiss}
                            className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                        >
                            Más tarde
                        </button>
                    </div>
                </div>
                <button
                    onClick={handleDismiss}
                    className="flex-shrink-0 ml-4 text-gray-400 hover:text-gray-500"
                >
                    <XMarkIcon className="h-5 w-5" />
                </button>
            </div>
        </div>
    );
};

export default InstallPromptRefined;
