from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
import logging

from .models import (
    MonitoringRule, Alert, MetricValue, HealthCheck, HealthCheckResult,
    SystemMetrics, NotificationChannel, AlertTemplate
)

logger = logging.getLogger(__name__)


@receiver(post_save, sender=MonitoringRule)
def monitoring_rule_post_save(sender, instance, created, **kwargs):
    """Señal post-save para MonitoringRule"""
    if created:
        logger.info(f"Nueva regla de monitoreo creada: {instance.name}")
        
        # Programar ejecución automática si está activa
        if instance.is_active:
            _schedule_rule_execution(instance)
    
    # Si se activó la regla, programar ejecución
    if not created and instance.is_active:
        logger.info(f"Regla de monitoreo activada: {instance.name}")
        _schedule_rule_execution(instance)


@receiver(post_save, sender=Alert)
def alert_post_save(sender, instance, created, **kwargs):
    """Señal post-save para Alert"""
    if created:
        logger.info(f"Nueva alerta creada: {instance.title} - {instance.severity}")
        
        # Enviar notificaciones inmediatas para alertas críticas
        if instance.severity == 'critical':
            _send_immediate_notifications(instance)
    
    # Si se resolvió la alerta, limpiar alertas relacionadas
    if not created and instance.status == 'resolved':
        logger.info(f"Alerta resuelta: {instance.title}")
        _cleanup_related_alerts(instance)


@receiver(post_save, sender=HealthCheck)
def health_check_post_save(sender, instance, created, **kwargs):
    """Señal post-save para HealthCheck"""
    if created:
        logger.info(f"Nueva verificación de salud creada: {instance.name}")
        
        # Programar ejecución automática si está activa
        if instance.is_active:
            _schedule_health_check_execution(instance)
    
    # Si se activó la verificación, programar ejecución
    if not created and instance.is_active:
        logger.info(f"Verificación de salud activada: {instance.name}")
        _schedule_health_check_execution(instance)


@receiver(post_save, sender=HealthCheckResult)
def health_check_result_post_save(sender, instance, created, **kwargs):
    """Señal post-save para HealthCheckResult"""
    if created:
        logger.info(f"Nuevo resultado de verificación de salud: {instance.health_check.name} - {instance.status}")
        
        # Crear alerta si la verificación falló
        if instance.status == 'unhealthy':
            _create_health_check_alert(instance)


@receiver(post_save, sender=SystemMetrics)
def system_metrics_post_save(sender, instance, created, **kwargs):
    """Señal post-save para SystemMetrics"""
    if created:
        # Evaluar reglas de monitoreo que usan métricas del sistema
        _evaluate_system_metric_rules(instance)


@receiver(post_save, sender=NotificationChannel)
def notification_channel_post_save(sender, instance, created, **kwargs):
    """Señal post-save para NotificationChannel"""
    if created:
        logger.info(f"Nuevo canal de notificación creada: {instance.name}")
    
    # Si se desactivó el canal, actualizar reglas que lo usan
    if not created and not instance.is_active:
        _update_rules_using_channel(instance)


@receiver(post_save, sender=AlertTemplate)
def alert_template_post_save(sender, instance, created, **kwargs):
    """Señal post-save para AlertTemplate"""
    if created:
        logger.info(f"Nueva plantilla de alerta creada: {instance.name}")
    
    # Si se marcó como plantilla por defecto, desmarcar otras
    if not created and instance.is_default:
        _set_default_alert_template(instance)


@receiver(post_delete, sender=MonitoringRule)
def monitoring_rule_post_delete(sender, instance, **kwargs):
    """Señal post-delete para MonitoringRule"""
    logger.info(f"Regla de monitoreo eliminada: {instance.name}")
    
    # Cancelar tareas programadas
    _cancel_scheduled_rule_execution(instance)


@receiver(post_delete, sender=Alert)
def alert_post_delete(sender, instance, **kwargs):
    """Señal post-delete para Alert"""
    logger.info(f"Alerta eliminada: {instance.title}")


@receiver(post_delete, sender=HealthCheck)
def health_check_post_delete(sender, instance, **kwargs):
    """Señal post-delete para HealthCheck"""
    logger.info(f"Verificación de salud eliminada: {instance.name}")
    
    # Cancelar tareas programadas
    _cancel_scheduled_health_check_execution(instance)


@receiver(post_delete, sender=NotificationChannel)
def notification_channel_post_delete(sender, instance, **kwargs):
    """Señal post-delete para NotificationChannel"""
    logger.info(f"Canal de notificación eliminado: {instance.name}")
    
    # Actualizar reglas que usan este canal
    _update_rules_using_channel(instance, deleted=True)


def _schedule_rule_execution(rule):
    """Programar ejecución de regla de monitoreo"""
    try:
        from celery import shared_task
        
        # Programar ejecución periódica
        execute_monitoring_rule.apply_async(
            args=[rule.id],
            countdown=rule.check_interval
        )
        
        logger.info(f"Ejecución programada para regla: {rule.name}")
        
    except Exception as e:
        logger.error(f"Error programando ejecución de regla {rule.name}: {str(e)}")


def _schedule_health_check_execution(health_check):
    """Programar ejecución de verificación de salud"""
    try:
        from celery import shared_task
        
        # Programar ejecución periódica
        execute_health_check.apply_async(
            args=[health_check.id],
            countdown=health_check.check_interval
        )
        
        logger.info(f"Ejecución programada para verificación de salud: {health_check.name}")
        
    except Exception as e:
        logger.error(f"Error programando ejecución de verificación {health_check.name}: {str(e)}")


def _send_immediate_notifications(alert):
    """Enviar notificaciones inmediatas para alertas críticas"""
    try:
        from .services import MonitoringService
        
        service = MonitoringService()
        service._send_notifications(alert.rule, alert)
        
        logger.info(f"Notificaciones inmediatas enviadas para alerta crítica: {alert.title}")
        
    except Exception as e:
        logger.error(f"Error enviando notificaciones inmediatas: {str(e)}")


def _cleanup_related_alerts(alert):
    """Limpiar alertas relacionadas cuando se resuelve una alerta"""
    try:
        # Buscar alertas relacionadas que puedan estar resueltas
        related_alerts = Alert.objects.filter(
            rule=alert.rule,
            status='active',
            triggered_at__lt=alert.triggered_at
        )
        
        for related_alert in related_alerts:
            related_alert.status = 'resolved'
            related_alert.resolved_at = timezone.now()
            related_alert.resolved_by = alert.resolved_by
            related_alert.save()
            
            logger.info(f"Alerta relacionada resuelta: {related_alert.title}")
        
    except Exception as e:
        logger.error(f"Error limpiando alertas relacionadas: {str(e)}")


def _create_health_check_alert(health_check_result):
    """Crear alerta para verificación de salud fallida"""
    try:
        # Buscar regla de monitoreo para verificaciones de salud
        rule = MonitoringRule.objects.filter(
            metric_type='custom',
            metric_name='health_check_failure'
        ).first()
        
        if not rule:
            # Crear regla por defecto si no existe
            from django.contrib.auth.models import User
            admin_user = User.objects.filter(is_superuser=True).first()
            
            if admin_user:
                rule = MonitoringRule.objects.create(
                    name='Verificación de Salud Fallida',
                    description='Alerta automática para verificaciones de salud fallidas',
                    metric_type='custom',
                    metric_name='health_check_failure',
                    comparison_operator='eq',
                    threshold_value=1,
                    severity='high',
                    is_active=True,
                    check_interval=300,
                    created_by=admin_user
                )
        
        if rule:
            # Crear alerta
            alert = Alert.objects.create(
                rule=rule,
                severity='high',
                title=f'Verificación de Salud Fallida: {health_check_result.health_check.name}',
                message=f'La verificación de salud "{health_check_result.health_check.name}" ha fallado: {health_check_result.message}',
                metric_value=1,
                threshold_value=1,
                metadata={
                    'health_check_id': health_check_result.health_check.id,
                    'health_check_name': health_check_result.health_check.name,
                    'response_time': health_check_result.response_time,
                    'error_message': health_check_result.message
                }
            )
            
            logger.info(f"Alerta creada para verificación de salud fallida: {alert.title}")
        
    except Exception as e:
        logger.error(f"Error creando alerta para verificación de salud fallida: {str(e)}")


def _evaluate_system_metric_rules(system_metric):
    """Evaluar reglas de monitoreo que usan métricas del sistema"""
    try:
        from .services import MonitoringService
        
        # Buscar reglas que usan esta métrica del sistema
        rules = MonitoringRule.objects.filter(
            metric_type='system',
            metric_name=system_metric.metric_name,
            is_active=True
        )
        
        service = MonitoringService()
        
        for rule in rules:
            try:
                # Evaluar regla con el nuevo valor
                alert_triggered = service._evaluate_rule(rule, system_metric.value)
                
                if alert_triggered:
                    # Crear alerta
                    alert = service._create_alert(rule, system_metric.value)
                    service._send_notifications(rule, alert)
                    
                    logger.info(f"Alerta creada por métrica del sistema: {alert.title}")
                
            except Exception as e:
                logger.error(f"Error evaluando regla {rule.name} con métrica del sistema: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error evaluando reglas de monitoreo: {str(e)}")


def _update_rules_using_channel(channel, deleted=False):
    """Actualizar reglas que usan un canal de notificación"""
    try:
        # Buscar reglas que usan este canal
        rules = MonitoringRule.objects.filter(
            notification_channels__contains=[channel.id]
        )
        
        for rule in rules:
            # Remover canal de la lista de canales de notificación
            if channel.id in rule.notification_channels:
                rule.notification_channels.remove(channel.id)
                rule.save()
                
                logger.info(f"Canal removido de regla: {rule.name}")
        
    except Exception as e:
        logger.error(f"Error actualizando reglas que usan canal: {str(e)}")


def _set_default_alert_template(template):
    """Establecer plantilla de alerta por defecto"""
    try:
        # Desmarcar otras plantillas como por defecto
        AlertTemplate.objects.filter(
            is_default=True
        ).exclude(id=template.id).update(is_default=False)
        
        logger.info(f"Plantilla establecida como por defecto: {template.name}")
        
    except Exception as e:
        logger.error(f"Error estableciendo plantilla por defecto: {str(e)}")


def _cancel_scheduled_rule_execution(rule):
    """Cancelar ejecución programada de regla"""
    try:
        # Cancelar tareas de Celery relacionadas
        from celery import current_app
        
        # Buscar y cancelar tareas relacionadas con esta regla
        # Esto es una implementación básica, en producción se necesitaría
        # un sistema más robusto para rastrear tareas específicas
        
        logger.info(f"Ejecución programada cancelada para regla: {rule.name}")
        
    except Exception as e:
        logger.error(f"Error cancelando ejecución programada: {str(e)}")


def _cancel_scheduled_health_check_execution(health_check):
    """Cancelar ejecución programada de verificación de salud"""
    try:
        # Cancelar tareas de Celery relacionadas
        from celery import current_app
        
        # Buscar y cancelar tareas relacionadas con esta verificación
        # Esto es una implementación básica, en producción se necesitaría
        # un sistema más robusto para rastrear tareas específicas
        
        logger.info(f"Ejecución programada cancelada para verificación: {health_check.name}")
        
    except Exception as e:
        logger.error(f"Error cancelando ejecución programada: {str(e)}")


# Tareas de Celery para ejecución automática
@shared_task
def execute_monitoring_rule(rule_id):
    """Ejecutar regla de monitoreo"""
    try:
        rule = MonitoringRule.objects.get(id=rule_id)
        
        if not rule.is_active:
            logger.warning(f"Regla no activa: {rule.name}")
            return
        
        from .services import MonitoringService
        service = MonitoringService()
        result = service.execute_rule(rule)
        
        logger.info(f"Regla ejecutada exitosamente: {rule.name}")
        
        # Programar próxima ejecución
        execute_monitoring_rule.apply_async(
            args=[rule_id],
            countdown=rule.check_interval
        )
        
        return result
        
    except MonitoringRule.DoesNotExist:
        logger.warning(f"Regla no encontrada: {rule_id}")
    except Exception as e:
        logger.error(f"Error ejecutando regla {rule_id}: {str(e)}")
        raise


@shared_task
def execute_health_check(health_check_id):
    """Ejecutar verificación de salud"""
    try:
        health_check = HealthCheck.objects.get(id=health_check_id)
        
        if not health_check.is_active:
            logger.warning(f"Verificación no activa: {health_check.name}")
            return
        
        from .services import HealthCheckService
        service = HealthCheckService()
        result = service.execute_health_check(health_check)
        
        logger.info(f"Verificación ejecutada exitosamente: {health_check.name}")
        
        # Programar próxima ejecución
        execute_health_check.apply_async(
            args=[health_check_id],
            countdown=health_check.check_interval
        )
        
        return result
        
    except HealthCheck.DoesNotExist:
        logger.warning(f"Verificación no encontrada: {health_check_id}")
    except Exception as e:
        logger.error(f"Error ejecutando verificación {health_check_id}: {str(e)}")
        raise


@shared_task
def collect_system_metrics():
    """Recopilar métricas del sistema"""
    try:
        import psutil
        
        metrics = [
            ('cpu', 'cpu_percent', psutil.cpu_percent(interval=1)),
            ('memory', 'memory_percent', psutil.virtual_memory().percent),
            ('disk', 'disk_percent', psutil.disk_usage('/').percent),
            ('disk', 'disk_free_gb', psutil.disk_usage('/').free / (1024**3)),
        ]
        
        for metric_type, metric_name, value in metrics:
            SystemMetrics.objects.create(
                metric_type=metric_type,
                metric_name=metric_name,
                value=value,
                unit='%' if 'percent' in metric_name else 'GB'
            )
        
        logger.info(f"Métricas del sistema recopiladas: {len(metrics)} métricas")
        
        # Programar próxima recopilación
        collect_system_metrics.apply_async(countdown=60)  # Cada minuto
        
    except Exception as e:
        logger.error(f"Error recopilando métricas del sistema: {str(e)}")
        raise


@shared_task
def cleanup_old_metrics():
    """Limpiar métricas antiguas"""
    try:
        # Eliminar métricas más antiguas de 30 días
        cutoff_date = timezone.now() - timedelta(days=30)
        
        deleted_count = SystemMetrics.objects.filter(
            timestamp__lt=cutoff_date
        ).delete()[0]
        
        logger.info(f"Métricas antiguas eliminadas: {deleted_count}")
        
        # Programar próxima limpieza
        cleanup_old_metrics.apply_async(countdown=24 * 60 * 60)  # Cada día
        
    except Exception as e:
        logger.error(f"Error limpiando métricas antiguas: {str(e)}")
        raise
