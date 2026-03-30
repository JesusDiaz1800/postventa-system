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
      "U_NX_OBS_MURO": "asd",
      "U_NX_OBS_MATRIZ": "asd",
      "U_NX_OBS_LOSA": "asd",
      "U_NX_OBS_ALMAC": "asdgwgde",
      "U_NX_OBS_PRE_ARM": "ewgwe",
      "U_NX_OBS_EXTER": "ewgw",
      "U_NX_GENE": "egweg",
      "U_NX_RET_MQ": 0,
      "U_NX_MAQ1": "1",
      "U_NX_INI1": 2,
      "U_NX_COR1": 3,
      "U_NX_MEZCLADO": 1,
      "U_NX_RESCATADA": 0,
      "U_NX_OBRAFINALIZADA": 1,
      "U_NX_FECHAVISITA": "2026-03-23",
      "TechnicianCode": 31,
      "U_NX_NREPORT": 4
    }
    
    print(f"Probando PATCH a SC {call_id} con payload completo...")
    try:
        res = sap_tx.update_service_call(call_id, payload)
        print(f"Resultado PATCH: {res}")
    except Exception as e:
        print(f"Excepcion capturada en script: {e}")

if __name__ == "__main__":
    test()
