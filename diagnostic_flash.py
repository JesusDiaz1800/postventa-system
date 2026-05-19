import os
import sys
from google import genai
from django.conf import settings
import django

# Environment setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
sys.path.append('backend')
django.setup()

def find_working_flash_model():
    print("=== BUSCANDO MODELO FLASH FUNCIONAL ===")
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    client = genai.Client(api_key=api_key)
    
    # Lista de posibles modelos Flash detectados o estándar
    candidates = [
        'gemini-1.5-flash',
        'gemini-1.5-flash-002',
        'gemini-1.5-flash-8b',
        'gemini-2.0-flash',
        'gemini-2.0-flash-lite',
        'gemini-2.1-flash',
        'gemini-3.1-flash-live-preview'
    ]
    
    working_models = []
    
    for model_id in candidates:
        print(f"Probando: {model_id}...", end=" ", flush=True)
        try:
            response = client.models.generate_content(
                model=model_id,
                contents="Ping"
            )
            print("OK!")
            working_models.append(model_id)
        except Exception as e:
            err = str(e)
            if "429" in err:
                print("LÍMITE (429)")
                working_models.append(f"{model_id} (QUOTA EXCEEDED)")
            else:
                print(f"FALLO: {err[:50]}...")
                
    print("\nModelos funcionales encontrados:")
    for m in working_models:
        print(f" - {m}")

if __name__ == "__main__":
    find_working_flash_model()
