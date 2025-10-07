from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from .models import MonitoringRule, HealthCheck, SystemMetrics
from .services import MonitoringService, HealthCheckService

logger = logging.getLogger(__name__)


@shared_task
def execute_monitoring_rule(rule_id):
    """Ejecutar regla de monitoreo"""
    try:
        rule = MonitoringRule.objects.get(id=rule_id)
        
        if not rule.is_active:
            logger.warning(f"Regla no activa: {rule.name}")
            return
        
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


@shared_task
def execute_all_monitoring_rules():
    """Ejecutar todas las reglas de monitoreo activas"""
    try:
        service = MonitoringService()
        result = service.execute_all_rules()
        
        logger.info(f"Todas las reglas de monitoreo ejecutadas: {result}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error ejecutando todas las reglas de monitoreo: {str(e)}")
        raise


@shared_task
def execute_all_health_checks():
    """Ejecutar todas las verificaciones de salud activas"""
    try:
        service = HealthCheckService()
        result = service.execute_all_health_checks()
        
        logger.info(f"Todas las verificaciones de salud ejecutadas: {result}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error ejecutando todas las verificaciones de salud: {str(e)}")
        raise


@shared_task
def send_alert_notifications(alert_id):
    """Enviar notificaciones para una alerta"""
    try:
        from .models import Alert
        
        alert = Alert.objects.get(id=alert_id)
        service = MonitoringService()
        service._send_notifications(alert.rule, alert)
        
        logger.info(f"Notificaciones enviadas para alerta: {alert.title}")
        
    except Alert.DoesNotExist:
        logger.warning(f"Alerta no encontrada: {alert_id}")
    except Exception as e:
        logger.error(f"Error enviando notificaciones para alerta {alert_id}: {str(e)}")
        raise


@shared_task
def cleanup_old_alerts():
    """Limpiar alertas antiguas"""
    try:
        # Eliminar alertas resueltas más antiguas de 90 días
        cutoff_date = timezone.now() - timedelta(days=90)
        
        deleted_count = Alert.objects.filter(
            status='resolved',
            resolved_at__lt=cutoff_date
        ).delete()[0]
        
        logger.info(f"Alertas antiguas eliminadas: {deleted_count}")
        
        # Programar próxima limpieza
        cleanup_old_alerts.apply_async(countdown=24 * 60 * 60)  # Cada día
        
    except Exception as e:
        logger.error(f"Error limpiando alertas antiguas: {str(e)}")
        raise


@shared_task
def generate_monitoring_report():
    """Generar reporte de monitoreo"""
    try:
        from .models import Alert, MonitoringRule, HealthCheck
        
        # Estadísticas del día
        today = timezone.now().date()
        alerts_today = Alert.objects.filter(triggered_at__date=today).count()
        active_alerts = Alert.objects.filter(status='active').count()
        total_rules = MonitoringRule.objects.filter(is_active=True).count()
        health_checks_total = HealthCheck.objects.filter(is_active=True).count()
        health_checks_healthy = HealthCheck.objects.filter(status='healthy').count()
        
        report = {
            'date': today.isoformat(),
            'alerts_today': alerts_today,
            'active_alerts': active_alerts,
            'total_rules': total_rules,
            'health_checks_total': health_checks_total,
            'health_checks_healthy': health_checks_healthy,
            'health_check_success_rate': (health_checks_healthy / health_checks_total * 100) if health_checks_total > 0 else 0
        }
        
        logger.info(f"Reporte de monitoreo generado: {report}")
        
        # Programar próximo reporte
        generate_monitoring_report.apply_async(countdown=24 * 60 * 60)  # Cada día
        
        return report
        
    except Exception as e:
        logger.error(f"Error generando reporte de monitoreo: {str(e)}")
        raise
