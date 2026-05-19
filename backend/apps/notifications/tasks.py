from celery import shared_task
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from django.conf import settings

from .models import Notification, NotificationCategory, NotificationPreferences
from .logging import notification_logger
from .config import (
    NOTIFICATION_RETENTION,
    NOTIFICATION_INTERVALS,
    EMAIL_NOTIFICATIONS
)


@shared_task
def cleanup_old_notifications():
    """
    Tarea para limpiar notificaciones antiguas.
    - Archiva notificaciones más antiguas que archive_after_days
    - Elimina notificaciones más antiguas que delete_after_days
    """
    try:
        now = timezone.now()
        archive_date = now - timedelta(days=NOTIFICATION_RETENTION['archive_after_days'])
        delete_date = now - timedelta(days=NOTIFICATION_RETENTION['delete_after_days'])
        
        # Archivar notificaciones antiguas
        to_archive = Notification.objects.filter(
            created_at__lte=archive_date,
            is_archived=False
        )
        
        archived_count = to_archive.update(is_archived=True)
        
        # Eliminar notificaciones muy antiguas
        to_delete = Notification.objects.filter(
            created_at__lte=delete_date
        )
        
        deleted_count = to_delete.delete()[0]
        
        notification_logger.info(
            'Limpieza de notificaciones completada',
            data={
                'archived_count': archived_count,
                'deleted_count': deleted_count,
                'archive_date': archive_date.isoformat(),
                'delete_date': delete_date.isoformat()
            }
        )
        
        return {
            'archived_count': archived_count,
            'deleted_count': deleted_count
        }
        
    except Exception as e:
        notification_logger.error(
            'Error en limpieza de notificaciones',
            data={'error': str(e)}
        )
        raise


@shared_task
def check_approaching_deadlines():
    """
    Tarea para verificar fechas límite próximas y enviar notificaciones.
    """
    try:
        from apps.incidents.models import Incident
        now = timezone.now()
        tomorrow = now.date() + timedelta(days=1)
        
        # Buscar incidencias con fecha límite próxima
        approaching_incidents = Incident.objects.filter(
            due_date=tomorrow,
            status__in=['open', 'in_progress']
        )
        
        for incident in approaching_incidents:
            from .utils import send_notification
            
            users_to_notify = {
                incident.assigned_to,
                incident.created_by,
                incident.last_modified_by
            }
            users_to_notify.discard(None)
            
            for user in users_to_notify:
                send_notification(
                    user=user,
                    title=f'Fecha límite próxima - Incidencia #{incident.id}',
                    message=f'La incidencia vence mañana',
                    notification_type='deadline_approaching',
                    is_important=True,
                    related_incident=incident,
                    metadata={
                        'incident_id': incident.id,
                        'title': incident.title,
                        'due_date': incident.due_date.isoformat()
                    }
                )
        
        notification_logger.info(
            'Verificación de fechas límite completada',
            data={'incidents_checked': approaching_incidents.count()}
        )
        
        return {'checked_count': approaching_incidents.count()}
        
    except Exception as e:
        notification_logger.error(
            'Error al verificar fechas límite',
            data={'error': str(e)}
        )
        raise


@shared_task
def send_daily_digest():
    """
    Tarea para enviar resumen diario de notificaciones por email.
    """
    if not EMAIL_NOTIFICATIONS['enabled']:
        return
        
    try:
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        
        yesterday = timezone.now() - timedelta(days=1)
        
        # Obtener usuarios con preferencias de resumen diario
        users_with_daily = NotificationPreferences.objects.filter(
            notification_frequency='daily',
            email_notifications=True
        ).select_related('user')
        
        for preferences in users_with_daily:
            user = preferences.user
            
            # Obtener notificaciones del día
            notifications = Notification.objects.filter(
                user=user,
                created_at__gte=yesterday,
                category__in=preferences.categories.all()
            ).order_by('-created_at')
            
            if notifications.exists():
                # Renderizar template
                context = {
                    'user': user,
                    'notifications': notifications,
                    'date': yesterday.date()
                }
                
                html_content = render_to_string(
                    'notifications/email/daily_digest.html',
                    context
                )
                
                # Enviar email
                send_mail(
                    subject=f'Resumen diario de notificaciones - {yesterday.date()}',
                    message='',
                    from_email=EMAIL_NOTIFICATIONS['from_email'],
                    recipient_list=[user.email],
                    html_message=html_content
                )
        
        notification_logger.info(
            'Envío de resumen diario completado',
            data={'users_processed': users_with_daily.count()}
        )
        
        return {'processed_count': users_with_daily.count()}
        
    except Exception as e:
        notification_logger.error(
            'Error al enviar resumen diario',
            data={'error': str(e)}
        )
        raise


@shared_task
def update_notification_metrics():
    """
    Tarea para actualizar métricas del sistema de notificaciones.
    """
    try:
        from django.core.cache import cache
        now = timezone.now()
        
        # Métricas generales
        total_notifications = Notification.objects.count()
        unread_notifications = Notification.objects.filter(is_read=False).count()
        important_notifications = Notification.objects.filter(is_important=True).count()
        
        # Métricas por categoría
        category_metrics = {}
        for category in NotificationCategory.objects.all():
            category_metrics[category.name] = {
                'total': Notification.objects.filter(category=category).count(),
                'unread': Notification.objects.filter(
                    category=category,
                    is_read=False
                ).count()
            }
        
        # Métricas de tiempo
        last_24h = now - timedelta(hours=24)
        notifications_24h = Notification.objects.filter(
            created_at__gte=last_24h
        ).count()
        
        last_7d = now - timedelta(days=7)
        notifications_7d = Notification.objects.filter(
            created_at__gte=last_7d
        ).count()
        
        # Guardar métricas en caché
        metrics = {
            'total_notifications': total_notifications,
            'unread_notifications': unread_notifications,
            'important_notifications': important_notifications,
            'notifications_24h': notifications_24h,
            'notifications_7d': notifications_7d,
            'by_category': category_metrics,
            'last_updated': now.isoformat()
        }
        
        cache.set('notification_metrics', metrics, timeout=3600)  # 1 hora
        
        notification_logger.info(
            'Actualización de métricas completada',
            data=metrics
        )
        
        return metrics
        
    except Exception as e:
        notification_logger.error(
            'Error al actualizar métricas',
            data={'error': str(e)}
        )
        raise


# Configurar tareas periódicas
def setup_periodic_tasks(sender, **kwargs):
    from django_celery_beat.models import PeriodicTask, IntervalSchedule
    
    # Limpieza de notificaciones (diaria)
    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=NOTIFICATION_INTERVALS['cleanup_interval'],
        period=IntervalSchedule.SECONDS
    )
    
    PeriodicTask.objects.get_or_create(
        name='cleanup_old_notifications',
        task='apps.notifications.tasks.cleanup_old_notifications',
        interval=schedule,
        queue='notifications'
    )
    
    # Verificación de fechas límite (horaria)
    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=NOTIFICATION_INTERVALS['deadline_check_interval'],
        period=IntervalSchedule.SECONDS
    )
    
    PeriodicTask.objects.get_or_create(
        name='check_approaching_deadlines',
        task='apps.notifications.tasks.check_approaching_deadlines',
        interval=schedule,
        queue='notifications'
    )
    
    # Resumen diario (8:00 AM)
    if EMAIL_NOTIFICATIONS['enabled']:
        from django_celery_beat.models import CrontabSchedule
        
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='0',
            hour='8',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*'
        )
        
        PeriodicTask.objects.get_or_create(
            name='send_daily_digest',
            task='apps.notifications.tasks.send_daily_digest',
            crontab=schedule,
            queue='notifications'
        )
    
    # Actualización de métricas (cada 5 minutos)
    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=300,  # 5 minutos
        period=IntervalSchedule.SECONDS
    )
    
    PeriodicTask.objects.get_or_create(
        name='update_notification_metrics',
        task='apps.notifications.tasks.update_notification_metrics',
        interval=schedule,
        queue='notifications'
    )