"""
AI Orchestrator con fallback y gestión de créditos mejorada
"""
import json
import time
import logging
from typing import Dict, Any, Optional, List
from django.conf import settings
from django.utils import timezone
from .models import AIProvider
from .providers import OpenAIAdapter, AnthropicAdapter, GoogleAdapter, LocalAdapter

logger = logging.getLogger(__name__)


class ProviderQuotaExceededError(Exception):
    """Excepción cuando se excede la cuota de un proveedor"""
    pass


class AIProviderManager:
    """Manager para proveedores de IA con gestión de cuotas y fallback"""
    
    def __init__(self):
        self.providers = {}
        self._load_providers()
    
    def _load_providers(self):
        """Cargar proveedores de IA desde la base de datos"""
        try:
            providers = AIProvider.objects.filter(enabled=True).order_by('priority')
            
            for provider in providers:
                config = {
                    'name': provider.name,
                    'api_key': provider.api_key_encrypted,  # TODO: Desencriptar
                    'enabled': provider.enabled,
                    'priority': provider.priority
                }
                
                if provider.type == 'openai':
                    self.providers[provider.name] = OpenAIProvider(provider)
                elif provider.type == 'anthropic':
                    self.providers[provider.name] = AnthropicProvider(provider)
                elif provider.type == 'google':
                    self.providers[provider.name] = GoogleProvider(provider)
                elif provider.type == 'local':
                    self.providers[provider.name] = LocalProvider(provider)
            
            logger.info(f"Cargados {len(self.providers)} proveedores de IA")
            
        except Exception as e:
            logger.error(f"Error cargando proveedores de IA: {e}")
    
    def get_available_provider(self, task_type='text', consent_external=True):
        """Obtener el mejor proveedor disponible para una tarea con lógica de fallback"""
        try:
            # Ordenar proveedores por prioridad
            sorted_providers = sorted(
                self.providers.items(),
                key=lambda x: x[1].provider.priority
            )
            
            for provider_name, provider in sorted_providers:
                # Verificar si el proveedor está disponible y soporta la tarea
                if not provider.is_available() or not provider.supports_task(task_type):
                    continue
                
                # Verificar consentimiento para proveedores externos
                if not consent_external and provider.type != 'local':
                    continue
                
                # Verificar cuota
                if not provider.has_quota():
                    logger.warning(f"Proveedor {provider_name} no tiene cuota restante")
                    continue
                
                return provider
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo proveedor disponible: {e}")
            return None
    
    def analyze_image(self, image_path, consent_external=False):
        """Analizar imagen con proveedores disponibles y lógica de fallback"""
        try:
            # Intentar proveedores externos primero (si hay consentimiento)
            if consent_external:
                provider = self.get_available_provider('vision', consent_external=True)
                if provider:
                    try:
                        result = provider.analyze_image(image_path)
                        result['provider_used'] = provider.name
                        result['fallback_used'] = False
                        result['tokens_consumed'] = provider.get_last_tokens_used()
                        return result
                    except ProviderQuotaExceededError:
                        logger.warning(f"Cuota del proveedor {provider.name} excedida, probando siguiente")
                        provider.mark_exhausted()
                    except Exception as e:
                        logger.error(f"Error con proveedor {provider.name}: {e}")
            
            # Fallback a proveedor local
            local_provider = self.providers.get('local')
            if local_provider and local_provider.is_available():
                try:
                    result = local_provider.analyze_image(image_path)
                    result['provider_used'] = 'local'
                    result['fallback_used'] = True
                    result['tokens_consumed'] = 0
                    return result
                except Exception as e:
                    logger.error(f"Error con proveedor local: {e}")
            
            # No hay proveedores disponibles
            return {
                'error': 'IA no disponible por límite de créditos. Intente nuevamente después de la hora de reinicio configurada.',
                'quota_exhausted': True,
                'next_reset_time': self._get_next_reset_time(),
                'fallback_used': False
            }
            
        except Exception as e:
            logger.error(f"Error analizando imagen: {e}")
            return {
                'error': f'Error en análisis de imagen: {str(e)}',
                'fallback_used': False
            }
    
    def generate_text(self, prompt, tone='neutral', consent_external=False):
        """Generar texto con proveedores disponibles y lógica de fallback"""
        try:
            # Intentar proveedores externos primero (si hay consentimiento)
            if consent_external:
                provider = self.get_available_provider('text', consent_external=True)
                if provider:
                    try:
                        result = provider.generate_text(prompt, tone)
                        result['provider_used'] = provider.name
                        result['fallback_used'] = False
                        result['tokens_consumed'] = provider.get_last_tokens_used()
                        return result
                    except ProviderQuotaExceededError:
                        logger.warning(f"Cuota del proveedor {provider.name} excedida, probando siguiente")
                        provider.mark_exhausted()
                    except Exception as e:
                        logger.error(f"Error con proveedor {provider.name}: {e}")
            
            # Fallback a proveedor local
            local_provider = self.providers.get('local')
            if local_provider and local_provider.is_available():
                try:
                    result = local_provider.generate_text(prompt, tone)
                    result['provider_used'] = 'local'
                    result['fallback_used'] = True
                    result['tokens_consumed'] = 0
                    return result
                except Exception as e:
                    logger.error(f"Error con proveedor local: {e}")
            
            # No hay proveedores disponibles
            return {
                'error': 'IA no disponible por límite de créditos. Intente nuevamente después de la hora de reinicio configurada.',
                'quota_exhausted': True,
                'next_reset_time': self._get_next_reset_time(),
                'fallback_used': False
            }
            
        except Exception as e:
            logger.error(f"Error generando texto: {e}")
            return {
                'error': f'Error generando texto: {str(e)}',
                'fallback_used': False
            }
    
    def _get_next_reset_time(self):
        """Obtener próxima hora de reinicio de cuota"""
        try:
            # Obtener la hora de reinicio más temprana de todos los proveedores
            providers = AIProvider.objects.filter(enabled=True)
            if providers.exists():
                # Por simplicidad, devolver la hora de reinicio del primer proveedor
                # En una implementación real, calcularías la más temprana
                return providers.first().quota_reset_time
            return "00:00"
            
        except Exception as e:
            logger.error(f"Error obteniendo próxima hora de reinicio: {e}")
            return "00:00"
    
    def get_provider_status(self):
        """Obtener estado de todos los proveedores"""
        try:
            status = {}
            
            for provider_name, provider in self.providers.items():
                status[provider_name] = {
                    'enabled': provider.is_enabled(),
                    'available': provider.is_available(),
                    'quota_remaining': provider.get_quota_remaining(),
                    'quota_reset_time': provider.get_quota_reset_time(),
                    'supports_vision': provider.supports_task('vision'),
                    'supports_text': provider.supports_task('text'),
                    'has_quota': provider.has_quota(),
                    'tokens_used_today': provider.get_tokens_used_today(),
                    'calls_used_today': provider.get_calls_used_today()
                }
            
            return status
            
        except Exception as e:
            logger.error(f"Error obteniendo estado de proveedores: {e}")
            return {}
    
    def refresh_providers(self):
        """Refrescar lista de proveedores desde la base de datos"""
        try:
            self.providers.clear()
            self._load_providers()
            logger.info("Proveedores de IA refrescados")
            
        except Exception as e:
            logger.error(f"Error refrescando proveedores: {e}")


class AIProviderWrapper:
    """Wrapper para proveedores de IA con gestión de cuotas"""
    
    def __init__(self, provider):
        self.provider = provider
        self.last_tokens_used = 0
    
    def is_available(self):
        """Verificar si el proveedor está disponible"""
        return self.provider.enabled and self.has_quota()
    
    def is_enabled(self):
        """Verificar si el proveedor está habilitado"""
        return self.provider.enabled
    
    def has_quota(self):
        """Verificar si el proveedor tiene cuota disponible"""
        return self.provider.has_quota()
    
    def supports_task(self, task_type):
        """Verificar si el proveedor soporta el tipo de tarea"""
        if task_type == 'vision':
            return self.provider.type in ['openai', 'anthropic', 'google', 'local']
        elif task_type == 'text':
            return self.provider.type in ['openai', 'anthropic', 'google', 'local']
        return False
    
    def get_quota_remaining(self):
        """Obtener cuota restante"""
        return self.provider.get_quota_remaining()
    
    def get_quota_reset_time(self):
        """Obtener hora de reinicio de cuota"""
        return self.provider.get_quota_reset_time()
    
    def get_tokens_used_today(self):
        """Obtener tokens usados hoy"""
        return self.provider.tokens_used_today
    
    def get_calls_used_today(self):
        """Obtener llamadas hechas hoy"""
        return self.provider.calls_made_today
    
    def get_last_tokens_used(self):
        """Obtener últimos tokens usados"""
        return self.last_tokens_used
    
    def mark_exhausted(self):
        """Marcar proveedor como agotado"""
        self.provider.mark_exhausted()
    
    def analyze_image(self, image_path):
        """Analizar imagen"""
        try:
            # Verificar cuota antes de procesar
            if not self.has_quota():
                raise ProviderQuotaExceededError(f"Cuota del proveedor {self.provider.name} excedida")
            
            # Procesar imagen (implementación simplificada)
            result = {
                'success': True,
                'analysis': {
                    'caption': f'Análisis de imagen realizado por {self.provider.name}',
                    'suggested_causes': [
                        'Posible defecto de fabricación',
                        'Daño durante transporte',
                        'Condiciones de instalación inadecuadas'
                    ],
                    'quality_assessment': {
                        'score': 85,
                        'issues': []
                    }
                },
                'provider_used': self.provider.name,
                'tokens_consumed': 100  # Simulado
            }
            
            # Actualizar cuota
            self.provider.consume_quota(result['tokens_consumed'])
            self.last_tokens_used = result['tokens_consumed']
            
            return result
            
        except Exception as e:
            logger.error(f"Error analizando imagen con {self.provider.name}: {e}")
            raise
    
    def generate_text(self, prompt, tone='neutral'):
        """Generar texto"""
        try:
            # Verificar cuota antes de procesar
            if not self.has_quota():
                raise ProviderQuotaExceededError(f"Cuota del proveedor {self.provider.name} excedida")
            
            # Generar texto (implementación simplificada)
            if tone == 'cliente':
                text = "Estimado cliente, hemos revisado la situación reportada y estamos trabajando en una solución."
            elif tone == 'proveedor':
                text = "Estimado proveedor, solicitamos su colaboración para revisar el lote mencionado."
            else:
                text = f"Texto generado por {self.provider.name} para: {prompt[:50]}..."
            
            result = {
                'success': True,
                'generated_text': text,
                'provider_used': self.provider.name,
                'tokens_consumed': 50  # Simulado
            }
            
            # Actualizar cuota
            self.provider.consume_quota(result['tokens_consumed'])
            self.last_tokens_used = result['tokens_consumed']
            
            return result
            
        except Exception as e:
            logger.error(f"Error generando texto con {self.provider.name}: {e}")
            raise


# Alias para compatibilidad
OpenAIProvider = AIProviderWrapper
AnthropicProvider = AIProviderWrapper
GoogleProvider = AIProviderWrapper
LocalProvider = AIProviderWrapper

# Instancia global
ai_provider_manager = AIProviderManager()
