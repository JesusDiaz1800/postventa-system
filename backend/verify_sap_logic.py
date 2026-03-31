import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))
django.setup()

from apps.sap_integration.sap_transaction_service import SAPTransactionService
from apps.core.thread_local import set_current_country, clear_current_country

def test_logic():
    print("=== TEST LÓGICA SAP TRANSACTION SERVICE (COLOMBIA vs CHILE) ===")
    
    # Pruebas de Cierre
    print("\n--- TEST: CLOSE SERVICE CALL ---")
    
    # 1. Colombia
    set_current_country('CO')
    sap_co = SAPTransactionService()
    # Mocking _login and update_service_call to see payload
    def mock_update(call_id, payload):
        print(f"  [CO] Payload: {payload}")
        return {'success': True}
    sap_co.update_service_call = mock_update
    sap_co.session_cookies = True # Bypass login
    sap_co.close_service_call(1234, "Cierre Colombia")
    clear_current_country()

    # 2. Chile
    set_current_country('CL')
    sap_cl = SAPTransactionService()
    sap_cl.update_service_call = mock_update
    sap_cl.session_cookies = True # Bypass login
    sap_cl.close_service_call(1234, "Cierre Chile")
    clear_current_country()

    # Pruebas de Cancelación
    print("\n--- TEST: CANCEL SERVICE CALL ---")
    
    # 1. Colombia
    set_current_country('CO')
    sap_co.cancel_service_call(1234, "Cancelacion Colombia")
    clear_current_country()

    # 2. Chile
    set_current_country('CL')
    sap_cl.cancel_service_call(1234, "Cancelacion Chile")
    clear_current_country()

if __name__ == "__main__":
    test_logic()
