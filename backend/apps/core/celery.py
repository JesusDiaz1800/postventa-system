import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')

app = Celery('postventa_system')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Configuración de rutas de cola
app.conf.task_routes = {
    'apps.notifications.tasks.*': {'queue': 'notifications'},
    'apps.documents.tasks.*': {'queue': 'documents'},
    'apps.incidents.tasks.*': {'queue': 'incidents'},
}

# Configuración de prioridades y límites
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Bogota',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hora
    task_soft_time_limit=3000,  # 50 minutos
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

# Configuración de retry
app.conf.task_annotations = {
    '*': {
        'retry_backoff': True,
        'retry_backoff_max': 600,  # 10 minutos máximo
        'max_retries': 3,
        'rate_limit': '10/m'
    }
}

# Horarios de tareas periódicas
app.conf.beat_schedule = {
    'cleanup-old-notifications': {
        'task': 'apps.notifications.tasks.cleanup_old_notifications',
        'schedule': 86400.0,  # 24 horas
        'options': {'queue': 'notifications'}
    },
    'check-approaching-deadlines': {
        'task': 'apps.notifications.tasks.check_approaching_deadlines',
        'schedule': 3600.0,  # 1 hora
        'options': {'queue': 'notifications'}
    },
    'send-daily-digest': {
        'task': 'apps.notifications.tasks.send_daily_digest',
        'schedule': 28800.0,  # 8 horas (8 AM)
        'options': {'queue': 'notifications'}
    },
    'update-notification-metrics': {
        'task': 'apps.notifications.tasks.update_notification_metrics',
        'schedule': 300.0,  # 5 minutos
        'options': {'queue': 'notifications'}
    },
}