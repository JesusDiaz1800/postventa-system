/**
 * Configuración de rutas de la aplicación
 * Centraliza todas las rutas del sistema
 */

export const ROUTES = {
  // Rutas principales
  HOME: '/',
  LOGIN: '/login',
  DASHBOARD: '/dashboard',
  
  // Gestión de incidencias
  INCIDENTS: '/incidents',
  CREATE_INCIDENT: '/incidents/create',
  INCIDENT_DETAIL: '/incidents/:id',
  
  // Centro de documentos
  DOCUMENTS: '/documents',
  DOCUMENT_VIEWER: '/documents/:id/view',
  
  // Reportes
  VISIT_REPORTS: '/reports/visit',
  SUPPLIER_REPORTS: '/reports/supplier',
  LAB_REPORTS: '/reports/lab',
  QUALITY_REPORTS: '/reports/quality',
  INTERNAL_QUALITY_REPORTS: '/reports/quality/internal',
  CLIENT_QUALITY_REPORTS: '/reports/quality/client',
  
  // Gestión de usuarios
  USERS: '/users',
  USER_PROFILE: '/users/profile',
  
  // Configuración
  SETTINGS: '/settings',
  PROFILE: '/profile',
};

/**
 * Genera URL con parámetros
 * @param {string} route - Ruta base
 * @param {object} params - Parámetros para reemplazar
 * @returns {string} URL generada
 */
export const generateUrl = (route, params = {}) => {
  let url = route;
  Object.keys(params).forEach(key => {
    url = url.replace(`:${key}`, params[key]);
  });
  return url;
};

/**
 * Navegación principal del sistema
 */
export const NAVIGATION = [
  {
    name: 'Dashboard',
    href: ROUTES.DASHBOARD,
    icon: 'HomeIcon',
    current: false,
  },
  {
    name: 'Incidencias',
    href: ROUTES.INCIDENTS,
    icon: 'ExclamationTriangleIcon',
    current: false,
  },
  {
    name: 'Documentos',
    href: ROUTES.DOCUMENTS,
    icon: 'DocumentTextIcon',
    current: false,
  },
  {
    name: 'Reportes',
    icon: 'ChartBarIcon',
    current: false,
    children: [
      {
        name: 'Reportes de Visita',
        href: ROUTES.VISIT_REPORTS,
        icon: 'DocumentTextIcon',
      },
      {
        name: 'Reportes de Proveedor',
        href: ROUTES.SUPPLIER_REPORTS,
        icon: 'BuildingOfficeIcon',
      },
      {
        name: 'Reportes de Laboratorio',
        href: ROUTES.LAB_REPORTS,
        icon: 'BeakerIcon',
      },
      {
        name: 'Reportes de Calidad',
        href: ROUTES.QUALITY_REPORTS,
        icon: 'CheckCircleIcon',
        children: [
          {
            name: 'Calidad Interna',
            href: ROUTES.INTERNAL_QUALITY_REPORTS,
          },
          {
            name: 'Calidad Cliente',
            href: ROUTES.CLIENT_QUALITY_REPORTS,
          },
        ],
      },
    ],
  },
  {
    name: 'Usuarios',
    href: ROUTES.USERS,
    icon: 'UsersIcon',
    current: false,
  },
  {
    name: 'Configuración',
    href: ROUTES.SETTINGS,
    icon: 'CogIcon',
    current: false,
  },
];

export default ROUTES;
