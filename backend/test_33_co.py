import os
import django
import requests
import json
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))
django.setup()

from apps.sap_integration.sap_transaction_service import SAPTransactionService
from apps.core.thread_local import set_current_country

def test_problem_type_33_only():
    set_current_country('CO')
    sap_tx = SAPTransactionService()
    if not sap_tx._login():
        print("Login failed")
        return

    url = f"{sap_tx.base_url}/ServiceCalls"
    
    # Intento de creación con ProblemType 33 pero SIN CallType
    payload = {
        "CustomerCode": "901663921",
        "Subject": "TEST PROBLEM TYPE 33",
        "TechnicianCode": 2,
        "ProblemType": 33,
        "Origin": -1,
        "Series": 36
    }
    
    print(f"Trying payload: {json.dumps(payload)}")
    response = requests.post(
        url,
        data=json.dumps(payload),
        cookies=sap_tx.session_cookies,
        verify=False
    )
    
    if response.status_code in (200, 201):
        print("Success 33!")
        print(response.json()['ServiceCallID'])
    else:
        print(f"Failed {response.status_code}: {response.text}")

if __name__ == "__main__":
    test_problem_type_33_only()
