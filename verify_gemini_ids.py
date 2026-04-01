import os
import sys
from google import genai
from django.conf import settings
import django

# Environment setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
sys.path.append('backend')
django.setup()

def test_model(client, model_id):
    print(f"Probando {model_id}...")
    try:
        response = client.models.generate_content(
            model=model_id,
            contents="Say 'Flash OK'"
        )
        print(f"  - EXITOSO: {response.text.strip()}")
        return True
    except Exception as e:
        print(f"  - FALLIDO: {e}")
        return False

try:
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key:
        print("Error: No GEMINI_API_KEY")
        sys.exit(1)
        
    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1'})
    
    models_to_try = [
        'gemini-1.5-flash-latest', 
        'gemini-1.5-flash', 
        'gemini-1.5-flash-001',
        'gemini-1.5-flash-002',
        'gemini-2.0-flash',
        'gemini-1.5-flash-8b'
    ]
    
    results = {}
    for m in models_to_try:
        results[m] = test_model(client, m)
    
    print("\nResumen de resultados:")
    for m, ok in results.items():
        print(f"{' [OK] ' if ok else ' [FAIL]'} {m}")

except Exception as e:
    print(f"Error general: {e}")
