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


@shared_task
def send_daily_technician_itinerary():
    """
    Envia un resumen diario a primera hora (6:00 AM) a cada tecnico
    con sus visitas programadas para el dia, organizadas por comuna en formato tabla,
    marcado como de ALTA IMPORTANCIA.
    """
    import pytz
    import logging
    from django.utils import timezone
    from datetime import datetime, time
    from django.contrib.auth import get_user_model
    from django.core.mail import EmailMessage
    from apps.visits.models import VisitReport
    import unicodedata
    
    logger = logging.getLogger(__name__)
    
    try:
        # 1. Obtener la fecha local en Chile (America/Santiago)
        tz = pytz.timezone('America/Santiago')
        now_local = timezone.localtime(timezone.now())
        today = now_local.date()
        
        # Rango de hoy en local convertido a UTC para consulta DB
        start_local = tz.localize(datetime.combine(today, time.min))
        end_local = tz.localize(datetime.combine(today, time.max))
        
        # Obtener todas las visitas programadas para hoy
        # Se consideran en borrador (draft) como programadas, pero para ser exhaustivos,
        # incluimos todas las que no estén cerradas/enviadas o aprobadas.
        visits_today = VisitReport.objects.filter(
            visit_date__range=(start_local, end_local)
        ).exclude(status__in=['approved', 'closed', 'sent'])
        
        if not visits_today.exists():
            logger.info(f"No programmed visits found for today ({today}). Skipping daily itinerary dispatch.")
            return "No se encontraron visitas programadas para hoy."
            
        # 2. Obtener tecnicos activos
        User = get_user_model()
        technicians = User.objects.filter(role='technical_service', is_active=True)
        
        if not technicians.exists():
            logger.warning("No active technicians found in the system. Skipping itinerary.")
            return "No hay técnicos activos en el sistema."
            
        # Helper para normalizar strings
        def clean_str(s):
            if not s: return ""
            return "".join(
                c for c in unicodedata.normalize('NFD', s.lower())
                if unicodedata.category(c) != 'Mn'
            ).strip()
            
        # 3. Asignar visitas a cada tecnico usando fuzzy match
        tech_visits = {tech.id: [] for tech in technicians}
        
        for visit in visits_today:
            clean_tech = clean_str(visit.technician)
            if not clean_tech:
                continue
            for tech in technicians:
                u_full = clean_str(f"{tech.first_name} {tech.last_name}")
                u_username = clean_str(tech.username)
                if clean_tech == u_full or clean_tech == u_username or (len(clean_tech) > 3 and (clean_tech in u_full or u_full in clean_tech)):
                    tech_visits[tech.id].append(visit)
                    break
                    
        # 4. Despachar email de alta importancia a cada tecnico con visitas
        emails_sent = 0
        for tech in technicians:
            visits = tech_visits[tech.id]
            if not visits:
                continue
                
            # Ordenar de manera inteligente por comuna y luego por proyecto
            visits = sorted(visits, key=lambda x: (x.commune or '', x.project_name or ''))
            
            # Construir cuerpo HTML en formato tabla premium Stitch 2.0 (glassmorphic / clean)
            subject = f"📅 [IMPORTANTE] Tu Itinerario de Visitas para Hoy - {today.strftime('%d/%m/%Y')}"
            
            # Filas de la tabla
            rows_html = ""
            plain_text_rows = ""
            domain = getattr(settings, 'FRONTEND_URL', 'https://sertec.polifusion.com')
            
            for idx, v in enumerate(visits):
                visit_url = f"{domain.rstrip('/')}/visit-reports/{v.id}/edit"
                # Alternancia de color de fila
                bg_color = "#f8fafc" if idx % 2 == 0 else "#ffffff"
                
                rows_html += f"""
                <tr style="background-color: {bg_color}; border-bottom: 1px solid #e2e8f0;">
                    <td style="padding: 10px 12px; font-size: 12px; font-weight: bold; color: #1e3a8a; text-transform: uppercase;">{v.commune or 'No Especificado'}</td>
                    <td style="padding: 10px 12px; font-size: 12px; font-weight: 800; color: #1e293b;">{v.project_name or 'No Especificado'}</td>
                    <td style="padding: 10px 12px; font-size: 11px; color: #475569;">{v.client_name or 'No Especificado'}</td>
                    <td style="padding: 10px 12px; font-size: 11px; color: #475569;">{v.address or 'No Especificada'}</td>
                    <td style="padding: 10px 12px; font-size: 11px; text-align: center;">
                        <a href="{visit_url}" target="_blank" style="background-color: #2563eb; color: #ffffff; padding: 4px 8px; border-radius: 6px; text-decoration: none; font-size: 10px; font-weight: bold; display: inline-block;">Ficha</a>
                    </td>
                </tr>
                """
                plain_text_rows += f"- [{v.commune or 'Comuna n/a'}] {v.project_name or 'Obra n/a'} | Cliente: {v.client_name or 'n/a'} | Dir: {v.address or 'n/a'} | Link: {visit_url}\n"
                
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>{subject}</title>
            </head>
            <body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f1f5f9; margin: 0; padding: 20px;">
                <div style="max-width: 650px; margin: 0 auto; background-color: #ffffff; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); overflow: hidden;">
                    <!-- Encabezado -->
                    <div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 25px 20px; color: #ffffff; text-align: center;">
                        <h1 style="font-size: 20px; font-weight: 900; margin: 0; letter-spacing: 0.5px; text-transform: uppercase;">Sertec Polifusión</h1>
                        <p style="font-size: 12px; font-weight: bold; margin: 5px 0 0 0; color: #93c5fd; letter-spacing: 2px; text-transform: uppercase;">Itinerario Diario de Visitas en Terreno</p>
                    </div>
                    
                    <!-- Cuerpo -->
                    <div style="padding: 25px 20px;">
                        <p style="font-size: 14px; color: #334155; line-height: 1.5; margin-top: 0;">
                            Estimado/a <strong>{tech.first_name}</strong>,
                        </p>
                        <p style="font-size: 13px; color: #475569; line-height: 1.5;">
                            A continuación, le presentamos el resumen de sus visitas programadas para hoy, <strong>{today.strftime('%d/%m/%Y')}</strong>, organizadas geográficamente por comuna para optimizar su traslado:
                        </p>
                        
                        <!-- Tabla de Itinerario -->
                        <div style="margin-top: 20px; border-radius: 12px; border: 1px solid #cbd5e1; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                            <table style="width: 100%; border-collapse: collapse; text-align: left; background-color: #ffffff;">
                                <thead>
                                    <tr style="background-color: #f1f5f9; border-bottom: 2px solid #cbd5e1;">
                                        <th style="padding: 10px 12px; font-size: 10px; font-weight: 800; color: #475569; text-transform: uppercase; tracking-wider;">Comuna</th>
                                        <th style="padding: 10px 12px; font-size: 10px; font-weight: 800; color: #475569; text-transform: uppercase; tracking-wider;">Obra/Proyecto</th>
                                        <th style="padding: 10px 12px; font-size: 10px; font-weight: 800; color: #475569; text-transform: uppercase; tracking-wider;">Cliente</th>
                                        <th style="padding: 10px 12px; font-size: 10px; font-weight: 800; color: #475569; text-transform: uppercase; tracking-wider;">Dirección</th>
                                        <th style="padding: 10px 12px; font-size: 10px; font-weight: 800; color: #475569; text-transform: uppercase; tracking-wider; text-align: center;">Acción</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {rows_html}
                                </tbody>
                            </table>
                        </div>
                        
                        <p style="font-size: 12.5px; color: #64748b; margin-top: 25px; line-height: 1.5; font-style: italic;">
                            Por favor, revise la ficha de cada visita para ver planos de trazabilidad, datos de contacto del instalador y cargar evidencias de terreno y firmas digitales.
                        </p>
                    </div>
                    
                    <!-- Pie de página -->
                    <div style="background-color: #f8fafc; border-top: 1px solid #e2e8f0; padding: 15px 20px; text-align: center;">
                        <p style="font-size: 11px; color: #94a3b8; margin: 0;">
                            Este es un reporte de alerta automático con prioridad alta emitido por Sertec Polifusión System.
                        </p>
                        <p style="font-size: 10px; color: #cbd5e1; margin: 5px 0 0 0;">
                            &copy; {timezone.now().year} Polifusión S.A. Todos los derechos reservados.
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            plain_text_body = f"""
Estimado/a {tech.first_name},

A continuación le presentamos el itinerario de sus visitas programadas para hoy ({today.strftime('%d/%m/%Y')}), ordenadas por comuna:

{plain_text_rows}

Por favor, revise el portal móvil para ver planos, cargar fotos de evidencia y registrar firmas en terreno.

Atentamente,
Departamento de Postventa y Servicio Técnico
Polifusión S.A.
            """
            
            # Enviar email marcado como de Alta Importancia (Redirigido temporalmente a jdiaz@polifusion.cl en pre-producción)
            email = EmailMessage(
                subject=subject,
                body=plain_text_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=['jdiaz@polifusion.cl']
            )
            email.content_subtype = "html"
            email.body = html_content
            
            # Encabezados SMTP estándar de Alta Importancia
            email.extra_headers = {
                'X-Priority': '1',
                'X-MSMail-Priority': 'High',
                'Importance': 'high'
            }
            
            email.send(fail_silently=False)
            emails_sent += 1
            logger.info(f"Daily itinerary email successfully dispatched (Redirected to 'jdiaz@polifusion.cl' from '{tech.email}') for today's visits.")
            
        return f"Resumen diario de itinerarios completado. Emails enviados: {emails_sent}"
        
    except Exception as e:
        logger.error(f"Error sending daily technician itineraries: {str(e)}")
        return f"Error: {str(e)}"


from celery.signals import on_after_finalize

# Configurar tareas periódicas
@on_after_finalize.connect
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

    # Resumen de visitas para técnicos (Lunes a Viernes a las 6:00 AM)
    from django_celery_beat.models import CrontabSchedule
    
    schedule_6am, _ = CrontabSchedule.objects.get_or_create(
        minute='0',
        hour='6',
        day_of_week='1-5',  # Lunes a Viernes
        day_of_month='*',
        month_of_year='*'
    )
    
    PeriodicTask.objects.get_or_create(
        name='send_daily_technician_itinerary',
        task='apps.notifications.tasks.send_daily_technician_itinerary',
        crontab=schedule_6am,
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