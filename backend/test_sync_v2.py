import os
import django
import sys
import logging

# Setup Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup Django
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.core.thread_local import set_current_country, get_current_country
from apps.sap_integration.sap_transaction_service import SAPTransactionService

def test_sync_v2():
    print("=== TEST SYNC COLOMBIA V2 ===")
    set_current_country('CO')
    
    tx_service = SAPTransactionService()
    test_customer = "C900238275" # Optimizacion de procesos...
    
    # Probamos con el nuevo ID 1
    target_tech_id = 1
    
    try:
        print(f"Attempting to create test service call for {test_customer} with Tech ID {target_tech_id}...")
        result = tx_service.create_service_call(
            customer_code=test_customer,
            subject="TEST SYNC WITH NEW TECH ID 1",
            description="Verified technician presence in SQL, now testing SL creation.",
            priority='L',
            technician_code=target_tech_id
        )
        print(f"Result: {result}")
        if result.get('success'):
            print(f"SUCCESS! Created DocNum: {result.get('doc_num')}")
        else:
            print(f"SYNC FAILED: {result.get('error')}")
    except Exception as e:
        print(f"EXCEPTION creating service call: {e}")

if __name__ == "__main__":
    test_sync_v2()
