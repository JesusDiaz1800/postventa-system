import os
import django
import sys
import requests

# Setup Django
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.sap_integration.sap_transaction_service import SAPTransactionService

def check_sl_metadata():
    tx = SAPTransactionService()
    if not tx._login():
        print("Login failed")
        return

    # Check one specific employee to see all their fields
    emp_id = 1
    url = f"{tx.base_url}/EmployeesInfo({emp_id})"
    try:
        print(f"Fetching full data for Employee {emp_id} from SL...")
        res = requests.get(url, cookies=tx.session_cookies, verify=False)
        if res.status_code == 200:
            data = res.json()
            for k, v in data.items():
                if 'tech' in k.lower() or 'role' in k.lower() or 'type' in k.lower() or 'pos' in k.lower():
                    print(f" {k}: {v}")
            
            # Print everything to a file for thorough inspection if needed, or just print keys here
            print("\nAll keys in EmployeesInfo:")
            print(", ".join(data.keys()))
        else:
            print(f"Failed to fetch employee: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_sl_metadata()
