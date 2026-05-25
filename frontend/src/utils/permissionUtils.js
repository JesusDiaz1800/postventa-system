/**
 * SERTEC - Utilidades de Permisos
 * Todos los permisos y páginas corresponden a la funcionalidad real del sistema.
 */

// Permisos de Acción — con descripción y categoría
export const PERMISSION_LABELS = {
    'can_manage_users':          'Gestionar Usuarios',
    'can_manage_visits':         'Crear y Editar Reportes de Visita',
    'can_view_reports':          'Ver Reportes de Visita',
    'can_delete_visits':         'Eliminar Reportes de Visita',
    'can_sign_reports':          'Firmar Reportes (Firma Digital)',
    'can_send_reports':          'Enviar Reportes por Correo',
    'can_export_pdf':            'Generar y Exportar PDF',
    'can_schedule_visits':       'Programar Visitas en Calendario',
    'can_view_all_technicians':  'Ver Reportes de Todos los Técnicos',
    'can_access_admin':          'Acceso Total de Administrador',
    'can_view_audit_logs':       'Ver Auditoría del Sistema',
    'can_manage_system_settings':'Configuración del Sistema',
};

// Páginas accesibles en SERTEC
export const PAGE_LABELS = {
    'dashboard':        'Dashboard',
    'visit-reports':    'Reportes de Visita',
    'schedule-visit':   'Programar Visita',
    'users':            'Gestión de Usuarios',
    'audit':            'Auditoría del Sistema',
};

// Descripciones detalladas por permiso (para tooltips/UI)
export const PERMISSION_DESCRIPTIONS = {
    'can_manage_users':          'Crear, editar y eliminar usuarios del sistema',
    'can_manage_visits':         'Crear nuevos reportes y editar reportes existentes',
    'can_view_reports':          'Ver el listado e historial de reportes de visita',
    'can_delete_visits':         'Eliminar reportes de visita permanentemente',
    'can_sign_reports':          'Agregar firma digital del cliente en los reportes',
    'can_send_reports':          'Enviar reportes finalizados por correo al vendedor SAP',
    'can_export_pdf':            'Generar vista previa y exportar reportes en formato PDF',
    'can_schedule_visits':       'Agendar y programar visitas en el calendario',
    'can_view_all_technicians':  'Ver reportes de todos los técnicos, no solo los propios',
    'can_access_admin':          'Acceso completo a todas las funcionalidades administrativas',
    'can_view_audit_logs':       'Ver el registro de auditoría y acciones del sistema',
    'can_manage_system_settings':'Modificar configuraciones globales del sistema',
};

// Categorías para agrupar permisos en la UI
export const PERMISSION_CATEGORIES = {
    'Reportes de Visita': [
        'can_view_reports',
        'can_manage_visits',
        'can_delete_visits',
        'can_view_all_technicians',
    ],
    'Acciones en Reportes': [
        'can_sign_reports',
        'can_send_reports',
        'can_export_pdf',
    ],
    'Programación': [
        'can_schedule_visits',
    ],
    'Administración': [
        'can_manage_users',
        'can_view_audit_logs',
        'can_access_admin',
        'can_manage_system_settings',
    ],
};

/**
 * Calcula el estado efectivo de un permiso sumando el rol + override del usuario
 */
export const getEffectivePermission = (rolePerms, userOverrides, key) => {
    if (userOverrides && userOverrides[key] !== undefined) {
        return userOverrides[key];
    }
    return rolePerms?.[key] || false;
};

/**
 * Determina si el permiso actual es un override o heredado del rol
 */
export const isPermissionOverridden = (userOverrides, key) => {
    return userOverrides && userOverrides[key] !== undefined;
};
