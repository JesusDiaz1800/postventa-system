"""
Servicio para integración con Google Gemini AI
Optimizado para análisis de laboratorio con gestión de cuotas
"""
import os
from django.conf import settings
from django.core.cache import cache
import logging
import hashlib
import json
from typing import Dict, Any, Optional

# Importación condicional de Google Generative AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_AVAILABLE = False
    logging.warning("Google Generative AI no está disponible. Instalar con: pip install google-generativeai")

logger = logging.getLogger(__name__)

class GeminiService:
    """
    Servicio para interactuar con la API de Gemini AI
    Optimizado para análisis de laboratorio con gestión de cuotas
    """
    
    def __init__(self):
        """Inicializar el servicio con la API key"""
        if not GEMINI_AVAILABLE:
            raise ImportError("Google Generative AI no está disponible. Instalar con: pip install google-generativeai")
        
        self.api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if not self.api_key:
            # Intentar cargar desde variables de entorno
            self.api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.api_key or self.api_key == 'your-gemini-api-key-here':
            raise ValueError("GEMINI_API_KEY no está configurada en settings o variables de entorno")
        
        # Configurar el SDK
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.cache_timeout = 3600  # 1 hora de cache
        logger.info("GeminiService inicializado correctamente")
    
    def _get_cache_key(self, content: str, analysis_type: str) -> str:
        """Generar clave de cache única"""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        return f"gemini_{analysis_type}_{content_hash}"
    
    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """Obtener respuesta desde cache"""
        return cache.get(cache_key)
    
    def _cache_response(self, cache_key: str, response: str) -> None:
        """Guardar respuesta en cache"""
        cache.set(cache_key, response, self.cache_timeout)
    
    def generate_content(self, prompt: str, max_tokens: int = None, use_cache: bool = True) -> str:
        """
        Generar contenido usando Gemini AI con cache
        
        Args:
            prompt (str): El prompt para enviar a Gemini
            max_tokens (int, optional): Número máximo de tokens en la respuesta
            use_cache (bool): Si usar cache o no
            
        Returns:
            str: La respuesta generada por Gemini
        """
        try:
            # Verificar cache si está habilitado
            if use_cache:
                cache_key = self._get_cache_key(prompt, "general")
                cached_response = self._get_cached_response(cache_key)
                if cached_response:
                    logger.info("Respuesta obtenida desde cache")
                    return cached_response
            
            logger.info(f"Enviando prompt a Gemini: {prompt[:100]}...")
            
            # Configurar parámetros de generación
            generation_config = {}
            if max_tokens:
                generation_config['max_output_tokens'] = max_tokens
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config if generation_config else None
            )
            
            # Guardar en cache si está habilitado
            if use_cache:
                self._cache_response(cache_key, response.text)
            
            logger.info("Respuesta recibida de Gemini exitosamente")
            return response.text
            
        except Exception as e:
            logger.error(f"Error al generar contenido con Gemini: {e}")
            raise
    
    def analyze_real_image(self, image_file, analysis_type: str = 'comprehensive_technical_analysis', 
                          description: str = '', context: str = '') -> Dict[str, Any]:
        """
        Analizar imagen real de falla en tuberías o accesorios
        
        Args:
            image_file: Archivo de imagen subido
            analysis_type (str): Tipo de análisis a realizar
            description (str): Descripción adicional del contexto
            context (str): Contexto adicional del análisis
            
        Returns:
            dict: Análisis detallado de la imagen
        """
        import time
        import uuid
        from PIL import Image
        import io
        
        start_time = time.time()
        analysis_id = str(uuid.uuid4())
        
        try:
            # Leer y procesar la imagen
            image_data = image_file.read()
            image_file.seek(0)  # Resetear el puntero del archivo
            
            # Crear objeto PIL Image
            pil_image = Image.open(io.BytesIO(image_data))
            
            # Convertir a formato compatible con Gemini
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Redimensionar si es muy grande (máximo 1024x1024)
            max_size = 1024
            if pil_image.width > max_size or pil_image.height > max_size:
                pil_image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Convertir a bytes para Gemini
            img_byte_arr = io.BytesIO()
            pil_image.save(img_byte_arr, format='JPEG', quality=85)
            img_byte_arr = img_byte_arr.getvalue()
            
            # Crear prompt para análisis
            prompt = f"""
            Como experto en análisis de fallas de tuberías y accesorios industriales, 
            analiza esta imagen y proporciona un análisis técnico detallado.
            
            CONTEXTO: {context if context else 'Análisis de falla en sistema de tuberías'}
            DESCRIPCIÓN ADICIONAL: {description if description else 'Ninguna'}
            
            Proporciona tu análisis en el siguiente formato JSON:
            {{
                "observations": "Descripción detallada de lo que observas en la imagen",
                "possible_causes": ["Lista de posibles causas técnicas identificadas"],
                "recommendations": ["Recomendaciones técnicas específicas"],
                "corrective_actions": ["Acciones correctivas sugeridas"],
                "severity_level": "Baja/Media/Alta/Crítica",
                "material_identification": "Identificación del material o componente",
                "failure_type": "Tipo específico de falla observada",
                "environmental_factors": "Factores ambientales que pudieron contribuir",
                "technical_notes": "Notas técnicas adicionales"
            }}
            
            Sé técnico, preciso y profesional en tu análisis. Enfócate en aspectos técnicos 
            observables y proporciona recomendaciones prácticas.
            """
            
            # Usar el modelo de visión de Gemini
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Preparar contenido con imagen y texto
            content = [
                {
                    "mime_type": "image/jpeg",
                    "data": img_byte_arr
                },
                prompt
            ]
            
            logger.info(f"Enviando imagen a Gemini para análisis (ID: {analysis_id})")
            
            # Generar análisis
            response = model.generate_content(content)
            
            processing_time = round(time.time() - start_time, 2)
            
            # Intentar parsear como JSON
            try:
                analysis = json.loads(response.text)
            except json.JSONDecodeError:
                # Si no es JSON válido, crear estructura manual
                analysis = {
                    "observations": response.text[:300] + "...",
                    "possible_causes": ["Análisis detallado en proceso"],
                    "recommendations": ["Revisar análisis completo"],
                    "corrective_actions": ["Implementar monitoreo continuo"],
                    "severity_level": "Media",
                    "material_identification": "Por determinar",
                    "failure_type": "Análisis general",
                    "environmental_factors": "Por evaluar",
                    "technical_notes": "Análisis técnico en proceso"
                }
            
            return {
                'success': True,
                'analysis': analysis,
                'confidence_score': 0.85,  # Score estimado
                'processing_time': processing_time,
                'tokens_used': len(response.text) // 4,  # Estimación aproximada
                'model_used': 'gemini-1.5-flash',
                'analysis_id': analysis_id
            }
            
        except Exception as e:
            logger.error(f"Error al analizar imagen real: {e}")
            return {
                'success': False,
                'error': str(e),
                'analysis': None,
                'processing_time': round(time.time() - start_time, 2),
                'analysis_id': analysis_id
            }

    def analyze_failure_image(self, image_description: str) -> Dict[str, Any]:
        """
        Analizar imagen de falla en tuberías o accesorios
        
        Args:
            image_description (str): Descripción de la imagen o análisis visual
            
        Returns:
            dict: Análisis detallado de la falla
        """
        cache_key = self._get_cache_key(image_description, "image_analysis")
        
        try:
            # Verificar cache
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                return json.loads(cached_response)
            
            prompt = f"""
            Como experto en análisis de fallas de tuberías y accesorios industriales, 
            analiza la siguiente descripción de imagen y proporciona un análisis técnico detallado:
            
            DESCRIPCIÓN DE LA IMAGEN: {image_description}
            
            Proporciona tu análisis en el siguiente formato JSON:
            {{
                "tipo_falla": "Clasificación específica del tipo de falla observada",
                "descripcion_visual": "Descripción detallada de lo que se observa en la imagen",
                "posibles_causas": ["Lista de posibles causas técnicas"],
                "severidad": "Baja/Media/Alta/Crítica",
                "recomendaciones_inmediatas": ["Acciones inmediatas recomendadas"],
                "recomendaciones_preventivas": ["Medidas preventivas a largo plazo"],
                "material_afectado": "Tipo de material o componente afectado",
                "condiciones_ambientales": "Factores ambientales que pudieron contribuir"
            }}
            
            Sé técnico, preciso y profesional en tu análisis.
            """
            
            response = self.generate_content(prompt, max_tokens=800)
            
            # Intentar parsear como JSON
            try:
                analysis = json.loads(response)
            except json.JSONDecodeError:
                # Si no es JSON válido, crear estructura manual
                analysis = {
                    "tipo_falla": "Análisis general",
                    "descripcion_visual": response[:200] + "...",
                    "posibles_causas": ["Análisis detallado requerido"],
                    "severidad": "Media",
                    "recomendaciones_inmediatas": ["Revisar análisis completo"],
                    "recomendaciones_preventivas": ["Implementar monitoreo continuo"],
                    "material_afectado": "Por determinar",
                    "condiciones_ambientales": "Por evaluar"
                }
            
            # Guardar en cache
            self._cache_response(cache_key, json.dumps(analysis))
            
            return {
                'success': True,
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"Error al analizar imagen de falla: {e}")
            return {
                'success': False,
                'error': str(e),
                'analysis': None
            }
    
    def professionalize_problem_description(self, problem_description: str) -> Dict[str, Any]:
        """
        Redactar problema de forma profesional y justificada
        
        Args:
            problem_description (str): Descripción original del problema
            
        Returns:
            dict: Descripción profesional y justificada
        """
        cache_key = self._get_cache_key(problem_description, "professional_redaction")
        
        try:
            # Verificar cache
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                return json.loads(cached_response)
            
            prompt = f"""
            Como redactor técnico especializado en documentación de laboratorio, 
            reformula la siguiente descripción de problema de manera profesional, 
            técnica y justificada, evitando términos como "falla", "error" o "problema":
            
            DESCRIPCIÓN ORIGINAL: {problem_description}
            
            Reformula el texto considerando:
            1. Usar terminología técnica apropiada
            2. Enfocarse en "observaciones", "hallazgos" o "condiciones"
            3. Justificar técnicamente la situación
            4. Evitar atribuir culpa directa
            5. Mantener un tono profesional y constructivo
            6. Incluir contexto técnico relevante
            
            Proporciona tu respuesta en el siguiente formato JSON:
            {{
                "titulo_profesional": "Título técnico apropiado",
                "descripcion_redactada": "Descripción reformulada de manera profesional",
                "justificacion_tecnica": "Justificación técnica de la situación",
                "contexto_operacional": "Contexto operacional relevante",
                "terminologia_utilizada": ["Lista de términos técnicos utilizados"],
                "nivel_urgencia": "Bajo/Medio/Alto",
                "recomendacion_redaccion": "Sugerencia adicional para la redacción"
            }}
            
            El texto debe sonar como un informe técnico profesional, no como un reporte de falla.
            """
            
            response = self.generate_content(prompt, max_tokens=600)
            
            # Intentar parsear como JSON
            try:
                redaction = json.loads(response)
            except json.JSONDecodeError:
                # Si no es JSON válido, crear estructura manual
                redaction = {
                    "titulo_profesional": "Observación Técnica",
                    "descripcion_redactada": response[:300] + "...",
                    "justificacion_tecnica": "Análisis técnico en proceso",
                    "contexto_operacional": "Contexto operacional por definir",
                    "terminologia_utilizada": ["Técnico", "Profesional"],
                    "nivel_urgencia": "Medio",
                    "recomendacion_redaccion": "Revisar redacción completa"
                }
            
            # Guardar en cache
            self._cache_response(cache_key, json.dumps(redaction))
            
            return {
                'success': True,
                'redaction': redaction
            }
            
        except Exception as e:
            logger.error(f"Error al redactar problema: {e}")
            return {
                'success': False,
                'error': str(e),
                'redaction': None
            }
    
    def get_analysis_statistics(self) -> Dict[str, Any]:
        """
        Obtener estadísticas de uso del servicio (sin exponer información sensible)
        
        Returns:
            dict: Estadísticas básicas del servicio
        """
        return {
            'service_status': 'Operativo',
            'cache_enabled': True,
            'cache_timeout': self.cache_timeout,
            'model': 'gemini-1.5-flash',
            'optimization': 'Cache habilitado para optimizar cuotas'
        }

# Instancia global del servicio
gemini_service = None

def get_gemini_service():
    """
    Obtener la instancia del servicio Gemini (singleton)
    """
    global gemini_service
    if gemini_service is None:
        if not GEMINI_AVAILABLE:
            raise ImportError("Google Generative AI no está disponible. Instalar con: pip install google-generativeai")
        gemini_service = GeminiService()
    return gemini_service