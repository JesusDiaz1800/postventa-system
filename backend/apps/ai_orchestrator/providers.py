from __future__ import annotations
import json
import time
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class AIProviderAdapter(ABC):
    """Abstract base class for AI provider adapters"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        self.config = provider_config
        self.name = provider_config['name']
        self.api_key = provider_config.get('api_key', '')
        self.enabled = provider_config.get('enabled', True)
    
    @abstractmethod
    def analyze_image(self, image_data: bytes, image_type: str) -> dict[str, Any]:
        """Analyze an image and return results"""
        pass
    
    @abstractmethod
    def generate_text(self, prompt: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Generate text based on prompt and context"""
        pass
    
    @abstractmethod
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        pass
    
    def analyze_document(self, document_text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Análisis genérico de texto de documento para extracción de datos"""
        prompt = f"Analiza el siguiente texto de un documento de incidencia y extrae los datos en formato JSON:\n\n{document_text}"
        return self.generate_text(prompt, context)

    def analyze_file(self, file_bytes: bytes, mime_type: str, document_text: str = "") -> Dict[str, Any]:
        """Análisis multimodal de archivo (si el proveedor lo soporta)"""
        # Fallback por defecto a análisis de texto si no hay soporte multimodal
        if document_text:
            return self.analyze_document(document_text)
        return {'error': 'Este proveedor no soporta análisis multimodal de archivos'}
    
    def is_available(self) -> bool:
        """Check if provider is available"""
        return self.enabled and bool(self.api_key)





class GoogleAdapter(AIProviderAdapter):
    """Adapter for Google GenAI SDK (v2025 Standard)"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        self._service = None
        
    @property
    def service(self):
        """Lazy load GeminiService"""
        if self._service is None:
            try:
                from apps.ai.gemini_service import get_gemini_service
                self._service = get_gemini_service()
            except Exception as e:
                logger.error(f"Failed to initialize GeminiService: {e}")
        return self._service

    
    def analyze_image(self, image_data: bytes, image_type: str) -> Dict[str, Any]:
        """Analyze image using unified GeminiService"""
        service = self.service
        if not service:
            return {'error': 'GeminiService not available'}
        
        try:
            # We use the advanced analyze_real_image for better results
            result = service.analyze_real_image(
                image_files=[image_data],
                analysis_type='orchestrator_inspection',
                description='Análisis técnico detallado de la imagen para auditoría de calidad.'
            )
            
            if result.get('success'):
                # Map GeminiService format to Orchestrator format
                analysis = result.get('analysis', {})
                return {
                    'success': True,
                    'data': {
                        'description': analysis.get('observations', 'Sin observaciones'),
                        'possible_causes': analysis.get('possible_causes', []),
                        'recommendations': analysis.get('recommendations', []),
                        'severity': analysis.get('severity_level', 'Media')
                    },
                    'tokens_used': result.get('tokens_used', 2000),
                    'provider': 'google'
                }
            
            return {'error': result.get('error', 'Error en el análisis de imagen')}
            
        except Exception as e:
            error_msg = str(e).lower()
            if "429" in error_msg or "quota" in error_msg or "resource_exhausted" in error_msg:
                 return {'error': 'Quota Exceeded', 'code': 429}
            logger.error(f"Google Gemini analysis error: {str(e)}")
            return {'error': str(e)}

    
    def generate_text(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate text using simplified generate_content from GeminiService"""
        service = self.service
        if not service:
            return {'error': 'GeminiService not available'}
        
        try:
            # GeminiService.generate_content handles cache and fallbacks internally
            content = service.generate_content(prompt, use_cache=True)
            
            return {
                'success': True,
                'text': content,
                'tokens_used': len(content) // 4, # Rough estimate
                'provider': 'google'
            }
            
        except Exception as e:
            error_msg = str(e).lower()
            if "429" in error_msg or "quota" in error_msg or "resource_exhausted" in error_msg:
                 return {'error': 'Quota Exceeded', 'code': 429}
            
            logger.error(f"Google Gemini text generation error: {str(e)}")
            return {'error': str(e)}

    def estimate_tokens(self, text: str) -> int:

        """Estimate token count (rough approximation)"""
        return len(text.split()) * 1.3


class LocalAdapter(AIProviderAdapter):
    """Adapter for local AI models (fallback) using Ollama"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        self.enabled = True  # Local models are always available
        try:
            from apps.ai.ollama_service import OllamaService
            self.ollama = OllamaService()
        except ImportError:
            logger.error("OllamaService not found. Standard Local fallback will be used.")
            self.ollama = None
    
    def is_available(self) -> bool:
        """Local adapter is always available as the ultimate fallback"""
        return True
    
    def analyze_image(self, image_data: bytes, image_type: str) -> Dict[str, Any]:
        """Analyze image using Ollama (Llama 3.2 Vision)"""
        if self.ollama:
            try:
                result = self.ollama.analyze_real_image(
                    image_files=[image_data],
                    analysis_type='standard_inspection',
                    description='Analiza esta imagen industrial e identifica posibles problemas o estados del producto.',
                )
                if result.get('success'):
                    # Transform Ollama result to orchestrator format
                    analysis = result.get('analysis', {})
                    return {
                        'success': True,
                        'data': {
                            'description': analysis.get('observations', 'Sin observaciones'),
                            'possible_causes': analysis.get('possible_causes', []),
                            'recommendations': analysis.get('recommendations', []),
                            'severity': analysis.get('severity_level', 'Media')
                        },
                        'tokens_used': 0,
                        'provider': 'ollama-local'
                    }
            except Exception as e:
                logger.error(f"Ollama local analysis failed: {e}")

        # Basic image analysis using heuristics (Final Fallback)
        analysis_data = {
            'description': 'Análisis heurístico básico (Ollama no disponible)',
            'possible_causes': [
                'Posible defecto de fabricación',
                'Daño durante transporte o almacenamiento'
            ],
            'recommendations': [
                'Revisar especificaciones del producto',
                'Consultar con técnico especializado'
            ]
        }
        
        return {
            'success': True,
            'data': analysis_data,
            'tokens_used': 0,
            'provider': 'local-heuristics'
        }
    
    def generate_text(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate text using Ollama (Local AI)"""
        if self.ollama:
            try:
                # Use standard generate_content from OllamaService
                # Increment timeout for local generation under load
                content = self.ollama.generate_content(prompt, timeout=90)
                if content:
                    return {
                        'success': True,
                        'text': content,
                        'tokens_used': 0,
                        'provider': 'ollama-local'
                    }
            except Exception as e:
                logger.error(f"Ollama local text generation failed: {e}")

        # Basic text generation using templates (Final Fallback)
        try:
            if 'cliente' in prompt.lower():
                text = "Estimado cliente, hemos revisado la situación reportada y estamos trabajando en una solución (IA Local básica)."
            elif 'proveedor' in prompt.lower():
                text = "Estimado proveedor, solicitamos su colaboración para revisar el lote mencionado (IA Local básica)."
            else:
                text = "Respuesta generada por el sistema local de emergencia. Los servicios de IA en la nube no están disponibles actualmente."
            
            return {
                'success': True,
                'text': text,
                'tokens_used': 0,
                'provider': 'local-heuristics'
            }
            
        except Exception as e:
            logger.error(f"Heuristic fallback generation failed: {str(e)}")
            return {'error': str(e)}
    
    def analyze_document(self, document_text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Análisis simulado pero estructurado para documentos (Fallback Gratuito)"""
        import json
        from django.utils import timezone
        
        # Intentar extraer algo de texto básico
        cliente = "No detectado (IA Local)"
        if "cliente" in document_text.lower():
            parts = document_text.lower().split("cliente")
            if len(parts) > 1:
                cliente = parts[1].split("\n")[0].strip(": \t")[:50]

        analysis_data = {
            "cliente": cliente,
            "rut_cliente": None,
            "obra": "Obra no detectada",
            "proveedor": "Polifusión (Default)",
            "fecha_incidente": timezone.now().date().isoformat(),
            "descripcion_breve": "Extracción básica local (Sin cuota de IA)",
            "descripcion_completa": document_text[:500] if document_text else "Sin contenido",
            "categoria": "Otro",
            "prioridad": "media",
            "tecnico": "Sistema Local",
            "producto_detectado": "Genérico"
        }
        
        return {
            'success': True,
            'data': json.dumps(analysis_data, ensure_ascii=False),
            'provider': 'local',
            'tokens_used': 0
        }

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        return len(text.split()) * 1.3


class AIOrchestrator:
    """Main orchestrator for AI providers"""
    
    def __init__(self):
        self.providers = {}
        self._load_providers()
    
    def _load_providers(self):
        """Load and initialize AI providers"""
        try:
            from .models import AIProvider
            # Get providers from database
            db_providers = AIProvider.objects.filter(enabled=True).order_by('priority')
            
            if not db_providers.exists():
                from apps.core.thread_local import get_current_country
                country = get_current_country() or 'default'
                logger.warning(f"No explicit AI providers found in DB ({country}), using defaults.")
                
            for provider in db_providers:

                logger.debug(f"Loading provider: {provider.name}")
                config = {
                    'name': provider.name,
                    'api_key': provider.get_api_key(),
                    'enabled': provider.enabled,
                    'priority': provider.priority
                }
                
                try:
                    if provider.name == 'google':
                        self.providers['google'] = GoogleAdapter(config)
                    elif provider.name == 'local':
                        self.providers['local'] = LocalAdapter(config)
                except Exception as provider_error:
                    logger.error(f"Failed to load provider {provider.name}: {provider_error}")
                    # Continue to next provider instead of failing the whole load
        except Exception as e:
            # Silently fail if DB is not ready (e.g. during migrations)
            logger.warning(f"AI Providers could not be loaded: {e}")
        
        # ENSURE LOCAL FALLBACK: Always have a local provider as last resort
        if 'local' not in self.providers:
            logger.info("Initializing default local fallback provider")
            self.providers['local'] = LocalAdapter({
                'name': 'local',
                'api_key': '',
                'enabled': True,
                'priority': 99
            })

    def analyze_document(self, document_text: str, file_bytes: bytes = None, mime_type: str = None) -> Dict[str, Any]:
        """
        Analiza un documento intentando varios proveedores si falla por cuota.
        Prioriza Gemini para archivos si se proporcionan file_bytes.
        """
        # 1. Intentar con Gemini si hay archivo (multimodal)
        if file_bytes and 'google' in self.providers:
            provider = self.providers['google']
            if provider.is_available() and self._check_db_quota('google'):
                result = provider.analyze_file(file_bytes, mime_type, document_text)
                if result.get('success'):
                    self._consume_db_quota('google', result.get('tokens_used', 2000))
                    return result
                if result.get('code') == 429:
                    logger.warning("Gemini Quota Exceeded. Falling back to text-based analysis with other providers.")

        # 2. Fallback a análisis basado en texto con otros proveedores (incluyendo Gemini si solo falló multimodal)
        for name in ['google', 'local']:
            if name not in self.providers:
                continue
            
            provider = self.providers[name]
            if not provider.is_available() or not self._check_db_quota(name):
                continue
                
            result = provider.analyze_document(document_text)
            if result.get('success'):
                self._consume_db_quota(name, result.get('tokens_used', 1000))
                return result
            
            
        # 3. Determinar tiempo de reinicio si hubo fallos de cuota
        try:
            from .models import AIProvider
            # Usar Gemini como referencia para el tiempo de reinicio (o el local si todos fallaron)
            p = AIProvider.objects.get(name='google')
            next_reset = p.get_next_reset_time().isoformat()
        except:
            next_reset = None
            
        return {
            'error': 'Todos los proveedores de IA fallaron o agotaron su cuota',
            'code': 429 if 'google' in self.providers else 500,
            'next_reset': next_reset
        }

    def _check_db_quota(self, provider_name: str) -> bool:
        from .models import AIProvider
        try:
            p = AIProvider.objects.get(name=provider_name)
            return p.has_quota()
        except:
            return True # Si no hay DB, permitir

    def _consume_db_quota(self, provider_name: str, tokens: int):
        from .models import AIProvider
        try:
            p = AIProvider.objects.get(name=provider_name)
            p.consume_quota(tokens)
        except:
            pass
    
    def analyze_image(self, image_data: bytes, image_type: str) -> Dict[str, Any]:
        """Analyze image using available providers"""
        start_time = time.time()
        quota_warning = None
        
        # Try providers in priority order
        for provider_name, provider in self.providers.items():
            if not provider.is_available():
                continue
            
            # Check quota for non-local providers
            if provider_name != 'local':
                from .models import AIProvider
                try:
                    db_provider = AIProvider.objects.get(name=provider_name)
                    if not db_provider.has_quota():
                        logger.warning(f"Provider {provider_name} quota exceeded")
                        if not quota_warning:
                            quota_warning = "⚠️ Sistema operando con capacidad reducida (Cuota IA agotada). Respuesta generada localmente."
                        continue
                except AIProvider.DoesNotExist:
                    continue
            
            try:
                logger.info(f"Attempting analysis with provider: {provider_name}")
                result = provider.analyze_image(image_data, image_type)
                
                if result.get('success'):
                    processing_time = time.time() - start_time
                    result['processing_time'] = processing_time
                    
                    # Update quota usage
                    if provider_name != 'local' and 'tokens_used' in result:
                        from .models import AIProvider
                        try:
                            db_provider = AIProvider.objects.get(name=provider_name)
                            db_provider.consume_quota(result['tokens_used'])
                            logger.info(f"Analysis successful with {provider_name}. Tokens: {result['tokens_used']}")
                        except AIProvider.DoesNotExist:
                            pass
                    
                    # Inject warning if we are in local mode but had quota failures
                    if provider_name == 'local' and quota_warning:
                        if 'data' in result and isinstance(result['data'], dict):
                            result['data']['warning'] = quota_warning
                            # Also append to description for visibility
                            if 'description' in result['data']:
                                result['data']['description'] += f"\n\n[{quota_warning}]"
                    
                    return result
                
                # Handle Explicit Quota Error from Adapter
                elif result.get('code') == 429:
                    logger.warning(f"Provider {provider_name} returned Quota Exceeded (429)")
                    if not quota_warning:
                        quota_warning = "⚠️ Sistema operando con capacidad reducida (Cuota IA agotada). Respuesta generada localmente."
                
                else:
                    logger.error(f"Provider {provider_name} returned error: {result.get('error')}")
                
            except Exception as e:
                logger.error(f"Provider {provider_name} failed with exception: {str(e)}", exc_info=True)
                continue
        
        # If all providers failed, return error
        return {
            'success': False,
            'error': 'Capacidad de IA agotada o servicios no disponibles localmente.',
            'processing_time': time.time() - start_time
        }
    
    def generate_text(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate text using available providers with robust error handling"""
        start_time = time.time()
        quota_warning = None
        
        # Try providers in priority order
        for provider_name, provider in self.providers.items():
            if not provider.is_available():
                continue
            
            # Check quota for non-local providers
            if provider_name != 'local':
                from .models import AIProvider
                try:
                    db_provider = AIProvider.objects.get(name=provider_name)
                    if not db_provider.has_quota():
                        logger.warning(f"Provider {provider_name} quota exceeded in DB check")
                        if not quota_warning:
                            quota_warning = "⚠️ Sistema operando con capacidad reducida (Cuota IA agotada). Respuesta generada localmente."
                        continue
                except AIProvider.DoesNotExist:
                    pass
            
            try:
                logger.info(f"AI Orchestrator: Generating text with {provider_name}...")
                result = provider.generate_text(prompt, context)
                
                if result.get('success'):
                    processing_time = time.time() - start_time
                    result['processing_time'] = processing_time
                    
                    # Update quota usage
                    if provider_name != 'local' and 'tokens_used' in result:
                        from .models import AIProvider
                        try:
                            db_provider = AIProvider.objects.get(name=provider_name)
                            db_provider.consume_quota(result['tokens_used'])
                        except Exception as quota_err:
                            logger.error(f"Error updating quota for {provider_name}: {quota_err}")
                            pass

                    # Inject warning if we are in local mode but had quota failures
                    if provider_name == 'local' and quota_warning:
                        if 'text' in result:
                            result['text'] += f"\n\n[{quota_warning}]"
                    
                    logger.info(f"AI Orchestrator: Text generated successfully with {provider_name} in {processing_time:.2f}s")
                    return result
                
                # Handle Explicit Quota Error from Adapter
                elif result.get('code') == 429:
                    logger.warning(f"Provider {provider_name} returned Quota Exceeded (429)")
                    if not quota_warning:
                        quota_warning = "⚠️ Sistema operando con capacidad reducida (Cuota IA agotada). Respuesta generada localmente."
                else:
                    logger.error(f"Provider {provider_name} returned error status: {result.get('error')}")
                
            except Exception as e:
                logger.error(f"Provider {provider_name} failed with unhandled exception: {str(e)}", exc_info=True)
                continue
        
        # Final fallback error if everything failed
        logger.error("AI Orchestrator: All providers failed to generate text.")
        return {
            'success': False,
            'error': 'Generación de texto fallida (Servicios fuera de línea o sin cuota).',
            'processing_time': time.time() - start_time
        }

    
    def get_provider_status(self) -> List[Dict[str, Any]]:
        """Get status of all providers"""
        status_list = []
        
        for provider_name, provider in self.providers.items():
            from .models import AIProvider
            try:
                db_provider = AIProvider.objects.get(name=provider_name)
                status_list.append({
                    'name': provider_name,
                    'enabled': provider.enabled,
                    'available': provider.is_available(),
                    'has_quota': db_provider.has_quota(),
                    'tokens_used_today': db_provider.tokens_used_today,
                    'tokens_quota': db_provider.daily_quota_tokens,
                    'calls_made_today': db_provider.calls_made_today,
                    'calls_quota': db_provider.daily_quota_calls,
                    'next_reset': db_provider.get_next_reset_time().isoformat()
                })
            except AIProvider.DoesNotExist:
                status_list.append({
                    'name': provider_name,
                    'enabled': False,
                    'available': False,
                    'error': 'Provider not found in database'
                })
        
        return status_list


# Global orchestrator instance
_orchestrator = None

def get_orchestrator():
    """Retorna la instancia global del orquestador, inicializándola si es necesario"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AIOrchestrator()
    return _orchestrator
