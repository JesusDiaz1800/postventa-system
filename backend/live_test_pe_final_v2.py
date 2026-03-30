import os
import sys
import django
import json
import requests

# Add the backend directory to sys.path
backend_dir = r"c:\Users\jdiaz\Desktop\postventa-system\backend"
sys.path.append(backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.core.thread_local import set_current_country
from apps.sap_integration.sap_transaction_service import SAPTransactionService

def live_test_pe_final_v2():
    set_current_country('PE')
    sap_tx = SAPTransactionService()
    
    if not sap_tx._login():
        print("Login failed")
        return

    # Payload manual para probar la combinacion ganadora
    payload = {
        "Series": 36,
        "CustomerCode": 'CL20101095747',
        "Subject": 'TEST FINAL COMBINACION - PE V2',
        "Description": 'Assignee 13 (Albert) + Technician 1 (Luis)',
        "Status": 1,
        "ProblemType": 13,
        "CallType": 2,
        "AssigneeCode": 13,
        "TechnicianCode": 1,
        "U_NX_VENDEDOR": 'FABRICA'
    }
    
    print("Enviando payload con Assignee=13 y Technician=1...")
    # Use requests directly with cookies from sap_tx
    response = requests.post(
        f"{sap_tx.base_url}/ServiceCalls",
        json=payload,
        verify=False,
        cookies=sap_tx.session_cookies
    )
    
    if response.status_code < 400:
        print(f"¡EXITO TOTAL! DocNum: {response.json().get('DocNum')}")
    else:
        print(f"FALLO: {response.text}")

if __name__ == "__main__":
    live_test_pe_final_v2()
