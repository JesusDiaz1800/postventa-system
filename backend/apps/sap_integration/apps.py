from django.apps import AppConfig

class SapIntegrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.sap_integration'

    def ready(self):
        import apps.sap_integration.signals
