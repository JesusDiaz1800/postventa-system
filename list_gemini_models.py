import os
import sys
from google import genai
from django.conf import settings
import django

# Simular entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
sys.path.append('backend')
django.setup()

try:
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key:
         print("ERROR: No GEMINI_API_KEY found")
         sys.exit(1)

    print(f"Usando API KEY (ends with): ...{api_key[-4:]}")
    client = genai.Client(api_key=api_key)
    
    print("\nListando modelos disponibles:")
    for model in client.models.list():
        print(f" - {model}")
        
except Exception as e:
    print(f"ERROR: {e}")
