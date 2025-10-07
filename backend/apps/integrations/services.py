import requests
import json
import logging
import hashlib
import hmac
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User

from .models import (
    ExternalSystem, IntegrationTemplate, IntegrationInstance, 
    IntegrationLog, WebhookEndpoint, WebhookLog
)

logger = logging.getLogger(__name__)


class IntegrationService:
    """Servicio para gestionar integraciones"""
    
    def __init__(self):
        self.timeout = 30
        self.max_retries = 3
    
    def test_connection(self, system, test_config):
        """Probar conexión a un sistema externo"""
        try:
            # Configurar la petición
            headers = system.headers.copy()
            if system.api_key:
                headers['Authorization'] = f'Bearer {system.api_key}'
            elif system.token:
                headers['Authorization'] = f'Token {system.token}'
            
            # Realizar petición de prueba
            if system.system_type == 'rest':
                response = requests.get(
                    system.base_url,
                    headers=headers,
                    timeout=system.timeout,
                    verify=system.verify_ssl
                )
            elif system.system_type == 'api':
                response = requests.get(
                    system.endpoint_url,
                    headers=headers,
                    timeout=system.timeout,
                    verify=system.verify_ssl
                )
            else:
                # Para otros tipos de sistemas, implementar lógica específica
                response = requests.get(
                    system.base_url or system.endpoint_url,
                    headers=headers,
                    timeout=system.timeout,
                    verify=system.verify_ssl
                )
            
            return {
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'headers': dict(response.headers),
                'success': response.status_code < 400
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Connection test failed for {system.name}: {str(e)}")
            raise Exception(f"Error de conexión: {str(e)}")
    
    def sync_data(self, system, sync_config):
        """Sincronizar datos con un sistema externo"""
        try:
            # Crear instancia de sincronización
            instance = IntegrationInstance.objects.create(
                template=None,  # Se asignará después
                status='running',
                input_data=sync_config,
                started_by=User.objects.first(),  # Temporal
                started_at=timezone.now()
            )
            
            # Implementar lógica de sincronización específica
            # Esto dependerá del tipo de sistema y configuración
            
            # Actualizar estado
            instance.status = 'completed'
            instance.completed_at = timezone.now()
            instance.output_data = {'message': 'Sincronización completada'}
            instance.save()
            
            return {
                'instance_id': instance.id,
                'status': 'completed',
                'message': 'Sincronización iniciada exitosamente'
            }
            
        except Exception as e:
            logger.error(f"Data sync failed for {system.name}: {str(e)}")
            raise Exception(f"Error de sincronización: {str(e)}")
    
    def execute_template(self, template, input_data, user):
        """Ejecutar una plantilla de integración"""
        try:
            # Crear instancia de integración
            instance = IntegrationInstance.objects.create(
                template=template,
                status='running',
                input_data=input_data,
                started_by=user,
                started_at=timezone.now()
            )
            
            # Log de inicio
            IntegrationLog.objects.create(
                instance=instance,
                level='info',
                message='Iniciando ejecución de plantilla',
                step='start'
            )
            
            # Ejecutar la integración
            result = self._execute_integration(instance, template, input_data)
            
            # Actualizar estado
            instance.status = 'completed'
            instance.completed_at = timezone.now()
            instance.output_data = result
            instance.save()
            
            # Log de finalización
            IntegrationLog.objects.create(
                instance=instance,
                level='info',
                message='Plantilla ejecutada exitosamente',
                step='complete'
            )
            
            return instance
            
        except Exception as e:
            logger.error(f"Template execution failed for {template.name}: {str(e)}")
            
            # Actualizar estado a fallido
            instance.status = 'failed'
            instance.completed_at = timezone.now()
            instance.error_data = {'error': str(e)}
            instance.save()
            
            # Log de error
            IntegrationLog.objects.create(
                instance=instance,
                level='error',
                message=f'Error ejecutando plantilla: {str(e)}',
                step='error'
            )
            
            raise Exception(f"Error ejecutando plantilla: {str(e)}")
    
    def test_template(self, template, test_data):
        """Probar una plantilla de integración"""
        try:
            # Simular ejecución sin crear instancia
            result = self._execute_integration(None, template, test_data, test_mode=True)
            
            return {
                'success': True,
                'result': result,
                'message': 'Prueba exitosa'
            }
            
        except Exception as e:
            logger.error(f"Template test failed for {template.name}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Prueba fallida'
            }
    
    def cancel_instance(self, instance, user):
        """Cancelar una instancia de integración"""
        if instance.status in ['completed', 'cancelled', 'failed']:
            raise Exception("La instancia no puede ser cancelada en su estado actual")
        
        instance.status = 'cancelled'
        instance.completed_by = user
        instance.completed_at = timezone.now()
        instance.save()
        
        # Log de cancelación
        IntegrationLog.objects.create(
            instance=instance,
            level='warning',
            message='Instancia cancelada por el usuario',
            step='cancel'
        )
    
    def retry_instance(self, instance, user):
        """Reintentar una instancia de integración"""
        if instance.status != 'failed':
            raise Exception("Solo se pueden reintentar instancias fallidas")
        
        # Crear nueva instancia basada en la fallida
        new_instance = IntegrationInstance.objects.create(
            template=instance.template,
            status='running',
            input_data=instance.input_data,
            started_by=user,
            started_at=timezone.now()
        )
        
        # Log de reintento
        IntegrationLog.objects.create(
            instance=new_instance,
            level='info',
            message=f'Reintentando instancia fallida {instance.id}',
            step='retry'
        )
        
        try:
            # Ejecutar la integración
            result = self._execute_integration(new_instance, instance.template, instance.input_data)
            
            # Actualizar estado
            new_instance.status = 'completed'
            new_instance.completed_at = timezone.now()
            new_instance.output_data = result
            new_instance.save()
            
            # Log de éxito
            IntegrationLog.objects.create(
                instance=new_instance,
                level='info',
                message='Reintento exitoso',
                step='complete'
            )
            
            return new_instance
            
        except Exception as e:
            logger.error(f"Retry failed for instance {instance.id}: {str(e)}")
            
            # Actualizar estado a fallido
            new_instance.status = 'failed'
            new_instance.completed_at = timezone.now()
            new_instance.error_data = {'error': str(e)}
            new_instance.save()
            
            # Log de error
            IntegrationLog.objects.create(
                instance=new_instance,
                level='error',
                message=f'Error en reintento: {str(e)}',
                step='error'
            )
            
            raise Exception(f"Error en reintento: {str(e)}")
    
    def _execute_integration(self, instance, template, input_data, test_mode=False):
        """Ejecutar la lógica de integración"""
        try:
            # Obtener sistemas origen y destino
            source_system = template.source_system
            target_system = template.target_system
            
            # Log de inicio de procesamiento
            if instance:
                IntegrationLog.objects.create(
                    instance=instance,
                    level='info',
                    message=f'Procesando integración {template.name}',
                    step='process'
                )
            
            # Implementar lógica específica según el tipo de plantilla
            if template.template_type == 'incident_sync':
                result = self._sync_incidents(source_system, target_system, input_data, template)
            elif template.template_type == 'document_sync':
                result = self._sync_documents(source_system, target_system, input_data, template)
            elif template.template_type == 'user_sync':
                result = self._sync_users(source_system, target_system, input_data, template)
            elif template.template_type == 'notification':
                result = self._send_notification(source_system, target_system, input_data, template)
            else:
                result = self._generic_integration(source_system, target_system, input_data, template)
            
            # Log de éxito
            if instance:
                IntegrationLog.objects.create(
                    instance=instance,
                    level='info',
                    message='Integración procesada exitosamente',
                    step='success'
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Integration execution failed: {str(e)}")
            
            # Log de error
            if instance:
                IntegrationLog.objects.create(
                    instance=instance,
                    level='error',
                    message=f'Error en integración: {str(e)}',
                    step='error'
                )
            
            raise e
    
    def _sync_incidents(self, source_system, target_system, input_data, template):
        """Sincronizar incidentes"""
        # Implementar lógica de sincronización de incidentes
        return {'message': 'Incidentes sincronizados', 'count': 0}
    
    def _sync_documents(self, source_system, target_system, input_data, template):
        """Sincronizar documentos"""
        # Implementar lógica de sincronización de documentos
        return {'message': 'Documentos sincronizados', 'count': 0}
    
    def _sync_users(self, source_system, target_system, input_data, template):
        """Sincronizar usuarios"""
        # Implementar lógica de sincronización de usuarios
        return {'message': 'Usuarios sincronizados', 'count': 0}
    
    def _send_notification(self, source_system, target_system, input_data, template):
        """Enviar notificación"""
        # Implementar lógica de envío de notificaciones
        return {'message': 'Notificación enviada', 'status': 'sent'}
    
    def _generic_integration(self, source_system, target_system, input_data, template):
        """Integración genérica"""
        # Implementar lógica de integración genérica
        return {'message': 'Integración genérica ejecutada', 'status': 'completed'}


class WebhookService:
    """Servicio para gestionar webhooks"""
    
    def __init__(self):
        self.timeout = 30
    
    def test_endpoint(self, endpoint, test_config):
        """Probar un endpoint de webhook"""
        try:
            # Simular petición
            test_data = test_config.get('test_data', {})
            test_headers = test_config.get('test_headers', {})
            
            # Crear log de prueba
            log = WebhookLog.objects.create(
                endpoint=endpoint,
                status='received',
                request_method=endpoint.http_method,
                request_headers=test_headers,
                request_body=json.dumps(test_data),
                request_ip='127.0.0.1'
            )
            
            # Procesar webhook
            result = self._process_webhook(endpoint, test_data, test_headers, log)
            
            # Actualizar log
            log.status = 'processed'
            log.response_status = 200
            log.response_body = json.dumps(result)
            log.save()
            
            return {
                'success': True,
                'log_id': log.id,
                'result': result
            }
            
        except Exception as e:
            logger.error(f"Webhook test failed for {endpoint.name}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_webhook(self, endpoint, request_data, request_headers, request_ip):
        """Procesar un webhook entrante"""
        try:
            # Crear log
            log = WebhookLog.objects.create(
                endpoint=endpoint,
                status='received',
                request_method=request_data.get('method', 'POST'),
                request_headers=request_headers,
                request_body=json.dumps(request_data),
                request_ip=request_ip
            )
            
            # Validar autenticación
            if endpoint.requires_auth:
                if not self._validate_auth(endpoint, request_headers):
                    log.status = 'failed'
                    log.response_status = 401
                    log.response_body = json.dumps({'error': 'Unauthorized'})
                    log.save()
                    return {'error': 'Unauthorized'}, 401
            
            # Validar firma
            if endpoint.validate_signature:
                if not self._validate_signature(endpoint, request_data, request_headers):
                    log.status = 'failed'
                    log.response_status = 403
                    log.response_body = json.dumps({'error': 'Invalid signature'})
                    log.save()
                    return {'error': 'Invalid signature'}, 403
            
            # Procesar webhook
            result = self._process_webhook(endpoint, request_data, request_headers, log)
            
            # Actualizar log
            log.status = 'processed'
            log.response_status = 200
            log.response_body = json.dumps(result)
            log.save()
            
            return result, 200
            
        except Exception as e:
            logger.error(f"Webhook processing failed for {endpoint.name}: {str(e)}")
            
            # Actualizar log con error
            log.status = 'failed'
            log.response_status = 500
            log.response_body = json.dumps({'error': str(e)})
            log.error_message = str(e)
            log.save()
            
            return {'error': str(e)}, 500
    
    def _validate_auth(self, endpoint, request_headers):
        """Validar autenticación del webhook"""
        if not endpoint.auth_token:
            return True
        
        auth_header = request_headers.get('Authorization', '')
        expected_auth = f'Bearer {endpoint.auth_token}'
        
        return auth_header == expected_auth
    
    def _validate_signature(self, endpoint, request_data, request_headers):
        """Validar firma del webhook"""
        if not endpoint.signature_secret:
            return True
        
        signature_header = request_headers.get(endpoint.signature_header, '')
        if not signature_header:
            return False
        
        # Calcular firma esperada
        body = json.dumps(request_data)
        expected_signature = hmac.new(
            endpoint.signature_secret.encode('utf-8'),
            body.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature_header, expected_signature)
    
    def _process_webhook(self, endpoint, request_data, request_headers, log):
        """Procesar el webhook"""
        try:
            # Verificar condiciones de filtro
            if not self._check_filter_conditions(endpoint, request_data):
                log.status = 'ignored'
                log.save()
                return {'message': 'Webhook ignored due to filter conditions'}
            
            # Ejecutar script de procesamiento si existe
            if endpoint.processing_script:
                result = self._execute_processing_script(endpoint, request_data, request_headers)
            else:
                result = self._default_processing(endpoint, request_data, request_headers)
            
            return result
            
        except Exception as e:
            logger.error(f"Webhook processing failed: {str(e)}")
            raise e
    
    def _check_filter_conditions(self, endpoint, request_data):
        """Verificar condiciones de filtro"""
        if not endpoint.filter_conditions:
            return True
        
        # Implementar lógica de filtrado
        # Por ahora, siempre retornar True
        return True
    
    def _execute_processing_script(self, endpoint, request_data, request_headers):
        """Ejecutar script de procesamiento personalizado"""
        try:
            # En un entorno de producción, esto debería ejecutarse en un sandbox
            # Por ahora, solo retornar un resultado genérico
            return {
                'message': 'Webhook processed with custom script',
                'endpoint': endpoint.name,
                'timestamp': timezone.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Processing script execution failed: {str(e)}")
            raise e
    
    def _default_processing(self, endpoint, request_data, request_headers):
        """Procesamiento por defecto del webhook"""
        return {
            'message': 'Webhook processed successfully',
            'endpoint': endpoint.name,
            'timestamp': timezone.now().isoformat(),
            'data': request_data
        }
