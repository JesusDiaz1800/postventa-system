import { useState, useEffect } from 'react';
import { api } from '../services/api';

/**
 * Hook para cargar adjuntos de SAP de forma segura con autenticación
 * Convierte las respuestas a blob URLs para usar en <img> tags
 */
export function useSAPAttachment(atcEntry, line, isEnabled = true) {
    const [blobUrl, setBlobUrl] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!isEnabled || !atcEntry || !line) return;

        let objectUrl = null;

        const fetchAttachment = async () => {
            setLoading(true);
            setError(null);

            try {
                // Usar api de axios que ya incluye el token de autenticación
                const response = await api.get(`/sap/attachments/${atcEntry}/${line}/`, {
                    responseType: 'blob' // Importante: recibir como blob
                });

                // Crear URL temporal del blob
                objectUrl = URL.createObjectURL(response.data);
                setBlobUrl(objectUrl);
            } catch (err) {
                console.error('Error loading SAP attachment:', err);
                setError(err);
            } finally {
                setLoading(false);
            }
        };

        fetchAttachment();

        // Cleanup: revocar URL cuando se desmonte el componente
        return () => {
            if (objectUrl) {
                URL.revokeObjectURL(objectUrl);
            }
        };
    }, [atcEntry, line, isEnabled]);

    return { blobUrl, loading, error };
}
