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
from typing import Dict, Any, Optional, List

# Importación de Google Generative AI (nueva API)
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    types = None
    GEMINI_AVAILABLE = False
    logging.warning("Google Generative AI no está disponible. Instalar con: pip install google-genai")

logger = logging.getLogger(__name__)

class GeminiService:
    """
    Servicio para interactuar con la API de Gemini AI
    Optimizado para análisis de laboratorio con gestión de cuotas
    """
    
    def __init__(self):
        """Inicializar el servicio con la API key"""
        if not GEMINI_AVAILABLE:
            raise ImportError("Google Generative AI no está disponible. Instalar con: pip install google-genai")
        
        self.api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if not self.api_key:
            # Intentar cargar desde variables de entorno
            self.api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.api_key or self.api_key == 'your-gemini-api-key-here':
            # Instead of crashing, allow initialization but fail on generation
            logger.warning("GEMINI_API_KEY no configurada. El servicio funcionará pero fallará al generar contenido.")
            self.client = None
        else:
            # Configurar el cliente con la nueva API
            self.client = genai.Client(
                api_key=self.api_key,
                http_options={'api_version': 'v1'}
            )
            logger.info("GeminiService inicializado correctamente con google.genai (API v1)")
        
        self.cache_timeout = 3600  # 1 hora de cache

    # ... (rest of methods need to check if self.model is None) ...

    
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
        """
        if not self.client:
            raise ValueError("API Key no configurada. Configure GEMINI_API_KEY en el servidor.")

        try:
            # Verificar cache si está habilitado
            if use_cache:
                cache_key = self._get_cache_key(prompt, "general")
                cached_response = self._get_cached_response(cache_key)
                if cached_response:
                    logger.info("Respuesta obtenida desde cache")
                    return cached_response
            
            logger.info(f"Enviando prompt a Gemini: {prompt[:100]}...")
            
            # Configurar parámetros de generación con nueva API
            config = types.GenerateContentConfig(
                temperature=1.0,
                max_output_tokens=max_tokens if max_tokens else 2048
            )
            
            model_name = getattr(settings, 'AI_GOOGLE_MODEL', 'gemini-2.0-flash')
            response = self.client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config
            )
            
            # Guardar en cache si está habilitado
            if use_cache:
                self._cache_response(cache_key, response.text)
            
            logger.info("Respuesta recibida de Gemini exitosamente")
            return response.text
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                logger.warning(f"Límite de cuota de Gemini alcanzado: {e}")
                raise PermissionError("GEMINI_QUOTA_EXCEEDED")
            logger.error(f"Error al generar contenido con Gemini: {e}")
            raise

    def analyze_document_file(self, file_bytes: bytes, mime_type: str, prompt: str) -> str:
        """
        Analiza un archivo (PDF) directamente usando Gemini con capacidades multimodales.
        """
        if not self.client:
            raise ValueError("API Key no configurada.")
        
        try:
            # Preparar parte con archivo
            file_part = types.Part.from_bytes(
                data=file_bytes,
                mime_type=mime_type
            )
            
            model_name = getattr(settings, 'AI_GOOGLE_MODEL', 'gemini-2.0-flash')
            logger.info(f"Enviando archivo {mime_type} a Gemini para análisis multimodal...")
            response = self.client.models.generate_content(
                model=model_name,
                contents=[file_part, prompt]
            )
            
            logger.info("Análisis multimodal completado exitosamente")
            return response.text
            
        except Exception as e:
            logger.error(f"Error en análisis multimodal de documento: {e}")
            raise
    
    def analyze_real_image(self, image_files: List[Any], analysis_type: str = 'comprehensive_technical_analysis', 
                          description: str = '', context: str = '') -> Dict[str, Any]:
        """
        Analizar una o múltiples imágenes de falla en tuberías o accesorios
        
        Args:
            image_files: Lista de archivos de imagen (o un solo archivo para compatibilidad)
            analysis_type (str): Tipo de análisis a realizar
            description (str): Descripción adicional del contexto
            context (str): Contexto adicional del análisis
            
        Returns:
            dict: Análisis detallado de la(s) imagen(es)
        """
        import time
        import uuid
        from PIL import Image
        import io
        
        start_time = time.time()
        analysis_id = str(uuid.uuid4())
        
        # Normalizar entrada a lista
        if not isinstance(image_files, list):
            image_files = [image_files]
            
        try:
            image_parts = []
            
            for img_file in image_files:
                # Leer y procesar la imagen
                if isinstance(img_file, bytes):
                    image_data = img_file
                elif hasattr(img_file, 'read'):
                    image_data = img_file.read()
                    if hasattr(img_file, 'seek'):
                        img_file.seek(0)
                else:
                    continue # Skip invalid input

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
                
                # Preparar parte con imagen
                image_parts.append(types.Part.from_bytes(
                    data=img_byte_arr,
                    mime_type="image/jpeg"
                ))
            
            if not image_parts:
                raise ValueError("No valid images provided for analysis")

            # Crear prompt para análisis
            prompt = f"""
            Como experto en análisis técnico industrial de Postventa, 
            analiza las {len(image_parts)} imagen(es) proporcionada(s) y genera un análisis detallado.
            
            CONTEXTO: {context if context else 'Análisis técnico general'}
            INSTRUCCIÓN ESPECÍFICA: {description if description else 'Realiza un diagnóstico integral de lo que se observa en las imágenes.'}
            
            Responde ÚNICAMENTE en formato JSON con la siguiente estructura:
            {{
                "observations": "Descripción detallada de los hallazgos visuales",
                "possible_causes": ["Lista de posibles causas si es una falla, o factores detectados"],
                "recommendations": ["Recomendaciones técnicas o pasos a seguir"],
                "corrective_actions": ["Acciones sugeridas"],
                "severity_level": "Baja/Media/Alta/Crítica/Informativa",
                "material_identification": "Componentes o materiales identificados",
                "failure_type": "Categoría del hallazgo (ej: Desgaste, Instalación, Informativo, etc.)",
                "environmental_factors": "Factores del entorno detectados",
                "technical_notes": "Correlación entre las múltiples imágenes y conclusiones finales"
            }}
            
            Sé profesional, preciso y directo.
            """
            
            # Verificar cliente
            if not self.client:
                raise ValueError("API Key no configurada.")
            
            logger.info(f"Enviando {len(image_parts)} imágenes a Gemini para análisis (ID: {analysis_id})")
            
            # Generar análisis con nueva API (imágenes + prompt)
            contents = image_parts + [prompt]
            
            model_name = getattr(settings, 'AI_GOOGLE_MODEL', 'gemini-2.0-flash')
            response = self.client.models.generate_content(
                model=model_name,
                contents=contents
            )
            
            processing_time = round(time.time() - start_time, 2)
            
            # Intentar parsear como JSON (Limpiando markdown si existe)
            try:
                text_response = response.text.strip()
                if text_response.startswith('```'):
                    # Eliminar bloques de código markdown
                    text_response = text_response.replace('```json', '').replace('```', '').strip()
                    
                analysis = json.loads(text_response)
            except json.JSONDecodeError:
                # Si no es JSON válido, crear estructura manual
                analysis = {
                    "observations": response.text[:500] + "...",
                    "possible_causes": ["Análisis de múltiples imágenes en proceso"],
                    "recommendations": ["Revisar análisis completo en texto"],
                    "corrective_actions": ["Evaluación integral requerida"],
                    "severity_level": "Media",
                    "material_identification": "Multicomponente",
                    "failure_type": "Análisis complejo",
                    "environmental_factors": "Por evaluar",
                    "technical_notes": "Respuesta en formato texto libre"
                }
            
            return {
                'success': True,
                'analysis': analysis,
                'confidence_score': 0.90,
                'processing_time': processing_time,
                'tokens_used': len(response.text) // 4,
                'model_used': getattr(settings, 'AI_GOOGLE_MODEL', 'gemini-2.0-flash'),
                'analysis_id': analysis_id
            }
            
        except Exception as e:
            logger.error(f"Error al analizar imágenes reales: {e}")
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
    
    def generate_technical_report(self, analysis_data: Dict[str, Any], chat_history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generar un reporte técnico profesional basado en datos de análisis y chat
        """
        import time
        import datetime
        import json
        
        start_time = time.time()
        
        try:
            # Construir contexto para el reporte
            context_str = f"Datos de Análisis: {json.dumps(analysis_data, ensure_ascii=False)}\n"
            if chat_history:
                history_str = "\n".join([f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in chat_history[-10:]])
                context_str += f"\nHistorial de Chat (Contexto adicional):\n{history_str}"
            
            prompt = f"""
            Actúa como un Ingeniero Senior de Calidad y Postventa.
            Genera un REPORTE TÉCNICO PROFESIONAL en formato HTML (solo el contenido del body, con estilos inline elegantes y modernos) basado en la siguiente información.
            
            INFORMACIÓN:
            {context_str}
            
            ESTRUCTURA DEL REPORTE (HTML):
            1.  **Encabezado**: Título "Informe Técnico de Inspección", Fecha ({datetime.datetime.now().strftime('%d/%m/%Y')}), ID de Reporte (generar uno ficticio tipo RPT-2026-XXXX).
            2.  **Resumen Ejecutivo**: Breve descripción del problema y conclusión principal.
            3.  **Hallazgos Técnicos**: Lista detallada de observaciones (usa <ul> y <li>).
            4.  **Análisis de Causas**: Causas probables identificadas.
            5.  **Recomendaciones y Plan de Acción**: Pasos a seguir (usa tablas si es necesario).
            6.  **Nota de Confidencialidad**: Pie de página estándar.
            
            ESTILO (CSS Inline):
            - Usa fuentes sans-serif (Arial, Helvetica), color de texto #333.
            - Títulos en color #2c3e50, bordes inferiores sutiles.
            - Tablas con bordes colapsados, padding 8px, y header con background #f2f2f2.
            - El diseño debe ser limpio, corporativo e industrial.
            
            Salida esperada: Solo el código HTML (sin ```html ... ```).
            """
            
            # Verificar cliente
            if not self.client:
                 raise ValueError("API Key no configurada para generar reporte.")

            model_name = getattr(settings, 'AI_GOOGLE_MODEL', 'gemini-2.0-flash')
            response = self.client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            
            report_html = response.text.strip()
            # Limpiar markdown si existe
            if report_html.startswith('```'):
                report_html = report_html.replace('```html', '').replace('```', '').strip()
                
            return {
                'success': True,
                'report_html': report_html,
                'generated_at': datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generando reporte técnico: {e}")
            return {
                'success': False,
                'error': str(e)
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
            'model': 'gemini-flash-latest',
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