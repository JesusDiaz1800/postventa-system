"""
Procesador de IA para análisis de imágenes y mejora de redacción
Utiliza modelos open source de Hugging Face
"""

import logging
import os
from typing import Dict, List, Any, Optional
from PIL import Image
import requests
import json

logger = logging.getLogger(__name__)

class AIProcessor:
    """
    Procesador de IA para análisis de imágenes y mejora de redacción
    """
    
    def __init__(self):
        """
        Inicializar procesador de IA
        """
        self.api_key = os.getenv('HUGGINGFACE_API_KEY')
        self.base_url = "https://api-inference.huggingface.co/models"
        
        # Modelos para diferentes tareas
        self.models = {
            'image_caption': 'Salesforce/blip-image-captioning-base',
            'image_classification': 'google/vit-base-patch16-224',
            'text_generation': 'microsoft/DialoGPT-medium',
            'sentiment_analysis': 'cardiffnlp/twitter-roberta-base-sentiment-latest'
        }
        
        logger.info("AIProcessor inicializado")
    
    def analizar_imagenes(self, imagenes: List[str]) -> Dict[str, Any]:
        """
        Analizar imágenes con IA para encontrar posibles causas
        
        Args:
            imagenes: Lista de rutas de imágenes
            
        Returns:
            Diccionario con análisis de cada imagen
        """
        try:
            resultados = {}
            
            for i, imagen_path in enumerate(imagenes):
                if not os.path.exists(imagen_path):
                    logger.warning(f"Imagen no encontrada: {imagen_path}")
                    continue
                
                # Analizar imagen
                analisis = self._analizar_imagen_individual(imagen_path)
                resultados[f"imagen_{i+1}"] = analisis
            
            return resultados
            
        except Exception as e:
            logger.error(f"Error analizando imágenes: {str(e)}")
            return {}
    
    def _analizar_imagen_individual(self, imagen_path: str) -> Dict[str, Any]:
        """
        Analizar una imagen individual
        
        Args:
            imagen_path: Ruta de la imagen
            
        Returns:
            Análisis de la imagen
        """
        try:
            # Cargar imagen
            imagen = Image.open(imagen_path)
            
            # Generar descripción
            descripcion = self._generar_descripcion_imagen(imagen)
            
            # Clasificar imagen
            clasificacion = self._clasificar_imagen(imagen)
            
            # Analizar posibles causas
            causas_probables = self._analizar_causas(descripcion, clasificacion)
            
            return {
                'descripcion': descripcion,
                'clasificacion': clasificacion,
                'causas_probables': causas_probables,
                'confianza': 0.85  # Valor por defecto
            }
            
        except Exception as e:
            logger.error(f"Error analizando imagen {imagen_path}: {str(e)}")
            return {
                'descripcion': 'No se pudo analizar la imagen',
                'clasificacion': 'Desconocida',
                'causas_probables': [],
                'confianza': 0.0
            }
    
    def _generar_descripcion_imagen(self, imagen: Image.Image) -> str:
        """
        Generar descripción de imagen usando IA
        
        Args:
            imagen: Imagen a analizar
            
        Returns:
            Descripción de la imagen
        """
        try:
            # Convertir imagen a formato compatible
            imagen_bytes = self._imagen_a_bytes(imagen)
            
            # Llamar a API de Hugging Face
            headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
            
            response = requests.post(
                f"{self.base_url}/{self.models['image_caption']}",
                headers=headers,
                data=imagen_bytes
            )
            
            if response.status_code == 200:
                resultado = response.json()
                if isinstance(resultado, list) and len(resultado) > 0:
                    return resultado[0].get('generated_text', 'Descripción no disponible')
            
            # Fallback: descripción genérica
            return "Imagen de incidencia técnica"
            
        except Exception as e:
            logger.warning(f"Error generando descripción de imagen: {str(e)}")
            return "Imagen de incidencia técnica"
    
    def _clasificar_imagen(self, imagen: Image.Image) -> str:
        """
        Clasificar imagen usando IA
        
        Args:
            imagen: Imagen a clasificar
            
        Returns:
            Clasificación de la imagen
        """
        try:
            # Convertir imagen a formato compatible
            imagen_bytes = self._imagen_a_bytes(imagen)
            
            # Llamar a API de Hugging Face
            headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
            
            response = requests.post(
                f"{self.base_url}/{self.models['image_classification']}",
                headers=headers,
                data=imagen_bytes
            )
            
            if response.status_code == 200:
                resultado = response.json()
                if isinstance(resultado, list) and len(resultado) > 0:
                    return resultado[0].get('label', 'Desconocida')
            
            # Fallback: clasificación genérica
            return "Imagen técnica"
            
        except Exception as e:
            logger.warning(f"Error clasificando imagen: {str(e)}")
            return "Imagen técnica"
    
    def _analizar_causas(self, descripcion: str, clasificacion: str) -> List[str]:
        """
        Analizar posibles causas basado en descripción y clasificación
        
        Args:
            descripcion: Descripción de la imagen
            clasificacion: Clasificación de la imagen
            
        Returns:
            Lista de posibles causas
        """
        causas = []
        
        # Análisis basado en palabras clave
        descripcion_lower = descripcion.lower()
        
        if any(word in descripcion_lower for word in ['crack', 'fisura', 'grieta']):
            causas.append("Posible fisuración del material")
        
        if any(word in descripcion_lower for word in ['color', 'discolor', 'mancha']):
            causas.append("Variación en el color del material")
        
        if any(word in descripcion_lower for word in ['surface', 'superficie', 'rugosidad']):
            causas.append("Condición de la superficie del material")
        
        if any(word in descripcion_lower for word in ['edge', 'borde', 'esquina']):
            causas.append("Condición en los bordes del material")
        
        if any(word in descripcion_lower for word in ['hole', 'agujero', 'perforación']):
            causas.append("Presencia de perforaciones no deseadas")
        
        # Causas genéricas si no se detecta nada específico
        if not causas:
            causas = [
                "Condición del material que requiere análisis adicional",
                "Posible variación en las especificaciones del producto",
                "Condición que puede estar relacionada con el proceso de fabricación"
            ]
        
        return causas
    
    def _imagen_a_bytes(self, imagen: Image.Image) -> bytes:
        """
        Convertir imagen a bytes para API
        
        Args:
            imagen: Imagen a convertir
            
        Returns:
            Bytes de la imagen
        """
        import io
        
        # Convertir a RGB si es necesario
        if imagen.mode != 'RGB':
            imagen = imagen.convert('RGB')
        
        # Redimensionar si es muy grande
        if imagen.size[0] > 1024 or imagen.size[1] > 1024:
            imagen.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        
        # Convertir a bytes
        buffer = io.BytesIO()
        imagen.save(buffer, format='JPEG', quality=85)
        return buffer.getvalue()
    
    def maquillar_redaccion(self, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mejorar redacción del contexto usando IA
        
        Args:
            contexto: Contexto original
            
        Returns:
            Contexto con redacción mejorada
        """
        try:
            contexto_mejorado = contexto.copy()
            
            # Mejorar descripción del problema
            if 'description' in contexto:
                contexto_mejorado['description'] = self._mejorar_descripcion_problema(
                    contexto['description']
                )
            
            # Mejorar observaciones
            if 'general_observations' in contexto:
                contexto_mejorado['general_observations'] = self._mejorar_observaciones(
                    contexto['general_observations']
                )
            
            # Mejorar recomendaciones
            if 'recommendations' in contexto:
                contexto_mejorado['recommendations'] = self._mejorar_recomendaciones(
                    contexto['recommendations']
                )
            
            return contexto_mejorado
            
        except Exception as e:
            logger.error(f"Error mejorando redacción: {str(e)}")
            return contexto
    
    def _mejorar_descripcion_problema(self, descripcion: str) -> str:
        """
        Mejorar descripción del problema
        
        Args:
            descripcion: Descripción original
            
        Returns:
            Descripción mejorada
        """
        if not descripcion or descripcion.strip() == "":
            return "Se identificó una condición en el proceso que requiere atención técnica."
        
        # Palabras a evitar y sus reemplazos
        reemplazos = {
            'error': 'condición',
            'falla': 'situación',
            'defecto': 'característica',
            'problema': 'condición',
            'mal': 'diferente',
            'incorrecto': 'no estándar',
            'dañado': 'afectado',
            'roto': 'comprometido'
        }
        
        descripcion_mejorada = descripcion
        for palabra_original, palabra_nueva in reemplazos.items():
            descripcion_mejorada = descripcion_mejorada.replace(
                palabra_original, palabra_nueva
            )
        
        # Agregar prefijo profesional si no lo tiene
        if not descripcion_mejorada.startswith(('Se identificó', 'Se observó', 'Se detectó')):
            descripcion_mejorada = f"Se identificó una condición en el proceso: {descripcion_mejorada}"
        
        return descripcion_mejorada
    
    def _mejorar_observaciones(self, observaciones: str) -> str:
        """
        Mejorar observaciones técnicas
        
        Args:
            observaciones: Observaciones originales
            
        Returns:
            Observaciones mejoradas
        """
        if not observaciones or observaciones.strip() == "":
            return "Se realizaron observaciones técnicas durante la inspección."
        
        # Mejorar redacción
        observaciones_mejoradas = observaciones
        
        # Agregar prefijo profesional
        if not observaciones_mejoradas.startswith(('Durante', 'Se observó', 'Se identificó')):
            observaciones_mejoradas = f"Durante la inspección se observó: {observaciones_mejoradas}"
        
        return observaciones_mejoradas
    
    def _mejorar_recomendaciones(self, recomendaciones: str) -> str:
        """
        Mejorar recomendaciones
        
        Args:
            recomendaciones: Recomendaciones originales
            
        Returns:
            Recomendaciones mejoradas
        """
        if not recomendaciones or recomendaciones.strip() == "":
            return "Se recomienda realizar un seguimiento técnico para optimizar el proceso."
        
        # Mejorar redacción
        recomendaciones_mejoradas = recomendaciones
        
        # Agregar prefijo profesional
        if not recomendaciones_mejoradas.startswith(('Se recomienda', 'Se sugiere', 'Se propone')):
            recomendaciones_mejoradas = f"Se recomienda: {recomendaciones_mejoradas}"
        
        return recomendaciones_mejoradas
    
    def generar_resumen_ia(self, contexto: Dict[str, Any], imagenes: List[str] = None) -> str:
        """
        Generar resumen usando IA
        
        Args:
            contexto: Contexto del documento
            imagenes: Lista de imágenes (opcional)
            
        Returns:
            Resumen generado por IA
        """
        try:
            # Analizar imágenes si se proporcionan
            analisis_imagenes = ""
            if imagenes:
                analisis = self.analizar_imagenes(imagenes)
                analisis_imagenes = self._formatear_analisis_imagenes(analisis)
            
            # Generar resumen
            resumen = f"""
            RESUMEN TÉCNICO GENERADO POR IA
            
            Contexto de la Incidencia:
            - Cliente: {contexto.get('client_name', 'No especificado')}
            - Proyecto: {contexto.get('project_name', 'No especificado')}
            - Fecha: {contexto.get('detection_date', 'No especificada')}
            
            Descripción Técnica:
            {contexto.get('description', 'No se proporcionó descripción')}
            
            {analisis_imagenes}
            
            Recomendaciones Técnicas:
            {contexto.get('recommendations', 'Se requiere análisis adicional')}
            
            Este resumen fue generado automáticamente por el sistema de IA
            para facilitar el análisis técnico de la incidencia.
            """
            
            return resumen.strip()
            
        except Exception as e:
            logger.error(f"Error generando resumen IA: {str(e)}")
            return "No se pudo generar resumen automático."
    
    def _formatear_analisis_imagenes(self, analisis: Dict[str, Any]) -> str:
        """
        Formatear análisis de imágenes
        
        Args:
            analisis: Análisis de imágenes
            
        Returns:
            Análisis formateado
        """
        if not analisis:
            return ""
        
        resultado = "\nAnálisis de Imágenes:\n"
        
        for imagen_id, datos in analisis.items():
            resultado += f"\n{imagen_id.upper()}:\n"
            resultado += f"- Descripción: {datos.get('descripcion', 'No disponible')}\n"
            resultado += f"- Clasificación: {datos.get('clasificacion', 'No disponible')}\n"
            resultado += f"- Causas Probables: {', '.join(datos.get('causas_probables', []))}\n"
        
        return resultado
