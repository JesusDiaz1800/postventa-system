from django.apps import AppConfig


class AuditConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.audit'
    verbose_name = 'Auditoría'
    
    def ready(self):
        """Configurar señales cuando la app está lista"""
        # import apps.audit.signals  # Commented out to avoid circular imports