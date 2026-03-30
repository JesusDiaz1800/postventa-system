import os
import sys
import django

# Añadir el path del backend (donde está apps/)
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.core.thread_local import set_current_country
from apps.sap_integration.sap_query_service import SAPQueryService

def test_sap_routing():
    service = SAPQueryService()
    countries = ['CL', 'PE', 'CO']
    
    print("--- DEBUG SAP ROUTING START ---")
    
    for country in countries:
        set_current_country(country)
        db_alias = service._get_db_alias()
        print(f"Country Context: {country} -> Target DB: {db_alias}")
        
        # Verificar que el alias sea el esperado
        expected = {
            'CL': 'sap_db',
            'PE': 'sap_db_pe',
            'CO': 'sap_db_co'
        }[country]
        
        if db_alias == expected:
            print(f"  [OK] Ruteo correcto.")
        else:
            print(f"  [ERROR] Se esperaba {expected} pero se obtuvo {db_alias}")

    print("--- DEBUG SAP ROUTING END ---")

if __name__ == "__main__":
    test_sap_routing()
