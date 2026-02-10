import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';

/**
 * Hook para buscar clientes en SAP
 * @param {string} query - Texto de búsqueda (nombre o RUT)
 */
export const useSAPCustomerSearch = (query) => {
    return useQuery({
        queryKey: ['sap-customers', query],
        queryFn: async () => {
            if (!query || query.length < 3) return [];
            const response = await api.get(`/sap/customers/search/?q=${query}`);
            return response.data.results;
        },
        enabled: !!query && query.length >= 3,
        staleTime: 300000, // 5 min
        retry: false
    });
};

/**
 * Hook para obtener una llamada de servicio de SAP por ID
 * @param {string|number} callId - ID de la llamada de servicio
 */
export const useSAPServiceCall = (callId) => {
    return useQuery({
        queryKey: ['sap-service-call', callId],
        queryFn: async () => {
            const response = await api.get(`/sap/service-calls/${callId}/`);
            return response.data;
        },
        enabled: !!callId && String(callId).length > 0,
        retry: false,
        staleTime: 60000 // 1 min
    });
};

/**
 * Hook para obtener proyectos (obras) de un cliente SAP
 * @param {string} cardCode - Código del cliente (CardCode)
 */
export const useSAPCustomerProjects = (cardCode) => {
    return useQuery({
        queryKey: ['sap-customer-projects', cardCode],
        queryFn: async () => {
            const response = await api.get(`/sap/customers/${cardCode}/projects/`);
            return response.data.projects;
        },
        enabled: !!cardCode,
        staleTime: 300000 // 5 min
    });
};

/**
 * Hook para obtener llamadas de servicio recientes
 * @param {string} customerCode - (Opcional) Filtrar por cliente
 */
export const useSAPRecentCalls = (customerCode = null) => {
    return useQuery({
        queryKey: ['sap-recent-calls', customerCode],
        queryFn: async () => {
            const params = customerCode ? { customer_code: customerCode } : {};
            const response = await api.get('/sap/service-calls/recent/', { params });
            return response.data.results;
        },
        staleTime: 60000 // 1 min
    });
};
