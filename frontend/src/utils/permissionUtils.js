export const PERMISSION_LABELS = {
    'can_manage_users': 'Gestionar Usuarios',
    'can_manage_incidents': 'Gestionar Incidencias',
    'can_view_reports': 'Ver Reportes',
    'can_manage_workflows': 'Gestionar Flujos de Trabajo',
    'can_manage_documents': 'Gestionar Documentos',
    'can_access_admin': 'Acceso Total Admin',
    'can_export_data': 'Exportar Datos',
    'can_view_audit_logs': 'Ver Logs de Auditoría',
    'can_manage_system_settings': 'Configuración del Sistema',
    'can_view_supplier_reports': 'Ver Reportes de Proveedores',
    'can_reopen_incidents': 'Reabrir Incidencias Cerradas'
};

export const PAGE_LABELS = {
    'reports': 'Panel de Control',
    'incidents': 'Incidencias',
    'documents': 'Documentos',
    'visit-reports': 'Reportes de Visita',
    'quality-reports/client': 'Calidad (Cliente)',
    'quality-reports/internal': 'Calidad Interna',
    'supplier-reports': 'Reportes Proveedor',
    'users': 'Usuarios',
    'ai': 'Chat IA',
    'audit': 'Auditoría'
};

/**
 * Calcula el estado efectivo de un permiso sumando el rol + override del usuario
 */
export const getEffectivePermission = (rolePerms, userOverrides, key) => {
    // Si hay un override explícito (true/false), manda el usuario
    if (userOverrides && userOverrides[key] !== undefined) {
        return userOverrides[key];
    }
    // Si no, lo que diga el rol
    return rolePerms?.[key] || false;
};

/**
 * Determina si el permiso actual es un override o heredado
 */
export const isPermissionOverridden = (userOverrides, key) => {
    return userOverrides && userOverrides[key] !== undefined;
};
