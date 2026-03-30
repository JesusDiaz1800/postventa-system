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


class OpenAIAdapter(AIProviderAdapter):
    """Adapter for OpenAI API"""
    
    def __init__(self, provider_config: dict[str, Any]):
        super().__init__(provider_config)
        try:
            import openai
            import httpx
            # Fix for httpx 0.28+ breaking older openai versions due to 'proxies' param removal
            self.client = openai.OpenAI(
                api_key=self.api_key,
                http_client=httpx.Client()
            )
        except ImportError:
            logger.error("OpenAI library not installed")
            self.client = None
    
    def analyze_image(self, image_data: bytes, image_type: str) -> Dict[str, Any]:
        """Analyze image using OpenAI Vision API"""
        if not self.client:
            return {'error': 'OpenAI client not available'}
        
        try:
            import base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            response = self.client.chat.completions.create(
                model=getattr(settings, 'AI_OPENAI_MODEL', 'gpt-4o'),
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analiza esta imagen de un producto industrial (tubería, accesorio, llave) y proporciona: 1) Una descripción detallada de lo que ves, 2) Tres posibles causas técnicas del problema observado, ordenadas por probabilidad, 3) Recomendaciones de inspección adicional. Responde en español y en formato JSON."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{image_type};base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            # Try to parse JSON response
            try:
                analysis_data = json.loads(content)
            except json.JSONDecodeError:
                # If not JSON, create structured response
                analysis_data = {
                    'description': content,
                    'possible_causes': [],
                    'recommendations': []
                }
            
            return {
                'success': True,
                'data': analysis_data,
                'tokens_used': tokens_used,
                'provider': 'openai'
            }
            
        except Exception as e:
            logger.error(f"OpenAI image analysis error: {str(e)}")
            return {'error': str(e)}
    
    def generate_text(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate text using OpenAI API"""
        if not self.client:
            return {'error': 'OpenAI client not available'}
        
        try:
            messages = [{"role": "user", "content": prompt}]
            
            response = self.client.chat.completions.create(
                model=getattr(settings, 'AI_OPENAI_MODEL', 'gpt-4o'),
                messages=messages,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            return {
                'success': True,
                'text': content,
                'tokens_used': tokens_used,
                'provider': 'openai'
            }
            
        except Exception as e:
            logger.error(f"OpenAI text generation error: {str(e)}")
            return {'error': str(e)}
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        return len(text.split()) * 1.3  # Rough estimate


    def analyze_document(self, document_text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Análisis de documento optimizado para Gemini"""
        prompt = f"Analiza el siguiente texto de un documento de incidencia y extrae los datos en formato JSON:\n\n{document_text}"
        return self.generate_text(prompt, context)

    def analyze_file(self, file_bytes: bytes, mime_type: str, document_text: str = "") -> Dict[str, Any]:
        """Análisis multimodal usando Gemini"""
        if not self.client:
            return {'error': 'Gemini client not available'}
        
        try:
            prompt = "Analiza este documento y extrae la información técnica en formato JSON."
            if document_text:
                prompt += f"\nContexto del texto extraído:\n{document_text}"
            
            content = [
                {"mime_type": mime_type, "data": file_bytes},
                prompt
            ]
            
            response = self.client.generate_content(content)
            return {
                'success': True,
                'data': response.text,
                'provider': 'google'
            }
        except Exception as e:
            if "429" in str(e):
                from .models import AIProvider
                try:
                    p = AIProvider.objects.get(name='google')
                    next_reset = p.get_next_reset_time().isoformat()
                except:
                    next_reset = None
                return {'error': 'Quota Exceeded', 'code': 429, 'next_reset': next_reset}
            return {'error': str(e)}

class AnthropicAdapter(AIProviderAdapter):
    """Adapter for Anthropic Claude API"""
    
    def __init__(self, provider_config: dict[str, Any]):
        super().__init__(provider_config)
        try:
            import anthropic
            import httpx
            # Fix for httpx 0.28+ breaking older anthropic versions due to 'proxies' param removal
            self.client = anthropic.Anthropic(
                api_key=self.api_key,
                http_client=httpx.Client()
            )
        except ImportError:
            logger.error("Anthropic library not installed")
            self.client = None
    
    def analyze_image(self, image_data: bytes, image_type: str) -> Dict[str, Any]:
        """Analyze image using Anthropic Claude API"""
        if not self.client:
            return {'error': 'Anthropic client not available'}
        
        try:
            import base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            response = self.client.messages.create(
                model=getattr(settings, 'AI_ANTHROPIC_MODEL', 'claude-3-5-sonnet-20240620'),
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analiza esta imagen de un producto industrial (tubería, accesorio, llave) y proporciona: 1) Una descripción detallada de lo que ves, 2) Tres posibles causas técnicas del problema observado, ordenadas por probabilidad, 3) Recomendaciones de inspección adicional. Responde en español y en formato JSON."
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": image_type,
                                    "data": base64_image
                                }
                            }
                        ]
                    }
                ]
            )
            
            content = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            
            # Try to parse JSON response
            try:
                analysis_data = json.loads(content)
            except json.JSONDecodeError:
                analysis_data = {
                    'description': content,
                    'possible_causes': [],
                    'recommendations': []
                }
            
            return {
                'success': True,
                'data': analysis_data,
                'tokens_used': tokens_used,
                'provider': 'anthropic'
            }
            
        except Exception as e:
            logger.error(f"Anthropic image analysis error: {str(e)}")
            return {'error': str(e)}
    
    def generate_text(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate text using Anthropic Claude API"""
        if not self.client:
            return {'error': 'Anthropic client not available'}
        
        try:
            response = self.client.messages.create(
                model=getattr(settings, 'AI_ANTHROPIC_MODEL', 'claude-3-5-sonnet-20240620'),
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            
            return {
                'success': True,
                'text': content,
                'tokens_used': tokens_used,
                'provider': 'anthropic'
            }
            
        except Exception as e:
            logger.error(f"Anthropic text generation error: {str(e)}")
            return {'error': str(e)}
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        return len(text.split()) * 1.3


class GoogleAdapter(AIProviderAdapter):
    """Adapter for Google GenAI SDK (v2025 Standard)"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            self.model_name = getattr(settings, 'AI_GOOGLE_MODEL', 'gemini-2.0-flash-exp')
        except ImportError:
            logger.error("Google GenAI SDK not installed")
            self.client = None
    
    def analyze_image(self, image_data: bytes, image_type: str) -> Dict[str, Any]:
        """Analyze image using Google Gemini API"""
        if not self.client:
            return {'error': 'Google Gemini client not available'}
        
        try:
            import io
            from PIL import Image
            from google.genai import types
            
            # Optimization: Resize image to max 1024px
            image = Image.open(io.BytesIO(image_data))
            if max(image.size) > 1024:
                image.thumbnail((1024, 1024))
            
            # Optimization: Compact prompt to save tokens
            prompt = """
            Rol: Auditor Calidad Industrial. Tarea: Análisis técnico imagen. Formato: JSON.
            JSON Schema:
            {
                "description": "Descripción técnica (materiales, anomalías)",
                "possible_causes": ["Causa 1", "Causa 2", "Causa 3"],
                "recommendations": ["Acción 1", "Acción 2", "Norma"]
            }
            Restricciones: Sin saludos. Vocabulario técnico preciso.
            """
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt, image],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            content = response.text
            tokens_used = response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
            
            # Try to parse JSON response
            try:
                analysis_data = json.loads(content)
            except json.JSONDecodeError:
                analysis_data = {
                    'description': content,
                    'possible_causes': [],
                    'recommendations': []
                }
            
            return {
                'success': True,
                'data': analysis_data,
                'tokens_used': tokens_used,
                'provider': 'google'
            }
            
        except Exception as e:
            # Check for Quota Error (429) via message string or attribute
            error_msg = str(e).lower()
            if "429" in error_msg or "quota" in error_msg or "resource_exhausted" in error_msg:
                 logger.warning("Gemini Quota Exceeded (429).")
                 return {'error': 'Quota Exceeded', 'code': 429}
                 
            logger.error(f"Google Gemini image analysis error: {str(e)}")
            return {'error': str(e)}
    
    def generate_text(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate text using Google Gemini API"""
        if not self.client:
            return {'error': 'Google Gemini client not available'}
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            content = response.text
            tokens_used = response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
            
            return {
                'success': True,
                'text': content,
                'tokens_used': tokens_used,
                'provider': 'google'
            }
            
        except Exception as e:
            # Check for Quota Error (429)
            error_msg = str(e).lower()
            if "429" in error_msg or "quota" in error_msg or "resource_exhausted" in error_msg:
                 return {'error': 'Quota Exceeded', 'code': 429}

            logger.error(f"Google Gemini text generation error: {str(e)}")
            return {'error': str(e)}
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        return len(text.split()) * 1.3


class LocalAdapter(AIProviderAdapter):
    """Adapter for local AI models (fallback)"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        self.enabled = True  # Local models are always available
    
    def is_available(self) -> bool:
        """Local adapter is always available as fallback"""
        return self.enabled
    
    def analyze_image(self, image_data: bytes, image_type: str) -> Dict[str, Any]:
        """Analyze image using local models (basic heuristics)"""
        try:
            # Basic image analysis using heuristics
            analysis_data = {
                'description': 'Análisis básico de imagen realizado con modelo local',
                'possible_causes': [
                    'Posible defecto de fabricación',
                    'Daño durante transporte o almacenamiento',
                    'Condiciones de instalación inadecuadas'
                ],
                'recommendations': [
                    'Revisar especificaciones del producto',
                    'Verificar condiciones de instalación',
                    'Consultar con técnico especializado'
                ]
            }
            
            return {
                'success': True,
                'data': analysis_data,
                'tokens_used': 0,
                'provider': 'local'
            }
            
        except Exception as e:
            logger.error(f"Local image analysis error: {str(e)}")
            return {'error': str(e)}
    
    def generate_text(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate text using local models (basic templates)"""
        try:
            # Basic text generation using templates
            if 'cliente' in prompt.lower():
                text = "Estimado cliente, hemos revisado la situación reportada y estamos trabajando en una solución."
            elif 'proveedor' in prompt.lower():
                text = "Estimado proveedor, solicitamos su colaboración para revisar el lote mencionado."
            else:
                text = "Texto generado con modelo local. Se recomienda revisión manual."
            
            return {
                'success': True,
                'text': text,
                'tokens_used': 0,
                'provider': 'local'
            }
            
        except Exception as e:
            logger.error(f"Local text generation error: {str(e)}")
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
            
            for provider in db_providers:
                logger.debug(f"Loading provider: {provider.name}")
                config = {
                    'name': provider.name,
                    'api_key': provider.get_api_key(),
                    'enabled': provider.enabled,
                    'priority': provider.priority
                }
                
                try:
                    if provider.name == 'openai':
                        self.providers['openai'] = OpenAIAdapter(config)
                    elif provider.name == 'anthropic':
                        self.providers['anthropic'] = AnthropicAdapter(config)
                    elif provider.name == 'google':
                        self.providers['google'] = GoogleAdapter(config)
                    elif provider.name == 'local':
                        self.providers['local'] = LocalAdapter(config)
                except Exception as provider_error:
                    logger.error(f"Failed to load provider {provider.name}: {provider_error}")
                    # Continue to next provider instead of failing the whole load
        except Exception as e:
            # Silently fail if DB is not ready (e.g. during migrations)
            logger.warning(f"AI Providers could not be loaded: {e}")

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
        for name in ['openai', 'anthropic', 'google', 'local']:
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
            'error': 'Todos los proveedores de IA no están disponibles. Intente nuevamente más tarde.',
            'processing_time': time.time() - start_time
        }
    
    def generate_text(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate text using available providers"""
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
                        except AIProvider.DoesNotExist:
                            pass

                    # Inject warning if we are in local mode but had quota failures
                    if provider_name == 'local' and quota_warning:
                        if 'text' in result:
                            result['text'] += f"\n\n[{quota_warning}]"
                    
                    return result
                
                # Handle Explicit Quota Error from Adapter
                elif result.get('code') == 429:
                    logger.warning(f"Provider {provider_name} returned Quota Exceeded (429)")
                    if not quota_warning:
                        quota_warning = "⚠️ Sistema operando con capacidad reducida (Cuota IA agotada). Respuesta generada localmente."
                
            except Exception as e:
                logger.error(f"Provider {provider_name} failed: {str(e)}")
                continue
        
        # If all providers failed, return error
        return {
            'error': 'Todos los proveedores de IA no están disponibles. Intente nuevamente más tarde.',
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
