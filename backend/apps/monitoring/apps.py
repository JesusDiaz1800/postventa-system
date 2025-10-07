from django.apps import AppConfig


class MonitoringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.monitoring'
    verbose_name = 'Sistema de Monitoreo'

    def ready(self):
        """Configurar el sistema de monitoreo al iniciar la aplicación"""
        import apps.monitoring.signals
        import apps.monitoring.tasks
