import React from 'react';
import { useSAPAttachment } from '../hooks/useSAPAttachment';

/**
 * Componente para mostrar una imagen de adjunto SAP de forma segura
 * Carga la imagen con autenticación y la muestra como blob URL
 */
export function SAPAttachmentImage({ atcEntry, line, filename, className = '' }) {
    const { blobUrl, loading, error } = useSAPAttachment(atcEntry, line, true);

    if (loading) {
        return (
            <div className={`${className} flex items-center justify-center bg-gray-100 animate-pulse`}>
                <svg className="h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
            </div>
        );
    }

    if (error || !blobUrl) {
        return (
            <div className={`${className} flex items-center justify-center bg-gray-50 border border-gray-200`}>
                <svg className="h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
            </div>
        );
    }

    return (
        <a href={blobUrl} target="_blank" rel="noopener noreferrer" className="block relative">
            <img
                src={blobUrl}
                alt={filename}
                className={className}
            />
            <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-opacity rounded-lg flex items-center justify-center">
                <svg className="h-8 w-8 text-white opacity-0 group-hover:opacity-100 transition-opacity" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
                </svg>
            </div>
        </a>
    );
}

/**
 * Componente para manejar descarga de archivos no-imagen
 */
export function SAPAttachmentFile({ atcEntry, line, filename, className = '' }) {
    const handleDownload = async () => {
        try {
            const response = await fetch(`/api/sap/attachments/${atcEntry}/${line}/`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });

            if (!response.ok) throw new Error('Download failed');

            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Error downloading attachment:', error);
            alert('Error al descargar el archivo');
        }
    };

    return (
        <button
            onClick={handleDownload}
            className={className}
        >
            <svg className="h-12 w-12 text-gray-400 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
            <p className="text-xs text-gray-600 text-center truncate w-full font-medium">{filename}</p>
        </button>
    );
}
