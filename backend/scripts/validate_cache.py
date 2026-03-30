import os
import sys
import django

# Añadir el path del backend
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.sap_integration.sap_query_service import SAPQueryService
from django.core.cache import cache

def validate_cache_access():
    print("Testing cache access...")
    try:
        cache.set('test_key', 'test_value', 10)
        val = cache.get('test_key')
        print(f"Direct cache test: {val}")
        
        service = SAPQueryService()
        # Intentar llamar a un método que use cache
        print("Calling search_customers (will hit cache logic)...")
        # Esto podría fallar por conexión a DB, pero queremos ver si falla antes por NameError: cache
        try:
            service.search_customers("test")
        except NameError as e:
            print(f"FAILED with NameError: {e}")
        except Exception as e:
            # Si es por DB connection, al menos ya sabemos que 'cache' estaba definido
            print(f"Reached DB logic, so cache is defined. (DB Error: {type(e).__name__})")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    validate_cache_access()
