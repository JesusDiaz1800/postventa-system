from django.apps import AppConfig


class IntegrationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.integrations'
    verbose_name = 'Integraciones'
    
    def ready(self):
        """Initialize integrations when Django starts"""
        try:
            from . import signals
        except ImportError:
            pass
