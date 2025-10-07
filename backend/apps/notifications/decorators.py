import functools
import json
from django.utils import timezone
from .logging import notification_logger


def handle_consumer_error(method):
    """
    Decorador para manejar errores en métodos de consumidores WebSocket.
    
    Registra errores y envía respuestas apropiadas al cliente.
    """
    @functools.wraps(method)
    async def wrapper(consumer, *args, **kwargs):
        try:
            return await method(consumer, *args, **kwargs)
            
        except json.JSONDecodeError as e:
            notification_logger.error(
                'Error al decodificar JSON',
                data={
                    'method': method.__name__,
                    'error': str(e),
                    'user_id': getattr(consumer.user, 'id', None)
                }
            )
            await consumer.send(text_data=json.dumps({
                'type': 'error',
                'code': 'invalid_json',
                'message': 'Formato JSON inválido'
            }))
            
        except ValueError as e:
            notification_logger.warning(
                'Error de validación',
                data={
                    'method': method.__name__,
                    'error': str(e),
                    'user_id': getattr(consumer.user, 'id', None)
                }
            )
            await consumer.send(text_data=json.dumps({
                'type': 'error',
                'code': 'validation_error',
                'message': str(e)
            }))
            
        except Exception as e:
            notification_logger.error(
                'Error inesperado en consumidor',
                data={
                    'method': method.__name__,
                    'error': str(e),
                    'user_id': getattr(consumer.user, 'id', None)
                }
            )
            await consumer.send(text_data=json.dumps({
                'type': 'error',
                'code': 'internal_error',
                'message': 'Error interno del servidor'
            }))
            
            # Cerrar conexión en caso de error crítico
            if method.__name__ in ['connect', 'receive']:
                await consumer.close(code=4000)
    
    return wrapper


def track_consumer_metrics(method):
    """
    Decorador para registrar métricas de los consumidores WebSocket.
    
    Registra tiempos de ejecución, éxito/fallo y otros datos.
    """
    @functools.wraps(method)
    async def wrapper(consumer, *args, **kwargs):
        start_time = timezone.now()
        success = False
        
        try:
            result = await method(consumer, *args, **kwargs)
            success = True
            return result
            
        finally:
            end_time = timezone.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Registrar métricas
            notification_logger.info(
                f'Métricas de {method.__name__}',
                data={
                    'method': method.__name__,
                    'success': success,
                    'execution_time': execution_time,
                    'user_id': getattr(consumer.user, 'id', None),
                    'timestamp': end_time.isoformat()
                },
                event_type='consumer_metrics',
                identifier=f'{method.__name__}_{getattr(consumer.user, "id", "anonymous")}'
            )
    
    return wrapper


def validate_message_type(required_type=None, allowed_types=None):
    """
    Decorador para validar el tipo de mensaje recibido.
    
    Args:
        required_type: Tipo específico requerido
        allowed_types: Lista de tipos permitidos
    """
    def decorator(method):
        @functools.wraps(method)
        async def wrapper(consumer, text_data, *args, **kwargs):
            try:
                data = json.loads(text_data)
                message_type = data.get('type')
                
                if required_type and message_type != required_type:
                    raise ValueError(f'Tipo de mensaje inválido. Se esperaba: {required_type}')
                
                if allowed_types and message_type not in allowed_types:
                    raise ValueError(f'Tipo de mensaje no permitido. Permitidos: {", ".join(allowed_types)}')
                
                return await method(consumer, text_data, *args, **kwargs)
                
            except json.JSONDecodeError:
                raise ValueError('Formato JSON inválido')
            
            except KeyError:
                raise ValueError('Tipo de mensaje requerido')
        
        return wrapper
    return decorator


def require_authentication(method):
    """
    Decorador para asegurar que el usuario está autenticado.
    """
    @functools.wraps(method)
    async def wrapper(consumer, *args, **kwargs):
        if not consumer.user or not consumer.user.is_authenticated:
            notification_logger.warning(
                'Intento de acceso no autorizado',
                data={
                    'method': method.__name__,
                    'user': getattr(consumer.user, 'username', 'anonymous')
                }
            )
            await consumer.send(text_data=json.dumps({
                'type': 'error',
                'code': 'authentication_required',
                'message': 'Autenticación requerida'
            }))
            await consumer.close(code=4001)
            return
        
        return await method(consumer, *args, **kwargs)
    
    return wrapper