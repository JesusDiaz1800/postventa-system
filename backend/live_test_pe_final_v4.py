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

def live_test_pe_final_v4():
    set_current_country('PE')
    sap_tx = SAPTransactionService()
    
    if not sap_tx._login():
        print("Login failed")
        return

    # Payload manual para probar la combinacion ganadora
    payload = {
        "Series": 36,
        "CustomerCode": 'CL20101095747',
        "Subject": 'TEST FINAL COMBINACION - PE V4',
        "Description": 'Assignee 13 + Tech 1 + BPProjectCode 3390',
        "Status": 1,
        "ProblemType": 13,
        "CallType": 2,
        "AssigneeCode": 13,
        "TechnicianCode": 1,
        "BPProjectCode": "3390", # Obra Las Doñas
        "U_NX_VENDEDOR": 'FABRICA',
        "U_NX_NOM_PRO": 'LAS DOÑAS' 
    }
    
    print("Enviando payload con Obra 3390...")
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
    live_test_pe_final_v4()
