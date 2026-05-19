import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';

export const useSAPCustomerSearch = (query) => {
    const countryCode = localStorage.getItem('country_code') || 'CL';
    return useQuery({
        queryKey: ['sap-customers', query, countryCode],
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
 * Hook para obtener una llamada de servicio de SAP por DocNum
 * @param {string|number} docNum - DocNum de la llamada de servicio
 */
export const useSAPServiceCall = (docNum) => {
    return useQuery({
        queryKey: ['sap-service-call', docNum],
        queryFn: async () => {
            const response = await api.get(`/sap/service-calls/${docNum}/`);
            return response.data;
        },
        enabled: !!docNum && String(docNum).length > 0,
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

/**
 * Hook para obtener vendedores activos de SAP
 */
export const useSAPSalesEmployees = () => {
    const countryCode = localStorage.getItem('country_code') || 'CL';
    return useQuery({
        queryKey: ['sap-sales-employees', countryCode],
        queryFn: async () => {
            const response = await api.get('/sap/sales-employees/');
            return response.data;
        },
        staleTime: 3600000 // 1 hora
    });
};

/**
 * Hook para obtener detalles completos del cliente SAP
 * Incluye: vendedor, direcciones, proyectos/obras
 * @param {string} cardCode - Código del cliente (CardCode)
 */
export const useSAPCustomerDetails = (cardCode) => {
    return useQuery({
        queryKey: ['sap-customer-details', cardCode],
        queryFn: async () => {
            if (!cardCode) return null;
            const response = await api.get(`/sap/customer-details/${cardCode}/`);
            return response.data;
        },
        enabled: !!cardCode,
        staleTime: 3600000 // 1 hora
    });
};

/**
 * Hook para obtener técnicos de SAP (EmpID)
 * @param {string} role - (Opcional) Filtrar por rol (ej. 'technician')
 */
export const useSAPTechnicians = (role = null) => {
    const countryCode = localStorage.getItem('country_code') || 'CL';
    return useQuery({
        queryKey: ['sap-technicians', countryCode, role],
        queryFn: async () => {
            const url = role ? `/sap/technicians/?role=${role}` : '/sap/technicians/';
            const response = await api.get(url);
            return response.data;
        },
        staleTime: 3600000 // 1 hora
    });
};
