
import React, { createContext, useContext, useState, useEffect } from 'react';

const PWAContext = createContext(null);

export const PWAProvider = ({ children }) => {
    const [deferredPrompt, setDeferredPrompt] = useState(null);
    const [isStandalone, setIsStandalone] = useState(false);

    useEffect(() => {
        // Check if standalone
        const checkStandalone = () => {
            const isStandaloneMode = window.matchMedia('(display-mode: standalone)').matches ||
                window.navigator.standalone ||
                document.referrer.includes('android-app://');
            setIsStandalone(isStandaloneMode);
        };

        checkStandalone();
        window.addEventListener('resize', checkStandalone); // Monitor changes

        // Check for globally intercepted prompt (Global Trap)
        if (window.deferredPrompt) {
            setDeferredPrompt(window.deferredPrompt);
            console.log('Restored PWA prompt from global trap');
        }

        // Capture install prompt (if it happens after load)
        const handleBeforeInstallPrompt = (e) => {
            e.preventDefault(); // Prevent browser default
            setDeferredPrompt(e);
            window.deferredPrompt = e; // Sync global
            console.log('PWA Install Prompt captured (React)');
        };

        window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

        return () => {
            window.removeEventListener('resize', checkStandalone);
            window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
        };
    }, []);

    const install = async () => {
        if (!deferredPrompt) return;
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        if (outcome === 'accepted') {
            setDeferredPrompt(null);
        }
    };

    return (
        <PWAContext.Provider value={{ deferredPrompt, isStandalone, install }}>
            {children}
        </PWAContext.Provider>
    );
};

export const usePWA = () => useContext(PWAContext);
