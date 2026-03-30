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
from apps.sap_integration.sap_query_service import SAPQueryService
from apps.sap_integration.sap_transaction_service import SAPTransactionService

def debug_colombia():
    print("=== DEBUG COLOMBIA INTEGRATION ===")
    set_current_country('CO')
    print(f"Current Country set to: {get_current_country()}")
    
    query_service = SAPQueryService()
    tx_service = SAPTransactionService()
    
    print("\n1. Testing Technicians Fetching...")
    try:
        techs = query_service.get_technicians()
        print(f"Technicians found: {len(techs)}")
        for t in techs:
            print(f" - {t}")
        if not techs:
            print("ERROR: No technicians returned for Colombia!")
    except Exception as e:
        print(f"EXCEPTION fetching technicians: {e}")

    print("\n2. Testing Service Call Creation (Dry Run / Small Test)...")
    # Using a dummy customer code from previous search if possible, or common one
    # Previous search showed C900238275
    test_customer = "C900238275"
    try:
        print(f"Attempting to create test service call for {test_customer}...")
        result = tx_service.create_service_call(
            customer_code=test_customer,
            subject="TEST DEBUG COLOMBIA",
            description="Created by debug script to verify mapping and sync.",
            priority='L'
        )
        print(f"Result: {result}")
        if not result.get('success'):
            print(f"SYNC FAILED: {result.get('error')}")
    except Exception as e:
        print(f"EXCEPTION creating service call: {e}")

if __name__ == "__main__":
    debug_colombia()
