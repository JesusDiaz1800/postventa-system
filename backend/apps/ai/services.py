import os
import base64
import requests
import json
import time
import uuid
from typing import Dict, Any, Optional, List
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import AIAnalysis, AIProvider
from .gemini_service import GeminiService
from .ollama_service import OllamaService
import logging

logger = logging.getLogger(__name__)

class AIService:
    """Orquestador de IA Híbrida (Gemini Cloud + Ollama Local)"""
    
    def __init__(self, provider_name: str = None):
        """Inicializar el orquestador con un proveedor específico o el activo por prioridad"""
        self.provider_name = provider_name
        self._provider_instance = None
        self._setup_provider()

    def _setup_provider(self):
        """Configura la instancia del proveedor basada en la base de datos o settings"""
        try:
            active_provider = None
            if self.provider_name:
                active_provider = AIProvider.objects.filter(name__iexact=self.provider_name, is_active=True).first()
            
            if not active_provider:
                # Buscar el de mayor prioridad (priority ASC)
                active_provider = AIProvider.objects.filter(is_active=True).order_by('priority').first()

            if active_provider:
                if active_provider.name.lower() == 'gemini':
                    self._provider_instance = GeminiService()
                elif active_provider.name.lower() == 'ollama':
                    self._provider_instance = OllamaService(
                        base_url=active_provider.base_url,
                        model=getattr(settings, 'OLLAMA_DEFAULT_MODEL', 'llama3')
                    )
            
            # Fallback por defecto si nada está configurado
            if not self._provider_instance:
                self._provider_instance = GeminiService()
                
        except Exception as e:
            logger.error(f"Error fatal configurando proveedor de IA: {e}")
            self._provider_instance = GeminiService()

    def _run_with_fallback(self, method_name: str, *args, **kwargs) -> Any:
        """
        Ejecuta un método del proveedor con fallback automático si falla por cuota (429).
        """
        try:
            # 1. Intentar con el proveedor configurado inicialmente
            if not self._provider_instance:
                self._setup_provider()
            
            method = getattr(self._provider_instance, method_name)
            return method(*args, **kwargs)
            
        except Exception as e:
            # 2. Detectar si el error amerita fallback (Cuota excedida o fallo de conexión en Gemini)
            error_str = str(e)
            is_quota_error = "GEMINI_QUOTA_EXCEEDED" in error_str or "429" in error_str
            
            # Solo hacemos fallback si estamos en Gemini y no es Ollama ya
            if is_quota_error and not isinstance(self._provider_instance, OllamaService):
                logger.warning(f"Fallback automático: Gemini agotado o inaccesible. Intentando con Ollama Local...")
                
                ollama_provider = AIProvider.objects.filter(name__iexact='Ollama', is_active=True).first()
                if ollama_provider:
                    temp_ollama = OllamaService(
                        base_url=ollama_provider.base_url,
                        model=getattr(settings, 'OLLAMA_DEFAULT_MODEL', 'llama3')
                    )
                    try:
                        # Reintentar la misma operación con Ollama
                        fallback_method = getattr(temp_ollama, method_name)
                        result = fallback_method(*args, **kwargs)
                        
                        # Inyectar metadata de fallback si el resultado es un dict
                        if isinstance(result, dict):
                            result['fallback_used'] = True
                            result['provider_used'] = 'Ollama (Modo Rescate)'
                        return result
                    except Exception as ollama_e:
                        logger.error(f"El fallback a Ollama también falló: {ollama_e}")
            
            # Si no hay solución, relanzar el error
            raise e

    def analyze_real_image(self, image_files: List[Any], analysis_type: str = 'comprehensive_technical_analysis', 
                          description: str = '', context: str = '') -> Dict[str, Any]:
        """Analizar una o múltiples imágenes con Fallback Híbrido"""
        try:
            return self._run_with_fallback(
                'analyze_real_image',
                image_files=image_files,
                analysis_type=analysis_type,
                description=description,
                context=context
            )
        except Exception as e:
            logger.error(f"Error total en analyze_real_image: {e}")
            return {'success': False, 'error': f"IA no disponible temporalmente: {str(e)}"}

    def analyze_failure_image(self, image_file, analysis_id=None):
        """Simplificación para compatibilidad con versiones anteriores"""
        try:
            # Reusar el método multimodal
            return self.analyze_real_image([image_file], description="Analiza detalladamente esta falla.")
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def professionalize_problem_description(self, description: str, context: Dict[str, Any] = None) -> str:
        """Mejora la redacción técnica usando IA con fallback"""
        try:
            # GeminiService y OllamaService tienen implementaciones de generate_content
            # que pueden servir para redactar profesionalmente si no tienen el método específico
            if hasattr(self._provider_instance, 'professionalize_problem_description'):
                return self._run_with_fallback(
                    'professionalize_problem_description',
                    description=description,
                    context=context
                )
            
            # Fallback a prompt genérico si el método no existe
            prompt = f"Actúa como un experto industrial. Reescribe de forma ultra-profesional esta descripción: '{description}'. Contexto: {context}"
            return self._run_with_fallback('generate_content', prompt=prompt)
        except Exception as e:
            logger.error(f"Error profesionalizando texto: {e}")
            return description

    def generate_technical_report(self, analysis_data: Any, context: Dict[str, Any] = None) -> str:
        """Genera el contenido del reporte técnico"""
        try:
            if hasattr(self._provider_instance, 'generate_technical_report'):
                return self._run_with_fallback('generate_technical_report', analysis_data, context)
            
            prompt = f"Genera un reporte técnico formal basado en estos datos de análisis: {analysis_data}. Contexto: {context}"
            return self._run_with_fallback('generate_content', prompt=prompt)
        except Exception as e:
            return f"Reporte automático (AI Offline): {str(analysis_data)}"

    def _demo_analysis(self, image_path, analysis_id):
        """Método de respaldo estático (Legacy)"""
        return {
            'success': True,
            'analysis': {
                'observations': 'Se detectan anomalías en la superficie del material.',
                'possible_causes': ['Desgaste natural', 'Instalación deficiente'],
                'recommendations': ['Inspección física inmediata'],
                'severity_level': 'Media'
            }
        }
    
    def save_analysis(self, user, analysis_type: str, image_path: str, 
                     analysis_result: Dict[str, Any]) -> AIAnalysis:
        """Save analysis result to database"""
        try:
            analysis = AIAnalysis.objects.create(
                user=user,
                analysis_type=analysis_type,
                status='completed',
                input_file_path=image_path,
                ai_provider=analysis_result.get('model', 'gemini'),
                model_used=analysis_result.get('model', 'gemini-pro'),
                processed_analysis=analysis_result.get('analysis', ''),
                confidence_score=analysis_result.get('confidence', 0.0),
                tokens_used=analysis_result.get('tokens_used', 0),
                cost=analysis_result.get('cost_estimate', 0.0)
            )
            
            logger.info(f"Analysis saved with ID: {analysis.id}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error saving analysis: {e}")
            raise
