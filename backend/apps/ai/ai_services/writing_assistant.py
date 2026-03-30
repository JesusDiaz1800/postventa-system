"""
AI Writing Assistant Service using Google Gemini API (Official SDK)
Provides professional text enhancement for visit reports and documents.
"""
import os
import logging
import json
from django.conf import settings

logger = logging.getLogger(__name__)

# Try to import the official SDK
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("google-genai package not installed. AI features will be limited.")


class AIWritingAssistant:
    """
    AI-powered writing assistant using Google Gemini API (Official SDK).
    Free tier: 60 requests per minute.
    """
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY', '')
        self.client = None
        self.model = "gemini-2.0-flash"  # Using latest model
        
        if GENAI_AVAILABLE and self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info("Gemini AI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self.client = None
    
    def _make_request(self, prompt: str) -> str:
        """Make a request to Gemini API using official SDK."""
        if not self.client:
            logger.warning("No Gemini client available. Using fallback.")
            return self._fallback_response(prompt)
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            return response.text
            
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return f"Error de IA: {str(e)}. Verifique su API key."
    
    def _fallback_response(self, prompt: str) -> str:
        """Fallback when API is not available."""
        if not self.api_key:
            return "⚠️ Configure GEMINI_API_KEY en el archivo .env del backend"
        if not GENAI_AVAILABLE:
            return "⚠️ Instale el paquete google-genai: pip install google-genai"
        return "⚠️ Error al conectar con la API de Gemini"
    
    def improve_text(self, text: str) -> dict:
        """Improve text to make it more professional."""
        prompt = f"""Eres un asistente de redacción técnica profesional para una empresa de polifusión y tuberías HDPE.

Tu tarea es mejorar el siguiente texto para hacerlo más profesional, claro y técnicamente preciso.

TEXTO ORIGINAL:
{text}

INSTRUCCIONES:
- Reescribe el texto de manera profesional
- Usa terminología técnica correcta del sector de tuberías y soldadura por polifusión
- Mantén la información original pero mejora la redacción
- Corrige errores de ortografía y gramática
- Hazlo más claro y conciso

Solo responde con el texto mejorado, sin explicaciones adicionales."""

        improved = self._make_request(prompt)
        
        return {
            "original_text": text,
            "improved_text": improved.strip(),
            "success": True
        }
    
    def fix_errors(self, text: str) -> dict:
        """Fix grammar, spelling and punctuation errors."""
        prompt = f"""Eres un corrector profesional de textos técnicos en español chileno.

Corrige todos los errores en el siguiente texto:
- Ortografía
- Gramática
- Puntuación
- Acentos
- Mayúsculas

TEXTO ORIGINAL:
{text}

INSTRUCCIONES:
- Mantén el significado original
- Conserva el tono técnico
- Solo corrige errores, no reescribas completamente

Responde SOLO con el texto corregido, sin explicaciones."""

        fixed = self._make_request(prompt)
        
        return {
            "original_text": text,
            "fixed_text": fixed.strip(),
            "success": True
        }
    
    def generate_technical_report(self, context: dict) -> dict:
        """Generate technical report content based on context."""
        prompt = f"""Eres un ingeniero técnico especializado en tuberías de polietileno de alta densidad (HDPE) y soldadura por termofusión/polifusión.

Genera un reporte técnico profesional basado en la siguiente información:

INFORMACIÓN DE LA VISITA:
- Cliente: {context.get('client_name', 'No especificado')}
- Proyecto/Obra: {context.get('project_name', 'No especificado')}
- Motivo de visita: {context.get('visit_reason', 'No especificado')}
- Observaciones previas: {context.get('observations', 'No especificado')}

GENERA LAS SIGUIENTES SECCIONES:

1. RESUMEN EJECUTIVO
   (2-3 oraciones resumiendo la visita)

2. HALLAZGOS TÉCNICOS
   • Punto 1
   • Punto 2
   • Punto 3

3. RECOMENDACIONES
   • Acción sugerida 1
   • Acción sugerida 2

Usa terminología técnica del sector de tuberías HDPE PE100, soldadura por termofusión, y normas aplicables (ISO 4427, etc.)."""

        content = self._make_request(prompt)
        
        return {
            "generated_content": content.strip(),
            "success": True
        }
    
    def generate_closure_analysis(self, context: dict) -> dict:
        """
        Generate a professional analytical conclusion for incident closure.
        """
        stage = context.get('stage', 'General')
        evidence = context.get('evidence', 'No especificada')
        
        prompt = f"""Eres un Gerente de Calidad y Postventa experto en tuberías HDPE y termofusión.
Tu tarea es redactar una CONCLUSIÓN TÉCNICA ANALÍTICA para cerrar formalmente una incidencia en la etapa de: {stage.upper()}.

CONTEXTO DE LA INCIDENCIA:
- Cliente: {context.get('client_name', 'N/A')}
- Obra/Proyecto: {context.get('project_name', 'N/A')}
- Problema Reportado: {context.get('problem', 'N/A')}

EVIDENCIA Y HALLAZGOS DISPONIBLES:
{evidence}

INSTRUCCIONES DE REDACCIÓN:
1. Redacta un párrafo sólido y profesional de 100-150 palabras.
2. Comienza indicando la causa raíz identificada (si hay evidencia) o la resolución tomada.
3. Usa lenguaje técnico preciso (ej. "falla por contaminación", "parámetros de soldadura fuera de norma", "defecto de materia prima").
4. Concluye confirmando que el caso queda cerrado satisfactoriamente tras la gestión realizada.
5. NO uses listas ni viñetas, solo prosa formal para un informe final.
6. El tono debe ser objetivo, resolutivo y formal.

Genera SOLO el texto de la conclusión."""

        content = self._make_request(prompt)
        
        return {
            "analysis": content.strip(),
            "success": True
        }

    # Helper method to expand abbreviations (existing)
    def suggest_technical_terms(self, text: str) -> dict:
        """Suggest correct technical terms for the text."""
        prompt = f"""Eres un experto en terminología técnica de tuberías de polietileno y soldadura por polifusión.

Analiza el siguiente texto e identifica términos que podrían mejorarse con vocabulario técnico más preciso:

TEXTO:
{text}

Responde en formato JSON así:
{{"sugerencias": [
    {{"termino_original": "tubo", "termino_sugerido": "tubería de HDPE PE100", "razon": "Mayor precisión técnica"}},
    {{"termino_original": "pegar", "termino_sugerido": "soldar por termofusión", "razon": "Término técnico correcto"}}
]}}

Solo responde con el JSON válido, sin texto adicional ni markdown."""

        response = self._make_request(prompt)
        
        try:
            # Clean response if it has markdown
            clean_response = response.strip()
            if clean_response.startswith("```"):
                clean_response = clean_response.split("```")[1]
                if clean_response.startswith("json"):
                    clean_response = clean_response[4:]
            
            suggestions = json.loads(clean_response)
            return {"suggestions": suggestions.get("sugerencias", []), "success": True}
        except json.JSONDecodeError:
            return {"suggestions": [], "success": False, "raw_response": response}


    def generate_custom_text(self, prompt_text: str, context: dict, prompt_type: str = 'general') -> dict:
        """
        Generate text based on a specific prompt and context.
        Used for Quality Analysis, reasons, etc.
        """
        # Build prompt based on type
        full_prompt = prompt_text
        
        if prompt_type == 'quality_analysis':
            full_prompt = f"""Eres un Ingeniero de Calidad experto en tuberías HDPE y polifusión.
            
Basándote en la siguiente información de la incidencia:
- Producto: {context.get('product', 'N/A')}
- Cliente: {context.get('client', 'N/A')}
- Descripción del problema: {context.get('description', 'N/A')}

{prompt_text or "Realiza un análisis de causa raíz y sugiere acciones correctivas."}

Responde de forma profesional, técnica y concisa.
Solo entrega el texto del análisis."""

        content = self._make_request(full_prompt)
        
        return {
            "text": content.strip(),
            "success": True
        }


# Singleton instance
writing_assistant = AIWritingAssistant()
