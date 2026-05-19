import logging
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings


class NotificationLogger:
    """Sistema de logging para el sistema de notificaciones"""
    
    def __init__(self, app_name='notifications'):
        self.logger = logging.getLogger(app_name)
        self.setup_logger()
    
    def setup_logger(self):
        """Configurar el logger"""
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s - Data: %(data)s'
        )
        
        # Handler para archivo
        file_handler = logging.FileHandler('logs/notifications.log')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Nivel de logging según DEBUG
        self.logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    def _format_log_data(self, data):
        """Formatear datos adicionales para el log"""
        if isinstance(data, dict):
            return data
        return {'details': str(data)} if data else {}
    
    def _get_cache_key(self, event_type, identifier):
        """Generar key para caché"""
        return f'notification_event:{event_type}:{identifier}'
    
    def _should_rate_limit(self, event_type, identifier, window=60):
        """Verificar si el evento debe ser limitado por frecuencia"""
        cache_key = self._get_cache_key(event_type, identifier)
        if cache.get(cache_key):
            return True
            
        cache.set(cache_key, True, window)
        return False
    
    def info(self, message, data=None, event_type=None, identifier=None):
        """Registrar evento informativo"""
        extra = self._format_log_data(data)
        if not self._should_rate_limit(event_type, identifier):
            self.logger.info(message, extra={'data': extra})
    
    def warning(self, message, data=None, event_type=None, identifier=None):
        """Registrar advertencia"""
        extra = self._format_log_data(data)
        if not self._should_rate_limit(event_type, identifier):
            self.logger.warning(message, extra={'data': extra})
    
    def error(self, message, data=None, event_type=None, identifier=None):
        """Registrar error"""
        extra = self._format_log_data(data)
        # Los errores nunca son rate limited
        self.logger.error(message, extra={'data': extra})
    
    def critical(self, message, data=None, event_type=None, identifier=None):
        """Registrar error crítico"""
        extra = self._format_log_data(data)
        # Los errores críticos nunca son rate limited
        self.logger.critical(message, extra={'data': extra})
    
    def connection_event(self, event_type, user_id, success, details=None):
        """Registrar evento de conexión"""
        data = {
            'user_id': user_id,
            'success': success,
            'timestamp': timezone.now().isoformat(),
            'details': details
        }
        
        if success:
            self.info(
                f'WebSocket {event_type}',
                data=data,
                event_type='connection',
                identifier=user_id
            )
        else:
            self.error(
                f'Error en WebSocket {event_type}',
                data=data,
                event_type='connection_error',
                identifier=user_id
            )
    
    def notification_event(self, notification_id, event_type, success, details=None):
        """Registrar evento de notificación"""
        data = {
            'notification_id': notification_id,
            'success': success,
            'timestamp': timezone.now().isoformat(),
            'details': details
        }
        
        if success:
            self.info(
                f'Notificación {event_type}',
                data=data,
                event_type='notification',
                identifier=notification_id
            )
        else:
            self.error(
                f'Error en notificación {event_type}',
                data=data,
                event_type='notification_error',
                identifier=notification_id
            )
    
    def system_event(self, event_type, success, details=None):
        """Registrar evento del sistema"""
        data = {
            'success': success,
            'timestamp': timezone.now().isoformat(),
            'details': details
        }
        
        if success:
            self.info(
                f'Evento del sistema {event_type}',
                data=data,
                event_type='system',
                identifier=event_type
            )
        else:
            self.error(
                f'Error en evento del sistema {event_type}',
                data=data,
                event_type='system_error',
                identifier=event_type
            )


# Crear instancia global del logger
notification_logger = NotificationLogger()