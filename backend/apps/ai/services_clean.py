"""
Servicio de IA limpio - Solo Gemini (gratuito)
"""
import os
import base64
import requests
import json
import time
from typing import Dict, Any, Optional
from django.conf import settings
from django.core.files.storage import default_storage
from .models import AIAnalysis, AIProvider
import logging

logger = logging.getLogger(__name__)

class AIService:
    """Servicio de IA usando solo Gemini (gratuito)"""
    
    def __init__(self):
        self.providers = self._get_active_providers()
    
    def _get_active_providers(self):
        """Get active AI providers ordered by priority"""
        return AIProvider.objects.filter(is_active=True).order_by('priority')
    
    def _encode_image_to_base64(self, image_path: str) -> str:
        """Encode image file to base64 string"""
        try:
            with open(image_path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding image {image_path}: {e}")
            raise
    
    def _get_image_mime_type(self, image_path: str) -> str:
        """Get MIME type for image"""
        ext = os.path.splitext(image_path)[1].lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.bmp': 'image/bmp'
        }
        return mime_types.get(ext, 'image/jpeg')
    
    def analyze_image(self, image_path: str, analysis_type: str = 'technical_analysis') -> Dict[str, Any]:
        """Analyze image using Gemini (gratuito) with fallback"""
        
        # Import Gemini service
        from .gemini_service import GeminiService
        
        try:
            # Use Gemini service (gratuito)
            gemini = GeminiService()
            result = gemini.analyze_image_with_gemini(image_path, analysis_type)
            
            if result['success']:
                logger.info(f"Gemini analysis successful with {result['model']}")
                return result
            else:
                logger.warning(f"Gemini failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Gemini service error: {e}")
        
        # Fallback to demo mode if Gemini fails
        logger.info("Falling back to demo analysis")
        return self._demo_analysis(image_path, analysis_type)
    
    def generate_technical_report(self, analysis_data: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate technical report using Gemini (gratuito)"""
        
        # Import Gemini service
        from .gemini_service import GeminiService
        
        try:
            # Use Gemini service for report generation (gratuito)
            gemini = GeminiService()
            result = gemini.generate_technical_report(analysis_data, context)
            
            if result['success']:
                logger.info(f"Report generated successfully with {result['model']}")
                return result
            else:
                logger.warning(f"Report generation failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Gemini report generation error: {e}")
        
        # Fallback to basic report
        return {
            'success': True,
            'report': f"# Reporte Técnico\n\n{analysis_data}\n\n---\n*Reporte generado automáticamente*",
            'model': 'fallback',
            'tokens_used': 0,
            'cost_estimate': 0.0
        }
    
    def _demo_analysis(self, image_path: str, analysis_type: str) -> Dict[str, Any]:
        """Demo analysis when Gemini is not available"""
        filename = os.path.basename(image_path)
        file_size = os.path.getsize(image_path) if os.path.exists(image_path) else 0
        
        return {
            'success': True,
            'analysis': f"""
## Análisis Técnico - Modo Demo

**Archivo:** {filename}
**Tamaño:** {file_size:,} bytes
**Tipo:** {analysis_type}

### Descripción General
Imagen procesada para análisis de control de calidad postventa.

### Estado del Procesamiento
- **Procesamiento:** Completado
- **Método:** Análisis demo
- **Confianza:** 6.0/10

### Recomendaciones
Para análisis más detallado, verifique la configuración de Gemini.

---
*Análisis generado por sistema demo*
            """,
            'model': 'demo-mode',
            'tokens_used': 0,
            'confidence': 0.6,
            'cost_estimate': 0.0
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
