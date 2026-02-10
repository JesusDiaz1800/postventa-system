import os
import sys
import django
from django.conf import settings

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

def check_db():
    print("=== DIAGNÓSTICO DE CONEXIÓN A BASE DE DATOS ===")
    
    db_settings = settings.DATABASES['default']
    
    print(f"ENGINE: {db_settings.get('ENGINE')}")
    print(f"HOST: {db_settings.get('HOST')}")
    print(f"NAME: {db_settings.get('NAME')}")
    print(f"USER: {db_settings.get('USER')}")
    # Ocultar password por seguridad
    pass_len = len(db_settings.get('PASSWORD') or '')
    print(f"PASSWORD: {'*' * pass_len} (Length: {pass_len})")
    
    print("\n--- Variables de Entorno (.env check) ---")
    print(f"DB_HOST (env): {os.getenv('DB_HOST')}")
    print(f"DB_NAME (env): {os.getenv('DB_NAME')}")
    
    print("\n--- Probando conexión real ---")
    try:
        from apps.incidents.models import Incident
        count = Incident.objects.count()
        print(f"CONEXIÓN EXITOSA.")
        print(f"Total Incidentes en BD: {count}")
        
        last = Incident.objects.last()
        if last:
            print(f"Último Incidente: {last.code} - {last.cliente} ({last.created_at})")
    except Exception as e:
        print(f"ERROR DE CONEXIÓN: {e}")

if __name__ == "__main__":
    check_db()
