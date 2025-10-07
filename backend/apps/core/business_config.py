"""
This file isolates business logic and application-specific configurations
from the core Django settings. Keeping this separate improves organization
and clarity. In a more advanced system, some of this configuration might
be moved into the database and managed via an admin interface.
"""

# ==================== USER ROLES CONFIGURATION ====================
USER_ROLES = {
    'admin': {
        'permissions': ['view_all', 'edit_all', 'delete_all', 'manage_users'],
        'description': 'Administrador del sistema'
    },
    'supervisor': {
        'permissions': ['view_all', 'edit_assigned', 'manage_team'],
        'description': 'Supervisor de área'
    },
    'tecnico': {
        'permissions': ['view_assigned', 'upload_documents', 'edit_own'],
        'description': 'Técnico de campo'
    },
    'cliente': {
        'permissions': ['view_own', 'upload_own'],
        'description': 'Cliente externo'
    }
}

# ==================== BACKUP CONFIGURATION ====================
BACKUP_CONFIG = {
    'enabled': True,
    'schedule': 'daily',  # daily, weekly, monthly
    'retention_days': 30,
    'backup_path': r'\\backup-servidor\postventa',  # Should be controlled by env var
    'include_database': True,
    'include_media': True,
    'include_documents': True,
}

# ==================== MONITORING CONFIGURATION ====================
MONITORING_CONFIG = {
    'enabled': True,
    'check_interval': 300,  # 5 minutes
    'alert_email': 'admin@empresa.com', # Should be controlled by env var
    'disk_threshold': 90,  # Percentage
    'memory_threshold': 85,  # Percentage
}

# ==================== NOTIFICATION CONFIGURATION ====================
NOTIFICATION_CONFIG = {
    'email_notifications': True,
    'sms_notifications': False,  # Requires a specific service
    'push_notifications': False, # For future implementation
    'notification_recipients': {
        'new_incident': ['admin@empresa.com', 'supervisor@empresa.com'],
        'incident_escalated': ['admin@empresa.com'],
        'incident_closed': ['cliente@empresa.com'],
    }
}

# ==================== REPORTING CONFIGURATION ====================
REPORTING_CONFIG = {
    'default_format': 'pdf',
    'email_reports': True,
    'schedule_reports': True,
    'report_recipients': {
        'daily': ['admin@empresa.com'],
        'weekly': ['admin@empresa.com', 'supervisor@empresa.com'],
        'monthly': ['admin@empresa.com', 'gerencia@empresa.com'],
    }
}

# ==================== INTEGRATION CONFIGURATION ====================
INTEGRATION_CONFIG = {
    'erp_integration': False,
    'crm_integration': False,
    'accounting_integration': False,
    'api_endpoints': {
        'external_api_url': 'https://api.empresa.com',
        'api_key': 'your_api_key_here', # Should be controlled by env var
        'timeout': 30,
    }
}

# ==================== AI PROVIDERS CONFIGURATION ====================
# This provides a structured way to manage AI providers, which can be imported
# by the AI orchestrator app.
AI_PROVIDERS = {
    'openai': {
        'enabled_env': 'OPENAI_API_KEY',
        'daily_quota_tokens': 100000,
        'daily_quota_calls': 1000,
        'priority': 1,
    },
    'anthropic': {
        'enabled_env': 'ANTHROPIC_API_KEY',
        'daily_quota_tokens': 100000,
        'daily_quota_calls': 1000,
        'priority': 2,
    },
    'google': {
        'enabled_env': 'GEMINI_API_KEY', # Assuming google means gemini
        'daily_quota_tokens': 100000,
        'daily_quota_calls': 1000,
        'priority': 3,
    },
}
