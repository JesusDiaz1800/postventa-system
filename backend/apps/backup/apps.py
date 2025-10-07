from django.apps import AppConfig


class BackupConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.backup'
    verbose_name = 'Backup y Recuperación'
    
    def ready(self):
        """Initialize backup system when Django starts"""
        try:
            from . import signals
        except ImportError:
            pass
