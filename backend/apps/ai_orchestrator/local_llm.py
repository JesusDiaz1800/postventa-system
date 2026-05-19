"""
Local LLM integration for text generation and analysis
Supports GPT4All, Llama2, and other local models
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

class LocalLLMManager:
    """Manager for local LLM models"""
    
    def __init__(self):
        self.models = {}
        self.current_model = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize available local LLM models"""
        try:
            # Check for GPT4All
            if self._check_gpt4all():
                self.models['gpt4all'] = {
                    'name': 'GPT4All',
                    'type': 'gpt4all',
                    'enabled': True,
                    'model_path': os.path.join(settings.BASE_DIR, 'models', 'gpt4all-model.bin')
                }
            
            # Check for Llama2
            if self._check_llama2():
                self.models['llama2'] = {
                    'name': 'Llama2',
                    'type': 'llama2',
                    'enabled': True,
                    'model_path': os.path.join(settings.BASE_DIR, 'models', 'llama2-model.bin')
                }
            
            # Set default model
            if self.models:
                self.current_model = list(self.models.keys())[0]
            
            logger.info(f"Local LLM models initialized: {list(self.models.keys())}")
            
        except Exception as e:
            logger.error(f"Error initializing local LLM models: {e}")
    
    def _check_gpt4all(self) -> bool:
        """Check if GPT4All is available"""
        try:
            import gpt4all
            return True
        except ImportError:
            logger.warning("GPT4All not available")
            return False
    
    def _check_llama2(self) -> bool:
        """Check if Llama2 is available"""
        try:
            # Check if llama.cpp is available
            import llama_cpp
            return True
        except ImportError:
            logger.warning("Llama2 not available")
            return False
    
    def generate_text(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """Generate text using local LLM"""
        try:
            if not self.current_model:
                return "No hay modelos de IA local disponibles"
            
            model_info = self.models[self.current_model]
            
            if model_info['type'] == 'gpt4all':
                return self._generate_with_gpt4all(prompt, max_tokens, temperature)
            elif model_info['type'] == 'llama2':
                return self._generate_with_llama2(prompt, max_tokens, temperature)
            else:
                return "Tipo de modelo no soportado"
                
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return f"Error generando texto: {str(e)}"
    
    def _generate_with_gpt4all(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate text using GPT4All"""
        try:
            import gpt4all
            
            # Load model
            model = gpt4all.GPT4All(
                model_name=os.path.basename(self.models['gpt4all']['model_path']),
                model_path=os.path.dirname(self.models['gpt4all']['model_path'])
            )
            
            # Generate response
            response = model.generate(
                prompt=prompt,
                max_tokens=max_tokens,
                temp=temperature
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error with GPT4All: {e}")
            return "Error con GPT4All"
    
    def _generate_with_llama2(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate text using Llama2"""
        try:
            from llama_cpp import Llama
            
            # Load model
            llm = Llama(
                model_path=self.models['llama2']['model_path'],
                n_ctx=2048,
                n_threads=4
            )
            
            # Generate response
            response = llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["</s>", "Human:", "Assistant:"]
            )
            
            return response['choices'][0]['text']
            
        except Exception as e:
            logger.error(f"Error with Llama2: {e}")
            return "Error con Llama2"
    
    def analyze_incident(self, incident_data: Dict) -> Dict:
        """Analyze incident data and generate insights"""
        try:
            # Create analysis prompt
            prompt = self._create_incident_analysis_prompt(incident_data)
            
            # Generate analysis
            analysis = self.generate_text(prompt, max_tokens=800, temperature=0.3)
            
            # Parse analysis (try to extract structured data)
            structured_analysis = self._parse_analysis(analysis)
            
            return {
                'raw_analysis': analysis,
                'structured_analysis': structured_analysis,
                'model_used': self.current_model,
                'timestamp': str(pd.Timestamp.now())
            }
            
        except Exception as e:
            logger.error(f"Error analyzing incident: {e}")
            return {
                'error': str(e),
                'raw_analysis': 'Error en análisis',
                'structured_analysis': {},
                'model_used': self.current_model
            }
    
    def _create_incident_analysis_prompt(self, incident_data: Dict) -> str:
        """Create prompt for incident analysis"""
        prompt = f"""
        Analiza esta incidencia de postventa y proporciona un análisis técnico detallado:
        
        Datos de la incidencia:
        - Cliente: {incident_data.get('cliente', 'No especificado')}
        - SKU: {incident_data.get('sku', 'No especificado')}
        - Lote: {incident_data.get('lote', 'No especificado')}
        - Fecha de detección: {incident_data.get('fecha_deteccion', 'No especificado')}
        - Descripción: {incident_data.get('descripcion', 'No especificada')}
        - Categoría: {incident_data.get('categoria', 'No especificada')}
        - Subcategoría: {incident_data.get('subcategoria', 'No especificada')}
        
        Por favor, proporciona:
        1. Análisis de posibles causas
        2. Recomendaciones técnicas
        3. Acciones preventivas
        4. Nivel de criticidad
        
        Responde en formato estructurado y técnico.
        """
        return prompt
    
    def _parse_analysis(self, analysis: str) -> Dict:
        """Parse LLM analysis into structured data"""
        try:
            # Try to extract structured information
            structured = {
                'causes': [],
                'recommendations': [],
                'preventive_actions': [],
                'criticality_level': 'medium',
                'confidence': 0.7
            }
            
            # Simple parsing (can be improved with more sophisticated NLP)
            lines = analysis.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detect sections
                if 'causa' in line.lower() or 'cause' in line.lower():
                    current_section = 'causes'
                elif 'recomendación' in line.lower() or 'recommendation' in line.lower():
                    current_section = 'recommendations'
                elif 'preventiva' in line.lower() or 'preventive' in line.lower():
                    current_section = 'preventive_actions'
                elif 'criticidad' in line.lower() or 'criticality' in line.lower():
                    current_section = 'criticality'
                
                # Extract content
                if current_section and line.startswith('-'):
                    content = line[1:].strip()
                    if current_section in structured and isinstance(structured[current_section], list):
                        structured[current_section].append(content)
                    elif current_section == 'criticality':
                        structured['criticality_level'] = content.lower()
            
            return structured
            
        except Exception as e:
            logger.error(f"Error parsing analysis: {e}")
            return {}
    
    def generate_document_content(self, template_type: str, incident_data: Dict) -> str:
        """Generate document content based on template type and incident data"""
        try:
            if template_type == 'cliente_informe':
                return self._generate_client_report(incident_data)
            elif template_type == 'proveedor_carta':
                return self._generate_supplier_letter(incident_data)
            elif template_type == 'lab_report':
                return self._generate_lab_report(incident_data)
            else:
                return self._generate_generic_document(incident_data)
                
        except Exception as e:
            logger.error(f"Error generating document content: {e}")
            return "Error generando contenido del documento"
    
    def _generate_client_report(self, incident_data: Dict) -> str:
        """Generate client report content"""
        prompt = f"""
        Genera un informe para el cliente sobre esta incidencia de postventa.
        El tono debe ser profesional, empático y evitar lenguaje acusatorio.
        
        Datos de la incidencia:
        - Cliente: {incident_data.get('cliente', 'Estimado Cliente')}
        - SKU: {incident_data.get('sku', 'No especificado')}
        - Lote: {incident_data.get('lote', 'No especificado')}
        - Fecha de detección: {incident_data.get('fecha_deteccion', 'No especificada')}
        - Descripción: {incident_data.get('descripcion', 'No especificada')}
        
        El informe debe incluir:
        1. Saludo profesional
        2. Agradecimiento por la comunicación
        3. Descripción del problema (sin acusaciones)
        4. Acciones tomadas
        5. Conclusiones técnicas
        6. Recomendaciones
        7. Compromiso de mejora
        8. Despedida profesional
        
        Usa un tono que mantenga la relación con el cliente.
        """
        return self.generate_text(prompt, max_tokens=1000, temperature=0.5)
    
    def _generate_supplier_letter(self, incident_data: Dict) -> str:
        """Generate supplier letter content"""
        prompt = f"""
        Genera una carta técnica para el proveedor sobre esta incidencia de postventa.
        El tono debe ser directo, técnico y profesional.
        
        Datos de la incidencia:
        - Proveedor: {incident_data.get('proveedor', 'Estimado Proveedor')}
        - SKU: {incident_data.get('sku', 'No especificado')}
        - Lote: {incident_data.get('lote', 'No especificado')}
        - Número de pedido: {incident_data.get('num_pedido', 'No especificado')}
        - Descripción: {incident_data.get('descripcion', 'No especificada')}
        
        La carta debe incluir:
        1. Saludo profesional
        2. Referencia a la incidencia
        3. Descripción técnica del problema
        4. Evidencia presentada
        5. Análisis técnico
        6. Conclusiones
        7. Acciones requeridas del proveedor
        8. Plazos y seguimiento
        9. Despedida profesional
        
        Usa un tono técnico y directo.
        """
        return self.generate_text(prompt, max_tokens=1000, temperature=0.4)
    
    def _generate_lab_report(self, incident_data: Dict) -> str:
        """Generate laboratory report content"""
        prompt = f"""
        Genera un reporte de laboratorio técnico sobre esta incidencia de postventa.
        El tono debe ser científico, preciso y detallado.
        
        Datos de la incidencia:
        - Incidente: {incident_data.get('incidente', 'No especificado')}
        - Muestra: {incident_data.get('muestra', 'No especificada')}
        - Ensayos realizados: {incident_data.get('ensayos', 'No especificados')}
        - Observaciones: {incident_data.get('observaciones', 'No especificadas')}
        
        El reporte debe incluir:
        1. Encabezado técnico
        2. Objetivo del análisis
        3. Metodología utilizada
        4. Resultados de ensayos
        5. Observaciones técnicas
        6. Análisis de resultados
        7. Conclusiones técnicas
        8. Recomendaciones
        9. Firma del experto
        
        Usa terminología técnica y científica.
        """
        return self.generate_text(prompt, max_tokens=1200, temperature=0.3)
    
    def _generate_generic_document(self, incident_data: Dict) -> str:
        """Generate generic document content"""
        prompt = f"""
        Genera un documento técnico sobre esta incidencia de postventa.
        
        Datos de la incidencia:
        {json.dumps(incident_data, indent=2, ensure_ascii=False)}
        
        El documento debe ser profesional, técnico y completo.
        """
        return self.generate_text(prompt, max_tokens=800, temperature=0.5)
    
    def get_model_info(self) -> Dict:
        """Get information about available models"""
        return {
            'available_models': list(self.models.keys()),
            'current_model': self.current_model,
            'models_status': {name: info['enabled'] for name, info in self.models.items()}
        }
    
    def switch_model(self, model_name: str) -> bool:
        """Switch to a different model"""
        if model_name in self.models and self.models[model_name]['enabled']:
            self.current_model = model_name
            logger.info(f"Switched to model: {model_name}")
            return True
        else:
            logger.error(f"Model {model_name} not available or not enabled")
            return False

# Global instance
local_llm_manager = LocalLLMManager()
