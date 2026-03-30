import os
import django
import sys
import requests

# Setup Django
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.core.thread_local import set_current_country
from apps.sap_integration.sap_transaction_service import SAPTransactionService

def check_sl_metadata_co():
    set_current_country('CO')
    tx = SAPTransactionService()
    if not tx._login():
        print("Login failed")
        return

    print(f"Connected to: {tx.company_db}")

    # Check the 2 employees we found in SQL
    for emp_id in [1, 2]:
        url = f"{tx.base_url}/EmployeesInfo({emp_id})"
        try:
            print(f"\n--- Data for Employee {emp_id} ---")
            res = requests.get(url, cookies=tx.session_cookies, verify=False)
            if res.status_code == 200:
                data = res.json()
                print(f" Name: {data.get('FirstName')} {data.get('LastName')}")
                print(f" Active: {data.get('Active')}")
                print(f" Role Info Lines: {data.get('EmployeeRolesInfoLines')}")
                # Print any field containing 'Tech' (case insensitive)
                for k, v in data.items():
                    if 'tech' in k.lower():
                        print(f" {k}: {v}")
            else:
                print(f"Failed: {res.status_code} - {res.text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    check_sl_metadata_co()
