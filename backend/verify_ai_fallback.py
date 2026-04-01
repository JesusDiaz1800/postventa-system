import os
import django
import sys
from unittest.mock import MagicMock, patch

# Setup Django environment
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.ai.gemini_service import GeminiService

def verify_ai_fallback():
    print("=== Verificando Lógica de Fallback de IA ===")
    
    # 1. Crear instancia de GeminiService
    service = GeminiService()
    
    # 2. Mockear el cliente de Google GenAI para simular error 429 (Quota)
    # Importante: según GeminiService.py, el cliente está en self.client.models.generate_content
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("429: Quota exceeded for model gemini-2.0-flash")
    
    service.client = mock_client
    
    # 3. Mockear OllamaService para verificar su llamada
    with patch('apps.ai.gemini_service.OllamaService') as MockOllama:
        mock_ollama_instance = MockOllama.return_value
        mock_ollama_instance.generate_content.return_value = "Respuesta generada por OLLAMA (Local)"
        
        print("Solicitando contenido con Gemini (Simulando error 429)...")
        prompt = "test prompt"
        
        try:
            # Desactivamos el cache para forzar la llamada
            result = service.generate_content(prompt, use_cache=False)
            
            print(f"Resultado recibido: {result}")
            
            # 4. Verificar flujo
            # Debería haber llamado al menos dos veces a generate_content (gemini-2.0 y luego gemini-1.5 si falla el 2.0)
            # Como mockeamos generate_content con el mismo efecto para ambos en este mock simple:
            # Intentará 2.0 -> Falla -> Intentará 1.5 -> Falla -> Caerá en Ollama.
            
            if "OLLAMA" in result:
                print("SUCCESS: El sistema conmutó correctamente a Ollama tras el fallo de Gemini.")
            else:
                print("FAILED: No se recibió la respuesta de Ollama.")
                
            # Verificar que se intentó llamar a Ollama
            if mock_ollama_instance.generate_content.called:
                print("SUCCESS: Se llamó al método generate_content de OllamaService.")
            else:
                print("FAILED: No se llamó a OllamaService.")
                
        except Exception as e:
            print(f"ERROR inesperado durante la prueba: {e}")

if __name__ == "__main__":
    verify_ai_fallback()
