import os
import sys
import django

# Agregar el directorio backend al PYTHONPATH
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(script_dir, 'backend') if os.path.exists(os.path.join(script_dir, 'backend')) else script_dir
sys.path.insert(0, backend_dir)

print(f"DEBUG: sys.path[0] = {sys.path[0]}")

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.ai.models import AIProvider

def seed_providers():
    print("Iniciando registro de proveedores de IA...")
    
    # 1. Registrar Gemini (si no existe)
    gemini, created = AIProvider.objects.get_or_create(
        name='Gemini',
        defaults={
            'api_key': 'ENV_VAR',
            'is_active': True,
            'priority': 1
        }
    )
    if created:
        print("OK: Proveedor Gemini registrado.")
    else:
        print("- Proveedor Gemini ya existe.")

    # 2. Registrar Ollama Local (NB-JDIAZ26)
    ollama_url = "http://nb-jdiaz26:11434"
    ollama, created = AIProvider.objects.get_or_create(
        name='Ollama',
        defaults={
            'api_key': 'none',
            'base_url': ollama_url,
            'is_active': True,
            'priority': 2
        }
    )
    if created:
        print(f"OK: Proveedor Ollama registrado en {ollama_url}.")
    else:
        # Actualizar URL por si acaso
        ollama.base_url = ollama_url
        ollama.save()
        print(f"OK: Proveedor Ollama actualizado a {ollama_url}.")

    print("\nProceso completado exitosamente.")

if __name__ == "__main__":
    seed_providers()
