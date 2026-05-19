import os
import sys
import io
from PIL import Image
import django

# Environment setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
sys.path.append('backend')
django.setup()

from apps.ai.gemini_service import GeminiService
from apps.ai.ollama_service import OllamaService

def test_ai_services():
    print("=== INICIANDO PRUEBAS DE IA ===")
    
    # 1. Probar Gemini (Texto)
    print("\n1. Probando Gemini (Texto)...")
    gemini = GeminiService()
    try:
        res = gemini.generate_content("¿Cuál es la capital de Colombia?")
        print(f"   [OK] Gemini respondió: {res[:50]}...")
    except Exception as e:
        print(f"   [ERROR] Gemini falló: {e}")

    # 2. Probar Gemini (Imagen) - Usaremos una imagen de prueba blanca
    print("\n2. Probando Gemini (Imagen)...")
    try:
        img = Image.new('RGB', (100, 100), color = (73, 109, 137))
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        
        # Simular objeto de archivo de Django
        class MockFile:
            def __init__(self, content): self.content = content
            def read(self): return self.content
            def seek(self, pos): pass
        
        res_img = gemini.analyze_real_image(
            image_files=[MockFile(img_byte_arr.getvalue())],
            analysis_type='general'
        )
        if res_img.get('success'):
            print(f"   [OK] Gemini analizó la imagen usando: {res_img.get('model_used')}")
        else:
            print(f"   [ERROR] Gemini no pudo analizar la imagen: {res_img}")
    except Exception as e:
        print(f"   [ERROR] Excepción en prueba de imagen Gemini: {e}")

    # 3. Probar Ollama (Opcional - solo si nb-jdiaz26 está disponible)
    print("\n3. Probando Ollama Local (Respaldo)...")
    try:
        ollama = OllamaService()
        # Nota: Esto fallará si el PC local no está encendido o accesible
        res_ollama = ollama.generate_content("Hola, eres el respaldo local.")
        print(f"   [OK] Ollama respondió: {res_ollama[:50]}...")
    except Exception as e:
        print(f"   [INFO] Ollama no disponible (esperado si no hay conexión): {e}")

if __name__ == "__main__":
    test_ai_services()
