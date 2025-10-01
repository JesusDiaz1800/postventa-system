"""
AI Provider adapters for different AI services
"""
import json
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
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
    def analyze_image(self, image_data: bytes, image_type: str) -> Dict[str, Any]:
        """Analyze an image and return results"""
        pass
    
    @abstractmethod
    def generate_text(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate text based on prompt and context"""
        pass
    
    @abstractmethod
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        pass
    
    def is_available(self) -> bool:
        """Check if provider is available"""
        return self.enabled and bool(self.api_key)


class OpenAIAdapter(AIProviderAdapter):
    """Adapter for OpenAI API"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
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
                model="gpt-4o",
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
                model="gpt-4o",
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


class AnthropicAdapter(AIProviderAdapter):
    """Adapter for Anthropic Claude API"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
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
                model="claude-3-opus-20240229",
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
                model="claude-3-opus-20240229",
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
    """Adapter for Google Gemini API"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro-vision')
        except ImportError:
            logger.error("Google Generative AI library not installed")
            self.model = None
    
    def analyze_image(self, image_data: bytes, image_type: str) -> Dict[str, Any]:
        """Analyze image using Google Gemini API"""
        if not self.model:
            return {'error': 'Google Gemini client not available'}
        
        try:
            import io
            from PIL import Image
            
            image = Image.open(io.BytesIO(image_data))
            
            prompt = "Analiza esta imagen de un producto industrial (tubería, accesorio, llave) y proporciona: 1) Una descripción detallada de lo que ves, 2) Tres posibles causas técnicas del problema observado, ordenadas por probabilidad, 3) Recomendaciones de inspección adicional. Responde en español y en formato JSON."
            
            response = self.model.generate_content([prompt, image])
            
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
            logger.error(f"Google Gemini image analysis error: {str(e)}")
            return {'error': str(e)}
    
    def generate_text(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate text using Google Gemini API"""
        if not self.model:
            return {'error': 'Google Gemini client not available'}
        
        try:
            response = self.model.generate_content(prompt)
            content = response.text
            tokens_used = response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
            
            return {
                'success': True,
                'text': content,
                'tokens_used': tokens_used,
                'provider': 'google'
            }
            
        except Exception as e:
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
        from .models import AIProvider
        
        # Get providers from database
        db_providers = AIProvider.objects.filter(enabled=True).order_by('priority')
        
        for provider in db_providers:
            config = {
                'name': provider.name,
                'api_key': provider.api_key_encrypted,  # TODO: Decrypt
                'enabled': provider.enabled,
                'priority': provider.priority
            }
            
            if provider.name == 'openai':
                self.providers['openai'] = OpenAIAdapter(config)
            elif provider.name == 'anthropic':
                self.providers['anthropic'] = AnthropicAdapter(config)
            elif provider.name == 'google':
                self.providers['google'] = GoogleAdapter(config)
            elif provider.name == 'local':
                self.providers['local'] = LocalAdapter(config)
    
    def analyze_image(self, image_data: bytes, image_type: str) -> Dict[str, Any]:
        """Analyze image using available providers"""
        start_time = time.time()
        
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
                        continue
                except AIProvider.DoesNotExist:
                    continue
            
            try:
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
                        except AIProvider.DoesNotExist:
                            pass
                    
                    return result
                
            except Exception as e:
                logger.error(f"Provider {provider_name} failed: {str(e)}")
                continue
        
        # If all providers failed, return error
        return {
            'error': 'Todos los proveedores de IA no están disponibles. Intente nuevamente más tarde.',
            'processing_time': time.time() - start_time
        }
    
    def generate_text(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate text using available providers"""
        start_time = time.time()
        
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
                    
                    return result
                
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
# orchestrator = AIOrchestrator()  # Comentado temporalmente para migraciones
