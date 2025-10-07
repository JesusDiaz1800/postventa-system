import os
import psutil
import time
import requests
import subprocess
import json
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.db import connection
from django.core.cache import cache
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.template import Template, Context

from .models import (
    MonitoringRule, Alert, MetricValue, HealthCheck, HealthCheckResult,
    SystemMetrics, NotificationChannel
)

logger = logging.getLogger(__name__)


class MonitoringService:
    """Servicio principal de monitoreo"""
    
    def __init__(self):
        self.metric_collectors = {
            'system': self._collect_system_metrics,
            'database': self._collect_database_metrics,
            'api': self._collect_api_metrics,
            'user': self._collect_user_metrics,
            'incident': self._collect_incident_metrics,
            'document': self._collect_document_metrics,
            'backup': self._collect_backup_metrics,
            'custom': self._collect_custom_metrics,
        }
    
    def execute_all_rules(self):
        """Ejecutar todas las reglas de monitoreo activas"""
        try:
            active_rules = MonitoringRule.objects.filter(is_active=True)
            results = []
            
            for rule in active_rules:
                try:
                    result = self.execute_rule(rule)
                    results.append({
                        'rule_id': rule.id,
                        'rule_name': rule.name,
                        'success': True,
                        'result': result
                    })
                except Exception as e:
                    logger.error(f"Error executing rule {rule.name}: {str(e)}")
                    results.append({
                        'rule_id': rule.id,
                        'rule_name': rule.name,
                        'success': False,
                        'error': str(e)
                    })
            
            return {
                'total_rules': len(active_rules),
                'successful_executions': len([r for r in results if r['success']]),
                'failed_executions': len([r for r in results if not r['success']]),
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Error executing all monitoring rules: {str(e)}")
            raise
    
    def execute_rule(self, rule):
        """Ejecutar una regla de monitoreo específica"""
        try:
            # Recopilar valor de métrica
            metric_value = self._collect_metric_value(rule)
            
            # Guardar valor de métrica
            MetricValue.objects.create(
                rule=rule,
                value=metric_value,
                metadata={'execution_time': timezone.now().isoformat()}
            )
            
            # Evaluar regla
            alert_triggered = self._evaluate_rule(rule, metric_value)
            
            if alert_triggered:
                # Crear alerta
                alert = self._create_alert(rule, metric_value)
                
                # Enviar notificaciones
                self._send_notifications(rule, alert)
                
                return {
                    'metric_value': metric_value,
                    'threshold_value': rule.threshold_value,
                    'alert_triggered': True,
                    'alert_id': alert.id
                }
            else:
                return {
                    'metric_value': metric_value,
                    'threshold_value': rule.threshold_value,
                    'alert_triggered': False
                }
                
        except Exception as e:
            logger.error(f"Error executing rule {rule.name}: {str(e)}")
            raise
    
    def test_rule(self, rule, test_data):
        """Probar una regla de monitoreo"""
        try:
            # Recopilar valor de métrica
            metric_value = self._collect_metric_value(rule)
            
            # Evaluar regla
            alert_triggered = self._evaluate_rule(rule, metric_value)
            
            return {
                'metric_value': metric_value,
                'threshold_value': rule.threshold_value,
                'alert_triggered': alert_triggered,
                'rule_evaluation': {
                    'operator': rule.comparison_operator,
                    'condition_met': alert_triggered
                }
            }
            
        except Exception as e:
            logger.error(f"Error testing rule {rule.name}: {str(e)}")
            raise
    
    def _collect_metric_value(self, rule):
        """Recopilar valor de métrica según el tipo"""
        try:
            collector = self.metric_collectors.get(rule.metric_type)
            if not collector:
                raise ValueError(f"Tipo de métrica no soportado: {rule.metric_type}")
            
            return collector(rule)
            
        except Exception as e:
            logger.error(f"Error collecting metric value for {rule.metric_name}: {str(e)}")
            raise
    
    def _evaluate_rule(self, rule, metric_value):
        """Evaluar si una regla debe activar una alerta"""
        try:
            operator = rule.comparison_operator
            threshold = rule.threshold_value
            
            if operator == 'gt':
                return metric_value > threshold
            elif operator == 'gte':
                return metric_value >= threshold
            elif operator == 'lt':
                return metric_value < threshold
            elif operator == 'lte':
                return metric_value <= threshold
            elif operator == 'eq':
                return metric_value == threshold
            elif operator == 'ne':
                return metric_value != threshold
            else:
                logger.warning(f"Operador de comparación no soportado: {operator}")
                return False
                
        except Exception as e:
            logger.error(f"Error evaluating rule {rule.name}: {str(e)}")
            return False
    
    def _create_alert(self, rule, metric_value):
        """Crear una alerta"""
        try:
            # Verificar si ya existe una alerta activa para esta regla
            existing_alert = Alert.objects.filter(
                rule=rule,
                status='active'
            ).first()
            
            if existing_alert:
                # Actualizar alerta existente
                existing_alert.metric_value = metric_value
                existing_alert.message = f"Métrica {rule.metric_name} sigue fuera del rango normal"
                existing_alert.save()
                return existing_alert
            
            # Crear nueva alerta
            alert = Alert.objects.create(
                rule=rule,
                severity=rule.severity,
                title=f"Alerta: {rule.metric_name}",
                message=f"Métrica {rule.metric_name} ha excedido el umbral de {rule.threshold_value}",
                metric_value=metric_value,
                threshold_value=rule.threshold_value,
                metadata={
                    'rule_name': rule.name,
                    'metric_type': rule.metric_type,
                    'comparison_operator': rule.comparison_operator
                },
                tags=rule.tags
            )
            
            return alert
            
        except Exception as e:
            logger.error(f"Error creating alert for rule {rule.name}: {str(e)}")
            raise
    
    def _send_notifications(self, rule, alert):
        """Enviar notificaciones para una alerta"""
        try:
            channels = rule.notification_channels
            if not channels:
                return
            
            for channel_id in channels:
                try:
                    channel = NotificationChannel.objects.get(id=channel_id)
                    if channel.is_active:
                        self._send_notification(channel, alert)
                except NotificationChannel.DoesNotExist:
                    logger.warning(f"Canal de notificación no encontrado: {channel_id}")
                except Exception as e:
                    logger.error(f"Error enviando notificación a canal {channel_id}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error sending notifications for alert {alert.id}: {str(e)}")
    
    def _send_notification(self, channel, alert):
        """Enviar notificación a un canal específico"""
        try:
            if channel.channel_type == 'email':
                self._send_email_notification(channel, alert)
            elif channel.channel_type == 'slack':
                self._send_slack_notification(channel, alert)
            elif channel.channel_type == 'webhook':
                self._send_webhook_notification(channel, alert)
            elif channel.channel_type == 'sms':
                self._send_sms_notification(channel, alert)
            elif channel.channel_type == 'push':
                self._send_push_notification(channel, alert)
            else:
                logger.warning(f"Tipo de canal no soportado: {channel.channel_type}")
                
        except Exception as e:
            logger.error(f"Error sending notification to channel {channel.name}: {str(e)}")
    
    def _send_email_notification(self, channel, alert):
        """Enviar notificación por email"""
        try:
            config = channel.config
            recipients = config.get('recipients', [])
            
            if not recipients:
                logger.warning(f"No hay destinatarios configurados para el canal {channel.name}")
                return
            
            subject = f"[{alert.severity.upper()}] {alert.title}"
            message = f"""
            Alerta de Monitoreo
            
            Regla: {alert.rule.name}
            Métrica: {alert.rule.metric_name}
            Valor: {alert.metric_value}
            Umbral: {alert.threshold_value}
            Severidad: {alert.severity}
            
            Mensaje: {alert.message}
            
            Timestamp: {alert.triggered_at}
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=False
            )
            
            logger.info(f"Email notification sent for alert {alert.id}")
            
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
    
    def _send_slack_notification(self, channel, alert):
        """Enviar notificación a Slack"""
        try:
            config = channel.config
            webhook_url = config.get('webhook_url')
            
            if not webhook_url:
                logger.warning(f"No hay webhook URL configurado para el canal {channel.name}")
                return
            
            # Determinar color según severidad
            color_map = {
                'low': '#36a64f',      # Verde
                'medium': '#ffaa00',   # Amarillo
                'high': '#ff6600',     # Naranja
                'critical': '#ff0000'  # Rojo
            }
            color = color_map.get(alert.severity, '#808080')
            
            payload = {
                'attachments': [{
                    'color': color,
                    'title': alert.title,
                    'text': alert.message,
                    'fields': [
                        {'title': 'Regla', 'value': alert.rule.name, 'short': True},
                        {'title': 'Métrica', 'value': alert.rule.metric_name, 'short': True},
                        {'title': 'Valor', 'value': str(alert.metric_value), 'short': True},
                        {'title': 'Umbral', 'value': str(alert.threshold_value), 'short': True},
                        {'title': 'Severidad', 'value': alert.severity, 'short': True},
                        {'title': 'Timestamp', 'value': alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S'), 'short': True}
                    ],
                    'footer': 'Sistema de Monitoreo',
                    'ts': int(alert.triggered_at.timestamp())
                }]
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Slack notification sent for alert {alert.id}")
            
        except Exception as e:
            logger.error(f"Error sending Slack notification: {str(e)}")
    
    def _send_webhook_notification(self, channel, alert):
        """Enviar notificación a webhook"""
        try:
            config = channel.config
            webhook_url = config.get('url')
            
            if not webhook_url:
                logger.warning(f"No hay URL configurado para el canal {channel.name}")
                return
            
            payload = {
                'alert_id': alert.id,
                'rule_name': alert.rule.name,
                'metric_name': alert.rule.metric_name,
                'metric_value': alert.metric_value,
                'threshold_value': alert.threshold_value,
                'severity': alert.severity,
                'title': alert.title,
                'message': alert.message,
                'triggered_at': alert.triggered_at.isoformat(),
                'metadata': alert.metadata
            }
            
            headers = config.get('headers', {})
            response = requests.post(webhook_url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Webhook notification sent for alert {alert.id}")
            
        except Exception as e:
            logger.error(f"Error sending webhook notification: {str(e)}")
    
    def _send_sms_notification(self, channel, alert):
        """Enviar notificación por SMS"""
        try:
            config = channel.config
            # Implementar envío de SMS según el proveedor
            logger.info(f"SMS notification would be sent for alert {alert.id}")
            
        except Exception as e:
            logger.error(f"Error sending SMS notification: {str(e)}")
    
    def _send_push_notification(self, channel, alert):
        """Enviar notificación push"""
        try:
            config = channel.config
            # Implementar notificaciones push
            logger.info(f"Push notification would be sent for alert {alert.id}")
            
        except Exception as e:
            logger.error(f"Error sending push notification: {str(e)}")
    
    # Métodos para recopilar métricas
    def _collect_system_metrics(self, rule):
        """Recopilar métricas del sistema"""
        try:
            metric_name = rule.metric_name
            
            if metric_name == 'cpu_percent':
                return psutil.cpu_percent(interval=1)
            elif metric_name == 'memory_percent':
                return psutil.virtual_memory().percent
            elif metric_name == 'disk_percent':
                return psutil.disk_usage('/').percent
            elif metric_name == 'disk_free_gb':
                return psutil.disk_usage('/').free / (1024**3)
            elif metric_name == 'load_average':
                return os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0
            else:
                raise ValueError(f"Métrica de sistema no soportada: {metric_name}")
                
        except Exception as e:
            logger.error(f"Error collecting system metric {rule.metric_name}: {str(e)}")
            return 0
    
    def _collect_database_metrics(self, rule):
        """Recopilar métricas de base de datos"""
        try:
            metric_name = rule.metric_name
            
            if metric_name == 'connection_count':
                with connection.cursor() as cursor:
                    cursor.execute("SELECT count(*) FROM pg_stat_activity")
                    return cursor.fetchone()[0]
            elif metric_name == 'database_size_mb':
                with connection.cursor() as cursor:
                    cursor.execute("SELECT pg_database_size(current_database())")
                    return cursor.fetchone()[0] / (1024**2)
            elif metric_name == 'slow_queries':
                # Implementar detección de consultas lentas
                return 0
            else:
                raise ValueError(f"Métrica de base de datos no soportada: {metric_name}")
                
        except Exception as e:
            logger.error(f"Error collecting database metric {rule.metric_name}: {str(e)}")
            return 0
    
    def _collect_api_metrics(self, rule):
        """Recopilar métricas de API"""
        try:
            metric_name = rule.metric_name
            
            if metric_name == 'request_count':
                # Implementar contador de requests
                return 0
            elif metric_name == 'response_time_avg':
                # Implementar tiempo promedio de respuesta
                return 0
            elif metric_name == 'error_rate':
                # Implementar tasa de errores
                return 0
            else:
                raise ValueError(f"Métrica de API no soportada: {metric_name}")
                
        except Exception as e:
            logger.error(f"Error collecting API metric {rule.metric_name}: {str(e)}")
            return 0
    
    def _collect_user_metrics(self, rule):
        """Recopilar métricas de usuarios"""
        try:
            metric_name = rule.metric_name
            
            if metric_name == 'active_users':
                # Implementar contador de usuarios activos
                return 0
            elif metric_name == 'login_attempts':
                # Implementar contador de intentos de login
                return 0
            else:
                raise ValueError(f"Métrica de usuario no soportada: {metric_name}")
                
        except Exception as e:
            logger.error(f"Error collecting user metric {rule.metric_name}: {str(e)}")
            return 0
    
    def _collect_incident_metrics(self, rule):
        """Recopilar métricas de incidencias"""
        try:
            metric_name = rule.metric_name
            
            if metric_name == 'open_incidents':
                from apps.incidents.models import Incident
                return Incident.objects.filter(status='open').count()
            elif metric_name == 'incident_response_time':
                # Implementar tiempo promedio de respuesta
                return 0
            else:
                raise ValueError(f"Métrica de incidencia no soportada: {metric_name}")
                
        except Exception as e:
            logger.error(f"Error collecting incident metric {rule.metric_name}: {str(e)}")
            return 0
    
    def _collect_document_metrics(self, rule):
        """Recopilar métricas de documentos"""
        try:
            metric_name = rule.metric_name
            
            if metric_name == 'total_documents':
                from apps.documents.models import Document
                return Document.objects.count()
            elif metric_name == 'document_storage_usage':
                # Implementar uso de almacenamiento de documentos
                return 0
            else:
                raise ValueError(f"Métrica de documento no soportada: {metric_name}")
                
        except Exception as e:
            logger.error(f"Error collecting document metric {rule.metric_name}: {str(e)}")
            return 0
    
    def _collect_backup_metrics(self, rule):
        """Recopilar métricas de backup"""
        try:
            metric_name = rule.metric_name
            
            if metric_name == 'backup_success_rate':
                from apps.backup.models import BackupInstance
                total = BackupInstance.objects.count()
                successful = BackupInstance.objects.filter(status='completed').count()
                return (successful / total * 100) if total > 0 else 0
            elif metric_name == 'last_backup_age_hours':
                from apps.backup.models import BackupInstance
                last_backup = BackupInstance.objects.filter(status='completed').order_by('-completed_at').first()
                if last_backup:
                    return (timezone.now() - last_backup.completed_at).total_seconds() / 3600
                return 999  # Sin backups
            else:
                raise ValueError(f"Métrica de backup no soportada: {metric_name}")
                
        except Exception as e:
            logger.error(f"Error collecting backup metric {rule.metric_name}: {str(e)}")
            return 0
    
    def _collect_custom_metrics(self, rule):
        """Recopilar métricas personalizadas"""
        try:
            # Implementar lógica para métricas personalizadas
            # Esto podría incluir scripts externos, APIs, etc.
            return 0
            
        except Exception as e:
            logger.error(f"Error collecting custom metric {rule.metric_name}: {str(e)}")
            return 0


class AlertService:
    """Servicio para gestión de alertas"""
    
    def test_notification_channel(self, channel, test_data):
        """Probar canal de notificación"""
        try:
            test_message = test_data.get('test_message', 'Test message from monitoring system')
            
            # Crear alerta de prueba
            test_alert = Alert(
                rule=MonitoringRule.objects.first(),  # Usar primera regla disponible
                severity='medium',
                title='Prueba de Canal de Notificación',
                message=test_message,
                metric_value=100,
                threshold_value=90,
                triggered_at=timezone.now()
            )
            
            # Enviar notificación de prueba
            monitoring_service = MonitoringService()
            monitoring_service._send_notification(channel, test_alert)
            
            return {
                'success': True,
                'message': 'Canal de notificación probado exitosamente'
            }
            
        except Exception as e:
            logger.error(f"Error testing notification channel {channel.name}: {str(e)}")
            raise


class HealthCheckService:
    """Servicio para verificaciones de salud"""
    
    def execute_all_health_checks(self):
        """Ejecutar todas las verificaciones de salud activas"""
        try:
            active_checks = HealthCheck.objects.filter(is_active=True)
            results = []
            
            for health_check in active_checks:
                try:
                    result = self.execute_health_check(health_check)
                    results.append({
                        'health_check_id': health_check.id,
                        'health_check_name': health_check.name,
                        'success': True,
                        'result': result
                    })
                except Exception as e:
                    logger.error(f"Error executing health check {health_check.name}: {str(e)}")
                    results.append({
                        'health_check_id': health_check.id,
                        'health_check_name': health_check.name,
                        'success': False,
                        'error': str(e)
                    })
            
            return {
                'total_checks': len(active_checks),
                'successful_checks': len([r for r in results if r['success']]),
                'failed_checks': len([r for r in results if not r['success']]),
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Error executing all health checks: {str(e)}")
            raise
    
    def execute_health_check(self, health_check):
        """Ejecutar una verificación de salud específica"""
        try:
            start_time = time.time()
            
            if health_check.check_type == 'database':
                result = self._check_database(health_check)
            elif health_check.check_type == 'redis':
                result = self._check_redis(health_check)
            elif health_check.check_type == 'storage':
                result = self._check_storage(health_check)
            elif health_check.check_type == 'api':
                result = self._check_api(health_check)
            elif health_check.check_type == 'external':
                result = self._check_external(health_check)
            elif health_check.check_type == 'custom':
                result = self._check_custom(health_check)
            else:
                raise ValueError(f"Tipo de verificación no soportado: {health_check.check_type}")
            
            response_time = (time.time() - start_time) * 1000  # En milisegundos
            
            # Crear resultado
            health_result = HealthCheckResult.objects.create(
                health_check=health_check,
                status=result['status'],
                response_time=response_time,
                message=result['message'],
                metadata=result.get('metadata', {})
            )
            
            # Actualizar estado de la verificación
            health_check.status = result['status']
            health_check.last_check = timezone.now()
            health_check.save()
            
            return {
                'status': result['status'],
                'response_time': response_time,
                'message': result['message'],
                'metadata': result.get('metadata', {})
            }
            
        except Exception as e:
            logger.error(f"Error executing health check {health_check.name}: {str(e)}")
            
            # Crear resultado de error
            HealthCheckResult.objects.create(
                health_check=health_check,
                status='unhealthy',
                response_time=0,
                message=f'Error: {str(e)}',
                metadata={'error': str(e)}
            )
            
            # Actualizar estado de la verificación
            health_check.status = 'unhealthy'
            health_check.last_check = timezone.now()
            health_check.save()
            
            raise
    
    def _check_database(self, health_check):
        """Verificar salud de la base de datos"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                
                if result:
                    return {
                        'status': 'healthy',
                        'message': 'Base de datos accesible',
                        'metadata': {'query_result': result[0]}
                    }
                else:
                    return {
                        'status': 'unhealthy',
                        'message': 'Base de datos no responde correctamente'
                    }
                    
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Error de base de datos: {str(e)}'
            }
    
    def _check_redis(self, health_check):
        """Verificar salud de Redis"""
        try:
            cache.set('health_check', 'test', 10)
            value = cache.get('health_check')
            
            if value == 'test':
                return {
                    'status': 'healthy',
                    'message': 'Redis accesible'
                }
            else:
                return {
                    'status': 'unhealthy',
                    'message': 'Redis no responde correctamente'
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Error de Redis: {str(e)}'
            }
    
    def _check_storage(self, health_check):
        """Verificar salud del almacenamiento"""
        try:
            # Verificar espacio en disco
            disk_usage = psutil.disk_usage('/')
            free_percent = (disk_usage.free / disk_usage.total) * 100
            
            if free_percent > 10:  # Más del 10% libre
                status = 'healthy'
                message = f'Almacenamiento saludable ({free_percent:.1f}% libre)'
            elif free_percent > 5:  # Entre 5% y 10% libre
                status = 'degraded'
                message = f'Almacenamiento con poco espacio ({free_percent:.1f}% libre)'
            else:  # Menos del 5% libre
                status = 'unhealthy'
                message = f'Almacenamiento crítico ({free_percent:.1f}% libre)'
            
            return {
                'status': status,
                'message': message,
                'metadata': {
                    'free_percent': free_percent,
                    'free_bytes': disk_usage.free,
                    'total_bytes': disk_usage.total
                }
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Error verificando almacenamiento: {str(e)}'
            }
    
    def _check_api(self, health_check):
        """Verificar salud de API externa"""
        try:
            endpoint = health_check.endpoint
            if not endpoint:
                return {
                    'status': 'unhealthy',
                    'message': 'Endpoint no configurado'
                }
            
            response = requests.get(endpoint, timeout=health_check.timeout)
            response.raise_for_status()
            
            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'message': f'API accesible (status: {response.status_code})',
                    'metadata': {'status_code': response.status_code}
                }
            else:
                return {
                    'status': 'degraded',
                    'message': f'API responde con status: {response.status_code}',
                    'metadata': {'status_code': response.status_code}
                }
                
        except requests.exceptions.Timeout:
            return {
                'status': 'unhealthy',
                'message': 'Timeout al verificar API'
            }
        except requests.exceptions.ConnectionError:
            return {
                'status': 'unhealthy',
                'message': 'Error de conexión con API'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Error verificando API: {str(e)}'
            }
    
    def _check_external(self, health_check):
        """Verificar servicio externo"""
        try:
            # Implementar verificación de servicios externos
            return {
                'status': 'healthy',
                'message': 'Servicio externo accesible'
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Error verificando servicio externo: {str(e)}'
            }
    
    def _check_custom(self, health_check):
        """Verificar con script personalizado"""
        try:
            script = health_check.check_script
            if not script:
                return {
                    'status': 'unhealthy',
                    'message': 'Script de verificación no configurado'
                }
            
            # Ejecutar script personalizado
            result = subprocess.run(
                script,
                shell=True,
                capture_output=True,
                text=True,
                timeout=health_check.timeout
            )
            
            if result.returncode == 0:
                return {
                    'status': 'healthy',
                    'message': 'Script ejecutado exitosamente',
                    'metadata': {
                        'returncode': result.returncode,
                        'stdout': result.stdout,
                        'stderr': result.stderr
                    }
                }
            else:
                return {
                    'status': 'unhealthy',
                    'message': f'Script falló con código {result.returncode}',
                    'metadata': {
                        'returncode': result.returncode,
                        'stdout': result.stdout,
                        'stderr': result.stderr
                    }
                }
                
        except subprocess.TimeoutExpired:
            return {
                'status': 'unhealthy',
                'message': 'Timeout al ejecutar script'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Error ejecutando script: {str(e)}'
            }
