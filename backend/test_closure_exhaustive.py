import os
import django
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
sys.path.append(os.path.join(os.getcwd(), 'backend'))
django.setup()

from apps.sap_integration.sap_transaction_service import SAPTransactionService
from apps.core.thread_local import set_current_country, clear_current_country

def test_closing_exhaustive():
    print("=== TEST CIERRE EXHAUSTIVO COLOMBIA ===")
    
    set_current_country('CO')
    sap = SAPTransactionService()
    # No mocked, let it login
    
    # 1. Test con U_NX_FECHAVISITA
    print("\n--- INTENTO: CIERRE + FECHA ---")
    res1 = sap.update_service_call(12, {
        "Status": -2, 
        "Resolution": "Cierre con FECHA (Prueba Antigravity)",
        "U_NX_FECHAVISITA": "2026-03-30"
    })
    print(f"  Result 1: {res1}")

    # 2. Test con TechnicianCode
    print("\n--- INTENTO: CIERRE + TECHNICIAN ---")
    res2 = sap.update_service_call(11, {
        "Status": -2, 
        "Resolution": "Cierre con TECH (Prueba Antigravity)",
        "TechnicianCode": 2
    })
    print(f"  Result 2: {res2}")

    # 3. Test con ProblemType
    print("\n--- INTENTO: CIERRE + PROBLEM TYPE ---")
    res3 = sap.update_service_call(10, {
        "Status": -2, 
        "Resolution": "Cierre con ProblemType (Prueba Antigravity)",
        "ProblemType": 33
    })
    print(f"  Result 3: {res3}")

    clear_current_country()

if __name__ == "__main__":
    test_closing_exhaustive()
