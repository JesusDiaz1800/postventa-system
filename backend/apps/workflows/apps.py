from django.apps import AppConfig


class WorkflowsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.workflows'
    verbose_name = 'Workflows'
    
    def ready(self):
        """Configurar señales cuando la app está lista"""
        # import apps.workflows.signals  # Commented out to avoid circular imports