import os
import sys
import django
import requests

# Add the backend directory to sys.path
backend_dir = r"c:\Users\jdiaz\Desktop\postventa-system\backend"
sys.path.append(backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.sap_integration.sap_transaction_service import SAPTransactionService
from apps.core.thread_local import set_current_country

def inspect_sc():
    set_current_country('PE')
    service = SAPTransactionService()
    if not service._login():
        print("Login failed")
        return
        
    print("Obteniendo la última llamada de servicio en PE...")
    url = f"{service.base_url}/ServiceCalls?$top=1&$orderby=ServiceCallID desc"
    try:
        res = requests.get(url, cookies=service.session_cookies, verify=False, timeout=15)
        if res.status_code == 200:
            data = res.json().get('value', [])[0]
            print("DATOS DE LLAMADA EXISTENTE:")
            for k, v in data.items():
                if k in ['ServiceCallID', 'Status', 'Priority', 'Series', 'ProblemType', 'CallType', 'AssigneeCode', 'TechnicianCode']:
                    print(f"{k}: {v} (Type: {type(v)})")
        else:
            print(f"Error {res.status_code}: {res.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    inspect_sc()
