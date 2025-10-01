"""
AI-powered image analysis for incident images
Includes BLIP/CLIP for image understanding and local LLM integration
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
import clip
import requests
from django.conf import settings
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)

class ImageAnalyzer:
    """AI-powered image analysis for incident images"""
    
    def __init__(self):
        self.blip_processor = None
        self.blip_model = None
        self.clip_model = None
        self.clip_preprocess = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._load_models()
    
    def _load_models(self):
        """Load AI models for image analysis"""
        try:
            # Load BLIP model for image captioning
            self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            self.blip_model.to(self.device)
            
            # Load CLIP model for image understanding
            self.clip_model, self.clip_preprocess = clip.load("ViT-B/32", device=self.device)
            
            logger.info(f"AI models loaded successfully on {self.device}")
            
        except Exception as e:
            logger.error(f"Error loading AI models: {e}")
            self.blip_processor = None
            self.blip_model = None
            self.clip_model = None
            self.clip_preprocess = None
    
    def analyze_image(self, image_path: str) -> Dict:
        """
        Analyze an image and return comprehensive results
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dict with analysis results
        """
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            
            results = {
                'image_path': image_path,
                'image_size': image.size,
                'analysis_timestamp': None,
                'caption': None,
                'labels': [],
                'confidence_scores': {},
                'exif_data': self._extract_exif_data(image_path),
                'suggested_causes': [],
                'inspection_recommendations': [],
                'quality_assessment': {},
                'error': None
            }
            
            # Generate image caption using BLIP
            if self.blip_model and self.blip_processor:
                caption = self._generate_caption(image)
                results['caption'] = caption
            
            # Generate labels using CLIP
            if self.clip_model and self.clip_preprocess:
                labels = self._generate_labels(image)
                results['labels'] = labels
            
            # Analyze image quality
            results['quality_assessment'] = self._assess_image_quality(image)
            
            # Generate suggestions using local LLM
            suggestions = self._generate_suggestions(results)
            results['suggested_causes'] = suggestions.get('causes', [])
            results['inspection_recommendations'] = suggestions.get('recommendations', [])
            
            results['analysis_timestamp'] = str(torch.cuda.Event(enable_timing=True).elapsed_time(torch.cuda.Event(enable_timing=True)))
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing image {image_path}: {e}")
            return {
                'image_path': image_path,
                'error': str(e),
                'analysis_timestamp': None
            }
    
    def _generate_caption(self, image: Image.Image) -> str:
        """Generate image caption using BLIP"""
        try:
            inputs = self.blip_processor(image, return_tensors="pt").to(self.device)
            out = self.blip_model.generate(**inputs, max_length=50)
            caption = self.blip_processor.decode(out[0], skip_special_tokens=True)
            return caption
        except Exception as e:
            logger.error(f"Error generating caption: {e}")
            return "No se pudo generar descripción de la imagen"
    
    def _generate_labels(self, image: Image.Image) -> List[str]:
        """Generate image labels using CLIP"""
        try:
            # Preprocess image
            image_input = self.clip_preprocess(image).unsqueeze(0).to(self.device)
            
            # Define possible labels for incident analysis
            text_labels = [
                "defecto en producto",
                "grieta",
                "fisura",
                "deformación",
                "corrosión",
                "mancha",
                "rayón",
                "rotura",
                "desgaste",
                "contaminación",
                "producto en buen estado",
                "embalaje dañado",
                "etiqueta incorrecta",
                "color incorrecto",
                "tamaño incorrecto"
            ]
            
            # Tokenize text
            text_inputs = clip.tokenize(text_labels).to(self.device)
            
            # Get features
            with torch.no_grad():
                image_features = self.clip_model.encode_image(image_input)
                text_features = self.clip_model.encode_text(text_inputs)
                
                # Calculate similarities
                similarities = (image_features @ text_features.T).softmax(dim=-1)
                
                # Get top labels
                top_indices = similarities[0].topk(5).indices
                top_labels = [text_labels[i] for i in top_indices]
                
                return top_labels
                
        except Exception as e:
            logger.error(f"Error generating labels: {e}")
            return []
    
    def _extract_exif_data(self, image_path: str) -> Dict:
        """Extract EXIF data from image"""
        try:
            from PIL.ExifTags import TAGS
            
            image = Image.open(image_path)
            exif_data = {}
            
            if hasattr(image, '_getexif'):
                exif = image._getexif()
                if exif is not None:
                    for tag_id, value in exif.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_data[tag] = value
            
            return exif_data
            
        except Exception as e:
            logger.error(f"Error extracting EXIF data: {e}")
            return {}
    
    def _assess_image_quality(self, image: Image.Image) -> Dict:
        """Assess image quality metrics"""
        try:
            # Basic quality metrics
            width, height = image.size
            total_pixels = width * height
            
            # Convert to grayscale for analysis
            gray_image = image.convert('L')
            
            # Calculate brightness
            brightness = sum(gray_image.getdata()) / total_pixels
            
            # Calculate contrast (standard deviation)
            import numpy as np
            pixels = np.array(gray_image.getdata())
            contrast = np.std(pixels)
            
            # Assess quality
            quality_score = 0
            quality_issues = []
            
            if brightness < 50:
                quality_issues.append("Imagen muy oscura")
                quality_score -= 20
            elif brightness > 200:
                quality_issues.append("Imagen muy brillante")
                quality_score -= 20
            
            if contrast < 30:
                quality_issues.append("Bajo contraste")
                quality_score -= 15
            
            if total_pixels < 100000:  # Less than 100k pixels
                quality_issues.append("Resolución muy baja")
                quality_score -= 25
            
            quality_score = max(0, min(100, quality_score + 80))  # Base score + adjustments
            
            return {
                'score': quality_score,
                'issues': quality_issues,
                'brightness': brightness,
                'contrast': contrast,
                'resolution': f"{width}x{height}",
                'total_pixels': total_pixels
            }
            
        except Exception as e:
            logger.error(f"Error assessing image quality: {e}")
            return {'score': 0, 'issues': ['Error en análisis de calidad'], 'error': str(e)}
    
    def _generate_suggestions(self, analysis_results: Dict) -> Dict:
        """Generate suggestions using local LLM"""
        try:
            # Prepare context for LLM
            context = {
                'caption': analysis_results.get('caption', ''),
                'labels': analysis_results.get('labels', []),
                'quality_issues': analysis_results.get('quality_assessment', {}).get('issues', []),
                'exif_data': analysis_results.get('exif_data', {})
            }
            
            # Create prompt for local LLM
            prompt = self._create_analysis_prompt(context)
            
            # Use local LLM to generate suggestions
            suggestions = self._query_local_llm(prompt)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return {'causes': [], 'recommendations': []}
    
    def _create_analysis_prompt(self, context: Dict) -> str:
        """Create prompt for local LLM analysis"""
        prompt = f"""
        Analiza esta imagen de incidencia de postventa y proporciona sugerencias técnicas:
        
        Descripción de la imagen: {context.get('caption', 'No disponible')}
        Etiquetas detectadas: {', '.join(context.get('labels', []))}
        Problemas de calidad: {', '.join(context.get('quality_issues', []))}
        
        Por favor, proporciona:
        1. Posibles causas del problema (máximo 3)
        2. Recomendaciones de inspección (máximo 3)
        
        Responde en formato JSON:
        {{
            "causes": ["causa1", "causa2", "causa3"],
            "recommendations": ["recomendación1", "recomendación2", "recomendación3"]
        }}
        """
        return prompt
    
    def _query_local_llm(self, prompt: str) -> Dict:
        """Query local LLM for analysis suggestions"""
        try:
            # This would integrate with GPT4All or similar local LLM
            # For now, return default suggestions based on common patterns
            
            # Simple rule-based suggestions (can be replaced with actual LLM)
            suggestions = {
                'causes': [
                    'Defecto de fabricación',
                    'Daño durante transporte',
                    'Condiciones de almacenamiento inadecuadas'
                ],
                'recommendations': [
                    'Inspeccionar lote completo',
                    'Verificar condiciones de almacenamiento',
                    'Revisar proceso de fabricación'
                ]
            }
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error querying local LLM: {e}")
            return {'causes': [], 'recommendations': []}
    
    def batch_analyze_images(self, image_paths: List[str]) -> List[Dict]:
        """Analyze multiple images in batch"""
        results = []
        for image_path in image_paths:
            result = self.analyze_image(image_path)
            results.append(result)
        return results
    
    def get_model_status(self) -> Dict:
        """Get status of loaded AI models"""
        return {
            'blip_loaded': self.blip_model is not None,
            'clip_loaded': self.clip_model is not None,
            'device': self.device,
            'models_ready': self.blip_model is not None and self.clip_model is not None
        }

# Global instance
image_analyzer = ImageAnalyzer()
