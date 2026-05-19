"""
Configuraciones del sistema de notificaciones
"""

# Tipos de notificación disponibles
NOTIFICATION_TYPES = {
    # Incidencias
    'incident_created': {
        'title': 'Incidencia Creada',
        'category': 'incidents',
        'icon': 'new_releases',
        'color': '#4caf50',
        'important': True
    },
    'incident_updated': {
        'title': 'Incidencia Actualizada',
        'category': 'incidents',
        'icon': 'update',
        'color': '#2196f3'
    },
    'incident_escalated': {
        'title': 'Incidencia Escalada',
        'category': 'incidents',
        'icon': 'arrow_upward',
        'color': '#ff9800',
        'important': True
    },
    'incident_closed': {
        'title': 'Incidencia Cerrada',
        'category': 'incidents',
        'icon': 'check_circle',
        'color': '#4caf50'
    },
    
    # Documentos
    'document_uploaded': {
        'title': 'Documento Subido',
        'category': 'documents',
        'icon': 'upload_file',
        'color': '#2196f3'
    },
    'document_approved': {
        'title': 'Documento Aprobado',
        'category': 'documents',
        'icon': 'thumb_up',
        'color': '#4caf50'
    },
    'document_rejected': {
        'title': 'Documento Rechazado',
        'category': 'documents',
        'icon': 'thumb_down',
        'color': '#f44336',
        'important': True
    },
    
    # Workflow
    'workflow_step_completed': {
        'title': 'Paso de Workflow Completado',
        'category': 'workflow',
        'icon': 'done',
        'color': '#4caf50'
    },
    'workflow_approval_required': {
        'title': 'Aprobación de Workflow Requerida',
        'category': 'workflow',
        'icon': 'pending_actions',
        'color': '#ff9800',
        'important': True
    },
    
    # Sistema
    'system_alert': {
        'title': 'Alerta del Sistema',
        'category': 'system',
        'icon': 'warning',
        'color': '#f44336',
        'important': True
    },
    
    # Usuarios
    'user_assigned': {
        'title': 'Usuario Asignado',
        'category': 'users',
        'icon': 'person',
        'color': '#2196f3'
    },
    'user_registered': {
        'title': 'Usuario Registrado',
        'category': 'users',
        'icon': 'person_add',
        'color': '#4caf50'
    },
    
    # Fechas límite
    'deadline_approaching': {
        'title': 'Fecha Límite Próxima',
        'category': 'deadlines',
        'icon': 'schedule',
        'color': '#ff9800',
        'important': True
    },
    'deadline_exceeded': {
        'title': 'Fecha Límite Excedida',
        'category': 'deadlines',
        'icon': 'error',
        'color': '#f44336',
        'important': True
    },
    
    # Reportes
    'quality_report_submitted': {
        'title': 'Reporte de Calidad Enviado',
        'category': 'reports',
        'icon': 'assessment',
        'color': '#2196f3'
    },
    'quality_report_approved': {
        'title': 'Reporte de Calidad Aprobado',
        'category': 'reports',
        'icon': 'verified',
        'color': '#4caf50'
    },
    'quality_report_rejected': {
        'title': 'Reporte de Calidad Rechazado',
        'category': 'reports',
        'icon': 'cancel',
        'color': '#f44336',
        'important': True
    },
    'visit_report_submitted': {
        'title': 'Reporte de Visita Enviado',
        'category': 'reports',
        'icon': 'description',
        'color': '#2196f3'
    },
    'visit_report_approved': {
        'title': 'Reporte de Visita Aprobado',
        'category': 'reports',
        'icon': 'check_circle',
        'color': '#4caf50'
    },
    'visit_report_rejected': {
        'title': 'Reporte de Visita Rechazado',
        'category': 'reports',
        'icon': 'cancel',
        'color': '#f44336',
        'important': True
    }
}

# Configuración de categorías
NOTIFICATION_CATEGORIES = {
    'incidents': {
        'name': 'Incidencias',
        'description': 'Notificaciones relacionadas con incidencias',
        'icon': 'warning',
        'color': '#ff9800'
    },
    'documents': {
        'name': 'Documentos',
        'description': 'Notificaciones relacionadas con documentos',
        'icon': 'description',
        'color': '#2196f3'
    },
    'workflow': {
        'name': 'Workflow',
        'description': 'Notificaciones del flujo de trabajo',
        'icon': 'assignment',
        'color': '#4caf50'
    },
    'system': {
        'name': 'Sistema',
        'description': 'Alertas y notificaciones del sistema',
        'icon': 'settings',
        'color': '#f44336'
    },
    'users': {
        'name': 'Usuarios',
        'description': 'Notificaciones relacionadas con usuarios',
        'icon': 'people',
        'color': '#2196f3'
    },
    'deadlines': {
        'name': 'Fechas Límite',
        'description': 'Recordatorios de fechas límite',
        'icon': 'schedule',
        'color': '#ff9800'
    },
    'reports': {
        'name': 'Reportes',
        'description': 'Notificaciones de reportes',
        'icon': 'assessment',
        'color': '#2196f3'
    }
}

# Configuración de límites
NOTIFICATION_LIMITS = {
    'max_connections_per_user': 5,
    'max_notifications_per_page': 20,
    'max_important_notifications': 5,
    'notification_cleanup_days': 30,  # Días antes de archivar
    'rate_limit_window': 60,  # Segundos entre notificaciones similares
}

# Configuración de intervalos
NOTIFICATION_INTERVALS = {
    'cleanup_interval': 24 * 60 * 60,  # 24 horas
    'deadline_check_interval': 60 * 60,  # 1 hora
    'connection_timeout': 20,  # 20 segundos
    'ping_interval': 30,  # 30 segundos
}

# Configuración de retención
NOTIFICATION_RETENTION = {
    'max_age_days': 90,  # Máximo tiempo de retención
    'archive_after_days': 30,  # Días antes de archivar
    'delete_after_days': 90,  # Días antes de eliminar
}

# Configuración de correo electrónico
EMAIL_NOTIFICATIONS = {
    'enabled': True,
    'from_email': 'notificaciones@postventa.com',
    'include_categories': ['incidents', 'documents', 'system'],
    'daily_digest_time': '08:00',
    'weekly_digest_day': 'MON'
}

# Configuración de notificaciones push
PUSH_NOTIFICATIONS = {
    'enabled': True,
    'vapid_public_key': 'TU_CLAVE_PUBLICA_VAPID',
    'vapid_private_key': 'TU_CLAVE_PRIVADA_VAPID',
    'vapid_claims': {
        'sub': 'mailto:admin@postventa.com'
    }
}

# Configuración de WebSocket
WEBSOCKET_CONFIG = {
    'ping_interval': 30,
    'ping_timeout': 10,
    'close_timeout': 60,
    'max_message_size': 65536,
    'compression': True
}

# Configuración de caché
NOTIFICATION_CACHE = {
    'default_timeout': 300,  # 5 minutos
    'user_preferences_timeout': 3600,  # 1 hora
    'notification_count_timeout': 60,  # 1 minuto
}