import React from 'react';
import { usePWA } from '../hooks/usePWA';
import { 
  WifiIcon, 
  ExclamationTriangleIcon 
} from '@heroicons/react/24/outline';

const OfflineIndicator = () => {
  const { isOnline } = usePWA();

  if (isOnline) {
    return null;
  }

  return (
    <div className="fixed top-0 left-0 right-0 z-40 bg-red-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-center py-2">
          <div className="flex items-center space-x-2">
            <ExclamationTriangleIcon className="h-5 w-5" />
            <span className="text-sm font-medium">
              Sin conexión - Modo offline activado
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OfflineIndicator;
