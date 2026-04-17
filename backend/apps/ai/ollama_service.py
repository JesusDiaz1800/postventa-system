import requests
import json
import logging
import base64
from typing import Dict, Any, List, Optional
from django.conf import settings

logger = logging.getLogger(__name__)

class OllamaService:
    """
    Servicio para interactuar con Ollama API (Local LLM)
    Soporta generación de texto y análisis multimodal (visión)
    """

    def __init__(self, base_url: str = None, model: str = None):
        # Intentar obtener de settings si no se provee
        self.base_url = base_url or getattr(settings, 'OLLAMA_BASE_URL', 'http://localhost:11434')
        self.model = model or getattr(settings, 'OLLAMA_DEFAULT_MODEL', 'llama3')
        # Limpiar URL de posibles barras finales
        self.base_url = self.base_url.rstrip('/')
        
    def generate_content(self, prompt: str, system_prompt: str = None, timeout: int = 60) -> str:
        """Generar respuesta de texto simple"""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }


        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = requests.post(url, json=payload, timeout=timeout)
            response.raise_for_status()
            return response.json().get('response', '')
        except Exception as e:
            logger.error(f"Error en Ollama generate_content: {e}")
            raise

    def analyze_image(self, image_path: str, prompt: str, vision_model: str = None) -> str:
        """Analizar una imagen usando un modelo de visión local"""
        url = f"{self.base_url}/api/generate"
        model = vision_model or getattr(settings, 'OLLAMA_VISION_MODEL', 'llama3.2-vision')
        
        try:
            with open(image_path, "rb") as image_file:
                image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            
            payload = {
                "model": model,
                "prompt": prompt,
                "images": [image_base64],
                "stream": False
            }

            response = requests.post(url, json=payload, timeout=180)
            response.raise_for_status()
            return response.json().get('response', '')
        except Exception as e:
            logger.error(f"Error en Ollama analyze_image: {e}")
            raise

    def analyze_real_image(self, image_files: List[Any], analysis_type: str = 'comprehensive_technical_analysis', 
                          description: str = '', context: str = '') -> Dict[str, Any]:
        """
        Analizar una o múltiples imágenes usando Ollama Local.
        Referencia: https://ollama.com/library/llama3.2-vision
        """
        import uuid
        import io
        from PIL import Image
        
        url = f"{self.base_url}/api/generate"
        model = getattr(settings, 'OLLAMA_VISION_MODEL', 'llama3.2-vision')
        
        try:
            image_bases64 = []
            
            # Normalizar entrada a lista
            if not isinstance(image_files, list):
                image_files = [image_files]
                
            for img_file in image_files:
                # Leer y procesar
                if isinstance(img_file, bytes):
                    image_data = img_file
                elif hasattr(img_file, 'read'):
                    image_data = img_file.read()
                    if hasattr(img_file, 'seek'):
                        img_file.seek(0)
                else:
                    continue

                # Optimizar imagen para Ollama (Base64) - Redimensionamiento agresivo para velocidad
                pil_image = Image.open(io.BytesIO(image_data))
                if pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')
                
                # Redimensionar a 800px max para que el PC local no sufra
                if pil_image.width > 800 or pil_image.height > 800:
                    pil_image.thumbnail((800, 800))
                
                img_byte_arr = io.BytesIO()
                pil_image.save(img_byte_arr, format='JPEG', quality=80)
                image_bases64.append(base64.b64encode(img_byte_arr.getvalue()).decode('utf-8'))

            if not image_bases64:
                raise ValueError("No se proporcionaron imágenes válidas para Ollama")

            prompt = f"""
            Actúa como un experto en análisis técnico industrial. Analiza estas imágenes de Postventa.
            TIPO DE ANÁLISIS: {analysis_type}
            CONTEXTO: {context}
            INSTRUCCIÓN: {description}
            
            REQUISITO: Responde EXCLUSIVAMENTE en formato JSON con estas llaves: 
            "observations", "possible_causes" (lista), "recommendations" (lista), "severity_level".
            """

            payload = {
                "model": model,
                "prompt": prompt,
                "images": image_bases64,
                "format": "json",
                "stream": False
            }

            logger.info(f"Enviando {len(image_bases64)} imágenes a Ollama Local ({model}) - Timeout 180s")
            response = requests.post(url, json=payload, timeout=180)
            response.raise_for_status()
            
            response_data = response.json()
            text_response = response_data.get('response', '{}')
            
            # Parsear JSON directamente desde Ollama (usando parámetro format: "json")
            try:
                analysis = json.loads(text_response)
            except:
                analysis = {"observations": text_response}

            return {
                'success': True,
                'analysis': analysis,
                'model_used': f'ollama-{model}',
                'provider_used': 'Ollama Local',
                'analysis_id': str(uuid.uuid4())
            }
            
        except Exception as e:
            logger.error(f"Error en Ollama analyze_real_image: {e}")
            raise

    def chat(self, messages: List[Dict[str, str]], timeout: int = 60) -> str:
        """Mantener una conversación fluida"""
        url = f"{self.base_url}/api/chat"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }

        try:
            response = requests.post(url, json=payload, timeout=timeout)
            response.raise_for_status()
            return response.json().get('message', {}).get('content', '')
        except Exception as e:
            logger.error(f"Error en Ollama chat: {e}")
            raise
