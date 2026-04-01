import os
import sys
from google import genai
from django.conf import settings
import django

# Environment setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
sys.path.append('backend')
django.setup()

try:
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key:
        print("Error: No GEMINI_API_KEY")
        sys.exit(1)
        
    print(f"Usando API Key finalizada en: ...{api_key[-4:]}")
    # Probar sin forzar API version v1, dejar que el SDK elija o ir a v1beta
    client = genai.Client(api_key=api_key)
    
    print("\nListado de modelos oficiales disponibles:")
    for model in client.models.list():
        print(f" - ID: {model.name} | Display: {model.display_name}")

except Exception as e:
    print(f"Error listando modelos: {e}")
