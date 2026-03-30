import os
import sys
import django
import requests
from django.conf import settings
from django.db import connections

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

def check_db_connection(alias):
    try:
        connection = connections[alias]
        connection.ensure_connection()
        print(f"[OK] Conexión a Base de Datos '{alias}' exitosa.")
        return True
    except Exception as e:
        print(f"[ERROR] Fallo en Base de Datos '{alias}': {e}")
        return False

def check_sap_service_layer(country_code='CL'):
    try:
        from apps.sap_integration.sap_transaction_service import SAPTransactionService
        from apps.core.thread_local import set_current_country
        
        set_current_country(country_code)
        sap = SAPTransactionService()
        
        # Intentar login (obtener B1SESSION)
        if sap._login():
            print(f"[OK] SAP Service Layer {country_code} conectado correctamente.")
            return True
        else:
            print(f"[ERROR] SAP Service Layer {country_code} devolvió sesión nula.")
            return False
    except Exception as e:
        print(f"[ERROR] SAP Service Layer {country_code} falló: {e}")
        return False

def run_all_checks():
    print("=== INICIANDO VALIDACIÓN DE PRE-PRODUCCIÓN ===\n")
    
    countries = ['CL', 'PE', 'CO']
    db_aliases = {
        'CL': ['default', 'sap_db'],
        'PE': ['default_pe', 'sap_db_pe'],
        'CO': ['default_co', 'sap_db_co']
    }
    
    all_ok = True
    
    for country in countries:
        print(f"\n--- VALIDANDO {country} ---")
        
        # Validar DBs
        for alias in db_aliases[country]:
            if not check_db_connection(alias):
                all_ok = False
        
        # Validar SAP SL
        if not check_sap_service_layer(country):
            all_ok = False
            
    print("\n" + "="*40)
    if all_ok:
        print("RESULTADO: TODOS LOS SISTEMAS LISTOS PARA PRODUCCIÓN.")
    else:
        print("RESULTADO: EXISTEN ERRORES DE CONEXIÓN. REVISAR .ENV")
    print("="*40)

if __name__ == "__main__":
    run_all_checks()
