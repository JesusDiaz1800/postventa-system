import os
import django
import logging
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.users.models import User
from apps.sap_integration.sap_transaction_service import SAPTransactionService
from django.conf import settings

# Configure logging to see the outputs of our new logic
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SAP_VERIFY")

def verify_fallbacks():
    print("\n=== VERIFICACIÓN DE FALLBACKS SAP PER-COUNTRY ===")
    
    # Test Cases:
    # 1. User with .cl or no suffix -> Chile Fallback
    # 2. User with .pe suffix -> Peru Fallback
    # 3. User with .co suffix -> Colombia Fallback
    # 4. User with explicit SAP credentials -> Personalized
    
    test_data = [
        {"username": "test.admin", "expected_country": "CL", "expected_user": "ccalidad"},
        {"username": "user.pe", "expected_country": "PE", "expected_user": "jefsertec_ppe"},
        {"username": "user.co", "expected_country": "CO", "expected_user": "jefsertec_pco"},
        {"username": "user_with_sap", "sap_user": "custom_user", "sap_password": "pwd", "expected_country": "CL", "expected_user": "custom_user"},
    ]
    
    for case in test_data:
        print(f"\nProbando usuario: {case['username']}")
        
        # Create a mock user object (don't save to DB if possible, or use a temp one)
        user = User(username=case['username'])
        if 'sap_user' in case:
            user.sap_user = case['sap_user']
            user.sap_password = case['sap_password']
            
        print(f"  > Country Code detectado: {user.country_code}")
        
        # Initialize Service
        service = SAPTransactionService(request_user=user)
        
        print(f"  > DB asignada: {service.company_db}")
        print(f"  > Usuario SAP asignado: {service.user}")
        
        # assertions (print result)
        success = (user.country_code == case['expected_country'] and service.user == case['expected_user'])
        status = "PASSED" if success else "FAILED"
        print(f"  > RESULTADO: {status}")
        
        if not success:
            print(f"    ERROR: Expected {case['expected_country']}/{case['expected_user']}, got {user.country_code}/{service.user}")

if __name__ == "__main__":
    try:
        verify_fallbacks()
    except Exception as e:
        print(f"Error durante la verificación: {e}")
        import traceback
        traceback.print_exc()
