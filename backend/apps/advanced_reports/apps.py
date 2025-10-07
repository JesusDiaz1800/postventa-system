from django.apps import AppConfig


class AdvancedReportsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.advanced_reports'
    verbose_name = 'Reportes Avanzados'
    
    def ready(self):
        """Initialize advanced reports when Django starts"""
        try:
            from . import signals
        except ImportError:
            pass
