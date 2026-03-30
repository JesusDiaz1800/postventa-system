"""
AI Orchestrator con fallback y gestión de créditos mejorada
Redirigido a proveedores reales
"""
import logging
from .providers import get_orchestrator as get_real_orchestrator

logger = logging.getLogger(__name__)

def get_orchestrator():
    """
    Retorna el orquestador real definido en providers.py.
    Mantenemos esta función para compatibilidad con las vistas que importan desde aquí.
    """
    return get_real_orchestrator()

# Clase de compatibilidad si algo aún referencia AIProviderManager directamente
class AIProviderManager:
    def __init__(self):
        self.real_orchestrator = get_real_orchestrator()
    
    def analyze_image(self, image_data, image_type, consent_external=True):
        return self.real_orchestrator.analyze_image(image_data, image_type)
    
    def generate_text(self, prompt, context=None):
        return self.real_orchestrator.generate_text(prompt, context)

# Instancia global para compatibilidad
ai_provider_manager = AIProviderManager()
