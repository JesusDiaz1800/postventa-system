import os
import django
import sys

# Setup Django
BASE_DIR = r"c:\Users\jdiaz\Desktop\postventa-system\backend"
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.ai.gemini_service import get_gemini_service
from apps.ai.ollama_service import OllamaService

def test_gemini():
    print("Testing Gemini...")
    try:
        service = get_gemini_service()
        response = service.generate_content("Hola, dime simplemente 'funciona' si puedes leerme.")
        print(f"Gemini Response: {response}")
    except Exception as e:
        print(f"Gemini Error: {e}")

def test_ollama():
    print("\nTesting Ollama Fallback...")
    try:
        service = OllamaService()
        response = service.generate_content("Hola, dime 'local' si funcionas.", timeout=30)
        print(f"Ollama Response: {response}")
    except Exception as e:
        print(f"Ollama Error: {e}")

if __name__ == "__main__":
    test_gemini()
    test_ollama()
