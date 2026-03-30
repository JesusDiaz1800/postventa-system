import os, sys, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.core.settings'
import django; django.setup()

from apps.core.thread_local import set_current_country
from apps.sap_integration.sap_transaction_service import SAPTransactionService

def test():
    set_current_country('PE')
    sap_tx = SAPTransactionService()
    
    call_id = 3873
    payload = {
      "U_NX_OBS_MURO": "Test directo 1",
      "U_NX_NREPORT": 999
    }
    
    print(f"Probando PATCH a SC {call_id} con payload: {payload}")
    try:
        res = sap_tx.update_service_call(call_id, payload)
        print(f"Resultado PATCH: {res}")
    except Exception as e:
        print(f"Excepcion capturada en script: {e}")

if __name__ == "__main__":
    test()
