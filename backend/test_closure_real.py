import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))
django.setup()

from apps.sap_integration.sap_transaction_service import SAPTransactionService
from apps.core.thread_local import set_current_country, clear_current_country

def test_closing_real():
    print("=== TEST CIERRE REAL COLOMBIA (INC-2026-0008 / CallID 13) ===")
    
    set_current_country('CO')
    sap = SAPTransactionService()
    
    # 1. Intentar UN CIERRE MÍNIMO (Solo Status y Resolución)
    print("\n--- INTENTO 1: CIERRE MÍNIMO ---")
    res1 = sap.update_service_call(13, {"Status": -2, "Resolution": "Cierre de prueba Minimo (Antigravity)"})
    print(f"  Resultado 1: {res1}")

    # 2. Intentar UN CIERRE CON FECHA VISITA
    if not res1.get('success'):
        print("\n--- INTENTO 2: CIERRE CON FECHA VISITA ---")
        res2 = sap.update_service_call(13, {
            "Status": -2, 
            "Resolution": "Cierre de prueba con Fecha (Antigravity)",
            "U_NX_FECHAVISITA": "2026-03-30"
        })
        print(f"  Resultado 2: {res2}")

    clear_current_country()

if __name__ == "__main__":
    test_closing_real()
